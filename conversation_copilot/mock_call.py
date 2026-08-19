from __future__ import annotations

import os
import threading
import time
import tkinter as tk
import uuid
from pathlib import Path

from .capture import MEET_INACTIVE_MESSAGE, WindowCapture
from .video import LiveVideoSession, PORTRAIT_A_PATH, PORTRAIT_B_PATH
from .windows import CallWindow, _EnumWindowsProc, _snapshot_window, _user32

_MEDIA_SUFFIXES = {
    ".avi",
    ".bmp",
    ".gif",
    ".jpeg",
    ".jpg",
    ".mkv",
    ".mov",
    ".mp4",
    ".png",
    ".tiff",
    ".webm",
    ".webp",
}


def _media_files(root: Path) -> set[Path]:
    return {
        path.resolve()
        for path in root.rglob("*")
        if path.is_file() and path.suffix.casefold() in _MEDIA_SUFFIXES
    }


def _find_window(title: str) -> int:
    found = 0

    @_EnumWindowsProc
    def collect(hwnd: int, _lparam: int) -> bool:
        nonlocal found
        snapshot = _snapshot_window(hwnd)
        if snapshot and snapshot.title == title:
            found = snapshot.hwnd
            return False
        return True

    _user32.EnumWindows(collect, 0)
    if not found:
        raise RuntimeError("mock call window was not found")
    return found


def _pump(root: tk.Tk, seconds: float, tick) -> None:
    deadline = time.perf_counter() + seconds
    while time.perf_counter() < deadline:
        tick()
        root.update()
        time.sleep(1 / 30)


def _start_while_pumping(root: tk.Tk, start) -> None:
    errors: list[BaseException] = []

    def run() -> None:
        try:
            start()
        except BaseException as exc:
            errors.append(exc)

    worker = threading.Thread(target=run, name="mock-call-starter")
    worker.start()
    while worker.is_alive():
        root.update()
        time.sleep(0.01)
    worker.join()
    if errors:
        raise errors[0]


def _mock_window(title: str) -> tuple[tk.Tk, tk.Canvas]:
    root = tk.Tk()
    root.title(title)
    root.geometry("820x500")
    canvas = tk.Canvas(root, width=800, height=450, background="#282828")
    canvas.pack(fill="both", expand=True)
    photo_a = tk.PhotoImage(file=str(PORTRAIT_A_PATH)).subsample(3, 3)
    photo_b = tk.PhotoImage(file=str(PORTRAIT_B_PATH)).subsample(4, 4)
    canvas.create_image(190, 245, image=photo_a, tags="a")
    canvas.create_image(650, 245, image=photo_b, tags="b")
    canvas._fixture_images = (photo_a, photo_b)  # type: ignore[attr-defined]
    root.update()
    return root, canvas


def _title_invalidation_check() -> list[str]:
    eligible_title = f"F02 eligible mock call {uuid.uuid4()}"
    ineligible_title = f"F02 ineligible mock call {uuid.uuid4()}"
    root, canvas = _mock_window(eligible_title)
    hwnd = _find_window(eligible_title)

    def eligible() -> bool:
        snapshot = _snapshot_window(hwnd)
        return bool(snapshot and snapshot.visible and snapshot.title == eligible_title)

    target = CallWindow(hwnd, eligible_title, os.path.abspath(__file__), "Mock")
    capture = WindowCapture(
        target,
        eligibility_check=eligible,
        ineligible_message=MEET_INACTIVE_MESSAGE,
    )
    session = LiveVideoSession(target, capture, check_frame_changes=True)
    dimensions: set[tuple[int, int]] = set()
    started = time.perf_counter()
    _start_while_pumping(root, session.start)
    try:
        def animate() -> None:
            elapsed = time.perf_counter() - started
            canvas.coords("a", 190 + int(elapsed * 35) % 90, 245)
            if elapsed > 1.5:
                root.geometry("900x560")
            if capture.last_dimensions:
                dimensions.add(capture.last_dimensions)

        _pump(root, 7, animate)
        before = session.snapshot()
        session.switch_face()
        _pump(root, 1, animate)
        root.title(ineligible_title)
        root.update()
        invalidated_at = time.perf_counter()
        while capture.worker_alive and time.perf_counter() - invalidated_at < 2:
            root.update()
            time.sleep(0.02)
        session.stop()
        after = session.snapshot()
    finally:
        if session.worker_alive or capture.worker_alive:
            session.stop()
        root.destroy()

    invalid_index = capture.ineligible_callback_index
    checks = {
        "changing BGRA frames": before.changed_frame_count >= 2,
        "resize dimensions": len(dimensions) >= 2,
        "two face boxes": before.max_face_count >= 2,
        "selected landmarks": before.max_landmark_count == 478,
        "selected blendshapes": before.max_blendshape_count == 52,
        "first ineligible callback dropped": capture.dropped_ineligible_count == 1,
        "pending frame cleared": capture.frames.retained_count == 0,
        "no ineligible inference": bool(
            invalid_index and after.last_processed_callback_index < invalid_index
        ),
        "prompt invalidation stop": time.perf_counter() - invalidated_at < 2,
        "invalidation status": capture.stop_reason == MEET_INACTIVE_MESSAGE,
        "invalidation teardown": not session.worker_alive and not capture.worker_alive,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise RuntimeError("mock title invalidation failed: " + ", ".join(failed))
    return [
        f"title invalidation callback: {invalid_index}",
        f"processed callback before stop: {after.last_processed_callback_index}",
        f"observed dimensions: {len(dimensions)}",
    ]


def _target_close_check() -> str:
    title = f"F02 close mock call {uuid.uuid4()}"
    root, _canvas = _mock_window(title)
    hwnd = _find_window(title)
    target = CallWindow(hwnd, title, os.path.abspath(__file__), "Mock")
    capture = WindowCapture(
        target,
        eligibility_check=lambda: bool(_snapshot_window(hwnd)),
    )
    _start_while_pumping(root, capture.start)
    _pump(root, 1, lambda: None)
    closed_at = time.perf_counter()
    root.destroy()
    while capture.worker_alive and time.perf_counter() - closed_at < 2:
        time.sleep(0.02)
    capture.stop()
    if (
        capture.stop_reason != "Call window closed — reselect"
        or capture.worker_alive
        or capture.frames.retained_count
        or time.perf_counter() - closed_at >= 2
    ):
        raise RuntimeError(
            "mock target-close teardown failed "
            f"(reason={capture.stop_reason!r}, worker={capture.worker_alive}, "
            f"frames={capture.frames.retained_count}, "
            f"elapsed={time.perf_counter() - closed_at:.3f}s)"
        )
    return f"target-close stop: {(time.perf_counter() - closed_at) * 1000:.0f} ms"


def run_video_capture_check() -> str:
    project_root = Path(__file__).resolve().parent.parent
    before = _media_files(project_root)
    evidence = _title_invalidation_check()
    evidence.append(_target_close_check())
    if _media_files(project_root) != before:
        raise RuntimeError("mock capture wrote an image or video artifact")
    return "\n".join(
        ["Video capture check ready", *evidence, "workers/frames remaining: 0/0"]
    )
