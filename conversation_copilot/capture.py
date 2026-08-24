from __future__ import annotations

import ctypes
import gc
import threading
import time
import uuid
from dataclasses import dataclass
from typing import Callable

import numpy as np
from winrt.runtime import ApartmentType, init_apartment, uninit_apartment
from winrt.windows.graphics.capture import (
    Direct3D11CaptureFramePool,
    GraphicsCaptureSession,
)
from winrt.windows.graphics.capture.interop import create_for_window
from winrt.windows.graphics.directx import DirectXPixelFormat
from winrt.windows.graphics.directx.direct3d11.interop import (
    create_direct3d11_device_from_dxgi_device,
)
from winrt.windows.graphics.imaging import SoftwareBitmap
from winrt.windows.storage.streams import Buffer

from .windows import CallWindow, still_eligible, window_available, window_exists

MEET_INACTIVE_MESSAGE = "Google Meet tab no longer active — reselect"


@dataclass(slots=True)
class FramePacket:
    pixels: np.ndarray
    captured_at: float
    callback_index: int


class LatestFrameSlot:
    def __init__(self) -> None:
        self._condition = threading.Condition()
        self._frame: FramePacket | None = None
        self.replaced_count = 0

    def replace(self, frame: FramePacket) -> None:
        with self._condition:
            if self._frame is not None:
                self.replaced_count += 1
            self._frame = frame
            self._condition.notify()

    def take(self, timeout: float = 0.1) -> FramePacket | None:
        with self._condition:
            if self._frame is None:
                self._condition.wait(timeout)
            frame, self._frame = self._frame, None
            return frame

    def clear(self) -> None:
        with self._condition:
            self._frame = None
            self._condition.notify_all()

    @property
    def retained_count(self) -> int:
        with self._condition:
            return int(self._frame is not None)


class _Guid(ctypes.Structure):
    _fields_ = [
        ("data1", ctypes.c_uint32),
        ("data2", ctypes.c_uint16),
        ("data3", ctypes.c_uint16),
        ("data4", ctypes.c_ubyte * 8),
    ]

    @classmethod
    def parse(cls, value: str) -> "_Guid":
        return cls.from_buffer_copy(uuid.UUID(value).bytes_le)


def _com_method(pointer: ctypes.c_void_p, index: int, result, *arguments):
    address = ctypes.cast(
        pointer, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))
    )[0][index]
    return ctypes.WINFUNCTYPE(result, ctypes.c_void_p, *arguments)(address)


def _release(pointer: ctypes.c_void_p) -> None:
    if pointer:
        _com_method(pointer, 2, ctypes.c_ulong)(pointer)


def _create_direct3d_device():
    create_device = ctypes.WinDLL("d3d11").D3D11CreateDevice
    create_device.argtypes = [
        ctypes.c_void_p,
        ctypes.c_uint,
        ctypes.c_void_p,
        ctypes.c_uint,
        ctypes.c_void_p,
        ctypes.c_uint,
        ctypes.c_uint,
        ctypes.POINTER(ctypes.c_void_p),
        ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_void_p),
    ]
    create_device.restype = ctypes.c_long
    native_device = ctypes.c_void_p()
    native_context = ctypes.c_void_p()
    result = create_device(
        None,
        1,
        None,
        0x20,
        None,
        0,
        7,
        ctypes.byref(native_device),
        None,
        ctypes.byref(native_context),
    )
    if result < 0:
        raise OSError(result, "D3D11CreateDevice failed")

    dxgi_device = ctypes.c_void_p()
    dxgi_guid = _Guid.parse("54ec77fa-1377-44e6-8c32-88fd5f44c84c")
    query_interface = _com_method(
        native_device,
        0,
        ctypes.c_long,
        ctypes.POINTER(_Guid),
        ctypes.POINTER(ctypes.c_void_p),
    )
    result = query_interface(
        native_device, ctypes.byref(dxgi_guid), ctypes.byref(dxgi_device)
    )
    if result < 0:
        _release(native_context)
        _release(native_device)
        raise OSError(result, "IDXGIDevice query failed")
    try:
        return create_direct3d11_device_from_dxgi_device(dxgi_device.value)
    finally:
        _release(dxgi_device)
        _release(native_context)
        _release(native_device)


class WindowCapture:
    def __init__(
        self,
        target: CallWindow,
        *,
        eligibility_check: Callable[[], bool] | None = None,
        ineligible_message: str | None = None,
    ) -> None:
        self.target = target
        self.frames = LatestFrameSlot()
        self._eligibility_check = eligibility_check or (lambda: still_eligible(target))
        self._ineligible_message = ineligible_message or (
            MEET_INACTIVE_MESSAGE
            if target.kind == "Google Meet"
            else "Call window no longer available — reselect"
        )
        self._stop_event = threading.Event()
        self._ready_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._state_lock = threading.Lock()
        self._stop_reason = ""
        self._error = ""
        self._callback_count = 0
        self._dropped_ineligible_count = 0
        self._ineligible_callback_index: int | None = None
        self._last_dimensions: tuple[int, int] | None = None

    @property
    def stop_reason(self) -> str:
        with self._state_lock:
            return self._stop_reason

    @property
    def error(self) -> str:
        with self._state_lock:
            return self._error

    @property
    def callback_count(self) -> int:
        with self._state_lock:
            return self._callback_count

    @property
    def dropped_ineligible_count(self) -> int:
        with self._state_lock:
            return self._dropped_ineligible_count

    @property
    def ineligible_callback_index(self) -> int | None:
        with self._state_lock:
            return self._ineligible_callback_index

    @property
    def last_dimensions(self) -> tuple[int, int] | None:
        with self._state_lock:
            return self._last_dimensions

    @property
    def worker_alive(self) -> bool:
        return bool(self._thread and self._thread.is_alive())

    def _finish(self, reason: str, error: str = "") -> None:
        with self._state_lock:
            if not self._stop_reason:
                self._stop_reason = reason
            if error and not self._error:
                self._error = error
        self._stop_event.set()

    def _next_callback_index(self) -> int:
        with self._state_lock:
            self._callback_count += 1
            return self._callback_count

    def _drop_ineligible(self, callback_index: int) -> None:
        self.frames.clear()
        reason = (
            self._ineligible_message
            if window_exists(self.target.hwnd)
            else "Call window closed — reselect"
        )
        with self._state_lock:
            if self._stop_reason:
                return
            self._dropped_ineligible_count += 1
            self._ineligible_callback_index = callback_index
            self._stop_reason = reason
        self._stop_event.set()

    def start(self, timeout: float = 3.0) -> None:
        if self._thread and self._thread.is_alive():
            raise RuntimeError("capture is already running")
        self._thread = threading.Thread(
            target=self._run,
            name="conversation-copilot-wgc",
            daemon=False,
        )
        self._thread.start()
        if not self._ready_event.wait(timeout):
            self.stop()
            raise TimeoutError("capture did not initialize promptly")
        failure = self.error or self.stop_reason
        if failure:
            self.stop()
            raise RuntimeError(failure)

    def stop(self, timeout: float = 3.0) -> None:
        self._stop_event.set()
        self.frames.clear()
        thread = self._thread
        if thread and thread is not threading.current_thread():
            thread.join(timeout)
            if thread.is_alive():
                raise TimeoutError("capture thread did not stop promptly")

    def _run(self) -> None:
        apartment_initialized = False
        device = item = pool = session = None
        frame_token = closed_token = None
        pixel_format = DirectXPixelFormat.B8_G8_R8_A8_UINT_NORMALIZED
        current_size: list[int] = []

        try:
            init_apartment(ApartmentType.MULTI_THREADED)
            apartment_initialized = True
            if not GraphicsCaptureSession.is_supported():
                raise RuntimeError("Windows Graphics Capture is not supported")
            if not self._eligibility_check():
                self._finish(self._ineligible_message)
                return

            device = _create_direct3d_device()
            item = create_for_window(self.target.hwnd)
            size = item.size
            current_size[:] = [size.width, size.height]
            pool = Direct3D11CaptureFramePool.create_free_threaded(
                device, pixel_format, 1, size
            )
            session = pool.create_capture_session(item)

            def on_frame_arrived(sender, _args) -> None:
                callback_index = self._next_callback_index()
                if self._stop_event.is_set():
                    return
                if not self._eligibility_check():
                    self._drop_ineligible(callback_index)
                    return
                try:
                    frame = sender.try_get_next_frame()
                    if frame is None:
                        return
                    new_size = frame.content_size
                    with frame:
                        bitmap = SoftwareBitmap.create_copy_from_surface_async(
                            frame.surface
                        ).get()
                        with bitmap:
                            width = bitmap.pixel_width
                            height = bitmap.pixel_height
                            length = width * height * 4
                            buffer = Buffer(length)
                            buffer.length = length
                            bitmap.copy_to_buffer(buffer)
                            pixels = np.frombuffer(
                                memoryview(buffer), dtype=np.uint8, count=length
                            ).reshape(height, width, 4).copy()
                    # The title can change while WGC copies a frame. Recheck before
                    # publishing so that a raced non-Meet frame never reaches inference.
                    if self._stop_event.is_set():
                        pixels = None
                        return
                    if not self._eligibility_check():
                        pixels = None
                        self._drop_ineligible(callback_index)
                        return
                    self.frames.replace(
                        FramePacket(pixels, time.perf_counter(), callback_index)
                    )
                    with self._state_lock:
                        self._last_dimensions = (width, height)
                    if (new_size.width, new_size.height) != tuple(current_size):
                        current_size[:] = [new_size.width, new_size.height]
                        sender.recreate(
                            device, pixel_format, 1, new_size
                        )
                except BaseException as exc:
                    self.frames.clear()
                    self._finish(
                        "Capture failed — reselect",
                        f"capture callback failed ({type(exc).__name__})",
                    )

            def on_closed(_sender, _args) -> None:
                self.frames.clear()
                self._finish("Call window closed — reselect")

            frame_token = pool.add_frame_arrived(on_frame_arrived)
            closed_token = item.add_closed(on_closed)
            session.start_capture()
            self._ready_event.set()
            while not self._stop_event.wait(0.1):
                if not window_exists(self.target.hwnd):
                    self.frames.clear()
                    self._finish("Call window closed — reselect")
                elif not window_available(self.target.hwnd):
                    self.frames.clear()
                    self._finish(
                        self._ineligible_message
                        if window_exists(self.target.hwnd)
                        else "Call window closed — reselect"
                    )
        except BaseException as exc:
            self._finish(
                "Capture failed — reselect",
                f"capture initialization failed ({type(exc).__name__})",
            )
        finally:
            self._ready_event.set()
            self.frames.clear()
            if pool is not None and frame_token is not None:
                try:
                    pool.remove_frame_arrived(frame_token)
                except Exception:
                    pass
            if item is not None and closed_token is not None:
                try:
                    item.remove_closed(closed_token)
                except Exception:
                    pass
            if pool is not None:
                try:
                    pool.close()
                except Exception:
                    pass
            if session is not None and window_exists(self.target.hwnd):
                try:
                    session.close()
                except Exception:
                    pass
            if device is not None:
                try:
                    device.close()
                except Exception:
                    pass
            session = pool = item = device = None
            gc.collect()
            if apartment_initialized:
                uninit_apartment()
