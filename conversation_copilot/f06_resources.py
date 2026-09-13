"""F06 CPU Ask / cached GPU transcription and synthetic video resource sample."""
import argparse
import ctypes
import json
import statistics
import sys
import threading
import time
import wave
from pathlib import Path

import numpy as np

from .f06_evaluation import seed_case
from .memory import MemoryStore, default_database_path
from .semantic import default_cache_dir, embed_texts_if_ready


def distribution(values):
    values = sorted(values)
    return {"count": len(values), "p50_ms": statistics.median(values),
            "p95_ms": values[max(0, int(len(values) * .95) - 1)], "max_ms": max(values)}


def process_memory():
    class Counters(ctypes.Structure):
        _fields_ = [("cb", ctypes.c_ulong), ("PageFaultCount", ctypes.c_ulong)] + [
            (name, ctypes.c_size_t) for name in ("PeakWorkingSetSize", "WorkingSetSize", "QuotaPeakPagedPoolUsage",
            "QuotaPagedPoolUsage", "QuotaPeakNonPagedPoolUsage", "QuotaNonPagedPoolUsage", "PagefileUsage", "PeakPagefileUsage", "PrivateUsage")]
    counters = Counters()
    counters.cb = ctypes.sizeof(counters)
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.GetCurrentProcess.restype = ctypes.c_void_p
    get_memory = ctypes.WinDLL("psapi").GetProcessMemoryInfo
    get_memory.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong]
    if not get_memory(kernel.GetCurrentProcess(), ctypes.byref(counters), counters.cb):
        raise ctypes.WinError()
    return {name: getattr(counters, name) for name in ("PeakWorkingSetSize", "WorkingSetSize", "PrivateUsage", "PeakPagefileUsage")}


def measure_source_revalidation():
    from datetime import datetime, timezone
    from .models import ConversationTurn, SpeakerRole
    from .memory import SummaryOutput, SummaryStatementInput
    from .ask_memory import memory_source, summary_source, validate_sources
    with MemoryStore(":memory:") as store:
        contact = store.create_contact("F06 fictional long record")
        record = store.create_record(source_kind="call", source_label="500-turn revalidation", timezone_name="UTC", contact_id=contact.id, status="stopped",
            turns=[ConversationTurn(speaker_name="Contact", speaker_role=SpeakerRole.SELECTED_CONTACT, source="fixture",
                content=f"Plan {i}: an appointment needs confirmation.", timestamp=datetime(2026, 9, 7, tzinfo=timezone.utc), display_order=i) for i in range(1, 501)])
        memories = [store.create_memory(contact.id, f"Plan {i}: an appointment needs confirmation.", record_id=record, evidence_turns=[i]) for i in (1, 2)]
        summary = store.create_summary_draft(record, SummaryOutput(statements=[SummaryStatementInput(section="plans", content=f"Plan {i} needs confirmation.",
            kind="fact", confidence="high", evidence_turns=[i]) for i in (3, 4)]), expected_generation=1)
        store.approve_summary(summary)
        sources = tuple([memory_source(store, memory, contact.id) for memory in memories] +
                        [summary_source(store, row["id"], contact.id) for row in store.summary_statements(summary)])
        loads, times = [], []
        store._connection.set_trace_callback(lambda sql: loads.append(sql) if sql.startswith("SELECT * FROM conversation_turns WHERE") else None)
        for _ in range(100):
            started = time.perf_counter()
            assert validate_sources(store, sources)
            times.append((time.perf_counter() - started) * 1000)
        store._connection.set_trace_callback(None)
        assert len(loads) == 100, "each pass must load the shared record only once"
        store.delete_memory(memories[0])
        assert not validate_sources(store, sources), "cache must not outlive one validation pass"
        return {"record_turns": 500, "sources": 4, "full_record_loads_per_pass": 1, "latency": distribution(times)}


def run(output):
    cache = default_cache_dir(default_database_path())
    original = MemoryStore.semantic_cache_dir
    MemoryStore.semantic_cache_dir = property(lambda _self: cache)
    cold = time.perf_counter()
    assert embed_texts_if_ready(["What time is the dentist appointment?"], cache) is not None
    report = {"cold_bge_ms": (time.perf_counter() - cold) * 1000, "cpu_embedding_threads": 2, "ask_device": "CPU", "profiles": {}}
    def ask_queries(stop=None):
        with MemoryStore(":memory:") as store:
            session, _ = seed_case(store, "appointment")
            for index in range(99):
                store.create_memory(session.contact_id, f"Book number {index} is on the reading list.")
            store.backfill_semantic_embeddings()
            session.answer(store, "What time is the dentist appointment?")
            times, cpu = [], []
            dated_times = []
            while len(times) < 100 or (stop is not None and not stop.is_set()):
                started, processor = time.perf_counter(), time.process_time()
                dated = len(times) % 2 == 1
                result = session.answer(store, "What time is the dentist appointment recorded 07/09/2026?" if dated else "What time is the dentist appointment?",
                                        date_mode="recorded" if dated else None)
                assert result.status == "answered" and "3 PM" in result.answer
                times.append((time.perf_counter() - started) * 1000)
                if dated:
                    dated_times.append(times[-1])
                cpu.append((time.process_time() - processor) * 1000)
            return {"latency": distribution(times), "recorded_date_latency": distribution(dated_times), "process_cpu_time": distribution(cpu), "memory": process_memory(),
                    "current_memories": 100, "vectors": store._connection.execute("SELECT count(*) FROM memory_embeddings").fetchone()[0]}
    try:
        report["source_revalidation"] = measure_source_revalidation()
        report["profiles"]["ask_only"] = ask_queries()
        from .audio import _load_local_model, TRANSCRIBE_OPTIONS
        from .video import FaceProcessor
        import cv2
        fixture = Path(__file__).parent / "assets" / "f04"
        manifest = json.loads((fixture / "basic-video-chat.json").read_text())
        audio = {}
        for speaker, stem in (("alex", "user"), ("maya", "contact")):
            with wave.open(str(fixture / f"basic-video-chat-{stem}.wav")) as stream:
                audio[speaker] = np.frombuffer(stream.readframes(stream.getnframes()), dtype="<i2").astype(np.float32) / 32768
        model = _load_local_model()
        video = cv2.VideoCapture(str(fixture / "basic-video-chat.mp4"))
        frames = []
        turns = manifest["turns"][:12]
        for turn in turns:
            video.set(cv2.CAP_PROP_POS_MSEC, 1000 * (turn["start_seconds"] + turn["end_seconds"]) / 2)
            okay, frame = video.read()
            assert okay
            frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA))
        video.release()
        first = turns[0]
        list(model.transcribe(audio[first["speaker"]][int(first["start_seconds"] * 16000):int(first["end_seconds"] * 16000)], language="en", **TRANSCRIBE_OPTIONS)[0])
        baseline_text = None
        for concurrent in (False, True):
            stop = threading.Event()
            answer_result, failures = [], []
            def ask_worker():
                try:
                    answer_result.append(ask_queries(stop))
                except Exception as exc:
                    failures.append(str(exc))
            worker = threading.Thread(target=ask_worker) if concurrent else None
            if worker:
                worker.start()
            processor = FaceProcessor()
            transcription, video_times, decoded = [], [], []
            try:
                for index in range(36):
                    turn = turns[index % len(turns)]
                    samples = audio[turn["speaker"]][int(turn["start_seconds"] * 16000):int(turn["end_seconds"] * 16000)]
                    started = time.perf_counter()
                    segments, _ = model.transcribe(samples, language="en", **TRANSCRIBE_OPTIONS)
                    text = " ".join(segment.text for segment in segments)
                    transcription.append((time.perf_counter() - started) * 1000)
                    assert text.strip()
                    decoded.append((turn["speaker"], text))
                    started = time.perf_counter()
                    processor.process(frames[index % len(turns)], index * 500)
                    video_times.append((time.perf_counter() - started) * 1000)
            finally:
                processor.close()
                stop.set()
                if worker:
                    worker.join()
            assert not failures, failures
            report["profiles"]["concurrent" if concurrent else "transcription_video"] = {
                "transcription": distribution(transcription), "video": distribution(video_times),
                "completed_turns": len(decoded), "memory": process_memory(), "ask": answer_result,
                "same_attributed_text": decoded == baseline_text if concurrent else True}
            baseline_text = decoded
        profiles = report["profiles"]
        report["transcription_p95_regression_percent"] = 100 * (profiles["concurrent"]["transcription"]["p95_ms"] / profiles["transcription_video"]["transcription"]["p95_ms"] - 1)
        report["expanded_venv_bytes"] = sum(p.stat().st_size for p in Path(sys.prefix).rglob("*") if p.is_file())
        report["bge_cache_bytes"] = sum(p.stat().st_size for p in cache.rglob("*") if p.is_file())
        report["limitations"] = "Fictional cached-model replay; no physical capture or real call. Process CPU samples during concurrent work include other threads. No raw media produced."
    finally:
        MemoryStore.semantic_cache_dir = original
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    run(parser.parse_args().output)
