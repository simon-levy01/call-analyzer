# Conversation Copilot Master Plan

**Approved:** 2026-08-10  
**Delivery deadline:** 2026-10-01  
**Status:** Active

## Purpose

Build a Windows-first assistant for autistic users that runs beside a one-to-one WhatsApp, Zoom, or Google Meet video call. Google Meet is supported only in a dedicated Google Chrome window. The assistant combines visible facial signals, both sides of the conversation, and contact-specific memory to offer cautious possible tones, social cues, useful reminders, follow-up questions, and reply suggestions.

This is the grand plan. It defines direction, sequence, and gates. Each feature receives its own smaller plan immediately before implementation; this file must not prematurely specify every screen, algorithm, or schema.

## Definition of Finished

By October 1, the application must demonstrate a complete one-to-one call loop on the development Windows computer:

1. The user starts the assistant, selects a visible WhatsApp, Zoom, or dedicated Chrome-hosted Google Meet call window, and confirms or corrects the suggested contact.
2. The app follows the largest remote face and processes visual signals without recording video. A brief miss may reacquire automatically; after six seconds without the selected face it pauses without silently choosing another face, and the user explicitly resumes with **Continue tracking**.
3. It captures the user's microphone and one explicitly selected Windows playback endpoint, producing attributed conversation turns while clearly warning that every sound routed to that endpoint is in scope. Chrome and other non-call audio must be closed or kept silent during WhatsApp/Zoom capture. Once that audio session is healthy, visual capture loss pauses only facial signals: the empty face area collapses, the existing transcript and audio state remain visible, transcription continues until explicit Stop/close, and no replacement video or audio source is selected silently. A clean Stop may retain the two selections only inside the same live enumeration context; Refresh, fault, or in-process rebuild clears them. App restart never restores prior choices, though its fresh initial enumeration may suggest current defaults.
4. F04 first combines bounded recent turns with compact local visual/vocal observations into structured, evidence-backed tone hypotheses and social cues. After F05, bounded approved contact memories may enrich the same interpretation.
5. It can offer up to three items in each guidance category: possible tones, important cues, replies, remembered details to mention, and follow-up questions. The interface may show fewer.
6. Each interpretation item uses `low`, `medium`, or `high` confidence. The complete update may instead report insufficient or conflicting evidence, and it never presents emotion or intent as certain.
7. It creates post-call summaries and memory proposals. Approved memories remain available across future text and voice/video interactions.
8. Repeatable evaluation shows that the system is useful, responsive, contact-specific, and willing to abstain when evidence is weak.
9. The Windows demo works live, with a recorded fallback available.

## Product Principles

- **Hypotheses, not mind reading:** report possible affective tone and social meaning, never inner truth.
- **Evidence first:** each output identifies the words, vocal behavior, visible movement, or remembered context that influenced it.
- **Contact-aware, user-controlled:** the app may suggest a contact, but the user confirms the identity before memory is used or updated.
- **Long-lived memory:** approved memories do not expire automatically. Corrections supersede old memories while preserving history; the user can still delete them.
- **Local ownership:** memories, transcripts, and settings live on the user's computer. F04 sends only bounded transcript excerpts and compact derived vocal/visual observations to OpenAI. Sending raw audio later requires a separate explicit privacy and cost decision.
- **No video retention:** captured frames are processed in memory and are not written to disk or sent to an external vision service in the planned MVP.
- **Low cognitive load:** guidance changes only after meaningful new evidence, not on every frame or token.
- **One feature at a time:** finish, test, and review the active feature before beginning another.

## Scope

### Required

- Windows desktop operation beside WhatsApp Desktop, Zoom, and Google Meet in a dedicated Google Chrome window.
- User-selected application-window capture.
- One-to-one calls and one selected contact.
- Local facial landmarks/blendshapes, remote-face tracking, six-second loss protection, and explicit **Continue tracking** recovery.
- Explicit PyAudioWPatch microphone plus explicit WASAPI playback-endpoint loopback capture.
- Call-source priority: an eligible WhatsApp call suppresses Chrome/Meet selection; if one appears during active Meet capture, F03 stops both audio sides and requires explicit reselection. An idle WhatsApp main window does not block Meet.
- Audio-led combined-session lifecycle: once both explicit audio sides are healthy, loss of the selected visual target releases only F02 resources and transcription continues visibly until explicit Stop/close; no video target is selected automatically.
- Session-scoped audio selection convenience: a clean Stop/Start retains the exact microphone/playback records in the still-live enumeration context, while Refresh, fault, rebuild, and shutdown failure clear both and require explicit reselection. App restart restores no prior record/index; the fresh context may suggest its current Windows defaults.
- Transcription and separation of the user's speech from the contact's speech.
- English-only transcription. Hebrew and Auto are excluded until a future free local model passes a representative real-speech accuracy comparison.
- Multimodal conversation-atmosphere hypotheses limited initially to positive/warm, neutral/calm, sad/low-energy, tense/negative, energetic/high-energy, and emotionally intense; insufficient or conflicting evidence is an explicit abstention rather than a tone label.
- Contact-specific memories, relationship-specific interaction style, and shared context across imported text and calls.
- Live replies, reminders, and follow-up suggestions.
- Post-call summary and reviewed memory proposals.
- Evaluation, Claude review gates, Windows packaging, and demo fallback.

### Supporting, Not Headline Scope

- Reuse useful parts of the Autistic Analyzer POC: WhatsApp transcript parsing/import, contact history, recent analysis windows, review concepts, demo fixtures, and tests.
- Text import seeds contact history and provides a cheap, repeatable analysis path. A polished text-chat product and WhatsApp Web integration are optional.

### Explicitly Deferred

- Group calls and group chats.
- Facial recognition or biometric identity during F01-F08. After the October 1 MVP, revisit opt-in contact face enrollment as a separate feature only with explicit consent, user-controlled deletion, multiple reference samples, measured false-match/false-reject behavior, and confirmation before a suggested match becomes the Selected Contact. F05 uses aliases and explicit contact selection; one saved screenshot is not treated as reliable identity evidence.
- Hidden capture, employee/student scoring, or definitive emotion detection.
- Native/private Zoom, WhatsApp, or Google Meet integrations when selected-window capture is sufficient.
- macOS packaging.
- Hardware wearables.
- Cloud accounts or server-hosted memory.

## Technical Direction

These are preferred starting points, not permanent choices. Each feature plan must verify that its technology still fits before adopting it.

| Need | Preferred starting point | Fallback or later experiment |
|---|---|---|
| Windows window capture | `Windows.Graphics.Capture` secure picker | Narrow screen-region capture only if an app cannot be captured reliably |
| Facial observations | MediaPipe Face Landmarker in live-stream mode | ONNX Runtime/DirectML model after evaluation proves landmarks are insufficient |
| Remote face selection | Largest detected face plus **Switch face** correction; six-second loss lock plus **Continue tracking** | Saved per-app crop/layout |
| Audio capture | Explicit PyAudioWPatch microphone plus explicit WASAPI playback-endpoint loopback | Warn that endpoint scope includes every routed sound; close/quiet Chrome and other non-call audio during WhatsApp/Zoom |
| Speech transcription | Local `faster-whisper`; English only | Re-evaluate free local Hebrew models later; any cloud audio path needs explicit approval |
| Structured interpretation | Evaluated `gpt-5.6-luna` profile with enforced structured output, bounded stateless requests, and spend limits | One user-triggered `gpt-5.6-terra` check at an evaluated reasoning level; never automatic |
| Local application core | Reuse the POC's Python/FastAPI/Pydantic path where useful | Select the smallest Windows shell during the foundation feature |
| Durable storage and search | SQLite/FTS5 plus bounded local BGE-small similarity | Exact lifecycle/contact filtering remains SQL-first; vectors stay in the same database and are scored locally |
| Vocal observations | Simple local remote-speaker energy/rate/pause/overlap features from existing samples/timing | Add a vocal-analysis dependency only after measured uplift failure and an approved plan revision |

GPU acceleration is allowed and should be used when it improves the demo, but the basic MediaPipe path should remain CPU-capable. The supported release target is Windows; the lecturer's MacBook is not a packaging target.

## Reuse and Lessons from the Autistic Analyzer POC

The old application proved that an AI model can analyze a bounded conversation and propose useful contact memory. It is a reference implementation, not the final architecture.

Preserve:

- separate conversation history, regenerable analysis, reviewed contact assessment, and approved memories;
- deterministic parsing for known transcript formats and AI only where ambiguity requires it;
- recent analysis windows for latency and cost;
- timestamps, source, display order, and contact attribution;
- evidence-backed social cues, clarification suggestions, and an explicit abstention outcome;
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
| F02 — WhatsApp/Zoom/Chrome Meet window capture and facial signals | Aug 23 | Stable selected-window frames, largest-face tracking, explicit loss recovery, local observations, no frame retention |
| F03 — Two-sided audio and transcription | Aug 31 | Microphone and system audio become attributed transcript turns with acceptable latency |
| F04 — Multimodal tone and cue interpretation | Sep 9 | Stable English-only conversation-atmosphere hypotheses and remote social cues combine bounded language, local vocal, and local visual evidence |
| [F05 — Contact memory and personalization](plans/F05-contact-memory-personalization.md) | Sep 16 | Approved long-term memory, aliases, provenance, retrieval, supersession, and relationship-specific style |
| F06 — Live guidance, Ask Memory, and post-call review | Sep 22 | Replies, reminders, follow-ups, summaries, memory proposals, and natural-language questions over contact history work through one bounded guidance experience |
| F07 — Evaluation and calibration | Sep 27 | Repeatable scenarios, measured errors/latency/abstention, and tuned update behavior |
| F08 — Windows packaging and final demonstration | Oct 1 | Reliable live Windows demo, clean setup, limitations, and recorded fallback |

### Post-MVP Candidate

| Candidate | Timing | Outcome |
|---|---:|---|
| Opt-in contact face recognition | After F08; no current deadline | Suggest a contact from explicitly enrolled local reference images while still requiring user confirmation. This requires its own feature plan, privacy/biometric ADR, deletion controls, and false-match/false-reject evaluation before implementation. |

F02 completed on 2026-08-19 under the explicit validation exception below: real WhatsApp passed, real Zoom/Meet were user-waived and remain documented risks, and the final tool-disabled Claude Opus 5 review passed after correcting two-face **Continue tracking** recovery.

F02's completed standalone contract still stops its visual-only session when the selected window closes or becomes ineligible. Beginning with F03, the combined Assisted Call follows the audio-led rule above: a healthy explicit microphone/playback-endpoint session survives visual-target loss, while F02 signals stop, its empty thumbnail area collapses so the live transcript/audio state stays visible, and no replacement window is captured. Future feature plans must preserve this distinction. F03 also owns cross-source priority: while an eligible WhatsApp call exists, Chrome/Meet is not offered as a source; an already-running Meet session fails closed if a WhatsApp call appears.

F04 is approved as a memory-free interpretation feature. It analyzes the remote participant's possible social cues and may describe the recent conversation atmosphere; the user's finalized words provide context only, and the user's face/prosody are not analyzed. Automatic live analysis uses the cheapest passing Luna `none`/`low` profile with at least 12 seconds between request starts. Terra `none`/`low` is available only through an explicit one-request user action, with visible estimated cost and the same hard session budget. Detailed cadence, schema, evaluation, and privacy gates live in `plans/F04-multimodal-tone-cues.md`.

F05 planning was approved on 2026-08-27 and completed on 2026-09-01 after the consenting call, measured retrieval/performance/safety gates, full suite, and clean Opus 5 correction review passed. It uses explicit contact selection, aliases/disambiguation, local attributed-text Conversation Records, review-only AI proposals (including visibly grouped `likely_generic` concrete routine facts), immutable approved revisions, exact-contact lifecycle filtering, SQLite/FTS5 retrieval plus bounded local BGE-small similarity, and bounded memory enrichment of F04. The semantic dependency was selected only after the live indirect-employment case scored 0/3 with lexical retrieval and 3/3 locally at ranks 1, 2, and 2. September 3 follow-ups keep locally matched remembered context visible for 24 seconds after its last matching snapshot, use the latest eight complete turns within a 500-character semantic window, and pause semantic matching across explicit topic transitions while preserving lexical retrieval and immediate lifecycle/contact invalidation. Face recognition remains a separate post-MVP candidate. Detailed scope, storage, lifecycle, evaluation, and implementation evidence live in `plans/F05-contact-memory-personalization.md` and `docs/F05-VALIDATION.md`.

F06 must include an **Ask Memory** experience for natural-language questions over
the selected contact's approved memories and F06 conversation summaries, such as
`What time did Yaheli say his appointment was?`. It must reuse F05's exact-contact,
lifecycle-safe bounded retrieval rather than sending complete history to a model.
Answers show supporting contact/date/source context and must say that nothing was
found, present low-confidence alternatives, ask for clarification, or abstain when
the stored evidence is missing or ambiguous. Rejected, superseded, deleted,
unassigned, wrong-contact, or cloud-ineligible sensitive content cannot become
answer evidence.

The F06 grilling and feature plan must explicitly decide the smallest useful
interaction model (one-shot search versus short conversational follow-ups), how
the user selects one-contact versus explicit all-contact scope, what summary
records are searchable, whether query history is retained, how citations open
their memory/summary provenance, the local-retrieval versus bounded-model split,
token/cost limits, sensitive-memory permission, stale-result invalidation, and
missing/ambiguous-answer behavior. The MVP starts from contact-scoped question and
answer with provenance; a general autonomous chatbot is not implied. Prefer the
lightest local design that passes the fixed Ask Memory evaluation: first F05
metadata/FTS5 plus a small semantic embedding model and deterministic answers,
then an on-demand quantized sub-1B or roughly 1B local model only if it materially
improves query rewriting or grounded answer phrasing. A model must never replace
contact/lifecycle filtering or invent an answer when retrieval found no evidence.

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
4. Hand Claude Opus 5 the feature plan, changed files/diff, test results, and known limitations for QA/code review in a tool-disabled, read-only session. Each feature gate reviews that feature and its direct integration surface only, including existing components, contracts, and regression checks that the new feature touches or can affect; it does not repeat a general review of unrelated unchanged program code. Reserve whole-program Claude review for the dedicated project-wide/final gate. Use Opus 5 for preliminary reviews and the final required gate unless the user explicitly approves another model.
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
- retrieval handles indirect or euphemistic references such as `the event last week` by combining the confirmed contact, recent conversation turns, temporal metadata, importance/sensitivity, lexical matching, and locally computed semantic similarity rather than relying on shared keywords alone;
- the F05 retrieval test includes a sensitive-event case in which a later conversation refers indirectly to an earlier tragedy, plus a competing-event case that must return low confidence or abstain instead of selecting an ambiguous memory;
- local retrieval produces a bounded candidate set. A low-cost model may disambiguate only those candidates when local evidence is insufficient; the complete contact history or memory store is never sent merely to find a match;
- export and deletion are testable.

No memory framework is adopted merely because it is popular. Keep SQLite/FTS5 unless the measured indirect-reference gate requires the plan's bounded local embedding candidates; do not add a vector database.

F05 must integrate memory only after F04 is complete. It may add a bounded set of locally retrieved, approved memories to interpretation so indirect references such as a later mention of `the event` can be understood. That change must preserve F04's abstention/privacy rules and rerun the interpretation and modality comparisons; F04 contains no placeholder memory hook.

Memory-free F04 requests retain their existing 1,500-token target and 1,650 estimated-input-token hard ceiling. An F05 memory-aware request may add up to 700 estimated tokens for at most four short Approved Memory excerpts, giving a 2,200-token hard ceiling. The higher ceiling is activated only when memory context survives trimming; it does not increase the 1,000-token transcript target or the 400-token output cap. User-visible remembered-detail suggestions remain limited to three.

## Evaluation and Quality Gates

The project is not finished because a demo looks plausible. Evaluation must include:

- controlled one-to-one scenarios covering positive/warm, sad/low-energy, tense/negative, energetic/high-energy, emotional intensity, neutrality, humor, sarcasm, uncertainty, discomfort, and changing engagement;
- F04 comparisons of transcript only, transcript plus vocal observations, transcript plus visual observations, and all available F04 modalities; contact memory is excluded until F05 and then evaluated separately;
- the user-approved basic fictional two-person fixture remains the exact, speaker-separated F02-F05 replay; the approved HeyGen render adds a realistic compressed-video, neural-lip-sync, face-motion, and semantic-audio stress fixture, but its single animated voice, static Alex tile, watermark, and omitted opening line prevent it from replacing the basic fixture or a consenting live call;
- Ask Memory tests covering a correctly answered dated appointment, a follow-up question, no matching memory, two plausible appointments, wrong-contact isolation, corrected/superseded information, deleted evidence, sensitive cloud exclusion, provenance display, and bounded token/cost behavior;
- useful cue rate, incorrect cue rate, insufficient/conflicting abstention behavior, calibration, latency, stability, and API cost;
- wrong-contact, stale-memory, contradicted-memory, and no-face/no-audio cases, including six-second face loss without silent reselection, explicit visual continuation, visible uninterrupted audio transcription when visual capture ends mid-call, clean-stop selection retention versus fault/rebuild clearing, truthful endpoint-wide audio warnings/operating rules, and WhatsApp-over-Chrome source priority;
- checks that raw frames are not retained and local conversations/memories can be deleted;
- user correction of tone, contact selection, and memory proposals;
- Claude review before every code feature is marked complete.

**F02 validation exception — approved by the user on 2026-08-19:** the real WhatsApp call gate remains required and passed. The user explicitly waived the real Zoom and Google Meet calls for F02 completion, accepting the residual application/layout and Meet-title risks. In their place, F02 retains deterministic WGC/title-invalidation coverage plus memory-only generic-Chrome YouTube smoke checks while generic Chrome remains excluded from production selection. One portrait produced full selected-face signals; a four-person grid exposed a detector-scale ceiling in which full-window detection found no faces although diagnostic quadrant crops found three. This waives QA evidence only, not Zoom or dedicated Chrome-hosted Google Meet product support, and the untested live cases and large-portrait requirement remain documented for later validation.

**F03 validation exception — approved by the user on 2026-08-25:** real WhatsApp two-sided transcription passed. The user waived the F03 Zoom and Google Meet live calls for now; both are recorded as `WAIVED — not passed`. This accepts residual application-specific window, routing, layout, title, and endpoint-scope risks and does not present either app as validated.

## Cost Control

- Set a development budget alert at **$30** through October 1.
- Prefer replayable transcripts, audio samples, and derived visual fixtures during development.
- Use local MediaPipe and local transcription when reliable enough.
- For F04, target about 1,000 transcript and 1,500 total input tokens, cap output at 400 tokens, warn at `$0.15`, and stop automatic/manual interpretation at a `$0.25` session hard limit while local F02/F03 continue.
- Use the cheapest Luna `none`/`low` profile that passes for repeated structured analysis. Terra is limited to evaluation and explicit one-request user checks; it never activates automatically.
- Keep F04 real-model comparison under `$1.50`; the approved staged set is about `$0.62` once or `$1.25` including one full rerun at the conservative input ceiling.
- F05 post-call extraction shares F04's `$0.25` Assisted Call hard limit; when insufficient budget remains, the retained Conversation Record waits for manual retry. A large text import shows its estimate before analysis and has a separate `$0.25` per-run hard limit. F05's controlled real-model extraction/retrieval evaluation stops at `$2.00`. These caps may be revised only from recorded quality, token, and cost evidence.
- Do not add a second paid provider without evidence that the current stack blocks an acceptance criterion.

## Trimming Order

If the schedule slips, remove work in this order:

1. Group conversations and group calls.
2. Deep/private Zoom, WhatsApp, or Google Meet integrations beyond selected-window capture.
3. Polished text UI and WhatsApp Web convenience features.
4. Paid Hume/prosody experiments and extra emotion models.
5. Broad hardware optimization and macOS support.

Do not trim the working video capture path, evidence-backed multimodal interpretation, contact-aware guidance, uncertainty, repeatable evaluation, or the live Windows demo.
