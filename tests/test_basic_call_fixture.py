import hashlib
import json
import wave
from pathlib import Path

import cv2
import numpy as np

from conversation_copilot.video import FaceProcessor


FIXTURE_DIR = Path(__file__).parents[1] / "conversation_copilot" / "assets" / "f04"


def _manifest(name: str = "basic-video-chat.json") -> dict:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def _pcm(path: Path) -> np.ndarray:
    with wave.open(str(path), "rb") as stream:
        assert (stream.getnchannels(), stream.getsampwidth(), stream.getframerate()) == (1, 2, 16_000)
        return np.frombuffer(stream.readframes(stream.getnframes()), dtype="<i2")


def test_basic_call_fixture_integrity_timing_and_speaker_separation():
    manifest = _manifest()
    assert manifest["fixture_id"] == "f04-basic-video-chat-v1"
    assert len(manifest["turns"]) == 15
    assert len(manifest["expected_cues"]) >= 6
    assert len(manifest["expected_memory_proposals"]) >= 4

    for asset in manifest["assets"].values():
        path = FIXTURE_DIR / asset["file"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == asset["sha256"]

    user = _pcm(FIXTURE_DIR / manifest["assets"]["user_audio"]["file"])
    contact = _pcm(FIXTURE_DIR / manifest["assets"]["contact_audio"]["file"])
    assert len(user) == len(contact) == round(manifest["duration_seconds"] * manifest["sample_rate"])

    previous_end = 0.0
    for turn in manifest["turns"]:
        assert previous_end <= turn["start_seconds"] < turn["end_seconds"]
        previous_end = turn["end_seconds"]
        start = round(turn["start_seconds"] * manifest["sample_rate"])
        end = round(turn["end_seconds"] * manifest["sample_rate"])
        own, other = (contact, user) if turn["speaker"] == "maya" else (user, contact)
        assert np.abs(own[start:end].astype(np.int32)).max() > 100
        assert np.abs(other[start:end].astype(np.int32)).max() == 0


def test_basic_call_fixture_tracks_remote_face_across_authored_poses():
    manifest = _manifest()
    video = cv2.VideoCapture(str(FIXTURE_DIR / manifest["assets"]["video"]["file"]))
    processor = FaceProcessor()
    sampled = {}
    try:
        for turn in manifest["turns"]:
            pose = turn["remote_expression"]
            if turn["speaker"] != "maya" or pose in sampled:
                continue
            seconds = turn["start_seconds"] + 0.2
            video.set(cv2.CAP_PROP_POS_MSEC, seconds * 1_000)
            ok, frame = video.read()
            assert ok
            result = processor.process(cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA), round(seconds * 1_000))
            assert result.signal is not None
            assert result.face_count >= 1
            assert 0.3 < result.signal.face_box.center[0] < 0.7
            assert len(result.signal.landmarks) >= 468
            assert len(result.signal.blendshapes) >= 50
            sampled[pose] = dict(result.signal.blendshapes)
    finally:
        processor.close()
        video.release()

    assert set(sampled) == {"sad", "concerned", "amused", "uncertain", "warm", "tense"}
    reference = sampled["sad"]
    for pose, values in sampled.items():
        if pose != "sad":
            assert max(abs(values[key] - reference[key]) for key in values.keys() & reference.keys()) > 0.05


def test_heygen_call_fixture_media_and_remote_face_replay():
    manifest = _manifest("heygen-video-chat.json")
    path = FIXTURE_DIR / manifest["asset"]["file"]
    assert manifest["fixture_id"] == "f04-heygen-video-chat-v1"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == manifest["asset"]["sha256"]

    video = cv2.VideoCapture(str(path))
    processor = FaceProcessor()
    samples = []
    try:
        assert video.isOpened()
        assert round(video.get(cv2.CAP_PROP_FRAME_WIDTH)) == manifest["media"]["width"]
        assert round(video.get(cv2.CAP_PROP_FRAME_HEIGHT)) == manifest["media"]["height"]
        duration = video.get(cv2.CAP_PROP_FRAME_COUNT) / video.get(cv2.CAP_PROP_FPS)
        assert abs(duration - manifest["media"]["duration_seconds"]) < 0.05

        for seconds in manifest["validation"]["face_sample_seconds"]:
            video.set(cv2.CAP_PROP_POS_MSEC, seconds * 1_000)
            ok, frame = video.read()
            assert ok
            result = processor.process(cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA), round(seconds * 1_000))
            assert result.signal is not None
            assert result.face_count >= 1
            assert 0.35 < result.signal.face_box.center[0] < 0.75
            assert len(result.signal.landmarks) >= 468
            assert len(result.signal.blendshapes) >= 50
            samples.append(dict(result.signal.blendshapes))
    finally:
        processor.close()
        video.release()

    reference = samples[0]
    threshold = manifest["validation"]["minimum_blendshape_delta"]
    assert all(
        max(abs(values[key] - reference[key]) for key in values.keys() & reference.keys()) > threshold
        for values in samples[1:]
    )
