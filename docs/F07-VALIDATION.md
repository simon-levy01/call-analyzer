# F07 validation

**September 21 current disposition:** The user accepts current main as a limited F07 checkpoint and moves on. [Closeout](F07-CLOSEOUT-20260921.md) records retained code, rejected experiment, known failures and deferred gates. This supersedes historical active/release-pending status below; it does not convert any failed or unmeasured gate into a pass.

Additional local vision screening completed for six pipelines on DISFA development windows and two downloaded conversation clips. [RAM, latency, quality and limits](F07-VISION-SCREENING.md). No API spend or production change; original human, review and release gates remain pending.

## September 14 provisional comparison — before live testing

**Latest status supersedes the historical checkpoints below.** The user requested the evaluation now and again after human testing. The corrected run completed **144 independent Luna low API responses: 143 validated, one rejected**. This is the approved 72 matched visual + 24 unchanged-production + 48 semantic design, with two independent repeats per condition. No production code changed during this comparison. It is **not a release pass** or a substitute for the three consenting participant checks.

Private evidence: `build/f07-implementation-20260914/api-comparison-before-p1-v2/`. `jobs.json` freezes exact requests/schemas; `protocol.json` freezes source hashes, families and expectations; `report.json` preserves raw responses, validation, displayed candidates, usage and timing. `metrics.json` gives planned/dispatched/validated counts for each family group, arm and repeat. `compact-outputs.json` and `blinded-review.html` support later review; the separate mapping reveals conditions. **No user usefulness scores have been entered.** Output wording can reveal visual evidence, so the packet is not a fully blinded trial.

### Integrity and budget

The first comparison attempt had a fixture join error: JSON timestamps ended in `Z`, while dictionary keys used `+00:00`, so expression summaries disappeared. It was stopped after 13 validated responses and one interrupted dispatch; its full evidence and unresolved reservation remain under `api-comparison-before-p1/`. Those responses are excluded from the corrected comparison, not counted as independent repeats or silently refunded. The corrected preparation joins actual datetimes, raises on mismatched completed buckets, and checks that all 72 visual-arm instructions contain expression vocabulary and expression inputs differ from movement inputs.

The corrected run cost an estimated **$0.05875098**. Aggregate committed cost is **$0.07768505 / $0.30**, including earlier tuning and the interrupted attempt/reservation; **$0.22231495 remains**. The cap did **not** stop this evaluation. The earlier $0.13 reserve remains available for later work; the runner now permits explicitly reducing that reserve for the after-human run without resetting the aggregate ledger. Prices include reported cache reads/writes; these are estimates, not a provider invoice.

Only fictional text and bounded derived observations went to Luna. DISFA video stayed local, with exact frame/PTS checks and original archives preserved. The controlled expression arm combines **baseline completed movement buckets with candidate expression summaries**, keeping the movement prefix identical across arms. It does not measure candidate partial-bucket UI behavior. Dialogues are authored and paired with silent reactions, not genuine aligned speech; vocal alignment remains unknown. The provenance supplement verifies that the actual live-imported detector/ledger files matched frozen candidate hashes. The corrected future harness imports those modules from the frozen candidate directly.

### Measured comparisons

| Condition | Requests / validated | Estimated cost | Mean input tokens | Request wall-time p95 |
|---|---:|---:|---:|---:|
| No visual | 24 / 24 | $0.00817327 | 1,828.9 | 5.11s |
| Movement, common policy | 24 / 23 | $0.00982784 | 1,956.9 | 5.26s |
| Expressions, common policy | 24 / 24 | $0.01102785 | 2,023.9 | 5.98s |
| Visual unchanged production | 24 / 24 | $0.00999032 | 1,862.9 | 5.96s |
| Semantic unchanged production | 24 / 24 | $0.00960490 | 1,539.1 | 5.51s |
| Semantic candidate | 24 / 24 | $0.01012680 | 1,553.8 | 8.74s |

Expression input adds **67 tokens** versus movement and **161** versus unchanged production: below the unchanged **400-token allowance**. Its estimated actual cost increases **12.21% / 10.39%**, respectively, exceeding the separate **10% limit** in the visual comparisons. Cache-normalized increases are 6.83% / 8.31%; these do not erase the actual-cost result. Across all 48 matched candidate/production requests, added input is 87.83 tokens and cost increases 7.96% (normalized 5.18%). Report both workloads; do not use the combined result to hide the visual-only excess.

Wall times include local validation and evidence writes. Coarse provider timestamp p95 is 8s for semantic candidate responses; neither measure establishes actual UI or eligible-turn latency. The 6/7/20-second latency gates are not collectively passed. The rejected movement response (`visual-05`, repeat 2) returned `updated` with no tones/cues; its raw output is preserved and remains in the denominator. No transport retry replaced it.

### Technical findings, not human usefulness grades

- **Boundaries:** the candidate still labeled the practical oven-related call ending as withdrawal in **2/2**, versus production **1/2**. Explicit anxiety was retained in 2/2 on both versions. A privacy-only answer produced an unsupported uncertainty cue in candidate repeat 1. Narrow boundary calibration is incomplete.
- **Supplied memories:** both versions selected pottery and excluded swimming in 2/2. The candidate handled two possible fittings through clarification or low-confidence alternatives in 2/2. It used the tennis fact in a reply once and a Remember item once; production omitted it in both. Thus a missing Remember item is not automatically an omitted fact. The candidate also misread “right after my lesson” as a question ending in “right?” in one response. Every relevant memory was supplied in these requests: these are evidence-use findings, **not retrieval failures**. Retrieval recall remains unmeasured.
- **Attribution:** the reverted, unchanged extraction prompt still assigned the contact's ladder loan/return to “You” in candidate **2/2**, production **1/2**. Both versions expanded ambiguous “us” into the user and contact once. These high-confidence ownership claims block a clean safety result. Both preserved the unsigned-lease qualification and abstained on the garbled software winner in 2/2 each. Since extraction instructions are unchanged, differences between these small samples do not establish a causal regression or improvement.
- **Visual uplift:** smile observations sometimes added low-confidence warmth and sometimes changed nothing. No human-scored two-family uplift is established. Mouth-corner lowering was below threshold in every final expression summary; earlier poor recall is not resolved. Configuration precision/recall/coverage and exact onset/offset gates remain unpassed, not inferred from API output validity.

### Review and next gates

Actual **Claude Opus 5 only**, read-only with tools disabled, reviewed the new harness and then its corrections. `comparison-correction-review.json` cleared this **provisional before-P1 comparison**, with no remaining material blockers. It used the authenticated Claude Pro subscription, separate from the Luna API ledger. Current full suite: **279 passed in 25.00s**, `tests-comparison-reviewed.xml`; earlier failed and successful test/review evidence is retained. The original running harness, provenance supplement and corrected future harness are distinguished rather than rewriting frozen evidence.

One tuning round remains used; this comparison did not authorize a third round or silently alter the candidate. P1 development, any permitted second-round corrections, fresh applicable preliminary review, P2/P3 and the requested after-human comparison remain next. These 24 families have now been evaluated; using them to guide corrections makes them regression evidence. Repeating them cannot restore untouched holdout status; reserve fresh equivalents separately for any such claim. Twelve other DISFA subjects remain unprocessed, beyond the three development and twelve comparison subjects.

Keep all original 85% thresholds, other quality/resource gates, September 23 freeze, September 27 target/fallback and October 1 F08 Windows deadline. Human usefulness, matched resources, actual UI delivery and final post-human Opus review remain pending. **No final F07 commit/push or three-way main-match verification is claimed.**

## September 14 implementation / first tuning round

Working candidate implemented in the existing aggregator, video lifecycle, snapshot serializer and shared interpretation path. Three separate local configuration levels persist without movement; capture timestamps, gap resets, pending face-switch generation fencing and current/manual snapshots were added. Automatic requests still originate from finalized speech. Thresholds `.35/.30/.06` are an **unvalidated first candidate**, with low observation confidence; no emotion probability is claimed. No new dependency or video upload/retention path was added.

Private freeze and results: `build/f07-implementation-20260914/`. Unchanged production archive is Git `28e843f3e2efbfa5f494f8c40c759705e720bfe1`; separate candidate source, cases, baseline schemas/instructions, source bindings and approved protocol are retained. Eighteen tuning cases comprise six DISFA windows and twelve authored semantic cases. Twenty-four held-out families are reserved. DISFA/dialogue pairings are synthetic multimodal cases, not genuine aligned podcast speech; confound names do not prove the footage contains that confound. Actual source-derived held-out wire requests remain to be collected/frozen after candidate freeze. P1/P2/P3 identities, consent and outcomes remain pending.

The user explicitly selected **API / Luna low / $0.30 aggregate F07 cap**. First-round allocation is at most $0.075, leaving at least $0.225 reserved for later work. Real API baseline/candidate runs completed **24 responses**, one per tuning condition, for **$0.010754 estimated usage cost** total. These are not the final 144 comparisons or independent repeats. Exact requests, schemas, raw responses, validated guidance/proposals, timings and usage are retained under `api-baseline-round1-b/` and `api-candidate-round1/`. The initial baseline attempt failed before dispatch because its isolated source had no credential file; the runner now reads the original credential location without copying/logging it. No paid retry occurred. SDK serialization warnings are preserved; completed responses were validated. Current prices were verified against [OpenAI's Luna documentation](https://developers.openai.com/api/docs/models/gpt-5.6-luna).

Observed first-round limitations:

- Candidate boundary cases 1–3 abstained from emotional interpretation, and case 4 retained explicitly stated discomfort. Deterministic old elevated-motion/withdrawal behavior is removed. API boundary cases here have no visual evidence; they do not measure the visual arms.
- Both versions supplied both deposit/payday facts in replies but omitted a separate Remember item. Nursing reminder was selected and unrelated reminders suppressed. Retrieval was bypassed with eligible fictional candidates: this tests supplied-evidence use, **not retrieval recall**. No retrieval change was made.
- Candidate extraction case 9 attributed the contact's sketchbook to “your sketchbook”; this is an attribution regression. Case 12 also retained an unhelpful app-test non-event. The new extraction prompt **does not qualify for release** on this evidence. Candidate cooking reply also invented “I'm leaning toward” a food preference; user usefulness scoring remains pending.
- Saved-signal replay: smile 120 positive frames detected, 21 false-positive frames; brow 147 detected/35 missed, 2 false-positive frames; mouth corners **3 detected/39 missed**, no false-positive frames in these six windows. Weak intensity-1 frames are separate. These are frame diagnostics with a synthetic constant face box, not episode precision/recall or timing-gate passes. Mouth-corner performance is inadequate in this candidate. No held-out subject signals were inspected.

Automated evidence: initial affected 35 tests passed; after semantic changes 44 affected tests passed; four expression/lifecycle checks passed. Two complete-suite runs then crashed with Windows native exception `0x80000003` during GC in a coordinator worker. The isolated Tk integration test retained captured callbacks after destroying its root. Clearing those references and collecting cycles on the UI thread produced **275 passed twice**, in 24.03s and 24.88s (`tests-tk-cleanup.xml`, `tests-tk-confirm.xml`). Failed-run traces remain preserved. Two older token-bound fixtures were adjusted because the shorter boundary instructions changed their load; hard ceilings were not raised.

Semantic tuning timing/cost only: baseline p50/p95 3.38/7.80s, candidate 2.95/5.07s. Mean added input 26 tokens; actual estimated cost delta -3.49%; uncached normalized totals $0.0071464/$0.0069772. Cache usage is retained separately. These figures do not establish final visual-workload cost/token gates or actual UI delivery latency. Remaining aggregate authorization is $0.28924566, not a fresh cap.

### Verified preliminary review and corrections

The first tool-disabled read-only review completed with actual **`claude-opus-5`**, provider firstParty, no web searches; exact input/output are `review-input.txt`/`review.json`. This was the authenticated Claude subscription reviewer, separate from the Luna API ledger. Verdict: **not clear for human testing**. Six material findings covered absent configurations counted as evidence, uncertain samples destroying holds, one-sample offsets, broad boundary abstention, Continue tracking/cadence resets and the unversioned extraction prompt.

Corrections now under review: explicit below-threshold quality; pause observed duration through mouth/asymmetry uncertainty without extending gaps; retain completed offsets; filter only unsupported boundary-related cues while preserving other tones/context; Continue resets only local visual state and selection invalidation preserves paid cadence. Capture gaps compare capture times. Stale thumbnails disappear with stale signals. The failed extraction prompt was reverted to unchanged F06 wording, avoiding a prompt-version/resume migration. The API runner discovers prior spend/reservations and locks the shared allocation; its $0.075 limit intentionally covers tuning only, not final held-out execution. Seven focused checks now include uncertainty, offsets, capture age, selective cue filtering, cadence, alignment and ledger carry-forward; 49 affected tests pass. Two legacy regression assertions were updated to stop deriving expectations from the removed local override; an intermediate test edit left a dangling expectation reference, corrected and preserved in failed logs. The complete current suite is **278 passed in 24.25s** (`tests-reviewed-candidate.xml`). Fresh correction review pending.

Audio clock contract was traced: `audio.py` constructs turn drafts with `timestamp=job.started_utc`, and `_conversation_turn_from_audio` preserves that timestamp. Derived `bucket_alignment` is explicitly limited to the bucket, not the potentially longer expression episode. Unknown speech durations remain unknown. Existing F04 scenarios/results stay historical; their old boundary/withdrawal rubric is not valid for scoring this F07 policy. Run them against the frozen production source to reproduce historical results; use F07 expectations for this candidate.

Reviewer recommendation to ship only smiles/brows is **not accepted as a scope change**: the approved fallback retains the existing production visual representation if the complete expression candidate fails. The available six-window probe also cannot establish that no AU15 threshold could ever work. AU15 failure remains recorded; no new classifier or third tuning round is authorized. The full candidate is not a released feature.

### Clean preliminary correction disposition

Fresh `clock-review.json` verified actual **Claude Opus 5 only**, tools disabled, no subagents/helper models in that run: **“Clear for P1 development.”** The intervening correction review verified F1–F6 but found a repeated-frame clock-jitter crash and stale test expectations. Both are fixed. UI capture/poll times now derive from one stable UTC/performance-clock origin; out-of-order samples become unavailable instead of throwing. Latest complete suite: **278 passed in 24.36s**, `tests-clock-correction.xml`. No further Luna inference occurred; remaining aggregate authorization stays $0.28924566.

The intervening `correction-review.json` listed primary Opus 5 and 15 Haiku helper output tokens. This is preserved and disclosed; it is not represented as an Opus-only run. The final follow-up pinned the documented CLI background-model alias to Opus 5 and verified only that model in the response. All reviews used the authenticated Claude Pro subscription, not the Luna paid-API ledger. Non-blocking notes remain: audio-only transition can conservatively reset visual buckets after clock drift; all-duplicate partial buckets may omit an expression summary. These do not establish precision timing success.

One tuning round has been used; review-driven implementation corrections are not a new semantic tuning run. Second-round decisions must preserve the P1/freeze sequence. Required resource pairs, actual UI delivery latency, final 144 responses/two repeats, independent timing metrics, three consenting checks and blinded usefulness scoring remain unmeasured. **Preliminary code-review gate is clean for P1 development**, but participant consent/scheduling, bounded live-test spending/evidence preparation and actual results remain outstanding. Final post-human review and publication remain pending. F07 is not complete and this working candidate has not been committed/pushed as a reviewed release. Use [the prepared participant protocol](F07-MANUAL-CHECK.md) only after its remaining live-test preparations are complete.

## Downloaded DISFA development assessment

User-supplied DISFA has now been inventoried and used with the unchanged local MediaPipe processor. [Dataset assessment](F07-DATASETS.md) records complete label coverage, a fixed 3-development/24-reserved subject split, six development windows and 582/582 available probe signals. Three development videos have exact 20-fps frame/label alignment. Raw compact evidence is in `build/f07-disfa-20260914-v2/`; the initial five-window probe is preserved separately. All original archives remain intact; no human media uploaded, no new LLM responses, no production changes or accuracy/timing gate pass. Parser regression: 1 passed. Rare AU15 scores are much weaker than smiles/brows in this probe and require separate calibration; no candidate tuning rounds have started. Remaining full S0 case/input/protocol freezes and S1–S7 gates remain outstanding.

## September 14 preflight — S0 incomplete

**Subsequent user revision:** The user authorized assistant screenshot annotations or suitable datasets now and live checks later. Independent annotations no longer block implementation. [Dataset investigation and actual annotations](F07-DATASETS.md) record seven paused podcast point samples, including smile and brow-touch confounds. No positive mouth-corner-lowering coverage or precise onset/offset result is established. DISFA is the preferred independent dataset but requires research access; none was downloaded. Remaining S0 case/input/protocol freezes and later gates are still outstanding. The earlier blocker below records the pre-revision state and is superseded only as a prerequisite to implementation.

Read the five required project documents and all nine cards in the permanent F07 column, beginning at [F07.0](https://trello.com/c/wLMJMPeN). F01–F06 remain complete. Production code and Luna low configuration are unchanged; local-model comparisons remain set aside.

Private evidence: `build/f07-preflight-20260914-033817/manifest.json`. The new ignored directory preserves 90 source/configuration/asset hash records, copies of text sources, the approved plan before this status update, and the pre-existing planning diff. Baseline Git HEAD is `28e843f3e2efbfa5f494f8c40c759705e720bfe1`. This is a source baseline, not completed frozen model requests or scenario families. Existing historical results and unrelated personal PDFs were untouched.

| Preflight check | Observed result |
|---|---|
| Basic synthetic video | SHA-256 matches existing provenance; all 1,295 frames decoded; PTS 0–86.266667 seconds; strictly increasing; largest gap 0.066667 seconds |
| HeyGen synthetic video | SHA-256 matches existing provenance; all 1,346 frames decoded; PTS 0–53.8 seconds; strictly increasing; largest gap 0.04 seconds |
| Annotation coverage | NOT ESTABLISHED. Existing manifests provide authored pose labels and speech times, not independently annotated visible episodes for the three configurations. No F07 annotation files found in project assets/build. |
| Reviewer preflight | Authenticated Claude subscription; tool-disabled, safe-mode initialization catalog resolves `opus` to `claude-opus-5`. Raw initialization response retained locally. No user prompt, review or inference dispatched. Actual review response identity must still be verified at both gates. |
| Model-test method/budget | Asked user; pending. No new language-model responses or paid evaluation work. |

Frames were decoded in memory only; only frame timestamps were saved. Approved synthetic media were neither modified nor copied into new frame files. The source portrait sheet was visually inspected as feasibility context; it is not an independent human annotation or emotion ground truth. Both videos remain historical source families, not fresh held-out people or independent variants.

## Blocking S0 exit

The approved plan requires suitable independently annotated timing clips before code implementation. Precise PTS alone cannot establish onset/offset accuracy or prove all three configurations occur clearly. Requested the location of existing annotations; if none exist, obtain blind human annotations of suitable approved reusable sources using [the annotation protocol](F07-TIMING-PROTOCOL.md), and establish distinct tuning/held-out source assignments. Do not infer configuration labels from generation tags or detector output.

After this gap is resolved, complete the at-most-18 tuning-case and 24 fresh held-out-family freeze, exact requests/schemas/rubric, hidden expectations, and future participant/checkpoint protocol before S1/tuning. No family split or human participant allocation is claimed frozen by this preflight.

## Gates and remaining work

S1–S7 remain NOT STARTED. Expression precision/recall/coverage/timing, usefulness/opportunities/incorrect items/abstention, visual uplift, production comparison, confidence, safety integration, resources, transcription slowdown, token delta, API cost/latency, and all three participant outcomes are NOT MEASURED. Preliminary and final reviews are NOT RUN. No application tests were rerun merely to re-establish F06 status; no application code changed.

The approved design remains 72 matched visual + 24 unchanged-production + 48 calibration responses = 144, with two independent repeats. Preserve the three 85% gates, 400 mean added input-token allowance and separate 10% cost increase limit; all other plan thresholds remain unchanged. Missing annotations are not an expression accuracy failure and do not activate a measured-failure fallback automatically.

At most two tuning rounds; freeze September 23, target completion September 27, protect F08's October 1 Windows deadline. No reviewed release exists yet; commit/push and three-way main verification remain pending the applicable review, evaluation and human gates.
