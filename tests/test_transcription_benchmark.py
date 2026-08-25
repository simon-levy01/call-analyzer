import json
import wave
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

import conversation_copilot.transcription_benchmark as benchmark_module
from conversation_copilot.transcription_benchmark import (
    Case,
    CaseResult,
    Profile,
    ProfileResult,
    _call_like,
    benchmark_profile,
    fixture_cases,
    format_report,
    manifest_cases,
)


def test_call_like_is_deterministic(tmp_path: Path):
    source = tmp_path / "source.wav"
    first = tmp_path / "first.wav"
    second = tmp_path / "second.wav"
    samples = (np.sin(np.arange(1601) / 10) * 10_000).astype("<i2")
    with wave.open(str(source), "wb") as stream:
        stream.setparams((1, 2, 16_000, 0, "NONE", "not compressed"))
        stream.writeframes(samples.tobytes())

    _call_like(source, first)
    _call_like(source, second)

    assert first.read_bytes() == second.read_bytes()
    assert first.read_bytes() != source.read_bytes()
    with wave.open(str(first), "rb") as stream:
        assert stream.getnchannels() == 1
        assert stream.getsampwidth() == 2
        assert stream.getnframes() == len(samples)


def test_call_like_rejects_unsupported_wave_format(tmp_path: Path):
    source = tmp_path / "stereo.wav"
    with wave.open(str(source), "wb") as stream:
        stream.setparams((2, 2, 16_000, 0, "NONE", "not compressed"))
        stream.writeframes(np.zeros(8, dtype="<i2").tobytes())

    with pytest.raises(ValueError, match="mono 16-bit"):
        _call_like(source, tmp_path / "output.wav")


def test_report_ranks_accuracy_and_never_names_a_failed_profile():
    report = format_report(
        [
            ProfileResult("worse", "a", 0.2, 1.0, 0, [CaseResult("x", "en", 0.2, 1.0)]),
            ProfileResult("better", "b", 0.1, 2.0, 0, [CaseResult("x", "en", 0.1, 2.0)]),
            ProfileResult(
                "failed", "c", None, 0.0, 1, [CaseResult("x", "en", None, 0.0, "boom")]
            ),
        ]
    )

    assert report.index("better") < report.index("worse")
    assert "Corpus: built-in fixture (1 clips)" in report
    assert "Accuracy leader: better" in report
    assert "failed (c): WER n/a" in report


def test_benchmark_profile_reports_model_load_failure(monkeypatch, tmp_path: Path):
    def fail():
        raise RuntimeError("missing")

    monkeypatch.setattr(benchmark_module, "_load_local_model", fail)
    result = benchmark_profile(
        Profile(
            "local",
            benchmark_module.MODEL_NAME,
            {},
            revision=benchmark_module.MODEL_REVISION,
            local_cache=True,
        ),
        [Case("clip", tmp_path / "missing.wav", "hello", "en")],
    )

    assert result.wer is None
    assert result.failed_cases == 1
    assert "RuntimeError: missing" in result.cases[0].error
    assert "no profile completed successfully" in format_report([result])


def test_benchmark_profile_rejects_mislabeled_local_model(tmp_path: Path):
    with pytest.raises(ValueError, match="pinned production model"):
        benchmark_profile(
            Profile("local", "wrong-model", {}, local_cache=True),
            [Case("clip", tmp_path / "missing.wav", "hello", "en")],
        )


def test_benchmark_profile_rejects_empty_case_list():
    with pytest.raises(ValueError, match="at least one case"):
        benchmark_profile(benchmark_module.PROFILES["current"], [])


def test_production_profile_rejects_decode_option_drift(tmp_path: Path):
    changed = replace(benchmark_module.PROFILES["current"], options={"beam_size": 5})
    with pytest.raises(ValueError, match="pinned production model"):
        benchmark_profile(changed, [Case("clip", tmp_path / "clip.wav", "hello", "en")])


def test_benchmark_profile_excludes_decode_failure(monkeypatch, tmp_path: Path):
    class Model:
        def transcribe(self, media, **_options):
            if media.endswith("bad.wav"):
                raise RuntimeError("decode")
            return [SimpleNamespace(text="hello")], None

    monkeypatch.setattr(benchmark_module, "_load_local_model", Model)
    result = benchmark_profile(
        Profile(
            "local",
            benchmark_module.MODEL_NAME,
            {},
            revision=benchmark_module.MODEL_REVISION,
            local_cache=True,
        ),
        [
            Case("good.wav", tmp_path / "good.wav", "hello", "en"),
            Case("bad.wav", tmp_path / "bad.wav", "hello", "en"),
        ],
    )

    assert result.wer is None
    assert result.failed_cases == 1
    assert result.cases[0].wer == 0.0
    assert result.cases[1].wer is None


def test_benchmark_profile_micro_averages_exact_edit_counts(monkeypatch, tmp_path: Path):
    class Model:
        def transcribe(self, media, **_options):
            text = "one" if media.endswith("long.wav") else "hello"
            return [SimpleNamespace(text=text)], None

    monkeypatch.setattr(benchmark_module, "_load_local_model", Model)
    result = benchmark_profile(
        Profile(
            "local",
            benchmark_module.MODEL_NAME,
            {},
            revision=benchmark_module.MODEL_REVISION,
            local_cache=True,
        ),
        [
            Case("long.wav", tmp_path / "long.wav", "one two", "en"),
            Case("short.wav", tmp_path / "short.wav", "hello", "en"),
        ],
    )

    assert result.failed_cases == 0
    assert result.wer == pytest.approx(1 / 3)
    assert [case.wer for case in result.cases] == [0.5, 0.0]


def test_main_returns_failure_when_a_profile_fails(monkeypatch, tmp_path: Path):
    case = Case("clip", tmp_path / "clip.wav", "hello", "en")
    failed = ProfileResult(
        "failed", "model", None, 0.0, 1, [CaseResult("clip", "en", None, 0.0, "boom")]
    )
    monkeypatch.setattr(benchmark_module, "fixture_cases", lambda *_args: [case])
    monkeypatch.setattr(benchmark_module, "benchmark_profile", lambda *_args, **_kwargs: failed)

    assert benchmark_module.main(["--profiles", "current", "--clean-only"]) == 1


def test_fixture_cases_filters_language(tmp_path: Path):
    cases = fixture_cases(tmp_path, clean_only=True, language="en")

    assert [case.language for case in cases] == ["en"]
    assert [case.name for case in cases] == ["english.wav"]


def test_manifest_cases_loads_external_corpus(tmp_path: Path):
    media = tmp_path / "clip.wav"
    media.write_bytes(b"fixture")
    manifest = tmp_path / "cases.json"
    manifest.write_text(
        json.dumps([{"media": media.name, "reference": "שלום", "language": "he"}]),
        encoding="utf-8",
    )

    cases = manifest_cases(manifest)

    assert cases == [Case("clip.wav", media, "שלום", "he")]


@pytest.mark.parametrize(
    "payload, message",
    [
        ({}, "non-empty JSON list"),
        ([], "non-empty JSON list"),
        ([{"media": "clip.wav", "reference": "hello", "language": "fr"}], "en/he"),
        ([{"media": 3, "reference": "hello", "language": "en"}], "en/he"),
        ([{"media": "missing.wav", "reference": "hello", "language": "en"}], "does not exist"),
    ],
)
def test_manifest_cases_rejects_invalid_input(tmp_path: Path, payload, message):
    manifest = tmp_path / "cases.json"
    manifest.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match=message):
        manifest_cases(manifest)


@pytest.mark.parametrize(
    "arguments",
    [
        ["--manifest", "cases.json", "--media", "clip.wav"],
        ["--media", "clip.wav"],
        ["--media", "clip.wav", "--reference", "ref.txt", "--clean-only"],
        ["--media", "missing.wav", "--reference", "missing.txt"],
        ["--manifest", "missing.json"],
    ],
)
def test_main_rejects_invalid_input_combinations(arguments):
    with pytest.raises(SystemExit) as error:
        benchmark_module.main(arguments)

    assert error.value.code == 2


def test_main_rejects_language_with_no_compatible_profile():
    with pytest.raises(SystemExit) as error:
        benchmark_module.main(
            ["--profiles", "faster-whisper-transcriber", "--language", "he", "--clean-only"]
        )

    assert error.value.code == 2
