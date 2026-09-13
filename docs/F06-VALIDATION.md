# F06 validation record

**Closure update, 2026-09-14:** User accepted F06 as complete for now with documented Luna limitations and authorized publication. No additional final Luna live call or fresh final Opus review is claimed; latest review was Sonnet 5. This closure supersedes older pending-gate statements below. See the master plan closure record.

Status: earlier preliminary Opus 5 gate passed; user reported reply-direction and summary UX issues. Corrections and user-authorized behavior changes are implemented; user rechecks and fresh final Opus 5 review remain pending. No implementation commit/push.

## Baseline and scope

Local main, origin/main, remote main (`git ls-remote`) and the GitHub commits API independently matched `cf8d7d35de99fba3f8baee2245b2a49170dc132b` before work. The four unrelated untracked CV PDFs are untouched. F01–F05 stay accepted with existing exceptions and September 7 dedicated-Chrome Meet evidence; F07–F09 are excluded.

## Automated checks

Latest whole offline suite: **250 passed in 22.46 seconds**, including the 41-turn failure/resume/consolidation/usage test.

Coverage includes v3 legacy deletion quarantine, older migrations, injected migration rollback, approved-only retrieval, proposal rejection/restoration, Keep/Remove transactions, permission intersection, deletion scrubbing, generation guards, cancelled summary checkpoints, exact-source invalidation, temporal filtering before ranking, temporary questions, independent contact scope, hidden candidates, 12/24-second timers, budget equality and worker priority.

The isolated Tk test uses fictional SQLite data, hidden windows, fake device discovery and no model startup. It checks independent Ask contact selection, busy-validation retry, in/out-of-call ledger attribution across Stop, changed-question cloud gating, clearing an answer after external source deletion, embedding backfill resume, and duplicate review-dialog reuse. The 41-turn review test uses three extraction chunks once, interrupts the second summary chunk, resumes through bounded consolidation, counts six summary attempts including uncertain billing, persists usage, and retains partial coverage.

`pip check` found no broken requirements. The project wheel built successfully (8,878,240 bytes at that checkpoint). A fresh wheel after the first correction round also built (8,882,276 bytes), with all four F06 fixture files verified inside. No optional generative local LLM is installed.

## Fixed local questions

`assets/f06/questions.json` contains 40 predeclared fictional questions, including more than ten paraphrases/follow-ups. Expected facts and source identities are seeded independently of answers.

| Retrieval | All cases | Answerable | Recall@4 | Question-set p95 |
|---|---:|---:|---:|---:|
| Lexical | 35/40 | 18/23 | 0.7826 | 1.196 ms |
| Existing BGE-small | 40/40 | 23/23 | 1.0000 | 71.824 ms |

All 17 uncertainty/safety cases and returned citations passed. Lexical misses Q03/Q05/Q12/Q16/Q20 were recovered by BGE. A 100-memory corpus exposed unrelated semantic neighbors being presented as appointment alternatives: Ask now prioritizes exact subject matches, using semantic-only matches as fallback. Regression coverage preserves ambiguity between multiple exact appointments.

Reproduce: `.venv\Scripts\python.exe -m conversation_copilot.f06_evaluation --output build/f06-local-third-corrections.json`.

## Controlled models and spending

Prices were reverified on 2026-09-08 using the [official Luna page](https://developers.openai.com/api/docs/models/gpt-5.6-luna) and [OpenAI pricing announcement](https://openai.com/index/advancing-the-price-performance-frontier-with-gpt-5-6/): Luna $0.20 input/$1.20 output and Terra $2/$12 per million tokens, matching configured rates. Conservative cache-write reservations remain in force.

Initial requests received `credit_balance_exhausted`; the final unbilled ledger returned to zero. The user paused work, later authorized a tiny credit probe (9 input/5 output tokens, $0.0000078), then explicitly resumed implementation.

**Aggregate recorded F06 API spending: $0.03636400**, including that probe, uncertain failures and correction reruns. The $2 aggregate cap is persisted before evaluation dispatch in `build/f06-paid-spend.json`. Credit/authentication exhaustion stops the evaluator. This is task API accounting, not shared-account total billing.

`assets/f06/quality.json` defines 12 guidance checkpoints and 8 summary scenarios: direct/uncertain plans, conflicting appointments, corrections, unspecified AM/PM/zone, topic changes, approved style, no inferred relationship preferences, injection, small talk and follow-ups.

- Initial Luna `none`: automatic checks passed, but output inspection found an invented user reaction in G11 and a placeholder in G02. Instructions were corrected; those original replies are not accepted as ready-to-say guidance.
- First corrected `none`: ten outputs passed the limited automatic word checks, but G02 still contained `[state the main steps]`; this was not a quality pass. G01 timed out (17.628 seconds including SDK overhead), and G05 received HTTP 520 (6.710 seconds). Explicit rechecks of both passed. All eight corrected summaries passed, with citation IDs validated against supplied turns before persistence.
- BGE plus explicit cloud Ask met all 40 authored fact/abstention requirements after a Q40 recheck. Q40 initially returned `unavailable` rather than `no_match`, but correctly abstained on a missing venue with a valid citation; both are accepted abstention states. No-evidence/identity clarification remains local and is not sent simply to manufacture an API sample.
- Luna `low`: all 12 guidance cases passed. Successful-request p50/p95 were 4.531/5.341 seconds, versus corrected `none` 2.668/2.840 seconds before the two rechecks. Initial `none` was 2.729/3.589 seconds. These small samples describe successful requests; the two failures remain separately reported and charged.
- Earlier review checkpoint (superseded by the final 3.486/4.865/5.078-second paid run and offline guard replay below): all 12 fresh `none` cases passed automatic checks and output inspection found no placeholders (p50/p95/max 2.994/3.898/7.347 seconds). A deterministic candidate guard now drops bracket/angle placeholders without discarding valid companion candidates. G11 acknowledges the user's explicit question about whether the joke was serious; G12's neutral wording is weak and remains a manual-usefulness question. Selected combined guidance profile: **Luna `none`**, with lower measured latency than `low`; this is bounded fixture evidence, not proof of general conversational quality. Summary and explicit Ask also use `none`. No automatic Terra escalation or additional local LLM was added.

Raw fictional results: `build/f06-controlled-model-funded.json`, `build/f06-controlled-model-corrected.json`, `build/f06-guidance-low.json`, `build/f06-transient-rechecks.json`, `build/f06-guidance-review-corrections.json`. `--cloud` explicitly enables paid evaluation; `--ids` limits correction reruns. Preserve the spend ledger.

## Resources and installation

`f06_resources` uses the unchanged basic synthetic fixture, cached production GPU transcription and CPU face processing. Ask uses CPU BGE with the existing two-thread setting and 100 real current memories/100 vectors. No personal database is opened or raw media produced.

| Measurement | Result |
|---|---:|
| Cold BGE startup | 944.134 ms |
| 100 warm Ask queries, half recorded-date filtered, p50/p95/max | 73.208 / 88.639 / 96.673 ms |
| 50 recorded-date queries alone, p50/p95/max | 86.548 / 88.791 / 96.673 ms |
| 100 concurrent mixed Ask queries, p50/p95/max | 83.500 / 117.630 / 131.039 ms |
| 50 concurrent recorded-date queries, p50/p95/max | 87.421 / 117.630 / 131.039 ms |
| 36 transcription turns without Ask, p50/p95/max | 217.899 / 274.932 / 310.025 ms |
| Same 36 turns with Ask, p50/p95/max | 216.821 / 280.477 / 285.225 ms |
| Transcription p95 regression | **2.017%** |
| Attributed decoded text / completed turns | Identical; 36/36 in both runs |
| Video p95 without / with Ask | 13.084 / 17.472 ms |
| Ask-only peak working set / private bytes | 271,863,808 / 1,011,322,880 |
| Full replay peak working set / peak private-pagefile allocation | 2,068,762,624 / 4,748,587,008 |
| Expanded existing development venv | 2,680,825,531 bytes |
| BGE cache | 67,181,383 bytes |
| Selected cached production transcription model | 1,621,665,983 bytes |
| Fresh normal dependency resolution, 71 wheel downloads | 1,548,941,074 bytes |

Summed process CPU p50/p95: Ask alone 140.625/187.5 ms; concurrent 218.75/343.75 ms. Concurrent samples include transcription/video threads. The wheel manifest comes from a fresh normal-install dry run plus exact wheel Content-Length values; its transitive versions can differ from the measured existing venv. Download sizes exclude Python, OS/GPU drivers, project source and model caches. They are not runtime-memory measurements.

The only new dependency is PSF `tzdata==2026.3` (348.2 kB wheel): Windows lacked IANA data for stdlib `zoneinfo`; installed dateutil bundled older 2024a data. IANA zones use ZoneInfo; Windows native names use OS historical conversion only when they identify the current machine zone. Naive imported wall times use that recorded zone. Unknown/transferred native zones remain unresolved; UTC capture timestamps are never blindly treated as local time. Explicit complete event dates do not require a resolvable zone. [Package source](https://pypi.org/project/tzdata/).

Reproduce: `.venv\Scripts\python.exe -m conversation_copilot.f06_resources --output build/f06-resources-review-corrections.json`. This cached-model replay does not prove physical capture or a new minimum-PC specification. UI scheduling tests and the manual call cover different surfaces. No BGE summary vectors were added because the fixed baseline did not establish a need.

## Limits and remaining gates

Shared-turn overlap deliberately over-links summary dependencies: deletion can exclude extra content rather than leak deleted text. Legacy missing deletion provenance quarantines that contact's pre-migration records until explicit per-turn source review; unselected and known-deleted turns remain excluded. Date-filtered Ask scans one contact before ranking; all-contact discovery stays bounded FTS paging. Dismiss uses normalized wording plus memory identity, including common clarification paraphrases, rather than suppressing an entire category. It is a bounded lexical approximation; semantically distant paraphrases can evade it and must be assessed during manual testing. Review and actual usefulness testing must assess these choices.

The basic fixture is synthetic with exact turns/separate stems; HeyGen has one animated narrator, static self-view, watermarks and an omitted opening line. Neither establishes genuine emotion or replaces the consenting live call. Accepted platform evidence and waivers are unchanged.

Next: tool-disabled/read-only **claude-opus-5** clean full-diff correction review with actual model verification; concrete manual script and actual outcomes; fresh final Opus 5 review; final privacy/dependency/diff audit; commit/push main and independently verify local/origin/GitHub SHA equality; only then mark F06 complete. No manual, review or release pass is implied.

## Preliminary review and corrections

Claude CLI 2.1.226 was invoked with exact `--model claude-opus-5`, `--tools ""`, disabled slash commands/hooks, an empty strict MCP configuration, and a full review packet supplied through a file on stdin. It returned **“Failed to authenticate: OAuth session expired and could not be refreshed”**. API duration and token usage were zero, `modelUsage` was empty, and cost was $0. No reviewer model ran; no fallback was attempted and no review pass is claimed. The user was asked to restore the separate Claude login with `claude auth login`.

The user restored Claude OAuth. The authenticated full-packet review returned findings: actual `modelUsage` contains only `claude-opus-5`, one turn, no tools, 346,505 cache-creation input tokens, 2 input tokens and 59,025 output tokens. The CLI reported a $4.940685 token-price equivalent under Claude Pro; this is separate from OpenAI task API accounting and is not a claim of an additional cash charge. No gate pass was claimed. The current [manual script](F06-MANUAL-TEST.md) remains a draft until clean correction review. Local evidence: `build/f06-preliminary-opus5.json`, `build/f06-preliminary-manifest.json`.

The manual import fixture was checked through the existing US-format export parser: six turns dated 2026-09-08. Its appointment uses explicit ISO 2026-09-10 to avoid numeric-date ambiguity. The parser's accepted format was preserved.


Correction disposition (first authenticated reviewer artifact: `build/f06-preliminary-opus5-authenticated.json`):

| Finding | Disposition |
|---|---|
| A1 cascade FTS retention | Rejected after reproduction: SQLite cascades fire the existing statement deletion trigger. Three regression cases approve/index then delete summary, conversation, or contact; each leaves zero FTS rows. No redundant deletion layer added. |
| A2 dates | Fixed at shared source-date conversion; native aware call timestamps, naive imports, explicit dates and unknown zones covered. |
| A3 interrupted edit | Running-only guard. Editing a pending draft finalizes its partial checkpoint while retaining usage and user provenance; later explicit regeneration starts a separate draft. |
| A4 empty record | Shared record listing now supplies created_at. |
| B1/B5 guidance | Per-candidate placeholder/malformed-evidence-count rejection; unsupplied IDs still fail closed. F06 schema-inclusive 3,000-token trimming and boundary check; optional modalities are recalibrated after trimming. |
| B2 dismissal | Category-wide suppression removed; distinct meanings survive. Lexical approximation disclosed above. |
| B3 merge | Safety review retained. Merge preview explains retrieval withholding; multi-select opens one combined source review. |
| B4 legacy review | Exact selected-turn release with generation/source checks; unselected legacy exclusions and all known deletion exclusions survive. |
| B6 personalization | Relevant approved preferences ranked; up to two reserved slots even when more exist, with a visible conflict-review notice. |
| B7 long memories | Shared source validation accepts a separate display ceiling; guidance liveness/evidence does not inherit Ask's 400-character answer bound. |
| C1/C2 SQLite | Review refresh always reschedules after lock errors; guidance evidence catches unavailable/busy reads. Reindex caches eligible turns per record, remains global across approved statements; per-record indexing/WAL deferred until measured need. |
| C3/C4 | Terra preflight includes reservations and $0.27 live ceiling. Withheld full-source extraction no longer prevents partial summaries of eligible turns. |
| C5/C6 | Common lowercase nouns do not override UI identity; explicit name/possessive checks remain. Retrieval ambiguity propagated. |
| D | Deleted-record proposal guard; empty category frames hidden; contact choices refreshed; worker event reset copied back; evaluator cache monkeypatch restored in finally; evaluation guidance uses its authorized evaluation ledger, not live sub-ceiling. |
| E | Corrected unsupported G02 quality claim and stale packet header. Resource rerun includes recorded-date queries. |

All 40 BGE fixed questions and 17 safety cases still pass after corrections; 235 whole-suite tests passed. Fresh controlled guidance added $0.00343820, for the recorded $0.02881530 total. The next clean correction review must inspect the full current diff and this disposition, not merely accept the table.


Second review and correction round:

`build/f06-correction-opus5.json` returned seven further items, not a clean verdict. Actual model again solely `claude-opus-5`: one turn, no tools, 380,445 cache-creation input tokens, 2 input tokens, 41,544 output tokens; CLI token-price equivalent $4.84306 under Claude Pro, separate from the unchanged OpenAI evaluation ledger. Review duration 530.377 seconds. Its references to “committed” regressions mean the supplied working files; no implementation commit has been made.

- M1: missing exact turn provenance now creates a reviewable legacy quarantine, rather than an irreversible known-turn exclusion. Explicit safe-turn review still cannot release known deleted-turn exclusions. Regression covers the empty-provenance deletion path.
- M2: one validation-pass cache shares record turns and eligible-turn sets across memory and summary sources, including their cloud eligibility checks. It never persists between passes. Ask result delivery still polls at 150 ms; idle displayed-source checks run once per second, and exact-source previews retain their 250 ms check. A 500-turn, four-source fixture measured 100 passes: p50/p95/max **2.730/2.849/8.368 ms**, exactly one whole-record load per pass, and deletion invalidated the next pass. Reproduce `measure_source_revalidation()` in `f06_resources`; raw result `build/f06-revalidation.json`.
- M3: recordless user-authored approval timestamps now convert from UTC to the machine's local historical date for Recorded date queries; midnight regression uses a real local offset.
- M4: Stop completion and Ask close resume semantic backfill. One pending flag retains a request while a call/panel or current backfill is busy; the existing poll starts it when eligible. Isolated Tk coverage verifies backfill resumes on panel close.
- M5: visible guidance groups are repacked in fixed Reply, Remember, Follow up order after hiding empty groups.
- M6: coordinator signatures still include refreshed guidance evidence; the tone/cue stable card compares only its original status/tones/cues triple. Renewed guidance no longer restarts unchanged tone stability.
- M7: follow-up resolution uses the explicitly chosen event, not prior generated answers or automatic inference from stored questions. Questions/exchanges remain bounded temporary panel state, but question history is not sent to cloud or used as retrieval evidence. Without an event, ambiguous short follow-ups ask the user to choose one. This conservative limit is disclosed in the manual script.
- Smaller items: ambiguity wording now distinguishes withheld facts from supplied approved styles; the multiple-preference notice requests review rather than claiming actual conflict detection. Bulk memory confirmation uses one transaction and one summary reindex, with rollback regression. The shared named live ceiling is used by reservation and Terra preflight. Guidance max latency is now reported alongside p95.

The second-round whole suite passed **235 tests in 18.78 seconds** and BGE fixed questions remained **40/40**, lexical **35/40**. No extra paid model requests were needed for these store/UI corrections. Another full-diff Opus 5 correction review is required before handoff.


Third review and corrections:

`build/f06-second-correction-opus5.json` returned R1–R3, not a clean verdict. Actual model solely `claude-opus-5`: one turn, no tools; 387,532 cache-creation / 4,112 cache-read / 2 input / 35,768 output tokens, 446.735 seconds, $4.771586 CLI token-price equivalent under Claude Pro. `build/f06-review-metadata.json` maps each raw CLI JSON to verified metadata; each corresponding `*-findings.md` is its extracted result text included in the review packet. These are paired artifacts, not conflicting filenames.

- R1: the combined path now calls the unchanged F04 `_cautious_policy` and uses its result as the authoritative tone/cue result. No remote speech returns locally with no cloud call. With remote words available, the same bounded combined request may still provide factual replies/questions while local tone/cue abstention is preserved. **The suggested blanket removal of candidates on every tone abstention was not adopted**: the approved plan explicitly requires preserving useful word-supported replies despite tone uncertainty. Three fake-client regressions cover conflicting reassurance/boundary, possible sarcasm without vocal evidence, and withdrawal without visual evidence; each retains a question and exactly preserves the local policy. The no-remote regression asserts zero dispatches. Controlled G03 now abstains about tone instead of returning a discomfort cue.
- R2: manual intent travels with the guided result through coordinator and display. Explicit duplicates are delivered, dismissed suggestions may be requested again, and manual refresh bypasses the automatic 12-second display floor and renews its timers. Automatic duplicate/stability handling stays intact; tone stability still uses only the base signature. Regression covers both coordinator delivery and immediate visible replacement.
- R3: record-linked revision creation reindexes approved summaries after relinking in the same transaction. No-op sensitivity updates are guarded. A summary approved before a later sensitive proposal remains indexed and reachable locally after approval, with cloud permission still blocked.
- Lower-severity corrections: one worker-store connection is shared by the guidance request's current-source checks. Only one review dialog per record is retained; repeated opens focus it, and destruction removes the entry. The isolated Tk regression exercises repeated opens. Ask intentionally inherits the existing conservative bereavement restriction: semantic-only loss memories can be withheld; a direct subject query/source selection is required. This is now disclosed rather than silently claiming universal semantic recall.

Two additional 12-case paid guidance runs cost $0.00754870 combined. The first (`build/f06-guidance-policy-corrections.json`) exposed G07's unsupported “four PM works for me” despite automatic word checks. The final guard conservatively drops recognizable first-person commitments/reactions unless the whole wording is present in the user's recent speech, including negative future commitments. It supplements the model instructions; it is a lexical safety check, not a general semantic proof. The final paid run (`build/f06-guidance-commitment-corrections.json`) had p50/p95/max **3.486/4.865/5.078 seconds**. G03's negative-future wording was subsequently removed by the guard; all 12 paid outputs were replayed offline through the final code without additional API requests (`build/f06-guidance-final-guard-replay.json`), leaving candidates in ten cases and none in two. G12 remains awkward in this run and must be graded for usefulness by the user. No claim of universal naturalness is made.

Third-correction checkpoint whole suite: **242 passed in 19.22 seconds**. BGE fixed questions **40/40**, lexical **35/40**. A transparent isolated Tk layout smoke also opened the empty-record chooser and verified **all 11 review controls are mapped and fit the default dialog** (`build/f06-review-layout.json`); this is agent evidence, not the user's manual outcome. Another full-diff correction review remains required before manual handoff.


Fourth review attempt — session allowance exhausted:

The exact `claude-opus-5` correction attempt returned HTTP 429 before model execution: “You've hit your session limit · resets 7:20pm (Asia/Jerusalem)”. API duration and all token counts were zero, `modelUsage` was empty, and cost was zero. No clean review was obtained and no fallback model or separately billed provider was used. Raw response: `build/f06-third-correction-opus5.json`; frozen full packet and manifest: `build/f06-third-correction-review.txt` / `build/f06-third-correction-manifest.json`. After allowance resets, regenerate the packet to include this documentation checkpoint, retry the same exact-model/tool-disabled review, and verify actual model metadata. The manual script remains a draft until that gate is clean. No implementation commit/push has been made.


## Fourth review corrections (F1-F5), September 8 evening

The quota retry completed: raw `build/f06-third-correction-retry-opus5.json`, extracted `build/f06-third-correction-findings.md`. Actual metadata contains only `claude-opus-5`, firstParty, one tool-disabled turn, 534,941 ms. CLI token-price equivalent $5.233755 under Claude Pro; this is not OpenAI project API spending or a claim of an additional cash charge. The earlier zero-token quota failure remains historical evidence.

- F1: shared structured request releases a reservation if pre-dispatch source validation raises, before any API call. A simulated SQLite lock verifies zero committed/spent dollars.
- F2: `validate_sources` propagates SQLite errors. Ask retains and retries a pending result while busy, distinguishes changed evidence, and retries idle checks. Exact previews temporarily show busy and retry, restoring evidence after validation rather than falsely claiming deletion. UI regression injects busy validation before answer delivery.
- F3: reuse F05's explicit topic-boundary vocabulary; ordinary Actually/No/Instead openers do not reset guidance. Explicit Correction/Make that clears unsupported candidates while retaining dismissed fingerprints. Source/topic invalidation now produces a stale coordinator event rather than a cloud-failure banner. Topic reset and stale-event regressions added.
- F4: deletion's evidence-based statement purge is restricted to exclusions from that memory's lifecycle id. Cross-contact regression preserves a user-corrected, releasable quarantined summary and verifies explicit source review restores eligibility.
- F5: fake post-call job pauses after its first checkpoint and resumes without repeating extraction; isolated real Tk Ask callbacks cover outside/in-call ledger selection and capture attribution before a simulated Stop. Topic reset coverage is included with F3.
- Moderate corrections: trim oldest vocal/visual observations first; recalculate usable vocal/visual modality predicates using F04 criteria; do not overwrite the already-running review notice with a false preparing message; allow a newer-turn retrieval to receive a fresh snapshot id after Suggest now instead of discarding it solely due to the manual request's id.
- Explicit product limits: the top two approved communication-style preferences may be supplied even without a topical retrieval match (ranked matches first). Sensitive approved memory can appear locally in Possible remembered context and Remember; cloud payloads still filter permission independently. Manual evaluation must judge these choices deliberately.

Latest final paid guidance latency remains p50/p95/max 3.486/4.865/5.078 seconds; the final candidate guards were then replayed offline, not newly timed online. No additional paid OpenAI calls were made for this correction round. The isolated 11-control layout artifact is included in the next review packet. Packaging smoke before this fourth set of fixes was successful (`build/f06-current-package.json`); it is not a final release artifact.

Fourth-correction verification (September 9 local): **246 passed in 23.56 seconds**, `git diff --check` clean. All 12 stored guidance outputs revalidated offline, 10 retaining candidates and 2 abstaining; aggregate paid OpenAI ledger unchanged at $0.036364. Clean Opus 5 correction review is still required.


## Fifth review follow-through (September 9)

Verified only `claude-opus-5`, firstParty, one tool-disabled turn, 364,693 ms: `build/f06-fourth-correction-opus5.json`, extracted `build/f06-fourth-correction-findings.md`. Verdict: no blocking findings; remaining non-blocking corrections/disclosures handled below. CLI token-price equivalent $4.995701 under Claude Pro, separate from the unchanged OpenAI evaluation ledger.

1. Cloud Ask now requires the entry question to match the last local exchange before offering its estimate. UI regression types a different question and proves zero dispatch, then restores the locally answered question and checks both ledgers across Stop.
2. Retained deliberate limit: local and cloud context share four live retrieval slots. Sensitive local-only memories can displace cloud-eligible results; cloud gets fewer rows after filtering. Avoid a second retrieval pipeline absent manual evidence this harms usefulness. Cloud permission remains enforced at all existing boundaries.
3. Manual script now explicitly asks about acknowledgment coverage: first-person commitments/reactions are conservatively withheld unless their full wording is already supported by the user's recent speech. This can leave no reply candidate; do not silently loosen this guard.
4. README now distinguishes contact-confirmed Luna none from the no-contact low path. Current headline test evidence is reconciled; the 242-test figure is explicitly historical. Tk coverage description is expanded.
5. Shared review reload and affected delete/evidence/merged-memory-review callbacks now catch unavailable/busy sources. A deleted record is checked before converting its row. Permission errors include SQLite failures. No schema or retrieval change.
6. Regression verifies pending repeated manual requests coalesce into the latest one; expanding More reveals the prepared third candidate without another interpretation dispatch.

Local replay after the fourth fixes: BGE 40/40, p95 81.5773 ms; lexical 35/40, p95 1.3074 ms, same five paraphrase misses (`build/f06-local-fourth-corrections.json`). No new paid OpenAI requests. Fresh correction review remains pending before manual handoff.

Fifth-correction whole-suite verification: **247 passed in 19.58 seconds**; `git diff --check` passed.

Sixth review attempt blocked before execution: `build/f06-fifth-correction-opus5.json` returned HTTP 429, all tokens zero, empty modelUsage, zero CLI cost, reset 04:10 Asia/Jerusalem September 9. Frozen packet/manifest: `build/f06-fifth-correction-review.txt` / `build/f06-fifth-correction-manifest.json`. No fallback model used. The prior completed review found no blockers, but verification of its final fixes and a clean preliminary gate remain pending; manual tests have not been handed off.


## Sixth completed review and final small callback fixes

The retry completed with only `claude-opus-5` in metadata, firstParty, one tool-disabled turn, 440,208 ms. Raw `build/f06-fifth-correction-retry-opus5.json`, extracted `build/f06-fifth-correction-findings.md`; CLI token-price equivalent $5.262120 under Claude Pro, not OpenAI evaluation spending. Verdict: clean preliminary gate with two non-blocking corrections.

A: ordinary Ask resets discovery offset; only Next discovery page preserves it. Real Tk regression advances to offset 12, changes the question, and verifies offset 0 plus the expected source id.
B: Ask contact loading, discovery event contact refresh, review record listing and memory-proposal opening catch unavailable/busy store errors and show status. Ask loads contacts before creating its dialog, so failure leaves no incomplete window.

Current affected-suite rerun: **38 F06 tests passed in 7.35 seconds**; `git diff --check` passed. Most recent whole suite remains **247 passed in 19.58 seconds**, before these final UI-only changes. Full correction review is being rechecked. No additional OpenAI requests. Package build before this last UI patch succeeded (8,884,851 bytes; 25 source/fixture files matched); artifact `build/f06-final-corrections-package.json` is a checkpoint, not a final release.

Non-blocking observations retained for manual grading: zero-turn reviews honestly report no attributed text; guidance rebuilding can move keyboard focus. Ask uses audio-session liveness for ledger selection, so a video-only session after audio startup failure uses the outside-call allowance; this bounded fallback is not a second call allowance reset. No expanded video-only support claim is made.


## Clean preliminary gate and manual handoff — September 9

Raw `build/f06-sixth-correction-opus5.json`; extracted `build/f06-sixth-correction-findings.md`; frozen full packet and manifest `build/f06-sixth-correction-review.txt` / `build/f06-sixth-correction-manifest.json`. Metadata verifies only `claude-opus-5`, firstParty, one tool-disabled read-only turn, 311,047 ms, no tool use. CLI token-price equivalent $5.035411 under Claude Pro; OpenAI evaluation ledger remains $0.036364. Verdict: **clean preliminary gate, no material correctness/privacy/lifecycle/data-loss/budget/UI finding remains open**.

Completed the reviewer's pre-handoff process item: full offline suite **247 passed in 24.07 seconds** on the exact reviewed code. Frozen file hashes matched before recording this handoff, except the metadata file just updated to record the completed review; no application code changed after review. `git diff --check` passes.

Three expressly non-blocking observations retained for final audit/manual feedback: continuation estimate labels total chunks alongside a conservative remaining-work maximum and does not separately estimate expected cost; pressing Next discovery page with an invalid question can advance its offset until the next ordinary query resets it; an F05 Manage memory window opened from review can remain partially built after a busy read, although the surrounding callback reports the error. These do not invalidate the clean preliminary result. Use actual user outcomes and the required fresh final review to close the remaining audit.

Manual script is handed off in `docs/F06-MANUAL-TEST.md`. **No user result has been received or counted as a pass.** User must report actual outcomes before the fresh final Opus 5 review. No implementation commit/push or F06 completion claim.


## User-requested scrolling during manual testing

User requested a scrollable app window. The main controls now use a standard Tk canvas with vertical/horizontal scrollbars, wheel/Shift-wheel scrolling, Page Up/Down on the canvas, and automatic reveal when keyboard focus moves to a control. Transcript remains beside the controls; text/list/selector widgets retain their own wheel behavior. Isolated Tk integration verifies overflowing content can scroll and existing Ask/review flows still pass (1 passed in 5.95 seconds); `git diff --check` passed. This change follows the clean preliminary review and must be included in the fresh final review. User scroll/usability confirmation and remaining manual results are pending. Running app needs reopening to load the code.


## User feedback: reply direction, Terra experiment and linked review

Observed user report: suggestions answered the user's questions rather than responding to the contact. User also requested persistent summary loading, prose paragraphs, memories visible beside the summary, two-way linked edits, and then explicitly requested joint approval of the summary's linked pending memories.

Implemented: payload names the latest contact reply target; Reply/Follow up require its source ID and are suppressed when the user speaks last. User turns remain context/style, exact repeated wording is filtered, and older in-flight snapshots are rejected on newer speech. Live interpretation/guidance now explicitly requests Terra low; summary/Ask remain Luna none and all prior dollar caps remain enforced.

Review reuses source-linked summary sentences as readable paragraphs and shows this record's pending/approved memories in the same window. Loading persists through extraction/chunks/consolidation; paused/failed jobs report pending rather than falsely completing. Bidirectional selected edits reuse current revision/source eligibility and are atomic via nested SQLite savepoints. Shared-turn dependencies can link multiple facts: explicit per-item selection prevents blindly replacing all of them. User-corrected pending text retains that provenance on approval; normalized date metadata is cleared when free-text edits cannot safely update it. Joint summary approval verifies the displayed proposal set/content and summary content, approves only linked pending proposals, and rolls back everything if any approval fails. Rejected/excluded/unrelated proposals stay unchanged.

New regression coverage: contact-versus-user target and explicit Terra-low dispatch; pending/approved two-way edits and stale-edit rollback; joint-approval rollback and unrelated pending preservation; real isolated Tk paragraph/memory visibility and loading-to-complete transition. Existing UI test also retains scrolling and Ask lifecycle coverage. Earlier separate-approval tests/instructions were updated to the user's newer explicit joint-approval instruction.

Controlled fictional checks: Terra low G01/G02/G07 completed, with measured requests 6.481/4.453/4.289 seconds; one retained no reply candidate. Luna-none S01/S02 prose summaries completed with supported appointment wording and an explicitly unagreed plan, 4.362/2.348 seconds. These small samples are not a claim that Terra is generally better. Artifacts: `build/f06-terra-low-user-feedback.json`, `build/f06-paragraph-summary-user-feedback.json`. Recorded aggregate OpenAI evaluation spend **$0.0515957**, including earlier work, below the authorized $2 cap. Minor final prompt wording/source-name additions and exact-repeat filtering followed these samples and are covered by offline tests.

Fresh final Opus 5 review must include these user-driven changes; the earlier clean review does not cover them. Actual user recheck outcomes are pending. Restart the app and explicitly regenerate a summary to load the new behavior; no active call was terminated automatically.

Final user-feedback implementation check: **250 passed in 22.46 seconds**, `git diff --check` passed. No code changed after this run. User rechecks and fresh final review pending.


### Final Terra-low controlled test requested September 9

Current-code fictional guidance cases G01-G12: 12/12 bounded automatic checks passed; 12 paid gpt-5.6-terra requests with reasoning=low. Report: `build/f06-terra-low-final-test.json`, including captured UsageRecord values. Test token-price estimate: $0.034485; persisted aggregate F06 evaluation spend: $0.0860807, below the unchanged $2 cap. No application code changed for measurement.

Usage: 16,646 input tokens (13,120 cached reads; 3,490 cache-write tokens), 1,922 output tokens; API reported zero reasoning tokens. Median latency 3.621 seconds, maximum 6.874 seconds. Ten cases retained replies; G01/G04 abstained. Inspected candidates target the contact's latest turn. Some reply/follow-up suggestions duplicate each other (G08-G10); fixture success is not a live usability pass or a guarantee of personal style matching.

Five-minute estimate assumes about 25 automatic requests at the existing 12-second minimum cadence: measured fixture average extrapolates to $0.07184375 live; same token lengths with all input charged as fresh cache writes gives $0.134748. At 3,000 input tokens per request, all fresh cache writes and the observed mean output length, the estimate is $0.235550. Allowing roughly $0.01-$0.04 for a short Luna summary/extraction gives a practical planning range around $0.10-$0.30 total, dependent on transcript size/chunk count and cache reuse. This is a token-based scenario estimate, not a measured five-minute call or a billing-dashboard charge. Local transcription adds no API fee. Extra manual requests are excluded. Existing live ceiling $0.27 and full-call cap $0.35 remain; paid work stops if the next reservation cannot fit. Post-call reserve $0.08 is an allowance, not a fixed charge.

Prices verified against the official Terra model page (https://developers.openai.com/api/docs/models/gpt-5.6-terra) and OpenAI July 30 price update: $2/M input, $0.20/M cached reads, $12/M output; existing accounting applies 1.25x input to cache writes. User manual rechecks and fresh final Opus review remain pending.


### User-requested implied mentions, media and progressive feeding rechecks — September 9

Live profile remains Terra low. Full current offline suite: **250 passed in 22.19s**; machine-readable report `build/f06-user-requested-replays.xml`. Coverage includes 13 memory-call scenarios (progressive indirect employment/happy-event/grief cues, vague prompts, user-only cues, wrong contacts, dates, topic changes and longitudinal corrections); 3 basic/HeyGen media fixture checks; 49 audio tests; 9 video tests; 19 interpretation coordinator tests; and F06 guidance, review, budget and real isolated Tk UI checks. Progressive transcript feeding exercises authored video checkpoints, multiple calls, request construction, memory retrieval, display stability, cadence and stale-result handling. These deterministic tests use controlled semantic vectors/model responses in places: they do not constitute a fresh online Terra video evaluation or physical call test.

Real local BGE evaluation: **40/40**, p95 **75.159 ms** (`build/f06-user-requested-local.json`). Lexical-only baseline remains 35/40 with the same five paraphrase misses (Q03/Q05/Q12/Q16/Q20); no new failure in the selected embedding path.

Cached production GPU transcription + actual CPU face processing + concurrent CPU BGE queries were replayed twice. Each run completed 36 baseline and 36 concurrent transcriptions, with identical attributed text and no worker errors. Both used 100 stored memories and 100 vectors. First run: baseline/concurrent transcription p95 269.889/304.977 ms (**13.001% slowdown**, above the 10% target); repeat: 284.897 ms baseline and **6.261% slowdown**, below target. Concurrent Ask p95 91.912/90.242 ms. Peak process working set about 2.07 GB. Source revalidation retained one whole-record load per pass and invalidated deleted sources on the next pass. Artifacts: `build/f06-user-requested-resources.json` and `build/f06-user-requested-resources-repeat.json`.

Functional replays passed. Concurrency performance is variable across the two samples and is **not recorded as a consistently passing <=10% gate**; retain this open performance observation for the final audit. No application code or model settings changed, no new downloads or API requests, and the paid ledger remains $0.0860807. The existing 12-case Terra-low controlled result remains the latest paid quality sample. User explicitly deferred hands-on testing; physical capture, live usefulness and fresh final Opus review remain pending.


### Real-model paced transcript test — September 9

See `docs/F06-LIVE-FEED-REPORT.md` for the full expected-versus-actual timeline. Seventeen paced finalized turns, nine actual Terra-low checks and actual Luna extraction/summary. **Not an all-pass:** implied context was missed, tone/cue analysis persisted across a topic change, and a proposed memory strengthened loss into death. Smaller prose/duplicate issues recorded. Corrected run $0.04146608; including superseded harness run $0.09823428; aggregate $0.18431498. Earlier premature-Pepper finding from the superseded harness is not attributed to the real app. Service-level replay, no GUI/capture pass. No application fixes made in this testing turn.


### Implicit-reference fix and replay

The personal-loss classifier now recognizes the observed “lost her dog” wording without interpreting it as death. Inferred matches carry a possible-loss-reference marker used by guidance to offer tentative reminders/clarification. The shared topic matcher recognizes “Changing the subject.” Three local experiment variants and the full real Terra-low replay are documented in `docs/F06-LIVE-FEED-REPORT.md`. Turn 4 now produces “Possibly related: Maya lost her dog Pepper…” and “Is this possibly about Pepper?”; topic transition clears the reminder. 251 tests passed (23.20s); BGE 40/40. New run $0.0519956; aggregate $0.23631058. Earlier stale-analysis, extraction-strengthening and summary-markup findings remain open.


### Five varied fresh memories: real BGE + Terra low

`docs/F06-VARIED-MEMORY-REPORT.md` records five new-memory scenarios (McDonald's layoff, loved-one death, photography prize, voluntary resignation/relief, exam stress). Fifteen actual paid checkpoints: target retrieved 10/10 indirect clues, model reminder 9/10, all five topics eventually successful; all five topic transitions cleared context. First resignation clue falsely ambiguous due to exam distractor. Two vague openings retrieved an exam memory from “week”; local-only checkpoints, not model-tested. Separate real-BGE two-loved-one ambiguity check passed. No per-topic retrieval rules added. Guidance prompt now favors natural support instead of identity confirmation. Twenty relevant offline tests passed (1.46s). Paid test $0.0741396; aggregate $0.31045018. Raw `build/f06-implicit-variety-results.json`. Existing post-call findings and manual/final-review gates remain pending.


### September 12 real-call feedback corrections

Opt-in private log under `build/current-live-test.json` confirmed 9/10 guidance attempts discarded on ordinary new speech; the first model request was already about 13 seconds into the call. Ordinary new speech now suppresses outdated ready replies while preserving recent analysis; contact/generation/topic/correction/source invalidation remains. First automatic dispatch is gated at 12 seconds with one finalized turn sufficient. Cloud-eligible memory candidates are shown only when selected by model Remember; existing retention unchanged, private local context requires nonambiguous lexical support. Generic question narration was in the summary rather than extracted memories; both prompts now omit it and summary prompt prohibits inline source markup. Tone prompt prefers two supported hypotheses and local positive-rule matches allow a second calibrated model tone, while hard abstention/conflict gates remain. No guarantee of two unsupported labels: final controlled project case returned one, explicit two-tone case returned two.

254 tests passed in 23.91s. Controlled artifacts `build/f06-live-feedback-check.json`, `build/f06-live-feedback-two-tones-final.json`; actual extraction enabled for the fictional review cases. Generic-only summary empty; substantive project answer retained. New test estimate $0.02029010; aggregate F06 evaluation $0.33074028. Private call log review kept in its build directory, not copied into source docs. Existing running app requires restart; changes have not yet been verified in another physical call. Final Opus review remains pending.


### Current-code lost-job walkthrough

`docs/F06-LOST-JOB-WALKTHROUGH.md` shows the complete eight-turn transcript and four actual Terra-low outputs. First dispatch 12s, no vague-opening memory; indirect job-loss/rent clue at 24s selected the McDonald's reminder at 28.88s while exam/quitting distractors stayed hidden. Stronger clue retained it. Book topic at 48s stopped selecting it; existing 24s context retention cleared at 70.14s. Two tone hypotheses at stronger clue, one at vague opening. Serialized paced service replay, not physical capture or full GUI/coordinator concurrency; late-response speech delivery explicitly disclosed. Cost $0.0262108; aggregate $0.35695108. No application changes in this test.


### Vague lost-job clues with concurrent four-second feed

`docs/F06-VAGUE-JOB-4S.md` records ten turns, real BGE and three real Terra-low calls through the production coordinator. No explicit firing wording: stress, rent, long tenure and future uncertainty. Feed timing error <=0.015s, independent of API calls. Rent cue retrieved the layoff memory at 12s; first response selected only that reminder at 20.047s. Stored memory includes rent, so shared lexical detail helped. Raw supportive replies were removed because newer speech arrived; this remaining responsiveness limitation is explicit. A user-last snapshot returned no reply; topic-change snapshot removed memory candidates. No exact UI retention-expiry claim. Cost $0.0196996; aggregate $0.37665068. No application edits.

### Adaptive analysis cadence

Live app scheduling now estimates finalized-turn arrival spacing with a 50/50 moving average, targets three turns per request and clamps the interval to 10–15 seconds. Initial spacing estimate is four seconds. First automatic dispatch remains at 12 seconds; existing single-flight, latest-pending, manual bypass and budget checks remain. Duplicate offers do not change the estimate, silence alone does not request analysis, and session reset clears the rate estimate. Explicit fixed-cadence coordinator callers remain supported. Turn size is not modeled; this is a pacing heuristic, not an estimate of transcription latency. New speech can still suppress ready replies while inference runs; this change does not resolve that limitation. No paid model calls for this scheduler change. Focused checks: 31 passed, including fast (10s), steady (12s), slow (15s), duplicate-offer and silence cases. Physical-call verification and final review remain pending.

Full offline suite after cadence change: 257 passed in 23.12s. No additional API spend.

### September 13 dynamic-cadence actual API audit and context comparison

47 real Terra-low API calls across 12 wall-clock-paced transcript scenarios, including the recorded call, prior varied/implicit cases, two-loss ambiguity and normalized-date recency, plus 24 actual API context ablation calls (two trials per arm). All 71 requests have saved exact inputs, outputs and assistant judgments. New estimate $0.330444; persisted aggregate $0.70709468. User authorized a one-time $4 evaluation allowance, unused; normal application budgets unchanged. Full private artifacts: build/dynamic-api-audit-20260913/findings.md, report.md, context-comparison.md and raw JSON files.

Observed issues: stale/past tone across topic changes, generic-stress false-positive memories, question repetition, cue-label/evidence mismatch, unstable upstream ambiguity and new-speech reply suppression (12/27 validated reply batches). Two expected topic/correction invalidations, no API failures in this run. Feed error at most 0.033s. Late real-call context contains only 12 segments; full 30-segment prefix adds 322 actual input tokens and restores useful earlier detail. Longer/hand-selected history alone does not consistently improve current-tone relevance. Priority/clue instructions improve two bounded cases in two trials each; output variability remains. No application changes or post-call extraction in this audit. Physical manual verification and final review remain pending.


### September 13: 1,300-token context and six prompt variants

See `docs/F06-PROMPT-COMPARISON.md`. 120 real Terra-low checkpoint requests (six prompts × ten checkpoints × two trials), plus 96 real requests from six full recorded-call/service replays and twelve new fictional replays. All 216 requests have assistant assessments; five invalid empty/updated interpretations were rejected. Actual BGE retrieval, four-second fictional feeds, adaptive 10–15-second coordinator, max feed error <0.030s. Selected priority prompt improves current-topic focus and preserves more useful indirect memory cards than shorter variants, but repetition, retrieval ambiguity, weak labels and new-speech suppression remain. No post-call extraction or physical capture in this round.

F06 transcript budget is now 1,300 estimated tokens/180s, independent of instructions/schema, with a separate 4,500 estimated input ceiling. Old 16-segment truncation no longer binds before the token budget. App model remains Terra/low. 258 tests passed in 24.14s after selection. New estimate $0.99724010; recorded F06 aggregate $1.70433478. This round stayed below the user-authorized $4 ceiling; normal application budgets unchanged. No final review/commit/release yet.


### September 13: complete selected-prompt regression rerun

See `docs/F06-NEW-PROMPT-REGRESSION.md`. 159 fresh actual API calls (118 Terra/low, 41 Luna/none), every request assessed against its evidence. Replayed all 12 previous adaptive scenarios plus the two newer job variants, 20 repeated diagnostic checkpoints, original fixed/serialized scripts, controlled guidance/summary/Ask, and equivalent custom feedback checks. All 47 old adaptive prefixes matched. No application code changes or API transport/schema failures.

Results are mixed: stale negative tone after book-topic switch fell 9/10 to 0/10, but five-memory reminder selection fell 9/10 to 6/10 with unchanged 10/10 local target retrieval. Repeated project questions, weak tone/cue labels, upstream ambiguity and new-speech suppression remain. Raw invented Pepper death was filtered; a separate pending Luna meeting proposal invented an unstated event date. Generic-only review was empty; Pepper review retained corrections/preferences without inline source clutter. Controlled automatic checks 59/60, with Q10 a 3:00 PM versus 3 PM substring false negative; manual review found additional issues documented in the report.

Full local suite 258 passed in 25.18s; actual BGE Ask 40/40, lexical 35/40 unchanged. Both video fixtures replayed. Actual resource replay preserved all 36+36 transcription outputs, current p95 slowdown 8.42%, concurrent Ask p95 90.86ms; historical variability still prevents a consistently passing performance claim. New token-price estimate $0.47611090; persisted aggregate $2.18044568 within the authorized $4 cap. Normal application budgets unchanged. Private exact requests/raw outputs/assessments are under build/new-prompt-regression-20260913. Physical-call usefulness verification and fresh final review remain pending.


### September 13: memory-selection prompt blend and full comparison

See `docs/F06-MEMORY-PROMPT-BLEND.md`. One guidance prompt paragraph now combines discriminating factual clues across the ongoing topic and allows tentative approved-memory reminders without an exact name/event label. A more permissive first candidate was rejected after generic-stress false positives. Terra/low, 1,300-token transcript preparation, BGE, retrieval thresholds, cadence, retention, validation, and Luna review/Ask prompts remain unchanged.

Completed 271 actual API requests (112 paired candidate checks plus the same 159-request regression scope), all individually assessed with exact inputs/raw outputs retained. Useful reminders returned from 6/10 to 9/10 in the original five-memory sweep, with 10/10 local target retrieval and the early resignation ambiguity still withheld. Fresh final-candidate paired positive opportunities improved 9/16 to 16/16; transition/no-memory checkpoints are excluded. All ten matched book-topic negative-tone checks remain clear. An unrelated exam reminder in preference/scheduling context, boundary reminders, repeated questions and weak tone/evidence labels remain; no clean overall release-quality claim. The unstated pending meeting date was reproduced in unchanged Luna extraction.

258 automated tests passed in 23.32s, including existing video/transcript/UI fixtures. Controlled automatic checks passed 60/60, with qualitative limitations documented separately. One paced result was rejected for an intervening topic change; no API transport/schema errors. Cost estimates including cache writes reconcile to $0.92361810 for this round and $3.10406378 aggregate, below the authorized $4 cap. All paid harnesses finished. No physical microphone/WhatsApp usability pass, new resource benchmark, final Opus review, commit, or release in this round. The revised prompt is retained for experimentation.
