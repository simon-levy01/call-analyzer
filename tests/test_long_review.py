"""Large source messages remain lossless, bounded and retryable (no API)."""
import json
from types import SimpleNamespace
from conversation_copilot.memory import (MemoryStore, review_turn_fragments, extraction_chunks,
    extraction_reservation_tokens, analyze_record, FakeMemoryExtractor, ExtractionOutput,
    SummaryOutput, SummaryStatementInput)
from conversation_copilot.models import ConversationTurn
from conversation_copilot.interpretation import UsageLedger
from conversation_copilot.post_call import review_estimate, process_review, _edited_payloads


def test_large_message_chunks_source_integrity_and_resume():
    text=('A detailed project discussion. '*4000)+'END'
    turn=ConversationTurn(speaker_name='Alex',speaker_role='selected_contact',source='test',content=text,display_order=1)
    fragments=review_turn_fragments([turn])
    assert ''.join(t.content for t in fragments)==text
    assert all(t.display_order==1 and len(t.content)<=2000 for t in fragments)
    assert all(extraction_reservation_tokens(c,legacy=True)<=6000 for c in extraction_chunks([turn],legacy=True,max_turns=20))
    with MemoryStore(':memory:') as store:
        contact=store.create_contact('Alex')
        record=store.create_record(source_kind='import',source_label='Long',timezone_name='UTC',contact_id=contact.id,status='imported',turns=[turn])
        assert review_estimate(store,record)[0]>1
        calls=[]
        def fail_second(chunk):
            calls.append(chunk)
            if len(calls)==2: raise RuntimeError('Pause')
            return ExtractionOutput(),SimpleNamespace(input_tokens=0,output_tokens=0,reasoning_tokens=0,dollars=0)
        try: analyze_record(store,record,fail_second)
        except RuntimeError: pass
        batch=store.retryable_batch(record)
        version=store._connection.execute('select prompt_version from proposal_batches where id=?',(batch,)).fetchone()[0]
        assert version.startswith('f06-fragments-v3/')
        frozen=extraction_chunks([turn],prompt_version=version)
        assert [t.content for t in frozen[0]]==[t.content for t in calls[0]]
        extractor=FakeMemoryExtractor([ExtractionOutput() for _ in frozen[1:]])
        analyze_record(store,record,extractor,batch_id=batch)
        assert len(extractor.calls)==len(frozen)-1
        assert store.record_turns(record)[0].content==text
        summary_output=SummaryOutput(statements=[SummaryStatementInput(section='discussed',content='Alex discussed the project.',kind='fact',confidence='high',evidence_turns=[1])])
        merge_calls=[]
        def parse(**kw):
            assert len(kw['input'])<25000
            payload=json.loads(kw['input'])
            if payload.get('source_mode')=='previously_source_cited_drafts':
                merge_calls.append(payload)
                assert 'source' not in payload
            return SimpleNamespace(output_parsed=summary_output,usage=SimpleNamespace(input_tokens=100,output_tokens=100))
        summary=process_review(store,record,ledger=UsageLedger.product(),client=SimpleNamespace(responses=SimpleNamespace(parse=parse)))
        assert store.summary_statements(summary)
        assert merge_calls and not store._connection.execute('select partial from summary_versions where id=?',(summary,)).fetchone()[0]
        payloads=_edited_payloads('Alex discussed the project.',[turn])
        assert len(payloads)>1
        assert ''.join(row['text'] for p in payloads for row in p['source_context']['turns'])==text


def test_previously_valid_source_and_summary_boundaries_stay_unchanged():
    turns=[ConversationTurn(speaker_name='Alex',speaker_role='selected_contact',source='test',content='x'*3000,display_order=i) for i in range(1,5)]
    assert all(a is b for a,b in zip(turns,review_turn_fragments(turns)))
    current=extraction_chunks(turns,legacy=True,max_turns=20)
    historical=extraction_chunks(turns,max_turns=20,prompt_version='historical')
    assert [[t.display_order for t in c] for c in current]==[[t.display_order for t in c] for c in historical]


def test_large_unicode_message_also_fits_each_request():
    turn=ConversationTurn(speaker_name='Alex',source='test',display_order=1,content=chr(128578)*5000)
    assert ''.join(t.content for t in review_turn_fragments([turn]))==turn.content
    assert all(extraction_reservation_tokens(c,legacy=True)<=6000 for c in extraction_chunks([turn],legacy=True,max_turns=20))
