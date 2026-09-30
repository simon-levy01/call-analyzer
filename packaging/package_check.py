"""Offline packaged-runtime check, with synthetic data and no capture or inference API."""
def main():
    import json
    import os
    import socket
    import tempfile
    from pathlib import Path

    def deny(*args, **kwargs):
        raise RuntimeError('Network disabled during package check')
    socket.socket.connect = socket.socket.connect_ex = socket.create_connection = socket.getaddrinfo = deny
    os.environ['HF_HUB_OFFLINE'] = '1'
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    from conversation_copilot.__main__ import foundation_summary
    from conversation_copilot.memory import MemoryStore, default_database_path
    from conversation_copilot import audio, semantic
    # Exercise the same native-library import order as desktop readiness.
    audio.prepare_transcription_runtime()
    catalog = audio.AudioDeviceCatalog()
    try:
        device_count = len(catalog.microphones) + len(catalog.playbacks)
    finally:
        catalog.close()
    from conversation_copilot import desktop, video, capture
    from PySide6.QtCore import QSettings, QTimer
    from PySide6.QtWidgets import QApplication
    from unittest.mock import patch

    report = {'foundation': foundation_summary(), 'audio_devices': device_count, 'video': video.run_video_check()}
    vectors = semantic.embed_texts_if_ready(['Synthetic package check.'], semantic.default_cache_dir(default_database_path()))
    assert vectors is not None and vectors.shape == (1, 384), 'Local memory model unavailable'
    report['memory_model'] = 'ready'
    model = audio._load_local_model()
    assert model.model.device == 'cuda'
    report['transcription_model'] = 'loaded on ' + model.model.device
    del model
    app = QApplication([])
    with tempfile.TemporaryDirectory() as folder, MemoryStore(Path(folder) / 'check.sqlite3') as store:
        store.create_contact('Package check')
        with patch.object(desktop, 'QSettings', lambda *_: QSettings(str(Path(folder) / 'settings.ini'), QSettings.IniFormat)):
            window = desktop.Desktop(store, discover=False)
            for timer in window.findChildren(QTimer):
                timer.stop()
            window.show()
            app.processEvents()
            assert window.width() == 860 and window.height() == 721
            window.close()
    report['qt'] = 'Home rendered with isolated data'
    print(json.dumps(report, ensure_ascii=True))
    return 0


def profile_check():
    """Verify fresh-profile UI and persistence; model downloads are mocked here."""
    import json
    import os
    import socket
    import tempfile
    import time
    from pathlib import Path
    from unittest.mock import patch
    from contextlib import ExitStack
    from datetime import datetime, timezone
    def deny(*args, **kwargs):
        raise RuntimeError('Network disabled for fresh-profile check')
    socket.socket.connect = socket.socket.connect_ex = socket.create_connection = socket.getaddrinfo = deny
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QSettings
    from conversation_copilot import desktop, memory, setup_dialog, interpretation
    from conversation_copilot.models import ConversationTurn
    app = QApplication([])
    with tempfile.TemporaryDirectory() as folder, ExitStack() as patches:
        first, second = Path(folder) / 'first-user', Path(folder) / 'second-user'
        patches.enter_context(patch.dict(os.environ, {'LOCALAPPDATA': str(first)}))
        os.environ.pop('OPENAI_API_KEY', None)
        patches.enter_context(patch.object(desktop, 'QSettings', lambda *_: QSettings(str(first / 'settings.ini'), QSettings.IniFormat)))
        ready = {'audio': False, 'memory': False}
        patches.enter_context(patch.object(setup_dialog.audio, 'local_model_available', lambda: ready['audio']))
        patches.enter_context(patch.object(setup_dialog.audio, 'prepare_transcription_runtime', lambda: None))
        patches.enter_context(patch.object(setup_dialog.audio, '_load_local_model', lambda: object()))
        patches.enter_context(patch.object(setup_dialog.audio, 'install_local_model', lambda: ready.update(audio=True)))
        patches.enter_context(patch.object(setup_dialog.semantic, 'model_ready', lambda _: ready['memory']))
        def install(cache):
            cache.mkdir(parents=True, exist_ok=True)
            (cache / setup_dialog.semantic._MARKER).write_text('{}')
            ready['memory'] = True
        patches.enter_context(patch.object(setup_dialog.semantic, 'install_model', install))
        window = desktop.Desktop(discover=False)
        patches.enter_context(patch.object(window, 'refresh_devices', lambda: None))
        patches.enter_context(patch.object(window, 'schedule_semantic_backfill', lambda: None))
        assert not window.memory_store.list_contacts()
        assert interpretation.local_openai_api_key() is None
        window.show()
        window.check_initial_setup()
        deadline = time.monotonic() + 10
        while window.pending_jobs and time.monotonic() < deadline:
            app.processEvents()
            time.sleep(.01)
        assert window.pending_jobs == 0
        assert window.setup_dialog.isVisible()
        window.setup_dialog.key.setText('fixture-not-a-real-key')
        window.setup_dialog.start()
        deadline = time.monotonic() + 10
        while window.pending_jobs and time.monotonic() < deadline:
            app.processEvents()
            time.sleep(.01)
        assert window.pending_jobs == 0 and window.setup_dialog.prepare.text() == 'Continue to the app'
        contact = window.memory_store.create_contact('Synthetic user contact')
        mid = window.memory_store.create_memory(contact.id, 'Synthetic user information.')
        turn = ConversationTurn(speaker_name=contact.display_name, speaker_role='selected_contact', source='test',
            display_order=1, timestamp=datetime.now(timezone.utc), content='Synthetic saved call.')
        rid = window.memory_store.create_record(source_kind='call', source_label='Synthetic call', timezone_name='UTC',
            contact_id=contact.id, status='stopped', turns=[turn])
        window.setup_dialog.accept()
        window.close()
        window.memory_store.close()
        with memory.MemoryStore() as reopened:
            assert reopened.get_contact(contact.id).display_name == 'Synthetic user contact'
            assert reopened.current_revision(mid)['content'] == 'Synthetic user information.'
            assert reopened.summary_turns(rid)[0].content == 'Synthetic saved call.'
            assert not setup_dialog.needs_setup(reopened.path)
        assert interpretation.local_openai_api_key() == 'fixture-not-a-real-key'
        os.environ['LOCALAPPDATA'] = str(second)
        with memory.MemoryStore() as other:
            assert other.list_contacts() == []
        assert interpretation.local_openai_api_key() is None
    print(json.dumps({'fresh_profile': 'empty contacts and no API key', 'setup_ui': 'completed with mocked downloads',
        'persistence': 'contact, memory, call and key reopened', 'second_profile': 'separate empty store', 'network': 'blocked'}))
    return 0
