import argparse
import sys
from pathlib import Path

from pydantic import ValidationError

from .parser import parse_whatsapp_transcript

FIXTURE_PATH = Path(__file__).with_name("demo") / "lecturer_demo_chat.txt"


def foundation_summary(fixture_path: Path | None = None) -> str:
    text = (fixture_path or FIXTURE_PATH).read_text(encoding="utf-8-sig")
    turns = parse_whatsapp_transcript(text, source="demo")
    speaker_count = len({turn.speaker_name for turn in turns})
    if len(turns) != 500 or speaker_count != 2:
        raise ValueError(
            f"expected 500 Conversation Turns from 2 speakers, got {len(turns)} from {speaker_count}"
        )
    return "Foundation ready\n500 Conversation Turns\n2 speakers"


def show_window(summary: str) -> None:
    import tkinter as tk

    root = tk.Tk()
    root.title("Conversation Copilot")
    root.minsize(320, 140)
    tk.Label(root, text=summary, justify="center", padx=32, pady=24).pack()
    root.mainloop()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m conversation_copilot")
    parser.add_argument("--check", action="store_true", help="validate the bundled replay without opening a window")
    args = parser.parse_args(argv)

    try:
        summary = foundation_summary()
    except (OSError, ValidationError, ValueError) as exc:
        print(f"Foundation check failed: {exc}", file=sys.stderr)
        return 1

    if args.check:
        print(summary)
    else:
        show_window(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
