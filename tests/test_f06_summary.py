from datetime import datetime, timezone

import pytest
import sqlite3
import json
from types import SimpleNamespace

from conversation_copilot.memory import MemoryStore, SummaryOutput, SummaryStatementInput
from conversation_copilot.models import ConversationTurn, SpeakerRole
from conversation_copilot.memory import _SCHEMA, MemoryStoreUnavailable, MemoryProposalInput, FakeMemoryExtractor, ExtractionOutput
from conversation_copilot.interpretation import UsageLedger, InterpretationUnavailable
from conversation_copilot.post_call import process_review


def setup_record(store):
    contact = store.create_contact("Yaheli", disambiguator="fictional dentist case")
    record = store.create_record(
        source_kind="call", source_label="F06 fictional appointment", timezone_name="Asia/Jerusalem",
        contact_id=contact.id, status="stopped", turns=[ConversationTurn(
            speaker_name="Yaheli", speaker_role=SpeakerRole.SELECTED_CONTACT,
            source="fixture", content="My dentist appointment is Tuesday at 3 PM at Cedar Clinic.",
            timestamp=datetime(2026, 9, 7, 12, tzinfo=timezone.utc), display_order=1,
        )],
    )
    return contact.id, record


def draft(store, record):
    return store.create_summary_draft(record, SummaryOutput(statements=[SummaryStatementInput(
        section="plans", content="Dentist appointment Tuesday at 3 PM at Cedar Clinic.",
        kind="fact", confidence="high", evidence_turns=[1],
    )]), expected_generation=1)


def test_review_accepts_six_discussed_statements_without_retry(tmp_path):
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        _, record = setup_record(store)
        source = store.record_turns(record)[0]
        for order in range(2, 7):
            store.append_turn(record, source.model_copy(update={"display_order": order, "content": f"Project milestone {order} is complete."}))
        output = SummaryOutput(statements=[SummaryStatementInput(section="discussed", content=turn.content,
            kind="fact", confidence="high", evidence_turns=[turn.display_order]) for turn in store.record_turns(record)])
        calls = []
        def parse(**kwargs):
            calls.append(kwargs)
            return SimpleNamespace(output_parsed=output, usage=SimpleNamespace(input_tokens=100, output_tokens=100))
        summary = process_review(store, record, ledger=UsageLedger(), extractor=FakeMemoryExtractor([ExtractionOutput()]),
            client=SimpleNamespace(responses=SimpleNamespace(parse=parse)))
        assert len(calls) == 1
        assert len(store.summary_statements(summary)) == 6
        assert store._connection.execute("SELECT state FROM review_jobs WHERE record_id=?", (record,)).fetchone()[0] == "complete"
        oversized = output.model_copy(deep=True)
        for statement in oversized.statements:
            statement.content = "word " * 90
        longer = store.create_summary_draft(record, oversized, expected_generation=1)
        assert sum(len(s['content'].split()) for s in store.summary_statements(longer)) == 540


def test_summary_has_no_overall_word_or_statement_limit(tmp_path):
    with MemoryStore(tmp_path / 'long-summary.sqlite3') as store:
        _, record = setup_record(store)
        output = SummaryOutput(statements=[SummaryStatementInput(section='discussed',
            content=('A substantial topic was discussed. ' * 15).strip(), kind='fact', confidence='high', evidence_turns=[1])
            for _ in range(25)])
        sid = store.create_summary_draft(record, output, expected_generation=1)
        assert sum(len(s['content'].split()) for s in store.summary_statements(sid)) == 1875
        assert len(store.summary_statements(sid)) == 25
        assert store.summary_statements(sid)[0]['content'] == output.statements[0].content


def test_old_generation_user_edit_does_not_block_new_review(tmp_path):
    with MemoryStore(tmp_path/'generation.sqlite3') as store:
        _,record=setup_record(store)
        sid=draft(store,record)
        statement=store.summary_statements(sid)[0]
        edited=store.edit_review_summary(sid,'Dentist at 4 PM.',expected_statements={statement['id']:(statement['content'],0)})
        store.approve_summary(edited)
        with store.transaction() as db:
            db.execute('UPDATE conversation_records SET generation=generation+1 WHERE id=?',(record,))
        assert store.summary_for_review(record) is None
        client=SimpleNamespace(responses=SimpleNamespace(parse=lambda **_:SimpleNamespace(output_parsed=SummaryOutput(),
            usage=SimpleNamespace(input_tokens=100,output_tokens=10))))
        fresh=process_review(store,record,ledger=UsageLedger.product(),client=client,extractor=FakeMemoryExtractor([ExtractionOutput()]))
        assert fresh!=edited and store.summary_for_review(record)['record_generation']==2


@pytest.mark.parametrize('fail', [False, True])
def test_version_five_summary_migration_preserves_links_and_rolls_back(tmp_path, fail):
    from conversation_copilot.memory import _SUMMARY_SCHEMA, SCHEMA_VERSION
    path = tmp_path/'legacy.sqlite3'
    db = sqlite3.connect(path)
    for sql in (*_SCHEMA, *_SUMMARY_SCHEMA):
        db.execute(sql.replace('CHECK(length(content) >= 1)', 'CHECK(length(content) BETWEEN 1 AND 280)'))
    db.execute('CREATE TABLE declined_memories (record_id TEXT NOT NULL REFERENCES conversation_records(id) ON DELETE CASCADE, digest TEXT NOT NULL, PRIMARY KEY(record_id,digest))')
    db.execute(f'PRAGMA user_version={SCHEMA_VERSION}')
    db.commit()
    db.close()
    with MemoryStore(path) as store:
        contact,rid = setup_record(store)
        sid = draft(store,rid)
        store.create_memory(contact,'Dentist Tuesday',record_id=rid,evidence_turns=[1])
        store.approve_summary(sid)
        tables=('summary_versions','summary_statements','summary_evidence','summary_dependencies','summary_search')
        saved={t:[tuple(r) for r in store._connection.execute(f'SELECT * FROM {t}')] for t in tables}
        store._connection.execute('PRAGMA user_version=5')
    def failure(_):
        raise RuntimeError('migration failure')
    if fail:
        with pytest.raises(MemoryStoreUnavailable):
            MemoryStore(path,migration_hook=failure)
        with sqlite3.connect(path) as db:
            assert db.execute('PRAGMA user_version').fetchone()[0]==5
            assert {t:db.execute(f'SELECT * FROM {t}').fetchall() for t in tables}==saved
    with MemoryStore(path) as store:
        assert {t:[tuple(r) for r in store._connection.execute(f'SELECT * FROM {t}')] for t in tables}==saved
        assert store._connection.execute('PRAGMA foreign_keys').fetchone()[0]==1
        statement=store.summary_statements(sid)[0]
        longer='Substantive summary detail. '*150
        store.edit_summary_statement(statement['id'],longer)
        assert store.summary_statements(sid)[0]['content']==longer.strip()
        assert store.integrity_ok()


@pytest.mark.parametrize("changed", [False, True])
def test_long_edited_summary_chunks_resume_and_preserve_correction(tmp_path, changed):
    with MemoryStore(tmp_path / "edited.sqlite3") as store:
        _, record = setup_record(store)
        source = store.record_turns(record)[0]
        for order in range(2, 41):
            store.append_turn(record, source.model_copy(update={"display_order": order, "content": "We discussed a project milestone and its next steps. " * 40}))
        summary = draft(store, record)
        statement = store.summary_statements(summary)[0]
        # Model-generated fixtures retain evidence across the long call.
        with store.transaction() as db:
            db.executemany("INSERT INTO summary_evidence VALUES (?,?,?)", [(statement["id"], record, i) for i in range(2, 41)])
        edited = store.edit_review_summary(summary, "The appointment is Wednesday at 3 PM.", expected_statements={statement["id"]: (statement["content"], 0)})
        seen = []
        def parse(**kwargs):
            payload = json.loads(kwargs["input"])
            ids = [t["id"] for t in payload["source_context"]["turns"]]
            seen.append(ids)
            if len(seen) == 2:
                raise TimeoutError("fixture interruption")
            return SimpleNamespace(output_parsed=ExtractionOutput(), usage=SimpleNamespace(input_tokens=100, output_tokens=10))
        client = SimpleNamespace(responses=SimpleNamespace(parse=parse))
        ledger = UsageLedger.product()
        with pytest.raises(TimeoutError):
            process_review(store, record, ledger=ledger, client=client)
        assert store.retryable_batch(record) is None  # Normal transcript extraction must not resume an edit batch.
        if changed:
            # A changed visible source must not reuse another payload's chunk offsets.
            with store.transaction() as db:
                db.execute("UPDATE summary_statements SET content=content || ' Please remember.' WHERE summary_id=?", (edited,))
        assert process_review(store, record, ledger=ledger, client=client) == edited
        assert seen.count(seen[0]) == (2 if changed else 1)
        assert store._connection.execute("SELECT count(*) FROM proposal_batches WHERE record_id=?", (record,)).fetchone()[0] == (2 if changed else 1)
        assert set(i for chunk in seen for i in chunk) == set(range(1, 41))
        assert len(seen) > 2
        assert store.summary_statements(edited)[0]["content"].startswith("The appointment is Wednesday at 3 PM.")


def test_legacy_rejection_does_not_hide_explicit_edit_and_deleted_siblings_are_erased(tmp_path):
    with MemoryStore(tmp_path / "legacy.sqlite3") as store:
        _, record = setup_record(store)
        summary = draft(store, record)
        row = store.summary_statements(summary)[0]
        batch = store.create_batch(record, model="fake", reasoning="none")
        ids = store.store_proposals(batch, [MemoryProposalInput(content=text, memory_type="other", confidence="high", evidence_turns=[1]) for text in ("Legacy rejection", "Appointment", "Appointment paraphrase")])
        store.reject_proposal(ids[0])
        edited = store.edit_review_summary(summary, "Dentist appointment Wednesday.", expected_statements={row["id"]: (row["content"], 0)})
        assert all(not s["excluded"] for s in store.summary_statements(edited))
        batch = store.create_batch(record, model="fake", reasoning="none")
        ids = store.store_proposals(batch, [MemoryProposalInput(content=text, memory_type="other", confidence="high", evidence_turns=[1]) for text in ("Appointment", "Appointment paraphrase")])
        approved = store.approve_proposal(ids[0])
        store.delete_memory(approved)
        assert not store._connection.execute("SELECT 1 FROM memory_proposals WHERE id=?", (ids[1],)).fetchone()
        assert store.review_record_proposals(record, None, approve=True, expected_pending={}) == ()


def test_emptied_edited_summary_can_regenerate_from_remaining_source(tmp_path):
    with MemoryStore(tmp_path / "remaining.sqlite3") as store:
        contact, record = setup_record(store)
        source = store.record_turns(record)[0]
        store.append_turn(record, source.model_copy(update={"display_order": 2, "content": "I prefer mint tea."}))
        summary = draft(store, record)
        row = store.summary_statements(summary)[0]
        approved = store.create_memory(contact, "Appointment", record_id=record, evidence_turns=[1])
        edited = store.edit_review_summary(summary, "Appointment Wednesday.", expected_statements={row["id"]: (row["content"], 0)})
        store.delete_memory(approved)
        assert not store.summary_statements(edited)
        batch = store.create_batch(record, model="fake", reasoning="none")
        assert store.store_proposals(batch, [MemoryProposalInput(content="Appointment", memory_type="other", confidence="high", evidence_turns=[2])]) == []
        def parse(**kwargs):
            payload = json.loads(kwargs["input"])
            assert [t["id"] for t in payload["turns"]] == [2]
            return SimpleNamespace(output_parsed=SummaryOutput(statements=[SummaryStatementInput(section="discussed", content="Prefers mint tea.", kind="fact", confidence="high", evidence_turns=[2])]), usage=SimpleNamespace(input_tokens=100, output_tokens=20))
        regenerated = process_review(store, record, ledger=UsageLedger.product(), client=SimpleNamespace(responses=SimpleNamespace(parse=parse)))
        assert regenerated != edited
        assert store.summary_statements(regenerated)[0]["content"] == "Prefers mint tea."


def test_sensitive_generated_topic_survives_consolidation_with_automatic_cloud_eligibility(tmp_path, monkeypatch):
    monkeypatch.setattr("conversation_copilot.post_call._whole_summary_fits", lambda turns: False)
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        _, record = setup_record(store)
        source = store.record_turns(record)[0]
        for order in range(2, 42):
            store.append_turn(record, source.model_copy(update={"display_order": order, "content": f"Project milestone {order} is complete."}))
        def parse(**kwargs):
            payload = json.loads(kwargs['input'])
            if 'turns' in payload:
                turn = payload['turns'][0]
                statements = [SummaryStatementInput(section='discussed', content=turn['text'], kind='fact',
                    confidence='high', evidence_turns=[turn['id']], sensitivity='sensitive' if turn['id']==1 else 'normal')]
            else:
                assert any(1 in item['evidence_turns'] for item in payload['draft_statements'])
                statements = [SummaryStatementInput(**{**item, 'confidence':'high',
                    'sensitivity':'sensitive' if 1 in item['evidence_turns'] else 'normal'}) for item in payload['draft_statements']]
            return SimpleNamespace(output_parsed=SummaryOutput(statements=statements), usage=SimpleNamespace(input_tokens=100, output_tokens=100))
        summary = process_review(store, record, ledger=UsageLedger(), extractor=FakeMemoryExtractor([ExtractionOutput() for _ in range(3)]),
            client=SimpleNamespace(responses=SimpleNamespace(parse=parse)))
        statements = store.summary_statements(summary)
        assert len(statements) == 3 and any('dentist' in item['content'] for item in statements)
        assert not store._connection.execute('SELECT partial FROM summary_versions WHERE id=?', (summary,)).fetchone()[0]
        sensitive = next(item for item in statements if item['sensitivity']=='sensitive')
        assert not sensitive['cloud_allowed']
        token = store._connection.execute('SELECT created_at FROM review_jobs WHERE record_id=?', (record,)).fetchone()[0]
        assert store._summary_eligible(sensitive['id'], for_cloud=True, require_approved=False, review_token=token)
        with store.transaction() as db:
            db.execute("UPDATE review_jobs SET state='running' WHERE record_id=?", (record,))
        assert store._summary_eligible(sensitive['id'], for_cloud=True, require_approved=False, review_token=token)
        assert store._summary_eligible(sensitive['id'], for_cloud=True, require_approved=False, review_token='wrong-job')
        store.set_summary_cloud_permission(sensitive['id'], False)
        assert store._summary_eligible(sensitive['id'], for_cloud=True, require_approved=False, review_token=token)


def test_general_summary_preserves_specific_transcript_memory(tmp_path):
    with MemoryStore(tmp_path / 'memory.sqlite3') as store:
        _, record = setup_record(store)
        detail = store.record_turns(record)[0].content
        batch = store.create_batch(record, model='fake', reasoning='none')
        proposal = store.store_proposals(batch, [MemoryProposalInput(content=detail, memory_type='event_date',
            confidence='high', evidence_turns=[1])])[0]
        general = 'Yaheli discussed an upcoming appointment.'
        summary = store.create_summary_draft(record, SummaryOutput(statements=[SummaryStatementInput(
            section='discussed',content=general,kind='fact',confidence='high',evidence_turns=[1])]),expected_generation=1)
        assert store.summary_statements(summary)[0]['content'] == general
        row = store._connection.execute('SELECT content,state FROM memory_proposals WHERE id=?',(proposal,)).fetchone()
        assert row['content'] == detail and row['state'] == 'pending'


def test_linked_edits_and_joint_approval_are_atomic_and_keep_unrelated_pending(tmp_path):
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        contact, record = setup_record(store)
        turn = store.record_turns(record)[0]
        store.append_turn(record, turn.model_copy(update={"display_order": 2, "content": "I like tea."}))
        batch = store.create_batch(record, model="fake", reasoning="none")
        linked, unrelated = store.store_proposals(batch, [
            MemoryProposalInput(content="Dentist at 3 PM", memory_type="event_date", confidence="high", evidence_turns=[1]),
            MemoryProposalInput(content="Likes tea", memory_type="preference", confidence="high", evidence_turns=[2])])
        summary = draft(store, record)
        sentence = store.summary_statements(summary)[0]
        store.edit_review_sentence(sentence["id"], "Dentist at 4 PM", expected_content=sentence["content"], links={linked: "Dentist at 3 PM"})
        proposal = store._connection.execute("SELECT * FROM memory_proposals WHERE id=?", (linked,)).fetchone()
        assert proposal["state"] == "pending" and proposal["content"] == "Dentist at 4 PM"
        with pytest.raises(ValueError):
            store.edit_review_sentence(sentence["id"], "Dentist at 9 PM", expected_content="Dentist at 4 PM", links={linked: "stale"})
        assert store.summary_statements(summary)[0]["content"] == "Dentist at 4 PM"
        store.edit_pending_review_memory(linked, "Dentist at 5 PM", expected_content="Dentist at 4 PM", summary_ids=[sentence["id"]])
        assert store.summary_statements(summary)[0]["content"] == "Dentist at 5 PM"
        store.approve_summary(summary)
        approved = store._connection.execute("SELECT * FROM memory_proposals WHERE id=?", (linked,)).fetchone()
        assert approved["state"] == "approved"
        assert store._connection.execute("SELECT state FROM memory_proposals WHERE id=?", (unrelated,)).fetchone()[0] == "pending"
        memory_id = approved["approved_memory_id"]
        assert store.current_revision(memory_id)["author_origin"] == "user_corrected"
        store.correct_memory(memory_id, "Dentist at 6 PM", summary_choices={sentence["id"]: "update"})
        assert store.summary_statements(summary)[0]["content"] == "Dentist at 6 PM"
        store.edit_review_sentence(sentence["id"], "Dentist at 7 PM", expected_content="Dentist at 6 PM", links={memory_id: store.current_revision(memory_id)["id"]})
        assert store.current_revision(memory_id)["content"] == "Dentist at 7 PM"


def test_joint_approval_rolls_back_all_memories_on_failure(tmp_path, monkeypatch):
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        contact, record = setup_record(store)
        batch = store.create_batch(record, model="fake", reasoning="none")
        ids = store.store_proposals(batch, [MemoryProposalInput(content=text, memory_type="event_date", confidence="high", evidence_turns=[1]) for text in ("Dentist Tuesday", "Dentist at 3 PM")])
        summary = draft(store, record)
        approve = store._approve_proposal
        calls = []
        def fail_second(db, proposal_id, edited_content=None, **kwargs):
            calls.append(proposal_id)
            if len(calls) == 2:
                raise ValueError("fixture source changed")
            return approve(db, proposal_id, edited_content, **kwargs)
        monkeypatch.setattr(store, "_approve_proposal", fail_second)
        with pytest.raises(ValueError, match="fixture source changed"):
            store.approve_summary(summary)
        assert not store.list_current_memories(contact)
        assert all(store._connection.execute("SELECT state FROM memory_proposals WHERE id=?", (pid,)).fetchone()[0] == "pending" for pid in ids)
        assert store._connection.execute("SELECT state FROM summary_versions WHERE id=?", (summary,)).fetchone()[0] == "draft"


def test_unrelated_deletion_preserves_releasable_quarantined_summary(tmp_path):
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        _, record = setup_record(store)
        summary = draft(store, record)
        statement = store.summary_statements(summary)[0]["id"]
        store.edit_summary_statement(statement, "Dentist appointment corrected to 4 PM.")
        store.approve_summary(summary)
        with store.transaction() as db:
            db.execute("INSERT INTO summary_exclusions VALUES (?,0,'legacy_deletion','old-tombstone','test')", (record,))
        other = store.create_contact("Other fictional contact")
        memory = store.create_memory(other.id, "Unrelated note")
        store.delete_memory(memory)
        assert store.summary_statements(summary)[0]["content"] == "Dentist appointment corrected to 4 PM."
        store.review_legacy_summary_turns(record, {1}, expected_generation=1)
        assert store._summary_eligible(statement)


def test_post_call_pauses_between_chunks_and_resumes_checkpoint(tmp_path, monkeypatch):
    monkeypatch.setattr("conversation_copilot.post_call._whole_summary_fits", lambda turns: False)
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        _, record = setup_record(store)
        turn = store.record_turns(record)[0]
        for sequence in range(2, 22):
            store.append_turn(record, turn.model_copy(update={"display_order": sequence}))
        paused = [False]
        save = store.create_summary_draft
        def checkpoint(*args, **kwargs):
            result = save(*args, **kwargs)
            paused[0] = True
            return result
        monkeypatch.setattr(store, "create_summary_draft", checkpoint)
        client = SimpleNamespace(responses=SimpleNamespace(parse=lambda **kwargs: SimpleNamespace(
            output_parsed=SummaryOutput(), usage=SimpleNamespace(input_tokens=100, output_tokens=40))))
        extractor = FakeMemoryExtractor([ExtractionOutput(), ExtractionOutput()])
        with pytest.raises(ValueError, match="paused"):
            process_review(store, record, ledger=UsageLedger(), client=client, extractor=extractor, can_run=lambda: not paused[0])
        assert store._connection.execute("SELECT count(*) FROM review_chunks").fetchone()[0] == 1
        assert store._connection.execute("SELECT state FROM review_jobs").fetchone()[0] == "pending"
        assert store.summary_for_review(record) is None
        checkpoint = store._connection.execute('SELECT summary_id FROM review_chunks').fetchone()[0]
        with pytest.raises(ValueError, match='unfinished'):
            store.approve_summary(checkpoint)
        extraction_calls = len(extractor.calls)
        monkeypatch.setattr(store, "create_summary_draft", save)
        process_review(store, record, ledger=UsageLedger(), client=client, extractor=extractor)
        assert len(extractor.calls) == extraction_calls
        assert store._connection.execute("SELECT state FROM review_jobs").fetchone()[0] == "complete"


@pytest.mark.parametrize("target", ["summary", "source", "contact"])
def test_parent_deletion_scrubs_approved_summary_fts(tmp_path, target):
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        contact, record = setup_record(store)
        store.approve_summary(draft(store, record))
        assert store._connection.execute("SELECT count(*) FROM summary_search").fetchone()[0] == 1
        {"summary": lambda: store.delete_summary(record), "source": lambda: store.delete_source(record),
         "contact": lambda: store.delete_contact(contact)}[target]()
        assert store._connection.execute("SELECT count(*) FROM summary_search").fetchone()[0] == 0


def test_pending_review_allows_correction_and_closes_model_checkpoint(tmp_path):
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        _, record = setup_record(store)
        summary = draft(store, record)
        statement = store.summary_statements(summary)[0]["id"]
        with store.transaction() as db:
            db.execute("INSERT INTO review_jobs(record_id,generation,state,created_at) VALUES (?,1,'pending','test')", (record,))
        store.edit_summary_statement(statement, "Corrected appointment time is 4 PM.")
        assert store.summary_statements(summary)[0]["origin"] == "user_corrected"
        assert store._connection.execute("SELECT state FROM review_jobs").fetchone()[0] == "complete"
        store.edit_summary_statement(statement, "Corrected appointment time is 4 PM.", excluded=True)
        store.approve_summary(summary)
        assert not store._connection.execute("SELECT 1 FROM summary_search").fetchone()


def test_proposal_approval_reindexes_relinked_approved_summary(tmp_path):
    from conversation_copilot.ask_memory import summary_source, AskSession
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        contact, record = setup_record(store)
        summary = draft(store, record)
        statement = store.summary_statements(summary)[0]["id"]
        store.approve_summary(summary)
        batch = store.create_batch(record, model="fake", reasoning="none")
        proposal = store.store_proposals(batch, [MemoryProposalInput(content="Dentist appointment at 3 PM",
            memory_type="event_date", confidence="high", sensitivity="sensitive", evidence_turns=[1])])[0]
        store.approve_proposal(proposal)
        assert store._connection.execute("SELECT count(*) FROM summary_search WHERE statement_id=?", (statement,)).fetchone()[0] == 1
        source = summary_source(store, statement, contact)
        assert source and source.cloud_allowed
        result = AskSession(contact).answer(store, "Cedar Clinic", semantic=False)
        assert any(item.id == statement for item in result.sources)


def test_summary_correction_deletion_and_regeneration(tmp_path):
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        contact, record = setup_record(store)
        memory = store.create_memory(contact, "Dentist appointment Tuesday at 3 PM", record_id=record, evidence_turns=[1])
        summary = draft(store, record)
        statement = store.summary_statements(summary)[0]["id"]
        assert not store._summary_eligible(statement)
        store.approve_summary(summary)
        assert store._summary_eligible(statement)
        original = store.current_revision(memory)["id"]
        with pytest.raises(ValueError, match="Keep or Remove"):
            store.correct_memory(memory, "Dentist appointment Tuesday at 4 PM")
        assert store.current_revision(memory)["id"] == original
        revision = store.correct_memory(memory, "Dentist appointment Tuesday at 4 PM", summary_choices={statement: "keep"})
        assert store.summary_statements(summary)[0]["kind"] == "historical"
        assert store._connection.execute("SELECT correction_revision_id FROM summary_dependencies").fetchone()[0] == revision
        assert store._summary_eligible(statement)
        second = draft(store, record)
        store.delete_memory(memory)
        assert not store.summary_statements(summary)
        assert not store.summary_statements(second)
        assert not store.summary_turns(record)
        assert store.record_turns(record)
        with pytest.raises(ValueError, match="excluded"):
            draft(store, record)
        assert not store._connection.execute("SELECT * FROM summary_search").fetchall()
        store.validate_export(store.export_json(contact_id=contact))
        assert store.integrity_ok()


def test_unchanged_keep_remove_permissions_and_source_cascade(tmp_path):
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        contact, record = setup_record(store)
        memory = store.create_memory(contact, "Dentist at 3 PM", sensitivity="sensitive", record_id=record, evidence_turns=[1])
        summary = draft(store, record)
        statement = store.summary_statements(summary)[0]["id"]
        store.approve_summary(summary)
        store.correct_memory(memory, "Dentist at 3 PM", summary_choices={statement: "keep"})
        assert store.summary_statements(summary)[0]["kind"] == "fact"
        assert store.summary_turns(record, for_cloud=True)
        store.set_summary_cloud_permission(statement, True)
        assert store._summary_eligible(statement, for_cloud=True)
        store.set_cloud_permission(memory, True)
        assert store._summary_eligible(statement, for_cloud=True)
        store.set_cloud_permission(memory, False)
        assert store._summary_eligible(statement, for_cloud=True)
        store.correct_memory(memory, "Dentist at 4 PM", summary_choices={statement: "remove"})
        assert not store._summary_eligible(statement)
        store.delete_source(record, keep_memory_ids=[memory])
        assert not store.summary_statements(summary)
        assert store.current_revision(memory)
        assert store.integrity_ok()


def test_v3_legacy_deletion_quarantine_and_transactional_migration_restore(tmp_path):
    path = tmp_path / "legacy.sqlite3"
    db = sqlite3.connect(path)
    for sql in _SCHEMA:
        db.execute(sql)
    db.execute("INSERT INTO contacts VALUES ('c','Yaheli',NULL,NULL,'2026-09-01','2026-09-01')")
    db.execute("INSERT INTO memories(id,contact_id,deleted_at,created_at) VALUES ('gone','c','2026-09-02','2026-09-01')")
    db.execute("""INSERT INTO conversation_records VALUES
        ('r','c','call','fictional',NULL,NULL,'Asia/Jerusalem','stopped','pending',1,'2026-09-01')""")
    db.execute("INSERT INTO conversation_turns VALUES ('r',1,'selected_contact','Yaheli','Dentist at 3 PM',NULL,NULL,NULL)")
    db.execute("PRAGMA user_version=3")
    db.commit()
    original = list(db.iterdump())
    db.close()
    def fail(_db):
        raise RuntimeError("injected migration failure")
    with pytest.raises(MemoryStoreUnavailable):
        MemoryStore(path, migration_hook=fail)
    with sqlite3.connect(path) as restored:
        assert list(restored.iterdump()) == original
        assert restored.execute("PRAGMA user_version").fetchone()[0] == 3
    with MemoryStore(path) as store:
        assert not store.summary_turns("r")
        assert store.record_turns("r")
        assert store._connection.execute("SELECT reason FROM summary_exclusions").fetchone()[0] == "legacy_deletion"
        store.create_memory("c", "Current user-authored note")
        assert store.retrieve("c", "user-authored note").matches
        assert store.integrity_ok()


def test_rejected_memory_stays_rejected_after_summary_approval_and_restoration(tmp_path):
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        contact, record = setup_record(store)
        batch = store.create_batch(record, model="fake", reasoning="none")
        proposal = store.store_proposals(batch, [MemoryProposalInput(content="Dentist at 3 PM", memory_type="event_date", confidence="high", evidence_turns=[1])])[0]
        summary = draft(store, record)
        statement = store.summary_statements(summary)[0]["id"]
        store.reject_proposal(proposal)
        assert not store._summary_eligible(statement)
        store.approve_summary(summary)
        assert not store._summary_eligible(statement)
        store.edit_summary_statement(statement, store.summary_statements(summary)[0]["content"], excluded=False)
        assert store._summary_eligible(statement)
        assert store._connection.execute("SELECT state FROM memory_proposals WHERE id=?", (proposal,)).fetchone()[0] == "rejected"
        another = draft(store, record)
        assert store.summary_statements(another)[0]["excluded"]


def test_post_call_failure_resume_and_regeneration_do_not_repeat_extraction(tmp_path):
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        contact, record = setup_record(store)
        extractor = FakeMemoryExtractor([ExtractionOutput()])
        output = SummaryOutput(statements=[SummaryStatementInput(section="plans", content="Dentist at 3 PM", kind="fact", confidence="high", evidence_turns=[1])])
        calls = []
        def parse(**kwargs):
            calls.append(kwargs)
            if len(calls) == 1:
                raise TimeoutError("fictional uncertain billing")
            return SimpleNamespace(output_parsed=output, usage=SimpleNamespace(input_tokens=100, output_tokens=40))
        client = SimpleNamespace(responses=SimpleNamespace(parse=parse))
        ledger = UsageLedger.product()  # Mocked transport; this test checks resume, not the evaluation cap.
        with pytest.raises(TimeoutError):
            process_review(store, record, ledger=ledger, client=client, extractor=extractor)
        assert len(extractor.calls) == 1 and ledger.total_dollars > 0
        summary = process_review(store, record, ledger=ledger, client=client, extractor=extractor)
        assert len(extractor.calls) == 1
        store.approve_summary(summary)
        regenerated = process_review(store, record, ledger=ledger, client=client, extractor=extractor)
        assert regenerated != summary
        assert len(extractor.calls) == 1
        assert store._connection.execute("SELECT state FROM summary_versions WHERE id=?", (summary,)).fetchone()[0] == "approved"
        assert store._connection.execute("SELECT state FROM summary_versions WHERE id=?", (regenerated,)).fetchone()[0] == "draft"


def test_delete_summary_during_request_is_refused(tmp_path):
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        _, record = setup_record(store)
        def parse(**kwargs):
            with pytest.raises(ValueError, match="generation"):
                store.delete_summary(record)
            return SimpleNamespace(output_parsed=SummaryOutput(), usage=SimpleNamespace(input_tokens=100, output_tokens=40))
        process_review(store, record, ledger=UsageLedger(), extractor=FakeMemoryExtractor([ExtractionOutput()]),
                       client=SimpleNamespace(responses=SimpleNamespace(parse=parse)))
        assert store._connection.execute("SELECT 1 FROM summary_versions").fetchone()
        assert store._connection.execute("SELECT state FROM review_jobs").fetchone()[0] == "complete"
        assert store.integrity_ok()


def test_long_review_reuses_chunks_and_persists_usage(tmp_path, monkeypatch):
    monkeypatch.setattr("conversation_copilot.post_call._whole_summary_fits", lambda turns: False)
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        contact = store.create_contact("Yaheli")
        record = store.create_record(source_kind="call", source_label="fictional long review", contact_id=contact.id, status="stopped",
            timezone_name="Asia/Jerusalem", turns=[ConversationTurn(speaker_name="Yaheli", speaker_role=SpeakerRole.SELECTED_CONTACT,
                source="fixture", content=f"Plan item {i} needs a reminder.", display_order=i,
                timestamp=datetime(2026, 9, 7, 12, tzinfo=timezone.utc)) for i in range(1, 42)])
        extractor = FakeMemoryExtractor([ExtractionOutput()] * 3)
        calls = []
        def parse(**kwargs):
            payload = json.loads(kwargs["input"])
            calls.append(payload)
            if len(calls) == 2:
                raise TimeoutError("interrupted second chunk")
            ids = [row["id"] for row in payload["turns"]] if "turns" in payload else [t for s in payload["draft_statements"] for t in s["evidence_turns"]]
            output = SummaryOutput(statements=[SummaryStatementInput(section="follow_ups", content="A plan item needs a reminder.",
                kind="fact", confidence="high", evidence_turns=ids[:1])], partial=True)
            return SimpleNamespace(output_parsed=output, usage=SimpleNamespace(input_tokens=100, output_tokens=50))
        client = SimpleNamespace(responses=SimpleNamespace(parse=parse))
        ledger = UsageLedger.product()  # Mocked transport; retain uncertain charges while testing resume.
        with pytest.raises(TimeoutError):
            process_review(store, record, ledger=ledger, extractor=extractor, client=client)
        summary = process_review(store, record, ledger=ledger, extractor=extractor, client=client)
        assert len(extractor.calls) == 1 and len(calls) == 6
        assert sum("turns" in item and item["turns"][0]["id"] == 1 for item in calls) == 1
        assert store._connection.execute("SELECT partial FROM summary_versions WHERE id=?", (summary,)).fetchone()[0]
        usage = json.loads(store._connection.execute("SELECT usage_json FROM review_jobs WHERE record_id=?", (record,)).fetchone()[0])
        assert len(usage) == 6 and sum(item["dollars"] for item in usage) == pytest.approx(ledger.total_dollars)
        assert store.integrity_ok()
