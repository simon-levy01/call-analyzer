from __future__ import annotations

import inspect
import queue
import sys
import threading
import time
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import numpy as np
import pytest

import conversation_copilot.audio as audio_module
from conversation_copilot.__main__ import (
    _conversation_turn_from_audio,
    _keep_audio_after_video_end,
    _needs_audio_selection,
    _vocal_observation_from_audio,
)
from conversation_copilot.audio import (
    AudioCallSession,
    AudioDeviceCatalog,
    AudioUnavailable,
    MonoBlock,
    SpeechSegmenter,
    TurnDraft,
    TurnOrderer,
    TRANSCRIBE_OPTIONS,
    UtteranceJob,
    _latency_groups,
    _auto_language,
    production_transcription_language,
    transcription_language_labels,
    device_labels,
)
from conversation_copilot.models import SpeakerRole


class FakeModule:
    paWASAPI = 13
    paInt16 = 8
    paContinue = 0
    paComplete = 1
    paAbort = 2


class FakeStream:
    def __init__(self) -> None:
        self.active = False
        self.closed = False

    def start_stream(self) -> None:
        self.active = True

    def stop_stream(self) -> None:
        self.active = False

    def is_active(self) -> bool:
        return self.active

    def close(self) -> None:
        self.closed = True


class FakeBackend:
    def __init__(self, fail_open: int | None = None) -> None:
        self.devices = [
            self.info(0, "Microphone", inputs=2),
            self.info(1, "Microphone", inputs=1),
            self.info(2, "Speakers", outputs=2),
            self.info(3, "Speakers (loopback)", inputs=2, loopback=True),
        ]
        self.fail_open = fail_open
        self.open_calls: list[dict] = []
        self.streams: list[FakeStream] = []
        self.terminated = False
        self.default_input = 0
        self.default_output = 2

    @staticmethod
    def info(index, name, *, inputs=0, outputs=0, loopback=False):
        return {
            "index": index,
            "name": name,
            "hostApi": 0,
            "maxInputChannels": inputs,
            "maxOutputChannels": outputs,
            "defaultSampleRate": 48_000.0,
            "isLoopbackDevice": loopback,
        }

    def get_host_api_info_by_type(self, _kind):
        return {
            "index": 0,
            "name": "Windows WASAPI",
            "defaultInputDevice": self.default_input,
            "defaultOutputDevice": self.default_output,
        }

    def get_host_api_info_by_index(self, _index):
        return {"index": 0, "name": "Windows WASAPI"}

    def get_device_count(self):
        return len(self.devices)

    def get_device_info_by_index(self, index):
        return dict(self.devices[index])

    def get_wasapi_loopback_analogue_by_index(self, index):
        if index != 2:
            raise LookupError(index)
        return dict(self.devices[3])

    def get_default_input_device_info(self):
        return dict(self.devices[0])

    def get_default_wasapi_device(self):
        return dict(self.devices[2])

    def open(self, **kwargs):
        self.open_calls.append(kwargs)
        if self.fail_open == len(self.open_calls):
            raise OSError("unavailable")
        stream = FakeStream()
        self.streams.append(stream)
        return stream

    def terminate(self):
        self.terminated = True


def catalog(backend: FakeBackend | None = None):
    return AudioDeviceCatalog(backend or FakeBackend(), FakeModule)


def test_catalog_uses_session_indices_and_disambiguates_duplicates():
    devices = catalog()

    assert device_labels(devices.microphones) == [
        "Microphone [WASAPI #0]",
        "Microphone [WASAPI #1]",
    ]
    assert devices.default_microphone_index == 0
    assert devices.default_render_index == 2
    assert devices.playbacks[0].loopback.index == 3


def test_changed_record_opens_zero_streams_and_invalidates_catalog():
    backend = FakeBackend()
    devices = catalog(backend)
    session = AudioCallSession(
        devices,
        devices.microphones[0],
        devices.playbacks[0],
        "en",
        model_factory=lambda: object(),
        require_installed_model=False,
    )
    backend.devices[0]["name"] = "Changed"

    with pytest.raises(AudioUnavailable, match="changed"):
        session.start()

    assert backend.open_calls == []
    assert devices.closed


def test_playback_open_failure_closes_microphone():
    backend = FakeBackend(fail_open=2)
    devices = catalog(backend)
    session = AudioCallSession(
        devices,
        devices.microphones[0],
        devices.playbacks[0],
        "en",
        model_factory=lambda: object(),
        require_installed_model=False,
    )

    with pytest.raises(AudioUnavailable, match="Playback device"):
        session.start()

    assert [call["input_device_index"] for call in backend.open_calls] == [0, 3]
    assert backend.streams[0].closed
    assert devices.closed


def test_changed_playback_record_opens_zero_streams():
    backend = FakeBackend()
    devices = catalog(backend)
    session = AudioCallSession(
        devices,
        devices.microphones[0],
        devices.playbacks[0],
        "en",
        model_factory=lambda: object(),
        require_installed_model=False,
    )
    backend.devices[3]["name"] = "Changed"

    with pytest.raises(AudioUnavailable, match="changed"):
        session.start()

    assert backend.open_calls == []


def test_session_opens_only_explicit_microphone_and_loopback_indices():
    backend = FakeBackend()
    devices = catalog(backend)
    session = AudioCallSession(
        devices,
        devices.microphones[0],
        devices.playbacks[0],
        "en",
        model_factory=lambda: SimpleNamespace(
            transcribe=lambda *_args, **_kwargs: (iter(()), None)
        ),
        require_installed_model=False,
    )
    backend.devices[1]["name"] = "Unrelated microphone changed"

    session.start()

    assert [call["input_device_index"] for call in backend.open_calls] == [0, 3]
    assert all(stream.is_active() for stream in backend.streams)
    session.stop()
    assert all(stream.closed for stream in backend.streams)


def test_microphone_open_failure_includes_windows_privacy_guidance():
    backend = FakeBackend(fail_open=1)
    devices = catalog(backend)
    session = AudioCallSession(
        devices,
        devices.microphones[0],
        devices.playbacks[0],
        "en",
        model_factory=lambda: object(),
        require_installed_model=False,
    )

    with pytest.raises(AudioUnavailable, match="desktop-app microphone access"):
        session.start()

    assert len(backend.open_calls) == 1
    assert devices.closed


def test_stream_start_failure_tears_down_started_workers():
    class StartFailStream(FakeStream):
        def start_stream(self) -> None:
            raise OSError("start failed")

    class StartFailBackend(FakeBackend):
        def open(self, **kwargs):
            self.open_calls.append(kwargs)
            stream = StartFailStream() if len(self.open_calls) == 1 else FakeStream()
            self.streams.append(stream)
            return stream

    backend = StartFailBackend()
    devices = catalog(backend)
    session = AudioCallSession(
        devices,
        devices.microphones[0],
        devices.playbacks[0],
        "en",
        model_factory=lambda: SimpleNamespace(
            transcribe=lambda *_args, **_kwargs: (iter(()), None)
        ),
        require_installed_model=False,
    )

    with pytest.raises(AudioUnavailable, match="stream"):
        session.start()
    session.stop()

    assert session.snapshot().worker_count == 0
    assert all(stream.closed for stream in backend.streams)


def test_callback_overflow_faults_instead_of_blocking_or_dropping():
    devices = catalog()
    session = AudioCallSession(
        devices,
        devices.microphones[0],
        devices.playbacks[0],
        "en",
        model_factory=lambda: object(),
        require_installed_model=False,
    )
    session._native["microphone"] = queue.Queue(maxsize=1)
    callback = session._callback("microphone")
    callback(b"\0\0", 1, {}, 0)

    assert callback(b"\0\0", 1, {}, 0)[1] == FakeModule.paAbort
    assert session.snapshot().fault == ""
    session._monitor()
    assert session.snapshot().fault == "Audio processing cannot keep up"
    session.stop()


def test_native_format_bounds_reject_oversized_memory_before_open():
    backend = FakeBackend()
    backend.devices[0]["maxInputChannels"] = 32
    backend.devices[0]["defaultSampleRate"] = 384_000.0
    backend.devices[3]["maxInputChannels"] = 32
    backend.devices[3]["defaultSampleRate"] = 384_000.0
    devices = catalog(backend)
    session = AudioCallSession(
        devices,
        devices.microphones[0],
        devices.playbacks[0],
        "en",
        model_factory=lambda: object(),
        require_installed_model=False,
    )

    with pytest.raises(AudioUnavailable, match="12 MiB"):
        session.start()

    assert backend.open_calls == []


def test_segmenter_ignores_silence_and_bounds_voiced_utterances():
    sequence = 0
    cancelled = []

    def register(started, _utc):
        nonlocal sequence
        sequence += 1
        return started, sequence

    segmenter = SpeechSegmenter(100, register, cancelled.append)
    now = datetime.now(timezone.utc)
    assert segmenter.feed(MonoBlock(np.zeros(16_000, dtype=np.int16), 0.0, now)) == []
    segmenter.feed(MonoBlock(np.full(3_200, 1_000, dtype=np.int16), 0.0, now))
    segmenter.feed(MonoBlock(np.zeros(9_600, dtype=np.int16), 0.2, now))
    assert len(cancelled) == 1

    jobs = []
    for index in range(160):
        jobs.extend(
            segmenter.feed(
                MonoBlock(
                    np.full(1_600, 1_000, dtype=np.int16),
                    index / 10,
                    now,
                )
            )
        )
    jobs.extend(
        segmenter.feed(
            MonoBlock(np.zeros(9_600, dtype=np.int16), 16.0, now)
        )
    )

    assert len(jobs) == 3
    assert max(len(job.samples) for job in jobs) <= 7 * 16_000
    assert len(cancelled) == 1


def test_default_microphone_gate_keeps_quiet_speech():
    threshold = inspect.signature(AudioCallSession).parameters[
        "microphone_threshold"
    ].default
    segmenter = SpeechSegmenter(
        threshold, lambda started, _utc: (started, 1), lambda _key: None
    )
    now = datetime.now(timezone.utc)
    segmenter.feed(MonoBlock(np.full(6_400, 150, dtype=np.int16), 0.0, now))
    jobs = segmenter.feed(MonoBlock(np.zeros(9_600, dtype=np.int16), 0.4, now))

    assert len(jobs) == 1


def test_turn_orderer_waits_for_the_older_source():
    output = queue.Queue(maxsize=4)
    faults = []
    orderer = TurnOrderer(output, faults.append)
    older, newer = (1.0, 1), (2.0, 2)
    orderer.register(older)
    orderer.register(newer)
    make = lambda text: TurnDraft(
        speaker_name="You",
        speaker_role=SpeakerRole.USER,
        source="microphone",
        content=text,
        timestamp=datetime.now(timezone.utc),
    )

    orderer.complete(newer, make("newer"))
    assert output.empty()
    orderer.complete(older, make("older"))
    orderer.advance("microphone", 3.0)
    orderer.advance("system_audio_loopback", 3.0)

    assert [output.get().content, output.get().content] == ["older", "newer"]
    assert faults == []


def test_turn_orderer_holds_ready_turn_until_lagging_source_advances():
    output = queue.Queue(maxsize=4)
    orderer = TurnOrderer(output, lambda message: pytest.fail(message))
    key = (10.0, 1)
    orderer.register(key)
    orderer.complete(
        key,
        TurnDraft("You", SpeakerRole.USER, "microphone", "ready", datetime.now(timezone.utc)),
    )
    orderer.advance("microphone", 12.0)
    orderer.advance("system_audio_loopback", 9.0)
    assert output.empty()

    orderer.advance("system_audio_loopback", 10.0)
    assert output.get_nowait().content == "ready"


def test_turn_orderer_cancel_releases_a_ready_newer_turn():
    output = queue.Queue(maxsize=4)
    orderer = TurnOrderer(output, lambda message: pytest.fail(message))
    older, newer = (1.0, 1), (2.0, 2)
    orderer.register(older)
    orderer.register(newer)
    orderer.complete(
        newer,
        TurnDraft("You", SpeakerRole.USER, "microphone", "newer", datetime.now(timezone.utc)),
    )
    orderer.advance("microphone", 3.0)
    orderer.advance("system_audio_loopback", 3.0)
    assert output.empty()

    orderer.cancel(older)
    assert output.get_nowait().content == "newer"


def test_full_result_queue_faults_outside_orderer_lock_without_losing_draft():
    output = queue.Queue(maxsize=1)
    output.put_nowait(
        TurnDraft("You", SpeakerRole.USER, "microphone", "existing", datetime.now(timezone.utc))
    )
    faults = []
    orderer = TurnOrderer(output, faults.append)
    key = (1.0, 1)
    orderer.register(key)
    orderer.complete(
        key,
        TurnDraft("You", SpeakerRole.USER, "microphone", "retained", datetime.now(timezone.utc)),
    )
    orderer.advance("microphone", 2.0)
    orderer.advance("system_audio_loopback", 2.0)

    assert faults == ["Audio processing cannot keep up"]
    assert orderer.retained_count == 1


def wait_until(predicate, timeout=2):
    deadline = time.perf_counter() + timeout
    while time.perf_counter() < deadline:
        if predicate():
            return
        time.sleep(0.01)
    raise AssertionError("condition was not reached")


def test_disconnect_stops_both_streams_and_requires_reselection():
    backend = FakeBackend()
    devices = catalog(backend)
    session = AudioCallSession(
        devices,
        devices.microphones[0],
        devices.playbacks[0],
        "en",
        model_factory=lambda: SimpleNamespace(transcribe=lambda *_a, **_k: (iter(()), None)),
        require_installed_model=False,
    )
    session.start()
    backend.streams[0].active = False

    wait_until(lambda: bool(session.snapshot().fault))
    session.stop()

    snapshot = session.snapshot()
    assert snapshot.fault == "Microphone disconnected — reselect"
    assert snapshot.requires_reselection
    assert snapshot.stream_count == snapshot.worker_count == 0
    assert all(stream.closed for stream in backend.streams)


def test_model_failure_faults_and_clears_raw_work():
    class BrokenModel:
        def transcribe(self, *_args, **_kwargs):
            raise RuntimeError("private detail must not escape")

    devices = catalog()
    session = AudioCallSession(
        devices,
        devices.microphones[0],
        devices.playbacks[0],
        "en",
        model_factory=BrokenModel,
        require_installed_model=False,
    )
    session.start()
    key = session._register(1.0, datetime.now(timezone.utc))
    session._jobs.put_nowait(
        (
            key,
            UtteranceJob(
                key,
                "microphone",
                np.ones(16_000, dtype=np.int16),
                1.0,
                datetime.now(timezone.utc),
                time.perf_counter(),
                time.perf_counter(),
            ),
        )
    )

    wait_until(lambda: bool(session.snapshot().fault))
    session.stop()

    snapshot = session.snapshot()
    assert snapshot.fault == "Local transcription failed (RuntimeError)"
    assert snapshot.queued_jobs == snapshot.stream_count == snapshot.worker_count == 0


def test_live_transcription_uses_shared_production_options():
    calls = []

    class Model:
        def transcribe(self, *_args, **kwargs):
            calls.append(kwargs)
            return iter(()), None

    devices = catalog()
    session = AudioCallSession(
        devices,
        devices.microphones[0],
        devices.playbacks[0],
        "en",
        model_factory=Model,
        require_installed_model=False,
    )
    session.start()
    key = session._register(1.0, datetime.now(timezone.utc))
    session._jobs.put_nowait(
        (
            key,
            UtteranceJob(
                key,
                "microphone",
                np.ones(16_000, dtype=np.int16),
                1.0,
                datetime.now(timezone.utc),
                time.perf_counter(),
                time.perf_counter(),
            ),
        )
    )

    wait_until(lambda: bool(calls))
    session.stop()

    assert calls[0] == {"language": "en", "task": "transcribe", **TRANSCRIBE_OPTIONS}


def test_final_results_keep_physical_source_roles_and_capture_order():
    class ScriptedModel:
        def __init__(self):
            self.outputs = iter(("older", "newer"))

        def transcribe(self, *_args, **_kwargs):
            return iter((SimpleNamespace(text=next(self.outputs)),)), None

        def detect_language(self, *_args, **_kwargs):
            return "fr", 0.8, [("fr", 0.8), ("en", 0.15), ("he", 0.05)]

    devices = catalog()
    session = AudioCallSession(
        devices,
        devices.microphones[0],
        devices.playbacks[0],
        None,
        contact_name="Contact",
        model_factory=ScriptedModel,
        require_installed_model=False,
    )
    session.start()
    now = datetime.now(timezone.utc)
    for started, source in ((1.0, "microphone"), (2.0, "system_audio_loopback")):
        key = session._register(started, now)
        session._jobs.put_nowait(
            (
                key,
                UtteranceJob(
                    key,
                    source,
                    np.ones(16_000, dtype=np.int16),
                    started,
                    now,
                    time.perf_counter(),
                    time.perf_counter(),
                ),
            )
        )
    session._orderer.advance("microphone", 3.0)
    session._orderer.advance("system_audio_loopback", 3.0)
    wait_until(lambda: session.results.qsize() == 2)
    drafts = [session.results.get(), session.results.get()]
    session.stop()

    assert [draft.content for draft in drafts] == ["older", "newer"]
    assert [draft.speaker_role for draft in drafts] == [
        SpeakerRole.USER,
        SpeakerRole.SELECTED_CONTACT,
    ]
    assert [draft.source for draft in drafts] == [
        "microphone",
        "system_audio_loopback",
    ]
    assert drafts[0].speaker_name == "You"
    assert drafts[1].speaker_name == "Contact"


def test_remote_vocal_features_join_final_turns_without_retaining_samples():
    class Model:
        def transcribe(self, *_args, **_kwargs):
            return iter((SimpleNamespace(text="one two three four"),)), None

    devices = catalog()
    session = AudioCallSession(
        devices,
        devices.microphones[0],
        devices.playbacks[0],
        "en",
        model_factory=Model,
        require_installed_model=False,
    )
    session._model = Model()
    for done in session._source_done.values():
        done.set()
    now = datetime.now(timezone.utc)
    specifications = (
        (1.0, "system_audio_loopback"),
        (2.0, "system_audio_loopback"),
        (3.0, "system_audio_loopback"),
        (3.2, "microphone"),
    )
    jobs = []
    for started, source in specifications:
        key = session._register(started, now, source)
        jobs.append(
            UtteranceJob(
                key,
                source,
                np.full(16_000, 1_000, dtype=np.int16),
                started,
                now,
                started + 0.5,
                time.perf_counter(),
                voiced_samples=8_000,
            )
        )
    for job in jobs:
        session._submit(job.source, [job])
    session._orderer.advance("microphone", 5.0)
    session._orderer.advance("system_audio_loopback", 5.0)
    worker = threading.Thread(target=session._transcription_worker)
    worker.start()
    worker.join(1)
    wait_until(lambda: session.results.qsize() == 4)
    drafts = [session.results.get() for _ in range(4)]

    remote = [draft for draft in drafts if draft.source == "system_audio_loopback"]
    assert [draft.vocal.available for draft in remote] == [False, False, True]
    assert remote[2].vocal.relative_energy == pytest.approx(1.0)
    assert remote[2].vocal.voiced_ratio == pytest.approx(0.5)
    assert remote[2].vocal.words_per_voiced_second == pytest.approx(8.0)
    assert remote[2].vocal.gap_seconds == pytest.approx(0.5)
    assert remote[2].vocal.overlaps_user is True
    assert next(draft for draft in drafts if draft.source == "microphone").vocal is None
    assert _vocal_observation_from_audio(remote[2], 3).turn_display_order == 3
    assert all(job.samples.size == 0 for job in jobs)


def test_audio_drafts_construct_valid_conversation_turns():
    now = datetime.now(timezone.utc)
    drafts = (
        TurnDraft("You", SpeakerRole.USER, "microphone", "one", now),
        TurnDraft(
            "Contact",
            SpeakerRole.SELECTED_CONTACT,
            "system_audio_loopback",
            "two",
            now,
        ),
    )

    turns = [
        _conversation_turn_from_audio(draft, index)
        for index, draft in enumerate(drafts, 1)
    ]

    assert [turn.display_order for turn in turns] == [1, 2]
    assert [turn.source for turn in turns] == [
        "microphone",
        "system_audio_loopback",
    ]
    assert [turn.speaker_role for turn in turns] == [
        SpeakerRole.USER,
        SpeakerRole.SELECTED_CONTACT,
    ]


def test_auto_language_chooses_only_english_or_hebrew():
    model = SimpleNamespace(
        detect_language=lambda *_args, **_kwargs: (
            "fr",
            0.8,
            [("fr", 0.8), ("he", 0.15), ("en", 0.05)],
        )
    )

    assert _auto_language(model, np.zeros(16_000, dtype=np.float32)) == "he"


def test_audio_selection_blocks_only_when_usable_choices_exist():
    assert not _needs_audio_selection(None, -1, -1)
    assert not _needs_audio_selection(
        SimpleNamespace(microphones=[], playbacks=[]), -1, -1
    )
    usable = SimpleNamespace(microphones=[object()], playbacks=[object()])
    assert _needs_audio_selection(usable, -1, 0)
    assert _needs_audio_selection(usable, 0, -1)
    assert not _needs_audio_selection(usable, 0, 0)


def test_running_audio_outlives_video_capture_loss():
    running = SimpleNamespace(snapshot=lambda: SimpleNamespace(running=True))
    stopped = SimpleNamespace(snapshot=lambda: SimpleNamespace(running=False))

    assert _keep_audio_after_video_end(running)
    assert not _keep_audio_after_video_end(stopped)
    assert not _keep_audio_after_video_end(None)


def test_ten_start_stop_cycles_are_idempotent_and_reopen_devices():
    streams = []
    for _ in range(10):
        backend = FakeBackend()
        devices = catalog(backend)
        session = AudioCallSession(
            devices,
            devices.microphones[0],
            devices.playbacks[0],
            "he",
            model_factory=lambda: SimpleNamespace(transcribe=lambda *_a, **_k: (iter(()), None)),
            require_installed_model=False,
        )
        session.start()
        session.stop()
        session.stop()
        assert session.snapshot().stream_count == session.snapshot().worker_count == 0
        streams.extend(backend.streams)

    assert len(streams) == 20
    assert all(stream.closed for stream in streams)


def test_stop_acknowledges_before_workers_finish_draining():
    devices = catalog()
    session = AudioCallSession(
        devices,
        devices.microphones[0],
        devices.playbacks[0],
        "en",
        model_factory=lambda: SimpleNamespace(transcribe=lambda *_a, **_k: (iter(()), None)),
        require_installed_model=False,
    )
    session.start()

    started = time.perf_counter()
    session.request_stop()
    acknowledged = time.perf_counter() - started
    session.stop()

    assert acknowledged < 0.25
    assert session.snapshot().stream_count == session.snapshot().worker_count == 0
    assert session.snapshot().fault == ""


def test_internal_shutdown_timeout_closes_catalog_and_requires_reselection():
    class StuckWorker:
        def join(self, _timeout=None):
            pass

        def is_alive(self):
            return True

    devices = catalog()
    session = AudioCallSession(
        devices,
        devices.microphones[0],
        devices.playbacks[0],
        "en",
        model_factory=lambda: object(),
        require_installed_model=False,
        retain_catalog_on_clean_stop=True,
    )
    session._workers = [StuckWorker()]

    session._finish_shutdown()

    assert session.snapshot().fault == "Audio shutdown timed out"
    assert session.snapshot().requires_reselection
    assert devices.closed


def test_clean_stop_can_retain_session_catalog_for_explicit_restart_selection():
    backend = FakeBackend()
    devices = catalog(backend)
    session = AudioCallSession(
        devices,
        devices.microphones[0],
        devices.playbacks[0],
        "en",
        model_factory=lambda: SimpleNamespace(transcribe=lambda *_a, **_k: (iter(()), None)),
        require_installed_model=False,
        retain_catalog_on_clean_stop=True,
    )

    session.start()
    session.stop()

    assert session.snapshot().stream_count == session.snapshot().worker_count == 0
    assert all(stream.closed for stream in backend.streams)
    assert not devices.closed
    devices.close()
    assert backend.terminated


def test_callback_timestamp_marks_the_start_of_the_captured_block():
    devices = catalog()
    session = AudioCallSession(
        devices,
        devices.microphones[0],
        devices.playbacks[0],
        "en",
        model_factory=lambda: object(),
        require_installed_model=False,
    )
    session._native["microphone"] = queue.Queue(maxsize=1)
    before = time.perf_counter()
    session._callback("microphone")(b"\0" * (480 * 2 * 2), 480, {}, 0)
    after = time.perf_counter()
    block = session._native["microphone"].get_nowait()

    assert before - 0.011 <= block.started_monotonic <= after - 0.009


def test_model_load_failure_opens_zero_streams():
    backend = FakeBackend()
    devices = catalog(backend)

    def fail():
        raise RuntimeError("GPU unavailable")

    session = AudioCallSession(
        devices,
        devices.microphones[0],
        devices.playbacks[0],
        "en",
        model_factory=fail,
        require_installed_model=False,
    )
    with pytest.raises(AudioUnavailable, match="model"):
        session.start()
    assert backend.open_calls == []


def test_active_default_change_does_not_switch_explicit_streams():
    backend = FakeBackend()
    devices = catalog(backend)
    session = AudioCallSession(
        devices,
        devices.microphones[0],
        devices.playbacks[0],
        "en",
        model_factory=lambda: SimpleNamespace(
            transcribe=lambda *_args, **_kwargs: (iter(()), None)
        ),
        require_installed_model=False,
    )
    session.start()
    backend.default_input = backend.default_output = -1

    assert [call["input_device_index"] for call in backend.open_calls] == [0, 3]
    assert all(stream.is_active() for stream in backend.streams)
    session.stop()
    assert session.snapshot().fault == ""


def test_source_priority_change_stops_both_audio_sides():
    backend = FakeBackend()
    devices = catalog(backend)
    session = AudioCallSession(
        devices,
        devices.microphones[0],
        devices.playbacks[0],
        "en",
        model_factory=lambda: SimpleNamespace(
            transcribe=lambda *_args, **_kwargs: (iter(()), None)
        ),
        require_installed_model=False,
        source_guard=lambda: False,
        retain_catalog_on_clean_stop=True,
    )
    session.start()

    deadline = time.perf_counter() + 2
    while not session.snapshot().fault and time.perf_counter() < deadline:
        time.sleep(0.01)
    session.stop()

    assert session.snapshot().fault == "WhatsApp call available — reselect"
    assert session.snapshot().stream_count == session.snapshot().worker_count == 0
    assert devices.closed


def test_model_cache_requires_every_runtime_file(tmp_path, monkeypatch):
    assert (
        audio_module.MODEL_CACHE_DIRECTORY
        == "models--mobiuslabsgmbh--faster-whisper-large-v3-turbo"
    )
    monkeypatch.setattr(audio_module, "MODEL_CACHE", tmp_path)
    wrong_snapshot = (
        tmp_path
        / "models--mobiuslabsgmbh--faster-whisper-large-v3-turbo"
        / "snapshots"
        / "different-revision"
    )
    wrong_snapshot.mkdir(parents=True)
    required = tuple(sorted(audio_module.PINNED_MODEL_FILES))
    for name in required:
        wrong_snapshot.joinpath(name).write_bytes(b"model")
    old_snapshot = tmp_path / "models--Systran--faster-whisper-small" / "snapshots" / "one"
    old_snapshot.mkdir(parents=True)
    for name in required:
        old_snapshot.joinpath(name).write_bytes(b"model")
    assert not audio_module.local_model_available()

    snapshot = (
        tmp_path
        / "models--mobiuslabsgmbh--faster-whisper-large-v3-turbo"
        / "snapshots"
        / audio_module.MODEL_REVISION
    )
    snapshot.mkdir(parents=True)
    (snapshot / "model.bin").write_bytes(b"model")
    assert not audio_module.local_model_available()
    (snapshot / "config.json").write_text("{}", encoding="utf-8")
    assert not audio_module.local_model_available()
    tokenizer = snapshot / "tokenizer.json"
    tokenizer.write_text("{}", encoding="utf-8")
    assert not audio_module.local_model_available()
    (snapshot / "preprocessor_config.json").write_text("{}", encoding="utf-8")
    (snapshot / "vocabulary.json").write_text("{}", encoding="utf-8")
    assert audio_module.local_model_available()


def test_model_installer_verifies_the_pinned_snapshot(tmp_path, monkeypatch):
    calls = []

    class FakeWhisperModel:
        complete = False

        def __init__(self, model_name, **kwargs):
            calls.append((model_name, kwargs))
            snapshot = (
                tmp_path
                / audio_module.MODEL_CACHE_DIRECTORY
                / "snapshots"
                / audio_module.MODEL_REVISION
            )
            snapshot.mkdir(parents=True, exist_ok=True)
            files = set(audio_module.PINNED_MODEL_FILES)
            if not self.complete:
                files.remove("tokenizer.json")
            for name in files:
                snapshot.joinpath(name).write_bytes(b"model")

    monkeypatch.setattr(audio_module, "MODEL_CACHE", tmp_path)
    monkeypatch.setattr(audio_module, "prepare_transcription_runtime", lambda: None)
    monkeypatch.setitem(
        sys.modules,
        "faster_whisper",
        SimpleNamespace(WhisperModel=FakeWhisperModel),
    )

    with pytest.raises(RuntimeError, match="missing: tokenizer.json"):
        audio_module.install_local_model()
    FakeWhisperModel.complete = True
    audio_module.install_local_model()

    assert audio_module.local_model_available()
    assert calls[-1][0] == audio_module.MODEL_NAME
    assert calls[-1][1]["revision"] == audio_module.MODEL_REVISION


def test_provisioned_snapshot_matches_pinned_file_contract():
    snapshot = (
        audio_module.MODEL_CACHE
        / audio_module.MODEL_CACHE_DIRECTORY
        / "snapshots"
        / audio_module.MODEL_REVISION
    )
    if not snapshot.is_dir():
        pytest.skip("pinned production model is not provisioned on this machine")

    assert audio_module.PINNED_MODEL_FILES <= {path.name for path in snapshot.iterdir()}


def test_production_ui_supports_english_only():
    assert transcription_language_labels() == ("English",)
    assert production_transcription_language("English") == "en"
    with pytest.raises(KeyError):
        production_transcription_language("Hebrew")


def test_invalid_language_is_rejected_before_runtime_work():
    devices = catalog()
    with pytest.raises(ValueError, match="language"):
        AudioCallSession(
            devices,
            devices.microphones[0],
            devices.playbacks[0],
            "fr",
            require_installed_model=False,
        )


def test_catalog_enumeration_failure_terminates_backend():
    class BrokenBackend(FakeBackend):
        def get_host_api_info_by_type(self, _kind):
            raise OSError("unavailable")

    backend = BrokenBackend()
    with pytest.raises(AudioUnavailable):
        catalog(backend)
    assert backend.terminated


def test_revalidation_ignores_unrelated_catalog_change():
    backend = FakeBackend()
    devices = catalog(backend)
    backend.devices[1]["name"] = "Other microphone changed"

    devices.revalidate(devices.microphones[0], devices.playbacks[0])

    assert backend.open_calls == []
    assert not devices.closed


def test_revalidation_scan_failure_invalidates_catalog(monkeypatch):
    devices = catalog()
    microphone = devices.microphones[0]
    playback = devices.playbacks[0]

    def fail_scan():
        raise AudioUnavailable("unavailable")

    monkeypatch.setattr(devices, "_scan", fail_scan)
    with pytest.raises(AudioUnavailable, match="unavailable"):
        devices.revalidate(microphone, playback)
    assert devices.closed


def test_stopped_session_cannot_reuse_indices_or_reopen_streams():
    backend = FakeBackend()
    devices = catalog(backend)
    session = AudioCallSession(
        devices,
        devices.microphones[0],
        devices.playbacks[0],
        "en",
        model_factory=lambda: SimpleNamespace(
            transcribe=lambda *_args, **_kwargs: (iter(()), None)
        ),
        require_installed_model=False,
    )
    session.start()
    session.stop()

    with pytest.raises(RuntimeError, match="restarted"):
        session.start()
    assert len(backend.open_calls) == 2


def test_idle_source_watermark_releases_other_source_turn():
    devices = catalog()
    session = AudioCallSession(
        devices,
        devices.microphones[0],
        devices.playbacks[0],
        "en",
        model_factory=lambda: object(),
        require_installed_model=False,
    )
    session._configure_queues()
    session._orderer.finish_source("microphone")
    key = session._register(time.perf_counter() - 1, datetime.now(timezone.utc))
    session._orderer.complete(
        key,
        TurnDraft(
            "You",
            SpeakerRole.USER,
            "microphone",
            "released",
            datetime.now(timezone.utc),
        ),
    )
    worker = threading.Thread(
        target=session._source_worker,
        args=("system_audio_loopback",),
        daemon=True,
    )
    worker.start()

    wait_until(lambda: not session.results.empty())
    session._stop.set()
    worker.join(2)

    assert session.results.get_nowait().content == "released"
    assert not worker.is_alive()


def test_sparse_source_finalizes_open_utterance_without_more_callbacks():
    model = SimpleNamespace(
        transcribe=lambda *_args, **_kwargs: (
            iter((SimpleNamespace(text="heard"),)),
            None,
        )
    )
    devices = catalog()
    session = AudioCallSession(
        devices,
        devices.microphones[0],
        devices.playbacks[0],
        "en",
        model_factory=lambda: model,
        require_installed_model=False,
    )
    session._configure_queues()
    session._model = model
    session._source_done["system_audio_loopback"].set()
    session._orderer.finish_source("system_audio_loopback")
    workers = [
        threading.Thread(
            target=session._source_worker, args=("microphone",), daemon=True
        ),
        threading.Thread(target=session._transcription_worker, daemon=True),
    ]
    session._workers = workers
    for worker in workers:
        worker.start()
    base = time.perf_counter()
    ended = [base]
    session._monotonic_clock = lambda: ended[0]
    callback = session._callback("microphone")
    samples = np.full((19_200, 2), 1_000, dtype=np.int16)
    for offset in range(0, len(samples), 1_024):
        part = samples[offset : offset + 1_024]
        ended[0] = base + (offset + len(part)) / 48_000
        assert callback(part.tobytes(), len(part), {}, 0)[1] == FakeModule.paContinue
    session._monotonic_clock = time.perf_counter

    wait_until(lambda: not session.results.empty(), timeout=2)
    session._stop.set()
    for worker in workers:
        worker.join(2)

    assert session.results.get_nowait().content == "heard"
    assert not any(worker.is_alive() for worker in workers)


def test_sparse_short_candidate_releases_later_other_source_turn():
    devices = catalog()
    session = AudioCallSession(
        devices,
        devices.microphones[0],
        devices.playbacks[0],
        "en",
        model_factory=lambda: object(),
        require_installed_model=False,
    )
    session._configure_queues()
    session._orderer.finish_source("system_audio_loopback")
    base = time.perf_counter()
    now = [base]
    session._monotonic_clock = lambda: now[0]
    worker = threading.Thread(
        target=session._source_worker, args=("microphone",), daemon=True
    )
    worker.start()
    part = np.full((2_400, 2), 1_000, dtype=np.int16)
    now[0] = base + 0.05
    assert session._callback("microphone")(part.tobytes(), len(part), {}, 0)[1] == FakeModule.paContinue
    wait_until(lambda: session._native["microphone"].empty())
    time.sleep(0.05)
    key = session._register(base + 0.1, datetime.now(timezone.utc))
    session._orderer.complete(
        key,
        TurnDraft(
            "Contact",
            SpeakerRole.SELECTED_CONTACT,
            "system_audio_loopback",
            "later",
            datetime.now(timezone.utc),
        ),
    )
    assert session.results.empty()

    now[0] = base + 1.0
    wait_until(lambda: not session.results.empty())
    session._stop.set()
    worker.join(2)

    assert session.results.get_nowait().content == "later"
    assert not worker.is_alive()


def test_no_speech_status_updates_for_continuous_callback_sources():
    devices = catalog()
    session = AudioCallSession(
        devices,
        devices.microphones[0],
        devices.playbacks[0],
        "en",
        model_factory=lambda: object(),
        require_installed_model=False,
    )

    session._update_no_speech_status("microphone", False, 1.0, 11.0)

    assert session.snapshot().microphone_status == "Listening — no speech detected"


def test_unregistered_candidate_clamps_watermark_before_simultaneous_turn():
    devices = catalog()
    session = AudioCallSession(
        devices,
        devices.microphones[0],
        devices.playbacks[0],
        "en",
        model_factory=lambda: object(),
        require_installed_model=False,
    )
    segmenter = SpeechSegmenter(100, session._register, session._orderer.cancel)
    now = datetime.now(timezone.utc)
    segmenter.feed(MonoBlock(np.full(800, 1_000, dtype=np.int16), 10.0, now))
    newer = session._register(10.05, now)
    session._orderer.complete(
        newer,
        TurnDraft("You", SpeakerRole.USER, "microphone", "newer", now),
    )
    session._orderer.finish_source("microphone")

    session._advance_source("system_audio_loopback", segmenter, 12.0)

    assert session.results.empty()


def test_empty_inference_is_cancelled_without_a_final_result():
    devices = catalog()
    session = AudioCallSession(
        devices,
        devices.microphones[0],
        devices.playbacks[0],
        "en",
        model_factory=lambda: SimpleNamespace(
            transcribe=lambda *_args, **_kwargs: (
                iter((SimpleNamespace(text="   "),)),
                None,
            )
        ),
        require_installed_model=False,
    )
    session.start()
    now = datetime.now(timezone.utc)
    key = session._register(time.perf_counter(), now)
    session._jobs.put_nowait(
        (
            key,
            UtteranceJob(
                key,
                "microphone",
                np.ones(16_000, dtype=np.int16),
                key[0],
                now,
                key[0],
                time.perf_counter(),
            ),
        )
    )

    wait_until(lambda: session._jobs.empty() and session._orderer.retained_count == 0)
    session.stop()

    assert session.results.empty()
    assert session.snapshot().fault == ""


def test_benchmark_separates_single_and_overlapping_latency(tmp_path):
    import wave

    for name in ("single.wav", "overlap.wav"):
        with wave.open(str(tmp_path / name), "wb") as stream:
            stream.setnchannels(1)
            stream.setsampwidth(2)
            stream.setframerate(16_000)
            stream.writeframes(b"\0\0" * 16_000)
    manifest = {
        "clips": {"single.wav": {}, "overlap.wav": {}},
        "schedule": [
            {"source": "microphone", "clip": "single.wav", "start_seconds": 0.0},
            {
                "source": "system_audio_loopback",
                "clip": "overlap.wav",
                "start_seconds": 10.0,
            },
            {"source": "microphone", "clip": "single.wav", "start_seconds": 10.5},
        ],
    }

    single, overlap = _latency_groups(
        [("microphone", 0.0, 1.5), ("system_audio_loopback", 10.0, 3.5)],
        tmp_path,
        manifest,
    )

    assert single == [1.5]
    assert overlap == [3.5]


def test_source_worker_downmixes_resamples_segments_and_timestamps():
    class ScriptedModel:
        def transcribe(self, *_args, **_kwargs):
            return iter((SimpleNamespace(text="heard"),)), None

    devices = catalog()
    session = AudioCallSession(
        devices,
        devices.microphones[0],
        devices.playbacks[0],
        "en",
        model_factory=ScriptedModel,
        require_installed_model=False,
    )
    session._configure_queues()
    session._model = ScriptedModel()
    session._source_done["system_audio_loopback"].set()
    session._orderer.finish_source("system_audio_loopback")
    workers = [
        threading.Thread(target=session._source_worker, args=("microphone",), daemon=True),
        threading.Thread(target=session._transcription_worker, daemon=True),
    ]
    session._workers = workers
    for worker in workers:
        worker.start()
    started_utc = datetime.now(timezone.utc)
    stereo = np.repeat(
        np.concatenate(
            (np.full(24_000, 1_000, dtype=np.int16), np.zeros(28_800, dtype=np.int16))
        )[:, None],
        2,
        axis=1,
    )
    for offset in range(0, len(stereo), 1_024):
        part = stereo[offset : offset + 1_024]
        session._native["microphone"].put(
            SimpleNamespace(
                data=part.tobytes(),
                frames=len(part),
                started_monotonic=10.0 + offset / 48_000,
                started_utc=started_utc + timedelta(seconds=offset / 48_000),
            ),
            timeout=2,
        )
    session._stop.set()
    for worker in workers:
        worker.join(5)

    assert not any(worker.is_alive() for worker in workers)
    draft = session.results.get_nowait()
    assert draft.content == "heard"
    assert draft.source == "microphone"
    assert abs((draft.timestamp - started_utc).total_seconds()) < 0.03
