"""Offline regressions for long-call guidance; synthetic evidence only."""
from datetime import timedelta

from conversation_copilot import guidance
from conversation_copilot.f04_evaluation import EvaluationScenario
from conversation_copilot.interpretation import UsageLedger, build_snapshot


def test_recent_reply_ideas_survive_speech_but_not_changed_topic_or_expiry():
    snapshot = EvaluationScenario('continuation', 'live', 'Tell me about the project.',
                                  'We still need a launch date.').snapshot('transcript')
    update = guidance.GuidedInterpretation(status='insufficient_evidence', explanation='Limited evidence.', snapshot_id=1, generation=1,
        analyzed_order=2, context_at=snapshot.created_at,
        replies=[guidance.GuidanceCandidate(text='What date would be realistic?', confidence='medium', turn_ids=[2])])
    later = snapshot.turns[-1].model_copy(update={'display_order':3, 'content':'The budget is limited.',
                                                'timestamp':snapshot.created_at+timedelta(seconds=1)})
    now = snapshot.created_at+timedelta(seconds=3)
    assert guidance.reconcile_replies(update, [later], now).replies
    # Explicit resets and corrections still invalidate the old question.
    for text in ('Moving on, what about dinner?', 'Correction, the date is already set.', "I don't want to talk about it."):
        assert not guidance.reconcile_replies(update, [later.model_copy(update={'content':text})], now).replies
    assert not guidance.reconcile_replies(update, [later], snapshot.created_at+timedelta(seconds=24)).replies
    said = snapshot.turns[0].model_copy(update={'display_order':3, 'content':'What date would be realistic?'})
    assert not guidance.reconcile_replies(update, [said], now).replies
    assert update.replies  # Never mutate the saved model response.

    display = guidance.GuidanceDisplay()
    display.offer(update, 10, source_age=10)
    display.on_speech(later)
    assert display.visible('replies')
    display.tick(23.9)
    assert display.visible('replies')
    display.tick(24)
    assert not display.visible('replies')
    display.offer(update.model_copy(update={'snapshot_id':2}), 30)
    display.on_speech(said)
    assert not display.visible('replies')


def test_long_context_preserves_both_sensors_without_spending_more(monkeypatch):
    base = EvaluationScenario('sensor-budget','live','What next?','The project needs discussion.').snapshot('all')
    turns = [base.turns[-1].model_copy(update={'display_order':i+1,
             'timestamp':base.created_at+timedelta(seconds=i*2), 'content':'Project planning details matter. '*6}) for i in range(30)]
    vocal = [base.vocal_observations[0].model_copy(update={'turn_display_order':i+1}) for i in range(30)]
    visual = [base.visual_buckets[0].model_copy(update={'started_at':turns[-1].timestamp-timedelta(seconds=90-i*2),
              'ended_at':turns[-1].timestamp-timedelta(seconds=88-i*2)}) for i in range(45)]
    snapshot = build_snapshot(turns, snapshot_id=1, generation=1, vocal_observations=vocal, visual_buckets=visual,
                              created_at=turns[-1].timestamp+timedelta(seconds=1))
    def fake(schema, payload, instructions, **kwargs):
        assert kwargs['input_limit'] == 4500
        assert payload['x'] and payload['v']
        assert payload['turn_ids'] == [t.display_order for t in snapshot.turns]
        return guidance.GuidanceOutput.model_validate({'interpretation':{'status':'insufficient_evidence'}}), None
    monkeypatch.setattr(guidance,'f06_structured_request',fake)
    result = guidance.interpret_guidance(snapshot,ledger=UsageLedger())
    assert not result.replies  # No supported suggestion is not advice to wait.
