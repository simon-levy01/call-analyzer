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
        QTest.qWait(20)
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


def test_home_readiness_theme_and_modal_controls(window, monkeypatch):
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
    click(panel, "Ask")
    wait_for(lambda: not panel.running)
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
    assert not window.memory_store.record_pending_proposals(record)
    click(panel, "Approve summary")
    assert panel.version["state"] == "approved"
    panel.sentences.setCurrentRow(0)
    monkeypatch.setattr(desktop_data, "edit_text", lambda *_a, **_k: "They planned to meet Saturday.")
    panel.edit_sentence()
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
    click(window, "Start call  →")
    wait_for(lambda: window.audio_session is not None)
    assert window.session is preview and window.pages.currentWidget() is window.live
    record = window.current_record_id
    click(window, "■  END CALL")
    wait_for(lambda: window.audio_session is None and not window.stopping)
    assert generated == [record]
    assert window.memory_store.record_turns(record)[-1].content == "Final words survive shutdown."
    assert window.pages.currentWidget() is window.home

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
    popup = next(p for p in window.findChildren(desktop.Panel) if p.windowTitle() == "Remember")
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
    assert window.model_box.currentText() == "Terra low"


def test_import_preview_and_contact_aliases_export(window, monkeypatch, tmp_path):
    generated = []
    monkeypatch.setattr(window, "start_review_job", lambda record, ledger: generated.append(record))
    desktop_data.import_chat(window)
    QApplication.processEvents()
    panel = QApplication.activeModalWidget()
    text = panel.findChild(QPlainTextEdit)
    text.setPlainText("9/1/26, 10:00 - Me: Hello\n9/1/26, 10:01 - Alex: Let us meet Friday.\n")
    click(panel, "Preview")
    selector = panel.findChild(desktop.QComboBox)
    assert selector.count() == 2
    selector.setCurrentText("Me")
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


def test_review_reject_reopen_bulk_and_stale_edit(window, monkeypatch):
    panel = desktop_data.Review(window, seed_review(window))
    panel.show()
    pending = next(m for m in panel.memories if m["state"] == "pending")
    panel.review_memories(False, all_items=True)
    assert next(m for m in panel.memories if m["id"] == pending["id"])["state"] == "rejected"
    panel.reopen(pending)
    assert window.memory_store.record_pending_proposals(panel.record_id)
    panel.approve_summary(combined=True)
    assert panel.version["state"] == "approved"
    assert not window.memory_store.record_pending_proposals(panel.record_id)
    panel.close()
    panel = desktop_data.Review(window, seed_review(window))
    panel.show()
    errors = []
    monkeypatch.setattr(window, "report", lambda error, *_: errors.append(str(error)))
    panel.sentences.setCurrentRow(0)
    def raced_edit(*_a, **_k):
        sentence = panel.selected_sentence()
        window.memory_store.edit_summary_statement(sentence["id"], "A newer correction.")
        return "Stale correction."
    monkeypatch.setattr(desktop_data, "edit_text", raced_edit)
    panel.edit_sentence()
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
