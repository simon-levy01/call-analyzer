from __future__ import annotations

import math
import logging
import os
import queue
import site
import sys
import statistics
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable

import numpy as np

from .models import SpeakerRole

MODEL_CACHE = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "ConversationCopilot" / "models"
MODEL_NAME = "mobiuslabsgmbh/faster-whisper-large-v3-turbo"
MODEL_REVISION = "0a363e9161cbc7ed1431c9597a8ceaf0c4f78fcf"
MODEL_CACHE_DIRECTORY = "models--" + MODEL_NAME.replace("/", "--")
PINNED_MODEL_FILES = {
    "config.json",
    "model.bin",
    "preprocessor_config.json",
    "tokenizer.json",
    "vocabulary.json",
}
SUPPORTED_TRANSCRIPTION_LANGUAGES = {"English": "en"}
TRANSCRIBE_OPTIONS = {
    "beam_size": 1,
    "best_of": 1,
    "temperature": 0.0,
    "chunk_length": 15,
    "word_timestamps": True,
    "vad_filter": True,
    "condition_on_previous_text": False,
}
SAMPLE_RATE = 16_000
SAMPLE_WIDTH = 2
FRAMES_PER_BUFFER = 1_024
MAX_CALLBACK_SECONDS = 2
MAX_UTTERANCE_SECONDS = 7
MAX_RAW_BYTES = 12 * 1024 * 1024
MAX_JOBS = 4
MAX_RESULTS = 512
LOOPBACK_THRESHOLD = 100.0
DEFAULT_MICROPHONE_THRESHOLD = 100.0
WATERMARK_SAFETY_SECONDS = 0.25
MIN_VOICE_SAMPLES = int(0.3 * SAMPLE_RATE)
START_VOICE_SAMPLES = int(0.1 * SAMPLE_RATE)
END_SILENCE_SAMPLES = int(0.6 * SAMPLE_RATE)
MAX_UTTERANCE_SAMPLES = MAX_UTTERANCE_SECONDS * SAMPLE_RATE
REMOTE_ENERGY_BASELINE_UTTERANCES = 2
REMOTE_ENERGY_BASELINE_LIMIT = 20
MAX_CLIPPED_SAMPLE_RATIO = 0.01
LOGGER = logging.getLogger(__name__)


def transcription_language_labels() -> tuple[str, ...]:
    return tuple(SUPPORTED_TRANSCRIPTION_LANGUAGES)


def production_transcription_language(label: str) -> str:
    return SUPPORTED_TRANSCRIPTION_LANGUAGES[label]


class AudioUnavailable(RuntimeError):
    pass


class DeviceChanged(AudioUnavailable):
    pass


@dataclass(frozen=True, slots=True)
class AudioDeviceRecord:
    index: int
    name: str
    host_api_index: int
    host_api_name: str
    input_channels: int
    output_channels: int
    sample_rate: float
    is_loopback: bool

    @classmethod
    def from_info(cls, info: dict, host_api_name: str) -> "AudioDeviceRecord":
        return cls(
            index=int(info["index"]),
            name=str(info["name"]),
            host_api_index=int(info["hostApi"]),
            host_api_name=host_api_name,
            input_channels=int(info["maxInputChannels"]),
            output_channels=int(info["maxOutputChannels"]),
            sample_rate=float(info["defaultSampleRate"]),
            is_loopback=bool(info.get("isLoopbackDevice", False)),
        )


@dataclass(frozen=True, slots=True)
class PlaybackSelection:
    render: AudioDeviceRecord
    loopback: AudioDeviceRecord


def device_labels(records: list[AudioDeviceRecord]) -> list[str]:
    counts: dict[str, int] = {}
    for record in records:
        counts[record.name] = counts.get(record.name, 0) + 1
    return [
        f"{record.name} [WASAPI #{record.index}]" if counts[record.name] > 1 else record.name
        for record in records
    ]


class AudioDeviceCatalog:
    """One PortAudio enumeration context; selections die with this object."""

    def __init__(self, backend=None, module=None) -> None:
        if backend is None:
            import pyaudiowpatch as module

            backend = module.PyAudio()
        self.backend = backend
        self.module = module
        self.closed = False
        self._close_lock = threading.Lock()
        self.microphones: list[AudioDeviceRecord] = []
        self.playbacks: list[PlaybackSelection] = []
        self.default_microphone_index: int | None = None
        self.default_render_index: int | None = None
        try:
            self._enumerate()
        except Exception:
            self.closed = True
            self.backend.terminate()
            raise

    def _host_name(self, index: int) -> str:
        return str(self.backend.get_host_api_info_by_index(index)["name"])

    def _record(self, info: dict) -> AudioDeviceRecord:
        return AudioDeviceRecord.from_info(info, self._host_name(int(info["hostApi"])))

    def _scan(
        self,
    ) -> tuple[list[AudioDeviceRecord], list[PlaybackSelection], int | None, int | None]:
        try:
            wasapi = self.backend.get_host_api_info_by_type(self.module.paWASAPI)
        except (AttributeError, OSError) as exc:
            raise AudioUnavailable("Windows WASAPI is unavailable") from exc
        wasapi_index = int(wasapi["index"])
        records = [
            self._record(self.backend.get_device_info_by_index(index))
            for index in range(self.backend.get_device_count())
        ]
        microphones = [
            record
            for record in records
            if record.host_api_index == wasapi_index
            and record.input_channels > 0
            and not record.is_loopback
        ]
        renders = [
            record
            for record in records
            if record.host_api_index == wasapi_index
            and record.output_channels > 0
            and not record.is_loopback
        ]
        playbacks: list[PlaybackSelection] = []
        for render in renders:
            try:
                loopback = self._record(
                    self.backend.get_wasapi_loopback_analogue_by_index(render.index)
                )
            except (LookupError, OSError):
                continue
            if loopback.is_loopback and loopback.input_channels > 0:
                playbacks.append(PlaybackSelection(render, loopback))
        default_input = int(wasapi.get("defaultInputDevice", -1))
        default_output = int(wasapi.get("defaultOutputDevice", -1))
        default_microphone = (
            default_input if any(record.index == default_input for record in microphones) else None
        )
        default_render = (
            default_output if any(item.render.index == default_output for item in playbacks) else None
        )
        return microphones, playbacks, default_microphone, default_render

    def _enumerate(self) -> None:
        (
            self.microphones,
            self.playbacks,
            self.default_microphone_index,
            self.default_render_index,
        ) = self._scan()

    def revalidate(
        self, microphone: AudioDeviceRecord, playback: PlaybackSelection
    ) -> None:
        self._revalidate(microphone, playback)

    def revalidate_microphone(self, microphone: AudioDeviceRecord) -> None:
        self._revalidate(microphone, None)

    def _revalidate(
        self, microphone: AudioDeviceRecord, playback: PlaybackSelection | None
    ) -> None:
        if self.closed:
            raise DeviceChanged("Audio devices changed — reselect")
        try:
            current = self._scan()
        except (AudioUnavailable, AttributeError, IndexError, LookupError, OSError) as exc:
            self.close()
            raise DeviceChanged("Audio device unavailable — reselect") from exc
        if microphone not in current[0] or (
            playback is not None and playback not in current[1]
        ):
            self.close()
            raise DeviceChanged("Audio devices changed — reselect")

    def close(self) -> None:
        with self._close_lock:
            if not self.closed:
                self.closed = True
                self.backend.terminate()


@dataclass(slots=True)
class NativeBlock:
    data: bytes
    frames: int
    started_monotonic: float
    started_utc: datetime


@dataclass(slots=True)
class MonoBlock:
    samples: np.ndarray
    started_monotonic: float
    started_utc: datetime


@dataclass(slots=True)
class UtteranceJob:
    key: tuple[float, int]
    source: str
    samples: np.ndarray
    started_monotonic: float
    started_utc: datetime
    speech_ended_monotonic: float
    queued_monotonic: float
    voiced_samples: int = 0


@dataclass(frozen=True, slots=True)
class RemoteVocalDraft:
    available: bool
    duration_seconds: float | None = None
    relative_energy: float | None = None
    voiced_ratio: float | None = None
    words_per_voiced_second: float | None = None
    gap_seconds: float | None = None
    overlaps_user: bool | None = None
    unavailable_reason: str | None = None


@dataclass(frozen=True, slots=True)
class TurnDraft:
    speaker_name: str
    speaker_role: SpeakerRole
    source: str
    content: str
    timestamp: datetime
    vocal: RemoteVocalDraft | None = None


class TurnOrderer:
    def __init__(
        self,
        output: queue.Queue[TurnDraft],
        on_fault: Callable[[str], None],
        on_release: Callable[[float], None] | None = None,
    ) -> None:
        self._output = output
        self._on_fault = on_fault
        self._on_release = on_release or (lambda _latency: None)
        self._lock = threading.Lock()
        self._pending: set[tuple[float, int]] = set()
        self._ready: dict[tuple[float, int], tuple[TurnDraft, float | None]] = {}
        self._processed_through = {
            "microphone": float("-inf"),
            "system_audio_loopback": float("-inf"),
        }

    def register(self, key: tuple[float, int]) -> None:
        with self._lock:
            self._pending.add(key)

    def cancel(self, key: tuple[float, int]) -> None:
        with self._lock:
            self._pending.discard(key)
            result = self._drain_locked()
        self._after_drain(*result)

    def complete(
        self,
        key: tuple[float, int],
        draft: TurnDraft,
        queued_monotonic: float | None = None,
    ) -> None:
        with self._lock:
            if key not in self._pending:
                return
            self._ready[key] = (draft, queued_monotonic)
            result = self._drain_locked()
        self._after_drain(*result)

    def advance(self, source: str, processed_through: float) -> None:
        with self._lock:
            self._processed_through[source] = max(
                self._processed_through[source], processed_through
            )
            result = self._drain_locked()
        self._after_drain(*result)

    def finish_source(self, source: str) -> None:
        self.advance(source, float("inf"))

    def _drain_locked(self) -> tuple[bool, list[float]]:
        released: list[float] = []
        while self._pending:
            key = min(self._pending)
            ready = self._ready.get(key)
            if ready is None or min(self._processed_through.values()) < key[0]:
                return False, released
            draft, queued_monotonic = ready
            try:
                self._output.put_nowait(draft)
            except queue.Full:
                return True, released
            self._pending.remove(key)
            del self._ready[key]
            if queued_monotonic is not None:
                released.append(time.perf_counter() - queued_monotonic)
        return False, released

    def _after_drain(self, fault: bool, released: list[float]) -> None:
        for latency in released:
            self._on_release(latency)
        if fault:
            self._on_fault("Audio processing cannot keep up")

    def clear(self) -> None:
        with self._lock:
            self._pending.clear()
            self._ready.clear()
            for source in self._processed_through:
                self._processed_through[source] = float("-inf")

    @property
    def retained_count(self) -> int:
        with self._lock:
            return len(self._pending)


class SpeechSegmenter:
    def __init__(
        self,
        threshold: float,
        register: Callable[[float, datetime], tuple[float, int]],
        cancel: Callable[[tuple[float, int]], None],
    ) -> None:
        self.threshold = threshold
        self._register = register
        self._cancel = cancel
        self._candidate: list[MonoBlock] = []
        self._candidate_samples = 0
        self._blocks: list[np.ndarray] = []
        self._key: tuple[float, int] | None = None
        self._started_monotonic = 0.0
        self._started_utc = datetime.now(timezone.utc)
        self._speech_ended_monotonic = 0.0
        self._total_samples = self._voiced_samples = self._silence_samples = 0

    @property
    def active(self) -> bool:
        return self._key is not None

    @property
    def unregistered_start(self) -> float | None:
        return self._candidate[0].started_monotonic if self._candidate else None

    def feed(self, block: MonoBlock) -> list[UtteranceJob]:
        jobs: list[UtteranceJob] = []
        samples = block.samples
        offset = 0
        while offset < len(samples):
            if self.active:
                take = min(len(samples) - offset, MAX_UTTERANCE_SAMPLES - self._total_samples)
            else:
                take = len(samples) - offset
            part = samples[offset : offset + take]
            seconds = offset / SAMPLE_RATE
            current = MonoBlock(
                part,
                block.started_monotonic + seconds,
                block.started_utc + timedelta(seconds=seconds),
            )
            above = _rms(part) >= self.threshold
            if self.active:
                self._blocks.append(part.copy())
                self._total_samples += len(part)
                if above:
                    self._voiced_samples += len(part)
                    self._silence_samples = 0
                    self._speech_ended_monotonic = (
                        current.started_monotonic + len(part) / SAMPLE_RATE
                    )
                else:
                    self._silence_samples += len(part)
                if (
                    self._total_samples >= MAX_UTTERANCE_SAMPLES
                    or self._silence_samples >= END_SILENCE_SAMPLES
                ):
                    job = self._finalize()
                    if job:
                        jobs.append(job)
            elif above:
                self._candidate.append(current)
                self._candidate_samples += len(part)
                if self._candidate_samples >= START_VOICE_SAMPLES:
                    first = self._candidate[0]
                    self._key = self._register(first.started_monotonic, first.started_utc)
                    self._started_monotonic = first.started_monotonic
                    self._started_utc = first.started_utc
                    self._blocks = [item.samples.copy() for item in self._candidate]
                    self._total_samples = self._candidate_samples
                    self._voiced_samples = self._candidate_samples
                    self._speech_ended_monotonic = (
                        current.started_monotonic + len(part) / SAMPLE_RATE
                    )
                    self._candidate.clear()
                    self._candidate_samples = 0
            else:
                self._candidate.clear()
                self._candidate_samples = 0
            offset += take
        return jobs

    def flush(self) -> UtteranceJob | None:
        self._candidate.clear()
        self._candidate_samples = 0
        return self._finalize() if self.active else None

    def _finalize(self) -> UtteranceJob | None:
        key = self._key
        if key is None:
            return None
        if self._voiced_samples < MIN_VOICE_SAMPLES:
            self._cancel(key)
            job = None
        else:
            job = UtteranceJob(
                key=key,
                source="",
                samples=np.concatenate(self._blocks),
                started_monotonic=self._started_monotonic,
                started_utc=self._started_utc,
                speech_ended_monotonic=self._speech_ended_monotonic,
                queued_monotonic=time.perf_counter(),
                voiced_samples=self._voiced_samples,
            )
        self._blocks.clear()
        self._key = None
        self._speech_ended_monotonic = 0.0
        self._total_samples = self._voiced_samples = self._silence_samples = 0
        return job


def _rms(samples: np.ndarray) -> float:
    if not len(samples):
        return 0.0
    values = samples.astype(np.float32)
    return float(np.sqrt(np.mean(values * values)))


@dataclass(frozen=True, slots=True)
class AudioSnapshot:
    running: bool
    requires_reselection: bool
    microphone_status: str
    playback_status: str
    fault: str
    stream_count: int
    worker_count: int
    queued_jobs: int
    retained_results: int


_DLL_HANDLES: list[object] = []
_DLLS_CONFIGURED = False
_RUNTIME_LOCK = threading.Lock()
_RUNTIME_READY = False


def _configure_nvidia_dlls() -> None:
    global _DLLS_CONFIGURED
    if os.name != "nt" or _DLLS_CONFIGURED:
        return
    roots = [Path(path) / "nvidia" for path in site.getsitepackages()]
    if getattr(sys, 'frozen', False):
        roots.insert(0, Path(sys._MEIPASS) / 'nvidia')
    directories = [path for root in roots for path in root.glob("*/bin")]
    if directories:
        os.environ["PATH"] = (
            os.pathsep.join(map(str, directories))
            + os.pathsep
            + os.environ.get("PATH", "")
        )
        _DLL_HANDLES.extend(os.add_dll_directory(str(path)) for path in directories)
    _DLLS_CONFIGURED = True


def prepare_transcription_runtime() -> None:
    """Load CTranslate2 before MediaPipe without making module import GPU-dependent."""
    global _RUNTIME_READY
    with _RUNTIME_LOCK:
        if _RUNTIME_READY:
            return
        _configure_nvidia_dlls()
        import ctranslate2

        if ctranslate2.get_cuda_device_count() < 1:
            raise AudioUnavailable("A compatible NVIDIA GPU is unavailable")
        _RUNTIME_READY = True


def install_local_model() -> None:
    prepare_transcription_runtime()
    from faster_whisper import WhisperModel

    MODEL_CACHE.mkdir(parents=True, exist_ok=True)
    model = WhisperModel(
        MODEL_NAME,
        device="cuda",
        compute_type="float16",
        download_root=str(MODEL_CACHE),
        revision=MODEL_REVISION,
    )
    del model
    if not local_model_available():
        snapshot = MODEL_CACHE / MODEL_CACHE_DIRECTORY / "snapshots" / MODEL_REVISION
        missing = sorted(
            name for name in PINNED_MODEL_FILES if not snapshot.joinpath(name).is_file()
        )
        raise RuntimeError(
            f"Installed transcription model is incomplete at {snapshot} "
            f"(missing: {', '.join(missing)})"
        )


def local_model_available() -> bool:
    model_root = MODEL_CACHE / MODEL_CACHE_DIRECTORY / "snapshots" / MODEL_REVISION
    return all(model_root.joinpath(name).is_file() for name in PINNED_MODEL_FILES)


def _load_local_model():
    prepare_transcription_runtime()
    from faster_whisper import WhisperModel

    return WhisperModel(
        MODEL_NAME,
        device="cuda",
        compute_type="float16",
        download_root=str(MODEL_CACHE),
        local_files_only=True,
        revision=MODEL_REVISION,
    )


def run_audio_replay() -> str:
    """Cached-model and real pipeline replay with networking denied."""
    import json
    import socket
    import tempfile
    import wave

    fixture_dir = Path(__file__).with_name("assets") / "audio"
    manifest = json.loads((fixture_dir / "manifest.json").read_text(encoding="utf-8"))
    before = _audio_artifacts(Path.cwd())
    attempts = 0
    original_connect = socket.socket.connect
    original_connect_ex = socket.socket.connect_ex
    original_create_connection = socket.create_connection
    original_getaddrinfo = socket.getaddrinfo

    def deny(*_args, **_kwargs):
        nonlocal attempts
        attempts += 1
        raise OSError("network disabled for offline replay")

    socket.socket.connect = deny
    socket.socket.connect_ex = deny
    socket.create_connection = deny
    socket.getaddrinfo = deny
    previous_tempdir = tempfile.tempdir
    previous_temp = os.environ.get("TEMP")
    previous_tmp = os.environ.get("TMP")
    temp_artifacts: dict[str, tuple[int, int]] = {}
    try:
        with tempfile.TemporaryDirectory(prefix="conversation-copilot-audio-") as temp_root:
            tempfile.tempdir = temp_root
            os.environ["TEMP"] = os.environ["TMP"] = temp_root
            model = _load_local_model()
            wers: dict[str, float] = {}
            recalls: dict[str, float] = {}
            auto_languages: dict[str, str] = {}
            latencies: list[float] = []
            rtfs: list[float] = []
            for name in ("english.wav", "hebrew.wav", "long-english.wav"):
                expected = manifest["clips"][name]
                started = time.perf_counter()
                segments, _info = model.transcribe(
                    str(fixture_dir / name),
                    language=expected["language"],
                    task="transcribe",
                    **TRANSCRIBE_OPTIONS,
                )
                materialized = list(segments)
                elapsed = time.perf_counter() - started
                text = " ".join(segment.text.strip() for segment in materialized).strip()
                wers[name] = _validation_wer(
                    expected["text"], text, expected["language"]
                )
                if expected.get("keywords"):
                    recalls[name] = _validation_keyword_recall(
                        text, expected["keywords"], expected["language"]
                    )
                with wave.open(str(fixture_dir / name), "rb") as stream:
                    clip_seconds = stream.getnframes() / stream.getframerate()
                latencies.append(elapsed)
                rtfs.append(elapsed / clip_seconds)
                if not all(segment.words for segment in materialized):
                    raise RuntimeError("replay did not return word timestamps")
            for name in ("english.wav", "hebrew.wav"):
                expected = manifest["clips"][name]
                with wave.open(str(fixture_dir / name), "rb") as stream:
                    samples = np.frombuffer(
                        stream.readframes(stream.getnframes()), dtype="<i2"
                    ).astype(np.float32) / 32768.0
                language = _auto_language(model, samples)
                segments, _info = model.transcribe(
                    samples,
                    language=language,
                    task="transcribe",
                    **TRANSCRIBE_OPTIONS,
                )
                text = " ".join(segment.text.strip() for segment in segments).strip()
                if _validation_wer(expected["text"], text, expected["language"]):
                    raise RuntimeError("Auto replay accuracy failed")
                auto_languages[name] = language
            silence, _ = model.transcribe(
                np.zeros(5 * 60 * SAMPLE_RATE, dtype=np.float32),
                language="en",
                task="transcribe",
                **TRANSCRIBE_OPTIONS,
            )
            if _accepted_text(silence):
                raise RuntimeError("digital silence produced a transcript")
            room_noise = np.random.default_rng(0).normal(
                0, 25, 10 * SAMPLE_RATE
            ).astype(np.float32)
            room_noise[4 * SAMPLE_RATE : 4 * SAMPLE_RATE + 800] += 2_000
            noise_segments, _ = model.transcribe(
                room_noise / 32768.0,
                language="en",
                task="transcribe",
                **TRANSCRIBE_OPTIONS,
            )
            if _accepted_text(noise_segments):
                raise RuntimeError("non-speech noise produced a transcript")
            (
                scheduled_passes,
                pipeline_turns,
                timestamp_error,
                _pipeline_latencies,
                _pipeline_peak_jobs,
                _pipeline_saturations,
                _pipeline_final_jobs,
                _pipeline_final_workers,
                _pipeline_final_results,
            ) = _pipeline_replay(
                model, fixture_dir, manifest
            )
            del model
            temp_artifacts = _audio_artifacts(Path(temp_root))
    finally:
        socket.socket.connect = original_connect
        socket.socket.connect_ex = original_connect_ex
        socket.create_connection = original_create_connection
        socket.getaddrinfo = original_getaddrinfo
        tempfile.tempdir = previous_tempdir
        for name, value in (("TEMP", previous_temp), ("TMP", previous_tmp)):
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value
    if _audio_artifacts(Path.cwd()) != before or temp_artifacts:
        raise RuntimeError("replay created an audio artifact")
    if attempts:
        raise RuntimeError("cached replay attempted network access")
    if wers["english.wav"] > 0.15 or wers["hebrew.wav"] > 0.20:
        raise RuntimeError("replay WER threshold failed")
    if min(recalls.values()) < 0.90:
        raise RuntimeError("replay keyword threshold failed")
    if auto_languages != {"english.wav": "en", "hebrew.wav": "he"}:
        raise RuntimeError("Auto language detection failed")
    return (
        "Audio replay PASS\n"
        f"fixed WER en/he: {wers['english.wav']:.3f}/{wers['hebrew.wav']:.3f}\n"
        f"keyword recall en/he: {recalls['english.wav']:.2f}/{recalls['hebrew.wav']:.2f}\n"
        f"max RTF: {max(rtfs):.3f}\n"
        f"fixed inference max: {max(latencies):.3f}s\n"
        f"pipeline schedule attribution: {scheduled_passes}/{len(manifest['schedule'])}\n"
        f"pipeline turns: {pipeline_turns}\n"
        f"timestamp max error: {timestamp_error:.3f}s\n"
        "silence turns: 0\nnetwork attempts: 0\naudio artifacts: 0"
    )


def _pipeline_replay(
    model, fixture_dir: Path, manifest: dict, *, feed_speed: float = 4.0
) -> tuple[int, int, float, list[tuple[str, float, float]], int, int, int, int, int]:
    """Drive native blocks through the production source workers and orderer."""
    import wave
    from types import SimpleNamespace

    rate = int(manifest["sample_rate"])
    clips: dict[str, np.ndarray] = {}
    for name in manifest["clips"]:
        with wave.open(str(fixture_dir / name), "rb") as stream:
            if (
                stream.getframerate() != rate
                or stream.getnchannels() != 1
                or stream.getsampwidth() != SAMPLE_WIDTH
            ):
                raise RuntimeError("replay fixture format changed")
            clips[name] = np.frombuffer(stream.readframes(stream.getnframes()), dtype="<i2")
    schedule = sorted(manifest["schedule"], key=lambda item: item["start_seconds"])
    total_samples = max(
        int(item["start_seconds"] * rate) + len(clips[item["clip"]])
        for item in schedule
    ) + rate
    timelines = {
        "microphone": np.zeros(total_samples, dtype=np.int16),
        "system_audio_loopback": np.zeros(total_samples, dtype=np.int16),
    }
    for item in schedule:
        start = int(item["start_seconds"] * rate)
        clip = clips[item["clip"]]
        timelines[item["source"]][start : start + len(clip)] = clip

    native_formats = {
        "microphone": (48_000, 2),
        "system_audio_loopback": (192_000, 2),
    }
    native_timelines = {
        source: np.repeat(samples, native_rate // rate)
        for source, samples in timelines.items()
        for native_rate, _channels in (native_formats[source],)
    }
    microphone = AudioDeviceRecord(
        0, "Replay microphone", 0, "WASAPI", 2, 0, 48_000, False
    )
    render = AudioDeviceRecord(
        1, "Replay playback", 0, "WASAPI", 0, 2, 192_000, False
    )
    loopback = AudioDeviceRecord(
        2, "Replay loopback", 0, "WASAPI", 2, 0, 192_000, True
    )
    replay_catalog = SimpleNamespace(
        module=SimpleNamespace(paContinue=0, paComplete=1, paAbort=2),
        backend=None,
        close=lambda: None,
    )
    session = AudioCallSession(
        replay_catalog,
        microphone,
        PlaybackSelection(render, loopback),
        None,
        contact_name="Contact",
        model_factory=lambda: model,
        require_installed_model=False,
    )
    session._model = model
    session._configure_queues()
    session._workers = [
        threading.Thread(
            target=session._source_worker,
            args=(source,),
            name=f"replay-{source}",
            daemon=True,
        )
        for source in timelines
    ]
    session._workers.append(
        threading.Thread(
            target=session._transcription_worker,
            name="replay-transcription",
            daemon=True,
        )
    )
    for worker in session._workers:
        worker.start()
    base_monotonic = time.perf_counter()
    base_utc = datetime.now(timezone.utc)
    callback_monotonic = [base_monotonic]
    callback_utc = [base_utc]
    session._monotonic_clock = lambda: callback_monotonic[0]
    session._utc_clock = lambda: callback_utc[0]
    callbacks = {
        source: session._callback(source) for source in native_timelines
    }
    feed_started = time.perf_counter()
    offsets = {source: 0 for source in native_timelines}
    feed_error: Exception | None = None
    try:
        while any(
            offsets[source] < len(samples)
            for source, samples in native_timelines.items()
        ):
            active = [
                source
                for source, samples in native_timelines.items()
                if offsets[source] < len(samples)
            ]
            source = min(
                active,
                key=lambda item: offsets[item] / native_formats[item][0],
            )
            native_rate, channels = native_formats[source]
            offset = offsets[source]
            virtual_seconds = offset / native_rate
            delay = feed_started + virtual_seconds / feed_speed - time.perf_counter()
            if delay > 0:
                time.sleep(delay)
            part = native_timelines[source][offset : offset + FRAMES_PER_BUFFER]
            interleaved = np.repeat(part[:, None], channels, axis=1)
            offsets[source] += len(part)
            if source == "system_audio_loopback" and not np.any(part):
                continue
            duration = len(part) / native_rate
            callback_monotonic[0] = base_monotonic + virtual_seconds + duration
            callback_utc[0] = base_utc + timedelta(
                seconds=virtual_seconds + duration
            )
            _output, status = callbacks[source](
                interleaved.tobytes(), len(part), {}, 0
            )
            if status != replay_catalog.module.paContinue:
                raise RuntimeError(
                    f"pipeline callback stopped ({session._fault_message or 'deferred fault'})"
                )
    except Exception as exc:
        feed_error = exc
    finally:
        session._stop.set()
        deadline = time.perf_counter() + 90
        for worker in session._workers:
            worker.join(max(0, deadline - time.perf_counter()))
    final_workers = sum(worker.is_alive() for worker in session._workers)
    final_jobs = session._jobs.qsize()
    if final_workers:
        raise RuntimeError("pipeline replay did not tear down")
    if feed_error:
        raise feed_error
    if session._fault_message:
        raise RuntimeError(f"pipeline replay failed ({session._fault_message})")
    drafts: list[TurnDraft] = []
    while not session.results.empty():
        drafts.append(session.results.get_nowait())
    final_results = session.results.qsize() + session._orderer.retained_count
    if not drafts or [draft.timestamp for draft in drafts] != sorted(
        draft.timestamp for draft in drafts
    ):
        raise RuntimeError("pipeline turn ordering failed")

    scheduled_passes = 0
    timestamp_errors: list[tuple[float, float]] = []
    for index, item in enumerate(schedule):
        next_start = min(
            (
                later["start_seconds"]
                for later in schedule[index + 1 :]
                if later["source"] == item["source"]
            ),
            default=float("inf"),
        )
        matching = [
            draft
            for draft in drafts
            if draft.source == item["source"]
            and item["start_seconds"]
            <= (draft.timestamp - base_utc).total_seconds()
            < next_start
        ]
        expected = manifest["clips"][item["clip"]]
        text = " ".join(draft.content for draft in matching)
        if not matching or _validation_wer(expected["text"], text, expected["language"]) > 0.20:
            raise RuntimeError("pipeline replay accuracy/attribution failed")
        role = (
            SpeakerRole.USER
            if item["source"] == "microphone"
            else SpeakerRole.SELECTED_CONTACT
        )
        if any(draft.speaker_role != role for draft in matching):
            raise RuntimeError("pipeline speaker role failed")
        threshold = (
            250.0 if item["source"] == "microphone" else LOOPBACK_THRESHOLD
        )
        clip = clips[item["clip"]]
        native_rate = native_formats[item["source"]][0]
        source_block_samples = math.ceil(FRAMES_PER_BUFFER * rate / native_rate)
        first_voiced = next(
            offset
            for offset in range(0, len(clip), source_block_samples)
            if _rms(clip[offset : offset + source_block_samples]) >= threshold
        )
        expected_start = item["start_seconds"] + first_voiced / rate
        timestamp_errors.append(
            (
                abs((matching[0].timestamp - base_utc).total_seconds() - expected_start),
                FRAMES_PER_BUFFER / native_rate + 0.020,
            )
        )
        scheduled_passes += 1
    maximum_timestamp_error = max(error for error, _tolerance in timestamp_errors)
    if any(error > tolerance for error, tolerance in timestamp_errors):
        raise RuntimeError("pipeline timestamp threshold failed")
    if len(drafts) != len(session._completion_latencies):
        raise RuntimeError("pipeline latency/result count changed")
    release_metrics = [
        (
            draft.source,
            (draft.timestamp - base_utc).total_seconds(),
            latency,
        )
        for draft, latency in zip(drafts, session._completion_latencies, strict=True)
    ]
    return (
        scheduled_passes,
        len(drafts),
        maximum_timestamp_error,
        release_metrics,
        session._peak_jobs,
        session._job_saturations,
        final_jobs,
        final_workers,
        final_results,
    )


def run_audio_benchmark(seconds: float) -> str:
    """Run the production two-source replay while the retained F02 loop runs."""
    import json
    import statistics

    if not math.isfinite(seconds) or seconds <= 0:
        raise ValueError("benchmark seconds must be positive")
    fixture_dir = Path(__file__).with_name("assets") / "audio"
    manifest = json.loads((fixture_dir / "manifest.json").read_text(encoding="utf-8"))
    model = _load_local_model()
    stop = threading.Event()
    errors: list[Exception] = []
    single_latencies: list[float] = []
    overlap_latencies: list[float] = []
    peak_jobs = replay_count = 0
    saturations = final_jobs = final_workers = final_results = 0

    def replay_audio() -> None:
        nonlocal peak_jobs, replay_count, saturations, final_jobs, final_workers, final_results
        try:
            while not stop.is_set():
                result = _pipeline_replay(model, fixture_dir, manifest, feed_speed=1.0)
                single, overlap = _latency_groups(result[3], fixture_dir, manifest)
                single_latencies.extend(single)
                overlap_latencies.extend(overlap)
                peak_jobs = max(peak_jobs, result[4])
                saturations += result[5]
                final_jobs = result[6]
                final_workers = result[7]
                final_results = result[8]
                replay_count += 1
        except Exception as exc:
            errors.append(exc)

    audio_worker = threading.Thread(
        target=replay_audio, name="audio-benchmark", daemon=True
    )
    audio_worker.start()
    try:
        from .benchmark import run_delegate_benchmark

        video = run_delegate_benchmark(seconds, "cpu")
    finally:
        stop.set()
        audio_worker.join(90)
        model = None
    if audio_worker.is_alive():
        raise RuntimeError("audio benchmark worker did not stop")
    if errors:
        raise RuntimeError(f"audio benchmark failed ({type(errors[0]).__name__})")
    if not single_latencies or not overlap_latencies or not replay_count:
        raise RuntimeError("audio benchmark produced no completed turns")
    single_ordered = sorted(single_latencies)
    overlap_ordered = sorted(overlap_latencies)
    single_p95 = single_ordered[
        min(len(single_ordered) - 1, round((len(single_ordered) - 1) * 0.95))
    ]
    overlap_p95 = overlap_ordered[
        min(len(overlap_ordered) - 1, round((len(overlap_ordered) - 1) * 0.95))
    ]
    maximum = max(overlap_latencies)
    if single_p95 > 3.0 or maximum > 5.0 or saturations:
        raise RuntimeError(
            "audio benchmark latency/queue threshold failed "
            f"(single_p95={single_p95:.3f}s, overlap_p95={overlap_p95:.3f}s, "
            f"overlap_max={maximum:.3f}s, peak={peak_jobs}, saturations={saturations})"
        )
    return "\n".join(
        [
            f"Concurrent F02/F03 benchmark PASS ({video.seconds:.1f}s)",
            f"audio turns/replays: {len(single_latencies) + len(overlap_latencies)}/{replay_count}",
            f"audio single-source final latency p95: {single_p95:.3f}s",
            f"audio overlap final latency p95/max: {overlap_p95:.3f}/{maximum:.3f}s",
            f"audio job queue peak/final: {peak_jobs}/{final_jobs}",
            f"audio job queue saturations: {saturations}",
            f"F02 signal rate: {video.signal_rate:.2f}/s",
            f"F02 frame age p95: {video.frame_age_p95_ms:.1f} ms",
            f"working set start/end: {video.working_set_start_mib:.1f}/{video.working_set_end_mib:.1f} MiB",
            f"post-warm-up growth: {video.warm_growth_mib_per_min:.2f} MiB/min",
            f"workers/results remaining: {final_workers}/{final_results}",
        ]
    )


def _latency_groups(
    metrics: list[tuple[str, float, float]], fixture_dir: Path, manifest: dict
) -> tuple[list[float], list[float]]:
    import wave

    durations: dict[str, float] = {}
    for name in manifest["clips"]:
        with wave.open(str(fixture_dir / name), "rb") as stream:
            durations[name] = stream.getnframes() / stream.getframerate()
    intervals = [
        (
            item["source"],
            float(item["start_seconds"]),
            float(item["start_seconds"]) + durations[item["clip"]],
        )
        for item in manifest["schedule"]
    ]
    single: list[float] = []
    overlap: list[float] = []
    for source, started, latency in metrics:
        destination = overlap if any(
            other_source != source
            and other_start < started + MAX_UTTERANCE_SECONDS
            and other_end > started
            for other_source, other_start, other_end in intervals
        ) else single
        destination.append(latency)
    return single, overlap


def _audio_artifacts(*roots: Path) -> dict[str, tuple[int, int]]:
    suffixes = {".wav", ".mp3", ".flac", ".m4a", ".ogg", ".aac"}
    found: dict[str, tuple[int, int]] = {}
    for root in roots:
        for directory, subdirs, files in os.walk(root, onerror=lambda _error: None):
            subdirs[:] = [name for name in subdirs if name not in {".git", ".venv"}]
            for name in files:
                path = Path(directory, name)
                if path.suffix.casefold() in suffixes:
                    stat = path.stat()
                    found[str(path)] = (stat.st_size, stat.st_mtime_ns)
    return found


def _validation_words(text: str, language: str) -> list[str]:
    import re
    import unicodedata

    tokens = re.findall(r"\w+", unicodedata.normalize("NFKC", text).casefold(), re.UNICODE)
    forms = {
        "en": {("seven",): "#7", ("forty", "two"): "#42", ("one", "hundred"): "#100"},
        "he": {("שבע",): "#7", ("ארבעים", "ושתיים"): "#42", ("מאה",): "#100"},
    }[language]
    result: list[str] = []
    index = 0
    while index < len(tokens):
        for source, target in sorted(forms.items(), key=lambda item: len(item[0]), reverse=True):
            if tuple(tokens[index : index + len(source)]) == source:
                result.append(target)
                index += len(source)
                break
        else:
            result.append(f"#{tokens[index]}" if tokens[index] in {"7", "42", "100"} else tokens[index])
            index += 1
    return result


def _validation_error_counts(reference: str, hypothesis: str, language: str) -> tuple[int, int]:
    left = _validation_words(reference, language)
    right = _validation_words(hypothesis, language)
    row = list(range(len(right) + 1))
    for i, expected in enumerate(left, 1):
        next_row = [i]
        for j, actual in enumerate(right, 1):
            next_row.append(min(next_row[-1] + 1, row[j] + 1, row[j - 1] + (expected != actual)))
        row = next_row
    return row[-1], len(left)


def _validation_wer(reference: str, hypothesis: str, language: str) -> float:
    edits, words = _validation_error_counts(reference, hypothesis, language)
    return edits / max(1, words)


def _validation_keyword_recall(text: str, keywords: list[str], language: str) -> float:
    actual = _validation_words(text, language)
    wanted = [_validation_words(keyword, language) for keyword in keywords]
    return sum(any(actual[i : i + len(item)] == item for i in range(len(actual))) for item in wanted) / len(wanted)


def _accepted_text(segments) -> str:
    return " ".join(
        segment.text.strip()
        for segment in segments
        if getattr(segment, "no_speech_prob", 0.0) < 0.8
        and getattr(segment, "avg_logprob", 0.0) > -1.5
    ).strip()


def _auto_language(model, samples: np.ndarray) -> str:
    _language, _probability, probabilities = model.detect_language(
        samples, vad_filter=True
    )
    approved = [item for item in probabilities if item[0] in {"en", "he"}]
    if len(approved) != 2:
        raise RuntimeError("English/Hebrew language detection unavailable")
    return max(approved, key=lambda item: item[1])[0]


class AudioCallSession:
    def __init__(
        self,
        catalog: AudioDeviceCatalog,
        microphone: AudioDeviceRecord,
        playback: PlaybackSelection,
        language: str | None,
        *,
        contact_name: str = "Selected contact",
        microphone_threshold: float = DEFAULT_MICROPHONE_THRESHOLD,
        model_factory: Callable[[], object] = _load_local_model,
        require_installed_model: bool = True,
        source_guard: Callable[[], bool] | None = None,
        retain_catalog_on_clean_stop: bool = False,
    ) -> None:
        if language not in {None, "en", "he"}:
            raise ValueError("language must be English, Hebrew, or Auto")
        self.catalog = catalog
        self.microphone = microphone
        self.playback = playback
        self.language = language
        self.contact_name = contact_name
        self.microphone_threshold = microphone_threshold
        self._model_factory = model_factory
        self._require_installed_model = require_installed_model
        self._source_guard = source_guard
        self._retain_catalog_on_clean_stop = retain_catalog_on_clean_stop
        self.results: queue.Queue[TurnDraft] = queue.Queue(maxsize=MAX_RESULTS)
        self._jobs: queue.PriorityQueue[tuple[tuple[float, int], UtteranceJob]] = queue.PriorityQueue(maxsize=MAX_JOBS)
        self._native: dict[str, queue.Queue[NativeBlock]] = {}
        self._source_done = {"microphone": threading.Event(), "system_audio_loopback": threading.Event()}
        self._stop = threading.Event()
        self._done = threading.Event()
        self._deferred_faults: queue.SimpleQueue[str] = queue.SimpleQueue()
        self._state_lock = threading.Lock()
        self._shutdown_lock = threading.Lock()
        self._sequence_lock = threading.Lock()
        self._capture_lock = threading.Lock()
        self._sequence = 0
        self._capture_intervals: dict[
            tuple[float, int], tuple[str, float, float | None]
        ] = {}
        self._remote_energy_baseline: list[float] = []
        self._last_remote_end: float | None = None
        self._streams: dict[str, object] = {}
        self._workers: list[threading.Thread] = []
        self._finalizer: threading.Thread | None = None
        self._model: object | None = None
        self._running = False
        self._shutdown_timed_out = False
        self._completion_latencies: list[float] = []
        self._peak_jobs = 0
        self._job_saturations = 0
        self._monotonic_clock = time.perf_counter
        self._utc_clock = lambda: datetime.now(timezone.utc)
        self._requires_reselection = False
        self._fault_message = ""
        self._microphone_status = "Inactive"
        self._playback_status = "Inactive"
        self._orderer = TurnOrderer(
            self.results, self._fault, self._completion_latencies.append
        )

    def start(self) -> None:
        if self._running or self._stop.is_set():
            raise RuntimeError("audio session cannot be restarted")
        if self._require_installed_model and not local_model_available():
            raise AudioUnavailable("Local transcription model is not installed")
        try:
            self._model = self._model_factory()
        except Exception as exc:
            LOGGER.error("local model load failed (%s)", type(exc).__name__)
            raise AudioUnavailable("Local transcription model is unavailable") from exc
        try:
            self.catalog.revalidate(self.microphone, self.playback)
            self._configure_queues()
        except Exception:
            self._model = None
            raise
        module = self.catalog.module
        try:
            self._streams["microphone"] = self.catalog.backend.open(
                format=module.paInt16,
                channels=self.microphone.input_channels,
                rate=int(self.microphone.sample_rate),
                input=True,
                input_device_index=self.microphone.index,
                frames_per_buffer=FRAMES_PER_BUFFER,
                stream_callback=self._callback("microphone"),
                start=False,
            )
        except Exception as exc:
            self._start_failed(
                "Microphone unavailable — enable desktop-app microphone access in "
                "Windows Settings > Privacy & security > Microphone, then reselect",
                exc,
            )
        try:
            self._streams["system_audio_loopback"] = self.catalog.backend.open(
                format=module.paInt16,
                channels=self.playback.loopback.input_channels,
                rate=int(self.playback.loopback.sample_rate),
                input=True,
                input_device_index=self.playback.loopback.index,
                frames_per_buffer=FRAMES_PER_BUFFER,
                stream_callback=self._callback("system_audio_loopback"),
                start=False,
            )
        except Exception as exc:
            self._start_failed("Playback device unavailable — reselect", exc)

        self._workers = [
            threading.Thread(target=self._source_worker, args=("microphone",), name="audio-microphone", daemon=True),
            threading.Thread(target=self._source_worker, args=("system_audio_loopback",), name="audio-loopback", daemon=True),
            threading.Thread(target=self._transcription_worker, name="audio-transcription", daemon=True),
        ]
        for worker in self._workers:
            worker.start()
        try:
            for stream in self._streams.values():
                stream.start_stream()
            monitor = threading.Thread(
                target=self._monitor, name="audio-monitor", daemon=True
            )
            monitor.start()
            self._workers.append(monitor)
        except Exception as exc:
            self._start_failed("Audio stream unavailable — reselect", exc)
        with self._state_lock:
            self._running = True
            self._microphone_status = "Listening"
            self._playback_status = "Listening"

    def _configure_queues(self) -> None:
        formats = {
            "microphone": (self.microphone.sample_rate, self.microphone.input_channels),
            "system_audio_loopback": (
                self.playback.loopback.sample_rate,
                self.playback.loopback.input_channels,
            ),
        }
        callback_bytes = 0
        for source, (rate, channels) in formats.items():
            blocks = max(1, math.ceil(rate * MAX_CALLBACK_SECONDS / FRAMES_PER_BUFFER))
            self._native[source] = queue.Queue(maxsize=blocks)
            callback_bytes += blocks * FRAMES_PER_BUFFER * channels * SAMPLE_WIDTH
        retained_utterances = (2 + MAX_JOBS + 1) * MAX_UTTERANCE_SAMPLES * SAMPLE_WIDTH
        if callback_bytes + retained_utterances > MAX_RAW_BYTES:
            raise AudioUnavailable("Selected audio formats exceed the 12 MiB memory limit")

    def _callback(self, source: str):
        def callback(in_data, frame_count, _time_info, status_flags):
            module = self.catalog.module
            if self._stop.is_set():
                return None, module.paComplete
            if status_flags:
                self._deferred_faults.put("Audio processing cannot keep up")
                return None, module.paAbort
            try:
                record = (
                    self.microphone
                    if source == "microphone"
                    else self.playback.loopback
                )
                duration = int(frame_count) / record.sample_rate
                ended_monotonic = self._monotonic_clock()
                ended_utc = self._utc_clock()
                self._native[source].put_nowait(
                    NativeBlock(
                        bytes(in_data),
                        int(frame_count),
                        ended_monotonic - duration,
                        ended_utc - timedelta(seconds=duration),
                    )
                )
            except queue.Full:
                self._deferred_faults.put("Audio processing cannot keep up")
                return None, module.paAbort
            except Exception as exc:
                LOGGER.error("audio callback failed (%s)", type(exc).__name__)
                self._deferred_faults.put(
                    f"{'Microphone' if source == 'microphone' else 'Call audio'} failed ({type(exc).__name__}) — reselect"
                )
                return None, module.paAbort
            return None, module.paContinue

        return callback

    def _source_worker(self, source: str) -> None:
        import av

        record = self.microphone if source == "microphone" else self.playback.loopback
        threshold = (
            self.microphone_threshold
            if source == "microphone"
            else LOOPBACK_THRESHOLD
        )
        segmenter = SpeechSegmenter(
            threshold,
            lambda started, utc: self._register(started, utc, source),
            self._cancel,
        )
        resampler = av.AudioResampler(format="s16", layout="mono", rate=SAMPLE_RATE)
        last_voice = self._monotonic_clock()
        last_output_monotonic: float | None = None
        last_output_utc: datetime | None = None
        try:
            while not self._stop.is_set() or not self._native[source].empty():
                if self._fault_message:
                    break
                try:
                    block = self._native[source].get(timeout=0.1)
                except queue.Empty:
                    now = self._monotonic_clock()
                    processed_through = now - WATERMARK_SAFETY_SECONDS
                    if (
                        last_output_monotonic is not None
                        and now - last_output_monotonic
                        >= END_SILENCE_SAMPLES / SAMPLE_RATE
                    ):
                        job = segmenter.flush()
                        if job:
                            self._submit(source, [job])
                    self._update_no_speech_status(
                        source, segmenter.active, last_voice, now
                    )
                    self._advance_source(source, segmenter, processed_through)
                    continue
                values = np.frombuffer(block.data, dtype="<i2")
                expected = block.frames * record.input_channels
                if len(values) != expected:
                    raise ValueError("audio callback payload size changed")
                channels = values.reshape(block.frames, record.input_channels)
                mono_values = np.rint(channels.astype(np.float32).mean(axis=1)).astype(np.int16)
                frame = av.AudioFrame.from_ndarray(
                    mono_values.reshape(1, -1), format="s16", layout="mono"
                )
                frame.sample_rate = int(record.sample_rate)
                offset = 0
                for converted in resampler.resample(frame):
                    samples = converted.to_ndarray().reshape(-1).copy()
                    mono = MonoBlock(
                        samples,
                        block.started_monotonic + offset / SAMPLE_RATE,
                        block.started_utc + timedelta(seconds=offset / SAMPLE_RATE),
                    )
                    if _rms(samples) >= threshold:
                        last_voice = self._monotonic_clock()
                        self._set_source_status(source, "Listening — speech detected")
                    self._submit(source, segmenter.feed(mono))
                    duration = len(samples) / SAMPLE_RATE
                    offset += len(samples)
                    last_output_monotonic = mono.started_monotonic + duration
                    last_output_utc = mono.started_utc + timedelta(seconds=duration)
                self._advance_source(
                    source,
                    segmenter,
                    block.started_monotonic + block.frames / record.sample_rate,
                )
                self._update_no_speech_status(
                    source,
                    segmenter.active,
                    last_voice,
                    self._monotonic_clock(),
                )
            if not self._fault_message:
                for converted in resampler.resample(None):
                    samples = converted.to_ndarray().reshape(-1).copy()
                    if last_output_monotonic is not None and last_output_utc is not None:
                        self._submit(
                            source,
                            segmenter.feed(
                                MonoBlock(
                                    samples, last_output_monotonic, last_output_utc
                                )
                            ),
                        )
                        duration = len(samples) / SAMPLE_RATE
                        last_output_monotonic += duration
                        last_output_utc += timedelta(seconds=duration)
                job = segmenter.flush()
                if job:
                    self._submit(source, [job])
        except Exception as exc:
            LOGGER.error("%s source worker failed (%s)", source, type(exc).__name__)
            self._fault(
                f"{'Microphone' if source == 'microphone' else 'Call audio'} failed ({type(exc).__name__}) — reselect"
            )
        finally:
            self._orderer.finish_source(source)
            self._source_done[source].set()

    def _submit(self, source: str, jobs: list[UtteranceJob]) -> None:
        for job in jobs:
            job.source = source
            with self._capture_lock:
                interval = self._capture_intervals.get(job.key)
                if interval:
                    self._capture_intervals[job.key] = (
                        interval[0], interval[1], job.speech_ended_monotonic
                    )
            try:
                self._jobs.put_nowait((job.key, job))
                with self._sequence_lock:
                    self._peak_jobs = max(self._peak_jobs, self._jobs.qsize())
                self._set_source_status(source, "Transcribing")
            except queue.Full:
                with self._sequence_lock:
                    self._job_saturations += 1
                self._cancel(job.key)
                self._fault("Audio processing cannot keep up")

    def _advance_source(
        self, source: str, segmenter: SpeechSegmenter, processed_through: float
    ) -> None:
        unregistered = segmenter.unregistered_start
        self._orderer.advance(
            source,
            min(processed_through, unregistered)
            if unregistered is not None
            else processed_through,
        )

    def _transcription_worker(self) -> None:
        model = self._model
        try:
            if model is None:
                raise RuntimeError("local model was not loaded")
            while not all(event.is_set() for event in self._source_done.values()) or not self._jobs.empty():
                if self._fault_message:
                    break
                try:
                    _, job = self._jobs.get(timeout=0.1)
                except queue.Empty:
                    continue
                if time.perf_counter() - job.queued_monotonic > 30:
                    self._cancel(job.key)
                    self._fault("Audio processing cannot keep up")
                    break
                samples = job.samples.astype(np.float32) / 32768.0
                job.samples = np.empty(0, dtype=np.int16)
                language = self.language or _auto_language(model, samples)
                segments, _info = model.transcribe(
                    samples,
                    language=language,
                    task="transcribe",
                    **TRANSCRIBE_OPTIONS,
                )
                content = _accepted_text(segments)
                discarded = not content or content.casefold() in {
                    "[blank_audio]", "[silence]", "[music]"
                }
                if discarded:
                    del samples
                    self._cancel(job.key)
                else:
                    microphone = job.source == "microphone"
                    vocal = (
                        self._remote_vocal_draft(job, content, samples)
                        if not microphone
                        else None
                    )
                    del samples
                    self._orderer.complete(
                        job.key,
                        TurnDraft(
                            speaker_name="You" if microphone else self.contact_name,
                            speaker_role=SpeakerRole.USER if microphone else SpeakerRole.SELECTED_CONTACT,
                            source=job.source,
                            content=content,
                            timestamp=job.started_utc,
                            vocal=vocal,
                        ),
                        job.speech_ended_monotonic,
                    )
                self._set_source_status(job.source, "Listening")
        except Exception as exc:
            LOGGER.error("transcription worker failed (%s)", type(exc).__name__)
            self._fault(f"Local transcription failed ({type(exc).__name__})")
        finally:
            self._model = None

    def _register(
        self, started: float, _utc: datetime, source: str = ""
    ) -> tuple[float, int]:
        with self._sequence_lock:
            self._sequence += 1
            key = (started, self._sequence)
        if source:
            with self._capture_lock:
                cutoff = started - 90
                self._capture_intervals = {
                    item_key: interval
                    for item_key, interval in self._capture_intervals.items()
                    if interval[2] is None or interval[2] >= cutoff
                }
                self._capture_intervals[key] = (source, started, None)
        self._orderer.register(key)
        return key

    def _cancel(self, key: tuple[float, int]) -> None:
        with self._capture_lock:
            self._capture_intervals.pop(key, None)
        self._orderer.cancel(key)

    def _remote_vocal_draft(
        self, job: UtteranceJob, content: str, samples: np.ndarray
    ) -> RemoteVocalDraft:
        duration = job.speech_ended_monotonic - job.started_monotonic
        voiced_seconds = job.voiced_samples / SAMPLE_RATE
        rms = _rms(samples)
        clipped_ratio = float(np.mean(np.abs(samples) >= 0.999)) if len(samples) else 1.0
        with self._capture_lock:
            overlaps_user = any(
                source == "microphone"
                and started < job.speech_ended_monotonic
                and (ended is None or ended > job.started_monotonic)
                for source, started, ended in self._capture_intervals.values()
            )
            self._capture_intervals.pop(job.key, None)
        previous_end = self._last_remote_end
        if duration > 0:
            self._last_remote_end = job.speech_ended_monotonic
        reliable = (
            duration > 0
            and job.voiced_samples >= MIN_VOICE_SAMPLES
            and voiced_seconds <= duration + END_SILENCE_SAMPLES / SAMPLE_RATE
            and rms > 0
            and clipped_ratio <= MAX_CLIPPED_SAMPLE_RATIO
        )
        baseline = self._remote_energy_baseline
        if reliable:
            reason = (
                "Too little reliable remote speech for a session baseline"
                if len(baseline) < REMOTE_ENERGY_BASELINE_UTTERANCES
                else ("No earlier reliable remote turn for gap timing" if previous_end is None else "")
            )
            if not reason:
                result = RemoteVocalDraft(
                    available=True,
                    duration_seconds=duration,
                    relative_energy=rms / statistics.median(baseline),
                    voiced_ratio=min(1.0, job.voiced_samples / len(samples)),
                    words_per_voiced_second=len(content.split()) / voiced_seconds,
                    gap_seconds=max(0.0, job.started_monotonic - previous_end),
                    overlaps_user=overlaps_user,
                )
            else:
                result = RemoteVocalDraft(False, unavailable_reason=reason)
            baseline.append(rms)
            del baseline[:-REMOTE_ENERGY_BASELINE_LIMIT]
            return result
        reason = (
            "Remote audio was clipped"
            if clipped_ratio > MAX_CLIPPED_SAMPLE_RATIO
            else "Remote vocal timing or speech activity was unreliable"
        )
        return RemoteVocalDraft(False, unavailable_reason=reason)

    def _set_source_status(self, source: str, status: str) -> None:
        with self._state_lock:
            if source == "microphone":
                self._microphone_status = status
            else:
                self._playback_status = status

    def _update_no_speech_status(
        self, source: str, active: bool, last_voice: float, now: float
    ) -> None:
        if not active and now - last_voice >= 10:
            self._set_source_status(source, "Listening — no speech detected")

    def _monitor(self) -> None:
        next_source_check = 0.0
        while not self._stop.is_set():
            if self._stop.wait(0.1):
                return
            try:
                message = self._deferred_faults.get_nowait()
            except queue.Empty:
                message = ""
            if message:
                self._fault(message)
                return
            now = time.perf_counter()
            if self._source_guard and now >= next_source_check:
                next_source_check = now + 0.5
                try:
                    source_allowed = self._source_guard()
                except Exception as exc:
                    LOGGER.error("call source priority check failed (%s)", type(exc).__name__)
                    source_allowed = False
                if not source_allowed:
                    self._fault("WhatsApp call available — reselect")
                    return
            inactive_source = ""
            with self._shutdown_lock:
                for source, stream in self._streams.items():
                    if self._stop.is_set():
                        return
                    try:
                        active = stream.is_active()
                    except Exception as exc:
                        LOGGER.error("stream status failed (%s)", type(exc).__name__)
                        active = False
                    if not active:
                        inactive_source = source
                        break
            if inactive_source:
                if self._stop.is_set():
                    return
                self._fault(
                    "Microphone disconnected — reselect"
                    if inactive_source == "microphone"
                    else "Call playback source disconnected — reselect"
                )
                return

    def _start_failed(self, message: str, exc: Exception) -> None:
        with self._state_lock:
            self._requires_reselection = True
            if not self._fault_message:
                self._fault_message = message
        self._stop.set()
        self._close_streams()
        self.catalog.close()
        self._model = None
        if self._workers:
            self._start_finalizer()
        raise AudioUnavailable(message) from exc

    def _fault(self, message: str) -> None:
        with self._state_lock:
            if self._fault_message:
                return
            self._fault_message = message
            self._requires_reselection = True
        self._stop.set()
        self._start_finalizer()

    def request_stop(self) -> None:
        self._stop.set()
        self._start_finalizer()

    def _start_finalizer(self) -> None:
        with self._shutdown_lock:
            if self._finalizer and self._finalizer.is_alive():
                return
            self._finalizer = threading.Thread(
                target=self._finish_shutdown, name="audio-shutdown", daemon=True
            )
            self._finalizer.start()

    def _finish_shutdown(self) -> None:
        self._close_streams()
        deadline = time.perf_counter() + 5
        workers = tuple(self._workers)
        for worker in workers:
            if worker is threading.current_thread():
                continue
            worker.join(max(0, deadline - time.perf_counter()))
        timed_out = any(
            worker is not threading.current_thread() and worker.is_alive()
            for worker in workers
        )
        if timed_out:
            with self._state_lock:
                self._running = False
                self._shutdown_timed_out = True
                self._requires_reselection = True
                self._fault_message = "Audio shutdown timed out"
            self.catalog.close()
            self._done.set()
            threading.Thread(
                target=self._finish_late_shutdown,
                args=(workers,),
                name="audio-shutdown-reaper",
                daemon=True,
            ).start()
            return
        self._clear_queues()
        self._orderer.clear()
        if self._fault_message or not self._retain_catalog_on_clean_stop:
            self.catalog.close()
        with self._state_lock:
            self._running = False
            if not self._fault_message:
                self._microphone_status = self._playback_status = "Stopped"
        self._done.set()

    def _finish_late_shutdown(self, workers: tuple[threading.Thread, ...]) -> None:
        for worker in workers:
            if worker is not threading.current_thread():
                worker.join()
        self._clear_queues()
        self._orderer.clear()
        self.catalog.close()

    def _close_streams(self) -> None:
        with self._shutdown_lock:
            streams, self._streams = list(self._streams.values()), {}
        for stream in streams:
            try:
                if stream.is_active():
                    stream.stop_stream()
            except Exception as exc:
                LOGGER.error("stream stop failed (%s)", type(exc).__name__)
            try:
                stream.close()
            except Exception as exc:
                LOGGER.error("stream close failed (%s)", type(exc).__name__)

    def _clear_queues(self) -> None:
        for item in [*self._native.values(), self._jobs]:
            while True:
                try:
                    item.get_nowait()
                except queue.Empty:
                    break
        with self._capture_lock:
            self._capture_intervals.clear()

    def stop(self, timeout: float = 5.0) -> None:
        self.request_stop()
        if not self._done.wait(timeout):
            raise TimeoutError("audio workers did not stop within five seconds")
        if self._shutdown_timed_out:
            raise TimeoutError("audio workers did not stop within five seconds")

    def snapshot(self) -> AudioSnapshot:
        retained_results = self.results.qsize() + self._orderer.retained_count
        with self._shutdown_lock:
            stream_count = len(self._streams)
        worker_count = sum(worker.is_alive() for worker in self._workers)
        with self._state_lock:
            return AudioSnapshot(
                running=self._running,
                requires_reselection=self._requires_reselection,
                microphone_status=self._microphone_status,
                playback_status=self._playback_status,
                fault=self._fault_message,
                stream_count=stream_count,
                worker_count=worker_count,
                queued_jobs=self._jobs.qsize(),
                retained_results=retained_results,
            )
