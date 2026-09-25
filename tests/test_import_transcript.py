import pytest
from conversation_copilot import import_transcript as imp
from conversation_copilot.interpretation import UsageLedger, LUNA_MODEL
from conversation_copilot.memory import MemoryStore


def test_twenty_line_cloud_boundary_and_full_local_attribution(monkeypatch):
    lines = [f'{"Alex" if i%2 else "Me"}: message {i}' for i in range(30)]
    def fake(schema,payload,instructions,**kw):
        assert payload == {'lines':'\n'.join(lines[:20]), 'contact_names': []}
        assert kw['model']==LUNA_MODEL and kw['reasoning']=='low'
        return imp.Participants(names=['Alex','Me']),None
    monkeypatch.setattr(imp,'f06_structured_request',fake)
    turns, suggestion = imp.detect_import('\n'.join(lines), ledger=UsageLedger.product())
    assert suggestion is None
    assert len(turns)==30 and turns[-1].content=='message 29'
    with MemoryStore(':memory:') as store:
        contact=store.create_contact('Alex')
        preview=store.import_preview(turns,timezone_name='UTC')
        record=store.confirm_import(preview,user_name='Me',contact_id=contact.id,source_label='Test')
        saved=store.record_turns(record)
        assert saved[0].speaker_role=='user' and saved[1].speaker_role=='selected_contact'
        assert all(t.timestamp is None for t in saved)
        from types import SimpleNamespace
        from conversation_copilot.memory import FakeMemoryExtractor, ExtractionOutput, MemoryProposalInput, SummaryOutput, SummaryStatementInput
        from conversation_copilot.post_call import process_review
        output=SummaryOutput(statements=[SummaryStatementInput(section='discussed',content='Alex sent message 1.',
            kind='fact',confidence='high',evidence_turns=[2])])
        extractor=FakeMemoryExtractor([ExtractionOutput(proposals=[MemoryProposalInput(content='Alex sent message 1.',
            memory_type='shared_reference',confidence='high',sensitivity='normal',evidence_turns=[2])])])
        client=SimpleNamespace(responses=SimpleNamespace(parse=lambda **kw: SimpleNamespace(output_parsed=output,
            usage=SimpleNamespace(input_tokens=100,output_tokens=50))))
        summary=process_review(store,record,ledger=UsageLedger.product(),extractor=extractor,client=client)
        assert store.summary_statements(summary)[0]['content']=='Alex sent message 1.'
        assert len(store.list_proposals(contact.id))==1


@pytest.mark.parametrize('text',[
    'Me: Hello\nAlex: Hi\nThird: Also here',
    'Unlabelled opening\nMe: Hello\nAlex: Hi',
    'Me: Hello\nAlex:',
    'Me: Hello\n6/20/26, 14:03 - Alex: Hi',
])
def test_ambiguous_or_extra_speakers_fail_closed(text):
    with pytest.raises(ValueError): imp.parse_labelled_transcript(text,['Me','Alex'])


def test_timed_labels_and_whatsapp_dates():
    turns=imp.parse_labelled_transcript('Me: First line\nsecond line\n[00:12] Alex: Reply',['Me','Alex'])
    assert turns[0].content=='First line\nsecond line' and turns[1].content=='Reply'
    turns=imp.parse_labelled_transcript('6/20/26, 14:03 - Me: Hello\n6/20/26, 14:04 - Alex: Hi',['Me','Alex'])
    assert turns[0].timestamp.year==2026


def test_missing_or_invented_participants_and_oversize_are_rejected(monkeypatch):
    monkeypatch.setattr(imp,'f06_structured_request',lambda *a,**k:(imp.Participants(names=['Me','Invented']),None))
    with pytest.raises(ValueError): imp.detect_import('Me: hello\nAlex: hi',ledger=UsageLedger.product())
    assert len(imp.participant_sample('x'*8001))==399


def test_sample_can_end_on_speaker_heading(monkeypatch):
    text='Me: Hello\n'+'continuation\n'*18+'Alex:\nReply'
    monkeypatch.setattr(imp,'f06_structured_request',lambda *a,**k:(imp.Participants(names=['Me','Alex']),None))
    assert imp.detect_import(text,ledger=UsageLedger.product())[0][-1].content=='Reply'


def test_bare_mentioned_name_does_not_change_speaker():
    turns=imp.parse_labelled_transcript('Me: Guest list:\nAlex\nSam\nAlex: Thanks',['Me','Alex'])
    assert len(turns)==2 and turns[0].content=='Guest list:\nAlex\nSam'
    with pytest.raises(ValueError): imp.parse_labelled_transcript('Me\nHello\nAlex\nHi',['Me','Alex'])


def test_whatsapp_notices_urls_and_colon_continuations(monkeypatch):
    text='6/20/26, 14:01 - Messages are encrypted\n6/20/26, 14:03 - Me: Details\nAddress: Here\nhttps://example.com\nAlex: quoted text\n6/20/26, 14:04 - Alex: Thanks'
    monkeypatch.setattr(imp,'f06_structured_request',lambda *a,**k:(imp.Participants(names=['Me','Alex']),None))
    turns,_=imp.detect_import(text,ledger=UsageLedger.product())
    assert len(turns)==2
    assert turns[0].content=='Details\nAddress: Here\nhttps://example.com\nAlex: quoted text'
    with pytest.raises(ValueError): imp.parse_labelled_transcript(text+'\n6/20/26, 14:05 - Third: Hello',['Me','Alex'])


def test_contact_suggestion_is_grounded_and_exact_alias_wins(monkeypatch):
    def detect(suggestion, names=()):
        monkeypatch.setattr(imp,'f06_structured_request',lambda *a,**k:(imp.Participants(names=['Me','Alex'],suggested_contact=suggestion),None))
        return imp.detect_import('Me: Hello\nAlex: Hi',ledger=UsageLedger.product(),contact_names=names)[1]
    assert detect('Alex')=='Alex'
    assert detect('Invented') is None
    assert detect('Me',['alex'])=='Alex'
    assert detect('Alex',['Me','Alex']) is None
