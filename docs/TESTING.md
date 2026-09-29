# Testing

## Offline suite

From the repository root, after installing `.[test]`:

```powershell
$env:QT_QPA_PLATFORM = "offscreen"
.\.venv\Scripts\python -m pytest
.\.venv\Scripts\python -m pip check
.\.venv\Scripts\python -m conversation_copilot --check
```

The ordinary suite uses fictional fixtures, temporary databases, and fake providers.
It covers transcript parsing, call-window selection, audio/video processing,
guidance timing and retention, contact isolation, source citations, budgets,
imports, summaries, approval/rejection, deletion, and Qt controls/recovery.
Offscreen Qt tests exercise widgets without opening a desktop window.

For focused UI and approval-boundary checks:

```powershell
.\.venv\Scripts\python -m pytest tests/test_f06_ui.py tests/test_f06_ask.py
```

## Model and device checks

Real microphone/playback capture, call-window modes, model quality, and installation
on a clean Windows machine require separate validation. Unit tests do not establish
those results. See [current validation status](F08-VALIDATION.md).

`tools/evaluation/` retains reusable research runners and code imported by tests.
Some runners call paid providers or download models. They are not setup checks.
Use a fresh isolated run directory, an explicitly selected method, and an applicable
budget before new paid inference. Preserve previous ledgers, timeout reservations,
raw answers, and baselines. Never run evaluations against the user's live database.
Historical reports and private evidence stay local; earlier public versions remain
in Git history. No credentials or real call logs belong in a commit or source ZIP.

## Illustrative cost estimate

The Home estimate uses historical workload measurements, not a billing guarantee:
3,371.15 live input tokens, 1,722 cached input tokens and 1,646.15 cache-write tokens
per update; measured output profiles are 351.05 Luna and 263.25 Sol tokens.
Post-call input/output is scaled from a 341.461483-second recording (9,276 input,
9,270 cache writes, 762 output). Current model prices and update cadence come from
`conversation_copilot/interpretation.py`. Ask, manual refresh, retries, and edited
summary regeneration are excluded. Speech density, caching, and output vary.
