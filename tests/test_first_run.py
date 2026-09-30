import threading
import time
from pathlib import Path
from datetime import datetime, timezone

import pytest
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication

from conversation_copilot import desktop, memory, setup_dialog, interpretation
from conversation_copilot.models import ConversationTurn


@pytest.fixture
def fresh_app(monkeypatch, tmp_path):
    app = QApplication.instance() or QApplication([])
    monkeypatch.setattr(interpretation.sys, 'frozen', True, raising=False)
    monkeypatch.setenv('LOCALAPPDATA', str(tmp_path))
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    monkeypatch.setattr(desktop, 'QSettings', lambda *_: QSettings(str(tmp_path / 'settings.ini'), QSettings.IniFormat))
    window = desktop.Desktop(discover=False)
    window.show()
    monkeypatch.setattr(window, 'refresh_devices', lambda: None)
    monkeypatch.setattr(window, 'schedule_semantic_backfill', lambda: None)
    yield window
    deadline = time.monotonic() + 3
    while window.pending_jobs and time.monotonic() < deadline:
        app.processEvents()
        time.sleep(.01)
    assert window.pending_jobs == 0
    window.close()
    app.processEvents()


def finish_job(window):
    deadline = time.monotonic() + 3
    while window.pending_jobs and time.monotonic() < deadline:
        QApplication.processEvents()
        time.sleep(.01)
    assert window.pending_jobs == 0


def fake_models(monkeypatch, window, *, fail=False):
    ready = {'audio': False, 'memory': False}
    installs = []
    monkeypatch.setattr(setup_dialog.audio, 'prepare_transcription_runtime', lambda: None)
    monkeypatch.setattr(setup_dialog.audio, 'local_model_available', lambda: ready['audio'])
    monkeypatch.setattr(setup_dialog.audio, '_load_local_model', lambda: object())
    monkeypatch.setattr(setup_dialog.semantic, 'model_ready', lambda _: ready['memory'])
    def audio_install():
        installs.append('audio')
        if fail:
            raise OSError('Download interrupted')
        ready['audio'] = True
    def memory_install(cache):
        installs.append('memory')
        ready['memory'] = True
        cache.mkdir(parents=True, exist_ok=True)
        (cache / setup_dialog.semantic._MARKER).write_text('{}')
    monkeypatch.setattr(setup_dialog.audio, 'install_local_model', audio_install)
    monkeypatch.setattr(setup_dialog.semantic, 'install_model', memory_install)
    return ready, installs


def test_fresh_setup_and_saved_data_survive_reopening_without_redownload(fresh_app, monkeypatch):
    window = fresh_app
    ready, installs = fake_models(monkeypatch, window)
    assert not window.memory_store.list_contacts()
    window.check_initial_setup()
    finish_job(window)
    panel = window.setup_dialog
    assert panel.isVisible()
    panel.key.setText('fixture-not-a-real-key')
    panel.start()
    finish_job(window)
    assert installs == ['audio', 'memory']
    assert panel.prepare.text() == 'Continue to the app'
    assert panel.key.text() == ''
    assert interpretation.local_openai_api_key() == 'fixture-not-a-real-key'
    assert not panel.key.isEnabled()
    panel.accept()
    window.open_model_setup()
    window.setup_dialog.start()
    finish_job(window)
    assert installs == ['audio', 'memory']
    window.setup_dialog.accept()
    contact = window.memory_store.create_contact('My own contact')
    memory_id = window.memory_store.create_memory(contact.id, 'My own saved information.')
    turn = ConversationTurn(speaker_name='My own contact', speaker_role='selected_contact',
        source='test', display_order=1, timestamp=datetime.now(timezone.utc), content='My own call.')
    record_id = window.memory_store.create_record(source_kind='call', source_label='My own call',
        timezone_name='UTC', contact_id=contact.id, turns=[turn], status='stopped')
    path = window.memory_store.path
    window.close()
    with memory.MemoryStore(path) as reopened:
        assert reopened.get_contact(contact.id).display_name == 'My own contact'
        assert reopened.current_revision(memory_id)['content'] == 'My own saved information.'
        assert reopened.summary_turns(record_id)[0].content == 'My own call.'
    assert not setup_dialog.needs_setup(path)
    assert installs == ['audio', 'memory']


def test_download_failure_can_retry_and_keeps_key(fresh_app, monkeypatch):
    window = fresh_app
    ready, installs = fake_models(monkeypatch, window, fail=True)
    window.open_model_setup()
    panel = window.setup_dialog
    panel.key.setText('fixture-not-a-real-key')
    panel.start()
    finish_job(window)
    assert 'Download interrupted' in panel.status.text()
    assert not panel.busy and panel.prepare.isEnabled()
    assert panel.prepare.text() == 'Retry setup'
    assert interpretation.local_openai_api_key() == 'fixture-not-a-real-key'
    monkeypatch.setattr(setup_dialog.audio, 'install_local_model', lambda: ready.update(audio=True))
    panel.start()
    finish_job(window)
    assert panel.prepare.text() == 'Continue to the app'


def test_new_windows_profile_has_no_contacts_or_credentials(monkeypatch, tmp_path):
    monkeypatch.setattr(interpretation.sys, 'frozen', True, raising=False)
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    monkeypatch.setenv('LOCALAPPDATA', str(tmp_path / 'first-user'))
    with memory.MemoryStore() as first:
        first.create_contact('Only belongs to first user')
    interpretation.save_local_openai_api_key('fixture-first-user-key')
    monkeypatch.setenv('LOCALAPPDATA', str(tmp_path / 'second-user'))
    with memory.MemoryStore() as second:
        assert second.list_contacts() == []
    assert interpretation.local_openai_api_key() is None


def test_setup_requires_key_and_keeps_dialog_alive_during_download(fresh_app, monkeypatch):
    window = fresh_app
    ready, installs = fake_models(monkeypatch, window)
    window.open_model_setup()
    panel = window.setup_dialog
    panel.start()
    assert not installs and 'Enter your OpenAI API key' in panel.status.text()
    released = threading.Event()
    monkeypatch.setattr(setup_dialog.audio, 'prepare_transcription_runtime', lambda: released.wait(2))
    panel.key.setText('fixture-not-a-real-key')
    panel.start()
    try:
        panel.close()
        assert panel.isVisible() and panel.busy
        panel.start()
        assert window.pending_jobs == 1
    finally:
        released.set()
    finish_job(window)
