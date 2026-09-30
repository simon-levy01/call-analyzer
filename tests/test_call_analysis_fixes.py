"""Synthetic regressions derived from three private calls; no model inference."""
import json
from datetime import timedelta
from types import SimpleNamespace

import pytest

from conversation_copilot import guidance, post_call
from conversation_copilot.f04_evaluation import EvaluationScenario
from conversation_copilot.interpretation import (
    UsageLedger, _ground_interpretation, InterpretationUpdate, Evidence,
    ToneHypothesis, prepare_interpretation_request, _cautious_policy,
)
from conversation_copilot.memory import MemoryStore, FakeMemoryExtractor, ExtractionOutput, SummaryOutput, SummaryStatementInput
from conversation_copilot.models import ConversationTurn


def snapshot():
    return EvaluationScenario('grounding', 'regression', 'Show me the jacket.', 'Which jacket?').snapshot('all')


@pytest.mark.parametrize('text,accepted', [
    ("Sure—I'll show you the first option.", True),
    ("I'll show it closer.", True),
    ("I'm sorry for your loss.", True),
    ("I'm doing okay, just a little tired.", False),
    ("I might have green.", False),
    ("I don't think I have green.", False),
    ("I'll attend on Friday.", False),
    ("I won't bring it up.", False),
    ("I'll show up Friday at four.", False),
    ("I have a question about the jacket.", True),
])
def test_optional_actions_and_unsupported_personal_claims(monkeypatch, text, accepted):
    output = guidance.GuidanceOutput.model_validate({'interpretation': {'status':'insufficient_evidence'},
        'replies':[{'text':text, 'confidence':'medium', 'turn_ids':[2]}]})
    monkeypatch.setattr(guidance, 'f06_structured_request', lambda *a, **k: (output, None))
    assert bool(guidance.interpret_guidance(snapshot(), ledger=UsageLedger()).replies) == accepted


def test_user_question_is_not_answered_by_the_copilot(monkeypatch):
    case = snapshot()
    case = case.model_copy(update={'turns':[*case.turns, case.turns[0].model_copy(update={
        'display_order':3, 'content':'How long has this call been going?'})]})
    output = guidance.GuidanceOutput.model_validate({'interpretation': {'status':'insufficient_evidence'},
        'replies':[{'text':'About three minutes so far.', 'confidence':'high', 'turn_ids':[3]}]})
    def fake(schema, payload, instructions, **kwargs):
        assert all(row[0] in ('u','c') for row in payload['t'])
        assert 'rolling context window' in instructions
        return output, None
    monkeypatch.setattr(guidance, 'f06_structured_request', fake)
    assert not guidance.interpret_guidance(case, ledger=UsageLedger()).replies


def test_personal_claim_needs_cited_user_evidence_and_every_claim_is_checked(monkeypatch):
    case=snapshot()
    case=case.model_copy(update={'turns':[case.turns[0].model_copy(update={'content':"I'm tired."}),case.turns[1]]})
    def run(text,ids):
        output=guidance.GuidanceOutput.model_validate({'interpretation':{'status':'insufficient_evidence'},
            'replies':[{'text':text,'confidence':'medium','turn_ids':ids}]})
        monkeypatch.setattr(guidance,'f06_structured_request',lambda *a,**k:(output,None))
        return guidance.interpret_guidance(case,ledger=UsageLedger()).replies
    assert run("I'm tired. Could we take a break?",[1,2])
    assert not run("I'm tired. Could we take a break?",[2])
    assert not run("I'm tired. I'm free on Friday.",[1,2])


@pytest.mark.parametrize('source,claim', [
    ("I don't think I have the green one.","I have the green one."),
    ("Did you say I'll be there?","I'll be there."),
    ("I wouldn't say I'm excited.","I'm excited."),
    ('She said, "I am excited."','I am excited.'),
    ("I'm tired?","I'm tired."),
])
def test_negated_quoted_or_questioned_user_words_do_not_license_claim(monkeypatch,source,claim):
    case=snapshot()
    case=case.model_copy(update={'turns':[case.turns[0].model_copy(update={'content':source}),case.turns[1]]})
    output=guidance.GuidanceOutput.model_validate({'interpretation':{'status':'insufficient_evidence'},
        'replies':[{'text':claim+' Could we discuss the jacket?', 'confidence':'medium','turn_ids':[1,2]}]})
    monkeypatch.setattr(guidance,'f06_structured_request',lambda *a,**k:(output,None))
    assert not guidance.interpret_guidance(case,ledger=UsageLedger()).replies


@pytest.mark.parametrize('reply,continuation',[
    ('Could you say more about the jacket?','The jacket I mean is the blue one—'),
    ('Do you want me to show the timeline now?','The timeline slipped again, which is why—'),
    ('Should we change the project deadline?','The project has a small budget.'),
])
def test_related_continuation_is_not_an_answer(reply,continuation):
    candidate=guidance.GuidanceCandidate(text=reply,confidence='medium',turn_ids=[2])
    later=snapshot().turns[-1].model_copy(update={'display_order':3,'content':continuation})
    assert not guidance.reply_superseded(candidate,later)


def test_current_nonverbal_observation_does_not_require_current_contact_speech():
    case=snapshot()
    case=case.model_copy(update={'created_at':case.created_at+timedelta(seconds=40),
        'visual_buckets':[case.visual_buckets[-1].model_copy(update={'ended_at':case.created_at+timedelta(seconds=39)})]})
    update=InterpretationUpdate(status='updated',tones=[ToneHypothesis(kind='positive_warm',confidence='low',
        hypothesis='Possible warmth.',evidence=Evidence(explanation='Recent observed configuration.',modalities=['visual']))])
    assert _ground_interpretation(update,case,[1,2]).tones
    case=case.model_copy(update={'created_at':case.created_at+timedelta(seconds=30)})
    assert not _ground_interpretation(update,case,[1,2]).tones


def test_supportive_replies_are_not_filtered_as_personal_states(monkeypatch):
    output=guidance.GuidanceOutput.model_validate({'interpretation':{'status':'insufficient_evidence'},
        'replies':[{'text':"I'm here to listen.",'confidence':'medium','turn_ids':[2]},
                   {'text':"I'm with you—go ahead.",'confidence':'medium','turn_ids':[2]}]})
    monkeypatch.setattr(guidance,'f06_structured_request',lambda *a,**k:(output,None))
    assert len(guidance.interpret_guidance(snapshot(),ledger=UsageLedger()).replies)==2


@pytest.mark.parametrize('ids,age,kind,text,accepted', [
    ([2],0,'positive_warm','Thank you for helping.',True),
    ([1],0,'positive_warm','Thank you for helping.',False),
    ([99],0,'positive_warm','Thank you for helping.',False),
    ([],0,'positive_warm','Thank you for helping.',False),
    ([2],25,'positive_warm','Thank you for helping.',False),
    ([2],0,'neutral_calm','Friday night.',False),
    ([2],0,'neutral_calm','I feel calm.',True),
    ([2],0,'positive_warm','Cool cool cool.',False),
])
def test_cues_need_fresh_contact_sources(ids, age, kind, text, accepted):
    case=snapshot()
    case=case.model_copy(update={'turns':[case.turns[0],case.turns[1].model_copy(update={'content':text})],
        'created_at':case.turns[-1].timestamp+timedelta(seconds=age)})
    result=_ground_interpretation(InterpretationUpdate(status='updated', tones=[ToneHypothesis(
        kind=kind, confidence='medium', hypothesis='Possible tone.',
        evidence=Evidence(explanation='Source wording.',modalities=['language'],turn_ids=ids))]),case,[1,2])
    assert bool(result.tones) == accepted


def test_old_sarcasm_does_not_override_new_topic():
    case=snapshot()
    case=case.model_copy(update={'turns':[case.turns[1].model_copy(update={'display_order':1,'content':'Oh great, exactly what I needed.'}),
        case.turns[1].model_copy(update={'display_order':2,'content':'Moving on, the meeting is Friday.'})]})
    assert _cautious_policy(case) is None


def test_contact_answers_filter_late_reply_but_keep_displayed_reply():
    case=snapshot()
    candidate=guidance.GuidanceCandidate(text='About three minutes so far.', confidence='high',turn_ids=[2])
    update=guidance.GuidedInterpretation(status='insufficient_evidence',explanation='No cue.',snapshot_id=1,generation=1,
        analyzed_order=2,context_at=case.created_at,replies=[candidate])
    later=case.turns[-1].model_copy(update={'display_order':3,'content':'Eleven minutes, almost twelve.'})
    assert not guidance.reconcile_replies(update,[later],case.created_at).replies
    display=guidance.GuidanceDisplay()
    display.offer(update,0)
    display.offer(guidance.reconcile_replies(update,[later],case.created_at).model_copy(update={'snapshot_id':2}),1)
    assert display.visible('replies') and not display.pending
    assert update.replies  # Saved accepted output is immutable to display filtering.
    assert guidance.reply_superseded(candidate,later.model_copy(update={'content':'fifteen minutes almost sixteen'}))
    assert not guidance.reply_superseded(guidance.GuidanceCandidate(text='Ten minutes should be enough.',confidence='medium',turn_ids=[2]),
        later.model_copy(update={'content':"I'll be there in five minutes"}))


def test_summary_consolidation_has_sources_and_cannot_raise_confidence(tmp_path, monkeypatch):
    monkeypatch.setattr(post_call,'_whole_summary_fits',lambda turns:False)
    with MemoryStore(tmp_path/'test.sqlite3') as store:
        contact=store.create_contact('Alex')
        turns=[ConversationTurn(speaker_name='Alex',speaker_role='selected_contact',source='fixture',
            content=f'Maybe project {i} will work.',display_order=i,timestamp=snapshot().created_at) for i in range(1,22)]
        record=store.create_record(source_kind='call',source_label='synthetic',timezone_name='UTC',contact_id=contact.id,status='stopped',turns=turns)
        calls=[]
        def fake(schema,payload,instructions,**kwargs):
            calls.append(payload)
            if 'draft_statements' in payload:
                assert payload['draft_statements'][0]['confidence']=='medium'
                assert {r['id'] for r in payload['source']['turns']} >= {1,2,20,21}
                confidence='high'
                ids=[1,21]
            else:
                confidence='medium'
                ids=[payload['turns'][0]['id']]
            return SummaryOutput(statements=[SummaryStatementInput(section='discussed',content='Alex discussed possible projects.',
                kind='fact',confidence=confidence,evidence_turns=ids)]),None
        monkeypatch.setattr(post_call,'f06_structured_request',fake)
        summary=post_call.process_review(store,record,ledger=UsageLedger(),extractor=FakeMemoryExtractor([ExtractionOutput()]))
        assert len(calls)==3
        assert store.summary_statements(summary)[0]['confidence']=='medium'
        assert store.integrity_ok()


def test_summary_compaction_keeps_speaker_changes_and_recording_dates():
    case=snapshot()
    turns=[ConversationTurn(**t.model_dump(),speaker_name='Alex' if t.speaker_role.value=='selected_contact' else 'You',source='fixture') for t in case.turns]
    turns.append(turns[-1].model_copy(update={'display_order':3,'speaker_name':'Renamed','timestamp':turns[-1].timestamp+timedelta(days=1)}))
    payload=post_call._summary_payload(turns)
    assert payload['speaker_names']=={'user':'You','selected_contact':'Alex'}
    assert payload['turns'][-1]['speaker_name']=='Renamed'
    assert len(payload['recording_dates'])==2
    assert payload['recording_dates'][0][1]==turns[0].timestamp.isoformat()
    assert [row['text'] for row in payload['turns']]==[turn.content for turn in turns]


@pytest.mark.parametrize('verbose', [False, True])
def test_oversized_merge_finishes_with_bounded_draft_consolidation(tmp_path,monkeypatch,verbose):
    monkeypatch.setattr(post_call,'_whole_summary_fits',lambda turns:False)
    with MemoryStore(tmp_path/'large.sqlite3') as store:
        contact=store.create_contact('Alex')
        turns=[ConversationTurn(speaker_name='Alex',speaker_role='selected_contact',source='fixture',
            content='A detailed fictional project discussion. '*60,display_order=i,timestamp=snapshot().created_at) for i in range(1,42)]
        record=store.create_record(source_kind='call',source_label='synthetic large',timezone_name='UTC',contact_id=contact.id,status='stopped',turns=turns)
        drafts=[]
        def fake(schema,payload,instructions,**kwargs):
            if 'draft_statements' in payload:
                from conversation_copilot.interpretation import estimate_english_tokens, REQUEST_PROTOCOL_OVERHEAD_TOKENS
                assert payload.get('source',{}).get('turns') or payload.get('source_mode')=='previously_source_cited_drafts'
                assert sum(estimate_english_tokens(value) for value in (json.dumps(payload,ensure_ascii=False,separators=(',',':')),
                    instructions,json.dumps(schema.model_json_schema(),separators=(',',':'))))+REQUEST_PROTOCOL_OVERHEAD_TOKENS<=kwargs['input_limit']
                return SummaryOutput(statements=[SummaryStatementInput(**item) for item in payload['draft_statements'][:8]],
                    partial=len(payload['draft_statements'])>8),None
            ids=[r['id'] for r in payload['turns']]
            item=SummaryStatementInput(section='discussed',content=f'Project section beginning at {ids[0]} was discussed.',kind='fact',confidence='medium',evidence_turns=ids)
            items = [item] if not verbose else [item.model_copy(update={'content':(f'Section {ids[0]}: '+ 'note '*49).strip()}) for _ in range(4)]
            drafts.extend(item.content for item in items)
            return SummaryOutput(statements=items),None
        monkeypatch.setattr(post_call,'f06_structured_request',fake)
        summary=post_call.process_review(store,record,ledger=UsageLedger(),extractor=FakeMemoryExtractor([ExtractionOutput()]*20))
        assert store._connection.execute('SELECT partial FROM summary_versions WHERE id=?',(summary,)).fetchone()[0]
        assert all(row['content'] in drafts for row in store.summary_statements(summary))
        assert sum(len(row['content'].split()) for row in store.summary_statements(summary))<=500
        assert store._connection.execute('SELECT state FROM review_jobs WHERE record_id=?',(record,)).fetchone()[0]=='complete'


def test_frozen_extraction_boundaries_survive_new_prompt_and_ceiling(monkeypatch):
    from conversation_copilot import memory
    turns=[ConversationTurn(speaker_name='Alex',speaker_role='selected_contact',source='fixture',content='Details. '*100,
        display_order=i,timestamp=snapshot().created_at) for i in range(1,51)]
    original=memory.extraction_chunks(turns)
    version='f06-context-v2/'+json.dumps({'ceiling':memory.MAX_EXTRACTION_RESERVATION_TOKENS,
        'chunks':[[t.display_order for t in chunk] for chunk in original]})
    v1=memory.extraction_chunks(turns,prompt_version='f06-context-v1/200')
    monkeypatch.setattr(memory,'MAX_EXTRACTION_RESERVATION_TOKENS',9400)
    monkeypatch.setattr(memory,'EXTRACTION_INSTRUCTIONS',memory.EXTRACTION_INSTRUCTIONS+' Future instructions.'*100)
    assert memory.extraction_chunks(turns,prompt_version=version)==original
    assert memory.extraction_chunks(turns,prompt_version='f06-context-v1/200')==v1
    with pytest.raises(ValueError,match='boundaries changed'):
        memory.extraction_chunks(turns[:-1],prompt_version=version)


def test_interrupted_extraction_resumes_exact_unfinished_turns(tmp_path,monkeypatch):
    from conversation_copilot import memory
    with MemoryStore(tmp_path/'resume.sqlite3') as store:
        contact=store.create_contact('Alex')
        turns=[ConversationTurn(speaker_name='Alex',speaker_role='selected_contact',source='fixture',content='Details. '*100,
            display_order=i,timestamp=snapshot().created_at) for i in range(1,51)]
        record=store.create_record(source_kind='call',source_label='resume fixture',timezone_name='UTC',contact_id=contact.id,status='stopped',turns=turns)
        original=memory.extraction_chunks(turns)
        extractor=FakeMemoryExtractor([ExtractionOutput()])
        def interrupted(chunk):
            if extractor.calls:
                raise TimeoutError('fixture interruption')
            return extractor(chunk)
        with pytest.raises(TimeoutError):
            memory.analyze_record(store,record,interrupted)
        batch=store.retryable_batch(record)
        assert batch and store.batch_progress(batch)[0]==1
        monkeypatch.setattr(memory,'MAX_EXTRACTION_RESERVATION_TOKENS',9400)
        monkeypatch.setattr(memory,'EXTRACTION_INSTRUCTIONS',memory.EXTRACTION_INSTRUCTIONS+' More wording.'*100)
        resumed=FakeMemoryExtractor([ExtractionOutput()] * len(original))
        memory.analyze_record(store,record,resumed,batch_id=batch)
        assert [[t.display_order for t in chunk] for chunk in resumed.calls]==[[t.display_order for t in chunk] for chunk in original[1:]]


def test_changed_source_starts_new_batch_without_erasing_old_checkpoint(tmp_path):
    from conversation_copilot import memory
    with MemoryStore(tmp_path/'changed.sqlite3') as store:
        contact=store.create_contact('Alex')
        turn=ConversationTurn(speaker_name='Alex',speaker_role='selected_contact',source='fixture',content='Project details.',
            display_order=1,timestamp=snapshot().created_at)
        record=store.create_record(source_kind='call',source_label='changed source',timezone_name='UTC',contact_id=contact.id,status='stopped',turns=[turn])
        with pytest.raises(TimeoutError):
            memory.analyze_record(store,record,lambda chunk:(_ for _ in ()).throw(TimeoutError('fixture')))
        old=store.retryable_batch(record)
        store.append_turn(record,turn.model_copy(update={'display_order':2}))
        assert store.retryable_batch(record) is None
        assert post_call.review_estimate(store,record)[1]>0
        new=memory.analyze_record(store,record,FakeMemoryExtractor([ExtractionOutput()]),batch_id=old)
        assert new!=old and store.batch_progress(old)[2]=='invalidated'
        assert store.batch_progress(new)[2]=='pending_review'
