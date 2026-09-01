import json
import sqlite3
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
import numpy as np

from conversation_copilot.memory import (
    AmbiguousContact,
    ExtractionOutput,
    FakeMemoryExtractor,
    MemoryProposalInput,
    MemoryStore,
    MemoryStoreUnavailable,
    OpenAIMemoryExtractor,
    SCHEMA_VERSION,
    analyze_record,
    extraction_chunks,
    extraction_maximum_cost,
    extraction_reservation_tokens,
)
from conversation_copilot.interpretation import (
    BudgetLimits,
    InterpretationModelOutputInvalid,
    InterpretationUnavailable,
    UsageLedger,
    conservative_request_cost,
)
import conversation_copilot.memory as memory_module
import conversation_copilot.semantic as semantic_module
from conversation_copilot.models import ConversationTurn, SpeakerRole


def turn(order: int, role: SpeakerRole, content: str) -> ConversationTurn:
    return ConversationTurn(
        speaker_name="You" if role is SpeakerRole.USER else "Alex",
        speaker_role=role,
        source="fixture",
        content=content,
        timestamp=datetime(2026, 8, 18, 12, tzinfo=timezone.utc) + timedelta(seconds=order),
        display_order=order,
    )


def record(store: MemoryStore, contact_id: str | None, count: int = 2) -> str:
    turns = [
        turn(index, SpeakerRole.USER if index % 2 else SpeakerRole.SELECTED_CONTACT, f"line {index}")
        for index in range(1, count + 1)
    ]
    return store.create_record(
        source_kind="call", source_label="fictional WhatsApp call", timezone_name="Asia/Jerusalem",
        contact_id=contact_id, turns=turns, status="stopped",
    )


def test_schema_reopen_foreign_keys_rollback_and_corruption(tmp_path):
    path = tmp_path / "memory.sqlite3"
    with MemoryStore(path) as store:
        contact = store.create_contact("Alex")
        assert store.integrity_ok()
        assert store._connection.execute("PRAGMA user_version").fetchone()[0] == SCHEMA_VERSION
        assert store._connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        with pytest.raises(sqlite3.IntegrityError):
            with store.transaction() as db:
                db.execute(
                    "INSERT INTO contact_aliases(id,contact_id,spelling,normalized,origin) VALUES ('bad','missing','Bad','bad','user')"
                )
        assert store.get_contact(contact.id).display_name == "Alex"

    with MemoryStore(path) as reopened:
        assert reopened.get_contact(contact.id).display_name == "Alex"

    missing = tmp_path / "missing.sqlite3"
    with pytest.raises(MemoryStoreUnavailable, match="existing verified"):
        MemoryStore(missing, verify=False)
    assert not missing.exists()

    path.write_bytes(b"not sqlite")
    with pytest.raises(MemoryStoreUnavailable):
        MemoryStore(path)
    assert path.read_bytes() == b"not sqlite"


def test_current_database_open_runs_one_integrity_scan(tmp_path, monkeypatch):
    path = tmp_path / "memory.sqlite3"
    with MemoryStore(path):
        pass
    original = MemoryStore._verify_database
    calls = []

    def counted(connection, *, allow_uninitialized=False):
        calls.append(allow_uninitialized)
        return original(connection, allow_uninitialized=allow_uninitialized)

    monkeypatch.setattr(MemoryStore, "_verify_database", staticmethod(counted))
    with MemoryStore(path):
        pass
    assert calls == [True]


def test_version_one_migrates_to_semantic_table_with_backup_cleanup(tmp_path):
    path = tmp_path / "memory.sqlite3"
    with MemoryStore(path) as store:
        contact = store.create_contact("Alex")
    old = sqlite3.connect(path)
    old.execute("DROP TABLE memory_embeddings")
    old.execute("PRAGMA user_version = 1")
    old.commit()
    old.close()

    with MemoryStore(path) as migrated:
        assert migrated.get_contact(contact.id).display_name == "Alex"
        assert migrated._connection.execute("PRAGMA user_version").fetchone()[0] == SCHEMA_VERSION
        assert migrated._connection.execute(
            "SELECT name FROM sqlite_master WHERE name='memory_embeddings'"
        ).fetchone()
    assert not path.with_suffix(".sqlite3.migration-backup").exists()


def test_semantic_candidates_are_contact_first_and_embeddings_follow_lifecycle(
    tmp_path, monkeypatch
):
    def fake_vectors(texts, _cache_dir):
        vectors = np.zeros((len(texts), 384), dtype=np.float32)
        for index, text in enumerate(texts):
            lowered = text.casefold()
            axis = 0 if any(
                phrase in lowered
                for phrase in ("lost their job", "let me go", "need to make money", "new role", "getting used")
            ) else 1
            vectors[index, axis] = 1
        return vectors

    monkeypatch.setattr(semantic_module, "embed_texts_if_ready", fake_vectors)
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        selected = store.create_contact("Test Contact")
        other = store.create_contact("Other Contact")
        job = store.create_memory(selected.id, "Test Contact lost their job recently", memory_type="event_date")
        store.create_memory(other.id, "Other Contact lost their job recently", memory_type="event_date")
        assert store.backfill_semantic_embeddings() == 2

        result = store.retrieve(
            selected.id,
            "They let me go and now I need to make money",
            semantic_query="They let me go and now I need to make money",
        )
        assert result.semantic_available is True
        assert [item.memory_id for item in result.matches] == [job]
        assert result.matches[0].reason == "semantic"
        assert store._connection.execute("SELECT count(*) FROM memory_embeddings").fetchone()[0] == 2

        old_revision = store.current_revision(job)["id"]
        store.correct_memory(job, "Test Contact is getting used to a new role")
        assert store._connection.execute(
            "SELECT count(*) FROM memory_embeddings WHERE revision_id=?", (old_revision,)
        ).fetchone()[0] == 0
        assert store.backfill_semantic_embeddings() == 1
        store.retrieve(selected.id, "I am getting used to it", semantic_query="I am getting used to it")
        assert store._connection.execute("SELECT count(*) FROM memory_embeddings").fetchone()[0] == 2
        store.delete_memory(job)
        assert store._connection.execute("SELECT count(*) FROM memory_embeddings").fetchone()[0] == 1


def test_retrieve_rechecks_deletion_before_emitting_a_semantic_candidate(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(
        semantic_module,
        "embed_texts_if_ready",
        lambda texts, _cache: np.pad(
            np.ones((len(texts), 1), dtype=np.float32), ((0, 0), (0, 383))
        ),
    )
    path = tmp_path / "memory.sqlite3"
    with MemoryStore(path) as store:
        contact = store.create_contact("Test Contact")
        memory_id = store.create_memory(
            contact.id, "Test Contact moved apartment", memory_type="event_date"
        )
        store.backfill_semantic_embeddings()
        original = store._semantic_candidates
        deleted = False

        def delete_after_candidates(query, eligible_sql, params):
            nonlocal deleted
            result = original(query, eligible_sql, params)
            if result[0] and not deleted:
                with MemoryStore(path, verify=False) as writer:
                    writer.delete_memory(memory_id)
                deleted = True
            return result

        monkeypatch.setattr(store, "_semantic_candidates", delete_after_candidates)
        result = store.retrieve(
            contact.id,
            "carrying everything upstairs",
            semantic_query="carrying everything upstairs",
        )

        assert deleted is True
        assert result.matches == ()


def test_semantic_scoring_reaches_an_old_memory_past_twelve_newer_items(
    tmp_path, monkeypatch
):
    def fake_vectors(texts, _cache_dir):
        vectors = np.zeros((len(texts), 384), dtype=np.float32)
        for index, text in enumerate(texts):
            vectors[index, 0 if "employment" in text.casefold() else 1] = 1
        return vectors

    monkeypatch.setattr(semantic_module, "embed_texts_if_ready", fake_vectors)
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        contact = store.create_contact("Test Contact")
        target = store.create_memory(
            contact.id,
            "Test Contact experienced an employment loss",
            memory_type="event_date",
        )
        for index in range(13):
            store.create_memory(
                contact.id,
                f"Test Contact likes fixture topic {index}",
                memory_type="preference",
            )
        assert store.backfill_semantic_embeddings() == 14

        result = store.retrieve(
            contact.id,
            "They let me go and I need to find income",
            semantic_query="indirect employment uncertainty",
        )

        assert [item.memory_id for item in result.matches] == [target]


def test_semantic_query_skips_model_when_contact_has_no_stored_vectors(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(
        semantic_module,
        "embed_texts_if_ready",
        lambda *_args: (_ for _ in ()).throw(AssertionError("model should not load")),
    )
    monkeypatch.setattr(semantic_module, "model_ready", lambda _cache: False)
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        contact = store.create_contact("Test Contact")
        store.create_memory(contact.id, "Test Contact likes tea", memory_type="preference")

        result = store.retrieve(
            contact.id,
            "Would they like a warm drink?",
            semantic_query="Would they like a warm drink?",
        )

        assert result.matches == ()
        assert result.semantic_available is False


def test_missing_semantic_model_keeps_reduced_recall_safe(tmp_path, monkeypatch):
    monkeypatch.setattr(semantic_module, "embed_texts_if_ready", lambda _texts, _cache: None)
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        contact = store.create_contact("Test Contact")
        store.create_memory(contact.id, "Test Contact lost their job recently", memory_type="event_date")
        result = store.retrieve(
            contact.id,
            "They let me go and I need to make money",
            semantic_query="They let me go and I need to make money",
        )
        assert result.matches == ()
        assert result.semantic_available is False


def test_verified_reopen_makes_interrupted_analysis_retryable(tmp_path):
    path = tmp_path / "memory.sqlite3"
    with MemoryStore(path) as store:
        contact = store.create_contact("Alex")
        record_id = record(store, contact.id)
        batch_id = store.create_batch(record_id, model="fake", reasoning="none")
        interrupted_call = store.create_record(
            source_kind="call", source_label="crashed call", timezone_name="UTC",
            contact_id=contact.id, status="active",
        )
        interrupted_unassigned = store.create_record(
            source_kind="call", source_label="crashed unassigned call", timezone_name="UTC",
            status="active",
        )

    with MemoryStore(path, verify=False) as worker:
        assert worker.list_records(contact.id)[0]["analysis_state"] == "running"
        assert all(row["id"] != interrupted_call for row in worker.list_records(contact.id))
        assert all(row["id"] != interrupted_unassigned for row in worker.list_unassigned())

    with MemoryStore(path) as reopened:
        records = {row["id"]: row for row in reopened.list_records(contact.id)}
        assert records[record_id]["analysis_state"] == "failed"
        assert records[interrupted_call]["status"] == "stopped"
        assert records[interrupted_call]["analysis_state"] == "pending"
        unassigned = {row["id"]: row for row in reopened.list_unassigned()}
        assert interrupted_unassigned in unassigned
        assert reopened.batch_progress(batch_id)[2] == "failed"
        assert reopened.retryable_batch(record_id) == batch_id
        reopened.delete_source(interrupted_unassigned)
        reopened.delete_contact(contact.id)
        assert reopened.list_contacts() == []


def test_failed_migration_restores_original_and_retains_backup(tmp_path):
    path = tmp_path / "old.sqlite3"
    connection = sqlite3.connect(path)
    connection.execute("CREATE TABLE legacy(value TEXT)")
    connection.execute("INSERT INTO legacy VALUES ('preserved')")
    connection.commit()
    connection.close()

    def fail(_db):
        raise RuntimeError("injected migration failure")

    with pytest.raises(MemoryStoreUnavailable):
        MemoryStore(path, migration_hook=fail)
    backup = path.with_suffix(".sqlite3.migration-backup")
    assert backup.exists()
    restored = sqlite3.connect(path)
    assert restored.execute("SELECT value FROM legacy").fetchone()[0] == "preserved"
    assert restored.execute("PRAGMA user_version").fetchone()[0] == 0
    restored.close()


def test_contacts_alias_ambiguity_assignment_and_merge_rollback(tmp_path):
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        alex_friend = store.create_contact("Alex", "friend", aliases=[("Al", "nickname")])
        alex_work = store.create_contact("Alex", "work", aliases=[("Al", "nickname")])
        eitan = store.create_contact("Eitan", aliases=[("Sommer", "nickname")])
        with pytest.raises(AmbiguousContact) as error:
            store.resolve_contact("Al")
        assert {item.id for item in error.value.candidates} == {alex_friend.id, alex_work.id}
        assert store.resolve_contact("Sommer").id == eitan.id
        store.add_alias(eitan.id, "Eiti")
        added = next(item for item in store.list_aliases(eitan.id) if item["spelling"] == "Eiti")
        store.remove_alias(added["id"])
        assert all(item["spelling"] != "Eiti" for item in store.list_aliases(eitan.id))
        edited = store.edit_contact(
            eitan.id, display_name="Eitan Sommer", disambiguator="friend", timezone_name="Asia/Jerusalem"
        )
        assert edited.label == "Eitan Sommer — friend"

        unassigned = record(store, None)
        active = store.create_record(
            source_kind="call", source_label="active call", timezone_name="UTC"
        )
        assert store.retrieve(None, "line").matches == ()
        assert [item["id"] for item in store.list_unassigned()] == [unassigned]
        assert active not in {item["id"] for item in store.list_unassigned()}
        generation = store.assign_record(unassigned, alex_friend.id)
        assert generation == 2

        before = store.merge_preview(alex_friend.id, alex_work.id)
        assert before["aliases"] >= 1
        with pytest.raises(RuntimeError):
            store.merge_contacts(
                alex_friend.id, alex_work.id,
                failure_hook=lambda _db: (_ for _ in ()).throw(RuntimeError("rollback")),
            )
        assert store.get_contact(alex_work.id).display_name == "Alex"
        store.merge_contacts(alex_friend.id, alex_work.id)
        with pytest.raises(KeyError):
            store.get_contact(alex_work.id)
        assert store.resolve_contact("Al").id == alex_friend.id


def test_concurrent_reader_survives_short_writer_and_locked_write_rolls_back(tmp_path):
    path = tmp_path / "memory.sqlite3"
    with MemoryStore(path) as writer, MemoryStore(path, verify=False) as reader:
        contact = writer.create_contact("Alex")
        memory_id = writer.create_memory(contact.id, "Alex likes mint tea")
        reader._connection.execute("PRAGMA busy_timeout=1")
        with writer.transaction() as db:
            db.execute("UPDATE contacts SET display_name='Alexander' WHERE id=?", (contact.id,))
            assert reader.retrieve(contact.id, "mint tea").matches[0].memory_id == memory_id
            with pytest.raises(sqlite3.OperationalError, match="locked"):
                reader.create_contact("Blocked writer")
        assert not reader.list_contacts("Blocked writer")
        assert reader.create_contact("Second writer").display_name == "Second writer"


def test_import_requires_two_participants_and_explicit_mapping(tmp_path):
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        contact = store.create_contact("Maya")
        turns = [
            turn(1, SpeakerRole.UNCLEAR, "Hello").model_copy(update={"speaker_name": "Simon"}),
            turn(2, SpeakerRole.UNCLEAR, "Hi").model_copy(update={"speaker_name": "Maya"}),
        ]
        preview = store.import_preview(turns, timezone_name="Asia/Jerusalem", chunk_turns=1)
        assert preview.participants == ("Simon", "Maya")
        assert preview.estimated_chunks == 2
        record_id = store.confirm_import(
            preview, user_name="Simon", contact_id=contact.id, source_label="fictional export"
        )
        roles = [item.speaker_role for item in store.record_turns(record_id)]
        assert roles == [SpeakerRole.USER, SpeakerRole.SELECTED_CONTACT]
        with pytest.raises(ValueError):
            store.import_preview(turns[:1], timezone_name="UTC")


def test_active_record_is_not_manageable_or_analyzable(tmp_path):
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        contact = store.create_contact("Maya")
        active = store.create_record(
            source_kind="call", source_label="live fictional call", timezone_name="UTC",
            contact_id=contact.id, turns=[turn(1, SpeakerRole.USER, "hello")], status="active",
        )
        assert store.list_records(contact.id) == []
        with pytest.raises(ValueError, match="active"):
            store.create_batch(active, model="fake", reasoning="none")


def test_proposal_lifecycle_duplicates_revisions_sensitivity_and_deletion(tmp_path):
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        contact = store.create_contact("Maya")
        record_id = record(store, contact.id)
        batch = store.create_batch(record_id, model="fake", reasoning="none")
        proposals = [
            MemoryProposalInput(
                content="Maya's phone number is 0501111111", memory_type="person", confidence="high",
                evidence_turns=[2],
            ),
            MemoryProposalInput(
                content="Maya's phone number is 0502222222", memory_type="person", confidence="high",
                evidence_turns=[2],
            ),
            MemoryProposalInput(
                content="Maya's dog Pepper died", memory_type="event_date", confidence="high",
                sensitivity="sensitive", evidence_turns=[2], original_date_text="August 18",
                normalized_date_start=datetime(2026, 8, 18, tzinfo=timezone.utc),
            ),
            MemoryProposalInput(
                content="Pepper, Maya's dog, died", memory_type="event_date", confidence="medium",
                sensitivity="sensitive", evidence_turns=[2],
            ),
        ]
        ids = store.store_proposals(batch, proposals)
        assert store.proposal_duplicates(ids[0]) == []
        assert store.proposal_duplicates(ids[1]) == []
        assert store.proposal_duplicates(ids[3])

        store.reject_proposal(ids[0])
        assert store.retrieve(contact.id, "0501111111").matches == ()
        store.reopen_proposal(ids[0])
        phone_memory = store.approve_proposal(ids[0])
        pepper_memory = store.approve_proposal(ids[2])
        first_revision = store.current_revision(pepper_memory)
        assert not first_revision["cloud_allowed"]
        assert store.retrieve(contact.id, "Pepper", for_cloud=True).matches == ()

        permitted_revision = store.set_cloud_permission(pepper_memory, True)
        assert permitted_revision != first_revision["id"]
        assert store.retrieve(contact.id, "Pepper", for_cloud=True).matches[0].memory_id == pepper_memory
        corrected_revision = store.correct_memory(pepper_memory, "Maya's dog Pepper died on August 18")
        assert corrected_revision != permitted_revision
        current = store.retrieve(contact.id, "Pepper").matches
        assert [item.revision_id for item in current] == [corrected_revision]

        store.delete_memory(pepper_memory)
        assert store.retrieve(contact.id, "Pepper").matches == ()
        assert store._connection.execute(
            "SELECT count(*) FROM memory_revisions WHERE memory_id=?", (pepper_memory,)
        ).fetchone()[0] == 0
        assert store._connection.execute(
            "SELECT count(*) FROM memory_proposals WHERE approved_memory_id=?", (pepper_memory,)
        ).fetchone()[0] == 0
        assert store._connection.execute("SELECT count(*) FROM memory_search WHERE revision_id IN (SELECT id FROM memory_revisions WHERE memory_id=?)", (pepper_memory,)).fetchone()[0] == 0

        user_memory = store.create_memory(contact.id, "Maya prefers direct answers", memory_type="communication_style")
        assert store.current_revision(user_memory)["author_origin"] == "user_created"
        store.connect_memories(phone_memory, user_memory)
        store.delete_contact(contact.id)
        assert store._connection.execute("SELECT count(*) FROM memories").fetchone()[0] == 0


def test_bulk_proposal_review_is_atomic(tmp_path):
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        contact = store.create_contact("Maya")
        record_id = record(store, contact.id)
        batch = store.create_batch(record_id, model="fake", reasoning="none")
        ids = store.store_proposals(batch, [
            MemoryProposalInput(content=f"Maya detail {index}", memory_type="other", confidence="medium")
            for index in range(5)
        ])

        approved = store.review_proposals(ids[:2], approve=True)
        assert len(approved) == 2
        store.review_proposals(ids[2:4], approve=False)
        states = {
            row["id"]: row["state"]
            for row in store._connection.execute("SELECT id,state FROM memory_proposals")
        }
        assert [states[proposal_id] for proposal_id in ids] == [
            "approved", "approved", "rejected", "rejected", "pending"
        ]

        with pytest.raises(ValueError, match="current pending"):
            store.review_proposals([ids[4], ids[0]], approve=True)
        assert store._connection.execute(
            "SELECT state FROM memory_proposals WHERE id=?", (ids[4],)
        ).fetchone()[0] == "pending"
        assert store._connection.execute(
            "SELECT count(*) FROM memory_revisions WHERE content='Maya detail 4'"
        ).fetchone()[0] == 0


def test_bulk_memory_deletion_scrubs_all_selected_and_rolls_back_together(tmp_path):
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        contact = store.create_contact("Maya")
        memory_ids = [
            store.create_memory(contact.id, f"Maya remembers codeword{index}")
            for index in range(3)
        ]
        store.delete_memories(memory_ids[:2])
        assert store.retrieve(contact.id, "codeword0").matches == ()
        assert store.retrieve(contact.id, "codeword1").matches == ()
        assert store.retrieve(contact.id, "codeword2").matches[0].memory_id == memory_ids[2]

        survivor = store.create_memory(contact.id, "Maya likes rollback checks")
        with pytest.raises(KeyError):
            store.delete_memories([survivor, "missing-memory"])
        assert store.retrieve(contact.id, "rollback checks").matches[0].memory_id == survivor


def test_source_deletion_defaults_delete_and_can_keep_detached_memory(tmp_path):
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        contact = store.create_contact("Alex")
        record_id = record(store, contact.id)
        delete_id = store.create_memory(contact.id, "Alex likes tea", record_id=record_id)
        keep_id = store.create_memory(contact.id, "Alex works at Acme", record_id=record_id)
        store.correct_memory(keep_id, "Alex works at Acme Labs")
        preview = store.source_deletion_preview(record_id)
        assert {item["memory_id"] for item in preview} == {delete_id, keep_id}
        assert len(preview) == 2
        assert all(item["delete"] is True for item in preview)
        store.delete_source(record_id, keep_memory_ids=[keep_id])
        assert store.retrieve(contact.id, "tea").matches == ()
        assert store.retrieve(contact.id, "Acme Labs").matches[0].memory_id == keep_id
        source = store._connection.execute(
            "SELECT record_id,turn_sequences,source_deleted_at FROM memory_sources WHERE revision_id=?",
            (store.current_revision(keep_id)["id"],),
        ).fetchone()
        assert source["record_id"] is None and source["turn_sequences"] == "[]" and source["source_deleted_at"]


def test_historical_reassignment_defaults_delete_and_keeps_only_explicit_review_items(tmp_path):
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        wrong = store.create_contact("Alex", "wrong")
        corrected = store.create_contact("Alex", "correct")
        record_id = record(store, wrong.id)
        delete_id = store.create_memory(wrong.id, "Wrongly attributed item", record_id=record_id)
        keep_id = store.create_memory(wrong.id, "Reviewed transferable item", record_id=record_id)
        unrelated_id = store.create_memory(wrong.id, "Unrelated retained item")
        store.connect_memories(keep_id, unrelated_id)
        preview = store.reassignment_preview(record_id)
        assert all(item["delete"] for item in preview)
        assert store.reassign_record(record_id, corrected.id, keep_memory_ids=[keep_id]) == 2
        assert store.retrieve(wrong.id, "attributed").matches == ()
        assert store.retrieve(corrected.id, "transferable").matches[0].memory_id == keep_id
        kept = store._connection.execute("SELECT contact_id,needs_review FROM memories WHERE id=?", (keep_id,)).fetchone()
        assert tuple(kept) == (corrected.id, 1)
        assert store._connection.execute("SELECT deleted_at FROM memories WHERE id=?", (delete_id,)).fetchone()[0]
        assert store._connection.execute("SELECT count(*) FROM memory_connections").fetchone()[0] == 0


def test_reassigned_approved_source_does_not_block_original_contact_deletion(tmp_path):
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        original = store.create_contact("Alex", "original")
        corrected = store.create_contact("Alex", "corrected")
        record_id = record(store, original.id)
        batch = store.create_batch(record_id, model="fake", reasoning="none")
        proposal_id = store.store_proposals(batch, [
            MemoryProposalInput(content="Alex likes tea", memory_type="preference", confidence="medium")
        ])[0]
        memory_id = store.approve_proposal(proposal_id)
        store.reassign_record(record_id, corrected.id)
        assert store._connection.execute("SELECT count(*) FROM memory_proposals WHERE approved_memory_id=?", (memory_id,)).fetchone()[0] == 0
        store.delete_contact(original.id)
        with pytest.raises(KeyError):
            store.get_contact(original.id)


def test_extraction_is_bounded_resumable_and_never_auto_approves(tmp_path):
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        contact = store.create_contact("Alex")
        record_id = record(store, contact.id, count=5)
        first = ExtractionOutput(proposals=[
            MemoryProposalInput(content="Alex likes tea", memory_type="preference", confidence="medium", evidence_turns=[2])
        ])
        fake = FakeMemoryExtractor([first, RuntimeError("temporary failure")])
        with pytest.raises(RuntimeError):
            analyze_record(store, record_id, fake, chunk_turns=2)
        batch_id = store._connection.execute("SELECT id FROM proposal_batches").fetchone()[0]
        assert store.batch_progress(batch_id) == (1, 3, "failed")
        assert store.retrieve(contact.id, "tea").matches == ()

        retry = FakeMemoryExtractor([ExtractionOutput(), ExtractionOutput()])
        analyze_record(store, record_id, retry, batch_id=batch_id, chunk_turns=2)
        assert store.batch_progress(batch_id) == (3, 3, "pending_review")
        assert [len(call) for call in fake.calls] == [2, 2]
        assert [len(call) for call in retry.calls] == [2, 1]


def test_duplicate_discovery_does_not_hold_the_write_transaction(tmp_path, monkeypatch):
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        contact = store.create_contact("Alex")
        record_id = record(store, contact.id)
        batch = store.create_batch(record_id, model="fake", reasoning="none")
        observed = []
        original = store._duplicate_flags

        def checked(db, batch_id, contact_id):
            observed.append(db.in_transaction)
            return original(db, batch_id, contact_id)

        monkeypatch.setattr(store, "_duplicate_flags", checked)
        store.store_proposals(batch, [
            MemoryProposalInput(content="Alex likes tea", memory_type="preference", confidence="medium")
        ])
        assert observed == [False]


def test_extraction_chunks_and_cost_use_the_same_token_bound():
    items = [turn(index, SpeakerRole.SELECTED_CONTACT, "durable detail " * 80) for index in range(1, 21)]
    chunks = extraction_chunks(items)
    count, maximum = extraction_maximum_cost(items)
    assert count == len(chunks) > 1 and maximum > 0
    assert maximum == sum(
        conservative_request_cost(
            "gpt-5.6-luna",
            extraction_reservation_tokens(chunk),
            max_output_tokens=2_400,
        )
        for chunk in chunks
    )
    oversized = [turn(1, SpeakerRole.SELECTED_CONTACT, "x" * 20_000)]
    with pytest.raises(ValueError, match="exceeds"):
        extraction_chunks(oversized)


def test_openai_memory_extractor_is_stateless_bounded_and_validates_output():
    calls = []
    usage = SimpleNamespace(
        input_tokens=300, output_tokens=30,
        input_tokens_details=SimpleNamespace(cached_tokens=0, cache_write_tokens=0),
        output_tokens_details=SimpleNamespace(reasoning_tokens=0),
    )
    response = SimpleNamespace(output_parsed=ExtractionOutput(), usage=usage)
    client = SimpleNamespace(responses=SimpleNamespace(
        parse=lambda **kwargs: (calls.append(kwargs), response)[1]
    ))
    ledger = UsageLedger(BudgetLimits())

    output, _record = OpenAIMemoryExtractor(client=client, ledger=ledger)([
        turn(1, SpeakerRole.USER, "Ordinary small talk")
    ])

    assert output.proposals == [] and len(calls) == 1
    assert calls[0]["store"] is False and calls[0]["max_output_tokens"] == 2_400
    assert calls[0]["text_format"] is ExtractionOutput and len(ledger.records) == 1

    missing = SimpleNamespace(output_parsed=None, usage=usage)
    with pytest.raises(InterpretationModelOutputInvalid):
        OpenAIMemoryExtractor(
            client=SimpleNamespace(responses=SimpleNamespace(parse=lambda **_kwargs: missing)),
            ledger=UsageLedger(BudgetLimits()),
        )([turn(1, SpeakerRole.USER, "A durable detail")])


def test_openai_memory_extractor_retries_transient_and_releases_auth_reservations(monkeypatch):
    class ApiError(RuntimeError):
        def __init__(self, status_code):
            self.status_code = status_code

    usage = SimpleNamespace(input_tokens=200, output_tokens=20)
    success = SimpleNamespace(output_parsed=ExtractionOutput(), usage=usage)

    class Responses:
        def __init__(self, outcomes):
            self.outcomes = iter(outcomes)
            self.calls = 0

        def parse(self, **_kwargs):
            self.calls += 1
            outcome = next(self.outcomes)
            if isinstance(outcome, Exception):
                raise outcome
            return outcome

    monkeypatch.setattr(memory_module.time, "sleep", lambda _seconds: None)
    responses = Responses([ApiError(429), success])
    ledger = UsageLedger(BudgetLimits())
    OpenAIMemoryExtractor(
        client=SimpleNamespace(responses=responses), ledger=ledger
    )([turn(1, SpeakerRole.USER, "A durable detail")])
    assert responses.calls == 2 and len(ledger.records) == 1

    auth_ledger = UsageLedger(BudgetLimits())
    with pytest.raises(InterpretationUnavailable):
        OpenAIMemoryExtractor(
            client=SimpleNamespace(responses=Responses([ApiError(401)])), ledger=auth_ledger
        )([turn(1, SpeakerRole.USER, "A durable detail")])
    assert auth_ledger.records == ()


def test_contact_change_invalidates_review_batch_and_prevents_approval(tmp_path):
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        wrong = store.create_contact("Alex", "wrong")
        corrected = store.create_contact("Alex", "correct")
        record_id = record(store, wrong.id)
        batch = store.create_batch(record_id, model="fake", reasoning="none")
        proposal_id = store.store_proposals(batch, [
            MemoryProposalInput(content="Alex likes tea", memory_type="preference", confidence="medium")
        ])[0]
        assert store.batch_progress(batch)[2] == "pending_review"
        store.assign_record(record_id, corrected.id)
        store.fail_batch(batch, "late worker failure")
        assert store.batch_progress(batch)[2] == "invalidated"
        assert store.list_proposals(corrected.id) == []
        with pytest.raises(ValueError, match="current pending"):
            store.approve_proposal(proposal_id)


def test_exact_contact_lifecycle_filters_ambiguity_export_and_version(tmp_path):
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        maya = store.create_contact("Maya")
        alex = store.create_contact("Alex")
        pepper = store.create_memory(
            maya.id, "Maya's dog Pepper died on August 18", memory_type="event_date",
            sensitivity="sensitive", normalized_date_start=datetime(2026, 8, 18, tzinfo=timezone.utc),
        )
        store.create_memory(alex.id, "Alex's dog Pepper won a show", memory_type="event_date")
        direct = store.retrieve(maya.id, "Pepper")
        assert {item.memory_id for item in direct.matches} == {pepper}
        assert all(item.contact_id == maya.id for item in direct.matches)

        store.create_memory(
            maya.id, "Maya promised to send the draft Friday", memory_type="commitment"
        )
        indirect = store.retrieve(maya.id, "how have you been since the event")
        assert not indirect.ambiguous and indirect.matches[0].memory_id == pepper
        assert store.retrieve(maya.id, "How is pottery class? I made a bowl today").matches == ()

        moved = store.create_memory(
            maya.id, "Maya moved apartment on August 20", memory_type="event_date",
            normalized_date_start=datetime(2026, 8, 20, tzinfo=timezone.utc),
        )
        recent = store.retrieve(maya.id, "since the event")
        assert not recent.ambiguous and [item.memory_id for item in recent.matches] == [moved]

        store.create_memory(
            maya.id, "Maya started a new role on August 20", memory_type="event_date",
            normalized_date_start=datetime(2026, 8, 20, tzinfo=timezone.utc),
        )
        ambiguous = store.retrieve(maya.id, "since the event")
        assert ambiguous.ambiguous and ambiguous.status == "possibilities"
        assert len(ambiguous.matches) == 3

        pottery = store.create_memory(maya.id, "Maya finished her pottery piece", memory_type="recurring_topic")
        lexical = store.retrieve(maya.id, "did you finish the pottery piece since last week")
        assert not lexical.ambiguous and lexical.matches[0].memory_id == pottery

        rejected_record = record(store, maya.id)
        batch = store.create_batch(rejected_record, model="fake", reasoning="none")
        proposal_id = store.store_proposals(batch, [
            MemoryProposalInput(content="Maya likes mango", memory_type="preference", confidence="low")
        ])[0]
        store.reject_proposal(proposal_id)
        assert store.retrieve(maya.id, "mango").matches == ()

        payload = store.export_json(contact_id=maya.id)
        store.validate_export(payload)
        serialized = json.dumps(payload)
        assert "memory_search" not in serialized and "embedding" not in serialized and alex.id not in serialized
        payload["version"] = 2
        with pytest.raises(ValueError, match="unsupported"):
            store.validate_export(payload)
        with pytest.raises(ValueError):
            store.export_json()


def test_all_contact_export_chunks_more_than_sqlite_legacy_parameter_limit(tmp_path):
    with MemoryStore(tmp_path / "large-export.sqlite3") as store:
        for index in range(510):
            store.create_contact(f"Contact {index}")
        payload = store.export_json(all_data=True)
        assert len(payload["contacts"]) == 510
        assert payload["records"] == [] and payload["memories"] == []


def test_lexical_filter_keeps_content_words_and_drops_name_only_shared_reference(tmp_path):
    with MemoryStore(tmp_path / "lexical-focus.sqlite3") as store:
        contact = store.create_contact("Yaheli")
        job = store.create_memory(
            contact.id, "Yaheli lost his job", memory_type="event_date",
            normalized_date_start=datetime(2026, 8, 1, tzinfo=timezone.utc),
        )
        store.create_memory(
            contact.id,
            "Yaheli and Nora laughed about the smoke alarm",
            memory_type="shared_reference",
        )

        assert store.retrieve(contact.id, "Job hunting is rough").matches[0].memory_id == job
        assert store.retrieve(contact.id, "Nora's surgery is tomorrow").matches == ()
        assert store.retrieve(contact.id, "What happened after Nora's surgery?").matches == ()
        assert memory_module.query_date("Hi May, how are you?") is None


def test_memory_type_cue_can_disambiguate_a_named_contact_reference(tmp_path) -> None:
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        contact = store.create_contact("Maya")
        commitment = store.create_memory(
            contact.id,
            "Maya promised to send the draft Friday",
            memory_type="commitment",
        )
        shared = store.create_memory(
            contact.id,
            "Maya calls the blue mug Neptune",
            memory_type="shared_reference",
        )

        assert store.retrieve(contact.id, "What did Maya promise?").matches[0].memory_id == commitment
        assert store.retrieve(contact.id, "What is the Neptune reference?").matches[0].memory_id == shared


def test_unknown_event_dates_remain_ambiguous_in_either_sort_position(tmp_path):
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        dateless_first = store.create_contact("Maya", "dateless sorts first")
        store.create_memory(
            dateless_first.id,
            "Maya moved apartment on August 20",
            memory_type="event_date",
            normalized_date_start=datetime(2026, 8, 20, tzinfo=timezone.utc),
        )
        store.create_memory(dateless_first.id, "Maya changed jobs", memory_type="event_date")
        assert store.retrieve(dateless_first.id, "since the event").ambiguous

        dated_first = store.create_contact("Maya", "dated sorts first")
        store.create_memory(dated_first.id, "Maya changed jobs", memory_type="event_date")
        store.create_memory(
            dated_first.id,
            "Maya moves apartment on September 1",
            memory_type="event_date",
            normalized_date_start=datetime(2026, 9, 1, tzinfo=timezone.utc),
        )
        assert store.retrieve(dated_first.id, "since the event").ambiguous


def test_user_correction_can_change_or_clear_event_date(tmp_path):
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        contact = store.create_contact("Maya")
        memory_id = store.create_memory(
            contact.id,
            "Maya moved apartment",
            memory_type="event_date",
            original_date_text="2026-08-18",
            normalized_date_start=datetime(2026, 8, 18, tzinfo=timezone.utc),
        )
        store.correct_memory(
            memory_id,
            "Maya moved apartment",
            normalized_date_start=datetime(2026, 8, 20, tzinfo=timezone.utc),
        )
        current = store.current_revision(memory_id)
        assert current["normalized_date_start"] == "2026-08-20"
        assert current["original_date_text"] == "2026-08-20"

        store.correct_memory(memory_id, "Maya moved apartment", normalized_date_start=None)
        current = store.current_revision(memory_id)
        assert current["normalized_date_start"] is None
        assert current["original_date_text"] is None


def test_management_list_and_search_rows_expose_dates_for_correction(tmp_path):
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        contact = store.create_contact("Maya")
        memory_id = store.create_memory(
            contact.id,
            "Maya moved apartment",
            memory_type="event_date",
            original_date_text="August 18",
            normalized_date_start=datetime(2026, 8, 18, tzinfo=timezone.utc),
        )
        for row in (
            store.list_current_memories(contact.id)[0],
            store.search("moved apartment", contact_id=contact.id)[0],
        ):
            assert row["memory_id"] == memory_id
            assert row["original_date_text"] == "August 18"
            assert row["normalized_date_start"] == "2026-08-18"

        store.correct_memory(memory_id, "Maya moved to a new apartment")
        current = store.current_revision(memory_id)
        assert current["original_date_text"] == "August 18"
        assert current["normalized_date_start"] == "2026-08-18"


def test_database_path_creation_failure_is_wrapped_as_unavailable(tmp_path):
    blocking_file = tmp_path / "not-a-directory"
    blocking_file.write_text("blocked", encoding="utf-8")
    with pytest.raises(MemoryStoreUnavailable, match="memory database is unavailable"):
        MemoryStore(blocking_file / "memory.sqlite3")


def test_merge_rehomes_retrieval_and_contact_delete_clears_fts(tmp_path):
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        survivor = store.create_contact("Maya", "friend")
        merged = store.create_contact("Maya", "work")
        other = store.create_contact("Alex")
        other_memory = store.create_memory(other.id, "Alex prefers coffee")
        memory_id = store.create_memory(merged.id, "Maya prefers mint tea")
        record_id = record(store, merged.id)
        batch_id = store.create_batch(record_id, model="fake", reasoning="none")
        proposal_id = store.store_proposals(batch_id, [
            MemoryProposalInput(content="Maya likes coffee", memory_type="preference", confidence="medium")
        ])[0]
        assert store.merge_preview(survivor.id, merged.id)["pending_proposals"] == 1
        store.merge_contacts(survivor.id, merged.id)
        assert store.batch_progress(batch_id)[2] == "pending_review"
        approved = store.approve_proposal(proposal_id)
        assert store.current_revision(approved)["content"] == "Maya likes coffee"
        match = store.retrieve(survivor.id, "mint tea").matches[0]
        assert match.memory_id == memory_id and match.contact_id == survivor.id
        store.delete_contact(survivor.id)
        assert store.retrieve(other.id, "coffee").matches[0].memory_id == other_memory
        assert store._connection.execute("SELECT count(*) FROM memory_search").fetchone()[0] == 1


def test_explicit_date_query_restricts_temporal_candidates(tmp_path):
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        contact = store.create_contact("Maya")
        wanted = store.create_memory(
            contact.id, "Maya's appointment is August 18, 2026", memory_type="event_date",
            normalized_date_start=datetime(2026, 8, 18, tzinfo=timezone.utc),
        )
        store.create_memory(
            contact.id, "Maya moved on August 20, 2026", memory_type="event_date",
            normalized_date_start=datetime(2026, 8, 20, tzinfo=timezone.utc),
        )
        result = store.retrieve(contact.id, "What happened on August 18, 2026?")
        assert [item.memory_id for item in result.matches] == [wanted]

        missing_query = "What happened on August 19, 2026?"
        missing = store.retrieve(contact.id, missing_query, date_query=missing_query)
        assert missing.matches == () and missing.status == "abstain"

        commitment = store.create_memory(
            contact.id, "Maya promised to send the draft Friday", memory_type="commitment"
        )
        dated_lexical = store.retrieve(
            contact.id, "Are we still on for the draft? Does August 30 work?"
        )
        assert dated_lexical.matches[0].memory_id == commitment

        incidental = store.create_memory(contact.id, "Maya prefers tea", memory_type="preference")
        result = store.retrieve(
            contact.id, "We discussed tea. I am free June 5.", date_query=""
        )
        assert result.matches[0].memory_id == incidental


def test_explicit_date_uses_local_calendar_date_and_keeps_other_digits(tmp_path):
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        contact = store.create_contact("Maya")
        wanted = store.create_memory(
            contact.id, "Call Maya at 0501111111 on August 30, 2026", memory_type="event_date",
            normalized_date_start=datetime.fromisoformat("2026-08-30T00:00:00+03:00"),
        )
        store.create_memory(
            contact.id, "Call Maya at 0502222222 on August 30, 2026", memory_type="event_date",
            normalized_date_start=datetime.fromisoformat("2026-08-30T00:00:00+03:00"),
        )

        result = store.retrieve(contact.id, "Should I call 0501111111 on August 30, 2026?")
        assert not result.ambiguous and result.matches[0].memory_id == wanted
        assert store.current_revision(wanted)["normalized_date_start"] == "2026-08-30"


def test_close_non_temporal_candidates_return_possibilities(tmp_path):
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        contact = store.create_contact("Maya")
        store.create_memory(contact.id, "Maya's phone number is 0501111111", memory_type="person")
        store.create_memory(contact.id, "Maya's phone number is 0502222222", memory_type="person")

        result = store.retrieve(contact.id, "Which phone number should I call?")
        assert result.ambiguous and result.status == "possibilities"
        assert len(result.matches) == 2

        temporal = store.retrieve(contact.id, "Which phone number should I call before the meeting?")
        assert temporal.ambiguous and temporal.status == "possibilities"


def test_same_type_candidates_with_a_clear_lexical_winner_are_selected(tmp_path):
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        contact = store.create_contact("Maya")
        wanted = store.create_memory(contact.id, "Maya prefers mint tea", memory_type="preference")
        store.create_memory(contact.id, "Maya prefers direct answers", memory_type="preference")

        result = store.retrieve(contact.id, "Maya mint tea")
        assert not result.ambiguous and result.matches[0].memory_id == wanted


def test_active_contact_cannot_be_deleted_until_the_call_stops(tmp_path):
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        contact = store.create_contact("Maya")
        record_id = store.create_record(
            source_kind="call", source_label="active call", timezone_name="UTC",
            contact_id=contact.id,
        )
        store.create_memory(contact.id, "Maya likes tea")

        with pytest.raises(ValueError, match="stop the active call"):
            store.delete_contact(contact.id)
        assert store.get_contact(contact.id).display_name == "Maya"
        store.stop_record(record_id)
        store.delete_contact(contact.id)


def test_approved_proposals_are_not_duplicated_and_connections_stay_with_contact(tmp_path):
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        maya = store.create_contact("Maya")
        alex = store.create_contact("Alex")
        record_id = record(store, maya.id)
        batch = store.create_batch(record_id, model="fake", reasoning="none")
        proposal_id = store.store_proposals(batch, [
            MemoryProposalInput(content="Maya likes tea", memory_type="preference", confidence="medium")
        ])[0]
        maya_memory = store.approve_proposal(proposal_id)
        alex_memory = store.create_memory(alex.id, "Alex likes coffee")

        assert store.list_proposals(maya.id) == []
        with pytest.raises(ValueError, match="same contact"):
            store.connect_memories(maya_memory, alex_memory)


def test_search_filters_current_memory_by_type_sensitivity_and_date(tmp_path):
    with MemoryStore(tmp_path / "memory.sqlite3") as store:
        maya = store.create_contact("Maya")
        alex = store.create_contact("Alex")
        wanted = store.create_memory(
            maya.id, "Maya has a private appointment", memory_type="event_date", sensitivity="sensitive",
            normalized_date_start=datetime(2026, 8, 18, tzinfo=timezone.utc),
        )
        store.create_memory(maya.id, "Maya likes tea", memory_type="preference")
        store.create_memory(alex.id, "Alex has a private appointment", memory_type="event_date", sensitivity="sensitive")
        rows = store.search(
            "", contact_id=maya.id, memory_type="event_date", sensitivity="sensitive",
            date_from="2026-08-18", date_to="2026-08-18",
        )
        assert [row["memory_id"] for row in rows] == [wanted]
