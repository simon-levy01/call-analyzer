# F08 — Polish, QA and reliable Windows setup

**Recorded:** 26 September 2026, at the user's request to make the plan.
**Status:** User-accepted limited polish checkpoint — September 28. Search approval check passed; final verification is recorded in [validation](../docs/F08-VALIDATION.md). Original unperformed targets remain deferred, not passed. F08.11 submission/handoff remains open.
**Sequence:** F10 accepted by user → F08 → F09. October 1 remains the usable Windows/submission target.
**Application:** Conversation Assistant project; current native window title is Conversation Copilot. No rename is implied.

## 1. Goal and boundaries

Find reproducible bugs and usability problems in the current Qt application, make bounded root-cause fixes, and establish dependable Windows operation with truthful setup instructions. Preserve the working capture, transcription, guidance and memory behavior.

Both Codex and **Claude Opus 5.5** must independently operate the native application. Claude also reviews coverage, code and fixes. A static review, browser session, simulated Qt click or Codex-operated click cannot satisfy Claude's hands-on requirement.

This planning session may write documentation/Trello and perform minimal safe native access checks. It does not authorize the full campaign, fixes, integration installation, product inference, commit or push. The subsequent implementation request starts execution within this plan's gates.

No prompt tournament, production prompt/model switch, new feature family, toolkit rewrite, ASR replacement, Mac implementation or required dedicated installer. F10 is finished from the user's perspective; earlier omitted tests remain omitted, rather than becoming retrospective passes.

## 2. Current baseline and evidence

Planning source baseline: `cec4a5b5969f2004ee244111f4cb2c5a1d325412`, plus pre-existing local changes to AGENTS.md, PLAN.md and CONTEXT.md. Capture a fresh complete source/configuration manifest before execution; do not discard those edits or touch unrelated PDFs.

Read before execution:

- AGENTS.md, CONTEXT.md, PLAN.md and docs/TESTING.md.
- plans/F10-ui-ux-accessibility.md and docs/F10-QT-MIGRATION.md.
- docs/UI-REFINEMENTS-20260924.md, docs/IMPORT-PARTICIPANTS-20260925.md, docs/LONG-IMPORT-REVIEW-20260925.md and docs/BULK-APPROVAL-FIX-20260925.md.
- docs/SUMMARY-SEARCH-20260926.md, docs/DEMO-RETENTION-20260926.md, docs/SECTIONS-REPLAY-20260926.md, docs/HUMOR-TONES-20260926.md and docs/TONE-PAIR70-20260926.md.
- Current source: conversation_copilot/desktop.py, desktop_data.py, __main__.py, memory.py, semantic.py, audio.py, video.py, interpretation.py, guidance.py, post_call.py and import_transcript.py.

Current contracts, superseding older inventories:

- Home and Live open **Contact information**, which contains Conversation history. Home Edit opens the same panel; it is not a separate contact-name editor.
- Live has **Possible tones**, **Cues & context**, **Possible responses**, and **Related memories**. Four slots per section; responses combine replies/follow-ups; guarded retention is 180 seconds. Preserve dismissals, source/topic invalidation, uncertainty and current prompts.
- Live/Ask select Luna low (`gpt-5.6-luna`) or Sol low (`gpt-6-sol`). Review generation uses the higher-end shared entry, currently Sol. Verify routing from the source manifest rather than copying obsolete model names from older plans.
- Home Refresh refreshes call windows only. It preserves audio/contact choices and an unchanged preview. Face-loss tolerance is 18 seconds; healthy audio survives video loss.
- Import selector identifies the **contact**; the other speaker is the user. Exact unique contact aliases outrank model suggestions. Import and generate explicitly confirms mapping.
- Normal End call saves then automatically generates. Import and generate, changed-summary saves and Retry generation can also dispatch cloud work. Exiting the app does not start fresh generation. Opening stored Review does not regenerate.
- Schema 6 retains full summary statements. Unfinished summary checkpoints are not complete/approvable/searchable summaries. Edited summaries require approval again; approved memories survive pending-memory regeneration.
- Pending rejection removes the proposal; approved-memory deletion has separate dependency consequences. Bulk saves are atomic background operations and intentionally prevent closing until the write resolves.
- Product usage accounting remains; test caps and historical ledgers remain separate. Product cloud eligibility never bypasses contact, source, approval or deletion rules.

## 3. Native Computer Use prerequisite — second monitor only

### Capability record

| Agent | Available route and observed evidence | Status |
|---|---|---|
| Codex | Windows Computer Use plugin, node_repl + `@oai/sky`; real Qt Home observed and Contact information opened with a screenshot-based native click on a disposable fixture. An earlier accessibility-index click did not open the panel. User then stopped Computer Use with Escape. | Basic observe/action/result demonstrated only; full QA untested. Second-monitor placement and clean completion were not verified in that earlier check. |
| Claude Opus 5.5 | Claude Code CLI 2.1.281 and Claude Desktop 1.26832.0.0 installed at inspection. No Claude-native observation/action/result has been obtained. Installed CLI and cloud connectors do not establish native access. | **BLOCKED prerequisite:** verify supported desktop integration, exact model and direct native action. |

Private Codex probe: `build/f08-planning-capability-20260926-152711/`. It used the actual Desktop with discovery disabled, a synthetic contact, separate SQLite/QSettings, key overrides and blocked sockets/providers. It was not normal production startup, capture, embedding validation, a complete workflow or evidence for Claude.

### Supported Claude route and what remains unresolved

Use Claude Desktop's **local Code tab on Windows** as the first supported route to verify. Anthropic documents Windows native Computer Use in Desktop for Pro/Max, enabled under Settings → General → Computer use, with per-session application permission. Its built-in CLI Computer Use is documented as macOS-only and unavailable in noninteractive `-p` mode. Sources checked September 26: [Desktop Computer Use](https://code.claude.com/docs/en/desktop#let-claude-use-your-computer), [CLI platform limits](https://code.claude.com/docs/en/computer-use).

The user must enable required application access and select the exact Opus 5.5 model. Record actual session/model metadata and the tools it receives. No update, installation, permission change or API-funded bridge is authorized in this planning session. If the installed Desktop lacks the feature/model, explain the exact unmet prerequisite and resolve the integration with the user. Do not substitute another model or quietly turn this into a paid Anthropic API integration.

Desktop integration is a proposed execution route, not an already connected agent. Give Claude its own frozen packet and isolated launch instructions; obtain its native action log/screenshots directly from its session. Codex may prepare the fixture and later read evidence, but Claude must choose and issue its own mouse/keyboard actions.

### Minimal check and desktop scheduling

1. Identify the **second monitor** by its actual display identity, bounds and scale. Do not assume it is to the right, that screen index 1 means the user's second monitor, or that it shares the primary monitor's DPI. If ambiguous, ask before input.
2. Place the fixture app on that monitor before interaction. Verify screenshots/bounds of the main window and every opened dialog; keep popups, source viewers and the Claude working window there too. If placement cannot be verified with supported tools, leave the check blocked. Do not operate the primary monitor or change system display settings.
3. Start a fresh disposable fixture with one fictional contact, separate settings and blocked cloud transports. Leave capture devices/windows empty and Start disabled. Preserve real confirmations. Do not use QtTest clicks or auto-confirm hooks for native evidence.
4. Agent observes Home, clicks Contact information, observes the fixture name and empty memory sections, closes the panel, and observes Home again. Record timestamps, exact model/tool, observations, action and result, including failed targeting attempts. Stop here during planning.
5. Run **Codex then Claude**, never concurrently. Close/reset the first fixture and release desktop control before the second pass. Use equivalent fixtures from the same immutable seed, separate writable stores and evidence directories. A user Escape/stop immediately stops native input.

All further native activity is second-monitor-only unless the user explicitly changes that constraint. Passing this small check establishes tool access, not product quality. The full campaign cannot claim the dual-native gate until both agents actually pass.

## 4. Isolation, fixtures and evidence

Execution uses a fresh ignored `build/f08-<timestamp>/` directory, with `seed/`, `codex/`, `claude/`, `offline/`, `startup/` and `retests/` subdirectories. Never reuse a historical paid runner/output path. Source snapshots, fixture versions and hashes identify every run. Keep a sanitized findings summary in `docs/F08-VALIDATION.md` when execution begins; do not create fictitious results now.

### Before launching a campaign fixture

- Use explicit disposable database paths for the main store **and every worker-created store**. Use separate QSettings INI files and disposable key configuration. Unsetting OPENAI_API_KEY is insufficient because the product also reads local key files.
- Replace live guidance, Ask, participant detection, extraction, summary and regeneration providers with deterministic fake/saved responses. Cover automatic callbacks as well as buttons. Block outbound provider/network calls in the fixture process; record attempted dispatches. Exercise the guard against a local stub before trusting it. No real keys are needed.
- Use local existing assets only. Block implicit model downloads. Do not import historical build runners to borrow helpers: some dispatch paid inference on import.
- Keep confirmations real in native fixtures, including cancellation and safe default focus. Reset by creating a new copy from the seed, never by editing the user's data or deleting earlier evidence.
- Preserve real contacts, transcripts, approved memories, credentials, model caches and every historical charge/reservation ledger. Do not copy private logs into Claude's review packet or Trello. Audit scoped diffs and fixture paths before and after.
- Use synthetic app screenshots only; avoid private call windows, credential panes, unrelated desktop content and raw captured media in evidence. Keep exports and diagnostic artifacts private and outside later in-app deletion claims.

### Small fixture set

| Fixture | Purpose |
|---|---|
| Empty | No contact/history/memory; missing key/runtime/device readiness; safe capability check. |
| Two contacts | Alex and Sam with distinct facts, one ambiguous alias, corrected/deleted source cases and an unassigned legacy record. No real contact data. |
| Complete call | Synthetic attributed turns, saved guidance covering all eight supported tone labels and all four Live sections, one indirect-memory link, deterministic summary and pending proposals. Separate supplied answers from actual retrieval. |
| Review stress | Draft/approved/incomplete summaries, pending/approved/superseded proposals, synthetic large batch of about 500 eligible proposals; small ordinary batch as control. |
| Import variants | Two-speaker plain and dated WhatsApp text; undated, Unicode, unknown third speaker, empty/invalid, >20-line detection boundary, one oversized message and a synthetic long transcript. |
| Delayed/failing work | Deterministic provider delay/error/invalid output, SQLite lock/write/finalize failure, stale callback and source deletion while work is pending. |

### Result vocabulary and record

`N` = not run; `P` = pass with evidence; `F` = observed failure; `B` = blocked with named prerequisite. Never turn N/B into P through source review or a historical waiver. A source-confirmed absence is recorded separately from a failed control. For example, Home has no audio-refresh button; do not invent one in the inventory.

For every control/state and scenario, record: ID, exact source/fixture hash, agent and actual model, evidence method, display/OS/runtime, preconditions, action, expected result, observed result, P/F/B, timestamp/evidence path and finding ID. Keep original failures and later retests as separate rows. `N/N` below means Codex/Claude native outcomes are both not run; offline/physical/API outcomes have separate records and cannot overwrite these columns.

Evidence methods: **native interaction**, **Qt/offscreen simulation**, **offline backend check**, **actual production startup**, **physical capture/device check**, **fresh model/API check**. Label combinations explicitly. Screenshots do not prove audio capture; fake answers do not establish semantic quality/API parity.

## 5. Current control inventory and expected behavior

This inventory comes from desktop.py and desktop_data.py on the planning baseline. Confirm it against the frozen running build at campaign start, adding any newly found control. Shared controls X01–X06 apply separately to every relevant panel; record each occurrence, not just one global pass.

### Home, setup and Live — desktop.py

| ID | Control | Expected result / required states | Codex/Claude |
|---|---|---|---|
| H01 | Light/Dark theme | Toggle both ways, persist only fixture preference; readable controls in both themes. | N/N |
| H02 | Settings | Open key-only panel; no model call or key exposure. | N/N |
| H03 | Selected contact selector | Choose/clear confirms scope, updates readiness and invalidates old guidance; no silent active-call reassignment. | N/N |
| H04 | Create | Open Create contact; Close cancels without storing. | N/N |
| H05 | Display name field | Accept valid names; readable blank/invalid/large-input handling. | N/N |
| H06 | Optional disambiguator field | Preserve entered text; empty allowed. | N/N |
| H07 | Create contact submission | Store once and select new contact; duplicate/repeated click/save failure safe. | N/N |
| H08 | Edit | Open current contact's Contact information; absent contact safely handled. | N/N |
| H09 | Contact information | Same current contact panel; no inference on open. | N/N |
| H10 | Import text | Open mapping flow only with selected contact and eligible call state. | N/N |
| H11 | Microphone selector | Explicit current device selection; no stale index restoration across restart. | N/N |
| H12 | Call audio selector | Explicit playback endpoint; all routed sound warning stays visible. | N/N |
| H13 | Microphone threshold slider | Keyboard/mouse adjust 50–2000; lower means more sensitive, not volume. | N/N |
| H14 | Call window selector | Eligible WhatsApp/Zoom/dedicated Chrome Meet only; selection/preview invalidation safe. | N/N |
| H15 | Refresh call windows | Windows-only refresh preserves contact/audio and unchanged preview. | N/N |
| H16 | Preview face | Loading/success/failure states; no paid inference or raw-media retention. | N/N |
| H17 | Home Switch face | Correct selected preview face; no silent source replacement. | N/N |
| H18 | Live and Ask model selector | Current two low-effort choices; estimate updates; review model independent. | N/N |
| H19 | Cost estimate tooltip | Readable illustrative estimate; not a balance or spending guarantee. | N/N |
| H20 | Start call | Disabled until contact/window/devices/runtime/key ready; single start, busy feedback and failure cleanup. | N/N |
| H21 | Open unsaved transcript | Recover retained text after save failure; no false “saved” state. | N/N |
| L01 | END CALL | Drain final turns, stop resources, persist then fake-generate Review; failed saves preserve recovery. | N/N |
| L02 | Refresh all | Coalesced manual refresh, correct busy state and dismissal reset; stale results rejected. | N/N |
| L03 | Transcript | Open live transcript without stopping capture. | N/N |
| L04 | Contact information from Live | Use call contact/model; browsing cannot reassign call. | N/N |
| L05 | Switch face / Continue tracking | 18-second face-loss behavior, explicit recovery, audio continuity. | N/N |
| L06 | Guidance scroll area | All four sections reachable; End/status stay accessible at constrained size. | N/N |
| L07 | Pop out — each section/item kind | Frozen contact/time/text, nonmodal and movable; multiple allowed; no inference. | N/N |
| L08 | Dismiss — each section/item kind | Shared label/cross-response dedup correct; hidden overflow does not resurface. | N/N |
| L09 | Popup Sources | Exact actual evidence only; changed/deleted evidence invalidates visible content. | N/N |
| L10 | Popup move/resize/Close | Remain on second monitor, frozen through normal expiry/End; close frees resources. | N/N |
| L11 | Transcript selection/scroll | Read-only copyable attributed turns; updates do not force reader to bottom. | N/N |
| L12 | Return to latest | Scroll to latest deliberately without changing transcript/capture. | N/N |
| K01 | Replacement API key field | Password mode; existing key only shown as fixed mask; synthetic values only. | N/N |
| K02 | Save key | Empty keeps existing; valid replacement saved in fixture only; failed write readable; no paid validation. | N/N |

### Contact information, History and Import — desktop_data.py

| ID | Control | Expected result / required states | Codex/Claude |
|---|---|---|---|
| C01 | Conversation history | Open contact-scoped history; closing refreshes parent. | N/N |
| C02 | Memory question field | 500-character bound; keyboard selection/editing; empty/Unicode input handled. | N/N |
| C03 | Ask button | One fake request at a time; loading/error/abstention; source-safe answer. | N/N |
| C04 | Enter in question | Same search; no accidental dialog close/default action. | N/N |
| C05 | Answer/quote scroll and selection | Full readable answer and literal summary quotations; suggestions labelled not agreements. | N/N |
| C06 | View conversation from citation | Correct record/shared Review; no generation on navigation. | N/N |
| C07 | Memory-list scroll | Associated and other approved memories; dates, empty states, no pending leakage. | N/N |
| C08 | Edit saved memory | Shared editor; valid revision, correction effects/Keep-Remove-Cancel choices, retrieval refresh. | N/N |
| C09 | Delete saved memory | Consequence confirmation, cancellation, dependency invalidation; unrelated data intact. | N/N |
| C10 | Edit aliases | Open aliases for selected contact only. | N/N |
| C11 | Alias list selection | Correct target; no-selection Remove safe. | N/N |
| C12 | Alias Add | Single-line editor; blank/normalized/duplicate/ambiguous cases handled. | N/N |
| C13 | Alias Remove | Remove selected association; other contacts/aliases unaffected. | N/N |
| C14 | Merge contact | Disabled in active/starting call; open target selection otherwise. | N/N |
| C15 | Merge target selector | Other contact only; no self/stale selection. | N/N |
| C16 | Merge selected contact | Effects confirmation, cancellation and atomic ownership changes. | N/N |
| C17 | Reviewed for this contact checkboxes | Explicit selection of transferred memories; no automatic approval. | N/N |
| C18 | Confirm selected memories | Only checked eligible revisions confirmed; partial/empty/stale cases safe. | N/N |
| C19 | Export data | Warn exported file survives app deletion; save/cancel/write error; exact contact scope. | N/N |
| C20 | Delete contact | Confirm affected counts; clear selected contact and stale views; preserve other contact. | N/N |
| T01 | History record list | Correct date/source/review/analysis state; empty and long history usable. | N/N |
| T02 | History Review button | Correct shared Review with no automatic regeneration. | N/N |
| T03 | History record double-click | Same record-opening behavior as Review button. | N/N |
| T04 | Reassign | Target selector then Continue; active record protected. | N/N |
| T05 | Reassignment target selector | Explicit valid contact, safe empty/stale list. | N/N |
| T06 | Continue reassignment | Show derived-memory effects before mutation. | N/N |
| T07 | Derived-memory checkboxes | Checked means delete; unchecked explicitly retains as documented; clear consequences. | N/N |
| T08 | Apply reassignment | Final confirmation; atomic reassign, source/retrieval invalidation. | N/N |
| T09 | Delete source | Effect preview and final Delete source; keep/delete memory choices honoured. | N/N |
| T10 | Unassigned | List legacy unassigned records without expanding Ask evidence. | N/N |
| T11 | Unassigned record selector | Correct original record; no-selection state safe. | N/N |
| T12 | Assign to selected contact | Preserve source text and correct ownership; no implicit approval. | N/N |
| I01 | Transcript paste editor | Plain/dated/undated/Unicode content; edits clear stale detection/mapping. | N/N |
| I02 | Open file | Qt file dialog, correct content/source label; cancel/read failure safe. | N/N |
| I03 | Detect participants | Bounded first-20-line fake request; full local parse; busy guard and late-result invalidation. | N/N |
| I04 | Which participant is the contact? | Exact alias preference, explicit correction; other speaker visibly user. | N/N |
| I05 | Import and generate | Confirm mapping, persist exactly once then fake-generate; no save merely from detection. | N/N |

### Review and shared interaction — desktop_data.py and desktop.py

| ID | Control | Expected result / required states | Codex/Claude |
|---|---|---|---|
| R01 | Saved summary selection/scroll | Full read-only saved text; unfinished checkpoints excluded from complete summary. | N/N |
| R02 | Edit summary | Whole-text editor; real edit saves draft/regenerates pending only; no-op spends nothing. | N/N |
| R03 | Approve summary | Source-safe approval including eligible linked pending memories; stale/partial refusal. | N/N |
| R04 | Reject summary | Confirmation; remove from approved search, preserving transcript and unrelated memories. | N/N |
| R05 | View transcript | Correct full original record, read-only and source-safe. | N/N |
| R06 | Retry generation | Explicit resume of eligible work/checkpoints; failure/empty success distinguished. | N/N |
| R07 | Pending-memory checkbox | Mouse/Space toggle one eligible proposal; approved rows not selectable for approval. | N/N |
| R08 | Edit pending memory | Preserve pending state and revision checks; shared editor validation. | N/N |
| R09 | Individual Approve | Exactly one eligible proposal, atomic save and correct summary links. | N/N |
| R10 | Individual Reject | Remove pending proposal, retain original transcript and approved data. | N/N |
| R11 | Approved-memory Edit | Same correction/dependency safeguards as Contact information. | N/N |
| R12 | Approved-memory Delete | Same consequence/source invalidation safeguards as Contact information. | N/N |
| R13 | Select all pending | Select eligible pending batch only. | N/N |
| R14 | Clear selection | Clear all pending checks without mutation. | N/N |
| R15 | Approve selected | Checked eligible rows only; preserve selection after failed write. | N/N |
| R16 | Reject selected | Checked eligible rows only; cancellation and rollback safe. | N/N |
| R17 | Approve all | All eligible pending memories once; no stale/superseded rows. | N/N |
| R18 | Reject all pending | Pending-only scope; approved rows/transcript untouched. | N/N |
| R19 | Approve all memories and summary | Combined source-safe atomic transaction; no partial approval on error. | N/N |
| R20 | Review later | Close without approval; reopening retains state; closing generation is not cancellation. | N/N |
| X01 | Close / title-bar close / Escape per panel | Correct nested modality and focus return; Review save intentionally blocks close, then restores it. | N/N |
| X02 | Shared editor text / Save / Cancel | Each field/action separately logged; focus starts in editor, Cancel preserves data, stale/write failures readable. | N/N |
| X03 | Yes / No / Cancel confirmations | Each applicable choice separately logged; safe No/Cancel default, clear consequences, no fake Undo. | N/N |
| X04 | File dialog navigation/name/type/Open/Save/Cancel/overwrite | Separately log import/export choices; cancel and denied/unwritable destination preserve app state. | N/N |
| X05 | Main minimize/maximize/resize/close | No clipped critical controls; close during start/call/stop/work safe; remains on second monitor. | N/N |
| X06 | Tab/Shift-Tab/Enter/Space/Escape and scrollbars | Every reachable control, visible focus, correct labels/roles, no update-driven focus stealing. | N/N |

No removed controls are silently reintroduced: there is no separate Home History, key reveal, normal diagnostics wall, manual memory creation, rejected-proposal reopening, language or text-size selector. Record usability findings about current omissions without treating historical mockups as requirements.

## 6. Functional, adversarial and recovery scenarios

Each scenario starts N; record native, offline and physical/API evidence independently. Both agents cover every native control and the core journeys; faults requiring injection may be armed by a fixture, but the agent must observe/operate the resulting real UI itself.

| ID | Scenario and acceptance |
|---|---|
| J01 | Complete synthetic call → all guidance sections → End → full Review → approve/reject/edit → restart → later indirect retrieval and Ask with exact citations. Verify the fact was retrieved from the approved fixture store, not embedded in a fake answer without retrieval. |
| J02 | Plain/WhatsApp/undated import → contact mapping correction → original text preservation → full summary/proposals → review → later search. Include >20-line speaker absence, third speaker, colon/URL continuations, Unicode and oversized messages; no invented dates or silent loss. |
| J03 | Two-contact isolation across selection, active-call browsing, alias ambiguity, merge/review, reassign, unassigned records and source/contact/memory deletion. Open popup/Ask/summary viewers during mutations and check invalidation. |
| J04 | Approved and draft summaries, offers versus agreements, source-only/memory-only/combined citations, no-match/ambiguity, superseded and deleted facts. Incomplete checkpoints remain hidden; edits require reapproval and keep approved memories intact. |
| J05 | Rapid/repeated Start/End/Refresh/Ask/Detect/Approve; close/Escape/back during discovery, preview, startup, stop, generation and saving. Correct duplicate guards, truthful in-progress state, late callbacks ignored, no stuck modal or double writes. |
| J06 | Missing/invalid credentials, offline/timeout/rate-limit/provider error, invalid structured response and exhausted provider credit as distinct fake failures. Local history remains usable; no retry storm or background cloud escape. |
| J07 | Missing/corrupt model cache, unavailable local runtime, vanished window/device and invalidated source priority. No silent device/window substitution; healthy audio survives visual loss; explicit recovery after 18-second face loss. |
| J08 | Record creation, turn persistence, finalization, edited-summary save and bulk transaction failures; locked database, disk/write failure and migration rollback using disposable copies. Preserve original/recovery text and completed checkpoints, avoid false success and generation from failed saves. |
| J09 | Cold/repeated restart and interrupted work: committed data durable, uncommitted transactions atomic, no automatic replay of completed generation. Product device choices are not restored by stale index. |
| J10 | 500-proposal batch plus ordinary control; UI timers and native input remain responsive, saves atomic, close blocking explained and released after error/success. Existing real-data timing is background evidence only. |
| J11 | At least 10 deterministic start/stop cycles and one 20-minute synthetic session. Sample process-tree memory/CPU, worker/thread/handle counts, queues, pending work and event-loop gaps. After warm-up, no orphan capture/worker, unbounded queue or continuing resource growth; investigate repeatable growth. Record baseline/deltas rather than inventing a universal MB ceiling. |
| J12 | Keyboard walkthrough in both themes; 1024×768 and 1280×720 where physical display permits, plus constrained window size. Windows 100/150/200% physical scaling checked only with supported user-controlled setup; simulated Qt scaling reported separately. Verify 4.5:1 normal text, 3:1 large text/control contrast and actual accessibility names/roles; screen-reader behavior unverified until exercised. |
| J13 | Actual Windows capture/microphone/playback checks with synthetic local target/audio or consenting call. Cover available WhatsApp/Zoom/dedicated Chrome Meet separately; previous waivers are historical. Unavailable integration/device receives B, not a pass from mocks. No fresh cloud inference without authorization. |

### Production startup and ONNX gate — J14

Use a fresh process through ordinary `python -m conversation_copilot`, preserving real module order and real discovery/runtime preparation. Isolate store/settings/key/provider access at the boundary; explicitly document any wrapper. **Do not preload FastEmbed/ONNX** or substitute `Desktop(discover=False)` for this check.

Trace the current order: __main__ → desktop/Qt → Home audio import → discovery/transcription preparation → semantic backfill → worker-store retrieval. Existing WinRT↔Qt subprocess tests cover only part of this order. semantic.py can catch embedding failures and fall back to lexical retrieval, so a visible window or model-ready marker is not sufficient.

Record installed cache path and hash, actual imports, backfill count, valid 384-dimensional embedding, main/worker cache agreement, and successful indirect retrieval before the keyword. Compare missing-model and broken-installed-model UI messages. Keep model cache unchanged; use an explicit read-only existing cache binding or an isolated copy. Repeat cold start after a confirmed fix. If a reproduction requires unavailable hardware/cache, leave the corresponding result blocked. Any eventual fix belongs in the normal production path with a subprocess regression check, not only in the demo launcher.

### Existing checks to reuse

Use maintained tests/test_f06_ui.py, test_memory.py, test_f06_ask.py, test_f06_summary.py, test_import_transcript.py, test_long_review.py, test_guidance_sections.py, test_guidance_freshness.py, test_audio.py, test_windows.py and test_capture.py. Inspect current fixture guards before running. Extend only confirmed gaps; do not build a new generic QA framework.

Run focused affected checks for each fix, then the complete offline suite once the candidate is stable. Record environment and command. Historical counts (including 446 tests) are not F08 results. Keep physical capture, native UI and real-provider acceptance distinct from the offline suite.

## 7. Execution order, findings and correction limits

1. **F08.01 Planning:** focused plan, current inventory, permanent Trello column and execution prompt. Completed only as documentation; open prerequisites remain visible.
2. **F08.02 Safety and capabilities:** freeze source/seed, verify fixture cloud block and second-monitor placement; obtain Codex and exact Opus 5.5 capability logs. Resolve missing Claude access with the user before the dual-native campaign.
3. **F08.03 Codex native pass:** current controls, core journeys, empty/busy/failure states; save independent findings on frozen baseline.
4. **F08.04 Claude native pass:** reset equivalent seed, same baseline, sequential desktop access. Claude submits its own findings before reading Codex's findings. Give both the same required coverage but allow independent exploratory choices. Do not edit source between passes; an unsafe baseline failure may block affected cases and require clearly versioned retests.
5. **F08.05 Functional/recovery/startup checks:** maintained offline checks, controlled faults, actual production startup, physical device coverage and resource measurements. These may be prepared before native passes, but do not overlap resource measurements or shared desktop control.
6. **F08.06 Bounded fixes and retests:** combine findings after both initial reports; trace callers/root cause, implement smallest correction, preserve original evidence and add a focused regression. Both agents natively retest affected UI; rerun affected backend checks and stable full suite. Stop new cosmetic scope when it endangers core gates/submission.
7. **F08.07 Reliable Windows source setup:** validate documented prerequisites/launch/recovery outside the development checkout; reconcile README with current controls and dependencies.
8. **F08.08 Preliminary Claude QA/code review:** exact Opus 5.5 reviews complete scoped diff, coverage gaps, startup/setup evidence, both native logs and corrections. Resolve material findings and obtain follow-up before user walkthrough. Its independent native pass remains a separate gate.
9. **F08.09 User walkthrough:** concrete script covering J01, import/mapping, summary correction, bulk decisions, source/deletion boundaries, resize/keyboard, recovery and startup. Record actual results and limits; fix/retest affected behavior. No assumed pass from silence or F10 acceptance.
10. **F08.10 Final review and publication:** fresh exact Opus 5.5 final review after human outcomes/corrections; follow-up and targeted human rechecks as needed. Then commit/push only reviewed scoped changes under the implementation authorization; verify local main/origin/main/GitHub main equality. No publication in this planning session.
11. **F08.11 Submission and F09 handoff:** prepare deliverables before October 1, finalize against reviewed source; record remaining F09 prerequisites. Drafting submission material can proceed alongside QA without starting Mac implementation.

Findings use stable `F08-BUG-NNN` IDs. Record severity, affected control/journey, reproducible steps, expected/actual, source/fixture version, evidence, root cause, fix disposition and regression/native retest references. Classify a suspected automation-targeting problem separately from a product defect until reproduced.

- **P0:** private-data exposure, cross-contact corruption or irreversible unintended loss. Stop affected testing; preserve evidence.
- **P1:** crash, stuck call/workflow, failed persistence or broken core journey without dependable recovery. Blocks completion.
- **P2:** reproducible wrong behavior, misleading state or substantial usability/accessibility problem with workaround. Fix within scope or obtain explicit acceptance of that concrete limitation at closeout.
- **P3:** minor cosmetic issue. Log and defer when it competes with reliability/delivery.

No blanket advance waiver. A changed prompt, provider, backend or broader redesign requires a separate decision. Model semantic errors seen in saved output remain documented limitations; fixing UI retention/attribution bugs must not become another prompt competition.

## 8. Reliable Windows setup and submission

Source setup is required; installer work is optional. Reuse Python 3.12 and pinned Qt 6.8.3 baseline until evidence supports a change. Verify pyproject requirements, wheel/assets/models, GPU/runtime requirements, native libraries, local storage paths, explicit model provisioning, key setup and actionable errors. Review distribution notices for included dependencies/assets. Do not infer compatibility with every Python >=3.12 or CPU-only Windows from metadata.

README currently contains obsolete UI/model/cap/face-loss/roadmap statements. Reconcile it against the frozen production source and this plan; retain historic results in their dated reports. Validate install/start from a new source directory with spaces/non-ASCII where practical, a fresh environment, and unavailable-network/missing-model recovery. No hidden dependency on ignored build files or private caches should be presented as reproducible source setup.

**Clean-machine target remains to be selected at F08.07:** prefer another suitable Windows PC; otherwise use a clean profile/environment or suitable VM and state its limits. A new venv on the development PC proves neither fresh-machine GPU drivers nor physical-device operation. This open logistical choice does not block writing the plan.

### Working schedule, not a confirmed user appointment

| Date | Intended milestone |
|---|---|
| Sep 26 | Plan recorded; capability/integration prerequisites visible. |
| Sep 27–28 | Sequential native passes, failure/startup checks, bounded corrections and setup evidence. |
| Sep 29 | Aim for preliminary review and user walkthrough; confirm user availability when ready. |
| Sep 30 | Final fixes/review; record video and assemble PDF/source ZIP from the reviewed candidate. |
| Oct 1 | Usable Windows/submission target; final artifact/link/access checks. |

If prerequisites or P0/P1 failures threaten this schedule, notify the user promptly with the concrete blocker. Trim installer, decoration and Mac expansion first. Do not silently pass a missing Claude test or indefinitely defer submission.

The supplied submission brief requires:

- A video of at most five minutes: idea name/one-line explanation, major implemented features, a simple API/tool/library flow diagram, and recordings of working features at readable resolution. Use synthetic data and label simulated/fake outputs honestly.
- A Google Drive link viewable by anyone with the link, checked without relying on the owner's session.
- A PDF containing video link, repository link and final Kanban screenshot.
- A source archive named **finalproject.zip**, including necessary tracked assets/instructions and excluding keys, real databases, private logs/evaluation history, venv and unrelated PDFs. Provision large external models explicitly rather than promising they are in the archive.
- The brief also requests a private repository and lecturer access. Verify requirements/current access at delivery; any sharing change, invitation or final external submission is a separate explicit action, not authorized by this planning task.

## 9. Exit checklist and F09 boundary

- [ ] Every current control/state has separate Codex/Claude native outcome and supporting evidence; no unexplained N rows at closeout. Blocked cases have named prerequisites and are not called passed.
- [ ] Both exact-agent native passes completed on second monitor, with separate logs and equivalent resettable fixtures.
- [ ] Core call/import/review/retrieval and source/contact/deletion journeys pass; no unresolved P0/P1 issue.
- [ ] Actual production startup/embedding order verified without demo preload, including worker retrieval; missing and broken model paths accurately reported.
- [ ] Affected regressions and stable full offline suite recorded; physical/API limitations disclosed separately.
- [ ] Responsiveness, cleanup, keyboard/focus/modal/resize/readability checks recorded; physical scaling/screen-reader gaps explicit.
- [ ] Windows source setup reproduced on the selected environment, with truthful hardware/model requirements.
- [ ] Preliminary exact Opus 5.5 QA/code review, user walkthrough/corrections, final review/follow-up and necessary user rechecks complete.
- [ ] Remaining lower-severity issues explicitly accepted or deferred with evidence; no invented quality/portability claims.
- [ ] Reviewed scoped publication verified; existing private data and all historical ledgers preserved.
- [ ] Submission video/PDF/source ZIP and link/access checks completed or tracked as a concrete dated delivery blocker, never silently deferred.

F09 follows F08, subject to submission priority. Carry forward whisper.cpp as the first shared free local Windows/Mac ASR candidate, current faster-whisper CPU as comparator, sherpa-onnx only if needed. Preserve working Windows CUDA backend. Record M5 and lecturer M1 exact chip/RAM/macOS before choosing baseline; actual M1 validation is necessary for an M1 claim. M5 testing is not a proxy. Mac window/audio capture and permissions remain separate work. No ASR replacement/download/comparison or paid fallback is authorized here.

## 10. Trello tracking

Board: [Conversation Copilot — Final Project](https://trello.com/b/XeJEDPBa/conversation-copilot-final-project). Preserve the existing [F08 roadmap card](https://trello.com/c/9uFlY8dH), feature IDs, earlier columns and history. Permanent column: **F08 — Polish, QA and reliable Windows setup**. Use F08.01–F08.11 from section 7 with actionable acceptance checklists and dependency/status notes. September 28 supersedes the historical planning status: F08.01–F08.10 close as the accepted limited checkpoint, with partial evidence explicitly described. F08.11 remains open for submission and deferred-check handoff. Earlier acceptance targets below are retained as the original plan.

Created September 26: 11 cards, each with three acceptance items. No execution item is marked passed.

| Card | Work | Planning-time status |
|---|---|---|
| [F08.01](https://trello.com/c/aPENtGDJ) | Focused plan and current control inventory | Done |
| [F08.02](https://trello.com/c/0ZTFQmEL) | Isolated fixtures and dual native access prerequisite | Done: isolated fixtures and both native tools verified |
| [F08.03](https://trello.com/c/Jtr8h9nM) | Codex native control and workflow pass | Accepted basic pass; full coverage deferred |
| [F08.04](https://trello.com/c/vGBY2yZc) | Claude Opus 5.5 independent native pass | Accepted basic pass; full coverage deferred |
| [F08.05](https://trello.com/c/AZE0o49N) | Functional, recovery, production startup and resource checks | Accepted offline/startup/resource evidence; physical checks deferred |
| [F08.06](https://trello.com/c/ms7dGkHX) | Bounded root-cause fixes and regression/native retests | Fixes/regressions complete; dual-native retests deferred |
| [F08.07](https://trello.com/c/VeWX3lHt) | Reliable Windows source setup and current README | Development-host source setup passed; clean-machine deferred |
| [F08.08](https://trello.com/c/WdAOrurW) | Preliminary Opus 5.5 QA/code review and corrections | Done: exact Opus 5.5 review and corrections |
| [F08.09](https://trello.com/c/4OlpS35k) | User walkthrough and targeted corrections | Done for now: user accepted requested corrections |
| [F08.10](https://trello.com/c/EVSrAkJv) | Final Opus 5.5 review and reviewed publication | Final review done; reviewed changes included in closeout commit |
| [F08.11](https://trello.com/c/X0ko56DP) | October 1 submission deliverables and F09 handoff | OPEN: October 1 video/PDF/ZIP and deferred-check handoff |

## 11. Ready-to-paste implementation / QA-session prompt

```text
Execute F08 — Polish, QA and reliable Windows setup in:
C:\Users\Banan\Desktop\Programming\Final project call helper

Read AGENTS.md, CONTEXT.md, PLAN.md, docs/TESTING.md and
plans/F08-polish-qa-setup.md, its linked current F10 reports and F08 Trello cards.
F10 is accepted; F08 is the only active feature. Preserve existing uncommitted
work, current prompts/models, Windows backend, real data and every old ledger.

Start at F08.02. Use fresh disposable stores/settings, synthetic fixtures and
fake/saved providers; verify all automatic cloud paths are blocked, including
End call, import, summary edits and retry. No fresh product-model inference
without method choice and applicable budget; old caps do not fund this stage.

Keep ALL native interaction and dialogs on the SECOND MONITOR. Verify monitor
identity/placement before input. Stop on user Escape or unverified placement.
First resolve Claude's native prerequisite with the user: exact Claude Opus 5.5
must directly observe, act and observe the actual Qt app using its own tools.
Desktop on Windows is the documented route to verify; CLI installation is not
proof. Do not install integrations or substitute another model/method silently.

Run Codex and Claude native passes sequentially on equivalent reset fixtures
and one frozen source version, with separate independent findings/logs. Cover
every inventory control and core workflow. Keep offline/Qt simulation, native
UI, physical-device and API evidence distinct. Test the actual production
startup/ONNX/worker retrieval path without the demo embedding preload.

Reproduce and triage findings, make bounded root-cause fixes with focused
regressions, retest affected native flows in both agents and run the stable
offline suite. Complete Windows source setup checks after functional polish.
Resolve clean-environment availability at that gate; do not claim a clean
machine pass from a development venv.

Require preliminary Opus 5.5 QA/code review and corrections before my
walkthrough, then actual user outcomes, corrections, fresh final review and
follow-up. Only publish reviewed scoped changes after these gates under the
project workflow; verify local/origin/GitHub main equality. Do not erase prior
failed checks or call blocked work passed. Keep October 1 and the required
video/PDF/finalproject.zip visible; protect time for submission work. F09 and
whisper.cpp investigation follow, with no ASR replacement during F08.
```
