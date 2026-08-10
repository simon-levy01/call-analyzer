import subprocess
import sys

import pytest

import conversation_copilot.__main__ as application

EXPECTED_SUMMARY = "Foundation ready\n500 Conversation Turns\n2 speakers"


def test_foundation_summary_contains_counts_and_no_message_body():
    summary = application.foundation_summary()

    assert summary == EXPECTED_SUMMARY
    assert "sprinting with hot coffee" not in summary


def test_check_does_not_open_window(monkeypatch, capsys):
    monkeypatch.setattr(
        application,
        "show_window",
        lambda _summary: pytest.fail("--check opened a window"),
    )

    assert application.main(["--check"]) == 0
    assert capsys.readouterr().out.strip() == EXPECTED_SUMMARY


def test_check_returns_nonzero_when_fixture_validation_fails(tmp_path, monkeypatch, capsys):
    invalid_fixture = tmp_path / "invalid.txt"
    invalid_fixture.write_text("6/20/26, 14:03 - Alex: One", encoding="utf-8")
    monkeypatch.setattr(application, "FIXTURE_PATH", invalid_fixture)

    assert application.main(["--check"]) == 1
    assert "expected 500 Conversation Turns" in capsys.readouterr().err


def test_module_check_command():
    result = subprocess.run(
        [sys.executable, "-m", "conversation_copilot", "--check"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == EXPECTED_SUMMARY
