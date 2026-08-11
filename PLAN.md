# Conversation Copilot Master Plan

**Approved:** 2026-08-10  
**Delivery deadline:** 2026-10-01  
**Status:** Active

## Purpose

Build a Windows-first assistant for autistic users that runs beside a one-to-one WhatsApp or Zoom video call. It combines visible facial signals, both sides of the conversation, and contact-specific memory to offer cautious possible tones, social cues, useful reminders, follow-up questions, and reply suggestions.

This is the grand plan. It defines direction, sequence, and gates. Each feature receives its own smaller plan immediately before implementation; this file must not prematurely specify every screen, algorithm, or schema.

## Definition of Finished

By October 1, the application must demonstrate a complete one-to-one call loop on the development Windows computer:

1. The user starts the assistant, selects a visible WhatsApp or Zoom call window, and confirms or corrects the suggested contact.
2. The app follows the largest remote face and processes visual signals without recording video.
3. It captures the user's microphone and the other person's system audio, producing attributed conversation turns.
4. It combines visual observations, conversation context, and approved contact memory into structured, evidence-backed tone hypotheses and social cues.
5. It can offer up to three items in each guidance category: possible tones, important cues, replies, remembered details to mention, and follow-up questions. The interface may show fewer.
6. It uses `low`, `medium`, `high`, or `unclear` confidence and never presents emotion or intent as certain.
7. It creates post-call summaries and memory proposals. Approved memories remain available across future text and voice/video interactions.
8. Repeatable evaluation shows that the system is useful, responsive, contact-specific, and willing to abstain when evidence is weak.
9. The Windows demo works live, with a recorded fallback available.

## Product Principles

- **Hypotheses, not mind reading:** report possible affective tone and social meaning, never inner truth.
- **Evidence first:** each output identifies the words, vocal behavior, visible movement, or remembered context that influenced it.
- **Contact-aware, user-controlled:** the app may suggest a contact, but the user confirms the identity before memory is used or updated.
- **Long-lived memory:** approved memories do not expire automatically. Corrections supersede old memories while preserving history; the user can still delete them.
- **Local ownership:** memories, transcripts, and settings live on the user's computer. Relevant audio, transcript excerpts, derived visual signals, and selected memories may be sent to OpenAI when required for transcription or analysis.
- **No video retention:** captured frames are processed in memory and are not written to disk or sent to an external vision service in the planned MVP.
- **Low cognitive load:** guidance changes only after meaningful new evidence, not on every frame or token.
- **One feature at a time:** finish, test, and review the active feature before beginning another.

## Scope

### Required

- Windows desktop operation beside WhatsApp Desktop and Zoom.
- User-selected application-window capture.
- One-to-one calls and one selected contact.
- Local facial landmarks/blendshapes and remote-face tracking.
- Microphone and Windows system-audio capture.
- Transcription and separation of the user's speech from the contact's speech.
- Multimodal tone hypotheses such as possibly happy, sad, angry/tense, emotionally intense, neutral, or unclear.
- Contact-specific memories, relationship-specific interaction style, and shared context across imported text and calls.
- Live replies, reminders, and follow-up suggestions.
- Post-call summary and reviewed memory proposals.
- Evaluation, Claude review gates, Windows packaging, and demo fallback.

### Supporting, Not Headline Scope

- Reuse useful parts of the Autistic Analyzer POC: WhatsApp transcript parsing/import, contact history, recent analysis windows, review concepts, demo fixtures, and tests.
- Text import seeds contact history and provides a cheap, repeatable analysis path. A polished text-chat product and WhatsApp Web integration are optional.

### Explicitly Deferred

- Group calls and group chats.
- Facial recognition or biometric identity.
- Hidden capture, employee/student scoring, or definitive emotion detection.
- Native Zoom or WhatsApp private integrations when selected-window capture is sufficient.
- macOS packaging.
- Hardware wearables.
- Cloud accounts or server-hosted memory.

## Technical Direction

These are preferred starting points, not permanent choices. Each feature plan must verify that its technology still fits before adopting it.

| Need | Preferred starting point | Fallback or later experiment |
|---|---|---|
| Windows window capture | `Windows.Graphics.Capture` secure picker | Narrow screen-region capture only if an app cannot be captured reliably |
| Facial observations | MediaPipe Face Landmarker in live-stream mode | ONNX Runtime/DirectML model after evaluation proves landmarks are insufficient |
| Remote face selection | Largest detected face plus user correction | Saved per-app crop/layout |
| Audio capture | Microphone plus Windows WASAPI loopback | Selected application audio if reliable isolation is available |
| Speech transcription | Local `faster-whisper` first | Current low-cost OpenAI transcription/realtime model |
| Structured interpretation | Current low-cost OpenAI model with enforced structured output | Stronger OpenAI model for post-call analysis only when quality requires it |
| Local application core | Reuse the POC's Python/FastAPI/Pydantic path where useful | Select the smallest Windows shell during the foundation feature |
| Durable storage and search | SQLite plus FTS5 baseline | Compare Mem0 and Graphiti during the memory feature; adopt only if they win against the acceptance criteria |
| Optional voice emotion signal | Simple local prosody features | Hume only if the paid experiment materially improves measured results |

GPU acceleration is allowed and should be used when it improves the demo, but the basic MediaPipe path should remain CPU-capable. The supported release target is Windows; the lecturer's MacBook is not a packaging target.

## Reuse and Lessons from the Autistic Analyzer POC

The old application proved that an AI model can analyze a bounded conversation and propose useful contact memory. It is a reference implementation, not the final architecture.

Preserve:

- separate conversation history, regenerable analysis, reviewed contact assessment, and approved memories;
- deterministic parsing for known transcript formats and AI only where ambiguity requires it;
- recent analysis windows for latency and cost;
- timestamps, source, display order, and contact attribution;
- evidence-backed social cues, clarification suggestions, and an explicit `unclear` outcome;
- import previews, demo transcripts, and useful parser/storage/API tests.

Correct or redesign:

- never save an AI-generated assessment as approved before review;
- record provenance, evidence, dates, corrections, contradictions, and supersession for memory;
- use contact aliases instead of exact-name identity;
- use API-enforced structured output instead of parsing requested JSON from free text;
- learn relationship-specific reply style from both speakers without turning unrelated user behavior into contact memory;
- split the single-file POC only when feature boundaries require it.

## Feature Roadmap

Target dates are completion targets. If one slips, apply the trimming order instead of starting several unfinished features.

| Feature | Target | Outcome |
|---|---:|---|
| F01 — Foundation and selective POC reuse | Aug 14 | Runnable project, chosen desktop approach, imported tests/fixtures, shared event/contact vocabulary |
| F02 — WhatsApp/Zoom window capture and facial signals | Aug 23 | Stable selected-window frames, largest-face tracking, local observations, no frame retention |
| F03 — Two-sided audio and transcription | Aug 31 | Microphone and system audio become attributed transcript turns with acceptable latency |
| F04 — Multimodal tone and cue interpretation | Sep 9 | Structured, uncertainty-aware tones/cues combine visual, vocal, and language evidence |
| F05 — Contact memory and personalization | Sep 16 | Approved long-term memory, aliases, provenance, retrieval, supersession, and relationship-specific style |
| F06 — Live guidance and post-call review | Sep 22 | Replies, reminders, follow-ups, summaries, and memory proposals work in the call loop |
| F07 — Evaluation and calibration | Sep 27 | Repeatable scenarios, measured errors/latency/abstention, and tuned update behavior |
| F08 — Windows packaging and final demonstration | Oct 1 | Reliable live Windows demo, clean setup, limitations, and recorded fallback |

## Per-Feature Workflow

Before implementation of feature `FNN`:

1. Read `PLAN.md`, `CONTEXT.md`, the current Trello board, relevant code/tests, and prior feature outcomes.
2. Create `plans/FNN-short-name.md` containing the feature goal, user-visible result, dependencies, technology decision or spike, acceptance checks, demo, risks, and explicit non-goals.
3. Create a permanent Trello column named `FNN — Feature Name`. Add cards for planning, implementation slices, validation, Claude review, and corrections.
4. Confirm the feature is the only active implementation feature.

During and after implementation:

1. Build the smallest complete vertical slice and leave one runnable check for non-trivial logic.
2. Test with saved inputs before spending API budget on live calls.
3. Demonstrate the feature against its acceptance checks.
4. Hand Claude the feature plan, changed files/diff, test results, and known limitations for QA/code review.
5. Fix accepted findings or record why a finding was rejected.
6. Rerun the feature checks, commit the reviewed result, and push it to the project's GitHub repository so the accepted history is preserved remotely.
7. Mark the feature complete in its plan and permanent Trello column before planning the next feature.

## Agent and Source-of-Truth Rules

- The head agent maintains this master plan, the glossary, and cross-feature consistency.
- New feature sessions must read the master plan, glossary, current feature plan, Trello column, and relevant code before editing.
- `PLAN.md` controls project direction; the current feature plan controls implementation scope; Trello records execution status.
- GitHub records accepted implementation history. A code feature is not complete until its post-Claude-review result is committed and pushed.
- A feature session may clarify or reduce its feature but must not silently expand the master scope.
- Architectural changes that affect later features must update this plan and the board.

## Memory Requirements

The memory feature plan must compare SQLite/FTS5, Mem0, and Graphiti using a small project-specific retrieval test. Choose the smallest system that satisfies all of these:

- data remains stored locally and separated by confirmed contact;
- aliases can suggest a contact without silently selecting one;
- memories distinguish facts, preferences, dates/plans, cue patterns, and relationship-specific interaction style;
- every memory carries provenance and relevant dates;
- proposed, approved, rejected, corrected, superseded, and deleted states are representable;
- approved memories persist indefinitely unless the user changes or deletes them;
- current retrieval excludes superseded facts but preserves their history;
- retrieval is fast enough for live guidance and does not flood the model with irrelevant history;
- export and deletion are testable.

No memory framework is adopted merely because it is popular. If SQLite/FTS5 passes the test, use it.

## Evaluation and Quality Gates

The project is not finished because a demo looks plausible. Evaluation must include:

- controlled one-to-one scenarios covering happiness, sadness, tension/anger, emotional intensity, neutrality, sarcasm, uncertainty, and changing engagement;
- comparisons of transcript-only, current multimodal context, and multimodal context plus contact memory;
- useful cue rate, incorrect cue rate, `unclear`/abstention behavior, latency, stability, and API cost;
- wrong-contact, stale-memory, contradicted-memory, and no-face/no-audio cases;
- checks that raw frames are not retained and local conversations/memories can be deleted;
- user correction of tone, contact selection, and memory proposals;
- Claude review before every code feature is marked complete.

## Cost Control

- Set a development budget alert at **$30** through October 1.
- Prefer replayable transcripts, audio samples, and derived visual fixtures during development.
- Use local MediaPipe and local transcription when reliable enough.
- Use a low-cost OpenAI model for repeated structured analysis and a stronger model only for targeted evaluation or post-call quality.
- Do not add a second paid provider without evidence that the current stack blocks an acceptance criterion.

## Trimming Order

If the schedule slips, remove work in this order:

1. Group conversations and group calls.
2. Deep/private Zoom or WhatsApp integrations beyond selected-window capture.
3. Polished text UI and WhatsApp Web convenience features.
4. Paid Hume/prosody experiments and extra emotion models.
5. Broad hardware optimization and macOS support.

Do not trim the working video capture path, evidence-backed multimodal interpretation, contact-aware guidance, uncertainty, repeatable evaluation, or the live Windows demo.
