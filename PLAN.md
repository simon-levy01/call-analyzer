# Conversation Copilot Master Plan

September 21: reviewed current fixes/citation checkpoint published on main `addfe9b`, with local/origin/GitHub equality verified. Further semantic fixes isolated on `codex/call-semantic-fixes-20260921`, consuming the second/final calibration round; 336 offline tests pass. Full shortest-call Luna-low agent comparison completed: 64 fresh answers +2 exact reuses, 32/33 local passes per arm, both full post-call scratch checks pass. The candidate reduces some role/repetition errors but loses useful memories and adds unsupported summary details; do not merge the whole candidate. Verified tool-disabled Opus5 review/follow-up cleared the experimental checkpoint and docs-only main publication; the mistaken missing-schema-bound finding was retracted, citation pruning remains unvalidated, and remaining suggestions are untested hypotheses. No further calibration round remains. [Report](docs/CALL-SEMANTIC-AGENT-20260921.md). No F07 acceptance or candidate merge claimed.

September 21 publication request: user explicitly authorized current fixes plus the bounded citation correction on main, then further semantic work on a new branch. 335 offline tests pass; fresh verified tool-disabled Opus 5 review cleared checkpoint publication; baseline addfe9b was published with local/origin/GitHub equality verified. This is a checkpoint, not F07 acceptance. [Scope and evidence](docs/CITATION-MAIN-20260921.md).

September 21 [source-limit experiment](docs/CALL-SOURCE-CAP-20260921.md): first two-thirds of shortest call, three Luna-low agent arms, all prefix post-call pipelines pass locally. Citation mismatch confirmed; no broad semantic win from removing caps. Seven agent save failures remain in results. Production unchanged; proposed bounded correction needs implementation/review and API acceptance. Original F07 gates and tuning limits remain; other calls deferred.

Supplementary delivery follow-up: seven separately logged fresh Luna-low attempts fill the save gaps; all raw JSON is preserved. Total 55 fresh dispatches plus 21 exact reuses. With supplements, 67/69 requested outputs pass locally; two schema failures remain. First-pass failures and denominators are unchanged; no repairs or third attempts.

September 21 shortest-call comparison complete: 99 fresh isolated Luna/Terra/Sol low answers, 97 local output passes, 3 full scratch post-call passes. [Findings](docs/CALL-FULL-AGENT-REPLAY-20260921.md). The user deferred the other two calls before any fresh requests; 234 requests remain queued, 12 earlier saved reuses preserved. No production changes, API spend or F07 gate completion.

September 21 diagnostic:36 fresh isolated Luna/Terra/Sol low agent responses completed across six selected cases,two repeats. Local validation/replay passes; mixed quality findings recorded in [comparison](docs/CALL-AGENT-COMPARISON-20260921.md). No production changes, API spending, new tuning or F07 gates passed. Paid Luna/Terra comparison remains blocked by account credits; preserve its original caps and all evidence.

September 19 diagnostic: requested identical-input Luna-low/Terra-low API comparison is prepared but blocked by exhausted API account credits.23 cases/92 planned responses, zero model answers;35 offline tests pass. Caps $0.30 Luna/$0.50 Terra; preserved failures and append-only unbilled reconciliation. [Details](docs/CALL-MODEL-API-20260919.md). No production change, new tuning round, agent inference or F07 gate completion.

September 17 API checkpoint: 90 independent Luna-low responses compare frozen old/revised production requests with two repeats; $0.09749827/$0.30 committed. Specific attribution/summary improvements coexist with garbled-speech, category and repetition failures. A post-API empty-cue validation correction passes 334 tests and changes only one of 32 saved revised guidance results. See [comparison](docs/CALL-PROMPT-API-20260917.md). Verified tool-disabled Opus 5 review/follow-up cleared the diagnostic checkpoint; live rechecks/final release review still pending. No F07 gate or main-branch publication claimed.

**September 16 call corrections:** User requested prior-log analysis and isolated fixes, excluding echo. Baseline branch `codex/pre-call-fixes-20260916` (`75d5b27`), correction branch `codex/call-analysis-fixes-20260916`. [Implementation, offline comparisons and remaining gates](docs/CALL-FIXES-20260916.md). No main merge, new paid evaluation or F07 completion is claimed. User permits a needed +200 per individual token cap; original dollar/cost gates remain.

**September 14 visual-model screening:** User authorized local downloads/comparisons of MediaPipe/F07, LibreFace, OpenFace2, Py-Feat XGBoost, OpenGraphAU and OpenFace3 with RAM prioritized. [Evidence and external dataset access](docs/F07-VISION-SCREENING.md). This is diagnostic research alongside F07, not a production replacement or a new tuning round. All original release gates and deadlines remain.
Completed CPU screening: all six pipelines tested on DISFA development data and two new conversation clips; portrait peak resident memory ranged from 258 to 1,326 MiB. Current pipeline retained; independent annotated validation and full F07 gates remain pending.

**Approved:** 2026-08-10  
**Windows MVP delivery deadline:** 2026-10-01

**Status:** Active

**Latest F07 checkpoint — 2026-09-14:** User-requested before-live comparison completed: 144 independent Luna-low responses, 143 validated; 279 offline tests pass. Aggregate committed API cost $0.07768505/$0.30; cap did not stop tests. Tool-disabled Opus-5-only harness review cleared after corrections. Boundary/ownership failures and visual-only cost excess remain; no release pass. P1/P2/P3, permitted corrections, after-human comparison, final review and reviewed publication remain pending. [Results](docs/F07-VALIDATION.md). F01–F06 stay complete; September 23/27 and F08 October 1 deadlines unchanged.

**F07 execution update — 2026-09-14:** S0 preflight is active under the user's implementation request. Source baseline and reusable media clocks/hashes are preserved. The user subsequently authorized provisional assistant screenshot annotations or a suitable dataset, with live checks later; independent annotations no longer block implementation. Remaining scenario/input/protocol freezes still apply. See [F07 validation](docs/F07-VALIDATION.md) and [dataset findings](docs/F07-DATASETS.md). F01–F06 remain complete; F07 is not complete and no release is claimed.

**Roadmap update approved:** 2026-09-15 — F08 is narrowed to easy Windows installation and Claude review, including necessary installation checks and review corrections. Final presentation/demo preparation and a recorded fallback are deferred, not F08 completion gates. F09 macOS implementation/testing follows immediately after the smaller F08 is complete; it need not wait until October 1. F07 remains active with unchanged gates. October 1 remains the Windows installation delivery target, not a required presentation date; no Mac completion date is committed.

## F06 closure — user accepted 14 September 2026

F06 is **complete for now by explicit user acceptance**. After reviewing the remaining Luna-quality limitations, the user instructed: “consider everything done for now”, commit/push, and update the plan. This supersedes pending closure requirements for another final Luna live call and another final Opus review; neither is reported as passed. Earlier manual calls and preliminary Opus reviews remain historical evidence. The latest independent review was Claude Sonnet 5, with two confirmed code findings fixed and covered by tests.

Current configuration: Luna low for live guidance, manual interpretation, Ask Memory and post-call review. 270 automated tests pass. Completed comparison: 258 historical agent answers (226 distinct requests plus32 exact reuses),12 new agent answers,6 changed-prompt agent checks, and24 new Luna API calls costing an estimated $0.02118703. Existing API results were reused. Local-model experiments are set aside, with results preserved.

Known accepted limitations: occasional ambiguous job reminders, overreading a verbal boundary as discomfort, and uncertain attribution/meaning from garbled speech. These remain evaluation/calibration work for F07; no claim of perfect memory recall or agent/API equivalence. F07, including planned facial-expression improvements, is next but has not started. No F07 implementation is authorized by this closure.

Evidence: [completed checks and review dispositions](docs/F06-AGENT-API-EXPANDED.md), [test index](docs/TESTING.md). Private raw logs, databases and archives remain Git-ignored; future devices need a private archive transfer. Exact publication SHA and verified main pointers are recorded on the existing Trello release/roadmap cards to avoid a self-referential commit hash.

## Purpose

Build a Windows-first assistant for autistic users that runs beside a one-to-one WhatsApp, Zoom, or Google Meet video call. Google Meet is supported only in a dedicated Google Chrome window. The assistant combines visible facial signals, both sides of the conversation, and contact-specific memory to offer cautious possible tones, social cues, useful reminders, follow-up questions, and reply suggestions.

This is the grand plan. It defines direction, sequence, and gates. Each feature receives its own smaller plan immediately before implementation; this file must not prematurely specify every screen, algorithm, or schema.

## Definition of Finished

By October 1, the application must support a complete one-to-one call loop on the development Windows computer with easy installation. Formal presentation/demo preparation is deferred by the September 15 roadmap update:

1. The user starts the assistant, selects a visible WhatsApp, Zoom, or dedicated Chrome-hosted Google Meet call window, and confirms or corrects the suggested contact.
2. The app follows the largest remote face and processes visual signals without recording video. A brief miss may reacquire automatically; after six seconds without the selected face it pauses without silently choosing another face, and the user explicitly resumes with **Continue tracking**.
3. It captures the user's microphone and one explicitly selected Windows playback endpoint, producing attributed conversation turns while clearly warning that every sound routed to that endpoint is in scope. Chrome and other non-call audio must be closed or kept silent during WhatsApp/Zoom capture. Once that audio session is healthy, visual capture loss pauses only facial signals: the empty face area collapses, the existing transcript and audio state remain visible, transcription continues until explicit Stop/close, and no replacement video or audio source is selected silently. A clean Stop may retain the two selections only inside the same live enumeration context; Refresh, fault, or in-process rebuild clears them. App restart never restores prior choices, though its fresh initial enumeration may suggest current defaults.
4. F04 first combines bounded recent turns with compact local visual/vocal observations into structured, evidence-backed tone hypotheses and social cues. After F05, bounded approved contact memories may enrich the same interpretation.
5. It can offer up to three items in each guidance category: possible tones, important cues, replies, remembered details to mention, and follow-up questions. The interface may show fewer.
6. Each interpretation item uses `low`, `medium`, or `high` confidence. The complete update may instead report insufficient or conflicting evidence, and it never presents emotion or intent as certain.
7. It creates post-call summaries and memory proposals. Approved memories remain available across future text and voice/video interactions.
8. Repeatable evaluation shows that the system is useful, responsive, contact-specific, and willing to abstain when evidence is weak.
9. Easy Windows installation and startup are verified, with Claude review and required corrections complete. A polished live presentation and recorded fallback are deferred; neither blocks F08 completion or F09.

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
- Evaluation, Claude review gates, and easy Windows installation. Final demo preparation and a recorded fallback remain deferred work.

### Supporting, Not Headline Scope

- Reuse useful parts of the Autistic Analyzer POC: WhatsApp transcript parsing/import, contact history, recent analysis windows, review concepts, demo fixtures, and tests.
- Text import seeds contact history and provides a cheap, repeatable analysis path. A polished text-chat product and WhatsApp Web integration are optional.

### Explicitly Deferred

- Group calls and group chats.
- Facial recognition or biometric identity during F01-F08. After the October 1 MVP, revisit opt-in contact face enrollment as a separate feature only with explicit consent, user-controlled deletion, multiple reference samples, measured false-match/false-reject behavior, and confirmation before a suggested match becomes the Selected Contact. F05 uses aliases and explicit contact selection; one saved screenshot is not treated as reliable identity evidence.
- Hidden capture, employee/student scoring, or definitive emotion detection.
- Native/private Zoom, WhatsApp, or Google Meet integrations when selected-window capture is sufficient.
- macOS operation and packaging during F01-F08; F09 follows the reduced installation/review F08 immediately when complete, without waiting for a final demonstration or October 1.
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

GPU acceleration is allowed when useful, but the basic MediaPipe path should remain CPU-capable. The F01-F08 release target is Windows; a MacBook is not required for the October 1 installation delivery target. F09 follows F08 completion and adds macOS as a supported platform only after implementation and validation on a real Mac.

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
| [F06 — Live guidance, Ask Memory, and post-call review](plans/F06-live-guidance-ask-memory-post-call-review.md) | Complete for now — Sep 14 | Replies, reminders, follow-ups, manually approved summaries, existing memory-proposal review, and natural-language questions over approved local evidence |
| [F07 — Evaluation and calibration](plans/F07-evaluation-calibration.md) | Sep 27 | First candidate under evaluation; review corrections and measured failures recorded. Human/held-out/release gates pending |
| F08 — Easy Windows installation and Claude review | After F07; by Oct 1, sooner if ready | Simple install/startup, required setup checks, Claude review/corrections and reviewed publication; no final demo or recorded fallback gate |
| F09 — macOS support | Immediately after F08 completion; no committed finish date | Enable testing on the user's Mac: selected-window capture, two-sided audio, local transcription, existing guidance/memory, and Mac setup/packaging while preserving Windows operation |

### F07 — Evaluation and calibration (first candidate under evaluation)

September 14: implemented first persistent-expression/shared-calibration candidate and ran 24 Luna-low API tuning responses ($0.010754 of the newly authorized $0.30 total). Dataset replay and API outputs expose inadequate mouth-corner recall and an attribution regression; no release pass is claimed. One tuning round used. Automated cleanup investigation and preliminary Opus review are in progress. See [F07 validation](docs/F07-VALIDATION.md); final 144 comparisons, participant checks, freeze/final review and reviewed publication remain outstanding.

Latest correction checkpoint: **278 tests passed; verified tool-disabled Opus 5 preliminary correction review cleared P1 development**. Failed extraction wording reverted; first candidate/source/results preserved. P1 consent/setup/results and second-round/freeze decisions are next. Final release gates remain pending; no commit/push yet.

The [feature plan](plans/F07-evaluation-calibration.md) was approved on 2026-09-14, including self-review revisions. It owns expression levels/duration/timing, targeted reminder/boundary/garbled-attribution calibration, matched visual and unchanged-production comparisons, numerical gates and three consenting participant checks. Local observations update continuously; automatic cloud guidance remains speech-triggered. Luna low and the existing privacy/selected-face boundaries remain unchanged.

Stop tuning September 23 and finish by September 27, using the approved fallback if improvements fail their gates. Both verified Claude Opus 5 review gates, actual user testing, corrections and commit/push verification remain required. F01–F06 stay complete; F08 retains the October 1 Windows installation target and may finish earlier, allowing F09 to start immediately. Execution status: [F07 roadmap card](https://trello.com/c/68EGr9Sh) and its permanent feature column. No implementation or inference ran during planning.

### F08 — Easy Windows installation and Claude review (planned; not started)

Scope reduced by the user on September 15 to enable earlier Mac development/testing. After F07 closes, create the focused F08 plan and permanent feature column. Choose the simplest reliable installation/startup path, including required dependencies/models, user-supplied API-key setup and short setup/troubleshooting instructions; do not choose an installer technology prematurely.

Verify installation in a clean supported Windows environment and startup outside the development checkout. Preserve existing local data and keep credentials/private logs out of distributable files. Retain the normal preliminary/final Claude review, focused installation/user checks, necessary corrections and reviewed commit/push verification. Do not reopen unrelated accepted feature gates or turn this into new functionality or an open-ended whole-program rewrite.

Final demo rehearsal, presentation materials, recorded fallback and demo-only polish are explicitly excluded. Track them as deferred presentation work with a date to be chosen later; do not make them a hidden dependency of F09. October 1 remains the installation delivery target, not a wait-until date. F09 starts as soon as F08 is accepted and published.

### F09 — macOS support (planned; not started)

Trello: [F09 roadmap card](https://trello.com/c/fCrlrZ8P/91-f09-macos-support-after-f08).

Start immediately after F08's easy Windows installation and Claude review are complete; do not wait for October 1 or final demo preparation. The user will run this feature on a Mac so they can test the application there as well as on Windows. At that point, record its chip, memory, and macOS version and choose the supported hardware/OS baseline from measured results. Create `plans/F09-macos-support.md` and the permanent F09 Trello column immediately before implementation, following the existing per-feature workflow. Until then, keep F09 as a Feature Backlog roadmap card; do not start a second active feature or prebuild portability abstractions. Prioritize an early working Mac call path for user testing; full Mac acceptance still requires the checks below, not a polished presentation.

Reuse the existing Python UI, interpretation, contact memory, and local face-processing logic wherever compatible. F09 owns Mac window discovery/capture, microphone and call-audio capture with explicit selection and permissions, a local transcription runtime that does not require NVIDIA CUDA, conditional platform dependencies/imports, native storage paths, and Mac setup/packaging. Choose capture and transcription implementations in the F09 plan after an early on-Mac capture/accuracy/latency check; do not assume the current Windows dependencies or GPU path work on Mac.

Completion requires a clean Mac install and a complete call-to-guidance-to-post-call-memory demonstration, measured transcription accuracy/latency alongside video processing, permission-denial/recovery and audio-device/lifecycle checks, and real WhatsApp, Zoom, and dedicated Chrome/Meet validation for each claimed Mac integration. Preserve existing privacy, contact confirmation, bounded cloud requests, local audio processing, no raw media retention, and audio continuity after visual loss. Windows validation waivers do not count as Mac evidence. Rerun affected Windows regression checks, document the supported Mac configuration and limitations, and complete the existing Claude review, corrections, commit/push, and Trello completion gates.

### Post-MVP Candidate

| Candidate | Timing | Outcome |
|---|---:|---|
| Opt-in contact face recognition | After F08; no current deadline | Suggest a contact from explicitly enrolled local reference images while still requiring user confirmation. This requires its own feature plan, privacy/biometric ADR, deletion controls, and false-match/false-reject evaluation before implementation. |

F02 completed on 2026-08-19 under the explicit validation exception below: real WhatsApp passed, real Zoom/Meet were user-waived and remain documented risks, and the final tool-disabled Claude Opus 5 review passed after correcting two-face **Continue tracking** recovery.

F02's completed standalone contract still stops its visual-only session when the selected window closes or becomes ineligible. Beginning with F03, the combined Assisted Call follows the audio-led rule above: a healthy explicit microphone/playback-endpoint session survives visual-target loss, while F02 signals stop, its empty thumbnail area collapses so the live transcript/audio state stays visible, and no replacement window is captured. Future feature plans must preserve this distinction. F03 also owns cross-source priority: while an eligible WhatsApp call exists, Chrome/Meet is not offered as a source; an already-running Meet session fails closed if a WhatsApp call appears.

F04 is approved as a memory-free interpretation feature. It analyzes the remote participant's possible social cues and may describe the recent conversation atmosphere; the user's finalized words provide context only, and the user's face/prosody are not analyzed. Automatic live analysis uses the cheapest passing Luna `none`/`low` profile with at least 12 seconds between request starts. Terra `none`/`low` is available only through an explicit one-request user action, with visible estimated cost and the same hard session budget. Detailed cadence, schema, evaluation, and privacy gates live in `plans/F04-multimodal-tone-cues.md`.

F05 planning was approved on 2026-08-27 and completed on 2026-09-01 after the consenting call, measured retrieval/performance/safety gates, full suite, and clean Opus 5 correction review passed. It uses explicit contact selection, aliases/disambiguation, local attributed-text Conversation Records, review-only AI proposals (including visibly grouped `likely_generic` concrete routine facts), immutable approved revisions, exact-contact lifecycle filtering, SQLite/FTS5 retrieval plus bounded local BGE-small similarity, and bounded memory enrichment of F04. The semantic dependency was selected only after the live indirect-employment case scored 0/3 with lexical retrieval and 3/3 locally at ranks 1, 2, and 2. September 3 follow-ups keep locally matched remembered context visible for 24 seconds after its last matching snapshot, use the latest eight complete turns within a 500-character semantic window, and pause semantic matching across explicit topic transitions while preserving lexical retrieval and immediate lifecycle/contact invalidation. Face recognition remains a separate post-MVP candidate. Detailed scope, storage, lifecycle, evaluation, and implementation evidence live in `plans/F05-contact-memory-personalization.md` and `docs/F05-VALIDATION.md`.

F06 must include an **Ask Memory** experience for natural-language questions over
the selected contact's Approved Memories and manually Approved Summaries, such as
`What time did Yaheli say his appointment was?`. It must reuse F05's exact-contact,
lifecycle-safe bounded retrieval rather than sending complete history to a model.
Answers show supporting contact/date/source context and must say that nothing was
found, present low-confidence alternatives, ask for clarification, or abstain when
the stored evidence is missing or ambiguous. Deleted, unassigned, wrong-contact,
and unreviewed content cannot become answer evidence. Rejected proposals and linked
summary statements remain excluded unless the user explicitly restores a summary
statement through review; this does not approve the proposal. Superseded memory
revisions are not current evidence. A summary statement explicitly kept after a
correction may remain dated history with a linked correction, never silently current
truth. Sensitive content without cloud permission remains eligible only for local use.

The [F06 feature plan](plans/F06-live-guidance-ask-memory-post-call-review.md)
records the September 7 interview: two visible candidates per new guidance category
(three supported), short temporary Ask follow-ups, separate in-call Ask contact scope,
manual summary/memory approval, source links, correction Keep/Remove choices, rejection
and deletion controls, and bounded shared costs. Existing FTS5/structured/source-based
answers and BGE retrieval remain the default. Explicit cloud help is the preferred
enhancement so an additional local LLM is not required on less capable PCs. Any local
LLM experiment needs measured usefulness, complete package/RAM/latency and concurrent-call
evidence; it remains optional and outside the normal install. No model replaces
contact/lifecycle filtering or invents an answer when retrieval found no evidence.

## Per-Feature Workflow

Before implementation of feature `FNN`:

1. Read `PLAN.md`, `CONTEXT.md`, the current Trello board, relevant code/tests, and prior feature outcomes.
2. Create `plans/FNN-short-name.md` containing the feature goal, user-visible result, dependencies, technology decision or spike, acceptance checks, demo, risks, and explicit non-goals.
3. Create a permanent Trello column named `FNN — Feature Name`. Add cards for planning, implementation slices, validation, Claude review, and corrections.
4. Confirm the feature is the only active implementation feature.

During and after implementation:

1. Build the smallest complete vertical slice and leave one runnable check for non-trivial logic.
2. Test with saved inputs before spending API budget on live calls.
3. Before asking the user to test, complete agent-run feature/affected-integration checks and obtain a preliminary tool-disabled, read-only **Claude Opus 5** (`claude-opus-5`) QA/code review of the plan, complete diff, test evidence and known limitations. Verify and record the actual reviewer model; do not silently substitute an older Opus or Sonnet. Correct accepted findings, rerun affected checks and obtain a clean follow-up first.
4. Give the user a concrete manual-test script, demonstrate the feature against its acceptance checks and record the user's actual results. Fix reported defects and rerun affected checks. Silence is not a pass.
5. After user testing, obtain a fresh tool-disabled, read-only **Claude Opus 5** review of the final complete diff, automated evidence, manual outcomes and corrections. Both reviews cover only the feature and its direct integration surfaces, not unrelated unchanged code. Reserve whole-program review for the dedicated final gate. Use Opus 5 unless the user explicitly approves another model. The pre-test pass does not replace the post-test gate.
6. Fix accepted findings or record evidence for rejection; rerun affected checks and obtain correction review until no material findings remain. Obtain targeted user rechecks if fixes change manually tested behavior. Audit the final diff, commit the reviewed result and push it; verify local main, origin/main and GitHub main match.
7. Mark the feature complete in its plan and permanent Trello column only after both review gates, user testing, corrections and release verification. This general workflow was reaffirmed on 2026-09-08 for F06 and future work; it does not reopen accepted F01–F05 gates.

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
- live retrieval produces a bounded candidate set. For explicitly requested F06 cloud Ask (user revision 2026-09-13), Luna low may consider all eligible approved, cloud-permitted memories and summaries for one selected contact if they fit a bounded request; otherwise use a ranked shortlist. Never send the entire multi-contact store. Preserve contact/lifecycle/privacy checks and cited evidence;
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

**Google Meet follow-up — passed 2026-09-07:** a consenting live call in dedicated Chrome admitted the current code-shaped Meet title, captured three visible participants, detected faces in the normal layout and after the small-tile screen-share fallback, and produced attributed transcript plus live interpretation. The user accepted the run as passed. The historical F02/F03 waivers remain an accurate record of the earlier release gates; this later evidence closes the observed title, small-gallery, and tested-call routing risks for this Chrome/Meet configuration without expanding the product beyond explicit selected-window capture or one analyzed face.

## Cost Control

**F06 planning decision — approved 2026-09-07:** F06 will raise the Assisted Call hard limit to **$0.35**, with **$0.08 reserved for post-call summary/extraction** and at most **$0.27 for paid live work**. Retain the $0.15 warning. All call-funded work shares the same ledger and accounts for in-flight reservations. If longer post-call work cannot fit, keep it pending and offer an explicit continuation button with its cost estimate and a bounded run limit. The $0.25 amounts below describe the accepted F04/F05 baseline until F06 implements this change; this decision does not reopen those completed gates.

**F06 approval decision — approved 2026-09-07:** Summary drafts require explicit manual review/approval before search can use them. Ask Memory searches current eligible Approved Summaries and Approved Memories only. Summary approval and Memory Proposal approval remain separate actions; automatic approval is deferred.

**F06 Ask Memory decision — approved 2026-09-07:** Begin with existing local structured/FTS5/source-based answers and BGE-small retrieval. An optional small local LLM requires measured F06 usefulness and complete-footprint/concurrent-call evidence before adoption. An OpenAI fallback requires an explicit action and visible estimate for each request, capped at **$0.04 per answer** and **$0.13 per outside-call Ask session**. During calls it shares the live budget and cannot consume the post-call reserve. Sensitive-memory permissions remain enforced. These are upper limits; testing records actual cost rather than aiming to consume them.

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
5. Broad hardware optimization. macOS support remains F09 immediately after the reduced F08; it has no October 1 completion commitment and is not blocked by deferred demo preparation.

Do not trim the working video capture path, evidence-backed multimodal interpretation, contact-aware guidance, uncertainty, repeatable evaluation, or working Windows operation. Formal demo preparation and a recorded fallback are deferred by the September 15 decision.

**F06 post-call tuning — 2026-09-13:** User-authorized 1.5x extraction reservation (6,000→9,000), whole-transcript summary input up to 9,000, and Ask input/evidence +300 tokens (6,300/4,700). Post-call Luna low; live settings unchanged. Saved 88-turn call replay used only extraction and summary, two final requests costing $0.00265096; four variants total $0.02796231. See `docs/F06-POST-CALL-CONTEXT-TEST.md` for actual output and remaining generic-memory limitations. Automated checks: 268 passed; user retest and final review/release remain pending.

Final F06 tuning replay after raising proposal ceiling8→12 used2 requests ($0.00245255); total current tuning $0.03041486, aggregate evaluation $3.45659864. Six pending proposals cover the desired fact groups, with remaining interpretation/summary-resolution mistakes documented in the report. This is not a clean model-quality acceptance claim.
