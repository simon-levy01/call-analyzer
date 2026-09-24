# F10 — UI/UX and accessibility

## September 24 — revised Review and Home controls

Latest user instructions supersede older detailed controls below: window-only Refresh preserving contact/audio/unchanged preview; centered green Start wording; Enter searches Memories with a headerless result; fixed proportional Review panes; direct View transcript and Reject summary (no More actions); whole-summary editing regenerates pending memories only for changed wording and preserves approved memories; concise confirmations, immediate rejected-suggestion deletion with no reopen/permanent-delete step. Show only the selected model's illustrative ten-minute cost including higher-end post-call generation. Distinguish empty successful generation, no transcript and retryable failure. See [verification](../docs/UI-REFINEMENTS-20260924.md); user acceptance is still pending.

## September 22 — GPT-6 model update

Supersedes every earlier Luna/Terra choice below: Live/Ask now select GPT-6 Luna low (default) or GPT-6 Sol low. Memory extraction, imported-text generation and the post-call summary pipeline follow the higher-end entry of that ordered list, currently Sol low, regardless of the Live/Ask selection. Luna medium is a requested timing-test arm only, not an additional UI option. Historical results and evaluation caps remain unchanged. See [migration verification](../docs/GPT6-MODEL-UPDATE.md).

## September 22 — user-authorized Qt migration

The user explicitly superseded the earlier keep-Tk assumption: select the best maintainable/customizable Windows/macOS toolkit and migrate the full interface on a branch. Work is on `codex/qt-ui-migration`; `main` is unchanged. Selected PySide6/Qt Widgets with shared light/dark styling and SVG control assets, retaining the Python capture/memory/inference backend. See [decision and checks](../docs/F10-QT-MIGRATION.md).

Home, Live, Settings, Memories, History, Import, Review and nested dialogs now use Qt. Start is larger and requires contact, explicit audio devices, call window, runtime and configured key. Slow discovery/start/stop/model work runs outside the GUI thread. Secondary windows are application-modal except frozen suggestion popouts. Native macOS capture remains F09, not an implied result of changing UI toolkit.

The user's reduced Memories scope still overrides the old data-management surface: Edit/Delete per memory and only aliases/merge/export/delete-contact controls. Merge-specific confirmation lives inside Merge, not as an extra normal Memories action. Old manual creation, all-contact filters, connections, cloud toggles and diagnostic model/settings buttons remain intentionally omitted. Automatic import/post-call generation remains approved behavior; no new permission prompt or product monetary cap is added. User acceptance and post-user-test review remain pending.

**Status:** S1–S3 system work and the current U1–U3 interface pass are implemented with offline coverage. A tool-disabled Claude review was completed and its concrete button-state, focus, popup-safety and Review-selection findings were corrected on September 22, 2026. Native computer-use access was unavailable; user visual acceptance and final review remain pending.
**Priority:** F10, then F08 Windows installation/review, then F09 macOS. October 1 remains the usable Windows MVP target with documented source setup.

**Trello:** Permanent `F10 — UI/UX and accessibility` column created on the project board. [Planning card](https://trello.com/c/w7tndIg7), [roadmap card](https://trello.com/c/nXjwv5A1). Cards F10.01–F10.11 cover planning/feasibility, S1–S3 system work, U1–U3 UI work, accessibility/integration, preliminary review/corrections, user walkthrough/corrections and final review/publication. Trello status has not been updated by this local implementation; review work remains pending and the plan is not yet published to GitHub.

## Goal and accepted decisions

Replace the testing-oriented interface with three main screens: **Home → Live call → Summary and memories**. Contact history opens the same summary/memory editor. Supporting tasks use panels or small windows instead of more top-level destinations.

The latest user decisions supersede conflicting older F10 inventory entries:

- Home combines contact selection/creation, one Memories search/management entry point, history, text import and call setup.
- Live/Ask model selector: **Luna low** (default) or **Terra low** only. Sol is not selectable; reasoning has no separate control.
- Terra's standard token rates are 10× Luna's; do not claim every call costs exactly 10×.
- Memory creation uses fixed **Terra low**. Planning interpretation: the whole post-call generation pipeline, including summary generation/consolidation, and imported-text memory extraction use Terra low; the Live/Ask selector does not affect them.
- Verified baseline differs from the user's assumed starting point: current extraction, summary and live/Ask paths use Luna. Moving post-call/import generation to Terra is a system change, not preservation of an existing default.
- Cloud use is automatic and allowed for all otherwise eligible content, including sensitive content and previously cloud-blocked content. Remove routine per-action cloud permission prompts and controls. Approval, ownership, correction, deletion and source-validity rules still apply.
- No application monetary caps for normal product operation. Keep ongoing estimated cost, actual model/usage attribution and uncertain-request accounting. Provider credit/quota limits still apply. This product decision does not run inference now, authorize evaluation spending, or reset historical evaluation ledgers/caps.
- One **Refresh all** action in Live. No per-item or per-category refresh/generate buttons; automatic updates continue.
- Five live categories: **Possible tones, Social cues, Replies, Related memories, Follow-up questions**. “Intents” means existing tone interpretations; do not add intent prediction.
- Up to **four useful items in each category**, all reachable without the old two-plus-More restriction; no filler. Stable category positions, individual **Pop out/Freeze**, **Dismiss** and compact source access.
- Freeze is only a temporary copy in a popup, independent of live refresh. It is not memory creation, approval or a pause of the pipeline.
- Face-loss tolerance increases from six to **18 seconds**.
- Memories combines natural-language questions and management in one contact-scoped screen: show the answer, the saved memories associated with it, and the remaining saved memories. Each memory shows its saved date and only Edit/Delete actions. Do not show raw sources, evidence, confidence or pending/rejected proposals there. The only contact controls on this screen are Edit aliases, Merge contact, Export data and Delete contact. No local-versus-cloud choice in the normal flow.
- Review supports individual approve/reject, checkbox multi-selection with approve/reject selected, approve all memories, reject all pending memories, and approve all memories plus summary.
- Settings contains only the API key: reuse the current system key by default and display stars. Never expose or copy the key into documentation, logs, screenshots or Trello. Text size, contrast, motion, language, help and contact-management settings are intentionally omitted.

## Screen map

```text
Home
 ├─ Selected contact → Memories / History / Text import
 │                                      └─ select record → Summary and memories
 ├─ Settings → masked API key and replacement override only
 └─ Start call → Live call
                 ├─ Refresh all / Dismiss / Pop out item
                 ├─ Show transcript / Memories
                 └─ End call → Summary and memories → Back to Home
```

These wireframes describe hierarchy, not final pixel placement. Keep capture ownership independent of view construction/destruction. September 22 refinement: secondary windows (including Settings, Memories, History, Review and Transcript) block interaction with their parent until closed; nested dialogs restore the parent's modal ownership. Live suggestion popouts alone remain non-modal. Capture continues while a modal window is open.

Home's Create, Edit, Memories, History and Import buttons share one horizontal centerline and respectively use the tone, social cue, memory, reply and follow-up category colors. Start call retains its primary blue. Use custom rounded artwork for buttons, cards and selectors, a compact model selector, and omit the attributed-text retention banner entirely.

## Screen 1 — Home

```text
Conversation Copilot                                      [Settings]
Contact [Search/select........................] [Create] [Edit]
[Memories] [History] [Import text]

Call window [.................................] [Refresh]
Microphone  [.................................]  [level]
Speakers    [.................................]  [level]
Mic sensitivity [-----------------------------]
Small selected-face preview                    [Switch face]
Live and Ask model [Luna low / Terra low]
Terra: 10× Luna token rates. Review generation: Terra low.
Readiness / concise endpoint-wide audio notice
                                                    [Start call]
```

- Choosing a contact from the selector confirms it immediately. Create adds a contact; Edit opens the combined Memories/contact-management screen. Changing the browsing contact outside a call does not silently reassign a running call.
- Start requires a confirmed contact, eligible call window, selected input/output devices and working local runtime. Surface missing key/readiness before a paid workflow; no paid key validation merely from opening Home or Settings.
- Preserve current eligible WhatsApp/Zoom/dedicated Chrome Meet rules, source priority and explicit device selection. Microphone sensitivity controls the existing speech threshold, not playback volume. Show levels without adding unsupported speaker sensitivity controls.
- No prior device index is restored across app restart. Preserve current clean-stop convenience only while its enumeration remains valid.
- Memories opens one contact-scoped surface with a natural-language question field, answer, associated saved memories and other saved memories. Show saved dates and Edit/Delete per memory. Do not show sources, evidence, pending/rejected proposals or add/connect actions. A compact contact strip contains only Edit aliases, Merge contact, Export data and Delete contact.
- History is a contact-scoped panel with date, source, duration where available and review status. Select a call or import to open the shared editor. Pending-review indicator on Home/history; unassigned legacy records can be assigned here. Calls without a selected contact are no longer the normal Start path.
- Import text opens a file/optional paste preview, participant mapping, chronological text and date/time-zone assumptions. Confirming import saves normalized text and automatically starts Terra memory generation; show processing and cost. Media placeholders/unsupported formats get clear messages. Reuse parser rules, do not invent duplicate-import detection.

## Screen 2 — Live call

```text
Contact · duration · model · estimated spend $...          [End call]
Compact audio/video/cloud state                           [Refresh all]

Possible tones                 Social cues
  item + confidence              item + confidence
  [Pop out] [Dismiss] [Source]    [Pop out] [Dismiss] [Source]

Replies                        Related memories
  up to four items               up to four items

Follow-up questions — up to four items

[Show transcript] [Memories] [Face preview / Switch / Continue]
```

- Show every available item up to four/category; wrap/scroll within a usable layout, with End call and status always reachable. Empty categories may show one concise availability message, never fabricated cards or advice to wait.
- Automatic generation and Refresh all use the shared coordinator. Keep the previous valid result while a refresh is pending; visibly mark updating without falsely making old evidence fresh. No new inference from layout changes, opening a popup or exposing hidden content.
- Dismiss removes that item from the live display and follows existing repetition suppression. Explicit Refresh all may reset dismissals as current manual refresh does. Contact/source invalidation and accepted source-age expiry still apply to the live view.
- Pop out copies the clicked item to a small movable, resizable, always-on-top window. Show its contact, category and captured time, plus Close. Its wording stays fixed as live updates continue; multiple popups may coexist. No special pin management, persistent collection or new saved-memory workflow.
- A popup is visibly a captured suggestion, not current advice. It survives normal source-age expiry and End call until the user closes it or exits the app. If an underlying source/contact is deleted or corrected, invalidate its sensitive content and explain that the source changed; do not leave stale deleted data on screen.
- Transcript popup updates without stealing focus or forcing the reader to the bottom after scrolling up. Use speaker labels, timestamps, selectable text and Return to latest; closing it leaves transcription running.
- Memories opened from Live uses the call's contact and current Live/Ask model. Its submitted question/answer runs independently of capture and shows the associated editable/deletable memories. No contact switch, source display or separate cloud button appears on this surface.
- Face controls stay compact. During loss, audio/transcription continue. Before 18 seconds, reacquire only the selected track; after that require Continue tracking. Never silently switch to another participant.
- End call stops capture safely, retains finalized turns and transitions to Review. Flush completed audio results before generation; prevent duplicate end-call jobs.

## Screen 3 — Summary and memories

```text
Contact · record date · duration · generation model · estimated total
Generating / ready / partial / failed                      [Back to Home]

Summary                           Memories from this conversation
[Editable source-linked text]     [ ] Memory text ... [Approve] [Reject]
[Approve summary]                 [ ] Memory text ... [Approve] [Reject]
[Sources]                         [Select all pending] [Clear selection]
                                  [Approve selected] [Reject selected]
                                  [Approve all memories] [Reject all pending]

[Approve all memories and summary] [Save draft / Review later]
Secondary: regenerate/continue, versions, transcript, source/data actions
```

- Newly ended calls automatically generate Terra-low summary and memory proposals. Opening historical records loads stored results into this same editor without automatic regeneration or reapproval.
- Distinguish draft/pending/approved/rejected/excluded and historical states. Edit either summary or memory and reuse source-linked correction previews; ambiguous linkage must not overwrite unrelated facts.
- Checkbox actions act on the selected eligible pending proposals. “Approve all memories” covers every eligible remaining pending proposal for this record, not just those linked to the summary. Combined approval includes the summary and all those pending proposals in one validated transaction.
- Reject individual/selected/all applies to pending proposals; it does not delete approved memories. Existing approved memories have explicit correction/deletion actions. Rejected items remain in review history with Reopen/Permanent delete in secondary actions.
- Bulk action previews show which items are affected. Revalidate revisions/sources before committing; no partial bulk mutation if selection changed. Keep content approval separate from automatic cloud permission.
- Preserve excluded/rejected summary dependencies, linked edit choices, sources, prior versions and sensitive labels. Cloud permission buttons disappear, but the sensitivity metadata remains useful context.
- Save draft/Review later preserves edits without approving them. Generation does not silently overwrite a draft the user is editing. Regeneration remains explicit, retains prior versions and protects saved corrections/deletions.
- Display partial progress/failure, retain completed chunks and allow explicit Continue/Retry. Provider exhaustion does not lose the transcript or already generated work. Successful chunks should complete automatically without an app-dollar stop.

## Supporting surfaces

| Surface | Scope and controls |
|---|---|
| Memories | Contact label, natural-language question field and Ask/Enter; model-based natural-language answer; associated saved memories followed by other saved memories; saved date and Edit/Delete on every memory. Cover loading, no match, ambiguity and provider error without showing raw sources, evidence, scores or pending/rejected proposals. Only Edit aliases, Merge contact, Export data and Delete contact appear as contact actions. Home and Live open the same component and selector. |
| Settings | Masked existing API key and replace/save override only. No text-size, contrast, motion, language, privacy/help or contact-management sections. |
| History actions | Reassign record with derived-memory effects, delete source with keep/delete-memory preview, legacy unassigned assignment, transcript/source access and supported exports. |
| Evidence | Reuse exact source viewer across cards, popups, memories, Ask and summary statements. Label current versus corrected/historical sources and unavailable/deleted evidence. Only claim sources actually cited by the answer. |
| Setup/recovery | Missing key/model/dependency instructions, device refresh/reselection and provider errors. No normal-screen diagnostic wall. Advanced opt-in private logging/troubleshooting remains secondary. |

API key implementation: resolve the existing environment/.env mechanism without exposing the value. Show a fixed masked indicator for an existing key rather than writing stars back as a credential. Untouched masked input means reuse existing key; typing a replacement is an explicit update. Keep any persisted override in the existing appropriate private local configuration or an OS-supported secure store, outside version control. No new account system, reveal toggle or automatic paid test.

All-contact discovery remains a secondary data action, not a scope switch in the combined Memories screen. Browsing another contact never changes call ownership. Retain existing date clarification and source-exclusion review only when relevant.

## System work and operation coverage

| Slice | Required change | Existing code to reuse/check |
|---|---|---|
| S1 — Models, cloud policy and accounting | Centralize the two live/Ask choices at low reasoning; fixed Terra low for review/import generation. Pass exact model into request, estimate and provenance. Enable cloud for otherwise eligible sensitive and previously blocked content without changing approvals or erasing historical permission records. Remove normal-product dollar stops while preserving accounting and evaluation caps. | `interpretation.py`: model table, key loader, UsageLedger, OpenAIInterpreter, f06_structured_request; `guidance.py`: interpret_guidance; `ask_memory.py`: cloud_answer; `memory.py`: OpenAIMemoryExtractor, analyze_record, cloud/source filters; `post_call.py`: estimates/generation. Audit UI call ceilings, extraction preflights, Ask per-answer limits and review continuation limits. |
| S2 — Live behavior | Increase only user-facing tone/cue/reply/remember/follow-up list limits from three to four through schema, instructions, parsing, display and local remembered-item blending. One Refresh all; Dismiss and temporary item snapshots for all five categories. Increase face loss to 18 seconds. | `interpretation.py` tone/cue schemas; `guidance.py` schemas, instructions and GuidanceDisplay; `video.py` loss threshold; `__main__.py` rendering/coordinator. Do not globally replace every three-item bound: citation/modality limits and unrelated collections are separate. |
| S3 — Review and Ask operations | Record-level approve/reject selected/all with source-safe atomicity; reuse historical editor; automatic post-stop pipeline without product spending cap; one model-based Ask action returning cited sources. | `memory.py`: review_proposals, approve_summary, correction/reassignment/deletion/export; `post_call.py`: process_review; `ask_memory.py`: retrieval, cloud_answer and validate_sources; `__main__.py`: finish_memory_record, open_review, open_ask. |
| U1 — Shell, Home and Settings | Three-screen navigation, contact/setup Home, masked key, compact readiness and selected-contact management. | Existing Tk widgets, contact search/create/select, audio catalog/threshold, window selection and contact/data operations. |
| U2 — Live and floating windows | Five categories, four-item layout, Refresh all, Dismiss, Pop out, transcript and access to the combined Memories surface; persistent End call and cost. | Existing timers, source viewer, renderers, safe window lifecycle and transcript flow. |
| U3 — History, import, memory and review UI | Combined Memories question/list/editor, contact history and pending review entry points; one Review editor; checkbox review; text import preview; close/edit handling. | Existing Ask retrieval, record choosers, import parser/store, manage_memory, review dialog and bulk operations. |
| U4 — Accessibility and integration | Keyboard/scaling/focus, recovery states, remove diagnostic controls, source setup docs and full saved-output walkthrough. | Existing UI/regression tests and disposal-safe stores. |

System slices establish operations first with fake/saved outputs; UI slices consume them. Implement sequentially as one F10 feature. Reuse SQLite and existing capture/retrieval/review operations; avoid a new service framework. Keep the current Tkinter approach unless a bounded accessibility/resize feasibility check demonstrates a concrete failure. Any toolkit replacement requires an explicit feasibility decision before implementation.

No monetary cap does not mean unlimited context/output, concurrent requests or blind retry loops. Retain finite request limits, chunking, current automatic cadence, cancellation/generation guards and accounting for failed/uncertain requests. Validate whether four items fit the current output budget; if not, make only the necessary bounded token change and record it. No new semantic calibration round or rejected F07 experiment merge.

## Failure copy and accessibility acceptance

| Trigger | User-facing message/action |
|---|---|
| No contact | “Choose or create a contact before starting the call.” Highlight Contact. |
| No microphone | “Choose a microphone. If it is missing, reconnect it and refresh devices.” |
| No speakers/playback | “Choose the speakers or headphones carrying the call audio.” |
| No call window | “Choose an active WhatsApp, Zoom or dedicated Chrome Meet call window.” |
| Missing key | “An API key is needed for assistance. Add it in Settings.” Local saved history remains available. |
| Provider insufficient credits | “Your API account has no available credit. Add credit, then retry. Your transcript is still being saved.” Use only when the provider error supports that diagnosis. |
| Rate limit / authentication / timeout | Distinct messages: temporarily rate-limited; key rejected; request timed out. Never label every provider failure “no usage left.” No repeated paid retry loop. |
| Face temporarily missing | “Face not visible. Audio and transcription continue.” After 18 seconds, show Continue tracking. |
| Video lost / device disconnected | Explain which stream stopped, retain what is healthy, offer explicit reselection; never switch devices/windows silently. |
| No supported guidance / no memory match | “Not enough recent evidence” / “No approved information found for this question.” No filler or fabricated answer. |
| Source changed / store busy / generation failed | Invalidate affected content, preserve unsaved edits and completed work, offer reopen/retry when applicable. |

- Keyboard: every control reachable with Tab/Shift+Tab, visible focus, Enter submits a Memories question, Space toggles checkboxes, Escape closes secondary popups without ending the call. Closing the live/main window must make stopping/saving explicit.
- Use text labels, not color-only states; target at least 4.5:1 normal-text contrast and 3:1 large text/non-text controls. Check actual toolkit screen-reader names/roles on Windows; report unsupported behavior honestly.
- Check main screens at 1024×768 and 1280×720, and Windows 100%, 150% and 200% display scaling on a suitable display. Provide scroll/reflow at constrained logical sizes; End call and status remain reachable. Small beside-call layout must keep all categories reachable.
- No live-update focus stealing, flashing, forced transcript scrolling or automatic popup opening. Freeze and transcript popups open only from user actions. Stable category order and reduced-motion default.
- Destructive contact/source/memory actions retain consequence previews and safe Cancel focus. No invented Undo for irreversible deletion.

## Validation, demo and release

1. Use fictional contacts and disposable databases with saved/fake model outputs first. Never launch against private call logs just to demonstrate UI.
2. Offline checks: model/low-reasoning propagation across all entry points; no Sol selection; product uncapped accounting versus preserved capped evaluation; all-content cloud eligibility without bypassing contact/approval/deletion rules; four-item boundary/no filler; coalesced refresh; 18-second loss threshold and continued audio; snapshot lifecycle; source invalidation; checkbox atomic approve/reject; no inference on history open; key masking/no credential logging.
3. End-to-end saved-output walkthrough: create/select contact → open Memories → ask a natural-language question → see the answer and associated memories → edit/delete against a disposable store → import memory → setup devices/window → start → five live categories → refresh/dismiss/pop out → read transcript → open Memories from Live → end → generate Terra review → edit and approve/reject individual/selected/all → reopen history in same editor. Repeat empty/failure, model switch, close/reopen, scaling and keyboard cases.
4. Fresh model-dependent testing still requires API/agent/local method selection and its applicable evaluation budget. Existing F07 evidence/budgets remain intact. No fresh inference or quality claim is authorized by creating this plan.
5. Complete affected automated checks and preliminary verified tool-disabled Claude Opus 5 review of plan/diff/evidence; correct findings before user testing. User walkthrough and corrections, then fresh final Claude review/corrections. No review pass is claimed here.
6. Update documented Windows source setup, publish only reviewed changes when implementing the agreed workflow, and verify local/origin/GitHub pointers. No commit/push is performed by this planning session.

## Risks, boundaries and next design step

The main risks are four-item density on a small screen, source-safe bulk actions/popups, Tk accessibility, increased cost without app dollar caps, and model changes affecting latency/output quality. Visible cost is an estimate, not a live provider balance; unknown usage is not zero cost. Do not attempt balance polling with unsupported APIs.

No new intent classifier, Sol selector, auto-sent replies, persistent frozen collection, full backup/restore, cloud account system, raw audio/video upload, biometric identity, new language, dedicated installer, Mac implementation or presentation work. Raw sensor metrics, separate manual test-model buttons, debug reasoning controls and local/cloud choice buttons leave the normal UI; useful diagnostics remain secondary.

Deferred system follow-up: stored rows already have audit timestamps, but memories and summary statements do not automatically derive semantic event date/time metadata from their own content. Add that later with source provenance, time-zone handling and the existing approval/correction/deletion boundaries; it is not part of this UI-only pass.

Next: review these screen wireframes with the user, then choose concrete spacing/density and run the bounded Tk layout/accessibility feasibility check. This plan records behavior and implementation scope; polished visual mockups and implementation/review remain outstanding.
