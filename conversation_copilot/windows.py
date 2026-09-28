from __future__ import annotations

import ctypes
import re
from dataclasses import dataclass
from ctypes import wintypes
from pathlib import Path

MEET_TITLE_MARKER = "Google Meet"
MEET_CODE_TITLE = re.compile(
    r"Meet - [a-z]{3}-[a-z]{4}-[a-z]{3} - Google Chrome"
)
WHATSAPP_CALL_TITLE = "Video call"

_PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
_DWMWA_CLOAKED = 14
_EnumWindowsProc = ctypes.WINFUNCTYPE(
    wintypes.BOOL, wintypes.HWND, wintypes.LPARAM
)

_user32 = ctypes.WinDLL("user32", use_last_error=True)
_kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
_dwmapi = ctypes.WinDLL("dwmapi", use_last_error=True)

_user32.EnumWindows.argtypes = [_EnumWindowsProc, wintypes.LPARAM]
_user32.EnumWindows.restype = wintypes.BOOL
_user32.IsWindow.argtypes = [wintypes.HWND]
_user32.IsWindow.restype = wintypes.BOOL
_user32.IsWindowVisible.argtypes = [wintypes.HWND]
_user32.IsWindowVisible.restype = wintypes.BOOL
_user32.IsIconic.argtypes = [wintypes.HWND]
_user32.IsIconic.restype = wintypes.BOOL
_user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
_user32.GetWindowTextLengthW.restype = ctypes.c_int
_user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
_user32.GetWindowTextW.restype = ctypes.c_int
_user32.GetClassNameW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
_user32.GetClassNameW.restype = ctypes.c_int
_user32.GetWindowThreadProcessId.argtypes = [
    wintypes.HWND,
    ctypes.POINTER(wintypes.DWORD),
]
_user32.GetWindowThreadProcessId.restype = wintypes.DWORD
_kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
_kernel32.OpenProcess.restype = wintypes.HANDLE
_kernel32.QueryFullProcessImageNameW.argtypes = [
    wintypes.HANDLE,
    wintypes.DWORD,
    wintypes.LPWSTR,
    ctypes.POINTER(wintypes.DWORD),
]
_kernel32.QueryFullProcessImageNameW.restype = wintypes.BOOL
_kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
_kernel32.CloseHandle.restype = wintypes.BOOL
_dwmapi.DwmGetWindowAttribute.argtypes = [
    wintypes.HWND,
    wintypes.DWORD,
    wintypes.LPVOID,
    wintypes.DWORD,
]
_dwmapi.DwmGetWindowAttribute.restype = ctypes.c_long


@dataclass(frozen=True, slots=True)
class CallWindow:
    hwnd: int
    title: str
    process_path: str
    kind: str
    process_id: int = 0

    @property
    def display_name(self) -> str:
        return f"{self.kind}: {self.title}"


@dataclass(frozen=True, slots=True)
class _WindowSnapshot:
    hwnd: int
    title: str
    process_path: str
    visible: bool
    minimized: bool
    cloaked: bool
    process_id: int = 0
    window_class: str = ""


def _window_text(hwnd: int) -> str:
    length = _user32.GetWindowTextLengthW(hwnd)
    if length <= 0:
        return ""
    buffer = ctypes.create_unicode_buffer(length + 1)
    _user32.GetWindowTextW(hwnd, buffer, len(buffer))
    return buffer.value.strip()


def _process_path(hwnd: int) -> str:
    process_id = wintypes.DWORD()
    _user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))
    handle = _kernel32.OpenProcess(
        _PROCESS_QUERY_LIMITED_INFORMATION, False, process_id.value
    )
    if not handle:
        return ""
    try:
        size = wintypes.DWORD(32768)
        buffer = ctypes.create_unicode_buffer(size.value)
        if not _kernel32.QueryFullProcessImageNameW(
            handle, 0, buffer, ctypes.byref(size)
        ):
            return ""
        return buffer.value
    finally:
        _kernel32.CloseHandle(handle)


def _process_id(hwnd: int) -> int:
    process_id = wintypes.DWORD()
    _user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))
    return int(process_id.value)


def _snapshot_window(hwnd: int) -> _WindowSnapshot | None:
    if not _user32.IsWindow(hwnd):
        return None
    cloaked = wintypes.DWORD()
    cloaked_result = _dwmapi.DwmGetWindowAttribute(
        hwnd,
        _DWMWA_CLOAKED,
        ctypes.byref(cloaked),
        ctypes.sizeof(cloaked),
    )
    if cloaked_result < 0:
        return None
    window_class = ctypes.create_unicode_buffer(256)
    _user32.GetClassNameW(hwnd, window_class, len(window_class))
    return _WindowSnapshot(
        hwnd=int(hwnd),
        title=_window_text(hwnd),
        process_path=_process_path(hwnd),
        visible=bool(_user32.IsWindowVisible(hwnd)),
        minimized=bool(_user32.IsIconic(hwnd)),
        cloaked=bool(cloaked.value),
        process_id=_process_id(hwnd),
        window_class=window_class.value,
    )


def _eligible(snapshot: _WindowSnapshot) -> CallWindow | None:
    if (
        not snapshot.title
        or not snapshot.process_path
        or not snapshot.visible
        or snapshot.minimized
        or snapshot.cloaked
    ):
        return None

    executable = Path(snapshot.process_path).name.casefold()
    if (
        executable in {"whatsapp.exe", "whatsapp.root.exe"}
        and snapshot.title.casefold() == WHATSAPP_CALL_TITLE.casefold()
    ):
        kind = "WhatsApp"
    elif executable == "zoom.exe" and (
        snapshot.window_class == "ConfMultiTabContentWndClass"
        or (not snapshot.window_class and snapshot.title.casefold() in {"meeting", "zoom meeting", "zoom webinar"})
    ):
        kind = "Zoom"
    elif (
        executable == "chrome.exe"
        and (
            MEET_TITLE_MARKER.casefold() in snapshot.title.casefold()
            or MEET_CODE_TITLE.fullmatch(snapshot.title)
        )
    ):
        kind = "Google Meet"
    else:
        return None
    return CallWindow(
        snapshot.hwnd,
        snapshot.title,
        snapshot.process_path,
        kind,
        snapshot.process_id,
    )


def eligible_window(hwnd: int) -> CallWindow | None:
    snapshot = _snapshot_window(hwnd)
    return _eligible(snapshot) if snapshot else None


def window_exists(hwnd: int) -> bool:
    return bool(_user32.IsWindow(hwnd))


def window_available(hwnd: int) -> bool:
    snapshot = _snapshot_window(hwnd)
    return bool(
        snapshot
        and snapshot.visible
        and not snapshot.minimized
        and not snapshot.cloaked
    )


def still_eligible(selected: CallWindow) -> bool:
    current = eligible_window(selected.hwnd)
    return bool(
        current
        and current.kind == selected.kind
        and current.process_path.casefold() == selected.process_path.casefold()
        and current.process_id == selected.process_id
    )


def _enumerate_call_windows() -> list[CallWindow]:
    windows: list[CallWindow] = []

    @_EnumWindowsProc
    def collect(hwnd: int, _lparam: int) -> bool:
        window = eligible_window(hwnd)
        if window:
            windows.append(window)
        return True

    if not _user32.EnumWindows(collect, 0):
        raise ctypes.WinError(ctypes.get_last_error())
    return windows


def list_call_windows() -> list[CallWindow]:
    windows = _enumerate_call_windows()
    windows = _apply_call_priority(windows)
    return sorted(windows, key=lambda window: (window.kind, window.title.casefold()))


def whatsapp_call_active() -> bool:
    return any(window.kind == "WhatsApp" for window in _enumerate_call_windows())


def _apply_call_priority(windows: list[CallWindow]) -> list[CallWindow]:
    if any(window.kind == "WhatsApp" for window in windows):
        return [window for window in windows if window.kind != "Google Meet"]
    return windows
