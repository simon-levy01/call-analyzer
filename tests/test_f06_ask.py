from conversation_copilot.ask_memory import AskSession, memory_source, validate_sources
from conversation_copilot.memory import MemoryStore
from conversation_copilot.ask_memory import query_period, source_event_date
from datetime import date, datetime, timezone
from types import SimpleNamespace


def test_search_excludes_pending_and_rejected_memories_and_summaries(tmp_path, monkeypatch):
    import pytest
    from conversation_copilot import interpretation
    from conversation_copilot.ask_memory import cloud_sources, cloud_answer, CloudAskOutput
    from conversation_copilot.memory import MemoryProposalInput, SummaryOutput, SummaryStatementInput
    from conversation_copilot.models import ConversationTurn

    with MemoryStore(tmp_path / 'approval-boundary.sqlite3') as store:
        contact = store.create_contact('Alex')
        approved, blocked = set(), set()
        for kind in ('memory', 'summary'):
            for state in ('approved', 'pending', 'rejected', 'legacy_rejected', 'approved_then_rejected'):
                if kind == 'summary' and state == 'legacy_rejected':
                    continue
                if kind == 'memory' and state == 'approved_then_rejected':
                    continue
                content = f'Alex has a dentist appointment at {kind}_{state} Clinic.'
                record = store.create_record(source_kind='call', source_label='Synthetic approval check',
                    timezone_name='UTC', contact_id=contact.id, status='stopped', turns=[ConversationTurn(
                        speaker_name='Alex', speaker_role='selected_contact', source='fixture',
                        display_order=1, content=content)])
                if kind == 'memory':
                    batch = store.create_batch(record, model='fake', reasoning='none')
                    item = store.store_proposals(batch, [MemoryProposalInput(content=content,
                        memory_type='event_date', confidence='high', evidence_turns=[1])])[0]
                    if state == 'approved':
                        item = store.approve_proposal(item)
                    elif state == 'rejected':
                        store.review_record_proposals(record, [item], approve=False, expected_pending={item: content})
                    elif state == 'legacy_rejected':
                        store.reject_proposal(item)
                else:
                    version = store.create_summary_draft(record, SummaryOutput(statements=[SummaryStatementInput(
                        section='plans', content=content, kind='fact', confidence='high', evidence_turns=[1])]),
                        expected_generation=1)
                    item = store.summary_statements(version)[0]['id']
                    if state == 'approved':
                        store.approve_summary(version)
                    elif state in ('rejected', 'approved_then_rejected'):
                        if state == 'approved_then_rejected':
                            store.approve_summary(version)
                        store.delete_summary(record)  # The Review button's actual rejection path.
                        assert not store._connection.execute('SELECT 1 FROM summary_search WHERE statement_id=?', (item,)).fetchone()
                        assert not store._connection.execute('SELECT 1 FROM summary_statements WHERE id=?', (item,)).fetchone()
                (approved if state == 'approved' else blocked).add(item)

        sources, complete = cloud_sources(store, contact.id, 'dentist appointment')
        assert complete and {source.id for source in sources} == approved
        result = AskSession(contact.id).answer(store, 'dentist appointment', semantic=False)
        assert {source.id for source in result.sources} == approved
        all_contacts = AskSession()
        all_contacts.set_scope(None, all_contacts=True)
        assert {source.id for source in all_contacts.answer(store, 'dentist appointment', semantic=False).sources} == approved
        seen = []
        def request(schema, payload, instructions, **kwargs):
            seen.append(payload)
            assert {entry['id'] for entry in payload['evidence']} == approved
            assert all('pending' not in entry['text'] and 'rejected' not in entry['text']
                       for entry in payload['evidence'])
            return CloudAskOutput(status='answered', answer='There is an approved appointment.',
                                  source_ids=[next(iter(approved))]), SimpleNamespace(dollars=0)
        monkeypatch.setattr(interpretation, 'f06_structured_request', request)
        assert cloud_answer(store, 'dentist appointment', contact_id=contact.id, ledger=None).status == 'answered'
        assert len(seen) == 1
        for item in blocked:
            monkeypatch.setattr(interpretation, 'f06_structured_request', lambda *a, **kw:
                (CloudAskOutput(status='answered', answer='Unsupported appointment.', source_ids=[item]),
                 SimpleNamespace(dollars=0)))
            with pytest.raises(ValueError, match='unsupported evidence'):
                cloud_answer(store, 'dentist appointment', contact_id=contact.id, ledger=None)


def test_approved_summary_offer_is_searchable_without_becoming_an_agreement(tmp_path):
    from conversation_copilot.ask_memory import cloud_sources, summary_source
    from conversation_copilot.memory import SummaryOutput, SummaryStatementInput
    from conversation_copilot.models import ConversationTurn
    with MemoryStore(tmp_path / 'offers.sqlite3') as store:
        contact = store.create_contact('Alex')
        rid = store.create_record(source_kind='call', source_label='Offers', timezone_name='UTC',
            contact_id=contact.id, status='stopped', turns=[ConversationTurn(speaker_name='Alex',
                speaker_role='selected_contact', source='fixture', display_order=1, content='You can call me during the event.')])
        sid = store.create_summary_draft(rid, SummaryOutput(statements=[SummaryStatementInput(section='follow_ups',
            content='Alex offered a call during the event.', kind='advice', confidence='high', evidence_turns=[1])]), expected_generation=1)
        store.approve_summary(sid)
        statement = store.summary_statements(sid)[0]['id']
        sources, complete = cloud_sources(store,contact.id,'Could I call Alex during the event?')
        assert complete and len(sources)==1 and sources[0].id==statement
        assert 'not an agreement' in sources[0].kind
        assert not store._summary_eligible(statement)  # General factual eligibility stays conservative.
        assert store._connection.execute('SELECT 1 FROM summary_search WHERE statement_id=?',(statement,)).fetchone()
        store.edit_summary_statement(statement,'Alex offered to talk during the event.')
        assert 'not an agreement' in summary_source(store,statement,contact.id).kind
        current=store.summary_statements(sid)[0]
        edited=store.edit_review_summary(sid,current['content']+'\n\nThe offer was discussed.',
            expected_statements={statement:(current['content'],0)})
        unchanged=store.summary_statements(edited)[0]
        assert unchanged['kind']=='advice' and unchanged['section']=='follow_ups' and unchanged['confidence']=='high'
        store.delete_summary(rid)
        assert summary_source(store,statement,contact.id) is None


def test_cloud_history_has_dated_sources_and_automatic_sensitive_eligibility_and_freshness(tmp_path, monkeypatch):
    from conversation_copilot.ask_memory import cloud_sources, cloud_answer, CloudAskOutput
    from conversation_copilot.f06_evaluation import seed_history
    from conversation_copilot import interpretation
    with MemoryStore(tmp_path / "history.sqlite3") as store:
        contact, ids, _ = seed_history(store)
        secret = store.create_memory(contact, "Private withheld detail", sensitivity="sensitive")
        other = store.create_contact("Wrong person")
        wrong = store.create_memory(other.id, "Other person's bereavement")
        sources, complete = cloud_sources(store, contact, "Who did he lose most recently?")
        assert complete and len(sources) == 19
        assert {ids["old_loss"], ids["new_loss"]} <= {s.id for s in sources}
        assert secret in {s.id for s in sources}
        assert wrong not in {s.id for s in sources}
        seen = {}
        def request(schema, payload, instructions, **kwargs):
            seen.update(payload)
            assert kwargs["model"] == "gpt-5.6-luna" and kwargs["reasoning"] == "low" and kwargs["is_current"]()
            return CloudAskOutput(status="answered", answer="His friend Maya died on September 5, 2026.",
                                  source_ids=[ids["new_loss"]]), SimpleNamespace(dollars=.001)
        monkeypatch.setattr(interpretation, "f06_structured_request", request)
        result = cloud_answer(store, "Who did he lose most recently?", contact_id=contact, ledger=None)
        assert [s.id for s in result.sources] == [ids["new_loss"]]
        assert seen["complete_eligible_history"] and len(seen["evidence"]) == 19
        assert next(s for s in sources if s.id == ids["new_loss"]).kind == "Approved memory"
        store.set_cloud_permission(ids["new_loss"], False)
        assert not validate_sources(store, result.sources, for_cloud=True)
        assert ids["new_loss"] in {source.id for source in cloud_sources(store, contact, "loss")[0]}


def test_cloud_long_memories_and_output_guards(tmp_path, monkeypatch):
    import pytest
    from conversation_copilot.ask_memory import cloud_sources, cloud_answer, CloudAskOutput
    from conversation_copilot import interpretation
    with MemoryStore(tmp_path / "long.sqlite3") as store:
        contact = store.create_contact("Alex")
        memory = store.create_memory(contact.id, "Detailed approved recollection. " * 20)
        sources, complete = cloud_sources(store, contact.id, "What is the missing venue?")
        assert complete and len(sources) == 1 and len(sources[0].content) > 400
        assert validate_sources(store, sources) and validate_sources(store, sources, for_cloud=True)
        response = CloudAskOutput(status="no_match", answer='There is no evidence for "missing venue".', source_ids=[])
        monkeypatch.setattr(interpretation, "f06_structured_request", lambda *a, **kw: (response, SimpleNamespace(dollars=.001)))
        for status in ("no_match", "clarification", "possibilities", "conflict", "unavailable"):
            response = response.model_copy(update={"status": status})
            assert cloud_answer(store, "What is the missing venue?", contact_id=contact.id, ledger=None).status == status
        response = CloudAskOutput(status="answered", answer="Source " + memory, source_ids=[memory])
        with pytest.raises(ValueError, match="prints evidence IDs"):
            cloud_answer(store, "What is the missing venue?", contact_id=contact.id, ledger=None)
        response = CloudAskOutput(status="answered", answer='Alex said "missing venue".', source_ids=[memory])
        with pytest.raises(ValueError, match="quote does not match"):
            cloud_answer(store, "What is the missing venue?", contact_id=contact.id, ledger=None)


def test_cloud_history_large_scope_is_bounded_and_preserves_ranked_old_event(tmp_path):
    from conversation_copilot.ask_memory import cloud_sources, cloud_answer, _cloud_evidence
    from conversation_copilot.interpretation import estimate_english_tokens, UsageLedger
    import json
    import pytest
    with MemoryStore(tmp_path / "large.sqlite3") as store:
        contact = store.create_contact("Alex")
        wanted = store.create_memory(contact.id, "Grandfather Arthur helped rehearse presentations in February.")
        for n in range(70):
            store.create_memory(contact.id, f"Later unrelated entry {n}. " + "Visited a different local garden with friends. " * 6)
        sources, complete = cloud_sources(store, contact.id, "Who helped him rehearse?")
        assert not complete and sources[0].id == wanted and len(sources) < 71
        assert sum(estimate_english_tokens(json.dumps(_cloud_evidence(s), ensure_ascii=False)) for s in sources) <= 4700
        def parse(**kwargs):
            assert not json.loads(kwargs["input"])["complete_eligible_history"]
            raise RuntimeError("Reached bounded dispatch")
        with pytest.raises(RuntimeError, match="Reached bounded dispatch"):
            cloud_answer(store, "Who helped him rehearse?", contact_id=contact.id, ledger=UsageLedger(),
                         client=SimpleNamespace(responses=SimpleNamespace(parse=parse)))


def test_local_appointment_scope_followups_and_stale_sources(tmp_path):
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        contact = store.create_contact("Yaheli", "dentist fixture")
        memory = store.create_memory(contact.id, "Yaheli's dentist appointment is Tuesday at 3 PM at Cedar Clinic.", memory_type="event_date")
        session = AskSession(contact.id)
        result = session.answer(store, "What time is Yaheli's dentist appointment?", semantic=False)
        assert result.status == "answered" and "3 PM" in result.answer
        assert result.sources[0].id == memory
        session.choose_event(memory)
        result = session.answer(store, "and where?", semantic=False)
        assert "Cedar Clinic" in result.answer
        assert validate_sources(store, result.sources)
        store.correct_memory(memory, "Dentist appointment Tuesday at 4 PM at Cedar Clinic.")
        assert not validate_sources(store, result.sources)
        assert "4 PM" in session.answer(store, "what time?", semantic=False).answer
        other = store.create_contact("Alex")
        assert session.answer(store, "What is Alex's appointment?").status == "clarification"
        session.set_scope(other.id)
        assert not session.questions and not session.exchanges and session.event_id is None
        assert session.answer(store, "and where?").status == "clarification"
        session.close()
        assert session.contact_id is None


def test_ask_approved_only_sensitive_deleted_and_ambiguous(tmp_path):
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        contact = store.create_contact("Yaheli")
        first = store.create_memory(contact.id, "Dentist appointment Tuesday at 3 PM", memory_type="event_date", sensitivity="sensitive")
        session = AskSession(contact.id)
        assert session.answer(store, "dentist appointment", semantic=False).status == "answered"
        assert memory_source(store, first, contact.id, for_cloud=True) is not None
        store.create_memory(contact.id, "Dentist appointment Friday at 10 AM", memory_type="event_date")
        assert session.answer(store, "dentist appointment", semantic=False).status == "possibilities"
        store.delete_memory(first)
        result = session.answer(store, "dentist appointment", semantic=False)
        assert "3 PM" not in result.answer
        assert result.status == "answered"
        session.set_scope(None, all_contacts=True)
        result = session.answer(store, "dentist appointment", semantic=False)
        assert result.status == "possibilities" and all(source.contact_label == "Yaheli" for source in result.sources)


def test_temporal_reference_is_source_zone_and_query_calendar():
    assert source_event_date("Appointment tomorrow at 3 PM", "2026-12-31T23:30:00+00:00", "Asia/Jerusalem") == "2027-01-02"
    assert source_event_date("Appointment tomorrow at 7 my time", "2026-09-07T12:00:00+00:00", "unknown") is None
    assert source_event_date("Today or tomorrow", "2026-09-07T12:00:00+00:00", "Asia/Jerusalem") is None
    assert query_period("last week", datetime(2027, 1, 1, tzinfo=timezone.utc)) == (date(2026, 12, 21), date(2026, 12, 27))
    assert query_period("yesterday", datetime(2027, 1, 1, tzinfo=timezone.utc)) == (date(2026, 12, 31), date(2026, 12, 31))
    assert query_period("09/10/2026", datetime.now(timezone.utc)) == (date(2026, 10, 9), date(2026, 10, 9))


def test_exact_subject_is_not_ambiguous_with_unrelated_semantic_neighbors(tmp_path, monkeypatch):
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        contact = store.create_contact("Yaheli")
        appointment = store.create_memory(contact.id, "Dentist appointment Tuesday at 3 PM")
        book = store.create_memory(contact.id, "Book number 87 is on the reading list")
        monkeypatch.setattr(store, "retrieve", lambda *a, **kw: SimpleNamespace(semantic_available=True, ambiguous=False, matches=(
            SimpleNamespace(memory_id=appointment, reason="lexical+semantic"), SimpleNamespace(memory_id=book, reason="semantic"))))
        result = AskSession(contact.id).answer(store, "What time is the dentist appointment?")
        assert result.status == "answered" and [source.id for source in result.sources] == [appointment]


def test_date_scope_is_applied_before_candidate_limit(tmp_path):
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        contact = store.create_contact("Yaheli")
        wanted = store.create_memory(contact.id, "Dentist appointment at 3 PM", normalized_date_start="2026-09-10")
        for day in range(1, 9):
            store.create_memory(contact.id, "Dentist appointment at 9 AM", normalized_date_start=f"2026-09-{day:02}")
        result = AskSession(contact.id).answer(store, "Dentist appointment on 10/09/2026", date_mode="event", semantic=False)
        assert result.status == "answered" and result.sources[0].id == wanted
