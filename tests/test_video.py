import socket
import time
from pathlib import Path
from unittest.mock import patch

import numpy as np

from conversation_copilot.capture import FramePacket, LatestFrameSlot
from conversation_copilot.windows import CallWindow
from conversation_copilot import video
from conversation_copilot.video import (
    FaceBox,
    RemoteFaceTracker,
    run_video_check,
    verify_assets,
)


def test_tracker_largest_switch_follow_and_six_second_loss():
    tracker = RemoteFaceTracker()
    large = FaceBox(0.05, 0.1, 0.4, 0.5)
    moved = FaceBox(0.12, 0.1, 0.4, 0.5)
    other = FaceBox(0.65, 0.2, 0.2, 0.3)

    assert tracker.update([other, large], 0) == large
    assert tracker.update([other, moved], 500) == moved
    tracker.request_switch()
    assert tracker.update([moved, other], 600) == other
    assert tracker.update([moved], 1_000) is None
    assert tracker.update([moved], 6_999) is None
    assert not tracker.is_lost
    assert tracker.update([moved], 7_000) is None
    assert tracker.is_lost
    assert tracker.update([moved, other], 7_100) is None
    tracker.request_continue()
    assert tracker.update([moved, other], 7_200) == other
    assert not tracker.is_lost


def test_replay_runs_offline_with_verified_local_assets():
    verify_assets()
    with patch.object(socket, "socket", side_effect=OSError("network disabled")):
        summary = run_video_check()

    assert "478 landmarks" in summary
    assert "52 blendshapes" in summary
    assert "Face lost without silent switching" in summary


def test_production_vision_sources_have_no_writer_or_network_client():
    from conversation_copilot import capture, video

    source = Path(capture.__file__).read_text(encoding="utf-8")
    source += Path(video.__file__).read_text(encoding="utf-8")
    for forbidden in ("imwrite", "VideoWriter", "requests.", "httpx.", "urllib."):
        assert forbidden not in source


def test_inference_failure_stops_capture_and_cleans_workers(monkeypatch):
    class FailingProcessor:
        def __init__(self):
            self.closed = False

        def process(self, _pixels, _timestamp):
            raise RuntimeError("fixture failure")

        def close(self):
            self.closed = True

        def switch_face(self):
            pass

    class FakeCapture:
        def __init__(self):
            self.frames = LatestFrameSlot()
            self.worker_alive = False
            self.stop_reason = ""

        def start(self):
            self.worker_alive = True

        def stop(self, _timeout=3):
            self.worker_alive = False
            self.frames.clear()

    processor = FailingProcessor()
    capture = FakeCapture()
    monkeypatch.setattr(video, "FaceProcessor", lambda: processor)
    session = video.LiveVideoSession(CallWindow(1, "Mock", "mock.exe", "Mock"), capture)
    session.start()
    capture.frames.replace(FramePacket(np.zeros((1, 1, 4), dtype=np.uint8), 1.0, 1))
    deadline = time.perf_counter() + 1
    while session.worker_alive and time.perf_counter() < deadline:
        time.sleep(0.01)

    assert not session.worker_alive
    assert not capture.worker_alive
    assert processor.closed
    assert session.snapshot().status == "Vision failed (RuntimeError) — reselect"


def test_stop_before_start_closes_processor(monkeypatch):
    class FakeProcessor:
        def __init__(self):
            self.close_count = 0

        def close(self):
            self.close_count += 1

        def switch_face(self):
            pass

    class FakeCapture:
        def __init__(self):
            self.frames = LatestFrameSlot()
            self.stop_reason = ""

        def stop(self, _timeout=3):
            self.frames.clear()

    processor = FakeProcessor()
    monkeypatch.setattr(video, "FaceProcessor", lambda: processor)
    session = video.LiveVideoSession(
        CallWindow(1, "Mock", "mock.exe", "Mock"), FakeCapture()
    )

    session.stop()

    assert processor.close_count == 1


def test_face_processor_close_is_idempotent():
    class NativeHandle:
        def __init__(self):
            self.close_count = 0

        def close(self):
            self.close_count += 1

    processor = video.FaceProcessor.__new__(video.FaceProcessor)
    processor._closed = False
    processor._landmarker = NativeHandle()
    processor._detector = NativeHandle()

    processor.close()
    processor.close()

    assert processor._landmarker.close_count == 1
    assert processor._detector.close_count == 1
