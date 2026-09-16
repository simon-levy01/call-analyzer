"""Local DISFA preparation and existing MediaPipe development probe; no cloud calls."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "build/datasets/DISFA"
ACTIONS = {4: "brow_lowering", 12: "smile_like", 15: "mouth_corner_lowering"}
DEVELOPMENT = {"SN001", "SN002", "SN003"}


def labels(raw: bytes) -> list[int]:
    rows = [line.split(",") for line in raw.decode("ascii").splitlines() if line.strip()]
    result = []
    for expected, row in enumerate(rows, 1):
        if len(row) != 2 or int(row[0]) != expected or not 0 <= int(row[1]) <= 5:
            raise ValueError("invalid or nonconsecutive DISFA label row")
        result.append(int(row[1]))
    if not result:
        raise ValueError("empty labels")
    return result


def episodes(values: list[int], minimum: int = 2) -> list[tuple[int, int]]:
    """Zero-based, half-open runs. Intensity 1 stays weak evidence, not absence."""
    result = []
    start = None
    for index, value in enumerate([*values, 0]):
        if value >= minimum and start is None:
            start = index
        elif value < minimum and start is not None:
            result.append((start, index))
            start = None
    return result


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def prepare(out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=False)
    # Split fixed by identifiers before examining labels or detector responses.
    split = {"development": sorted(DEVELOPMENT), "held_out": "all other subjects",
             "camera": "left only; right camera is the same subjects, not independent",
             "strong_label_minimum": 2, "weak_label": 1, "absent_label": 0,
             "purpose": "signal development; not the 144 language-model comparisons"}
    (out / "split.json").write_text(json.dumps(split, indent=2), encoding="utf8")
    inventory = []
    for path in sorted(DATA.iterdir()):
        if path.is_file():
            inventory.append({"file": path.name, "bytes": path.stat().st_size,
                              "sha256": digest(path)})
    parsed = {}
    with zipfile.ZipFile(DATA / "ActionUnit_Labels.zip") as archive:
        for member in archive.namelist():
            match = re.fullmatch(r"(SN\d{3})/\1_au(\d+)\.txt", member)
            if match:
                subject, action = match[1], int(match[2])
                if (subject, action) in parsed:
                    raise ValueError("duplicate labels")
                parsed[subject, action] = labels(archive.read(member))
    subjects = sorted({subject for subject, _ in parsed})
    if not DEVELOPMENT <= set(subjects):
        raise ValueError("development subjects missing")
    for subject in subjects:
        actions = {action for person, action in parsed if person == subject}
        if actions != {1, 2, 4, 5, 6, 9, 12, 15, 17, 20, 25, 26}:
            raise ValueError(f"incomplete action labels: {subject}")
        if len({len(values) for (person, _), values in parsed.items() if person == subject}) != 1:
            raise ValueError(f"inconsistent label lengths: {subject}")
    coverage = []
    for subject in subjects:
        for action in ACTIONS:
            values = parsed[subject, action]
            runs = episodes(values)
            coverage.append({"subject": subject, "action": action, "frames": len(values),
                             "positive_frames": sum(v >= 2 for v in values),
                             "weak_frames": values.count(1), "episodes": len(runs),
                             "holds_ge_3s_at_20fps": sum(b - a >= 60 for a, b in runs)})
    # Up to six fixed, label-selected development windows; never inspect holdout signals.
    windows = []
    for action in ACTIONS:
        candidates = [(a, b, subject) for subject in sorted(DEVELOPMENT)
                      for a, b in episodes(parsed[subject, action]) if b - a >= 60]
        if not candidates:
            # Preserve the subject split when a rare action has no sustained hold.
            candidates = sorted(((a, b, subject) for subject in sorted(DEVELOPMENT)
                                 for a, b in episodes(parsed[subject, action])),
                                key=lambda item: (-(item[1] - item[0]), item[2], item[0]))
        if candidates:
            a, b, subject = candidates[0]
            windows.append({"subject": subject, "action": action, "kind": "positive",
                            "start_frame": max(0, a - 20), "end_frame": min(b + 20, a + 120),
                            "label_episode": [a, b]})
    for subject in sorted(DEVELOPMENT):
        absent = [int(all(parsed[subject, au][i] == 0 for au in ACTIONS))
                  for i in range(len(parsed[subject, 4]))]
        runs = episodes(absent, 1)
        chosen = next(((a, b) for a, b in runs if b - a >= 80), None)
        if chosen:
            windows.append({"subject": subject, "kind": "neutral_control",
                            "start_frame": chosen[0], "end_frame": chosen[0] + 80})
    videos = {}
    with zipfile.ZipFile(DATA / "Videos_LeftCamera.zip") as archive:
        for info in archive.infolist():
            match = re.fullmatch(r"LeftVideo(SN\d{3})_comp\.avi", info.filename, re.I)
            if match:
                videos[match[1]] = info.filename
        if set(videos) != set(subjects):
            raise ValueError("left-video and annotation subject sets differ")
        for subject in sorted(DEVELOPMENT):
            target = out / videos[subject]
            # Exact whitelisted basename, never generic extractall on supplied archives.
            with archive.open(videos[subject]) as source, target.open("xb") as destination:
                shutil.copyfileobj(source, destination)
    result = {"inventory": inventory, "subjects": subjects, "coverage": coverage,
              "development_windows": windows, "left_video_members": videos,
              "label_indexing": "1-based file rows; zero-based half-open windows",
              "notes": ["XLS documents old AAM landmark failures; no automatic exclusion.",
                        "Landmark RAR/calibration/stimulus unused; original archives untouched.",
                        "Positive labels are AU configurations, not inner emotion."]}
    (out / "manifest.json").write_text(json.dumps(result, indent=2), encoding="utf8")
    return result


def probe(out: Path) -> None:
    import sys
    import importlib.metadata
    sys.path.insert(0, str(ROOT))
    import av
    import cv2
    from conversation_copilot.video import FaceProcessor

    manifest = json.loads((out / "manifest.json").read_text(encoding="utf8"))
    provenance = {"runner_sha256": digest(Path(__file__)),
                  "video_source_sha256": digest(ROOT / "conversation_copilot/video.py"),
                  "packages": {name: importlib.metadata.version(name) for name in ("mediapipe", "av", "numpy")},
                  "model_assets": {name: digest(ROOT / "conversation_copilot/assets" / name)
                                   for name in ("face_landmarker.task", "blaze_face_short_range.tflite")},
                  "cloud_requests": 0, "annotation_access": "labels local; no human media uploaded"}
    with (out / "probe-provenance.json").open("x", encoding="utf8") as file:
        json.dump(provenance, file, indent=2)
    names = ("mouthSmileLeft", "mouthSmileRight", "browDownLeft", "browDownRight",
             "mouthFrownLeft", "mouthFrownRight", "jawOpen")
    report = []
    with (out / "development-signals.jsonl").open("x", encoding="utf8") as output:
        for subject in sorted(DEVELOPMENT):
            processor = FaceProcessor()
            selected = [w for w in manifest["development_windows"] if w["subject"] == subject]
            count = 0
            last_pts = None
            detected = 0
            try:
                with av.open(str(out / manifest["left_video_members"][subject])) as container:
                    stream = container.streams.video[0]
                    rate = float(stream.average_rate)
                    if rate != 20:
                        raise ValueError(f"unexpected frame rate: {rate}")
                    for index, frame in enumerate(container.decode(stream)):
                        pts = float(frame.pts * frame.time_base)
                        if last_pts is not None and pts <= last_pts:
                            raise ValueError("nonmonotonic PTS")
                        if abs(pts - index / rate) > 0.001:
                            raise ValueError("video/label time alignment mismatch")
                        last_pts = pts
                        count += 1
                        if not any(w["start_frame"] <= index < w["end_frame"] for w in selected):
                            continue
                        result = processor.process(cv2.cvtColor(frame.to_ndarray(format="bgr24"),
                                                               cv2.COLOR_BGR2BGRA), round(pts * 1000))
                        signal = result.signal
                        scores = dict(signal.blendshapes) if signal else {}
                        if signal and not set(names) <= scores.keys():
                            raise ValueError("required installed blendshape category absent")
                        detected += bool(signal)
                        output.write(json.dumps({"subject": subject, "frame": index,
                                                 "pts_seconds": pts, "available": bool(signal),
                                                 "scores": {name: scores[name] for name in names if name in scores}}) + "\n")
                    expected = next(row["frames"] for row in manifest["coverage"] if row["subject"] == subject)
                    if count != expected:
                        raise ValueError(f"frame/label count mismatch {subject}: {count} != {expected}")
                report.append({"subject": subject, "decoded_frames": count, "fps": rate,
                               "last_pts": last_pts, "detected_probe_frames": detected})
            finally:
                processor.close()
    (out / "development-probe.json").write_text(json.dumps(report, indent=2), encoding="utf8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--probe", action="store_true", help="existing local MediaPipe only; no LLM")
    args = parser.parse_args()
    args.output = args.output.resolve()
    if not args.output.is_relative_to(ROOT / "build"):
        parser.error("private dataset evidence must stay inside Git-ignored build/")
    if args.probe:
        probe(args.output)
    else:
        prepare(args.output)
