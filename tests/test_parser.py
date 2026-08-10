from datetime import datetime

from conversation_copilot.__main__ import FIXTURE_PATH
from conversation_copilot.models import SpeakerRole
from conversation_copilot.parser import parse_whatsapp_transcript


def test_parses_dash_export_format():
    turns = parse_whatsapp_transcript("6/20/26, 14:03 - Alex: Hey, are you coming today?")

    turn = turns[0]
    assert turn.speaker_name == "Alex"
    assert turn.content == "Hey, are you coming today?"
    assert turn.timestamp == datetime(2026, 6, 20, 14, 3)
    assert turn.source == "paste"
    assert turn.speaker_role is SpeakerRole.UNCLEAR


def test_parses_bracket_export_format():
    turns = parse_whatsapp_transcript("[14:03, 6/20/2026] Alex: On my way")

    assert turns[0].speaker_name == "Alex"
    assert turns[0].content == "On my way"
    assert turns[0].timestamp == datetime(2026, 6, 20, 14, 3)


def test_preserves_multiline_message_continuations():
    turns = parse_whatsapp_transcript(
        "6/20/26, 14:03 - Alex: First line\n"
        "second line\n"
        "6/20/26, 14:05 - Simon: Reply"
    )

    assert turns[0].content == "First line\nsecond line"
    assert turns[1].content == "Reply"


def test_detects_media_placeholder_messages():
    turns = parse_whatsapp_transcript("6/20/26, 14:03 - Alex: <Media omitted>")

    assert turns[0].is_media is True


def test_keeps_display_order():
    turns = parse_whatsapp_transcript(
        "6/20/26, 14:03 - Alex: One\n6/20/26, 14:04 - Simon: Two"
    )

    assert [turn.display_order for turn in turns] == [1, 2]


def test_demo_transcript_has_500_turns_from_two_people():
    text = FIXTURE_PATH.read_text(encoding="utf-8")
    turns = parse_whatsapp_transcript(text, source="demo")

    assert len(turns) == 500
    assert {turn.speaker_name for turn in turns} == {"Maya Cohen", "Simon"}
    assert [turn.display_order for turn in turns] == list(range(1, 501))
    assert all(turn.source == "demo" for turn in turns)
    assert "sprinting with hot coffee" in text
    assert "short answers from me today are not anger" in text
    assert "Fine, examples first" in text
    assert "proof of concept" not in text.lower()
    assert "demo button" not in text.lower()
