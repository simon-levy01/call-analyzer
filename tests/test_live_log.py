import json
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace

import pytest
from pydantic import BaseModel

from conversation_copilot import test_log


def test_log_concurrent_roundtrip_and_media_rejection(tmp_path):
    log = test_log.TestLog(tmp_path / "evidence")
    with ThreadPoolExecutor(4) as pool:
        list(pool.map(lambda i: log.write("visual", sample=i), range(100)))
    log.pending.join()
    lines = [json.loads(line) for line in log.path.read_text(encoding="utf8").splitlines()]
    assert len(lines) == 100
    assert [line["sequence"] for line in lines] == list(range(1, 101))
    assert {line["data"]["sample"] for line in lines} == set(range(100))
    log.write("forbidden", frame=b"raw pixels")
    assert log.error == "TypeError"
    log.write("after_bad_record", valid=True)
    log.pending.join()
    rows = [json.loads(line) for line in log.path.read_text(encoding="utf8").splitlines()]
    assert len(rows) == 102
    assert rows[-2]["serialization_error"] == "TypeError"
    assert rows[-1]["data"] == {"valid": True}
    log.close()


def test_empty_guidance_has_replayable_evidence(tmp_path, monkeypatch):
    from conversation_copilot import guidance
    from conversation_copilot.f04_evaluation import EvaluationScenario
    from conversation_copilot.interpretation import UsageLedger
    log = test_log.TestLog(tmp_path / "evidence")
    monkeypatch.setattr(test_log, "active", log)
    snapshot = EvaluationScenario("log", "f06", "What happened?", "The bus arrived.").snapshot("transcript")
    output = guidance.GuidanceOutput.model_validate({"interpretation": {
        "status": "insufficient_evidence", "tones": [], "social_cues": []}})
    monkeypatch.setattr(guidance, "f06_structured_request", lambda *a, **k: (output, None))
    result = guidance.interpret_guidance(snapshot, ledger=UsageLedger())
    assert not result.replies
    assert log.error is None
    log.pending.join()
    events = [json.loads(line) for line in log.path.read_text(encoding="utf8").splitlines()]
    assert [e["event"] for e in events] == ["guidance_input", "guidance_supplied_evidence", "guidance_empty"]
    assert events[0]["data"]["snapshot"] == snapshot.model_dump(mode="json")
    log.close()
    with pytest.raises(FileExistsError):
        test_log.TestLog(tmp_path / "evidence")


def test_api_log_preserves_request_response_and_exception(tmp_path, monkeypatch):
    class Answer(BaseModel):
        answer: str
    log = test_log.TestLog(tmp_path / "evidence")
    monkeypatch.setattr(test_log, "active", log)
    seen = []
    response = Answer(answer="hello")
    def parse(**kwargs):
        seen.append(kwargs)
        return response
    client = SimpleNamespace(responses=SimpleNamespace(parse=parse), api_key="secret-key")
    kwargs = dict(model="fixture", input="test", instructions="fixture", text_format=Answer, store=False)
    assert test_log.parse_response(client, **kwargs) is response
    assert seen == [kwargs]
    def fail(**kwargs):
        raise RuntimeError("secret error body")
    client.responses.parse = fail
    with pytest.raises(RuntimeError):
        test_log.parse_response(client, **kwargs)
    log.pending.join()
    text = log.path.read_text(encoding="utf8")
    assert "secret" not in text
    rows = [json.loads(line) for line in text.splitlines()]
    assert [r["event"] for r in rows] == ["api_request", "api_response", "api_request", "api_error"]
    assert rows[0]["data"]["request_id"] == rows[1]["data"]["request_id"]
    assert rows[1]["data"]["response"] == {"answer": "hello"}
    log.close()


def test_memory_extraction_uses_the_same_opt_in_request_logger(monkeypatch):
    from conversation_copilot.memory import OpenAIMemoryExtractor, ExtractionOutput
    from conversation_copilot.f04_evaluation import EvaluationScenario
    from conversation_copilot.interpretation import UsageLedger
    seen = []
    response = SimpleNamespace(output_parsed=ExtractionOutput(),
                               usage=SimpleNamespace(input_tokens=300, output_tokens=30))
    client = object()  # No actual network client can be called.
    def record(actual_client, **kwargs):
        assert actual_client is client
        seen.append(kwargs)
        return response
    monkeypatch.setattr(test_log, 'parse_response', record)
    turns = EvaluationScenario('memory-log','log','What next?','The appointment is Friday.').snapshot('transcript').turns
    from conversation_copilot.models import ConversationTurn
    turns = [ConversationTurn(**t.model_dump(), speaker_name='Contact', source='fixture') for t in turns]
    output, _ = OpenAIMemoryExtractor(client=client, ledger=UsageLedger())(turns)
    assert not output.proposals and len(seen) == 1
    assert seen[0]['text_format'] is ExtractionOutput and seen[0]['store'] is False


def test_slow_disk_does_not_block_call_thread(tmp_path):
    import threading
    log = test_log.TestLog(tmp_path / "evidence")
    real = log.stream
    blocked = threading.Event()
    resume = threading.Event()
    class SlowStream:
        def write(self, line):
            blocked.set()
            assert resume.wait(5)
            real.write(line)
        def flush(self):
            real.flush()
        def close(self):
            real.close()
    log.stream = SlowStream()
    try:
        log.write("first")
        assert blocked.wait(2)
        log.write("second")  # Returns while the writer is still blocked.
        assert log.pending.qsize() == 1
    finally:
        resume.set()
        log.close()
    assert len(log.path.read_text(encoding="utf8").splitlines()) == 2


def test_start_failure_leaves_app_available(monkeypatch):
    monkeypatch.setenv("COPILOT_TEST_LOG", "1")
    monkeypatch.setattr(test_log, "active", None)
    monkeypatch.setattr(test_log, "startup_error", None)
    def denied(_path):
        raise PermissionError("private path")
    monkeypatch.setattr(test_log, "TestLog", denied)
    test_log.start()
    assert test_log.active is None
    assert test_log.startup_error == "PermissionError"


def test_visual_evidence_can_be_replayed_without_images(tmp_path):
    from datetime import datetime, timedelta, timezone
    from conversation_copilot.interpretation import VisualAggregator
    from conversation_copilot.video import FaceBox, FacialSignal
    log = test_log.TestLog(tmp_path / "evidence")
    original = VisualAggregator()
    start = datetime(2026, 9, 15, tzinfo=timezone.utc)
    for index in range(30):
        now = start + timedelta(seconds=index / 10)
        signal = FacialSignal(index * 100, FaceBox(.1, .1, .4, .4), (),
                              (("mouthSmileLeft", .8), ("mouthSmileRight", .8)))
        original.add(signal, now, captured_at=now)
        log.write("visual", observed_at=now, captured_at=now, signal_timestamp_ms=signal.timestamp_ms,
                  face_box=signal.face_box, blendshapes=dict(signal.blendshapes),
                  expressions=original.expressions(), buckets=original.buckets(now)[-1:])
    log.close()
    replay = VisualAggregator()
    for line in log.path.read_text(encoding="utf8").splitlines():
        item = json.loads(line)["data"]
        now = datetime.fromisoformat(item["observed_at"])
        signal = FacialSignal(item["signal_timestamp_ms"], FaceBox(**item["face_box"]), (), tuple(item["blendshapes"].items()))
        replay.add(signal, now, captured_at=datetime.fromisoformat(item["captured_at"]))
        assert [value.model_dump(mode="json") for value in replay.expressions()] == item["expressions"]
    assert replay.buckets(now) == original.buckets(now)
    assert log.error is None
