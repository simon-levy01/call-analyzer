import json
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from conversation_copilot.interpretation import (
    BudgetLimits,
    Evidence,
    EvidenceModality,
    InterpretationCoordinator,
    InterpretationUpdate,
    OpenAIInterpreter,
    RetrievedMemoryContext,
    SocialCue,
    UsageLedger,
    VisualBucket,
    build_snapshot,
    format_interpretation_body,
    prepare_interpretation_request,
)
from conversation_copilot.__main__ import _relabel_contact_turns
from conversation_copilot.memory import (
    format_memory_date as _format_memory_date,
    memory_retrieval_inputs as _memory_retrieval_inputs,
    parse_memory_date as _parse_memory_date,
)
from conversation_copilot.models import ConversationTurn, SpeakerRole


def turns():
    started = datetime(2026, 8, 25, 12, tzinfo=timezone.utc)
    return [
        ConversationTurn(
            speaker_name="You", speaker_role=SpeakerRole.USER, source="microphone",
            content="How have you been since the event?", timestamp=started, display_order=1,
        ),
        ConversationTurn(
            speaker_name="Maya", speaker_role=SpeakerRole.SELECTED_CONTACT, source="playback",
            content="It has been difficult, but I appreciate you asking.",
            timestamp=started + timedelta(seconds=5), display_order=2,
        ),
    ]


def test_memory_dates_use_day_month_year_in_the_ui():
    parsed = _parse_memory_date("25/08/2026")
    assert parsed == datetime(2026, 8, 25, tzinfo=timezone.utc)
    assert _format_memory_date(parsed) == "25/08/2026"
    assert _format_memory_date("2026-08-25") == "25/08/2026"
    with pytest.raises(ValueError):
        _parse_memory_date("2026-08-25")


def memory(rank=1, content="Maya's dog Pepper died on August 18"):
    return RetrievedMemoryContext(
        memory_id=f"memory-{rank}", revision_id=f"revision-{rank}", excerpt=content,
        memory_type="event_date", confidence="high", sensitivity_safe=True,
        rank=rank, relevance="date/type",
    )


def test_memory_context_requires_confirmation_is_strict_and_bounded():
    with pytest.raises(ValidationError):
        build_snapshot(turns(), snapshot_id=1, generation=1, retrieved_memories=[memory()])
    with pytest.raises(ValidationError, match="cloud-eligible"):
        build_snapshot(
            turns(), snapshot_id=1, generation=1, contact_id="contact-maya",
            retrieved_memories=[memory().model_copy(update={"sensitivity_safe": False})],
        )

    snapshot = build_snapshot(
        turns(), snapshot_id=1, generation=1, contact_id="contact-maya",
        retrieved_memories=[memory(index, f"memory excerpt {index}") for index in range(1, 7)],
    )
    assert len(snapshot.memories) == 4
    prepared = prepare_interpretation_request(snapshot)
    payload = json.loads(prepared.input_text)
    assert len(payload["m"]) <= 4
    assert prepared.estimated_input_tokens <= 2_200
    assert all(len(item[1]) <= 180 for item in payload["m"])


def test_memory_free_payload_and_ceiling_remain_unchanged():
    prepared = prepare_interpretation_request(build_snapshot(turns(), snapshot_id=1, generation=1))
    assert "m" not in json.loads(prepared.input_text)
    assert prepared.estimated_input_tokens <= 1_650


def test_seven_hundred_token_memory_budget_keeps_four_maximum_length_excerpts():
    reference_turns = turns()
    reference_turns[-1] = reference_turns[-1].model_copy(
        update={
            "content": reference_turns[-1].content
            + " We are still talking carefully about what happened and how it affects everyday life."
            * 3
            + " Today this remains important."
        }
    )
    snapshot = build_snapshot(
        reference_turns,
        snapshot_id=1,
        generation=1,
        contact_id="contact-maya",
        retrieved_memories=[
            memory(index, (f"Memory {index} " + "descriptive context " * 20)[:180])
            for index in range(1, 5)
        ],
    )
    prepared = prepare_interpretation_request(snapshot)

    assert prepared.memory_count == 4
    assert len(json.loads(prepared.input_text)["m"]) == 4
    assert prepared.estimated_input_tokens > 1_900
    assert prepared.estimated_input_tokens <= 2_200


def test_memory_metadata_over_seven_hundred_tokens_drops_lowest_ranked_rows():
    oversized = [
        memory(index, (f"Memory {index} " + "descriptive context " * 20)[:180]).model_copy(
            update={
                "revision_id": f"revision-{index}-" + "r" * 260,
                "relevance": "relevance " * 28,
            }
        )
        for index in range(1, 5)
    ]
    prepared = prepare_interpretation_request(build_snapshot(
        turns(), snapshot_id=1, generation=1, contact_id="contact-maya",
        retrieved_memories=oversized,
    ))
    payload = json.loads(prepared.input_text)

    assert prepared.memory_count == 1
    assert [row[0] for row in payload["m"]] == [item.revision_id for item in oversized[:prepared.memory_count]]
    assert prepared.estimated_input_tokens <= 2_200


def test_hard_ceiling_evicts_lowest_ranked_memory_and_updates_request_metadata():
    started = datetime(2026, 8, 25, 12, tzinfo=timezone.utc)
    long_turns = [
        ConversationTurn(
            speaker_name="Maya" if index == 1 else "You",
            speaker_role=(
                SpeakerRole.SELECTED_CONTACT if index == 1 else SpeakerRole.USER
            ),
            source="fixture",
            content="word " * 110,
            timestamp=started + timedelta(seconds=index),
            display_order=index,
        )
        for index in range(1, 3)
    ]
    memories = [
        memory(index).model_copy(update={
            "revision_id": f"revision-{index}-" + "r" * 164,
            "excerpt": ("memory " * 30)[:180],
            "relevance": ("reason " * 45)[:164],
        })
        for index in range(1, 5)
    ]
    prepared = prepare_interpretation_request(build_snapshot(
        long_turns,
        snapshot_id=1,
        generation=1,
        contact_id="contact-maya",
        retrieved_memories=memories,
    ))
    payload = json.loads(prepared.input_text)

    assert prepared.memory_count == len(payload["m"]) == 1
    assert payload["m"][0][0] == memories[0].revision_id
    assert {value.value for value in prepared.modalities} == {"language", "memory"}
    assert "approved memories" in prepared.instructions
    assert prepared.estimated_input_tokens <= 2_200


def test_four_model_memories_show_only_three_visible_possibilities():
    contexts = [memory(index, f"remembered detail {index}") for index in range(1, 5)]
    bodies = (
        format_interpretation_body(None, "No interpretation", contexts),
        format_interpretation_body(
            InterpretationUpdate(
                status="insufficient_evidence",
                explanation="No supported interpretation",
            ),
            "No interpretation",
            contexts,
        ),
    )

    assert all(body.count("The recent words may refer to:") == 3 for body in bodies)
    assert all(contexts[3].excerpt not in body for body in bodies)


def test_contact_change_relabels_only_contact_turns():
    conversation = turns()
    _relabel_contact_turns(conversation, "Yaheli")

    assert [turn.speaker_name for turn in conversation] == ["You", "Yaheli"]


def test_retrieval_query_removes_only_explicit_direct_addresses_and_not_common_word_names():
    conversation = turns()
    conversation[0].content = "Hey Maya, how are you after the event?"
    query, _date_query = _memory_retrieval_inputs(conversation)
    assert "Maya" not in query and "event" in query

    conversation[1].speaker_name = "Will"
    conversation[0].content = "Will you mark the date?"
    query, _date_query = _memory_retrieval_inputs(conversation)
    assert query.startswith("Will you mark the date?")


def test_statement_form_when_is_not_a_temporal_memory_request():
    conversation = turns()
    conversation[0].content = "One more thing. When I go quiet, I am usually thinking."
    conversation[1].content = "Thanks for telling me."
    _query, date_query = _memory_retrieval_inputs(conversation)
    assert date_query == ""


def test_long_snapshot_trims_to_the_ceiling_matching_the_payload():
    started = datetime(2026, 8, 25, 12, tzinfo=timezone.utc)
    long_turns = [
        ConversationTurn(
            speaker_name="Maya" if index == 1 else "You",
            speaker_role=(
                SpeakerRole.SELECTED_CONTACT if index == 1 else SpeakerRole.USER
            ),
            source="fixture",
            content="This is a bounded transcript sentence with ordinary context. " + str(index),
            timestamp=started + timedelta(seconds=index), display_order=index,
        )
        for index in range(1, 17)
    ]
    prepared = prepare_interpretation_request(build_snapshot(
        long_turns, snapshot_id=1, generation=1, contact_id="contact-maya",
        retrieved_memories=[memory()],
    ))
    payload = json.loads(prepared.input_text)
    ceiling = 2_200 if payload.get("m") else 1_650
    assert prepared.estimated_input_tokens <= ceiling
    assert len(payload["t"]) >= 2


def test_memory_displaces_optional_visual_rows_before_it_is_trimmed():
    started = datetime(2026, 8, 25, 12, tzinfo=timezone.utc)
    visual = [
        VisualBucket(
            started_at=started + timedelta(seconds=index),
            ended_at=started + timedelta(seconds=index + 1),
            availability=1, reliability=1, face_movement=0.123,
            smile_movement=0.123, brow_movement=0.123,
            eye_movement=0.123, mouth_movement=0.123,
        )
        for index in range(45)
    ]
    snapshot = build_snapshot(
        turns(), snapshot_id=1, generation=1, contact_id="contact-maya",
        visual_buckets=visual, retrieved_memories=[memory()],
    )
    prepared = prepare_interpretation_request(snapshot)
    payload = json.loads(prepared.input_text)

    assert prepared.memory_count == 1 and len(payload["m"]) == 1
    assert len(payload["v"]) < len(snapshot.visual_buckets)


def test_separate_memory_allowance_trims_old_transcript_before_relevant_memory():
    started = datetime(2026, 8, 25, 12, tzinfo=timezone.utc)
    long_turns = [
        ConversationTurn(
            speaker_name="Maya", speaker_role=SpeakerRole.SELECTED_CONTACT, source="fixture",
            content=("ordinary context words " * 10) + str(index),
            timestamp=started + timedelta(seconds=index), display_order=index,
        )
        for index in range(1, 17)
    ]
    snapshot = build_snapshot(
        long_turns, snapshot_id=1, generation=1, contact_id="contact-maya",
        retrieved_memories=[memory(content="memory " * 25)],
    )
    memory_prepared = prepare_interpretation_request(snapshot)
    memory_free_prepared = prepare_interpretation_request(
        snapshot.model_copy(update={"memories": []})
    )
    assert memory_prepared.estimated_input_tokens <= 2_200
    assert memory_free_prepared.estimated_input_tokens <= 1_500
    assert {value.value for value in memory_prepared.modalities} == {"language", "memory"}
    assert len(json.loads(memory_prepared.input_text)["t"]) == len(
        json.loads(memory_free_prepared.input_text)["t"]
    )
    calls = []
    usage = SimpleNamespace(
        input_tokens=500, output_tokens=20,
        input_tokens_details=SimpleNamespace(cached_tokens=0, cache_write_tokens=0),
        output_tokens_details=SimpleNamespace(reasoning_tokens=0),
    )
    parsed = InterpretationUpdate(
        status="insufficient_evidence", explanation="The recent words do not support a conclusion"
    )
    client = SimpleNamespace(responses=SimpleNamespace(
        parse=lambda **kwargs: (calls.append(kwargs), SimpleNamespace(output_parsed=parsed, usage=usage))[1]
    ))

    OpenAIInterpreter(client=client, ledger=UsageLedger(BudgetLimits()))(snapshot)

    payload = json.loads(calls[0]["input"])
    assert len(payload["t"]) < len(snapshot.turns)
    assert any(row[0] == "c" for row in payload["t"])
    assert len(payload["m"]) == 1
    assert "approved memories" in calls[0]["instructions"]


def test_memory_aware_path_reaches_model_and_cannot_create_unsupported_high_confidence():
    parsed = InterpretationUpdate(
        status="updated",
        social_cues=[
            SocialCue(
                kind="uncertainty", confidence="high",
                hypothesis="The remote participant may be uncertain",
                evidence=Evidence(explanation="The indirect words fit approved context", modalities=[EvidenceModality.MEMORY]),
            )
        ],
    )
    usage = SimpleNamespace(
        input_tokens=500, output_tokens=30,
        input_tokens_details=SimpleNamespace(cached_tokens=0, cache_write_tokens=0),
        output_tokens_details=SimpleNamespace(reasoning_tokens=0),
    )
    calls = []
    client = SimpleNamespace(
        responses=SimpleNamespace(
            parse=lambda **kwargs: (calls.append(kwargs), SimpleNamespace(output_parsed=parsed, usage=usage))[1]
        )
    )
    snapshot = build_snapshot(
        turns(), snapshot_id=1, generation=1, contact_id="contact-maya", retrieved_memories=[memory()]
    )
    result = OpenAIInterpreter(client=client, ledger=UsageLedger(BudgetLimits()))(snapshot)
    assert len(calls) == 1
    assert calls[0]["store"] is False and "approved memories" in calls[0]["instructions"]
    assert "include memory plus the present conversation modality" in calls[0]["instructions"]
    assert result.social_cues[0].confidence.value == "medium"


def test_contact_generation_reset_discards_old_memory_derived_result():
    pending = []

    def interpreter(snapshot):
        pending.append(snapshot)
        return InterpretationUpdate(
            status="insufficient_evidence", explanation="Several memories remain plausible"
        )

    coordinator = InterpretationCoordinator(interpreter, generation=1, minimum_interval_seconds=0)
    old = build_snapshot(
        turns(), snapshot_id=1, generation=1, contact_id="wrong", retrieved_memories=[memory()]
    )
    assert coordinator.offer(old, 0)
    coordinator.reset(2)
    # Whether the worker completes before or after reset, it cannot be accepted under generation 2.
    for event in coordinator.poll(1):
        assert event.kind.value == "stale"
    new = build_snapshot(turns(), snapshot_id=1, generation=2, contact_id="correct", retrieved_memories=[])
    assert coordinator.offer(new, 2)
