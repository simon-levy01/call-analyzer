from __future__ import annotations

import argparse
import gc
import json
import sys
import tempfile
import time
import wave
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from .audio import (
    MODEL_CACHE,
    MODEL_NAME,
    MODEL_REVISION,
    TRANSCRIBE_OPTIONS,
    _load_local_model,
    _validation_error_counts,
    _validation_words,
    prepare_transcription_runtime,
)

BENCHMARK_CACHE = MODEL_CACHE.parent / "benchmark-models"
FAIR_MODEL_OPTIONS = {
    "beam_size": 5,
    "temperature": 0.0,
    "word_timestamps": True,
    "vad_filter": True,
    "condition_on_previous_text": False,
}


@dataclass(frozen=True, slots=True)
class Profile:
    name: str
    model: str
    options: dict
    compute_type: str = "float16"
    revision: str | None = None
    local_cache: bool = False
    languages: frozenset[str] = frozenset({"en", "he"})
    production: bool = False


PROFILES = {
    "current": Profile(
        "Current project",
        MODEL_NAME,
        dict(TRANSCRIBE_OPTIONS),
        revision=MODEL_REVISION,
        local_cache=True,
        production=True,
    ),
    "faster-whisper-transcriber": Profile(
        "Faster-Whisper-Transcriber",
        "ctranslate2-4you/distil-whisper-large-v3-ct2-bfloat16",
        {
            "beam_size": 5,
            "temperature": 0.0,
            "without_timestamps": True,
            "vad_filter": True,
            "condition_on_previous_text": False,
        },
        "bfloat16",
        "844752f8428130093b17f8192c59b79a1113b1d5",
        languages=frozenset({"en"}),
    ),
    "stage-whisper": Profile(
        "Stage Whisper model proxy",
        "Systran/faster-whisper-base",
        {"beam_size": 5, "temperature": 0.0},
        revision="ebe41f70d5b6dfa9166e2c581c45c9c0cfc57b66",
    ),
    "noscribe": Profile(
        "noScribe precise",
        MODEL_NAME,
        {
            "beam_size": 1,
            "temperature": 0.0,
            "word_timestamps": True,
            "vad_filter": True,
        },
        revision=MODEL_REVISION,
        local_cache=True,
    ),
    "ivrit-large-v3": Profile(
        "ivrit.ai large-v3",
        "ivrit-ai/whisper-large-v3-ct2",
        dict(FAIR_MODEL_OPTIONS),
        revision="e9ed4a4a98d761b0f617d668303de2c514236c66",
    ),
    "ivrit-large-v3-turbo": Profile(
        "ivrit.ai large-v3-turbo",
        "ivrit-ai/whisper-large-v3-turbo-ct2",
        dict(FAIR_MODEL_OPTIONS),
        revision="72ad623a37947395efcc3933132353790e5a12f5",
    ),
    "ivrit-bilingual-v2-d4": Profile(
        "ivrit.ai bilingual v2-d4",
        "ivrit-ai/faster-whisper-v2-d4",
        dict(FAIR_MODEL_OPTIONS),
        revision="45ef6dd536dfbf6e8633796157cad00f428142cc",
    ),
    "general-large-v3": Profile(
        "General Whisper large-v3",
        "Systran/faster-whisper-large-v3",
        dict(FAIR_MODEL_OPTIONS),
        revision="edaa852ec7e145841d8ffdb056a99866b5f0a478",
    ),
    "current-fair": Profile(
        "Current large-v3-turbo (fair settings)",
        MODEL_NAME,
        dict(FAIR_MODEL_OPTIONS),
        revision=MODEL_REVISION,
        local_cache=True,
    ),
    "original-small": Profile(
        "Original project small",
        "Systran/faster-whisper-small",
        dict(FAIR_MODEL_OPTIONS),
        revision="536b0662742c02347bc0e980a01041f333bce120",
    ),
    "stage-base-fair": Profile(
        "Stage Whisper base (fair settings)",
        "Systran/faster-whisper-base",
        dict(FAIR_MODEL_OPTIONS),
        revision="ebe41f70d5b6dfa9166e2c581c45c9c0cfc57b66",
    ),
}
DEFAULT_PROFILES = ("current", "faster-whisper-transcriber", "stage-whisper", "noscribe")


@dataclass(frozen=True, slots=True)
class Case:
    name: str
    media: Path
    reference: str
    language: str


@dataclass(frozen=True, slots=True)
class CaseResult:
    case: str
    language: str
    wer: float | None
    seconds: float
    error: str | None = None


@dataclass(frozen=True, slots=True)
class ProfileResult:
    profile: str
    model: str
    wer: float | None
    seconds: float
    failed_cases: int
    cases: list[CaseResult]


def _call_like(source: Path, destination: Path, snr_db: float = 8.0) -> None:
    with wave.open(str(source), "rb") as stream:
        if stream.getnchannels() != 1 or stream.getsampwidth() != 2:
            raise ValueError("call-like input must be mono 16-bit PCM WAV")
        params = stream.getparams()
        samples = np.frombuffer(stream.readframes(stream.getnframes()), dtype="<i2").astype(
            np.float32
        )
    if len(samples) < 2:
        raise ValueError("call-like input must contain at least two samples")
    paired = samples[: len(samples) // 2 * 2].reshape(-1, 2).mean(axis=1)
    narrow = np.repeat(paired, 2)
    if len(narrow) < len(samples):
        narrow = np.append(narrow, narrow[-1])
    rms = float(np.sqrt(np.mean(narrow * narrow)))
    noise = np.random.default_rng(0).normal(
        0, rms / (10 ** (snr_db / 20)), len(narrow)
    )
    output = np.clip(narrow + noise, -32768, 32767).astype("<i2")
    with wave.open(str(destination), "wb") as stream:
        stream.setparams(params)
        stream.writeframes(output.tobytes())


def fixture_cases(temp_dir: Path, clean_only: bool = False, language: str = "en") -> list[Case]:
    fixture_dir = Path(__file__).with_name("assets") / "audio"
    manifest = json.loads((fixture_dir / "manifest.json").read_text(encoding="utf-8"))
    cases: list[Case] = []
    for filename in ("english.wav", "hebrew.wav"):
        expected = manifest["clips"][filename]
        if expected["language"] != language:
            continue
        source = fixture_dir / filename
        cases.append(Case(filename, source, expected["text"], expected["language"]))
        if not clean_only:
            degraded = temp_dir / filename.replace(".wav", "-call-like.wav")
            _call_like(source, degraded)
            cases.append(
                Case(degraded.name, degraded, expected["text"], expected["language"])
            )
    return cases


def manifest_cases(path: Path) -> list[Case]:
    entries = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(entries, list) or not entries:
        raise ValueError("manifest must be a non-empty JSON list")
    cases = []
    for entry in entries:
        if (
            not isinstance(entry, dict)
            or not isinstance(entry.get("media"), str)
            or not isinstance(entry.get("reference"), str)
            or entry.get("language") not in {"en", "he"}
        ):
            raise ValueError("manifest entries require media, reference, and en/he language")
        media = path.parent / entry["media"]
        if not media.is_file():
            raise ValueError(f"manifest media does not exist: {media}")
        cases.append(Case(media.name, media, entry["reference"], entry["language"]))
    return cases


def _transcript(model, case: Case, options: dict) -> str:
    segments, _info = model.transcribe(
        str(case.media), language=case.language, task="transcribe", **options
    )
    return " ".join(segment.text.strip() for segment in segments).strip()


def benchmark_profile(
    profile: Profile, cases: list[Case], *, allow_download: bool = False
) -> ProfileResult:
    if not cases:
        raise ValueError("benchmark requires at least one case")
    if profile.local_cache and (
        profile.model != MODEL_NAME
        or profile.revision != MODEL_REVISION
        or profile.compute_type != "float16"
        or (profile.production and profile.options != TRANSCRIBE_OPTIONS)
    ):
        raise ValueError("local profile must match the pinned production model")
    if any(not _validation_words(case.reference, case.language) for case in cases):
        raise ValueError("reference text must contain at least one word")
    results: list[CaseResult] = []
    edits = words = 0
    model = None
    try:
        if profile.local_cache:
            model = _load_local_model()
        else:
            prepare_transcription_runtime()
            from faster_whisper import WhisperModel

            model = WhisperModel(
                profile.model,
                device="cuda",
                compute_type=profile.compute_type,
                download_root=str(BENCHMARK_CACHE),
                local_files_only=not allow_download,
                revision=profile.revision,
            )
        for case in cases:
            started = time.perf_counter()
            error = None
            try:
                hypothesis = _transcript(model, case, profile.options)
                case_edits, reference_words = _validation_error_counts(
                    case.reference, hypothesis, case.language
                )
                wer = case_edits / reference_words
                edits += case_edits
                words += reference_words
            except Exception as exc:
                wer = None
                error = f"{type(exc).__name__}: {exc}"
            elapsed = time.perf_counter() - started
            results.append(CaseResult(case.name, case.language, wer, elapsed, error))
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
        results.extend(
            CaseResult(case.name, case.language, None, 0.0, error)
            for case in cases[len(results) :]
        )
    finally:
        if model is not None:
            del model
        gc.collect()
    failures = sum(item.error is not None for item in results)
    return ProfileResult(
        profile.name,
        profile.model,
        None if failures else edits / max(1, words),
        sum(item.seconds for item in results),
        failures,
        results,
    )


def format_report(results: list[ProfileResult], corpus: str = "built-in fixture") -> str:
    ranked = sorted(
        results,
        key=lambda item: (
            item.failed_cases > 0,
            item.wer is None,
            item.wer if item.wer is not None else float("inf"),
            item.seconds,
        ),
    )
    case_count = max((len(result.cases) for result in results), default=0)
    lines = ["Transcription accuracy benchmark", f"Corpus: {corpus} ({case_count} clips)", ""]
    for index, result in enumerate(ranked, 1):
        wer = f"{result.wer:.3f}" if result.wer is not None else "n/a"
        lines.append(
            f"{index}. {result.profile} ({result.model}): "
            f"WER {wer}, {result.seconds:.2f}s, failures {result.failed_cases}"
        )
        for case in result.cases:
            detail = f"; {case.error}" if case.error else ""
            wer = f"{case.wer:.3f}" if case.wer is not None else "n/a"
            lines.append(
                f"   {case.case} [{case.language}]: WER {wer}, "
                f"{case.seconds:.2f}s{detail}"
            )
    eligible = [item for item in ranked if not item.failed_cases and item.wer is not None]
    if not eligible:
        lines.append("\nAccuracy result: no profile completed successfully.")
    elif len(eligible) == 1:
        lines.append("\nAccuracy result: one eligible profile; no comparison winner.")
    elif len(eligible) > 1 and eligible[0].wer == eligible[1].wer:
        lines.append("\nAccuracy result: tie.")
    else:
        lines.append(f"\nAccuracy leader: {eligible[0].profile}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    parser = argparse.ArgumentParser(description="Compare linked Whisper applications by WER")
    parser.add_argument("--profiles", nargs="+", choices=PROFILES, default=list(DEFAULT_PROFILES))
    parser.add_argument("--download-models", action="store_true")
    parser.add_argument("--clean-only", action="store_true")
    parser.add_argument("--media", type=Path)
    parser.add_argument("--reference", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--language", choices=("en", "he"), default="en")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    custom = (args.media, args.reference)
    if args.manifest is not None and any(custom):
        parser.error("--manifest cannot be combined with --media or --reference")
    if any(custom) and not all(custom):
        parser.error("--media and --reference must be supplied together")
    if (any(custom) or args.manifest is not None) and args.clean_only:
        parser.error("--clean-only applies only to the built-in WAV fixtures")
    if args.media is not None and not args.media.is_file():
        parser.error(f"media file does not exist: {args.media}")
    if args.reference is not None and not args.reference.is_file():
        parser.error(f"reference file does not exist: {args.reference}")
    if args.manifest is not None and not args.manifest.is_file():
        parser.error(f"manifest file does not exist: {args.manifest}")
    compatible_profiles = [
        name for name in args.profiles if args.language in PROFILES[name].languages
    ]
    if not compatible_profiles:
        parser.error(f"no selected profile supports language {args.language}")

    with tempfile.TemporaryDirectory(prefix="transcription-benchmark-") as temp:
        cases = manifest_cases(args.manifest) if args.manifest else (
            [
                Case(
                    args.media.name,
                    args.media,
                    args.reference.read_text(encoding="utf-8-sig").strip(),
                    args.language,
                )
            ]
            if all(custom)
            else fixture_cases(Path(temp), args.clean_only, args.language)
        )
        if any(not _validation_words(case.reference, case.language) for case in cases):
            parser.error("reference text must contain at least one word")
        if any(case.language != args.language for case in cases):
            parser.error("every manifest case must match --language")
        results = [
            benchmark_profile(PROFILES[name], cases, allow_download=args.download_models)
            for name in compatible_profiles
        ]
    print(
        json.dumps([asdict(result) for result in results], ensure_ascii=True, indent=2)
        if args.json
        else format_report(
            results,
            f"manifest {args.manifest}"
            if args.manifest
            else (f"media {args.media}" if args.media else "built-in fixture"),
        )
    )
    return 1 if any(result.failed_cases for result in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
