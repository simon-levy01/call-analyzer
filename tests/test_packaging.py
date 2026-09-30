import sys

from conversation_copilot import interpretation


def test_frozen_key_is_saved_outside_bundle(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, 'frozen', True, raising=False)
    monkeypatch.setenv('LOCALAPPDATA', str(tmp_path))
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    interpretation.save_local_openai_api_key('fixture-not-a-real-key')
    assert interpretation.local_openai_api_key() == 'fixture-not-a-real-key'
    assert (tmp_path / 'ConversationCopilot' / '.env.local').is_file()
