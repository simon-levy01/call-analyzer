from datetime import datetime, timezone
from types import SimpleNamespace
import json
import time
import pytest
from conversation_copilot.ask_memory import AskSession, source_event_date, memory_source
from conversation_copilot.memory import MemoryStore, ExtractionOutput, FakeMemoryExtractor, SummaryOutput, SummaryStatementInput
from conversation_copilot.models import ConversationTurn, SpeakerRole
from conversation_copilot.guidance import interpret_guidance, GuidanceOutput, GuidanceCandidate, GuidanceDisplay
from conversation_copilot.f04_evaluation import EvaluationScenario
from conversation_copilot.interpretation import UsageLedger, RetrievedMemoryContext, estimate_english_tokens, REQUEST_PROTOCOL_OVERHEAD_TOKENS
from conversation_copilot.post_call import process_review


def test_native_source_dates_imports_common_alias_and_long_memory(tmp_path):
    zone = str(datetime.now().astimezone().tzinfo)
    local = datetime(2026, 9, 7, 23, 30).astimezone()
    assert source_event_date('Appointment tomorrow', local.astimezone(timezone.utc).isoformat(), zone) == '2026-09-08'
    assert source_event_date('Appointment tomorrow', '2026-09-07T23:30:00', zone) == '2026-09-08'
    assert source_event_date('Appointment 2026-09-10', '', 'unknown') == '2026-09-10'
    with MemoryStore(tmp_path / 'memory.sqlite3') as store:
        contact = store.create_contact('Yaheli')
        store.create_contact('Dentist')
        record = store.create_record(source_kind='call', source_label='fictional native date', timezone_name=zone,
            contact_id=contact.id, status='stopped', turns=[ConversationTurn(speaker_name='Yaheli', speaker_role=SpeakerRole.SELECTED_CONTACT,
                source='fixture', content='Dentist appointment tomorrow at 3 PM', timestamp=local.astimezone(timezone.utc), display_order=1)])
        memory = store.create_memory(contact.id, 'Dentist appointment tomorrow at 3 PM', record_id=record, evidence_turns=[1])
        result = AskSession(contact.id).answer(store, 'dentist appointment recorded 07/09/2026', semantic=False, date_mode='recorded')
        assert result.status == 'answered' and result.sources[0].id == memory
        long = store.create_memory(contact.id, 'Long approved memory. ' * 30)
        assert memory_source(store, long, contact.id) is None
        assert memory_source(store, long, contact.id, for_cloud=True, display_limit=None)
        empty = store.create_record(source_kind='call', source_label='empty', timezone_name=zone, contact_id=contact.id, status='stopped')
        assert next(r for r in store.list_records(contact.id) if r['id'] == empty)['created_at']


def test_legacy_turn_review_preserves_deleted_turns_and_partial_summary(tmp_path):
    with MemoryStore(tmp_path / 'memory.sqlite3') as store:
        contact = store.create_contact('Yaheli')
        record = store.create_record(source_kind='call', source_label='legacy fictional', timezone_name='UTC', contact_id=contact.id, status='stopped',
            turns=[ConversationTurn(speaker_name='Yaheli', speaker_role=SpeakerRole.SELECTED_CONTACT, source='fixture', content=f'Plan {i}',
                timestamp=datetime(2026,9,7,tzinfo=timezone.utc), display_order=i) for i in (1,2,3)])
        with store.transaction() as db:
            db.execute("INSERT INTO summary_exclusions VALUES (?,0,'legacy_deletion','old','date')", (record,))
            db.execute("INSERT INTO summary_exclusions VALUES (?,1,'deleted_memory','known','date')", (record,))
        store.review_legacy_summary_turns(record, {1,2}, expected_generation=1)
        assert [t.display_order for t in store.summary_turns(record)] == [2]
        extractor = FakeMemoryExtractor([ExtractionOutput()])
        def parse(**kwargs):
            assert [t['id'] for t in json.loads(kwargs['input'])['turns']] == [2]
            return SimpleNamespace(output_parsed=SummaryOutput(statements=[SummaryStatementInput(section='plans', content='Plan 2', kind='fact', confidence='high', evidence_turns=[2])]),
                usage=SimpleNamespace(input_tokens=100, output_tokens=50))
        summary = process_review(store, record, ledger=UsageLedger(), extractor=extractor, client=SimpleNamespace(responses=SimpleNamespace(parse=parse)))
        assert not extractor.calls
        assert store._connection.execute('SELECT partial FROM summary_versions WHERE id=?',(summary,)).fetchone()[0]
        store.review_legacy_summary_turns(record, {3}, expected_generation=1)
        assert [t.display_order for t in store.summary_turns(record)] == [2,3]


def test_live_guidance_shares_memory_allowance(monkeypatch):
    from conversation_copilot import interpretation
    snapshot = EvaluationScenario('shared','f06','Tell me more.','The appointment is Tuesday.').snapshot('all')
    memory = RetrievedMemoryContext(memory_id='m', revision_id='r', excerpt='Appointment on Tuesday.',
        memory_type='event_date', confidence='high', sensitivity_safe=True, rank=1, relevance='lexical')
    snapshot = snapshot.model_copy(update={'memories': [memory]})
    monkeypatch.setattr(interpretation, 'MEMORY_CONTEXT_BUDGET_TOKENS', 1)
    live = interpretation.prepare_interpretation_request(snapshot, preserve_transcript=True)
    legacy = interpretation.prepare_interpretation_request(snapshot)
    assert len(json.loads(live.input_text)['m']) == 1
    assert not json.loads(legacy.input_text).get('m')


def test_guidance_boundary_candidate_filter_and_distinct_dismissals(monkeypatch):
    from conversation_copilot import guidance
    snapshot = EvaluationScenario('boundary','f06','Could we review the appointment plan? '*12,'The appointment is on Tuesday at three. '*12).snapshot('all')
    copies = [snapshot.turns[i % 2].model_copy(update={'display_order': i+1}) for i in range(16)]
    memories = [RetrievedMemoryContext(memory_id=f'm{i}', revision_id=f'r{i}', excerpt='Appointment reminder. '*8, memory_type='event_date',
        confidence='high', sensitivity_safe=True, rank=i+1, relevance='lexical') for i in range(4)]
    from conversation_copilot.interpretation import build_snapshot
    snapshot = build_snapshot(copies, snapshot_id=snapshot.snapshot_id, generation=snapshot.generation,
        contact_id='boundary-contact', retrieved_memories=memories,
        vocal_observations=snapshot.vocal_observations, visual_buckets=snapshot.visual_buckets)
    def request(schema, payload, instructions, **kwargs):
        estimate = sum(estimate_english_tokens(s) for s in (json.dumps(payload,ensure_ascii=False,separators=(',',':')),instructions,json.dumps(schema.model_json_schema(),separators=(',',':')))) + REQUEST_PROTOCOL_OVERHEAD_TOKENS
        assert estimate <= guidance.GUIDANCE_INPUT_LIMIT
        # Reuse a real wire shape without depending on paid output.
        wire = {'status':'insufficient_evidence','tone':None,'cue':None}
        # A canonical accepted wire fixture from the existing model schema.
        from conversation_copilot.interpretation import _InterpretationWireUpdate
        wire = _InterpretationWireUpdate(status='insufficient_evidence')
        return GuidanceOutput(interpretation=wire, replies=[GuidanceCandidate(text='The plan is [fill in steps].', confidence='high',turn_ids=payload['turn_ids'][:1]),
            GuidanceCandidate(text='Could we confirm the time?',confidence='medium',turn_ids=[payload['reply_to_turn_id']]),
            GuidanceCandidate(text='Four PM works for me.',confidence='low',turn_ids=payload['turn_ids'][:1])]), None
    monkeypatch.setattr(guidance,'f06_structured_request',request)
    result = interpret_guidance(snapshot, ledger=UsageLedger())
    assert [c.text for c in result.replies] == ['Could we confirm the time?']
    original = request
    def negative_commitment(*args, **kwargs):
        output, usage = original(*args, **kwargs)
        output.replies[0].text = "I won't bring it up."
        return output, usage
    monkeypatch.setattr(guidance, 'f06_structured_request', negative_commitment)
    assert [c.text for c in interpret_guidance(snapshot, ledger=UsageLedger()).replies] == ['Could we confirm the time?']
    display = GuidanceDisplay()
    item = GuidanceCandidate(text='Could you clarify?',confidence='medium',turn_ids=[1])
    same = GuidanceCandidate(text='Would you explain that?',confidence='medium',turn_ids=[2])
    other = GuidanceCandidate(text='Shall we confirm the time?',confidence='medium',turn_ids=[2])
    assert display.fingerprint('replies',item) == display.fingerprint('replies',same)
    assert display.fingerprint('replies',item) != display.fingerprint('replies',other)


def test_missing_deletion_provenance_is_reviewable_and_bulk_review_is_atomic(tmp_path):
    with MemoryStore(tmp_path / 'memory.sqlite3') as store:
        contact = store.create_contact('Yaheli')
        record = store.create_record(source_kind='call', source_label='unknown provenance',timezone_name='UTC',contact_id=contact.id,status='stopped',
            turns=[ConversationTurn(speaker_name='Yaheli',speaker_role=SpeakerRole.SELECTED_CONTACT,source='fixture',content='Two separate plans.',
                timestamp=datetime(2026,9,7,tzinfo=timezone.utc),display_order=1)])
        memory = store.create_memory(contact.id,'An old plan.',record_id=record)
        store.delete_memory(memory)
        assert not store.summary_turns(record)
        store.review_legacy_summary_turns(record,{1},expected_generation=1)
        assert len(store.summary_turns(record)) == 1
        first = store.create_memory(contact.id,'Plan one')
        second = store.create_memory(contact.id,'Plan two')
        with store.transaction() as db:
            db.execute('UPDATE memories SET needs_review=1 WHERE id IN (?,?)',(first,second))
        with pytest.raises(ValueError):
            store.confirm_reviewed_memories({first:store.current_revision(first)['id'],second:'stale'})
        assert store._connection.execute('SELECT needs_review FROM memories WHERE id=?',(first,)).fetchone()[0] == 1
        store.confirm_reviewed_memories({first:store.current_revision(first)['id'],second:store.current_revision(second)['id']})
        assert store._connection.execute('SELECT sum(needs_review) FROM memories').fetchone()[0] == 0


def test_recordless_approval_date_uses_query_zone_and_guidance_keeps_tone_stable(tmp_path):
    from datetime import timedelta
    from conversation_copilot.guidance import GuidedInterpretation
    from conversation_copilot.interpretation import StableInterpretationCard, interpretation_signature
    with MemoryStore(tmp_path / 'memory.sqlite3') as store:
        contact=store.create_contact('Yaheli')
        memory=store.create_memory(contact.id,'Dentist appointment at three.')
        local = datetime(2026,9,8,0,30).astimezone()
        with store.transaction() as db:
            db.execute("UPDATE memory_revisions SET approved_at=? WHERE memory_id=?",(local.astimezone(timezone.utc).isoformat(),memory))
        result=AskSession(contact.id).answer(store,'dentist appointment recorded 08/09/2026',date_mode='recorded',semantic=False,
            reference=local)
        assert result.status == 'answered'
    first=GuidedInterpretation(status='insufficient_evidence',explanation='Not enough evidence.',snapshot_id=1,generation=1,
        replies=[GuidanceCandidate(text='Could we clarify?',confidence='medium',turn_ids=[1])])
    second=first.model_copy(update={'snapshot_id':2,'replies':[GuidanceCandidate(text='Could we clarify?',confidence='medium',turn_ids=[2])]})
    assert interpretation_signature(first) != interpretation_signature(second)
    card=StableInterpretationCard()
    assert card.offer(first,0) == 'replaced'
    assert card.offer(second,15) == 'unchanged' and card.shown_at == 0


@pytest.mark.parametrize('remote', ['I am fine; stop asking.', 'Oh great, exactly what I needed.', 'I do not want to discuss it.'])
def test_combined_guidance_preserves_cautious_tone_without_discarding_factual_questions(monkeypatch, remote):
    from conversation_copilot import guidance
    from conversation_copilot.interpretation import _InterpretationWireUpdate
    snapshot = EvaluationScenario('cautious','f06','Would you like to discuss this?',remote).snapshot('transcript')
    calls=[]
    def request(schema,payload,instructions,**kwargs):
        calls.append(payload)
        return GuidanceOutput(interpretation=_InterpretationWireUpdate(status='insufficient_evidence'),
            replies=[GuidanceCandidate(text='Would you like to change the subject?',confidence='medium',turn_ids=[2])]),None
    monkeypatch.setattr(guidance,'f06_structured_request',request)
    result=interpret_guidance(snapshot,ledger=UsageLedger())
    assert len(calls)==1 and result.replies
    assert result.status.value == 'insufficient_evidence'
    assert not result.tones and not result.social_cues


def test_no_remote_speech_returns_local_abstention_without_cloud(monkeypatch):
    from conversation_copilot import guidance
    snapshot=EvaluationScenario('no-remote','f06','One user turn.','Another user turn.').snapshot('transcript')
    snapshot=snapshot.model_copy(update={'turns':[t.model_copy(update={'speaker_role':SpeakerRole.USER}) for t in snapshot.turns]})
    def forbidden(*args,**kwargs): raise AssertionError('no remote evidence must not dispatch cloud')
    monkeypatch.setattr(guidance,'f06_structured_request',forbidden)
    result=interpret_guidance(snapshot,ledger=UsageLedger())
    assert result.status.value=='insufficient_evidence'
    assert not result.replies
