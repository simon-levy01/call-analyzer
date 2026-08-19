import numpy as np
import pytest

from conversation_copilot.capture import FramePacket, LatestFrameSlot, WindowCapture
from conversation_copilot.windows import CallWindow


def test_latest_frame_slot_replaces_and_clears_without_a_queue():
    slot = LatestFrameSlot()
    first = FramePacket(np.zeros((1, 1, 4), dtype=np.uint8), 1.0, 1)
    latest = FramePacket(np.ones((1, 1, 4), dtype=np.uint8), 2.0, 2)

    slot.replace(first)
    slot.replace(latest)

    assert slot.replaced_count == 1
    assert slot.retained_count == 1
    assert slot.take() is latest
    assert slot.retained_count == 0
    slot.replace(first)
    slot.clear()
    assert slot.retained_count == 0


def test_only_first_ineligible_callback_is_recorded():
    capture = WindowCapture(
        CallWindow(1, "Mock", "mock.exe", "Google Meet"),
        eligibility_check=lambda: False,
    )

    capture._drop_ineligible(7)
    capture._drop_ineligible(8)

    assert capture.callback_count == 0
    assert capture.dropped_ineligible_count == 1
    assert capture.ineligible_callback_index == 7


def test_start_reports_preinitialization_ineligibility(monkeypatch):
    capture = WindowCapture(
        CallWindow(1, "Mock", "mock.exe", "Google Meet"),
        eligibility_check=lambda: False,
    )

    def fail_before_ready():
        capture._finish("Google Meet tab no longer active — reselect")
        capture._ready_event.set()

    monkeypatch.setattr(capture, "_run", fail_before_ready)

    with pytest.raises(RuntimeError, match="Google Meet tab no longer active"):
        capture.start()
