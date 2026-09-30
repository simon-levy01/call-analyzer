from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from conversation_copilot.ask_memory import memory_source
from conversation_copilot.guidance import (
    GuidanceCandidate,
    GuidanceDisplay,
    GuidedInterpretation,
    capture_live_suggestion,
)
from conversation_copilot.interpretation import (
    BudgetLimits,
    Evidence,
    InterpretationBudgetExceeded,
    LIVE_ASK_MODELS,
    LIVE_ASK_REASONING,
    LUNA_MODEL,
    REVIEW_MODEL,
    REVIEW_REASONING,
    SocialCue,
    SOL_MODEL,
    ToneHypothesis,
    UsageLedger,
    UsageRecord,
)
from conversation_copilot.memory import (
    ExtractionOutput,
    FakeMemoryExtractor,
    MemoryProposalInput,
    MemoryStore,
    SummaryOutput,
    SummaryStatementInput,
)
from conversation_copilot.models import ConversationTurn, SpeakerRole
from conversation_copilot.post_call import process_review


def turn(order: int, text: str) -> ConversationTurn:
    return ConversationTurn(
        speaker_name="Alex",
        speaker_role=SpeakerRole.SELECTED_CONTACT,
        source="saved-test",
        content=text,
        timestamp=datetime(2026, 9, 21, 12, 0, order, tzinfo=timezone.utc),
        display_order=order,
    )


def record(store: MemoryStore, contact_id: str) -> str:
    return store.create_record(
        source_kind="call",
        source_label="fictional F10 test",
        timezone_name="UTC",
        contact_id=contact_id,
        status="stopped",
        turns=[turn(1, "The appointment is Tuesday."), turn(2, "The venue is Cedar Clinic.")],
    )


def test_product_profiles_and_uncapped_accounting_preserve_evaluation_caps():
    assert LIVE_ASK_MODELS == (LUNA_MODEL, SOL_MODEL) == ("gpt-5.6-luna", "gpt-6.1-sol")
    assert LIVE_ASK_REASONING == REVIEW_REASONING == "low"
    assert REVIEW_MODEL == LIVE_ASK_MODELS[-1]

    product = UsageLedger.product()
    reservation = product.reserve(SOL_MODEL, 9_000, max_output_tokens=2_400)
    product.complete(reservation, UsageRecord(SOL_MODEL, "low", 0, 0, 0, 0, 0, 10.0))
    product.release(product.reserve(SOL_MODEL, 9_000, max_output_tokens=2_400))
    assert product.total_dollars == 10.0 and not product.warning_reached

    capped = UsageLedger(BudgetLimits(0.01, 0.02, 0.03))
    reservation = capped.reserve(LUNA_MODEL, 1, max_output_tokens=1)
    capped.complete(reservation, UsageRecord(LUNA_MODEL, "low", 0, 0, 0, 0, 0, 0.02))
    with pytest.raises(InterpretationBudgetExceeded):
        capped.reserve(LUNA_MODEL, 1, max_output_tokens=1)


def test_sensitive_approved_memory_is_cloud_eligible_without_rewriting_permission_history(tmp_path):
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        contact = store.create_contact("Alex")
        memory_id = store.create_memory(contact.id, "Private appointment", sensitivity="sensitive")
        assert not store.current_revision(memory_id)["cloud_allowed"]
        source = memory_source(store, memory_id, contact.id, for_cloud=True)
        assert source is not None and source.cloud_allowed


def test_review_pipeline_uses_higher_end_low_provenance(tmp_path, monkeypatch):
    from conversation_copilot import post_call

    calls = []

    def request(*_args, **kwargs):
        calls.append(kwargs)
        return (
            SummaryOutput(statements=[SummaryStatementInput(
                section="discussed",
                content="Alex said the appointment is Tuesday.",
                kind="fact",
                confidence="high",
                evidence_turns=[1],
            )]),
            SimpleNamespace(input_tokens=1, output_tokens=1, reasoning_tokens=0, dollars=0.01),
        )

    monkeypatch.setattr(post_call, "f06_structured_request", request)
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        contact = store.create_contact("Alex")
        record_id = record(store, contact.id)
        summary_id = process_review(
            store,
            record_id,
            ledger=UsageLedger.product(),
            extractor=FakeMemoryExtractor([ExtractionOutput()]),
        )
        batch = store._connection.execute(
            "SELECT model,reasoning FROM proposal_batches WHERE record_id=?", (record_id,)
        ).fetchone()
        summary = store._connection.execute(
            "SELECT model FROM summary_versions WHERE id=?", (summary_id,)
        ).fetchone()
        assert tuple(batch) == (REVIEW_MODEL, "low")
        assert summary[0] == REVIEW_MODEL
        assert calls and all(call["model"] == REVIEW_MODEL and call["reasoning"] == "low" for call in calls)


def test_gpt6_prices_preserve_historical_accounting():
    from conversation_copilot.interpretation import _request_cost
    assert _request_cost(LUNA_MODEL, 1_000_000, 0, 1_000_000) == pytest.approx(1.40)
    assert _request_cost("gpt-6-luna", 1_000_000, 0, 1_000_000) == pytest.approx(0.60)
    assert _request_cost(SOL_MODEL, 1_000_000, 0, 1_000_000) == pytest.approx(12.00)
    assert _request_cost(SOL_MODEL, 1_000_000, 1_000_000, 0) == pytest.approx(.10)
    assert _request_cost("gpt-6-sol", 1_000_000, 1_000_000, 0) == pytest.approx(.20)
    assert _request_cost(SOL_MODEL, 1_000_000, 0, 0, 1_000_000) == pytest.approx(2.50)
    assert _request_cost("gpt-5.6-luna", 1_000_000, 0, 1_000_000) == pytest.approx(1.40)
    assert _request_cost("gpt-5.6-terra", 1_000_000, 0, 1_000_000) == pytest.approx(14.00)


@pytest.mark.parametrize("old_model", ["gpt-5.6-terra", "gpt-6-sol"])
def test_model_change_restarts_partial_extraction_without_relabeling(tmp_path, old_model):
    from conversation_copilot.memory import analyze_record
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        contact = store.create_contact("Alex")
        record_id = record(store, contact.id)
        old = store.create_batch(record_id, model=old_model, reasoning="low", chunks_total=1)
        store.fail_batch(old, "interrupted")
        new = analyze_record(store, record_id, FakeMemoryExtractor([ExtractionOutput()]), batch_id=old)
        assert new != old
        rows = {row["id"]: row for row in store._connection.execute("SELECT * FROM proposal_batches")}
        assert rows[old]["model"] == old_model and rows[old]["status"] == "invalidated"
        assert rows[new]["model"] == REVIEW_MODEL and rows[new]["status"] == "pending_review"


def test_four_item_live_contract_and_fixed_snapshots_cover_all_categories():
    evidence = Evidence(
        explanation="Current words and approved context",
        modalities=["language", "memory"],
        turn_ids=[2],
        memory_ids=["revision-1"],
    )
    tone = ToneHypothesis(kind="positive_warm", confidence="medium", hypothesis="Possible warmth", evidence=evidence)
    cue = SocialCue(kind="interest_engagement", confidence="medium", hypothesis="Possible interest", evidence=evidence)
    candidate = GuidanceCandidate(
        text="Could you say more?", confidence="medium", turn_ids=[2], memory_ids=["revision-1"]
    )
    update = GuidedInterpretation(
        status="updated",
        tones=[tone] * 4,
        social_cues=[cue] * 4,
        replies=[candidate] * 4,
        remember=[candidate] * 4,
        follow_up=[candidate] * 4,
        snapshot_id=1,
        generation=1,
    )
    assert all(len(getattr(update, category)) == 4 for category in (
        "tones", "social_cues", "replies", "remember", "follow_up"
    ))
    for category in ("tones", "social_cues", "replies", "remember", "follow_up"):
        frozen = capture_live_suggestion(update, category, 0, contact_id="contact-1")
        assert frozen.sources_are_current(
            contact_id="contact-1", turn_ids=[1, 2], memory_ids=["revision-1"]
        )
        assert not frozen.sources_are_current(
            contact_id="contact-1", turn_ids=[1, 2], memory_ids=[]
        )
    display = GuidanceDisplay()
    display.dismiss("tones", 0, update=update)
    assert not display.filter_update(update).tones
    assert display.filter_update(update).social_cues
    display.offer(update.model_copy(update={"manual": True}), 1, manual=True)
    assert display.filter_update(update).tones


def test_record_bulk_review_is_atomic_and_combined_approval_includes_unlinked_pending(tmp_path):
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        contact = store.create_contact("Alex")
        record_id = record(store, contact.id)
        batch = store.create_batch(record_id, model="fake", reasoning="none")
        proposal_ids = store.store_proposals(batch, [
            MemoryProposalInput(content="Appointment Tuesday", memory_type="event_date", confidence="high", evidence_turns=[1]),
            MemoryProposalInput(content="Venue Cedar Clinic", memory_type="event_date", confidence="high", evidence_turns=[2]),
        ])
        expected = {row["id"]: row["content"] for row in store.record_pending_proposals(record_id)}
        with pytest.raises(ValueError, match="changed"):
            store.review_record_proposals(
                record_id, proposal_ids, approve=False,
                expected_pending={**expected, proposal_ids[0]: "stale text"},
            )
        assert {row["state"] for row in store.list_proposals(contact.id)} == {"pending"}

        summary_id = store.create_summary_draft(
            record_id,
            SummaryOutput(statements=[SummaryStatementInput(
                section="discussed", content="The appointment is Tuesday.", kind="fact",
                confidence="high", evidence_turns=[1],
            )]),
            expected_generation=1,
        )
        statements = {
            row["id"]: (row["content"], row["excluded"])
            for row in store.summary_statements(summary_id)
        }
        store.approve_all_memories_and_summary(
            summary_id, expected_pending=expected, expected_statements=statements
        )
        assert store._connection.execute(
            "SELECT state FROM summary_versions WHERE id=?", (summary_id,)
        ).fetchone()[0] == "approved"
        assert {row["state"] for row in store._connection.execute(
            "SELECT state FROM memory_proposals WHERE id IN (?,?)", proposal_ids
        )} == {"approved"}

        reject_record = record(store, contact.id)
        reject_batch = store.create_batch(reject_record, model="fake", reasoning="none")
        rejected = store.store_proposals(reject_batch, [
            MemoryProposalInput(content="Draft one", memory_type="other", confidence="medium", evidence_turns=[1]),
            MemoryProposalInput(content="Draft two", memory_type="other", confidence="medium", evidence_turns=[2]),
        ])
        reject_expected = {
            row["id"]: row["content"] for row in store.record_pending_proposals(reject_record)
        }
        store.review_record_proposals(
            reject_record, None, approve=False, expected_pending=reject_expected
        )
        assert {row["state"] for row in store._connection.execute(
            "SELECT state FROM memory_proposals WHERE id IN (?,?)", rejected
        )} == set()
