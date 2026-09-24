# UI refinements — 24 September 2026

Work remains on `codex/qt-ui-migration`; no merge, commit or push is implied.

## Changes

- Home Refresh refreshes only the call-window list; contact, audio choices and an unchanged face preview survive. Start call retains its green styling with centered text.
- Dialog buttons no longer steal Enter as default actions. Ask Memory Enter searches; its answer area is headerless and hidden until a result arrives.
- Review uses fixed proportional panes rather than a draggable splitter. View transcript and Reject summary are direct actions. Confirmations do not repeat stored content.
- Whole-summary editing preserves approved memories, replaces pending suggestions and requests extraction from the edited summary only. Whitespace-only saves do not dispatch a request; failures preserve the correction and offer explicit Retry generation. Long source context is split using the actual serialized request size and checkpointed, so completed chunks are reused after an explicit retry. An individually oversized source turn fails clearly rather than silently truncating.
- Rejecting a pending memory erases its proposal row immediately. It does not delete the transcript or unrelated summary content. Schema 5 stores a normalized-content digest to suppress exact repeated proposals; this is a guessable fingerprint, not cryptographic erasure or semantic/paraphrase suppression. Actual approved-memory deletion retains the existing conservative dependent-summary deletion safeguards, now explained in the confirmation, and removes sibling pending proposals derived from the deleted source.
- Review mutations are disabled during generation and guarded in the store. An empty call reports that nothing was transcribed and does not offer a failing retry. A successful empty extraction is distinguished from a pending/failed job.

## Automatic generation diagnosis

Read-only inspection of three recent short production calls found completed generation jobs: two had summary content, all three had zero memory proposals, and one had an empty summary. Each had an extraction batch with non-zero output tokens (13, 29 and 224), and zero source exclusions; extraction was not skipped. No legacy rejected rows were present in the current production store. The ledger's stopped flag blocks live requests only, not post-call generation. These observations do **not** support claiming that generation never ran. The UI now explains empty results instead of leaving an unexplained blank pane. Longer-call automation is checked separately with the visible replay below.

## Ten-minute estimate

Home displays only the selected Live/Ask model's estimate: approximately **$0.07 Luna low** or **$0.41 Sol low**, including higher-end post-call generation. Prices come from the shared registry, not UI literals. The generation choice follows the final entry in the shared ordered selectable-model list; missing price data produces an unavailable estimate.

Token profiles reuse the saved 20-pair September 23 comparison: average live input 3,371.15, cached input 1,722, cache writes 1,646.15; output 351.05 Luna / 263.25 Sol. At the 12-second update interval this projects 50 updates. The September 22 shortest-call extraction/summary profile contributes 9,276 input, 9,270 cache writes and 762 output tokens, scaled from its 341.461483-second conversation span. New model IDs use the midpoint output profile until measured.

[Official OpenAI pricing](https://developers.openai.com/api/docs/pricing), checked September 24: Luna input/cached/cache-write/output per million tokens $0.10/$0.01/$0.125/$0.50; Sol $2/$0.20/$2.50/$10. This is an illustrative estimate, not a cap or billing guarantee. Speech density, chunking, caching and output vary. Ask, manual refreshes, retries and summary-edit regeneration are excluded.

## Verification

Initial offline suite: **360 passed**; final corrected suite: **368 passed** (40.02 seconds). Offline QtTest exercises actual widget mouse/key events, Enter search, editing/resizing, fixed panes, approval/rejection, failure/retry and no-op saves using disposable data. Schema-4 migration preservation, legacy rejection, sibling-source deletion, long edit checkpoint/resume, changed-payload restart, alternative-citation suppression, oversized-input handling, empty-edit recovery and running-job rejection guards have runnable checks. Active-preview preservation and concurrent receipt-attribution assertions also pass.

Opus 5.5 independently reviewed the source after the user-approved Claude Code update from 2.1.226 to 2.1.281. Three full review rounds prompted narrower rejection behavior, safer linked-summary edits, generation-state guards, preview preservation, per-job usage attribution, bounded/resumable regeneration and deleted-fact suppression. The final focused check closed all three remaining medium findings and found no newly introduced blocker. Its suggested additional guard excluding edited-summary batches from normal extraction resume was added with a regression assertion. All returned model metadata identifies `claude-opus-5-5`; no substitute model was used. Private review artifacts: `build/ui-refinements-review-20260924/`, including `final-check.json`.

Visible real-API replay: `build/ui-live-api-20260924/`, with a separate aggregate **$0.30** cap covering Luna low live guidance and Sol low generation/regeneration. The finished model-comparison ledger is untouched. Uses the saved shortest 88-turn call with original arrival timing (353.563248 seconds including setup/stop), isolated memory database and production retrieval/coordinator/API/render/review paths. Audio/video acquisition is simulated with attributed transcript turns; this is not a fresh microphone, camera or face-tracking test. Native Computer Use inspected the visible app; paid requests are logged with exact inputs, responses, source snapshot and persistent budget reservations. A setup-only missing call-window index required selecting the saved replay source before Start; no request was spent during that correction.

Private evidence stays under ignored `build/`; no call content or credentials are included in this report or Claude's code-only review. Final user visual acceptance, physical-device testing, Mac support and overall F10 acceptance are separate outstanding checks.

### Completed replay outcome

- 88/88 attributed turns processed. **32 API requests: 31 responses and one 15-second Luna timeout**, not retried. 29 Luna live attempts and three Sol requests (initial extraction, initial summary, edited-summary extraction).
- **$0.045932315 committed / $0.30 cap**: $0.044463315 known usage plus $0.001469 conservatively retained for the uncertain timeout. No open reservation or ledger reset. Provider-billed timeout cost is not known.
- Render logs show 2 unique tone texts, 3 social cues, 10 suggested responses, 1 related-memory text and 1 follow-up question. These are rendering/flow counts, not accuracy scores. Empty intervals remain legitimate; lexical retrieval reported reduced indirect recall because the optional semantic model was unavailable.
- Post-call Review opened automatically with a four-part summary and five pending memories. Saving unchanged wording spent nothing; removing the final paragraph saved a new user-edited version and generated three replacement pending memories. Approved seeded memories were untouched. The resulting Review was visibly inspected; no memory was approved in the real database.
- Read-only independent audit verified transcript count, API accounting, database/foreign-key integrity, exactly two summary versions, the exact edit, complete job and one regeneration batch. Evidence: `audit.json`, `manifest.json`, `initial-review.json`, `complete.json`, `ledger.json`, source snapshot and raw event log in the private run folder.
- Native Computer Use successfully started and visually inspected the app. Targeting child Review buttons hit an automation-helper cache limitation; those actions are covered by QtTest, not falsely counted as native clicks. The running UI/memory modules predated review corrections. The startup source snapshot is not a fully pinned build: post-call code was lazily imported while source edits were ongoing. Exact API inputs/responses and final data are preserved, but the run cannot certify one immutable final code revision. Later safety/accounting/long-call fixes were tested offline, without spending on another replay; the harness now eagerly imports post-call code for any future explicitly authorized run.

Model output still requires user review: generation can produce test-session details rather than useful lasting memories. This UI work does not establish uniformly correct semantic interpretation or introduce another prompt-tuning round.

### Explicit remaining limitations

Changed summary paragraphs without an exact original match conservatively inherit the visible summary's source union; deleting a linked approved memory can therefore remove a larger corrected paragraph, as the confirmation warns. Storage still divides long paragraphs into bounded 280-character statements. Edits save as drafts and explicitly require reapproval for Ask. Restoring legacy source exclusions has no new normal-UI control; unavailable sources are reported and cannot enter retry loops. The historical F04 runner's old-model compatibility is deferred, not silently relabeled or rerun.
