"""Qt interaction checks: disposable data, fake devices and saved answers only."""
import queue
import threading
import time
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from PySide6.QtCore import Qt, QTimer, QSettings, QPoint
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QPushButton, QPlainTextEdit, QLineEdit, QDialog
from conversation_copilot import desktop, desktop_data, memory
from conversation_copilot.f06_evaluation import seed_case
from conversation_copilot.models import ConversationTurn, SpeakerRole


@pytest.fixture(scope="module")
def qt():
    app = QApplication.instance() or QApplication([])
    app.setStyle("Fusion")
    return app


def wait_for(predicate, timeout=3000):
    deadline = time.monotonic() + timeout / 1000
    while not predicate() and time.monotonic() < deadline:
        QApplication.processEvents()
        time.sleep(.01)  # Release the GIL for the real Python worker threads.
    assert predicate()


def click(parent, text):
    matches = [b for b in parent.findChildren(QPushButton) if b.text() == text]
    assert matches, text
    QTest.mouseClick(matches[0], Qt.LeftButton)
    QApplication.processEvents()


@pytest.fixture
def window(qt, tmp_path, monkeypatch):
    monkeypatch.setattr(desktop, "QSettings", lambda *_: QSettings(str(tmp_path / "settings.ini"), QSettings.IniFormat))
    monkeypatch.setattr(desktop, "local_openai_api_key", lambda: "fixture-not-a-key")
    monkeypatch.setattr(desktop_data, "confirm", lambda *_a, **_k: True)
    monkeypatch.setattr(desktop, "confirm", lambda *_a, **_k: True)
    monkeypatch.setattr(memory.MemoryStore, "backfill_semantic_embeddings", lambda *_a, **_k: 0)
    store = memory.MemoryStore(tmp_path / "ui.sqlite3")
    session, _ = seed_case(store, "appointment")
    app = desktop.Desktop(store, discover=False)
    app.show()
    app.contact_box.setCurrentIndex(app.contact_box.findData(session.contact_id))
    QApplication.processEvents()
    yield app
    for child in app.findChildren(QDialog):
        child.close()
    app.closing = True
    if app.audio_session:
        app.stop()
    wait_for(lambda: not app.pending_jobs and app.audio_session is None)
    app.close()
    QApplication.processEvents()


def ready(app):
    app.audio_runtime_error = ""
    app.audio_catalog = SimpleNamespace(microphones=[object()], playbacks=[object()], close=lambda: None, closed=False)
    app.microphone_box.addItem("Fixture microphone")
    app.playback_box.addItem("Fixture speakers")
    app.windows = [SimpleNamespace(display_name="Fictional call", kind="Fixture")]
    app.window_box.addItem("Fictional call")
    app.window_box.setCurrentIndex(0)
    app.update_readiness()


def test_import_detect_select_edit_and_save(window, monkeypatch):
    from conversation_copilot import import_transcript as imp
    from PySide6.QtWidgets import QComboBox
    monkeypatch.setattr(imp,'f06_structured_request',lambda *a,**k:(imp.Participants(names=['Me','Alex'],suggested_contact='Alex'),None))
    generated=[]
    monkeypatch.setattr(window,'open_review',lambda rid: None)
    monkeypatch.setattr(window,'start_review_job',lambda rid,ledger: generated.append(rid))
    panel=desktop_data.import_chat(window)
    editor=panel.findChild(QPlainTextEdit)
    selector=panel.findChild(QComboBox)
    save=next(b for b in panel.findChildren(QPushButton) if b.text()=='Import and generate')
    editor.setPlainText('Me: Hello\nAlex: I start work tomorrow.')
    click(panel,'Detect participants')
    wait_for(lambda: selector.isEnabled())
    assert selector.count()==2 and selector.currentText()=='Alex' and save.isEnabled()
    selector.setCurrentText('Alex')
    assert save.isEnabled()
    editor.appendPlainText('Me: Good luck!')
    assert not save.isEnabled() and selector.count()==0
    assert not any('Suggested contact:' in item.text() for item in panel.findChildren(desktop.QLabel))
    click(panel,'Detect participants')
    wait_for(lambda: selector.isEnabled())
    selector.setCurrentText('Alex')
    click(panel,'Import and generate')
    assert len(generated)==1
    turns=window.memory_store.record_turns(generated[0])
    assert [t.speaker_role for t in turns]==['user','selected_contact','user']


def test_import_failure_and_close_ignore_late_result(window, monkeypatch):
    from PySide6.QtWidgets import QComboBox
    pending=[]
    monkeypatch.setattr(window,'run_job',lambda work,done: pending.append((work,done)))
    panel=desktop_data.import_chat(window)
    editor=panel.findChild(QPlainTextEdit)
    editor.setPlainText('Me: Hello\nAlex: Hi')
    click(panel,'Detect participants')
    assert editor.isReadOnly()
    pending.pop()[1](None,RuntimeError('Unavailable'))
    assert not editor.isReadOnly() and not panel.findChild(QComboBox).isEnabled()
    click(panel,'Detect participants')
    panel.close()
    QApplication.processEvents()
    pending.pop()[1](None,RuntimeError('Late result'))  # No deleted-widget access.


def test_home_readiness_theme_and_modal_controls(window, monkeypatch):
    assert window.start_button.property("role") == "start"
    assert not window.start_button.isEnabled()
    assert "✓" not in window.ready_text.text()
    ready(window)
    assert window.start_button.isEnabled()
    assert "✓" in window.ready_text.text()
    for selector in (window.microphone_box, window.playback_box, window.window_box, window.contact_box):
        selector.setCurrentIndex(-1)
        assert not window.start_button.isEnabled()
        selector.setCurrentIndex(0)
        assert window.start_button.isEnabled()
    assert window.model_box.width() <= 160
    assert window.start_button.height() >= 64
    old_theme = window.dark
    for dark in (False, True):
        window.dark = dark
        window.apply_theme()
        QApplication.processEvents()
        sample = QPoint(20, window.start_button.height() // 2)
        enabled_color = window.start_button.grab().toImage().pixelColor(sample).name()
        assert enabled_color in ("#15803d", "#166534")
        window.start_button.setEnabled(False)
        assert window.start_button.grab().toImage().pixelColor(sample).name() != enabled_color
        window.start_button.setEnabled(True)
    window.dark = old_theme
    window.apply_theme()
    QTest.mouseClick(window.theme_button, Qt.LeftButton)
    assert window.dark != old_theme
    window.open_settings()
    QApplication.processEvents()
    settings = QApplication.activeModalWidget()
    assert settings.windowTitle() == "Settings"
    field = settings.findChild(QLineEdit)
    assert field.echoMode() == QLineEdit.Password and field.text() == ""
    saved = []
    monkeypatch.setattr(desktop, "save_local_openai_api_key", saved.append)
    field.setText("replacement-fixture")
    click(settings, "Save key")
    assert saved == ["replacement-fixture"] and field.text() == ""
    theme = window.dark
    QTest.mouseClick(window.windowHandle(), Qt.LeftButton,
                     pos=window.theme_button.mapTo(window, window.theme_button.rect().center()))
    assert window.dark == theme
    nested = desktop.Panel(settings, "Nested")
    nested.show()
    QApplication.processEvents()
    assert QApplication.activeModalWidget() is nested
    nested.close()
    QApplication.processEvents()
    assert QApplication.activeModalWidget() is settings
    settings.close()
    QApplication.processEvents()
    assert QApplication.activeModalWidget() is None


def test_memories_ask_edit_delete_and_large_editor(window, monkeypatch):
    from conversation_copilot.ask_memory import AskSession
    monkeypatch.setattr(desktop_data, "cloud_answer", lambda store, *_a, **_k: AskSession(window.selected_contact_id).answer(store, "What time is the dentist appointment?"))
    panel = desktop_data.Memories(window, window.selected_contact_id)
    panel.show()
    panel.question.setText("What time is the dentist appointment?")
    assert panel.answer_card.isHidden()
    panel.question.setFocus()
    QTest.keyClick(panel.question, Qt.Key_Return)
    wait_for(lambda: not panel.running)
    assert panel.isVisible() and not panel.answer_card.isHidden()
    assert "3" in panel.answer.text() and panel.related
    assert not any(b.text() in {"Pending", "Add", "Connect", "Sources"} for b in panel.findChildren(QPushButton))
    item = dict(window.memory_store.list_current_memories(window.selected_contact_id)[0])
    monkeypatch.setattr(desktop_data, "edit_text", lambda *_a, **_k: "Dentist appointment is at 4 PM.")
    panel.edit_memory(item)
    assert "4 PM" in window.memory_store.current_revision(item["memory_id"])["content"]
    assert panel.result is None
    panel.delete_memory(item)
    assert not window.memory_store.list_current_memories(window.selected_contact_id)
    panel.close()
    measured = []
    def fill_editor():
        editor = QApplication.activeModalWidget()
        field = editor.findChild(QPlainTextEdit)
        before = field.size()
        editor.resize(900, 680)
        QApplication.processEvents()
        measured.append(field.width() > before.width() and field.height() > before.height())
        field.setPlainText("Updated wording")
        editor.accept()
    QTimer.singleShot(30, fill_editor)
    assert desktop.edit_text(window, "Edit memory", "Original") == "Updated wording"
    assert measured == [True]


def test_contact_information_history_and_summary_quotes(window, monkeypatch):
    from conversation_copilot.ask_memory import CloudAskOutput, summary_source
    from conversation_copilot import interpretation
    from PySide6.QtWidgets import QLabel
    rid = seed_review(window)
    sid = window.memory_store.summary_for_review(rid)['id']
    window.memory_store.approve_summary(sid)
    statement = window.memory_store.summary_statements(sid)[0]
    source = summary_source(window.memory_store, statement['id'], window.selected_contact_id)
    def request(schema, payload, instructions, **kwargs):
        assert source.id in {item['id'] for item in payload['evidence']}
        return CloudAskOutput(status='answered', answer='They discussed the book.', source_ids=[source.id]), SimpleNamespace(dollars=0)
    monkeypatch.setattr(interpretation, 'f06_structured_request', request)
    assert not any(b.text() == 'History' for b in window.findChildren(QPushButton))
    click(window, 'Contact information')
    panel = window.findChild(desktop_data.Memories)
    assert panel.windowTitle() == 'Contact information'
    panel.question.setText('What was discussed?')
    QTest.keyClick(panel.question, Qt.Key_Return)
    wait_for(lambda: not panel.running)
    assert any(w.text() == f'“{source.content}”' for w in panel.findChildren(QLabel))
    click(panel, 'View conversation')
    assert window.review_dialogs[rid].isVisible() and not window.review_running
    window.review_dialogs[rid].close()
    QApplication.processEvents()
    click(panel, 'Conversation history')
    history = panel.findChild(desktop_data.History)
    assert history.isVisible() and history.parent() is panel
    history.close()
    window.memory_store.delete_summary(rid)
    panel.validate_answer()
    assert panel.result is None and panel.summary_evidence.count() == 0


def test_review_does_not_present_an_intermediate_chunk_as_full_summary(window):
    rid = seed_review(window)
    store = window.memory_store
    sid = store.summary_for_review(rid)['id']
    with store.transaction() as db:
        db.execute("INSERT INTO review_jobs(record_id,generation,state,created_at) VALUES (?,1,'pending','fixture')", (rid,))
        db.execute('INSERT INTO review_chunks VALUES (?,0,?,0)', (rid,sid))
    panel = desktop_data.Review(window,rid)
    assert panel.version is None and not panel.narrative.toPlainText()
    assert 'unfinished' in panel.status.text()
    assert not next(b for b in panel.findChildren(QPushButton) if b.text() == 'Approve summary').isEnabled()


def seed_review(window):
    store = window.memory_store
    record = store.create_record(source_kind="call", source_label="UI fixture", timezone_name="UTC", contact_id=window.selected_contact_id,
        status="stopped", turns=[ConversationTurn(speaker_name="Alex", speaker_role=SpeakerRole.SELECTED_CONTACT,
            source="fixture", content="We discussed the book and will meet Friday.", display_order=1)])
    batch = store.create_batch(record, model="fake", reasoning="none")
    store.store_proposals(batch, [memory.MemoryProposalInput(content="Meet Friday", memory_type="event_date", confidence="high", evidence_turns=[1])])
    store.create_summary_draft(record, memory.SummaryOutput(statements=[memory.SummaryStatementInput(section="discussed",
        content="They discussed the book and planned to meet Friday.", kind="fact", confidence="high", evidence_turns=[1])]), expected_generation=1)
    return record


def test_window_refresh_preserves_devices_and_contact(window, monkeypatch):
    from conversation_copilot import windows
    ready(window)
    previous = window.windows[0]
    preview = SimpleNamespace(stop=lambda: None, snapshot=lambda: SimpleNamespace(status="Preview", current_signal=None, thumbnail_rgb=None))
    window.preview_session = preview
    catalog = window.audio_catalog
    selected = (window.selected_contact_id, window.microphone_box.currentText(), window.playback_box.currentText())
    monkeypatch.setattr(windows, "list_call_windows", lambda: [previous, SimpleNamespace(display_name="New call")])
    click(window, "Refresh")
    wait_for(lambda: not window.discovery_running)
    assert window.audio_catalog is catalog
    assert selected == (window.selected_contact_id, window.microphone_box.currentText(), window.playback_box.currentText())
    assert window.window_box.count() == 2 and window.window_box.currentIndex() == 0
    assert window.preview_session is preview
    monkeypatch.setattr(windows, "list_call_windows", lambda: [])
    click(window, "Refresh")
    wait_for(lambda: not window.discovery_running)
    assert window.window_box.currentIndex() == -1 and not window.start_button.isEnabled()
    assert window.preview_session is None
    assert window.audio_catalog is catalog and window.microphone_box.currentIndex() == 0


def test_model_cost_selection_and_future_price(window, monkeypatch):
    from conversation_copilot import interpretation as api
    first = window.call_cost_label.text()
    window.model_box.setCurrentIndex(1)
    assert window.call_cost_label.text() != first
    assert window.call_cost_label.text().count("$") == 1
    assert api.ten_minute_call_estimate("unknown") is None
    monkeypatch.setitem(api.MODEL_PRICES, "future", api.ModelPrice(3, .3, 15))
    monkeypatch.setattr(api, "LIVE_ASK_MODELS", (api.LUNA_MODEL, "future"))
    assert api.ten_minute_call_estimate("future") > api.ten_minute_call_estimate(api.LUNA_MODEL)


def test_review_rejection_shared_sources_and_generation_guards(window, monkeypatch):
    store = window.memory_store
    record = seed_review(window)
    original = store.record_pending_proposals(record)[0]
    batch = store.create_batch(record, model="fake", reasoning="none")
    store.store_proposals(batch, [memory.MemoryProposalInput(content="Likes books", memory_type="preference", confidence="high", evidence_turns=[1])])
    # create_batch supersedes old batches; put both shared-source suggestions in the current batch.
    store._connection.execute("UPDATE memory_proposals SET batch_id=? WHERE id=?", (batch, original["id"]))
    store._connection.commit()
    window.open_review(record)
    panel = window.review_dialogs[record]
    original_summary = panel.narrative.toPlainText()
    panel.review_memories(False, one=next(m for m in panel.memories if m["id"] == original["id"]))
    wait_for(lambda: not panel.saving)
    assert panel.narrative.toPlainText() == original_summary
    survivor = store.record_pending_proposals(record)[0]
    store.review_record_proposals(record, [survivor["id"]], approve=True, expected_pending={survivor["id"]: survivor["content"]})
    # Same rejected wording cannot be reinserted through either ingestion path.
    retry = store.create_batch(record, model="fake", reasoning="none")
    assert store.store_proposals(retry, [memory.MemoryProposalInput(content=original["content"], memory_type="event_date", confidence="high", evidence_turns=[1])]) == []
    store._connection.execute("INSERT INTO review_jobs(record_id,generation,state,created_at) VALUES (?,1,'running','test')", (record,))
    store._connection.commit()
    panel.reload()
    assert not next(b for b in panel.findChildren(QPushButton) if b.text() == "Reject summary").isEnabled()
    with pytest.raises(ValueError, match="generation"):
        store.delete_summary(record)
    with pytest.raises(ValueError, match="generation"):
        store.review_record_proposals(record, None, approve=True, expected_pending={})
    store._connection.execute("UPDATE review_jobs SET state='complete' WHERE record_id=?", (record,))
    store._connection.commit()
    panel.reload()
    # A memory correction must not replace a larger summary paragraph.
    approved = next(m for m in panel.memories if m["state"] == "approved")
    monkeypatch.setattr(desktop_data, "edit_text", lambda *_a, **_k: "Enjoys novels")
    panel.edit_memory(approved)
    assert panel.narrative.toPlainText() == original_summary


def test_empty_call_has_no_generation_or_retry(window):
    record = window.memory_store.create_record(source_kind="call", source_label="Empty test", timezone_name="UTC", contact_id=window.selected_contact_id, status="stopped", turns=[])
    window.open_review(record)
    assert not window.start_review_job(record, desktop.UsageLedger.product())
    panel = window.review_dialogs[record]
    assert "Nothing was transcribed" in panel.status.text()
    assert panel.retry_button.isHidden()


def test_oversized_source_reaches_chunked_review_without_retry_loop(window, monkeypatch):
    from conversation_copilot import post_call
    called = []
    monkeypatch.setattr(post_call, "process_review", lambda *_a, **_k: called.append(True))
    record = window.memory_store.create_record(source_kind="call", source_label="Oversized fixture", timezone_name="UTC", contact_id=window.selected_contact_id, status="stopped", turns=[ConversationTurn(speaker_name="Alex", speaker_role=SpeakerRole.SELECTED_CONTACT, source="fixture", content="Long sentence. " * 20000, display_order=1)])
    window.open_review(record)
    window.start_review_job(record, desktop.UsageLedger.product())
    wait_for(lambda: not window.review_running)
    panel = window.review_dialogs[record]
    assert called == [True] and "too long" not in panel.status.text()
    assert not panel.retry_button.isHidden()


def test_whole_summary_edit_noop_regenerate_retry_and_delete(window, monkeypatch):
    from conversation_copilot import post_call
    from conversation_copilot.interpretation import UsageRecord
    from PySide6.QtWidgets import QSplitter
    store = window.memory_store
    record = seed_review(window)
    approved = store.create_memory(window.selected_contact_id, "Keep this approved fact")
    window.open_review(record)
    panel = window.review_dialogs[record]
    assert not panel.findChildren(QSplitter)
    captions = {b.text() for b in panel.findChildren(QPushButton)}
    assert {"Edit summary", "View transcript", "Reject summary"} <= captions
    assert "Edit sentence" not in captions and not hasattr(panel, "more")
    requests = []
    def generation(schema, payload, instructions, **kwargs):
        requests.append(payload)
        assert schema is memory.ExtractionOutput and "Saturday" in payload["user_edited_summary"]
        if len(requests) == 1:
            raise RuntimeError("Simulated provider interruption")
        return memory.ExtractionOutput(proposals=[memory.MemoryProposalInput(content="Meet Saturday", memory_type="event_date", confidence="medium", evidence_turns=[1])]), UsageRecord("fake", "low", 0, 0, 0, 0, 0, 0)
    monkeypatch.setattr(post_call, "f06_structured_request", generation)
    original = panel.narrative.toPlainText()
    monkeypatch.setattr(desktop_data, "edit_text", lambda *_a, **_k: original)
    panel.edit_summary()
    assert not requests and not window.review_running
    monkeypatch.setattr(desktop_data, "edit_text", lambda *_a, **_k: "They planned to meet Saturday. " * 15)
    panel.edit_summary()
    wait_for(lambda: not window.review_running)
    assert len(requests) == 1 and "Saturday" in panel.narrative.toPlainText()
    assert record in window.review_errors and not panel.retry_button.isHidden()
    assert store.current_revision(approved)["content"] == "Keep this approved fact"
    saved = panel.narrative.toPlainText()
    monkeypatch.setattr(desktop_data, "edit_text", lambda *_a, **_k: saved)
    panel.edit_summary()
    assert len(requests) == 1
    click(panel, "Retry generation")
    wait_for(lambda: not window.review_running)
    assert len(requests) == 2 and record not in window.review_errors
    pending = store.record_pending_proposals(record)
    assert len(pending) == 1 and pending[0]["content"] == "Meet Saturday"
    confirmations = []
    monkeypatch.setattr(desktop_data, "confirm", lambda _p, _t, message, **_k: confirmations.append(message) or True)
    panel.review_memories(False, all_items=True)
    wait_for(lambda: not panel.saving)
    assert confirmations == ["Remove 1 pending memory? Approved memories will remain."]
    assert not store.record_pending_proposals(record)
    assert not store._connection.execute("SELECT 1 FROM memory_proposals WHERE id=?", (pending[0]["id"],)).fetchone()
    assert store.summary_turns(record)  # Rejecting a suggestion is not transcript deletion.
    assert store._connection.execute("SELECT 1 FROM declined_memories WHERE record_id=?", (record,)).fetchone()
    assert all(b.text() not in {"Reopen", "Permanently delete"} for b in panel.findChildren(QPushButton))
    panel.reject_summary()
    assert not store._connection.execute("SELECT 1 FROM summary_versions WHERE record_id=?", (record,)).fetchone()
    assert store.record_turns(record) and store.current_revision(approved)


def test_automatic_review_uses_stopped_call_ledger(window, monkeypatch):
    from conversation_copilot import post_call
    from conversation_copilot.interpretation import UsageLedger, UsageRecord
    store = window.memory_store
    record = seed_review(window)
    store.delete_summary(record)
    ledger = UsageLedger.product()
    ledger.stopped = True
    requests = []
    def generation(schema, payload, instructions, **kwargs):
        requests.append(payload)
        # Stopping live requests must not stop the post-call phase or reset its accounting.
        assert kwargs["ledger"].records == ledger.records
        reserve = kwargs["ledger"].reserve(post_call.REVIEW_MODEL, 100, live=False)
        usage = UsageRecord(post_call.REVIEW_MODEL, "low", 100, 0, 0, 20, 0, .0004)
        kwargs["ledger"].complete(reserve, usage)
        unrelated = ledger.reserve(post_call.REVIEW_MODEL, 50, live=False)
        ledger.complete(unrelated, UsageRecord(post_call.REVIEW_MODEL, "low", 50, 0, 0, 10, 0, .0002))
        return memory.SummaryOutput(statements=[memory.SummaryStatementInput(section="plans", content="Meet Friday.", kind="fact", confidence="high", evidence_turns=[1])]), usage
    monkeypatch.setattr(post_call, "f06_structured_request", generation)
    window.open_review(record)
    window.start_review_job(record, ledger)
    wait_for(lambda: not window.review_running)
    assert len(requests) == 1 and record not in window.review_errors
    assert window.review_dialogs[record].narrative.toPlainText() == "Meet Friday."
    assert ledger.total_dollars == pytest.approx(.0006)
    import json
    receipts = json.loads(store._connection.execute("SELECT usage_json FROM review_jobs WHERE record_id=?", (record,)).fetchone()[0])
    assert len(receipts) == 1 and receipts[0]["dollars"] == .0004


def test_review_history_checks_and_approval(window, monkeypatch):
    record = seed_review(window)
    panel = desktop_data.Review(window, record)
    panel.show()
    click(panel, "Select all pending")
    assert all(c.isChecked() for c in panel.checks.values() if c.isEnabled())
    click(panel, "Clear selection")
    assert not any(c.isChecked() for c in panel.checks.values())
    pending = next(m for m in panel.memories if m["state"] == "pending")
    check = panel.checks[pending["id"]]
    QTest.mouseClick(check, Qt.LeftButton, pos=QPoint(15, check.height() // 2))
    assert panel.checks[pending["id"]].isChecked()
    click(panel, "Approve selected")
    wait_for(lambda: not panel.saving)
    assert not window.memory_store.record_pending_proposals(record)
    click(panel, "Approve summary")
    wait_for(lambda: not panel.saving)
    assert panel.version["state"] == "approved"
    monkeypatch.setattr(window, "start_review_job", lambda *_: True)
    monkeypatch.setattr(desktop_data, "edit_text", lambda *_a, **_k: "They planned to meet Saturday.")
    panel.edit_summary()
    assert "Saturday" in panel.narrative.toPlainText()
    panel.close()
    history = desktop_data.History(window, window.selected_contact_id)
    history.show()
    assert history.records
    history.listing.setCurrentRow(0)
    history.review()
    assert record in window.review_dialogs
    assert not window.review_running


def test_worker_keeps_event_loop_responsive(window):
    release = threading.Event()
    completed, ticks = [], []
    timer = QTimer(window)
    timer.timeout.connect(lambda: ticks.append(time.monotonic()))
    timer.start(10)
    window.run_job(lambda: release.wait(2), lambda result, error: completed.append((result, error)))
    QTest.qWait(120)
    old = window.dark
    QTest.mouseClick(window.theme_button, Qt.LeftButton)
    assert window.dark != old and len(ticks) >= 4 and not completed
    release.set()
    wait_for(lambda: bool(completed))
    timer.stop()


def test_review_approval_runs_off_ui_thread_and_blocks_duplicate_clicks(window, monkeypatch):
    record = seed_review(window)
    panel = desktop_data.Review(window, record)
    panel.show()
    panel.select_all()
    release = threading.Event()
    calls, ticks = [], []
    original = memory.MemoryStore.review_record_proposals
    main_thread = threading.get_ident()
    def slow(store, *args, **kwargs):
        calls.append(threading.get_ident())
        assert release.wait(2), 'Approval blocked the Qt caller'
        return original(store, *args, **kwargs)
    monkeypatch.setattr(memory.MemoryStore, 'review_record_proposals', slow)
    timer = QTimer(panel)
    timer.timeout.connect(lambda: ticks.append(1))
    timer.start(10)
    try:
        panel.review_memories(True)
        wait_for(lambda: bool(calls))
        panel.review_memories(True)
        panel.reject()
        panel.close()
        QTest.qWait(80)
        assert ticks and panel.isVisible() and panel.saving
        assert calls == [calls[0]] and calls[0] != main_thread
    finally:
        release.set()
    wait_for(lambda: not window.pending_jobs)
    assert not panel.saving and not window.memory_store.record_pending_proposals(record)


def test_review_worker_failure_restores_selection_and_controls(window, monkeypatch):
    panel = desktop_data.Review(window, seed_review(window))
    panel.show()
    panel.select_all()
    errors = []
    monkeypatch.setattr(window, 'report', lambda error, *_: errors.append(str(error)))
    def fail(*_a, **_kw):
        raise ValueError('save failed')
    monkeypatch.setattr(memory.MemoryStore, 'review_record_proposals', fail)
    panel.review_memories(True)
    wait_for(lambda: not panel.saving)
    assert errors == ['save failed']
    assert all(c.isChecked() and c.isEnabled() for c in panel.checks.values())
    assert next(b for b in panel.findChildren(QPushButton) if b.text() == 'Approve selected').isEnabled()
    assert window.memory_store.record_pending_proposals(panel.record_id)


def test_fake_call_start_stop_flush_and_preview(window, monkeypatch):
    from conversation_copilot import audio, video
    ready(window)
    class Video:
        def __init__(self, *_):
            self.worker_alive = True
            self.capture = SimpleNamespace(worker_alive=True)
            self.switched = 0
        def start(self):
            pass
        def stop(self):
            self.worker_alive = self.capture.worker_alive = False
        def switch_face(self):
            self.switched += 1
        continue_tracking = switch_face
        def snapshot(self):
            return SimpleNamespace(status="Tracking", current_signal=None, thumbnail_rgb=None)
    class Audio:
        def __init__(self, *_a, **_k):
            self.results = queue.SimpleQueue()
            self.running = False
        def start(self):
            self.running = True
        def request_stop(self):
            pass
        def stop(self):
            self.results.put(SimpleNamespace(speaker_name="Alex", speaker_role=SpeakerRole.SELECTED_CONTACT,
                source="fixture", content="Final words survive shutdown.", timestamp=datetime.now(timezone.utc), vocal=None))
            self.running = False
        def snapshot(self):
            return SimpleNamespace(running=self.running, microphone_status="ready", playback_status="ready", fault=None)
    monkeypatch.setattr(video, "LiveVideoSession", Video)
    monkeypatch.setattr(audio, "AudioCallSession", Audio)
    monkeypatch.setattr(window, "begin_interpretation_session", lambda: None)
    generated = []
    monkeypatch.setattr(window, "start_review_job", lambda record, ledger: generated.append(record))
    window.preview_face()
    wait_for(lambda: window.preview_session is not None)
    preview = window.preview_session
    window.switch_preview()
    assert preview.switched == 1
    click(window, "Start call")
    wait_for(lambda: window.audio_session is not None)
    assert window.session is preview and window.pages.currentWidget() is window.live
    record = window.current_record_id
    click(window, "■  END CALL")
    wait_for(lambda: window.audio_session is None and not window.stopping)
    assert generated == [record]
    assert window.memory_store.record_turns(record)[-1].content == "Final words survive shutdown."
    assert window.pages.currentWidget() is window.home
    assert 'stopped' in window.face_preview.text().lower()

    # A finalization failure must still return Home and retain a recovery path.
    import sqlite3
    for dialog in window.findChildren(QDialog):
        dialog.close()
    QApplication.processEvents()
    window.audio_session = Audio()
    window.audio_session.start()
    window.session = Video()
    window.current_record_id = seed_review(window)
    monkeypatch.setattr(window.memory_store, "stop_record", lambda *_: (_ for _ in ()).throw(sqlite3.OperationalError("locked")))
    window.pages.setCurrentWidget(window.live)
    window.stop()
    wait_for(lambda: not window.stopping)
    assert window.pages.currentWidget() is window.home
    assert "could not be finalized" in window.persistence_error
    assert len(generated) == 1  # Don't generate from a failed/partial save.

    # Record creation failure must not turn into a false "Call saved" message.
    window.persistence_error = ""
    ready(window)
    monkeypatch.setattr(window.memory_store, "create_record", lambda **_: (_ for _ in ()).throw(sqlite3.OperationalError("locked")))
    window.start_call()
    wait_for(lambda: not window.starting and not window.stopping and window.audio_session is None)
    assert "Cannot safely retain transcript" in window.persistence_error
    assert "Cannot safely retain transcript" in window.status_label.text()
    assert window.turns[-1].content == "Final words survive shutdown."
    assert len(generated) == 1


def test_guidance_update_hides_old_rows_before_deferred_delete(window):
    from conversation_copilot.guidance import GuidedInterpretation, GuidanceCandidate
    window.pages.setCurrentWidget(window.live)
    window.render_guidance()
    update = GuidedInterpretation(status="insufficient_evidence", explanation="Not enough evidence for a tone.",
        replies=[GuidanceCandidate(text="Tell me more about the book.", confidence="medium", turn_ids=[1])],
        snapshot_id=1, generation=window.interpretation_generation, analyzed_order=1)
    window.guidance_display.offer(update, time.perf_counter())
    old_labels = list(window.guidance_rows["replies"].parentWidget().findChildren(desktop.QLabel))
    window.render_guidance()
    assert all(not widget.isVisible() for widget in old_labels if widget.text() == "Nothing useful to show yet.")


def test_popup_nonmodal_survives_expiry_but_not_source_deletion(window):
    source = window.memory_store.list_current_memories(window.selected_contact_id)[0]
    window.pop_out("remember", SimpleNamespace(memory_ids=[source["revision_id"]], preference_ids=[]), "Captured appointment")
    QApplication.processEvents()
    assert QApplication.activeModalWidget() is None
    popup = next(p for p in window.findChildren(desktop.Panel) if p.windowTitle() == "Related memories")
    window.invalidate_memory_context()
    assert any(l.text() == "Captured appointment" for l in popup.findChildren(desktop.QLabel))
    window.memory_store.delete_memory(source["memory_id"])
    QTest.qWait(650)
    assert any("source changed" in l.text() for l in popup.findChildren(desktop.QLabel))
    window.close()
    QApplication.processEvents()
    assert not any(p.isVisible() for p in window.findChildren(QDialog))


def test_delayed_device_discovery_and_combobox_keyboard(window, monkeypatch):
    from conversation_copilot import audio, windows
    gate = threading.Event()
    def catalog():
        gate.wait(2)
        return SimpleNamespace(microphones=[], playbacks=[], close=lambda: None)
    monkeypatch.setattr(audio, "AudioDeviceCatalog", catalog)
    monkeypatch.setattr(audio, "local_model_available", lambda: False)
    monkeypatch.setattr(windows, "list_call_windows", lambda: [])
    window.refresh_devices()
    QTest.qWait(100)
    assert window.discovery_running
    old = window.dark
    QTest.mouseClick(window.theme_button, Qt.LeftButton)
    assert window.dark != old
    assert not window.start_button.isEnabled()
    gate.set()
    wait_for(lambda: not window.discovery_running)
    assert "Install" in window.audio_status_label.text()
    # Exercise the actual custom Qt dropdown view, including keyboard selection.
    window.model_box.showPopup()
    QTest.keyClick(window.model_box, Qt.Key_End)
    QTest.keyClick(window.model_box, Qt.Key_Return)
    assert window.model_box.currentText() == "Sol 6.1 low"
    assert window.selected_live_model() == "gpt-6.1-sol"


def test_import_preview_and_contact_aliases_export(window, monkeypatch, tmp_path):
    from conversation_copilot import import_transcript as imp
    monkeypatch.setattr(imp,'f06_structured_request',lambda *a,**k:(imp.Participants(names=['Me','Alex']),None))
    generated = []
    monkeypatch.setattr(window, "start_review_job", lambda record, ledger: generated.append(record))
    desktop_data.import_chat(window)
    QApplication.processEvents()
    panel = QApplication.activeModalWidget()
    text = panel.findChild(QPlainTextEdit)
    text.setPlainText("9/1/26, 10:00 - Me: Hello\n9/1/26, 10:01 - Alex: Let us meet Friday.\n")
    click(panel, "Detect participants")
    selector = panel.findChild(desktop.QComboBox)
    wait_for(lambda: selector.isEnabled())
    assert selector.count() == 2
    selector.setCurrentText("Alex")
    click(panel, "Import and generate")
    assert len(generated) == 1
    assert window.memory_store.record_turns(generated[0])[1].speaker_role == SpeakerRole.SELECTED_CONTACT
    for dialog in window.findChildren(QDialog):
        dialog.close()
    QApplication.processEvents()
    memories = desktop_data.Memories(window, window.selected_contact_id)
    memories.show()
    memories.aliases()
    QApplication.processEvents()
    aliases = QApplication.activeModalWidget()
    monkeypatch.setattr(desktop_data, "edit_text", lambda *_a, **_k: "Alex nickname")
    click(aliases, "Add")
    assert any(r["spelling"] == "Alex nickname" for r in window.memory_store.list_aliases(window.selected_contact_id))
    listing = aliases.findChild(desktop.QListWidget)
    listing.setCurrentRow(next(i for i in range(listing.count()) if listing.item(i).text() == "Alex nickname"))
    click(aliases, "Remove")
    assert not any(r["spelling"] == "Alex nickname" for r in window.memory_store.list_aliases(window.selected_contact_id))
    aliases.close()
    target = tmp_path / "export.json"
    monkeypatch.setattr(desktop_data.QFileDialog, "getSaveFileName", lambda *_a, **_k: (str(target), ""))
    memories.export()
    import json
    payload = json.loads(target.read_text(encoding="utf-8"))
    window.memory_store.validate_export(payload)


def test_review_reject_deletes_bulk_and_stale_edit(window, monkeypatch):
    panel = desktop_data.Review(window, seed_review(window))
    panel.show()
    pending = next(m for m in panel.memories if m["state"] == "pending")
    panel.review_memories(False, all_items=True)
    wait_for(lambda: not panel.saving)
    assert not any(m["id"] == pending["id"] for m in panel.memories)
    assert window.memory_store._connection.execute("SELECT 1 FROM memory_proposals WHERE id=?", (pending["id"],)).fetchone() is None
    assert not window.memory_store.record_pending_proposals(panel.record_id)
    panel.close()
    panel = desktop_data.Review(window, seed_review(window))
    panel.show()
    errors = []
    monkeypatch.setattr(window, "report", lambda error, *_: errors.append(str(error)))
    def raced_edit(*_a, **_k):
        sentence = panel.statements[0]
        window.memory_store.edit_summary_statement(sentence["id"], "A newer correction.")
        return "Stale correction."
    monkeypatch.setattr(desktop_data, "edit_text", raced_edit)
    panel.edit_summary()
    assert errors and "changed" in errors[0]
    assert window.memory_store.summary_statements(panel.version["id"])[0]["content"] == "A newer correction."


def test_persistent_failure_copy_and_busy_store(window, monkeypatch):
    import sqlite3
    panel = desktop_data.Memories(window, window.selected_contact_id)
    panel.show()
    original = window.memory_store.list_current_memories
    monkeypatch.setattr(window.memory_store, "list_current_memories", lambda *_: (_ for _ in ()).throw(sqlite3.OperationalError("locked")))
    panel.reload()
    assert "unavailable" in panel.status.text()
    monkeypatch.setattr(window.memory_store, "list_current_memories", original)
    panel.close()
    window.pages.setCurrentWidget(window.live)
    window.set_interpretation_unavailable("Authentication unavailable", time.perf_counter())
    window.poll_interpretation(time.perf_counter())
    window.poll()
    assert "Authentication unavailable" in window.call_notice.text()
    window.current_record_id = seed_review(window)
    monkeypatch.setattr(window.memory_store, "append_turn", lambda *_: (_ for _ in ()).throw(sqlite3.OperationalError("locked")))
    monkeypatch.setattr(window, "offer_interpretation_snapshot", lambda: None)
    audio = SimpleNamespace(results=queue.SimpleQueue())
    audio.results.put(SimpleNamespace(speaker_name="Alex", speaker_role=SpeakerRole.SELECTED_CONTACT, source="fixture",
        content="Keep these words visible.", timestamp=datetime.now(timezone.utc), vocal=None))
    window.drain_audio_results(audio)
    window.poll()
    assert "could not be fully saved" in window.call_notice.text()
    assert window.turns[-1].content == "Keep these words visible."


def test_merge_has_explicit_revision_safe_confirmation(window):
    other = window.memory_store.create_contact("Alex", "another contact")
    identifier = window.memory_store.create_memory(other.id, "Alex likes sailing.")
    panel = desktop_data.Memories(window, window.selected_contact_id)
    panel.show()
    panel.merge()
    QApplication.processEvents()
    merger = QApplication.activeModalWidget()
    selector = merger.findChild(desktop.QComboBox)
    selector.setCurrentIndex(selector.findData(other.id))
    click(merger, "Merge selected contact")
    QApplication.processEvents()
    reviewer = QApplication.activeModalWidget()
    pending = next(r for r in window.memory_store.list_current_memories(window.selected_contact_id) if r["memory_id"] == identifier)
    assert pending["needs_review"]
    checks = reviewer.findChildren(desktop_data.QCheckBox)
    assert checks and not any(c.isChecked() for c in checks)
    checks[0].setChecked(True)
    click(reviewer, "Confirm selected memories")
    assert not next(r for r in window.memory_store.list_current_memories(window.selected_contact_id) if r["memory_id"] == identifier)["needs_review"]


def test_non_windows_discovery_does_not_import_capture(window, monkeypatch):
    import builtins
    original = builtins.__import__
    def guarded(name, *args, **kwargs):
        if name in {"windows", "video", "capture"} or name.startswith("winrt"):
            raise AssertionError("Windows capture imported on another platform")
        return original(name, *args, **kwargs)
    monkeypatch.setattr(desktop.sys, "platform", "darwin")
    monkeypatch.setattr(builtins, "__import__", guarded)
    window.refresh_devices()
    wait_for(lambda: not window.discovery_running)
    assert "not yet implemented" in window.audio_status_label.text()


def test_native_capture_and_qt_imports_in_either_order():
    import subprocess
    import sys
    for script in (
        "import conversation_copilot.capture; from PySide6.QtCore import Qt",
        "from PySide6.QtCore import Qt; import conversation_copilot.capture",
    ):
        result = subprocess.run([sys.executable, "-X", "faulthandler", "-c", script], capture_output=True, timeout=20)
        assert result.returncode == 0, result.stderr.decode(errors="replace")


def test_silent_poll_expires_actual_cue_labels(window, monkeypatch):
    from datetime import timedelta
    from PySide6.QtWidgets import QLabel
    from conversation_copilot import guidance
    clock=[datetime.now(timezone.utc)]
    class Clock:
        @classmethod
        def now(cls, tz=None):
            return clock[0]
    monkeypatch.setattr(guidance, 'datetime', Clock)
    update=guidance.GuidedInterpretation.model_validate({
        'snapshot_id':1,'generation':1,'analyzed_order':2,'context_at':clock[0],
        'status':'updated','social_cues':[{'kind':'interest_engagement','confidence':'medium',
        'hypothesis':'They are comparing delivery options.', 'evidence':{'explanation':'They asked about alternatives.',
        'modalities':['language'],'turn_ids':[2]}}]})
    window.stable_interpretation.offer(update,0)
    window.guidance_display.offer(update,0)
    window.render_guidance()
    def visible():
        return any('They are comparing delivery options.' in label.text() for label in window.findChildren(QLabel))
    assert visible()
    clock[0]+=timedelta(seconds=75)
    window.poll_interpretation(75)
    assert visible()
    clock[0]+=timedelta(seconds=105)
    window.poll_interpretation(180)
    QApplication.sendPostedEvents(None, 0)
    # Removed widgets await deferred destruction, so inspect the current layout.
    layout=window.guidance_rows['social_cues']
    assert not any('They are comparing delivery options.' in label.text()
        for i in range(1,layout.count()) if (widget:=layout.itemAt(i).widget())
        for label in widget.findChildren(QLabel))


def test_empty_analysis_keeps_all_guidance_until_original_expiry(window):
    from conversation_copilot import guidance as g, interpretation as ip
    evidence = ip.Evidence(explanation='Explicit discussion.', modalities=['language'], turn_ids=[1])
    initial = g.GuidedInterpretation(snapshot_id=1, generation=1, status='updated',
        tones=[ip.ToneHypothesis(kind='neutral_calm', hypothesis='Factual details.', confidence='medium', evidence=evidence)],
        social_cues=[ip.SocialCue(kind='other', hypothesis='Comparing options.', confidence='medium', evidence=evidence)],
        replies=[g.GuidanceCandidate(text='Tell me more.', confidence='medium', turn_ids=[1])],
        follow_up=[g.GuidanceCandidate(text='Which option?', confidence='medium', turn_ids=[1])],
        remember=[g.GuidanceCandidate(text='Earlier plans.', confidence='low', memory_ids=['r1'])])
    window.guidance_display.offer(initial, 10)
    local = ip.RetrievedMemoryContext(memory_id='m2', revision_id='r2', excerpt='Local memory.',
        memory_type='other', confidence='high', sensitivity_safe=False, rank=1, relevance='lexical')
    window.guidance_display.offer_local_remember([local], 1, 10)
    before = repr((window.guidance_display.items, window.guidance_display.local_remember))
    for number, status in enumerate(('insufficient_evidence', 'conflicting_evidence'), 2):
        empty = g.GuidedInterpretation(snapshot_id=number, generation=1, status=status,
            explanation='No new supported suggestions.')
        event = ip.CoordinatorEvent(ip.CoordinatorEventKind.ACCEPTED, number, empty)
        window.interpretation_coordinator = SimpleNamespace(
            snapshot=lambda: SimpleNamespace(in_flight=False), poll=lambda _: [event])
        window.poll_interpretation(10 + number)
        assert repr((window.guidance_display.items, window.guidance_display.local_remember)) == before
        for category in window.guidance_rows:
            row = window.guidance_rows[category].itemAt(1).widget()
            assert row.findChild(desktop.GuidanceLabel) is not None
    window.interpretation_coordinator = None
    window.guidance_display.offer_local_remember([], 5, 20)
    window.poll_interpretation(189)
    assert repr((window.guidance_display.items, window.guidance_display.local_remember)) == before
    window.poll_interpretation(190)
    assert all(not window.guidance_display.visible(category) for category in g.LIVE_CATEGORIES)


def test_responses_include_followups_newest_first_with_correct_controls(window):
    from conversation_copilot.guidance import GuidanceCandidate, DisplayedGuidance
    assert set(window.guidance_rows)=={'tones','social_cues','replies','remember'}
    display=window.guidance_display
    display.items['replies']=[DisplayedGuidance(GuidanceCandidate(text=f'Reply {n}',confidence='medium'),n,n,n) for n in (3,2,1)]
    display.items['follow_up']=[DisplayedGuidance(GuidanceCandidate(text='New question?',confidence='medium'),5,5,5)]
    display.last_snapshot=5
    window.render_guidance()
    layout=window.guidance_rows['replies']
    def texts():
        return [w.text() for i in range(1,layout.count()) for w in layout.itemAt(i).widget().findChildren(desktop.GuidanceLabel)]
    assert texts()==['New question?','Earlier: Reply 3','Earlier: Reply 2','Earlier: Reply 1']
    first=layout.itemAt(1).widget()
    click(first,'↗')
    popup=next(p for p in window.findChildren(QDialog) if p.isVisible())
    assert 'New question?' in [l.text() for l in popup.findChildren(desktop.QLabel)]
    popup.close()
    click(first,'×')
    assert not display.visible('follow_up')
    assert texts()==['Earlier: Reply 3','Earlier: Reply 2','Earlier: Reply 1']


def test_live_ambiguous_memories_are_uncertain_candidates_not_direct_labels(window, monkeypatch):
    from conversation_copilot.interpretation import InterpretationConfidence
    memory_id=window.memory_store.create_memory(window.selected_contact_id,'Alex lost a restaurant position.')
    revision=window.memory_store.current_revision(memory_id)
    match=SimpleNamespace(memory_id=memory_id,revision_id=revision['id'],content=revision['content'],
        memory_type='event_date',confidence='high',cloud_eligible=True,rank=1,reason='semantic')
    monkeypatch.setattr(memory.MemoryStore,'retrieve',lambda *a,**k:SimpleNamespace(matches=[match],ambiguous=True,semantic_available=True))
    monkeypatch.setattr(window,'submit_local',lambda _name,work:work())
    window.turns=[ConversationTurn(speaker_name='Alex',speaker_role='selected_contact',source='test',
        content='There is no paycheck now.',timestamp=datetime.now(timezone.utc),display_order=1)]
    window.offer_interpretation_snapshot();window.poll_memory_results()
    snapshot=window.latest_interpretation_snapshot
    assert snapshot and snapshot.memories
    assert snapshot.memories[0].confidence==InterpretationConfidence.LOW
    assert 'uncertain' in snapshot.memories[0].relevance
    shown = window.guidance_display.visible('remember')
    assert len(shown)==1 and shown[0].candidate.confidence=='low'
    assert shown[0].candidate.text.startswith('Possible match: ')
    assert 'uncertain' in window.memory_status_label.text()


def test_tone_context_views_and_popup_keep_original_description(window):
    from conversation_copilot.guidance import GuidedInterpretation
    from PySide6.QtWidgets import QLabel
    update=GuidedInterpretation.model_validate({'snapshot_id':1,'generation':1,'status':'updated',
        'tones':[{'kind':'tense_negative','confidence':'medium','hypothesis':'They describe a difficult week.',
        'evidence':{'explanation':'Explicit difficult wording.','modalities':['language'],'turn_ids':[2]}}]})
    window.guidance_display.offer(update,0);window.render_guidance()
    tone=window.guidance_rows['tones'].itemAt(1).widget()
    assert tone.findChild(desktop.GuidanceLabel).text()=='Negative / tense\nThey describe a difficult week.'
    context=window.guidance_rows['social_cues'].itemAt(1).widget()
    assert context.findChild(desktop.GuidanceLabel).text()=='Context: They describe a difficult week.'
    QTest.mouseClick(next(b for b in tone.findChildren(QPushButton) if b.accessibleName()=='Pop out'),Qt.LeftButton)
    popup=next(p for p in window.findChildren(desktop.Panel) if p.windowTitle()=='Possible tones')
    assert any('Negative / tense\nThey describe a difficult week.'==x.text() for x in popup.findChildren(QLabel))
    assert not popup.isModal();popup.close()
    QTest.mouseClick(next(b for b in context.findChildren(QPushButton) if b.accessibleName()=='Dismiss'),Qt.LeftButton)
    assert not window.guidance_display.tone_items() and not window.guidance_display.context_items()
    assert update.tones[0].hypothesis=='They describe a difficult week.'


@pytest.mark.parametrize('kind,expected', [
    ('positive_warm','Positive / warm'),('neutral_calm','Neutral / factual'),
    ('sad_low_energy','Downbeat / sad'),('tense_negative','Negative / tense'),
    ('energetic_high_energy','Energetic'),('emotionally_intense','Strongly expressed'),
    ('humor','Playful / humorous'),('sarcasm','Possibly sarcastic')])
def test_all_tone_labels_render_pop_out_and_dismiss(window,kind,expected):
    from conversation_copilot.guidance import GuidedInterpretation
    from PySide6.QtWidgets import QLabel
    category='social_cues' if kind in {'humor','sarcasm'} else 'tones'
    update=GuidedInterpretation.model_validate({'snapshot_id':1,'generation':1,'status':'updated',
        category:[{'kind':kind,'confidence':'medium','hypothesis':'Original observation.',
                   'evidence':{'explanation':'Explicit evidence.','modalities':['language'],'turn_ids':[2]}}]})
    window.guidance_display.offer(update,0);window.render_guidance()
    tone=window.guidance_rows['tones'].itemAt(1).widget()
    assert tone.findChild(desktop.GuidanceLabel).text()==expected+'\nOriginal observation.'
    QTest.mouseClick(next(b for b in tone.findChildren(QPushButton) if b.accessibleName()=='Pop out'),Qt.LeftButton)
    popup=next(p for p in window.findChildren(desktop.Panel) if p.windowTitle()=='Possible tones')
    assert any(x.text()==expected+'\nOriginal observation.' for x in popup.findChildren(QLabel))
    assert not popup.isModal();popup.close()
    QTest.mouseClick(next(b for b in tone.findChildren(QPushButton) if b.accessibleName()=='Dismiss'),Qt.LeftButton)
    assert not window.guidance_display.tone_items() and not window.guidance_display.context_items()
    assert getattr(update,category)[0].hypothesis=='Original observation.'


def test_section_numbers_highlight_new_items_then_expire_without_relighting(window, monkeypatch):
    from conversation_copilot.guidance import GuidedInterpretation
    from PySide6.QtWidgets import QLabel
    clock = [100.0]
    monkeypatch.setattr(desktop.time, 'perf_counter', lambda: clock[0])
    update = GuidedInterpretation.model_validate({'snapshot_id':1,'generation':1,'status':'insufficient_evidence',
        'explanation':'No affect evidence.',
        'replies':[{'text':text,'confidence':'medium','turn_ids':[1]}
                   for text in ('Tell me more.', 'That sounds difficult.')]})
    window.guidance_display.offer(update,100)
    window.render_guidance()
    def badges():
        layout = window.guidance_rows['replies']
        return [layout.itemAt(i).widget().findChild(QLabel,'guidance_number') for i in range(1,layout.count())]
    assert [b.text() for b in badges()] == ['1','2']
    assert all(b.property('new_item') and 'new' in b.accessibleName() for b in badges())
    button = window.guidance_rows['replies'].itemAt(1).widget().findChild(QPushButton)
    button.setFocus()
    first_badge = badges()[0]
    clock[0] = 112
    window.poll_interpretation(112)
    assert all(not b.property('new_item') for b in badges())
    assert badges()[0] is first_badge
    assert QApplication.focusWidget() is button
    window.guidance_display.offer(update.model_copy(update={'snapshot_id':2}),113)
    clock[0] = 113
    window.render_guidance()
    assert all(not b.property('new_item') for b in badges())
    window.guidance_display.dismiss('replies',0)
    window.render_guidance()
    assert [b.text() for b in badges()] == ['1']
    assert not badges()[0].property('new_item')


def test_retained_cue_buttons_target_visible_item(window):
    from conversation_copilot.guidance import GuidedInterpretation
    from PySide6.QtWidgets import QLabel
    for n in (1,2):
        update=GuidedInterpretation.model_validate({'snapshot_id':n,'generation':1,'analyzed_order':n,
            'context_at':datetime.now(timezone.utc),'status':'updated','social_cues':[{'kind':'interest_engagement',
            'confidence':'medium','hypothesis':f'Compare option {n}.','evidence':{'explanation':'Asking to compare.',
            'modalities':['language'],'turn_ids':[n]}}]})
        window.guidance_display.offer(update,n)
    window.render_guidance();layout=window.guidance_rows['social_cues']
    assert 'Compare option 2.' in layout.itemAt(1).widget().findChild(desktop.GuidanceLabel).text()
    older=layout.itemAt(2).widget();assert older.findChild(desktop.GuidanceLabel).text()=='Earlier: Cue: Compare option 1.'
    QTest.mouseClick(next(b for b in older.findChildren(QPushButton) if b.accessibleName()=='Dismiss'),Qt.LeftButton)
    assert [x.candidate.hypothesis for x in window.guidance_display.visible('social_cues')]==['Compare option 2.']


def test_first_dispatch_timer_and_earlier_label_on_empty_update(window, monkeypatch):
    from conversation_copilot.guidance import GuidedInterpretation,GuidanceCandidate
    calls = []
    window.model_box.setCurrentIndex(1)
    monkeypatch.setattr(desktop, 'OpenAIInterpreter',
        lambda **kw: (calls.append(kw), SimpleNamespace(_client=None))[1])
    monkeypatch.setattr(desktop.time,'perf_counter',lambda:100.)
    window.begin_interpretation_session()
    assert window.interpretation_coordinator._first_request_at==100.
    assert calls[0]["model"] == "gpt-6.1-sol" and calls[0]["reasoning"] == "low"
    update=GuidedInterpretation(snapshot_id=1,generation=1,analyzed_order=1,status='insufficient_evidence',explanation='No affect evidence.',
        replies=[GuidanceCandidate(text='Could you clarify?',confidence='medium',turn_ids=[1])])
    window.guidance_display.offer(update,100);window.render_guidance()
    window.guidance_display.offer(update.model_copy(update={'snapshot_id':2,'replies':[]}),105);window.render_guidance()
    from PySide6.QtWidgets import QLabel
    assert window.guidance_rows['replies'].itemAt(1).widget().findChild(desktop.GuidanceLabel).text()=='Earlier: Could you clarify?'


def test_batched_topic_change_keeps_displayed_uncertain_reply(window, monkeypatch):
    from conversation_copilot.guidance import GuidedInterpretation,GuidanceCandidate
    from PySide6.QtWidgets import QLabel
    update=GuidedInterpretation(snapshot_id=1,generation=1,analyzed_order=1,status='insufficient_evidence',explanation='No affect evidence.',
        replies=[GuidanceCandidate(text='How was the trip?',confidence='low',memory_ids=['uncertain-revision'])])
    window.guidance_display.offer(update,0);window.render_guidance()
    assert window.guidance_rows['replies'].itemAt(1).widget().findChild(desktop.GuidanceLabel).text().startswith('Possible connection:')
    now=datetime.now(timezone.utc)
    window.turns=[ConversationTurn(speaker_name='Alex',speaker_role='selected_contact',source='test',timestamp=now,display_order=n,content=text)
        for n,text in [(1,'Moving on, let us talk about something else.'),(2,'The weather is nice.')]]
    monkeypatch.setattr(window,'submit_local',lambda *a:None)
    window.offer_interpretation_snapshot()
    assert window.guidance_display.visible('replies')


@pytest.mark.parametrize('text', ['We can leave that alone. The park sounds good?',
    "I'd rather not talk about the numbers today.", 'Moving on, what about dinner?',
    'Correction, the time is already set.', 'Would a free walk help?'])
def test_speech_keeps_all_guidance_visible(window, monkeypatch, text):
    from conversation_copilot import interpretation as ip, guidance as g
    evidence=ip.Evidence(explanation='Explicit concern.',modalities=['language'],turn_ids=[1])
    update=g.GuidedInterpretation(snapshot_id=1,generation=1,status='updated',
        tones=[ip.ToneHypothesis(kind='tense_negative',confidence='medium',hypothesis='They describe financial pressure.',evidence=evidence)],
        social_cues=[ip.SocialCue(kind='other',confidence='medium',hypothesis='They explain a spending limit.',evidence=evidence)],
        replies=[g.GuidanceCandidate(text='Would a free walk help?',confidence='medium',turn_ids=[1])],
        follow_up=[g.GuidanceCandidate(text='Which park works?',confidence='medium',turn_ids=[1])],
        remember=[g.GuidanceCandidate(text='Possible job context.',confidence='low',memory_ids=['r'])])
    window.guidance_display.offer(update,10)
    window.render_guidance()
    window.turns=[ConversationTurn(speaker_name='You',speaker_role='user',source='test',
        content=text,timestamp=datetime.now(timezone.utc),display_order=2)]
    monkeypatch.setattr(window,'submit_local',lambda *a:None)
    window.offer_interpretation_snapshot()
    assert window.guidance_display.tone_items() and window.guidance_display.context_items()
    assert window.guidance_display.response_items() and window.guidance_display.visible('remember')
    for key in window.guidance_rows:
        assert window.guidance_rows[key].itemAt(1).widget().findChild(desktop.GuidanceLabel)
    window.set_interpretation_unavailable('Request timed out.',20)
    window.render_interpretation(replaced=True)
    assert all(window.guidance_display.visible(key) for key in g.LIVE_CATEGORIES)


def test_topic_change_keeps_local_memory_row_and_wrapped_rows_fit(window, monkeypatch):
    from conversation_copilot.interpretation import RetrievedMemoryContext
    from conversation_copilot.guidance import GuidedInterpretation,GuidanceCandidate
    from PySide6.QtWidgets import QLabel
    local=RetrievedMemoryContext(memory_id='m',revision_id='r',excerpt='Local only memory.',memory_type='other',confidence='high',sensitivity_safe=False,rank=1,relevance='lexical')
    window.guidance_display.offer_local_remember([local],1,0);window.render_guidance()
    window.turns=[ConversationTurn(speaker_name='Alex',speaker_role='selected_contact',source='test',timestamp=datetime.now(timezone.utc),display_order=1,content='Moving on, let us talk about something else.')]
    monkeypatch.setattr(window,'submit_local',lambda *a:None)
    window.offer_interpretation_snapshot()
    assert 'Local only memory.' in window.guidance_rows['remember'].itemAt(1).widget().findChild(desktop.GuidanceLabel).text()
    update=GuidedInterpretation(snapshot_id=2,generation=1,analyzed_order=1,status='insufficient_evidence',explanation='No affect evidence.',
        replies=[GuidanceCandidate(text=f'Option {i}: Could you explain the specific alternatives you are considering before deciding what to do next?',confidence='medium',turn_ids=[1]) for i in range(4)])
    window.guidance_display.offer(update,1);window.pages.setCurrentWidget(window.live);window.render_guidance();window.resize(900,780)
    for _ in range(10):QApplication.processEvents()
    for wording in window.findChildren(desktop.GuidanceLabel):
        if wording.isVisible():
            assert wording.height()>=wording.heightForWidth(wording.width())
            assert wording.parentWidget().height()>=wording.height()+6


def test_older_analysis_cannot_use_newer_snapshot_memory_confidence(window, monkeypatch):
    from conversation_copilot import interpretation as ip,guidance as g
    now=datetime.now(timezone.utc)
    window.turns=[ConversationTurn(speaker_name='Alex',speaker_role='selected_contact',source='test',timestamp=now,display_order=1,content='Money is tight.')]
    context=ip.RetrievedMemoryContext(memory_id='m',revision_id='r',excerpt='An earlier job loss.',memory_type='other',confidence='high',sensitivity_safe=True,rank=1,relevance='lexical')
    window.latest_interpretation_snapshot=ip.build_snapshot(window.turns,snapshot_id=2,generation=1,created_at=now,contact_id=window.selected_contact_id,retrieved_memories=[context])
    # Existing direct context must also be withdrawn, not retained by the stable card.
    window.stable_interpretation.offer_memory_possibilities([context],0)
    result=g.GuidedInterpretation(snapshot_id=1,generation=1,analyzed_order=1,context_at=now,status='insufficient_evidence',explanation='No affect evidence.',
        remember=[g.GuidanceCandidate(text='Possibly related: an earlier job loss.',confidence='low',memory_ids=['r'],turn_ids=[1])])
    event=ip.CoordinatorEvent(ip.CoordinatorEventKind.ACCEPTED,1,result)
    window.interpretation_coordinator=SimpleNamespace(snapshot=lambda:SimpleNamespace(in_flight=False),poll=lambda _: [event])
    window.poll_interpretation(1)
    assert not window.stable_interpretation.memory_possibilities
    assert 'uncertain' in window.memory_status_label.text()
    window.interpretation_coordinator=None


def test_f08_editor_keeps_blank_input_and_unchanged_save_is_noop(window):
    observed = []
    def blank_then_valid():
        dialog = QApplication.activeModalWidget()
        field = dialog.findChild(QPlainTextEdit)
        field.setPlainText('   ')
        click(dialog, 'Save')
        observed.append(dialog.isVisible())
        observed.append(any('Enter text' in x.text() for x in dialog.findChildren(desktop.QLabel)))
        field.setPlainText('A corrected memory.')
        click(dialog, 'Save')
    QTimer.singleShot(0, blank_then_valid)
    assert desktop.edit_text(window, 'Edit memory', 'Original memory.') == 'A corrected memory.'
    assert observed == [True, True]
    QTimer.singleShot(0, lambda: click(QApplication.activeModalWidget(), 'Save'))
    assert desktop.edit_text(window, 'Edit memory', 'Unchanged memory.') is None
    QTimer.singleShot(0, lambda: click(QApplication.activeModalWidget(), 'Save'))
    assert desktop.edit_text(window, 'Edit memory', 'Keep\u00a0nonbreaking\u2028text.') is None


def test_f08_import_disclosure_and_shutdown_cancel(window, monkeypatch):
    panel = desktop_data.import_chat(window)
    panel.findChild(QPlainTextEdit).setPlainText('Me: Hello\nAlex: Keep this unsaved import.')
    assert any('20 shortened lines' in x.text() for x in panel.findChildren(desktop.QLabel))
    monkeypatch.setattr(desktop_data, 'confirm', lambda *_a, **_k: False)
    assert not window.close()
    assert window.isVisible() and panel.isVisible() and window.timer.isActive()
    assert not window.closed and not window.closing
    assert window.memory_store.get_contact(window.selected_contact_id)
    monkeypatch.setattr(desktop_data, 'confirm', lambda *_a, **_k: True)
    panel.close()


def test_f08_long_combo_keeps_popup_and_list_width_together(window):
    selector = desktop.combo(['Long contact name ' * 30])
    selector.show()
    try:
        for width in (300, 900):
            selector.resize(width, 40)
            selector.showPopup()
            QApplication.processEvents()
            popup = selector.view().window()
            assert popup.width() <= min(selector.screen().availableGeometry().width(), max(width, 640))
            assert selector.view().width() >= popup.width() - 20
            selector.hidePopup()
    finally:
        selector.close()


def test_f08_undated_transcript_and_local_time(window):
    record = window.memory_store.create_record(source_kind='import', source_label='Undated fixture',
        timezone_name='UTC', contact_id=window.selected_contact_id, status='imported',
        turns=[ConversationTurn(speaker_name='Alex', speaker_role=SpeakerRole.SELECTED_CONTACT,
               timestamp=None, source='text_import', content='Keep the original words.', display_order=1)])
    panel = desktop_data.Review(window, record)
    panel.show()
    panel.view_transcript()
    transcript = QApplication.activeModalWidget().findChild(QPlainTextEdit).toPlainText()
    assert 'Date unavailable · Alex: Keep the original words.' == transcript
    stamp = datetime(2026, 9, 26, 14, 13, 24, 123456, tzinfo=timezone.utc)
    rendered = desktop.display_time(stamp)
    assert rendered == stamp.astimezone().isoformat(sep=' ', timespec='seconds')
    assert '123456' not in rendered


def test_f08_history_refreshes_after_review_without_losing_selection(window):
    record = seed_review(window)
    with window.memory_store.transaction() as db:
        db.execute("UPDATE conversation_records SET analysis_state='pending' WHERE id=?", (record,))
    history = desktop_data.History(window, window.selected_contact_id)
    history.show()
    history.listing.setCurrentRow(next(i for i, r in enumerate(history.records) if r['id'] == record))
    assert 'Summary: draft' in history.listing.currentItem().text()
    history.review()
    panel = window.review_dialogs[record]
    panel.approve_summary(combined=True)
    wait_for(lambda: not panel.saving)
    panel.close()
    QApplication.processEvents()
    assert history.selected()['id'] == record
    assert 'Summary: approved' in history.listing.currentItem().text()


def test_f08_import_opens_real_review(window, monkeypatch):
    from conversation_copilot import import_transcript as imp
    monkeypatch.setattr(imp, 'f06_structured_request', lambda *a, **k:
        (imp.Participants(names=['Me', 'Alex'], suggested_contact='Alex'), None))
    generated = []
    monkeypatch.setattr(window, 'start_review_job', lambda rid, ledger: generated.append(rid))
    panel = desktop_data.import_chat(window)
    panel.findChild(QPlainTextEdit).setPlainText('Me: Hello\nAlex: Bring the notebook.')
    click(panel, 'Detect participants')
    wait_for(lambda: panel.findChild(desktop.QComboBox).isEnabled())
    click(panel, 'Import and generate')
    assert len(generated) == 1
    assert window.review_dialogs[generated[0]].isVisible()
    assert not any(p.windowTitle() == 'Import text' for p in window.findChildren(QDialog))


def test_f08_import_discard_can_be_cancelled(window, monkeypatch):
    panel = desktop_data.import_chat(window)
    panel.findChild(QPlainTextEdit).setPlainText('Me: Hello\nAlex: Unsaved text.')
    monkeypatch.setattr(desktop_data, 'confirm', lambda *_a, **_k: False)
    panel.close()
    assert panel.isVisible() and 'Unsaved text.' in panel.findChild(QPlainTextEdit).toPlainText()
    monkeypatch.setattr(desktop_data, 'confirm', lambda *_a, **_k: True)
    panel.close()


def test_f08_validation_error_does_not_expose_input_or_internal_link(window, monkeypatch):
    from conversation_copilot import import_transcript as imp
    import json
    exported = json.dumps(window.memory_store.export_json(contact_id=window.selected_contact_id, all_data=False))
    requests = []
    def malformed_response(schema, payload, *args, **kwargs):
        requests.append(payload)
        return schema(names=['private fixture text'] * 9), None
    monkeypatch.setattr(imp, 'f06_structured_request', malformed_response)
    panel = desktop_data.import_chat(window)
    editor = panel.findChild(QPlainTextEdit)
    editor.setPlainText(exported)
    click(panel, 'Detect participants')
    wait_for(lambda: not editor.isReadOnly())
    assert requests and requests[0]['lines'] == imp.participant_sample(exported)
    text = ' '.join(x.text() for x in panel.findChildren(desktop.QLabel))
    assert 'could not be validated' in text
    assert 'private fixture text' not in text and 'pydantic' not in text and 'again..' not in text
    assert not next(b for b in panel.findChildren(QPushButton) if b.text() == 'Import and generate').isEnabled()


def test_f08_transferred_memory_is_labelled_and_not_retrievable(window):
    other = window.memory_store.create_contact('F08 other')
    identifier = window.memory_store.create_memory(other.id, 'F08 other likes sailing.')
    window.memory_store.merge_contacts(window.selected_contact_id, other.id)
    panel = desktop_data.Memories(window, window.selected_contact_id)
    assert any('Transferred memory' in x.text() for x in panel.findChildren(desktop.QLabel))
    assert identifier not in [r.memory_id for r in window.memory_store.retrieve(window.selected_contact_id, 'sailing').matches]


def test_f08_duplicate_contact_requires_disambiguation(window, monkeypatch):
    errors = []
    monkeypatch.setattr(window, 'report', lambda error, *_: errors.append(str(error)))
    contact = window.memory_store.get_contact(window.selected_contact_id)
    before = len(window.memory_store.list_contacts())
    window.create_contact()
    panel = QApplication.activeModalWidget()
    fields = panel.findChildren(QLineEdit)
    fields[0].setText(contact.display_name.upper())
    fields[1].setText(contact.disambiguator or '')
    click(panel, 'Create')
    assert errors and 'already exists' in errors[-1]
    assert len(window.memory_store.list_contacts()) == before and panel.isVisible()
    fields[1].setText('Another person')
    click(panel, 'Create')
    assert len(window.memory_store.list_contacts()) == before + 1


def test_f08_alias_duplicate_and_shared_alias_confirmation(window, monkeypatch):
    errors = []
    monkeypatch.setattr(window, 'report', lambda error, *_: errors.append(str(error)))
    panel = desktop_data.Memories(window, window.selected_contact_id)
    panel.show()
    panel.aliases()
    aliases = QApplication.activeModalWidget()
    name = window.memory_store.get_contact(window.selected_contact_id).display_name
    monkeypatch.setattr(desktop_data, 'edit_text', lambda *_a, **_k: name.upper())
    click(aliases, 'Add')
    assert errors and 'already belongs' in errors[-1]
    other = window.memory_store.create_contact('Shared F08 name')
    monkeypatch.setattr(desktop_data, 'edit_text', lambda *_a, **_k: other.display_name)
    monkeypatch.setattr(desktop_data, 'confirm', lambda *_a, **_k: False)
    click(aliases, 'Add')
    assert not any(r['spelling'] == other.display_name for r in window.memory_store.list_aliases(window.selected_contact_id))
    monkeypatch.setattr(desktop_data, 'confirm', lambda *_a, **_k: True)
    click(aliases, 'Add')
    with pytest.raises(memory.AmbiguousContact):
        window.memory_store.resolve_contact(other.display_name)


def test_f08_guidance_rebuild_does_not_focus_end_call(window):
    from conversation_copilot.guidance import GuidedInterpretation
    window.pages.setCurrentWidget(window.live)
    update = GuidedInterpretation.model_validate({'snapshot_id':1, 'generation':1, 'status':'updated',
        'tones':[{'kind':'neutral_calm', 'confidence':'medium', 'hypothesis':'A factual plan.',
                  'evidence':{'explanation':'A stated plan.', 'modalities':['language'], 'turn_ids':[1]}}]})
    window.guidance_display.offer(update, 0)
    window.render_guidance()
    action = next(b for b in window.guidance_rows['tones'].itemAt(1).widget().findChildren(QPushButton)
                  if b.accessibleName() == 'Dismiss')
    window.activateWindow()
    action.setFocus()
    ended = []
    window.stop_button.clicked.connect(lambda: ended.append(True))
    QTest.mouseClick(action, Qt.LeftButton)
    QApplication.processEvents()
    assert QApplication.focusWidget() is not window.stop_button
    QTest.keyClick(QApplication.focusWidget(), Qt.Key_Space)
    assert not ended
    assert not window.guidance_display.tone_items() and not window.guidance_display.context_items()


def test_f08_retained_memory_status_matches_visible_guidance(window):
    from conversation_copilot.interpretation import RetrievedMemoryContext
    context = RetrievedMemoryContext(memory_id='fixture-memory', revision_id='fixture-revision',
        excerpt='A previously approved appointment.', memory_type='other', confidence='high',
        sensitivity_safe=False, rank=1, relevance='lexical')
    window.stable_interpretation.offer_memory_possibilities([context], 0)
    window.guidance_display.offer_local_remember([context], 1, 0)
    window.poll_interpretation(30)
    assert window.guidance_display.visible('remember')
    assert 'Showing 1 retained memory' in window.memory_status_label.text()


@pytest.mark.parametrize('ambiguous', [False, True])
def test_retrieved_semantic_memory_is_visible_without_cloud_result(window, monkeypatch, ambiguous):
    from conversation_copilot import interpretation as ip, guidance as g
    clock = [10.0]
    monkeypatch.setattr(desktop.time, 'perf_counter', lambda: clock[0])
    memory_id = window.memory_store.create_memory(window.selected_contact_id, 'The contact recently lost a job.')
    revision_id = window.memory_store.current_revision(memory_id)['id']
    context = ip.RetrievedMemoryContext(memory_id=memory_id, revision_id=revision_id,
        excerpt='The contact recently lost a job.', memory_type='other', confidence='high',
        sensitivity_safe=True, rank=1, relevance='semantic')
    private = context.model_copy(update={'revision_id':'private', 'sensitivity_safe':False})
    turn = ConversationTurn(speaker_name='Contact', speaker_role='selected_contact', source='test',
        content="Money's been really tight.", timestamp=datetime.now(timezone.utc), display_order=1)
    window.turns = [turn]
    snapshot = ip.build_snapshot([turn],snapshot_id=1,generation=window.interpretation_generation,
        contact_id=window.selected_contact_id,retrieved_memories=[context])
    window.memory_snapshot_results.put((window.interpretation_generation,1,snapshot,ambiguous,[context,private],True,None,''))
    window.poll_memory_results()
    items = window.guidance_display.visible('remember')
    assert len(items)==1 and items[0].candidate.text.startswith('Possible match: ')
    assert items[0].candidate.confidence=='low' and items[0].candidate.memory_ids==[revision_id]
    window.guidance_display.offer(g.GuidedInterpretation(snapshot_id=1,generation=window.interpretation_generation,
        status='insufficient_evidence',explanation='No new supported observation.'),11)
    assert window.guidance_display.visible('remember')  # Empty API memory output cannot hide retrieval.
    window.guidance_display.offer(g.GuidedInterpretation(snapshot_id=2,generation=window.interpretation_generation,
        status='insufficient_evidence',explanation='No new supported observation.',remember=[g.GuidanceCandidate(text='Possibly related: a previous job loss.',
        confidence='low',memory_ids=[revision_id])]),12)
    items=window.guidance_display.visible('remember')
    assert len(items)==1 and items[0].candidate.text.startswith('Possibly related:')
    window.guidance_display.dismiss('remember',0)
    window.guidance_display.offer_local_remember([context],3,13)
    assert not window.guidance_display.visible('remember')
    window.guidance_display.invalidate(new_topic=True)
    window.guidance_display.offer_local_remember([context],4,20)
    window.guidance_display.tick(199)
    assert window.guidance_display.visible('remember')
    window.guidance_display.tick(200)
    assert not window.guidance_display.visible('remember')


def test_semantic_memory_fallback_rejects_stale_session(window):
    from conversation_copilot import interpretation as ip
    context=ip.RetrievedMemoryContext(memory_id='m',revision_id='r',excerpt='Old contact memory.',
        memory_type='other',confidence='high',sensitivity_safe=True,rank=1,relevance='semantic')
    window.memory_snapshot_results.put((window.interpretation_generation-1,1,None,False,[context],True,None,''))
    window.poll_memory_results()
    assert not window.guidance_display.visible('remember')


@pytest.mark.parametrize('boundary', ["I'd rather not talk about the numbers today.", 'We can leave that alone.'])
def test_memory_retrieval_keeps_context_through_discussion_boundary(window, monkeypatch, boundary):
    from conversation_copilot import interpretation as ip
    queries=[]
    monkeypatch.setattr(memory.MemoryStore,'retrieve',lambda _store,_cid,query,**kw:
        queries.append((query,kw)) or SimpleNamespace(matches=[],ambiguous=False,semantic_available=True))
    monkeypatch.setattr(window,'submit_local',lambda _name,work:work())
    now=datetime.now(timezone.utc)
    window.turns=[ConversationTurn(speaker_name='Contact',speaker_role='selected_contact',source='test',
        content=text,timestamp=now,display_order=n) for n,text in enumerate(
            ['Money is tight.', 'Even a meal out adds up.', 'I still want to see you.'],1)]
    window.offer_interpretation_snapshot() # Leave this older worker result queued.
    window.turns.append(window.turns[0].model_copy(update={'content':boundary,'display_order':4}))
    window.offer_interpretation_snapshot()
    window.poll_memory_results()
    assert window.latest_interpretation_snapshot.snapshot_id==2
    assert 'Money is tight' in queries[-1][1]['semantic_query']
    assert 'Money is tight' in queries[-1][1]['contact_cue_query']
    assert not window.guidance_display.visible('remember')


def test_f08_empty_actions_and_export_cancel_have_current_feedback(window, monkeypatch):
    ready(window)
    assert window.audio_status_label.text() == 'Both audio devices selected.'
    window.microphone_box.setCurrentIndex(-1)
    assert 'Choose both' in window.audio_status_label.text()
    panel = desktop_data.Memories(window, window.selected_contact_id)
    panel.ask()
    assert panel.status.text() == 'Enter a question first.'
    panel.status.setText('Exported.')
    monkeypatch.setattr(desktop_data.QFileDialog, 'getSaveFileName', lambda *_a, **_k: ('', ''))
    panel.export()
    assert panel.status.text().startswith('Export cancelled.')
    review = desktop_data.Review(window, seed_review(window))
    review.review_memories(True)
    assert review.status.text() == 'Select pending memories first.'
