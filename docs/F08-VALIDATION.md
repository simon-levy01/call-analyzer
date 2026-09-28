# F08 validation — 26 September 2026

## September 28 — F08 accepted for now

User tested Zoom, requested the selector/detail/number/color corrections, then said the result looks good and accepted this stage once the approval boundary check passes. Synthetic search verification passes: approved memories and summaries are included; pending proposals, both retained legacy rejections and current Review rejections, pending summaries and rejected summaries are excluded from local Ask and the actual cloud evidence payload. Unsupported citations are rejected. No search product change or paid inference was needed.

This is a **user-accepted limited checkpoint**, not completion of every original validation target. Both independent basic native passes and prior correction reviews are recorded; comprehensive native coverage and affected-flow dual-native retests, physical-device checks, alternative Zoom window modes and clean-machine Windows setup remain deferred/unverified. Development-host fresh-source/venv evidence is not a clean-machine pass. Earlier failures and all ledgers remain intact.

F08 polish is done for now. **October 1 submission remains open:** required video (up to five minutes, Google Drive link), PDF (repository link and Kanban screenshot), and `finalproject.zip`. F08.11 retains these deliverables and deferred-check handoff. F09/shared whisper.cpp investigation follows separately; no ASR replacement or Mac support is established.

The September 28 closeout commit includes these reviewed UI changes, approval regression and status updates. Earlier statements below about unpublished changes describe the pre-closeout checkpoint. Remote publication is verified separately after push; the prior `v1-working` tag remains unchanged.

### Final checks — September 28

- Search regression: **10 passed** in `tests/test_f06_ask.py`, including the new synthetic approval matrix and fake-provider payload/citation checks. Network/DNS blocked; no real data or provider calls. Private evidence: `build/f08-closeout-20260928/`.
- Final blocked-network offline suite: **464 passed**. Expanded search check after review: **10 passed**, including previously approved then rejected summaries and all-contact local search.
- Fresh exact **Claude Opus 5.5 high** final code review found no confirmed medium/high bug. Documentation findings corrected; production offer/tick/highlight clocks all use `perf_counter`. Follow-up review is recorded in private evidence.
- Current Review rejection leaves independently approved summaries eligible; legacy rejection excludes turn-linked summary statements (code-derived; shared-record linkage is not exercised by this new regression). The regression verifies rejected/pending sources are excluded, not that identical wording disappears from other independently approved sources.
- All 48 older evaluation ledgers plus the F08 API ledger verified unchanged; no new paid product inference. `git diff --check` passes.
- Current Home button roles: Refresh purple, Edit blue, Conversation history green; cues/context red in both themes. User accepted the reopened app.


## September 28 user walkthrough feedback

Subsequent requested color adjustment: Cues & context cards use muted red in dark
mode and pale red in light mode, with matching red new-item badges. This palette step changed the cards; the later Home/menu step also made Refresh purple, Edit blue and Conversation history green. Both synthetic Qt previews inspected; exact Opus 5.5
review found no blocker. Color-only follow-up, no new inference or publication;
the 463-test result below precedes this palette-only edit. Restart loads the palette.

User tested Zoom, liked the appearance, and requested three bounded changes:

- Selector: omit Zoom Workplace and auxiliary toolbar/dialog windows. Read-only
  Win32 metadata observed `Zoom Meeting` with `ConfMultiTabContentWndClass`,
  `ZPToolBarParentWnd` with `ZPToolBarParentWndClass`, and the leave-meeting dialog
  with `zLeaveWndClass`. Eligibility now accepts the observed meeting class,
  with exact meeting/webinar title fallback only when class lookup is unavailable.
  Both discovery and selected-window revalidation share this check. Fullscreen,
  screen sharing, older/localized clients and separate webinar windows remain
  unverified; a later enumeration found no Zoom windows because none were eligible
  then, so it is not counted as a native meeting-selection retest.
- Possible tones now show the existing hypothesis beneath the concise label;
  the popup preserves that same text. No additional model reasoning is requested.
- All four sections show 1–4 number badges. Newly displayed content is highlighted
  in its section color for 12 seconds; retained content keeps an outlined number.
  Reordering, ordinary redraw and repeated same evidence do not restart highlighting.
  Existing manual refresh intentionally resets display age. A recently displayed
  item can still be marked Earlier after a newer analysis omits it: the badge
  indicates appearance age, while Earlier indicates its analysis snapshot.

Exact Opus 5.5 high review identified a focus regression from rebuilding rows just
to fade highlights. Corrected by updating badge labels in place, verified through
the actual poll path with focus and widget identity preserved. Follow-up found no
confirmed medium/high issue; two low observations concern the distinct appearance
and snapshot ages above and highlighting a changed explanation under the same tone
label. Both are intentional visible-content behavior. Nonstandard Zoom modes need
native checks. No native pass is claimed for this change.

Initial focused run: 54 passed/13 failed (old first-QLabel lookups selected new
number badges, and a new test fixture omitted valid interpretation metadata).
After selecting the actual GuidanceLabel and correcting the fixture, targeted
checks: 15 passed. Final socket/DNS-blocked offline suite: **463 passed in 136.90s**.
Dark/light synthetic Qt previews inspected. Private review, logs and previews are
in `build/f08-zoom-guidance-20260928/`; original failed outcomes remain recorded.
Product prompts/models, private stores and old ledgers unchanged. User's running
app was not restarted or interrupted. Changes remain local, pending restart and
user verification; the earlier checkpoint push does not publish these new edits.

## Checkpoint publication authorization

After reviewing the fixes and API comparison, the user explicitly requested a
commit and push to main for now. This is a scoped correction checkpoint, not F08
completion. Existing Opus 5.5 reviews and the 461-check source-setup run cover the
unchanged product/test files. Private evidence, all ledgers, real data and unrelated
PDFs remain local. The earlier `v1-working` recovery tag is retained. Remaining
native/physical/user/clean-machine gates and October 1 deliverables remain open.

## Subsequent authorized API comparison

The user authorized one new **$0.30 aggregate cap** for a logged before/after run.
Completed **35/35** responses for **$0.07817512**, with no failures, retries or
unsettled requests. All prior ledgers remain unchanged. Private evidence and full
readable outputs: `build/f08-api-20260926/REPORT.html`; persistent new ledger in
that directory. No automatic continuation or reuse of its remaining allowance.

- Full 88-turn recorded log; 31 current Luna 5.6 low Live checkpoints compared with
  31 saved exact-request baseline outputs. Inputs, prompts, schema and limits match.
- Fresh Sol low extraction and full summary for both frozen source versions, using
  cloned disposable stores. Both extraction requests match, as do summary requests.
- Current summary: six statements; seven pending proposals, versus four and six
  before. One current proposal partly misattributes the user's words to the contact.
- Same saved outputs rendered through both source versions yield identical Qt text
  timelines. This supports preservation of guidance behavior, not better inference.
- Fresh outputs retain ASR-humor, stale advice and conversational-perspective issues.
  Both arms show the supplied historical memory before the explicit keyword.

No product changes, real-store writes, prompt/model revisions or publication were
made for the comparison. Recorded sensor/retrieval inputs and network-blocked
offscreen Qt evidence do not establish a new physical, native or worker-retrieval
pass. Initial offscreen missing-font screenshots are retained; installed-font
screenshots correct the harness rendering with an unchanged text timeline.
The remaining F08 gates below and October 1 video/PDF/source-ZIP work remain open.

## Current gate

Both agents completed independent basic native passes on one frozen source version.
Claude returned 20 candidate findings; corrections completed offline
regressions and exact Opus 5.5 code review. The user subsequently requested minimizing
Computer Use because of usage. Remaining native variants and affected-flow native
retests have not been passed by substituting offline checks. F10 remains accepted.
Physical capture, clean-machine setup, user walkthrough and final F08 acceptance remain pending.
Development-host source setup passed with the limits below; checkpoint publication is now authorized.

### Correction triage (all 20 Claude findings)

| ID | Disposition | Correction or evidence |
|---|---|---|
| 1 | Fixture artifact | Both native summary requests contain all four turns, including the final End turn. Fake summary selects the first three. Final-turn storage regression retained. |
| 2 | Intended behavior | Tone/context share dismissal by the accepted contract. Existing label/dismissal regressions retained; no change. |
| 3 | Defensive correction; native retest pending | Move focus to the guidance scroll area before rebuilding controls. Offline safe-focus test also passes baseline, so the native failure has not been reproduced offline. |
| 4 | Corrected | Reject normalized same-contact duplicate aliases; explicitly confirm cross-contact ambiguity. Matching still supports ambiguous names. |
| 5 | Label corrected | Transferred memories visibly require review. Backend already excludes them from retrieval until reviewed; no demonstrated eligibility leak. |
| 6 | Corrected | Undated transcript displays “Date unavailable”. |
| 7 | Corrected | Shared validation-error display removes raw schema diagnostics, URLs and input content from normal UI. |
| 8 | Corrected | Live footer points to memory-model setup in README in plain language. |
| 9 | Corrected | UI rejects identical normalized name/disambiguator; different disambiguators remain allowed. Existing data is unchanged. |
| 10 | Corrected | Shared display helper renders local seconds with timezone offset; stored timestamps unchanged. |
| 11 | Corrected | History displays actual summary review state, refreshes when Review closes and preserves selection. |
| 12 | Corrected | Blank shared text editor stays open with inline feedback. |
| 13 | Corrected | Exact unchanged Save is a no-op and preserves existing answers. |
| 14 | Corrected | Refresh import/device/export/contact-deletion status; reset stopped preview. |
| 15 | Corrected | Readable counts/model names and explicit pending-memory confirmation consequences. |
| 16 | Not reproduced | Codex native import opened Review. Dedicated Qt regression uses the real import-to-Review path; no speculative navigation rewrite. |
| 17 | Corrected | Reassignment confirmation names destination and checked deletion/unchecked retention. |
| 18 | Bounded corrections | Constrain dropdown width with full-label tooltip; give empty-action feedback and allow cancelling import discard. Alias original spelling stays intact; matching already normalizes whitespace. |
| 19 | Fixture limitation | Fake regeneration ignores edited-summary text. Existing real pipeline regression verifies edited text is sent, approved facts persist and explicit retry succeeds. No prompt change or fresh quality claim. |
| 20 | Fixture/eligibility limitation | Upgrade Ask regression to use real source selection, validation and citation navigation with only the structured provider faked. No production retrieval/prompt rewrite based on this report. |

Additional reproduced Codex finding: a corrupt copied semantic model had a readiness
marker and falsely reported semantic availability. Readiness now requires a valid
offline embedding; vectors with invalid shape, zero norm or nonfinite values fail
closed. Ordinary production startup succeeds with installed copied cache, backfills
the synthetic memory and retrieves it from the real worker before the job keyword.
The corrupt-cache candidate reports unavailable. No demo embedding preload is used.

Focused candidate v7: **17 passed**. Original frozen-baseline regression failures
and intermediate harness/assertion failures remain in private logs. Full-suite v1
and v2 each recorded **457 passed, 1 failed**: an old assertion expected the replaced
generic confirmation. The assertion was updated; neither failed run is a pass.
Full-suite v3 recorded **458 passed, 1 failed**: the strengthened Ask fake omitted
usage metadata required by the real pipeline. Correcting the fake to supply zero
usage makes the citation/navigation regression pass. Product code was not changed
for that test failure. Candidate full-suite v4: **461 passed in 130.20 seconds**, with
sockets/DNS blocked and offline Qt. Production/test hashes match the correction
follow-up review manifest.

Exact Opus 5.5 preliminary code review completed with `--effort high`, tools and MCP
disabled. Raw response metadata confirms `claude-opus-5-5`, one turn, no tool/subagent
use. It found two candidate regressions: first import paste hid the disclosure, and
cancelling discard during main-window close could leave Import with a closed store.
Both were corrected with focused checks. The review also identified a reproduced
NBSP/line-separator no-op-save issue; comparison now uses the initial editor text.
Safe validation messages now cover sibling handlers. Qt geometry reproduced the
dropdown view/container mismatch, corrected by bounding the popup rather than its
internal list. Exact-model correction follow-up completed with no confirmed remaining
bugs in the correction diff. Low residual limits remain: partial dialog closure on
cancelled exit, possible popup anchoring offset near a screen edge, repetitive error
wording, and Qt normalization of special whitespace during genuine edits. The busy
Review close guard is preceded by Desktop's pending-job wait. These are code/Qt
checks, not affected-flow native retests or final user acceptance.

The frozen-baseline sustained Qt workload completed **10 cycles + 1,200 seconds**,
11 saved calls and 11 completed review jobs. Warm-to-final resident/private growth
was 1.96/1.73 MiB; maximum event-loop gap 250 ms, final p95 31 ms. No pending jobs or
audio workers remained at close. All 193 provider responses were fake; five blocked
network attempts were guard self-probes. This is offscreen/synthetic evidence,
not physical capture, native interaction or a candidate-version long-run result.

Candidate missing-cache startup also reports unavailable correctly. Preservation
audit after corrections confirms **48 historical ledgers** and **24 installed model
files** unchanged. Current prompts/models, the ASR/capture backend and the user's
preexisting CONTEXT/PLAN changes are byte-identical to the execution-start manifest.
Only the scoped UI/readiness/asset-loading files, their tests and setup/session documentation
are changed by this execution. A clean Windows environment is still being resolved
with the user; no development-venv result will be called a clean-machine pass.

### Windows source-setup checks

A new source copy and venv were created in `setup/Windows source בדיקה`, with no
copied development environment, key, real database or ignored runtime files.
`pip install -e ".[test]"`, `pip check` and the packaged `--check` succeeded.
The latter read all 500 fictional turns/two speakers. Dependency versions and source
hashes are retained. The Windows host, Python installation, drivers and pip cache
are shared with development; this is **not a clean-machine pass**.

Ordinary production startup in that environment, using fresh data/settings and a
read-only binding/copy of installed model caches, passed real discovery, backfill,
384-dimensional vectors and indirect main/worker retrieval without an embedding
preload. It does not prove a fresh download, new GPU driver or physical capture.

The first fresh-environment suite recorded **457 passed, 4 failed**. The Unicode
source path exposed MediaPipe's native filename handling and OpenCV's `imread`:
existing verified model/portrait files could not be opened. Model loading now uses
the same verified bytes via `model_asset_buffer`, and replay portrait loading uses
`imdecode` on bytes read by Python. Model files, delegate/settings and processing
logic are unchanged. The maintained offline face-replay test now copies assets
to a directory containing spaces/Hebrew. **12 focused video checks pass**; the corrected
fresh-environment full suite passes **461 tests in 131.81 seconds**. Source/test hashes
match the current candidate. Exact Opus 5.5 high setup/code review found no high or
medium issue. It noted the preexisting gap between hash verification and a second
file read; this has not been promoted to an atomic verification claim. Small README
clarifications were applied (foundation check requires no model, provisioning links,
current control names). Original source copy and
failed run remain separate from `Windows source corrected בדיקה`.

A wheel was built for packaging inspection. Its 55 entries include product assets
and the foundation demo. Four optional F04 research audio/video files are omitted
by existing package-data patterns; full source tests need the source checkout.
The required source ZIP must include those tracked fixtures. Initial pip wheel
logging raised a cp1252 Unicode-output error while still creating the wheel;
the preserved UTF-8 (`python -X utf8`) repeat built successfully offline. This is
not a shipped wheel or source ZIP.

README now describes the current UI, models, automatic cloud behavior, source setup,
18-second face-loss buffer and 180-second guidance retention. Obsolete normal-product
caps and controls were removed; historical reports/ledgers remain unchanged.

Remaining F08 gates include clean-environment availability, affected-flow native
rechecks as needed under the user's reduced Computer Use preference, physical device
checks, actual user outcomes, final review and scoped publication. A source-colour
audit also flagged low checkbox/scrollbar/focus contrast in some states; full pixel,
keyboard and accessibility acceptance remains open. No whole-F08 pass is claimed.

For the next user walkthrough, use a fresh synthetic store/key/settings and fake
providers, not the real database: create/duplicate a contact, cancel a shared alias,
import/edit/cancel/close, open Review and approve a summary, view its Ask citation,
check unchanged/blank memory edits, then start/end a short synthetic call and inspect
retained-memory status. Record actual user outcomes and any corrections before final
review/publication. Nothing from this correction batch has been committed or pushed.

## Earlier evidence log

The dated progress sections below preserve observations and failures as recorded;
the current gate and correction results above supersede their in-progress status.

The user resumed after a physical Escape and explicitly allowed **either
monitor** while away. This supersedes the second-monitor-only restriction for
this execution session. Escape still stops native interaction immediately.

## Recovery and preservation

User requested a GitHub recovery tag before fixes. Annotated tag
[`v1-working`](https://github.com/simon-levy01/conversation-assistant/tree/v1-working)
was pushed and its remote peeled commit verified as
`cec4a5b5969f2004ee244111f4cb2c5a1d325412`, equal to local HEAD.
The tag does not contain uncommitted planning changes.

Private evidence directory: `build/f08-20260926-155722/`. Its manifest records
206 tracked file hashes, 48 historical ledger hashes and initial Git status.
`preserved-local/` separately copies the existing AGENTS.md, CONTEXT.md,
PLAN.md and F08 plan. Unrelated PDFs remain untouched. No product source,
prompt, model, real store or historical ledger was changed by capability setup.

## Capability evidence

| Check | Outcome | Evidence and limits |
|---|---|---|
| Windows displays | Observed | DISPLAY1 primary at (0,0), DISPLAY2 at (1920,0), both 1920×1080. Qt names are VG279Q3A and G27FC respectively, scale 1.0, 96 logical DPI. |
| Initial fixture launch | Failed safely | Original launcher expected Qt name DISPLAY2. Assertion stopped before creating the store/window; original script and stderr retained. This is a fixture assumption, not an app defect. |
| Corrected Codex capability | Pass, access only | Native Home → Contact information → Close → Home; synthetic contact and empty memory sections observed. Main window closed, process exit 0. Separate before/after/settled screenshots and action records retained under `codex/`. |
| Capability transport checks | Limited pass | Blocked socket `connect` and `create_connection` to loopback. This does not establish every workflow/provider guard or full network coverage. |
| Claude exact model/tools | Reported and observed | Desktop selector shows Opus 5.5; its response identifies `claude-opus-5-5` and native `mcp__computer-use__*` tools. Initial lookup stalled visibly; bounded follow-up returned the inventory. Raw text retained under `claude/`. |
| Claude native observation/action/result | Pass, access only | User granted Pythonw access. Exact Opus 5.5 independently observed Home, clicked Contact information, observed the synthetic name and empty memory sections, closed the panel and observed Home. Own native tool/action/result report retained in `claude/capability-completed.txt`; screenshots remain in its Desktop session. Access grant 13:09:59 UTC, screenshot taskbar 16:10 local. This was two controls, not the full campaign. |

The capability fixtures use separate SQLite and INI settings, no configured
key, disabled capture discovery/Start, blocked provider entry points and
socket connections. Confirmations remain real. They use `Desktop(discover=False)`
and **are not production-startup evidence**. No End-call/import/edit/retry
workflow was exercised by the capability probes. The subsequent full fixture
checks below are separate. No product inference or old-budget reuse.

## Workflow safety and native campaign in progress

`source/` freezes 55 tracked package/assets files; `source-manifest.json` records
their hashes. Both native campaigns use this same package and `fixture.py`.
The launcher uses the maintained `seed_case` appointment fixture, fresh SQLite,
QSettings and fake key file for each process; all worker stores retain that path.
It replaces SDK `OpenAI` with a deterministic fake that refuses unknown schemas.
Real review, import, budgeting, persistence and coordination paths remain active.
Audio/video/discovery are fake; semantic cache is absent and retrieval is lexical.
This is neither a physical capture check nor J14 production startup.

- Five network guard probes (`connect`, `connect_ex`, `create_connection`, DNS,
  UDP send) were blocked; an actual loopback listener accepted no connection.
- `offline/safety-v1.log` retains a harness failure: an incorrect store method
  name after End-call processing. Corrected `offline/safety-v2.log` passes End
  call, participant detection/import, edited-summary failure, explicit retry and
  Ask through the fake SDK. No workflow attempted network access. These are
  **Qt/offscreen checks**, not native evidence.
- Codex `native-v1` was closed before the fresh Claude fixture launched. Action/result records and screenshots
  `codex/native-001-*` onward. Tested portions include Home/key/contact creation,
  explicit fake device selection and preview, native Start/Live/transcript,
  all four rendered guidance sections and popup sources, shared tone dismissal,
  live Ask, End-call final-turn persistence, review edits/decisions, injected
  regeneration failure/retry, and Unicode/URL undated import with remapping.
  Unchanged summary save held fake request count at 6; it did not regenerate.
- Codex observations through `native-123` also cover Unicode alias addition/removal,
  saved-memory correction with linked-summary update, linked deletion, summary
  rejection, keyboard Ask, history, reassignment with explicit retained memory,
  source deletion, empty unassigned history, scoped JSON export, merge with explicit
  transferred-memory review, contact deletion, threshold keyboard bounds, model
  estimate update, both themes and a 1025×772 native Home window. Attempted border
  drags did not resize; keyboard system-menu resizing did. This is not an exact
  1024×768 or physical-DPI pass. Tool targeting failures remain in the evidence.
- Claude received the common full inventory and a fresh equivalent `native-v1`
  store/settings on the same frozen source and launcher. No Codex findings were
  supplied. Its native input is exclusive until it explicitly releases control.
  Unreachable injected-fault/large-batch states require supplementary fixtures.
- The injected unknown provider interruption deliberately exercises conservative
  reservation accounting. The disposable UI records a simulated $0.0239;
  **actual API spend is zero**. No historical ledger is used or altered.
- Suspected native issues await independent Claude findings and reproduction:
  retained memory visible while status says none displayed; old import-mapping
  sentence remains after editing invalidates mapping; undated transcript prints
  `None` before each speaker. No product fixes have been applied.

These observations are partial coverage. No full inventory, dual-native,
physical-device, API, setup, human acceptance or release pass is claimed.

### Independent Claude basic report received

The user subsequently requested testing/fixing all 20 findings while minimizing
Computer Use because of subscription usage. Reproduction and corrections now
prefer isolated offline/backend/Qt checks. Remaining native variants stay explicitly
unverified unless a targeted native recheck is actually performed. The original
frozen source and the running baseline resource workload are preserved separately
from the correction candidate; no fix is counted passed merely because it is written.

Exact Opus 5.5 completed its own native basic pass at approximately 17:21 local,
on G27FC, and explicitly released desktop control. It reported 53 fully exercised,
21 partially exercised and 12 unreachable inventory items. These are its own
claims, not a blanket pass of every variant: basic fixtures cannot establish failed
key writes, physical devices, restart durability or other omitted states. Its 20
candidate findings and coverage gaps are preserved independently in the private
report transcription and Desktop tool history before comparison with Codex.

One reported defect is already attributable to the fake provider: the final End
turn **was** included in both agents' four-turn summary requests. The deterministic
fake deliberately selects only three statements. This is not evidence of product
turn loss. Likewise, shared dismissal of a tone's label and its context wording is
part of the accepted display contract; preserve it. Other observations require
reproduction and severity triage, including focus moving to End after dismissal,
stale History state and transferred-memory review labelling.

Native tool activation failed after report completion; both failures were retained.
The user confirmed the desktop was unlocked. Reconnecting the tool restored native
activation and report scrolling. No Qt action was attempted during the separate
resource measurement. This was a tool interruption, not a product failure.

Supplementary fixtures now include 500 pending proposals, an unassigned record,
an approved offer summary, dated/undated/Unicode/third-speaker/late-speaker/oversized/
long imports and controlled provider/storage/key faults. The third boundary preflight
passed with six distinct fake provider errors and no workflow network attempts.
Native supplementary passes remain pending on equivalent fresh copies.

Ten focused offline storage checks passed (rollback, migration, atomic operations
and concurrent access). A short resource-harness check completed one cycle plus
seven seconds, with no remaining audio worker; this is not J11's sustained pass.
The actual ten-cycle plus twenty-minute baseline workload began at 14:25 UTC and
is still in progress. No final resource conclusion is available yet.

## Ordinary startup probes — initial J14 evidence

The command is ordinary `.venv/Scripts/python.exe -X utf8 -m conversation_copilot`
with `QT_QPA_PLATFORM=offscreen`. A private `sitecustomize.py` boundary isolates
LOCALAPPDATA, SQLite, INI settings and credentials, blocks sockets/DNS, binds the
installed audio cache read-only and uses a copied semantic cache. It instruments
the real `Desktop()` constructor with default discovery and observes its normal
backfill; it does not preload FastEmbed/ONNX or set `discover=False`. This remains
offscreen startup evidence, not native observation or physical audio capture.

- `installed-v1` and `installed-v2` stopped before app import: early instrumentation
  produced a `__main__.__file__` bootstrap error. Both logs and wrapper versions remain.
  Deferring the cache-write/import audit hook until the desktop module loads lets
  the normal entry point proceed. These two attempts are harness failures.
- `installed-v3`: ONNX/FastEmbed absent at the boundary and Desktop construction;
  real discovery found two microphone and four playback entries, left both
  unselected and reported no audio runtime error. Production backfill inserted
  one embedding. Main and worker stores used the same copied cache, produced
  `[1, 384]` vectors, and retrieved the synthetic lost-job memory by semantic
  matching from the money-wise cue before an explicit job keyword.
- `missing-v1`: no embeddings/vector, no indirect match, `semantic_available=false`.
- `broken-v1`: deliberately corrupted copied ONNX file, no embeddings/vector and
  no indirect match; load diagnostic is `InvalidProtobuf`. Retrieval nevertheless
  reports `semantic_available=true`. This is a reproduced diagnostic discrepancy
  to triage, not a successful broken-cache recovery or proof of native messaging.

The historical demo DLL failure was not reproduced in the successful ordinary
startup probe; no speculative production load-order fix has been made. Native
startup/messaging, cold repeat and full capture transitions remain to be checked.
Mid-run hashes confirm all 48 old ledgers and all 24 installed model-cache files
unchanged. Product source also remains byte-identical to the starting manifest.

## Next gates and delivery

Finish the independent native campaigns and supplementary state coverage, preserving
the frozen source and separate findings. Follow F08.05–F08.10 in the focused plan; no reviewed release
or main-branch publication is claimed by the recovery tag.

October 1 remains the Windows/submission target. Aim for preliminary review and
user walkthrough September 29, final review and video/PDF/`finalproject.zip`
assembly September 30, then link/access verification October 1. These are
working targets, not completed deliverables or confirmed user appointments.
F09/whisper.cpp work remains outside this stage.

Final-review follow-up triage: alleged rejected-summary index residue is not reproduced. `summary_versions` deletion cascades to statements/evidence/dependencies, and `summary_search_delete` removes the FTS row. Regression asserts both statement and index absence. No redundant reindex/product change was added. Legacy rejection wording corrected.
