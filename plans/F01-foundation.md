# F01 — Foundation and selective POC reuse

**Target:** 2026-08-14  
**Status:** Implementation validated — Claude Review Gate pending  
**Implementation gate:** Approved by the user on 2026-08-10.

## Goal

Create the smallest runnable Windows foundation for Conversation Copilot and carry forward only proven, relevant behavior from the Autistic Analyzer POC. F01 establishes the project baseline, one native Windows shell, one headless check, the shared contact/conversation vocabulary, and one deterministic replay path.

## User-visible result

Running one documented command opens a native Windows window titled **Conversation Copilot**. The window reports **Foundation ready** and shows only the bundled replay summary: **500 Conversation Turns** and **2 speakers**. It does not display message contents.

A second documented command performs the same foundation check without opening a window, prints the result, and exits successfully or returns a non-zero exit code on failure.

## Dependencies and starting facts

- Windows development computer with Python 3.12.10 and Tk 8.6, both already verified.
- Approved `PLAN.md`, `CONTEXT.md`, and ADRs 0001–0002.
- Autistic Analyzer POC at `C:\Users\Banan\Desktop\Reichmann Uni\Year 2\Semester 2\From Idea to Reality with AI\HW\HW4\Autistic Analyzer`.
- POC source commit `a1a9d1dd3d6e0c0b5a0dd89ef595b4e17f3b8f1c` from `https://github.com/simon-levy01/Final-Project-v1.git`.
- POC baseline verified before planning: `40 passed` with Python 3.12.10.
- No existing Git repository or application code in the new project directory.

## Decisions

### Minimum implementation rule

F01 must stop as soon as its acceptance checks pass. Implement the smallest clear solution and do not add architecture for hypothetical later needs.

- Reuse verified project code first, then Python/Tkinter standard-library features, then already-approved dependencies.
- Add no dependency except Pydantic, pytest, and the parser candidate only while its pass/fail spike is active. Remove the candidate if it loses.
- Add no factory, repository layer, service container, event bus, plugin system, generic base class, extension registry, premature async framework, or configuration for values that do not vary in F01.
- Prefer one direct function or module over an abstraction with one implementation. Split code only when an F01 boundary or test requires it.
- Do not create scaffolding, schemas, interfaces, flags, or TODO-driven hooks for later features.
- Keep the parser adapter thin. If adapting the external candidate becomes more complex than the proven fallback, fail the spike and use the fallback.
- Leave one runnable check for each non-trivial F01 behavior; do not create broad test infrastructure beyond the acceptance checks.
- Do not refactor unrelated documents or build any capability listed under Explicit non-goals.

### Project baseline

- Initialize this project directory as a Git repository during implementation.
- Use a minimal Python package with `pyproject.toml`, `.gitignore`, tests, and short setup/run/check instructions.
- Use standard `venv` and `pip`; add no dependency-management wrapper.
- Use Pydantic 2 for validation at imported-data and shared-model boundaries and pytest for runnable checks.

### Windows shell

- Use Python's stdlib Tkinter for the F01 window.
- Start it with `python -m conversation_copilot`.
- Provide `python -m conversation_copilot --check`; this path must not create a Tk window.
- Do not add FastAPI, Uvicorn, a browser shell, or another desktop framework in F01.
- This is a reversible foundation choice, so it does not require an ADR.

### Shared vocabulary

F01 introduces only these validated names:

- `ContactSuggestion`: an unconfirmed possible contact derived from an explicit source.
- `SelectedContact`: the contact confirmed by the user; F01 does not persist it.
- `ConversationTurn`: one ordered contribution with speaker attribution, source, content, and available timestamp.
- `Observation`: a time-bounded visible, vocal, or linguistic input before interpretation; F01 defines the boundary but does not capture observations.
- `SpeakerRole`: `user`, `selected_contact`, or `unclear`.
- `ConfidenceLevel`: `low`, `medium`, `high`, or `unclear`.

There will be no generic event base class, event bus, persistence schema, identifier framework, or speculative hierarchy. System/export notices are not Conversation Turns. Imported speaker names remain unconfirmed until mapped to a Selected Contact or the user.

## Parser technology spike

F01 will test one external parser before reusing POC implementation code:

- Candidate: [`whatsapp-chat-to-pdf==0.1.0`](https://pypi.org/project/whatsapp-chat-to-pdf/), MIT licensed, Python 3.9+, structured `Chat`/`Message` output.
- Reason to test: it claims fourteen timestamp formats, multiline reconstruction, and media/system-message classification.
- Risks: one young release, one maintainer, PDF-focused dependency/code, and no published support for the POC's time-first bracket format `[14:03, 6/20/2026]`.

The spike is pass/fail and time-bounded to one implementation slice. Adopt the candidate only if a thin adapter:

1. passes all five POC parser regressions listed below;
2. parses `lecturer_demo_chat.txt` into exactly 500 ordered Conversation Turns from exactly two speakers;
3. preserves bodies, multiline continuations, timestamps, source, display order, and media-placeholder behavior needed by those checks;
4. performs no network call, persistent write, PDF rendering, or other parsing side effect; and
5. produces the validated F01 Conversation Turn representation without keeping a second parser.

If any gate fails, remove the candidate and its transitive dependency, then use the exact POC fallback below. The finished application must contain one parser path, never both.

Rejected for F01:

- [`whatstk`](https://pypi.org/project/whatstk/): broader format support, but GPL-3.0-only and brings analytics/visualization dependencies.
- [`chat-miner`](https://pypi.org/project/chat-miner/): MIT, but brings dataframe, plotting, and word-cloud dependencies unrelated to F01.
- [`chat-export`](https://pypi.org/project/chat-export/): maintained and lightweight, but its product boundary is archive/HTML output rather than validated Conversation Turns.
- `chatpack`: its published Python artifact does not provide a Windows/Python 3.12 wheel.

## Exact Autistic Analyzer reuse

### Always reuse as behavioral checks/assets

| POC artifact | F01 use |
|---|---|
| `tests/test_parser.py::test_parses_dash_export_format` | Compatibility check for dashed exports. |
| `tests/test_parser.py::test_parses_bracket_export_format` | Compatibility check for the time-first bracket export. |
| `tests/test_parser.py::test_preserves_multiline_message_continuations` | Regression for continuation lines. |
| `tests/test_parser.py::test_detects_media_placeholder_messages` | Regression for non-retained media placeholders. |
| `tests/test_parser.py::test_keeps_display_order` | Regression for stable ordering. |
| `demo/lecturer_demo_chat.txt` | The single bundled F01 replay fixture. |
| Behavior from `tests/test_demo_mode.py::test_demo_transcript_has_500_messages_from_two_people` | Adapted fixture check for exactly 500 turns and two speakers; omit its POC UI/API assertions. |

The tests will be adapted only for the new module/model names. Their behavioral assertions remain the parser selection gate.

### Reuse only if the external candidate fails

Extract these symbols from POC `app.py`; do not copy the surrounding monolith:

- `DASH_EXPORT_RE` (`app.py:442`)
- `BRACKET_EXPORT_RE` (`app.py:445`)
- `parse_whatsapp_transcript` (`app.py:466`)
- `_message_from_match` (`app.py:481`)
- `_parse_timestamp` (`app.py:494`)
- `_is_media_placeholder` (`app.py:499`)

Adapt their dictionary output to the validated F01 Conversation Turn representation. Record the POC commit above in a source comment or attribution file. The fallback's known ceiling is the two proven 24-hour, numeric month/day formats; expand it only when a real failing export becomes an accepted requirement.

### Explicitly do not reuse in F01

- The complete `app.py`, `INDEX_HTML`, FastAPI endpoints, or CSS/HTML-coupled tests.
- `preview_import`, import-confirm APIs, exact-name contact selection, or the default self-name `Simon`.
- SQLite schema, storage helpers, databases, logs, or `get_recent_messages`; the recent-window behavior remains a later storage/analysis concern.
- Analysis, OpenAI configuration, free-text JSON parsing, review APIs, or memory functions/tests.
- `save_approved_memory` and the current assessment flow, which approve generated memory before review and conflict with the master plan.
- `fake_transcript_noam_1000.txt` and `fake_transcript_lior_1000.txt`; F01 needs only one replay fixture.
- `.env` files, API keys, videos, share artifacts, or generated outputs.

## Implementation slices

1. **Repository baseline:** initialize Git; add the minimal package, `pyproject.toml`, `.gitignore`, README commands, and test layout.
2. **Runnable Windows shell:** add the Tkinter entry point and side-effect-free headless check using one shared foundation-summary function.
3. **Shared vocabulary:** add only the approved Pydantic models/enums and focused boundary checks.
4. **Selective parser reuse:** run the external-parser gate, keep exactly one parser, adapt the five POC regressions, and add the single replay fixture/check.
5. **Validation:** run clean-environment tests and the manual Windows demo.
6. **Claude Review Gate:** provide this plan, complete diff, test output, demo evidence, parser-spike result, and known limitations.
7. **Corrections:** resolve accepted findings, record rejected findings with reasons, rerun checks, and close F01.

Only F01 implementation slices may be active while this Feature Column is open.

## Acceptance checks

- [x] From a clean virtual environment, documented setup succeeds on the development Windows computer.
- [x] `python -m conversation_copilot` opens one Tkinter window titled `Conversation Copilot`.
- [x] The window shows `Foundation ready`, `500 Conversation Turns`, and `2 speakers`, but no transcript body.
- [x] Closing the window exits cleanly without leaving a server or background process.
- [x] `python -m conversation_copilot --check` opens no window, prints the same summary, and exits `0`.
- [x] The check returns non-zero when its fixture/model validation fails.
- [x] All five adapted POC parser regressions pass.
- [x] The bundled fixture produces exactly 500 ordered Conversation Turns from two speakers.
- [x] The parser spike records which single implementation won and why; a rejected dependency is removed.
- [x] Shared models accept only the approved Speaker Roles and Confidence Levels and do not silently confirm a Contact Suggestion.
- [x] Startup/check requires no API key, network call, media permission, database, or persistent conversation data.
- [x] Tests pass with one documented command and do not spend API budget.
- [x] The implementation contains no unused dependency, abstraction, configuration, or later-feature scaffolding.
- [ ] Claude Review Gate is completed and accepted corrections are resolved before F01 is marked complete.

## Demo

1. Create and activate a clean virtual environment using the README commands.
2. Run the automated test command and show the passing parser, model, fixture, and headless checks.
3. Run `python -m conversation_copilot --check` and show the successful 500-turn/two-speaker summary.
4. Run `python -m conversation_copilot`, show the same summary in the Windows window, then close it cleanly.
5. Show the recorded parser-spike decision and confirm only one parser dependency/path remains.

## Risks and controls

- **Young external candidate:** require the existing regression suite and fixture gate; fall back to the proven small parser on any failure.
- **Ambiguous numeric dates:** retain the proven month/day behavior for F01 and document the ceiling instead of guessing locales.
- **POC has no license file:** reuse only internal project-owner behavior/code from the recorded commit; do not imply third-party provenance.
- **Tkinter may not satisfy a later native integration:** keep the shell thin and reversible; F01 proves the runnable foundation only.
- **Fixture privacy/display risk:** bundle only the existing synthetic lecturer fixture and show counts, never message bodies, in the F01 shell.

## Explicit non-goals

- A polished interface, transcript browser, file picker, editable contact flow, or production installer.
- Selected-window or screen capture, facial processing, audio capture, or transcription.
- Tone/Social Cue interpretation, OpenAI calls, live guidance, or post-call output.
- Durable storage, contact aliases, Conversation Memory, retrieval, correction, or supersession.
- Performance evaluation, model calibration, or final Windows packaging.
- Planning or implementing any feature after F01.

## Approval and completion record

- [x] **Feature plan approved by user** — approved explicitly on 2026-08-10.
- [ ] **F01 acceptance checks passed.**
- [ ] **Claude Review Gate passed and corrections resolved.**
- [ ] **F01 marked complete in this file and its permanent Trello Feature Column.**

## Implementation evidence

- **Parser spike:** `whatsapp-chat-to-pdf==0.1.0` passed the dash, multiline, media, order, and 500-turn checks but returned zero turns for `[14:03, 6/20/2026]`. It was removed with its isolated transitive dependencies.
- **Selected parser:** the six named parser symbols adapted from Autistic Analyzer commit `a1a9d1dd3d6e0c0b5a0dd89ef595b4e17f3b8f1c`; this is the only parser and adds no parser dependency.
- **Automated validation:** clean Python 3.12.10 environment, `python -m pytest` → `13 passed`; `python -m conversation_copilot --check` → exit `0` with the three required summary lines.
- **Fixture provenance:** bundled fixture Git blob `d76e92a18a017515f6733616067e9e19fab2e854` exactly matches the pinned POC commit and parses to 500 ordered turns from Maya Cohen and Simon.
- **Windows validation:** the Tkinter window visibly showed the exact title and summary; closing it left zero Conversation Copilot windows and zero matching Python background commands.
- **Known limitation:** the fallback intentionally supports only the two proven US numeric, 24-hour export formats; expand it only for an accepted failing export.
- **Claude Review Gate:** pending.
