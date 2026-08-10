import re
from datetime import datetime

from .models import ConversationTurn

# Adapted from Autistic Analyzer commit a1a9d1dd3d6e0c0b5a0dd89ef595b4e17f3b8f1c.
# ponytail: two proven US 24-hour formats; expand only for an accepted failing export.
DASH_EXPORT_RE = re.compile(
    r"^(?P<date>\d{1,2}/\d{1,2}/\d{2}), (?P<time>\d{1,2}:\d{2}) - (?P<sender>[^:]+): (?P<body>.*)$"
)
BRACKET_EXPORT_RE = re.compile(
    r"^\[(?P<time>\d{1,2}:\d{2}), (?P<date>\d{1,2}/\d{1,2}/\d{4})\] (?P<sender>[^:]+): (?P<body>.*)$"
)


def parse_whatsapp_transcript(text: str, source: str) -> list[ConversationTurn]:
    turns: list[ConversationTurn] = []

    for raw_line in text.splitlines():
        line = raw_line.rstrip().lstrip("\ufeff")
        match = DASH_EXPORT_RE.match(line) or BRACKET_EXPORT_RE.match(line)
        if match:
            turns.append(_message_from_match(match, len(turns) + 1, source))
        elif turns and line and not re.match(
            r"^(?:\d{1,2}/\d{1,2}/\d{2}, \d{1,2}:\d{2} - |"
            r"\[\d{1,2}:\d{2}, \d{1,2}/\d{1,2}/\d{4}\] )",
            line,
        ):
            turns[-1].content = f"{turns[-1].content}\n{line}"

    return turns


def _message_from_match(
    match: re.Match[str], display_order: int, source: str
) -> ConversationTurn:
    body = match.group("body")
    return ConversationTurn(
        speaker_name=match.group("sender"),
        source=source,
        content=body,
        timestamp=_parse_timestamp(match.group("date"), match.group("time")),
        display_order=display_order,
        is_media=_is_media_placeholder(body),
    )


def _parse_timestamp(date_text: str, time_text: str) -> datetime:
    date_format = "%m/%d/%y" if len(date_text.rsplit("/", 1)[-1]) == 2 else "%m/%d/%Y"
    return datetime.strptime(f"{date_text} {time_text}", f"{date_format} %H:%M")


def _is_media_placeholder(body: str) -> bool:
    normalized = body.strip().lower()
    return "media omitted" in normalized or (
        "omitted" in normalized and "image" in normalized
    )
