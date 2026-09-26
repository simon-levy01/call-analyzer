"""Offline regressions for long-call guidance; synthetic evidence only."""
from datetime import timedelta
import json
import pytest
from conversation_copilot import interpretation

from conversation_copilot import guidance
from conversation_copilot.f04_evaluation import EvaluationScenario
from conversation_copilot.interpretation import UsageLedger, build_snapshot
from conversation_copilot.interpretation import RetrievedMemoryContext, estimate_english_tokens, REQUEST_PROTOCOL_OVERHEAD_TOKENS


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
    display.tick(179)
    assert display.visible('replies')
    display.tick(180)
    assert not display.visible('replies')
    display.offer(update.model_copy(update={'snapshot_id':2}), 50)
    display.on_speech(said)
    assert not display.visible('replies')


def test_long_context_preserves_both_sensors_with_shared_budget(monkeypatch):
    base = EvaluationScenario('sensor-budget','live','What next?','The project needs discussion.').snapshot('all')
    turns = [base.turns[-1].model_copy(update={'display_order':i+1,
             'timestamp':base.created_at+timedelta(seconds=i*2), 'content':'Project planning details matter. '*6}) for i in range(30)]
    vocal = [base.vocal_observations[0].model_copy(update={'turn_display_order':i+1}) for i in range(30)]
    visual = [base.visual_buckets[0].model_copy(update={'started_at':turns[-1].timestamp-timedelta(seconds=90-i*2),
              'ended_at':turns[-1].timestamp-timedelta(seconds=88-i*2)}) for i in range(45)]
    snapshot = build_snapshot(turns, snapshot_id=1, generation=1, vocal_observations=vocal, visual_buckets=visual,
                              created_at=turns[-1].timestamp+timedelta(seconds=1))
    def fake(schema, payload, instructions, **kwargs):
        assert kwargs['input_limit'] == 6000
        assert payload['x'] and payload['v']
        assert payload['turn_ids'] == [t.display_order for t in snapshot.turns]
        return guidance.GuidanceOutput.model_validate({'interpretation':{'status':'insufficient_evidence'}}), None
    monkeypatch.setattr(guidance,'f06_structured_request',fake)
    result = guidance.interpret_guidance(snapshot,ledger=UsageLedger())
    assert not result.replies  # No supported suggestion is not advice to wait.


def test_shared_ceiling_trims_low_rank_memory_with_both_sensors(monkeypatch):
    base=EvaluationScenario('mixed-budget','live','What next?','The project needs discussion.').snapshot('all')
    memories=[RetrievedMemoryContext(memory_id=f'm{i}',revision_id=f'r{i}',excerpt='Project appointment detail. '*6,
        memory_type='event_date',confidence='medium',sensitivity_safe=True,rank=i+1,relevance='lexical') for i in range(4)]
    snapshot=base.model_copy(update={'memories':memories,'contact_id':'synthetic-budget',
        'vocal_observations':base.vocal_observations*6,'visual_buckets':base.visual_buckets*6})
    captured=[]
    def fake(schema,payload,instructions,**kwargs):
        total=sum(estimate_english_tokens(s) for s in (instructions,json.dumps(payload,ensure_ascii=False,separators=(',',':')),
            json.dumps(schema.model_json_schema(),separators=(',',':'))))+REQUEST_PROTOCOL_OVERHEAD_TOKENS
        assert total<=kwargs['input_limit']==6000
        assert payload['turn_ids']==[t.display_order for t in snapshot.turns]
        assert [row[2] for row in payload['t']]==[t.content for t in snapshot.turns]
        assert [m[0] for m in payload.get('m',[])]==[m.revision_id for m in memories[:len(payload.get('m',[]))]]
        captured.append((payload,instructions))
        return guidance.GuidanceOutput.model_validate({'interpretation':{'status':'insufficient_evidence'}}),None
    monkeypatch.setattr(guidance,'f06_structured_request',fake)
    original=guidance.GUIDANCE_INSTRUCTIONS
    # Vary instruction overhead to exercise the real shared boundary, without inference.
    for extra in range(0,15000,100):
        monkeypatch.setattr(guidance,'GUIDANCE_INSTRUCTIONS',original+' '*extra)
        guidance.interpret_guidance(snapshot,ledger=UsageLedger())
        payload,instructions=captured[-1]
        if 0<len(payload.get('m',[]))<4:
            assert payload['x'] and payload['v']
            # Exercise the real preflight; stop at its evidence gate BEFORE key lookup/dispatch.
            with pytest.raises(interpretation.InterpretationEvidenceChanged):
                interpretation._f06_structured_request(guidance.GuidanceOutput,payload,instructions,
                    ledger=UsageLedger(),input_limit=6000,output_limit=1800,is_current=lambda:False)
            break
    else:raise AssertionError('Did not exercise memory trimming at shared ceiling')
