# F10 UI implementation prompt for Claude Design

Implement the F10 Conversation Copilot desktop UI from the supplied reference images and the current GitHub repository. The current branch is a functional checkpoint: its Tk UI is wired to the existing operations, but its visual implementation is not accepted and does not match the mockups. Replace the presentation layer so the rendered product closely matches the images, while preserving the working system behavior and privacy/data boundaries.

Read these files before editing:

- `AGENTS.md`
- `CONTEXT.md`
- `PLAN.md`
- `docs/TESTING.md`
- `plans/F10-ui-ux-accessibility.md`
- `conversation_copilot/__main__.py`
- the five PNG references in `docs/f10-ui-mockups/`

Use only the latest five references:

1. `01-home.png`
2. `02-live-call-compact-v3.png`
3. `03-summary-and-memories.png`
4. `04-settings.png`
5. `05-manage-memories.png`

Ignore `02-live-call.png` and `02-live-call-compact-v2.png`; they are superseded.

## Non-negotiable visual direction

- Match the mockups as a coherent product: warm-white background, white cards, deep navy text, accessible bright-blue primary actions, green success, restrained red destructive actions, thin cool-gray borders, rounded cards, simple line icons, strong spacing and hierarchy.
- Do not leave any screen looking like default Tk widgets arranged in label frames. Create a deliberate theme and reusable styling only where it reduces duplication.
- Support keyboard navigation, visible focus, large click targets, readable wrapping, Default/Large/Extra large text, standard/high contrast, and reduced motion.
- The normal screen must fit without horizontal scrolling. Primary Home, Live, Review, Settings, and Manage Memories content should fit at their intended window sizes; resize/reflow instead of hiding essential controls.
- Remove `Unassigned` from the primary Home UI. The underlying retained-record workflow may remain reachable through secondary data/history actions if needed.

## Home

Follow `01-home.png`: contact selection and Create/Edit/Manage memories/Ask Memory/History/Import at the top; audio/call setup on the left; small selected-face preview before starting on the right; Luna low/Terra low segmented selector; readiness notice; Settings and Start call. Keep every existing operation wired.

## Compact Live companion

Follow only the narrow right-hand Conversation Copilot panel in `02-live-call-compact-v3.png`. The large video-call window shown to its left is a separate app and is not part of Conversation Copilot.

- The companion must be narrow enough to sit beside the call.
- Do not show the tracked face image after the call starts. Show only a tiny Face status and Switch/Continue action.
- Show Audio, Face, Cloud, contact, duration, selected model, cumulative call spend, End, Refresh all, Transcript, and Ask Memory.
- Show all five groups together: Possible tone, Social cue, Replies, Related memory, Follow-up.
- Do not show percentages or numeric confidence.
- Do not show raw evidence or an Evidence button on primary cards.
- Tone and social-cue cards show a cautious potential interpretation and a short `Why:` line, using saved-output phrasing such as:
  - `The recent atmosphere may be calm.`
  - `Why: Synthetic available observations.`
  - `The remote participant may be uncertain.`
  - `Why: Hesitant wording.`
- Example saved responses:
  - `What date would be realistic?`
  - `Would you like to tell me more?`
  - `Possibly related: the saved trip details.`
  - `Could we confirm the date?`
- Each item supports Pop out and Dismiss. Exact sources remain available inside the pop-out/details view.
- Up to four items per category must be reachable. At the intended compact size, keep all five category headers visible and use compact rows/reflow or responsive scaling rather than the old page-level scrolling layout.
- Luna low and Terra low are the only Live/Ask choices. Review and memory generation remain fixed to Terra low.

## Summary and memories Review

Follow `03-summary-and-memories.png`. Use the same screen for the just-ended call and historical records. Include metadata/status, editable summary, summary approval and sources, memory checkboxes, individual Approve/Reject, Select all/Clear, Approve/Reject selected, Approve/Reject all pending, combined `Approve all memories and summary`, Save draft/Review later, Regenerate/Continue, Versions, Transcript, and secondary source/data actions. Preserve optimistic-concurrency behavior in the existing store methods.

## Settings

Follow `04-settings.png`. Never display the actual API key; only show masked/configured state and accept an explicit replacement. Include persisted text size, contrast, reduced motion, privacy/cloud explanation, selected-contact aliases, merge/export/delete actions, help, Cancel, Save settings, and Back to Home.

## Manage Memories

Follow `05-manage-memories.png`. Replace the current oversized utility dialog with a simple list of saved memories. Show when each memory was saved and provide only Edit and Delete actions for each memory, plus Back to Home and Done. Do not show search, sorting, filters, pending proposals, rejected items, sources, source names, add/connect actions, contact management, aliases, merge, export, or any cloud-permission control. Delete keeps its existing confirmation and exact scope.

## Implementation boundaries

- Preserve all current backend behavior, storage rules, source validation, cumulative usage/cost accounting, 18-second face-loss buffer, review budgets, and deletion/approval boundaries.
- Do not run API, agent, or local-model inference. Use saved fixtures only.
- Do not rewrite the memory, audio, video, interpretation, or review pipelines just to style the UI.
- Do not add speculative framework layers. Reuse existing callbacks and store operations.
- Keep API keys and private call data out of logs, screenshots, fixtures, Git, and generated artifacts.

## Verification

Run the full offline suite and add/update focused Tk UI tests that invoke every non-destructive visible button and validate destructive button wiring against a disposable store. Test Home, compact Live, Review, Settings, and Manage Memories at default, Large, Extra large, and high-contrast settings. Verify keyboard-only navigation and resizing. Do not claim native computer-use verification unless the environment actually exposes the Tk window to the computer-use tool.

Return a concise list of files changed, the exact offline test result, screenshots of the rendered five screens, and any visual mismatch that remains.
