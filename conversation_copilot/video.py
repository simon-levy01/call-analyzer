from __future__ import annotations

import hashlib
import math
import threading
import time
from collections import deque
from dataclasses import dataclass
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np

from .capture import WindowCapture
from .windows import CallWindow

ASSET_DIR = Path(__file__).with_name("assets")
DETECTOR_PATH = ASSET_DIR / "blaze_face_short_range.tflite"
LANDMARKER_PATH = ASSET_DIR / "face_landmarker.task"
PORTRAIT_A_PATH = ASSET_DIR / "synthetic-person-a.png"
PORTRAIT_B_PATH = ASSET_DIR / "synthetic-person-b.png"
ASSET_HASHES = {
    DETECTOR_PATH: "b4578f35940bf5a1a655214a1cce5cab13eba73c1297cd78e1a04c2380b0152f",
    LANDMARKER_PATH: "64184e229b263107bc2b804c6625db1341ff2bb731874b0bcc2fe6544e0bc9ff",
    PORTRAIT_A_PATH: "f22bdc0fc61d6fab355b3c64ef660da6566dd3ea4048ba677917074c3abf2553",
    PORTRAIT_B_PATH: "dd500cc459190d152c3cd53f1aed61ac0f64f20fc024e942f30b464fb323c01c",
}

_CROP_MARGIN = 0.25
_LOST_AFTER_MS = 18_000


@dataclass(frozen=True, slots=True)
class FaceBox:
    x: float
    y: float
    width: float
    height: float

    @property
    def area(self) -> float:
        return self.width * self.height

    @property
    def center(self) -> tuple[float, float]:
        return self.x + self.width / 2, self.y + self.height / 2


@dataclass(frozen=True, slots=True)
class FacialSignal:
    timestamp_ms: int
    face_box: FaceBox
    landmarks: tuple[tuple[float, float, float], ...]
    blendshapes: tuple[tuple[str, float], ...]


@dataclass(frozen=True, slots=True)
class ProcessingResult:
    signal: FacialSignal | None
    face_count: int
    tracking_state: str
    thumbnail_rgb: np.ndarray | None


def _intersection_over_union(left: FaceBox, right: FaceBox) -> float:
    x1 = max(left.x, right.x)
    y1 = max(left.y, right.y)
    x2 = min(left.x + left.width, right.x + right.width)
    y2 = min(left.y + left.height, right.y + right.height)
    intersection = max(0.0, x2 - x1) * max(0.0, y2 - y1)
    union = left.area + right.area - intersection
    return intersection / union if union else 0.0


def _intersection_over_smaller(left: FaceBox, right: FaceBox) -> float:
    x1 = max(left.x, right.x)
    y1 = max(left.y, right.y)
    x2 = min(left.x + left.width, right.x + right.width)
    y2 = min(left.y + left.height, right.y + right.height)
    intersection = max(0.0, x2 - x1) * max(0.0, y2 - y1)
    smaller = min(left.area, right.area)
    return min(1.0, intersection / smaller) if smaller else 0.0


class RemoteFaceTracker:
    def __init__(self) -> None:
        self.selected: FaceBox | None = None
        self._missed_since_ms: int | None = None
        self._lost = False
        self._switch_requested = False
        self._continue_requested = False
        self._lock = threading.Lock()

    @property
    def is_lost(self) -> bool:
        with self._lock:
            return self._lost

    def request_switch(self) -> None:
        with self._lock:
            self._switch_requested = True

    def request_continue(self) -> None:
        with self._lock:
            self._continue_requested = True

    def update(self, boxes: list[FaceBox], timestamp_ms: int) -> FaceBox | None:
        with self._lock:
            switch_requested = self._switch_requested
            self._switch_requested = False
            if self._continue_requested:
                self._continue_requested = False
                self._missed_since_ms = None
                self._lost = False
            if switch_requested and boxes:
                ordered = sorted(boxes, key=lambda box: box.center[0])
                if self.selected is None:
                    selected = ordered[0]
                else:
                    current_index = min(
                        range(len(ordered)),
                        key=lambda index: _center_distance(
                            self.selected, ordered[index]
                        ),
                    )
                    selected = ordered[(current_index + 1) % len(ordered)]
                self.selected = selected
                self._missed_since_ms = None
                self._lost = False
                return selected

            if self._lost:
                return None
            if self.selected is None:
                if not boxes:
                    return None
                self.selected = max(boxes, key=lambda box: box.area)
                return self.selected

            matches = [
                box
                for box in boxes
                if _intersection_over_union(self.selected, box) >= 0.10
                or _center_distance(self.selected, box) <= 0.22
            ]
            if matches:
                self.selected = max(
                    matches,
                    key=lambda box: (
                        _intersection_over_union(self.selected, box),
                        -_center_distance(self.selected, box),
                    ),
                )
                self._missed_since_ms = None
                return self.selected

            if self._missed_since_ms is None:
                self._missed_since_ms = timestamp_ms
            elif timestamp_ms - self._missed_since_ms >= _LOST_AFTER_MS:
                self._lost = True
            return None


def _center_distance(left: FaceBox, right: FaceBox) -> float:
    return math.dist(left.center, right.center)


def verify_assets() -> None:
    for path, expected in ASSET_HASHES.items():
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"asset hash mismatch: {path.name}")


class FaceProcessor:
    def __init__(self, delegate: str = "cpu") -> None:
        verify_assets()
        delegate_value = (
            mp.tasks.BaseOptions.Delegate.GPU
            if delegate == "gpu"
            else mp.tasks.BaseOptions.Delegate.CPU
        )
        detector = mp.tasks.vision.FaceDetector.create_from_options(
            mp.tasks.vision.FaceDetectorOptions(
                base_options=mp.tasks.BaseOptions(
                    model_asset_path=str(DETECTOR_PATH), delegate=delegate_value
                ),
                min_detection_confidence=0.5,
            )
        )
        try:
            landmarker = mp.tasks.vision.FaceLandmarker.create_from_options(
                mp.tasks.vision.FaceLandmarkerOptions(
                    base_options=mp.tasks.BaseOptions(
                        model_asset_path=str(LANDMARKER_PATH), delegate=delegate_value
                    ),
                    running_mode=mp.tasks.vision.RunningMode.VIDEO,
                    num_faces=1,
                    output_face_blendshapes=True,
                    min_face_detection_confidence=0.5,
                    min_face_presence_confidence=0.5,
                    min_tracking_confidence=0.5,
                )
            )
        except BaseException:
            detector.close()
            raise
        self._detector = detector
        self._landmarker = landmarker
        self._closed = False
        self.tracker = RemoteFaceTracker()
        self._last_timestamp_ms = -1

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        try:
            self._landmarker.close()
        finally:
            self._detector.close()

    def switch_face(self) -> None:
        self.tracker.request_switch()

    def continue_tracking(self) -> None:
        self.tracker.request_continue()

    def process(self, bgra: np.ndarray, timestamp_ms: int) -> ProcessingResult:
        timestamp_ms = max(timestamp_ms, self._last_timestamp_ms + 1)
        self._last_timestamp_ms = timestamp_ms
        rgb = cv2.cvtColor(bgra, cv2.COLOR_BGRA2RGB)
        height, width = rgb.shape[:2]
        boxes = self._detect_boxes(rgb, timestamp_ms)
        selected = self.tracker.update(boxes, timestamp_ms)
        state = "Face lost" if self.tracker.is_lost else "Tracking"
        if selected is None:
            return ProcessingResult(None, len(boxes), state, None)

        x1, y1, x2, y2 = _expanded_pixels(selected, width, height)
        crop = np.ascontiguousarray(rgb[y1:y2, x1:x2])
        if crop.size == 0:
            return ProcessingResult(None, len(boxes), state, None)
        crop_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=crop)
        result = self._landmarker.detect_for_video(crop_image, timestamp_ms)
        if not result.face_landmarks or not result.face_blendshapes:
            return ProcessingResult(None, len(boxes), state, None)

        crop_width = x2 - x1
        crop_height = y2 - y1
        landmarks = tuple(
            (
                (x1 + landmark.x * crop_width) / width,
                (y1 + landmark.y * crop_height) / height,
                landmark.z * crop_width / width,
            )
            for landmark in result.face_landmarks[0]
        )
        blendshapes = tuple(
            (category.category_name, float(category.score))
            for category in result.face_blendshapes[0]
        )
        signal = FacialSignal(timestamp_ms, selected, landmarks, blendshapes)
        thumbnail = cv2.resize(crop, (160, 120), interpolation=cv2.INTER_AREA)
        return ProcessingResult(signal, len(boxes), state, thumbnail)

    def _detect_boxes(self, rgb: np.ndarray, timestamp_ms: int) -> list[FaceBox]:
        height, width = rgb.shape[:2]

        def detect(x1: int, y1: int, x2: int, y2: int) -> list[FaceBox]:
            image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=np.ascontiguousarray(rgb[y1:y2, x1:x2]),
            )
            return [
                FaceBox(
                    max(0.0, (x1 + item.bounding_box.origin_x) / width),
                    max(0.0, (y1 + item.bounding_box.origin_y) / height),
                    min(1.0, item.bounding_box.width / width),
                    min(1.0, item.bounding_box.height / height),
                )
                for item in self._detector.detect(image).detections
            ]

        boxes = detect(0, 0, width, height)
        if boxes:
            return boxes
        left, right = width * 3 // 5, width * 2 // 5
        top, bottom = height * 3 // 5, height * 2 // 5
        tiled = [
            box
            for x1, y1, x2, y2 in (
                (0, 0, left, top),
                (right, 0, width, top),
                (0, bottom, left, height),
                (right, bottom, width, height),
            )
            for box in detect(x1, y1, x2, y2)
        ]
        unique: list[FaceBox] = []
        for box in sorted(tiled, key=lambda item: item.area, reverse=True):
            if all(_intersection_over_smaller(box, seen) < 0.5 for seen in unique):
                unique.append(box)
        return unique


def _expanded_pixels(
    box: FaceBox, width: int, height: int
) -> tuple[int, int, int, int]:
    margin_x = box.width * _CROP_MARGIN
    margin_y = box.height * _CROP_MARGIN
    x1 = max(0, int((box.x - margin_x) * width))
    y1 = max(0, int((box.y - margin_y) * height))
    x2 = min(width, int((box.x + box.width + margin_x) * width))
    y2 = min(height, int((box.y + box.height + margin_y) * height))
    return x1, y1, x2, y2


@dataclass(frozen=True, slots=True)
class ReplayStep:
    name: str
    timestamp_ms: int
    frame: np.ndarray
    switch_face: bool = False
    continue_tracking: bool = False


def replay_steps() -> list[ReplayStep]:
    portrait_a = cv2.imread(str(PORTRAIT_A_PATH), cv2.IMREAD_COLOR)
    portrait_b = cv2.imread(str(PORTRAIT_B_PATH), cv2.IMREAD_COLOR)
    if portrait_a is None or portrait_b is None:
        raise ValueError("synthetic portrait fixture is unreadable")

    def frame(
        a: tuple[int, int, int] | None,
        b: tuple[int, int, int] | None,
    ) -> np.ndarray:
        canvas = np.full((450, 800, 3), 40, dtype=np.uint8)
        for portrait, placement in ((portrait_a, a), (portrait_b, b)):
            if placement is None:
                continue
            x, y, size = placement
            resized = cv2.resize(portrait, (size, size), interpolation=cv2.INTER_AREA)
            canvas[y : y + size, x : x + size] = resized
        return cv2.cvtColor(canvas, cv2.COLOR_BGR2BGRA)

    both_1 = ((40, 70, 320), (500, 90, 260))
    both_2 = ((100, 70, 320), (490, 90, 260))
    only_b = (None, (490, 90, 260))
    only_a = ((100, 70, 320), None)
    return [
        ReplayStep("initial", 0, frame(*both_1)),
        ReplayStep("move", 500, frame(*both_2)),
        ReplayStep("brief-miss-1", 1_000, frame(*only_b)),
        ReplayStep("brief-miss-2", 1_800, frame(*only_b)),
        ReplayStep("reacquired", 1_900, frame(*both_2)),
        ReplayStep("switch", 2_000, frame(*both_2), True),
        ReplayStep("switched-follow", 2_200, frame((70, 65, 340), (460, 85, 270))),
        ReplayStep("long-miss-start", 2_600, frame(*only_a)),
        ReplayStep("long-miss-middle", 14_000, frame(*only_a)),
        ReplayStep("face-lost", 20_600, frame(*only_a)),
        ReplayStep("no-silent-reselect", 20_800, frame(*both_2)),
        ReplayStep(
            "continued-selected-face",
            20_900,
            frame(*both_2),
            continue_tracking=True,
        ),
    ]


def run_video_check() -> str:
    processor = FaceProcessor()
    signals: list[tuple[str, FacialSignal]] = []
    states: dict[str, str] = {}
    face_counts: dict[str, int] = {}
    try:
        for step in replay_steps():
            if step.switch_face:
                processor.switch_face()
            if step.continue_tracking:
                processor.continue_tracking()
            result = processor.process(step.frame, step.timestamp_ms)
            states[step.name] = result.tracking_state
            face_counts[step.name] = result.face_count
            if result.signal:
                signals.append((step.name, result.signal))
    finally:
        processor.close()

    by_name = dict(signals)
    required = {
        "initial",
        "move",
        "reacquired",
        "switch",
        "switched-follow",
        "continued-selected-face",
    }
    if not required.issubset(by_name):
        raise ValueError("replay did not produce every required selected-face signal")
    if face_counts["initial"] < 2 or face_counts["switch"] < 2:
        raise ValueError("replay did not detect both fixture faces")
    if by_name["initial"].face_box.center[0] >= 0.5:
        raise ValueError("largest left-side face was not selected initially")
    if by_name["move"].face_box.center[0] <= by_name["initial"].face_box.center[0]:
        raise ValueError("selected face did not follow movement")
    if by_name["switch"].face_box.center[0] <= 0.5:
        raise ValueError("Switch face did not select the other visible face")
    if "brief-miss-1" in by_name or "brief-miss-2" in by_name:
        raise ValueError("a missing selected face emitted a Facial Signal")
    if states["face-lost"] != "Face lost" or "no-silent-reselect" in by_name:
        raise ValueError("extended loss silently selected another face")
    if by_name["continued-selected-face"].face_box.center[0] <= 0.5:
        raise ValueError("Continue tracking changed the selected face")

    timestamps = [signal.timestamp_ms for _, signal in signals]
    if timestamps != sorted(timestamps):
        raise ValueError("Facial Signal timestamps are not ordered")
    for _name, signal in signals:
        if len(signal.landmarks) != 478 or len(signal.blendshapes) != 52:
            raise ValueError("Facial Signal structure is incomplete")
        if not all(math.isfinite(value) for landmark in signal.landmarks for value in landmark):
            raise ValueError("Facial Signal contains a non-finite landmark")
        if not all(
            name and math.isfinite(score) and 0.0 <= score <= 1.0
            for name, score in signal.blendshapes
        ):
            raise ValueError("Facial Signal contains an invalid blendshape")
    return (
        f"Video check ready\n{len(signals)} selected-face Facial Signals\n"
        "478 landmarks\n52 blendshapes\nFace lost without silent switching"
    )


@dataclass(frozen=True, slots=True)
class LiveSnapshot:
    status: str
    signal_rate: float
    face_count: int
    landmark_count: int
    blendshape_count: int
    thumbnail_rgb: np.ndarray | None
    retained_raw_frames: int
    processing_frames: int
    processed_count: int
    changed_frame_count: int
    max_face_count: int
    max_landmark_count: int
    max_blendshape_count: int
    last_processed_callback_index: int
    current_signal: FacialSignal | None


class LiveVideoSession:
    def __init__(
        self,
        window: CallWindow,
        capture: WindowCapture | None = None,
        *,
        check_frame_changes: bool = False,
    ) -> None:
        self.processor = FaceProcessor()
        self.capture = capture or WindowCapture(window)
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()
        self._status = "Starting"
        self._face_count = 0
        self._signal: FacialSignal | None = None
        self._thumbnail: np.ndarray | None = None
        self._processing_frames = 0
        self._processed_count = 0
        self._changed_frame_count = 0
        self._last_checksum: int | None = None
        self._max_face_count = 0
        self._max_landmark_count = 0
        self._max_blendshape_count = 0
        self._last_processed_callback_index = 0
        self._signal_times: deque[float] = deque()
        self._check_frame_changes = check_frame_changes
        self._selection_epoch = 0
        self._selection_action: str | None = None
        self._selection_changed_at = 0.0

    @property
    def worker_alive(self) -> bool:
        return bool(self._thread and self._thread.is_alive())

    def start(self) -> None:
        try:
            self.capture.start()
        except BaseException:
            self.processor.close()
            raise
        self._thread = threading.Thread(
            target=self._process_frames,
            name="conversation-copilot-vision",
            daemon=False,
        )
        try:
            self._thread.start()
        except BaseException:
            self.capture.stop()
            self.processor.close()
            raise

    def switch_face(self) -> None:
        self._change_selection("switch")

    def continue_tracking(self) -> None:
        self._change_selection("continue")

    def _change_selection(self, action: str) -> None:
        with self._lock:
            self._selection_epoch += 1
            self._selection_action = action
            self._selection_changed_at = time.perf_counter()
            self._signal = None
            self._thumbnail = None

    def stop(self, timeout: float = 4.0) -> None:
        self._stop_event.set()
        try:
            self.capture.stop(timeout)
            if self._thread and self._thread is not threading.current_thread():
                self._thread.join(timeout)
                if self._thread.is_alive():
                    raise TimeoutError("vision worker did not stop promptly")
        finally:
            # A live worker owns the processor until its own finally block runs.
            if not self.worker_alive:
                self.processor.close()
                with self._lock:
                    self._signal = None
                    self._thumbnail = None
                    self._processing_frames = 0

    def _process_frames(self) -> None:
        failure = ""
        try:
            while not self._stop_event.is_set():
                packet = self.capture.frames.take(0.1)
                if packet is None:
                    if not self.capture.worker_alive:
                        break
                    continue
                with self._lock:
                    if packet.captured_at < self._selection_changed_at:
                        packet = None
                        continue
                    epoch = self._selection_epoch
                    action = self._selection_action
                    self._selection_action = None
                    self._processing_frames = 1
                # The vision worker alone mutates its tracker/processor.
                if action == "switch":
                    self.processor.switch_face()
                elif action == "continue":
                    self.processor.continue_tracking()
                checksum = (
                    int(np.sum(packet.pixels, dtype=np.uint64))
                    if self._check_frame_changes
                    else None
                )
                timestamp_ms = int(packet.captured_at * 1_000)
                result = self.processor.process(packet.pixels, timestamp_ms)
                now = time.perf_counter()
                with self._lock:
                    if epoch != self._selection_epoch:
                        self._processing_frames = 0
                        packet = None
                        continue
                    self._status = result.tracking_state
                    self._face_count = result.face_count
                    self._signal = result.signal
                    self._thumbnail = result.thumbnail_rgb
                    self._processed_count += 1
                    if checksum is not None:
                        if self._last_checksum is not None and checksum != self._last_checksum:
                            self._changed_frame_count += 1
                        self._last_checksum = checksum
                    self._max_face_count = max(self._max_face_count, result.face_count)
                    self._max_landmark_count = max(
                        self._max_landmark_count,
                        len(result.signal.landmarks) if result.signal else 0,
                    )
                    self._max_blendshape_count = max(
                        self._max_blendshape_count,
                        len(result.signal.blendshapes) if result.signal else 0,
                    )
                    self._last_processed_callback_index = packet.callback_index
                    if result.signal:
                        self._signal_times.append(now)
                    while self._signal_times and now - self._signal_times[0] > 1.0:
                        self._signal_times.popleft()
                    self._processing_frames = 0
                packet = None
        except BaseException as exc:
            failure = f"Vision failed ({type(exc).__name__}) — reselect"
        finally:
            self._stop_event.set()
            try:
                self.capture.stop()
            except (RuntimeError, TimeoutError) as exc:
                failure = failure or f"Stop failed ({type(exc).__name__})"
            try:
                self.processor.close()
            except Exception as exc:
                failure = failure or f"Vision cleanup failed ({type(exc).__name__})"
            with self._lock:
                self._status = self.capture.stop_reason or failure or "Stopped"
                self._signal = None
                self._thumbnail = None
                self._processing_frames = 0

    def snapshot(self) -> LiveSnapshot:
        with self._lock:
            signal = self._signal
            if signal is not None and time.perf_counter() - signal.timestamp_ms / 1000 > 0.5:
                signal = None
            return LiveSnapshot(
                status=self.capture.stop_reason or self._status,
                signal_rate=float(len(self._signal_times)),
                face_count=self._face_count,
                landmark_count=len(signal.landmarks) if signal else 0,
                blendshape_count=len(signal.blendshapes) if signal else 0,
                thumbnail_rgb=self._thumbnail if signal is not None else None,
                retained_raw_frames=self.capture.frames.retained_count,
                processing_frames=self._processing_frames,
                processed_count=self._processed_count,
                changed_frame_count=self._changed_frame_count,
                max_face_count=self._max_face_count,
                max_landmark_count=self._max_landmark_count,
                max_blendshape_count=self._max_blendshape_count,
                last_processed_callback_index=self._last_processed_callback_index,
                current_signal=signal,
            )
