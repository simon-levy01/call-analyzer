from types import SimpleNamespace

from conversation_copilot.guidance import GuidanceCandidate, GuidanceDisplay


def test_citation_lists_are_independently_bounded_and_require_supplied_memory(monkeypatch):
    import pytest
    from conversation_copilot import guidance
    from conversation_copilot.f04_evaluation import EvaluationScenario
    from conversation_copilot.interpretation import Evidence, RetrievedMemoryContext, UsageLedger

    snapshot = EvaluationScenario("citation-lists", "f06", "What about the trip?", "The dates changed.").snapshot("transcript")
    memories = tuple(RetrievedMemoryContext(memory_id=f"m{i}", revision_id=f"r{i}", excerpt=f"Trip detail {i}",
        memory_type="event_date", confidence="high", sensitivity_safe=True, rank=i, relevance="trip") for i in range(1, 4))
    snapshot = snapshot.model_copy(update={"contact_id": "contact", "memories": memories,
        "turns": (*snapshot.turns, snapshot.turns[-1].model_copy(update={"display_order": 3, "content": "The hotel changed too."}))})
    item = GuidanceCandidate(text="Possibly related: the saved trip details.", confidence="low", turn_ids=[1, 2, 3], memory_ids=["r1", "r2", "r3"])
    output = guidance.GuidanceOutput.model_validate({"interpretation": {"status": "insufficient_evidence", "explanation": "Factual update"}, "remember": [item]})
    monkeypatch.setattr(guidance, "f06_structured_request", lambda *a, **k: (output.model_copy(deep=True), None))
    assert guidance.interpret_guidance(snapshot, ledger=UsageLedger()).remember == [item]
    item.memory_ids = []
    assert not guidance.interpret_guidance(snapshot, ledger=UsageLedger()).remember
    item.memory_ids = ["not-supplied"]
    with pytest.raises(ValueError, match="unavailable evidence"):
        guidance.interpret_guidance(snapshot, ledger=UsageLedger())
    for field in ("turn_ids", "memory_ids"):
        with pytest.raises(ValueError):
            GuidanceCandidate(text="Too many", confidence="low", **{field: list(range(4)) if field == "turn_ids" else ["a", "b", "c", "d"]})
    assert Evidence(explanation="Four supporting turns", modalities=["language"], turn_ids=[1, 2, 3, 4]).turn_ids == [1, 2, 3, 4]
    with pytest.raises(ValueError):
        Evidence(explanation="Too many", modalities=["language"], turn_ids=[1, 2, 3, 4, 5])


def test_empty_updated_wire_abstains_without_losing_valid_reply(monkeypatch):
    from conversation_copilot import guidance
    from conversation_copilot.f04_evaluation import EvaluationScenario
    from conversation_copilot.interpretation import UsageLedger, _canonical_interpretation
    snapshot = EvaluationScenario("empty-updated", "f06", "Here is an option.", "Could you show it closer?").snapshot("transcript")
    output = guidance.GuidanceOutput.model_validate({
        "interpretation": {"status": "updated", "tones": [], "social_cues": [],
            "explanation": "No supported affective tone is established."},
        "replies": [{"text": "Sure, I'll show it closer.", "confidence": "high", "turn_ids": [2]}]})
    # Both standalone interpretation and combined guidance use this canonicalizer.
    for explanation in (None, "No supported affective tone is established."):
        wire = output.interpretation.model_copy(update={"explanation": explanation})
        result = _canonical_interpretation(wire)
        assert result.status == "insufficient_evidence" and not result.tones and not result.social_cues
        assert result.explanation == (explanation or "Recent evidence was insufficient or conflicting")
        assert wire.status == "updated"  # Preserve the original model answer.
    monkeypatch.setattr(guidance, "f06_structured_request", lambda *a, **k: (output, None))
    result = guidance.interpret_guidance(snapshot, ledger=UsageLedger())
    assert result.status == "insufficient_evidence"
    assert [item.text for item in result.replies] == ["Sure, I'll show it closer."]


def test_recent_reply_ideas_keep_analysis_and_filter_memories():
    from conversation_copilot.guidance import reconcile_replies, selected_memory_context, GuidedInterpretation
    original = GuidedInterpretation(snapshot_id=1, generation=1, status="insufficient_evidence", explanation="Limited evidence",
        replies=[GuidanceCandidate(text="Old reply", confidence="medium", turn_ids=[2])])
    original.remember = [GuidanceCandidate(text="Relevant fact", confidence="medium", memory_ids=["r1"])]
    cleaned = reconcile_replies(original, [])
    assert cleaned.status == original.status and cleaned.tones == original.tones
    assert cleaned.replies and not cleaned.follow_up
    assert original.replies
    candidates = [SimpleNamespace(revision_id="r1"), SimpleNamespace(revision_id="irrelevant")]
    assert selected_memory_context(candidates, original) == candidates[:1]


def test_transcript_1300_budget_is_separate_from_guidance_instructions(monkeypatch):
    from datetime import datetime, timedelta, timezone
    from conversation_copilot import guidance
    from conversation_copilot.models import ConversationTurn, SpeakerRole
    from conversation_copilot.interpretation import build_snapshot, UsageLedger
    turns = [ConversationTurn(speaker_name="Contact", speaker_role=SpeakerRole.SELECTED_CONTACT,
        source="test", content="project planning matters " * 4,
        timestamp=datetime(2026, 9, 13, tzinfo=timezone.utc) + timedelta(seconds=i * 4), display_order=i + 1)
        for i in range(30)]
    snapshot = build_snapshot(turns, snapshot_id=30, generation=1)
    assert 1_000 < snapshot.estimated_transcript_tokens <= 1_300
    assert len(snapshot.turns) == 30
    captured = []
    def request(schema, payload, instructions, **kwargs):
        captured.append(payload["turn_ids"])
        return guidance.GuidanceOutput.model_validate({"interpretation": {
            "status": "insufficient_evidence", "explanation": "No affect stated"}}), None
    monkeypatch.setattr(guidance, "f06_structured_request", request)
    guidance.interpret_guidance(snapshot, ledger=UsageLedger())
    monkeypatch.setattr(guidance, "GUIDANCE_INSTRUCTIONS", guidance.GUIDANCE_INSTRUCTIONS + " Extra instruction." * 20)
    guidance.interpret_guidance(snapshot, ledger=UsageLedger())
    assert captured == [list(range(1, 31))] * 2
    # Over-budget transcripts still drop whole oldest segments and keep the latest.
    extended = turns + [turns[-1].model_copy(update={"display_order": 31,
        "timestamp": turns[-1].timestamp + timedelta(seconds=4), "content": "detail " * 100})]
    bounded = build_snapshot(extended, snapshot_id=31, generation=1)
    assert bounded.estimated_transcript_tokens <= 1_300
    assert bounded.turns[0].display_order > 1 and bounded.turns[-1].display_order == 31


def test_direct_tone_rule_does_not_hide_second_model_tone(monkeypatch):
    from conversation_copilot import guidance
    from conversation_copilot.f04_evaluation import EvaluationScenario
    from conversation_copilot.interpretation import UsageLedger
    snapshot = EvaluationScenario("two-tones", "f06", "How do you feel?", "I feel calm and excited.").snapshot("transcript")
    output = guidance.GuidanceOutput.model_validate({"interpretation": {"status": "updated", "tones": [
        {"kind": "neutral_calm", "confidence": "medium", "hypothesis": "They describe feeling calm.",
         "evidence": {"explanation": "They say they feel calm.", "modalities": ["language"], "turn_ids": [2]}}], "social_cues": []}})
    monkeypatch.setattr(guidance, "f06_structured_request", lambda *a, **k: (output, None))
    result = guidance.interpret_guidance(snapshot, ledger=UsageLedger())
    assert {tone.kind.value for tone in result.tones} == {"energetic_high_energy", "neutral_calm"}


def update(number, text="Would you like to tell me more?", turn=1):
    return SimpleNamespace(snapshot_id=number, status='insufficient_evidence', tones=[], social_cues=[],
        replies=[GuidanceCandidate(text=text, confidence="medium", turn_ids=[turn])], remember=[], follow_up=[])


def test_guidance_targets_contact_not_user_and_uses_requested_model(monkeypatch):
    from conversation_copilot import guidance
    from conversation_copilot.f04_evaluation import EvaluationScenario
    from conversation_copilot.interpretation import UsageLedger, SOL_MODEL, _InterpretationWireUpdate
    snapshot = EvaluationScenario("direction", "f06", "What time is your appointment?", "It is at three.").snapshot("transcript")
    def request(schema, payload, instructions, **kwargs):
        assert kwargs["model"] == SOL_MODEL and kwargs["reasoning"] == "low"
        assert "avoid questions" in instructions
        return guidance.GuidanceOutput(interpretation=_InterpretationWireUpdate(status="insufficient_evidence"), replies=[
            GuidanceCandidate(text="My appointment is at three.", confidence="medium", turn_ids=[1]),
            GuidanceCandidate(text="Would a reminder help?", confidence="medium", turn_ids=[2])], follow_up=[
            GuidanceCandidate(text="What time is it?", confidence="medium", turn_ids=[1])]), None
    monkeypatch.setattr(guidance, "f06_structured_request", request)
    result = guidance.interpret_guidance(snapshot, ledger=UsageLedger(), model=SOL_MODEL, reasoning="low")
    assert [c.text for c in result.replies] == ["Would a reminder help?"] and not result.follow_up
    user_last = snapshot.model_copy(update={"turns": [*snapshot.turns, snapshot.turns[0].model_copy(update={"display_order": 3})]})
    result = guidance.interpret_guidance(user_last, ledger=UsageLedger(), model=SOL_MODEL, reasoning="low")
    assert not result.replies and not result.follow_up
    def next_move(schema, payload, instructions, **kwargs):
        assert payload['user_spoke_last'] and payload['reply_to_turn_id']==2 and payload['latest_turn_id']==3
        return guidance.GuidanceOutput(interpretation=_InterpretationWireUpdate(status='insufficient_evidence'), replies=[
            GuidanceCandidate(text='Give them time to answer your question.',confidence='medium',turn_ids=[3])]),None
    monkeypatch.setattr(guidance,'f06_structured_request',next_move)
    assert guidance.interpret_guidance(user_last,ledger=UsageLedger()).replies[0].text == 'Give them time to answer your question.'


def test_topic_reset_and_stale_evidence_are_not_cloud_failure():
    from conversation_copilot.memory import _TOPIC_BOUNDARY
    from conversation_copilot.f04_evaluation import EvaluationScenario
    from conversation_copilot.interpretation import InterpretationCoordinator, CoordinatorEventKind, InterpretationEvidenceChanged
    for text in ("Actually, that reminds me", "No, that was a joke about my cooking", "Instead I walked"):
        assert not _TOPIC_BOUNDARY.search(text)
    assert _TOPIC_BOUNDARY.search("Moving on, let's discuss the book")
    display = GuidanceDisplay()
    display.offer(update(1), 0)
    display.dismiss("replies", 0)
    display.expanded.add("replies")
    display.invalidate(new_topic=True)
    assert not display.dismissed and not display.expanded and display.pending is None
    assert all(not display.visible(category) for category in ("replies", "remember", "follow_up"))
    snapshot = EvaluationScenario("topic", "f06", "What now?", "Moving on").snapshot("transcript")
    coordinator = InterpretationCoordinator(lambda item: None, generation=snapshot.generation)
    coordinator._results.put((snapshot, None, InterpretationEvidenceChanged("topic changed")))
    assert coordinator.poll(0)[0].kind == CoordinatorEventKind.STALE


def test_guidance_stability_dismissal_expiry_and_hidden_candidates():
    display = GuidanceDisplay()
    display.offer(update(1), 0)
    original = display.visible("replies")[0].candidate.text
    display.offer(update(2, "Could you clarify?", 2), 3)
    assert display.visible("replies")[0].candidate.text == "Could you clarify?"
    display.tick(11.99)
    assert display.visible("replies")[0].candidate.text == "Could you clarify?"
    display.tick(12)
    assert display.visible("replies")[0].candidate.text == "Could you clarify?"
    display.dismiss("replies", 0)
    display.offer(update(3, "Would you explain that?", 2), 13)
    assert all(item.candidate.text != "Could you clarify?" for item in display.visible("replies"))
    display.offer(update(4, "A fresh question?", 3), 14, manual=True)
    assert display.visible("replies")
    display.tick(62)
    assert not display.visible("replies")
    many = update(5)
    many.replies *= 4
    display.offer(many, 64)
    assert len(display.visible("replies")) == 1  # Exact duplicates do not fill spare slots.
    display.invalidate(turn_ids=set())
    assert not display.visible("replies")


def test_suggest_now_replaces_stable_candidates_as_soon_as_it_returns():
    display = GuidanceDisplay()
    display.offer(update(1), 0)
    fresh = update(2, "Shall we confirm the date?", 2)
    fresh.manual = True
    display.offer(fresh, 2)
    assert display.visible("replies")[0].candidate.text == fresh.replies[0].text


def test_repeated_manual_requests_coalesce_and_more_does_not_dispatch():
    import threading
    import time
    from conversation_copilot.f04_evaluation import EvaluationScenario
    from conversation_copilot.guidance import GuidedInterpretation
    from conversation_copilot.interpretation import InterpretationCoordinator
    snapshot = EvaluationScenario("coalesce", "f06", "What now?", "Could we confirm?").snapshot("transcript")
    calls, released = [], threading.Event()
    def interpret(item):
        calls.append(item.snapshot_id)
        assert released.wait(2)
        return GuidedInterpretation(status="insufficient_evidence", explanation="Limited evidence.",
            snapshot_id=item.snapshot_id, generation=item.generation, manual=True)
    coordinator = InterpretationCoordinator(interpret, generation=snapshot.generation)
    for number in (1, 2, 3):
        coordinator.offer(snapshot.model_copy(update={"snapshot_id": number, "manual": True}), number, manual=True)
    released.set()
    deadline = time.perf_counter() + 2
    while time.perf_counter() < deadline:
        coordinator.poll(10)
        if calls == [1, 3] and not coordinator.snapshot().in_flight:
            break
        time.sleep(.005)
    assert calls == [1, 3]
    display = GuidanceDisplay()
    prepared = update(4)
    prepared.replies *= 3
    display.offer(prepared, 11)
    display.expanded.add("replies")
    assert len(display.visible("replies")) == 1 and calls == [1, 3]


def test_manual_duplicate_reaches_display_and_renews_explicitly():
    from conversation_copilot.guidance import GuidedInterpretation
    from conversation_copilot.f04_evaluation import EvaluationScenario
    from conversation_copilot.interpretation import InterpretationCoordinator, CoordinatorEventKind
    snapshot = EvaluationScenario("manual", "f06", "What now?", "Could we confirm the plan?").snapshot("transcript")
    result = GuidedInterpretation(status="insufficient_evidence", explanation="Limited evidence.", snapshot_id=1,
        generation=snapshot.generation, replies=[GuidanceCandidate(text="Could we confirm the date?",confidence="medium",turn_ids=[2])])
    coordinator = InterpretationCoordinator(lambda item: result, generation=snapshot.generation)
    coordinator._results.put((snapshot, result, None))
    assert coordinator.poll(0)[0].kind == CoordinatorEventKind.ACCEPTED
    manual = result.model_copy(update={"snapshot_id": 2, "manual": True})
    coordinator._results.put((snapshot.model_copy(update={"snapshot_id":2,"manual":True}),manual,None))
    assert coordinator.poll(2)[0].kind == CoordinatorEventKind.ACCEPTED
    display = GuidanceDisplay()
    display.offer(result, 0)
    display.offer(manual, 2)
    assert display.visible("replies")[0].supported_at == 2
    assert display.visible("replies")[0].shown_at == 2


def test_old_manual_guidance_cannot_replace_newer_result():
    display = GuidanceDisplay()
    display.offer(update(5), 0, manual=True)
    display.offer(update(4, text="Stale suggestion"), 1, manual=True)
    assert display.last_snapshot == 5
    assert all(item.candidate.text != "Stale suggestion" for item in display.visible("replies"))


def test_reply_dedup_does_not_join_separate_user_turns(monkeypatch):
    from conversation_copilot import guidance
    from conversation_copilot.f04_evaluation import EvaluationScenario
    from conversation_copilot.interpretation import UsageLedger
    snapshot = EvaluationScenario("separate", "f06", "We could try", "Okay.").snapshot("transcript")
    first = snapshot.turns[0]
    snapshot = snapshot.model_copy(update={"turns": (first,
        first.model_copy(update={"content": "another time", "display_order": 2}),
        snapshot.turns[1].model_copy(update={"display_order": 3}))})
    output = guidance.GuidanceOutput.model_validate({"interpretation": {"status": "insufficient_evidence", "explanation": "Brief acknowledgment"},
        "replies": [{"text": "Try another time?", "confidence": "medium", "turn_ids": [3]}]})
    monkeypatch.setattr(guidance, "f06_structured_request", lambda *a, **k: (output, None))
    result = guidance.interpret_guidance(snapshot, ledger=UsageLedger())
    assert result.replies[0].text == "Try another time?"
