from conversation_copilot.memory import (MemoryStore, FakeMemoryExtractor, ExtractionOutput,
    MemoryProposalInput, analyze_record, extraction_chunks, extraction_reservation_tokens)
from conversation_copilot.models import ConversationTurn, SpeakerRole


def turns(count):
    return [ConversationTurn(display_order=i, speaker_name="Alex", speaker_role=SpeakerRole.SELECTED_CONTACT,
                             content=f"Specific project detail {i}.", source="fixture") for i in range(1, count+1)]


def test_whole_short_call_and_overlap_stay_bounded():
    assert ExtractionOutput.model_json_schema()["properties"]["proposals"]["maxItems"] == 12
    source = turns(88)
    assert len(extraction_chunks(source)) == 1
    assert extraction_reservation_tokens(source) <= 9000
    chunks = extraction_chunks(turns(9), max_turns=5)
    assert [[t.display_order for t in c] for c in chunks] == [[1,2,3,4,5],[3,4,5,6,7],[5,6,7,8,9]]
    assert len(extraction_chunks(source, max_turns=20, legacy=True)) == 5


def test_resume_legacy_layout_and_overlap_preserves_new_facts(tmp_path):
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        contact = store.create_contact("Alex")
        record = store.create_record(source_kind="call", source_label="Legacy", contact_id=contact.id,
                                     timezone_name="UTC", status="stopped", turns=turns(41))
        batch = store.create_batch(record, model="fake", reasoning="none", chunks_total=3)
        store.append_batch_chunk(batch, [], input_tokens=0, output_tokens=0, reasoning_tokens=0, cost_dollars=0)
        store.fail_batch(batch, "interrupted")
        fake = FakeMemoryExtractor([ExtractionOutput(), ExtractionOutput()])
        analyze_record(store, record, fake, batch_id=batch)
        assert [[t.display_order for t in c] for c in fake.calls] == [list(range(21,41)),[41]]
        record = store.create_record(source_kind="call", source_label="Overlap", contact_id=contact.id,
                                     timezone_name="UTC", status="stopped", turns=turns(7))
        first = MemoryProposalInput(content="Alex prefers green", memory_type="preference", confidence="high", evidence_turns=[3])
        second = MemoryProposalInput(content="Alex will finish Friday", memory_type="other", confidence="high", evidence_turns=[6])
        recovered = first.model_copy(update={"content": "Alex prefers quiet offices"})
        batch = analyze_record(store, record, FakeMemoryExtractor([
            ExtractionOutput(proposals=[first]), ExtractionOutput(proposals=[first,second,recovered])]), chunk_turns=5)
        rows = store._connection.execute("SELECT content FROM memory_proposals WHERE batch_id=?", (batch,)).fetchall()
        assert sorted(r[0] for r in rows) == sorted([first.content,first.content,second.content,recovered.content])
        assert store._connection.execute("SELECT count(*) FROM potential_duplicates").fetchone()[0] >= 1


def test_whole_summary_uses_all_turns_and_checkpoints_legacy_range(tmp_path):
    import json
    from types import SimpleNamespace
    from conversation_copilot.memory import SummaryOutput, SummaryStatementInput
    from conversation_copilot.post_call import process_review, _whole_summary_fits
    from conversation_copilot.interpretation import UsageLedger
    source = turns(88)
    assert _whole_summary_fits(source)
    assert not _whole_summary_fits([t.model_copy(update={"content": "specific detail " * 100}) for t in source])
    with MemoryStore(tmp_path / "summary.sqlite3") as store:
        contact = store.create_contact("Alex")
        record = store.create_record(source_kind="call", source_label="Whole", contact_id=contact.id,
                                     timezone_name="UTC", status="stopped", turns=source)
        calls = []
        def parse(**kwargs):
            payload = json.loads(kwargs["input"])
            calls.append(payload)
            assert len(payload["turns"]) == 88 and kwargs["reasoning"]["effort"] == "low"
            return SimpleNamespace(output_parsed=SummaryOutput(statements=[SummaryStatementInput(
                section="discussed", content="Alex discussed a project.", kind="fact", confidence="high", evidence_turns=[1,88])]),
                usage=SimpleNamespace(input_tokens=100, output_tokens=100))
        process_review(store, record, ledger=UsageLedger(), extractor=FakeMemoryExtractor([ExtractionOutput()]),
                       client=SimpleNamespace(responses=SimpleNamespace(parse=parse)))
        assert len(calls) == 1
        row = store._connection.execute("SELECT first_chunk,chunk_index FROM review_chunks WHERE record_id=?", (record,)).fetchone()
        assert tuple(row) == (0,4)
