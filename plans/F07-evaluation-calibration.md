# F07 — Evaluation and calibration

**September 14 user revision — pretrained vision comparison:** Download and test the existing pretrained visual-model shortlist locally against MediaPipe/F07, emphasizing resident RAM, private committed memory and speed. Preserve independent dataset access/training-overlap distinctions. See [screening](../docs/F07-VISION-SCREENING.md). No local LLM comparison, paid API call, threshold tuning round or production substitution is implied. Existing safety, held-out, human, review and release gates remain.
Completed CPU screening: all six pipelines tested on DISFA development data and two new conversation clips; portrait peak resident memory ranged from 258 to 1,326 MiB. Current pipeline retained; independent annotated validation and full F07 gates remain pending.

**Latest comparison — September 14:** Before-P1 evaluation completed: 144 independent Luna-low responses, 143 validated; 279 offline tests pass. Aggregate committed API cost $0.07768505/$0.30, including the preserved interrupted fixture attempt; $0.22231495 remains. Verified tool-disabled Opus-5-only harness correction review cleared this provisional comparison. Boundary/ownership failures remain; visual-only estimated cost is +10.39% versus production (+12.21% versus movement), despite input remaining below +400 tokens. No release pass. See [results and honest gate status](../docs/F07-VALIDATION.md). Live checks and the requested after-human repeat are still pending; final review/publication remain gated.

**User sequencing revision — September 14:** User explicitly requested the evaluation before human testing and again afterward. Run the same 144-response design now as a provisional comparison, with two independent responses per condition; repeat after human testing/corrections. This supersedes the P1-before-first-comparison dependency, not the human/review gates or spending cap. Keep the original $0.30 aggregate authorization and all prior spend. Exposed cases used to guide changes become development/regression evidence; a later rerun alone cannot restore untouched held-out status. Preserve all versions and label any fresh equivalents separately. No new calibration round or third round is authorized merely by an evaluation run.

**Implementation update, September 14:** A first working S1–S3 candidate and first tuning round now exist; supersedes older “not started” status below. User selected real API Luna low with a new $0.30 aggregate cap. Twenty-four tuning responses cost $0.010754; final 144 responses have not run. Mouth-corner signal recall and a candidate attribution regression prevent claiming success. See [current evidence and remaining gates](../docs/F07-VALIDATION.md). Human testing, required resource/held-out evidence and both completed review gates remain outstanding. All original numerical gates, two-round limit and deadlines remain unchanged.

**Status:** Approved 2026-09-14, including the three self-review revisions. S0 preflight started September 14; application implementation and comparative model evaluation have not started. The user subsequently authorized assistant-authored screenshot annotations in place of waiting for independent timing annotations before implementation. Seven podcast point samples and dataset feasibility findings are recorded in [F07 datasets](../docs/F07-DATASETS.md). Remaining S0 case/input/protocol freezes are still required; independent timing accuracy is not claimed. See [preflight evidence](../docs/F07-VALIDATION.md).

**User revision — September 14, after preflight:** Independent human timing annotations are no longer a prerequisite to implementation for now. The user authorized this assistant to inspect one podcast participant through screenshots and create provisional annotations, or use a suitable existing dataset, with live call testing later. This supersedes the independent-annotation-before-code wording in S0/S1 and the timing-fixture paragraphs below. Assistant annotations must be labeled as such; sparse screenshots cannot pass the original precision timing gate. Missing configurations remain missing, not fabricated labels. The <=1-second independent timing gate remains unverified/deferred, not passed. This revision does not itself waive the 144-response design, method/budget rules, other numerical gates, preliminary/final Opus reviews, or declare future participant checks completed.

**Target:** September 27, 2026. Tuning cutoff: September 23. September 15 roadmap revision: F08 owns only easy Windows installation and Claude review by October 1 (sooner if ready); final demonstration preparation is deferred. F09 Mac implementation/testing follows immediately after F08 completion. F07 acceptance gates are unchanged.

**DISFA assessment — September 14:** The user supplied the dataset and authorized development use. Complete AU labels and three development videos were verified; six fixed windows were processed through unchanged local MediaPipe (582 signals). SN001–SN003 are development, other 24 subjects reserved; camera views are not independent subjects. See [dataset evidence](../docs/F07-DATASETS.md). This establishes a usable local development source, not a passed onset/offset or accuracy gate. Full guidance-case/input/protocol freezes remain outstanding; no production tuning round or new Luna response has run.

**Roadmap card:** [F07 — Evaluation and calibration — target Sep 27](https://trello.com/c/68EGr9Sh).

**Trello publication:** Permanent column **F07 — Evaluation and calibration** created and nine execution cards published 2026-09-14. Begin with [F07.0](https://trello.com/c/wLMJMPeN). Column ID: `6aa734373bc14ecb72436b93`. Planning documents remain local until Git publication; no implementation/review/evaluation pass is implied.

## Goal and user-visible result

Improve the evidence behind Conversation Copilot's guidance, then measure whether the guidance becomes more useful without additional incorrect suggestions. Retain a clearly visible held expression even when its movement stops. Distinguish smile-like mouth corners, brow lowering and mouth-corner lowering; never turn one into a claim about inner emotion or intent.

Target three documented semantic problems: ambiguous/irrelevant memory reminders, overreading verbal boundaries as discomfort, and unsupported ownership or meaning inferred from garbled speech. Ship only changes that pass their applicable gates. More visual citations, more memory proposals or higher confidence alone are not success.

F01–F06 remain accepted as complete. Their recorded results are evidence, not closure gates to reopen. Luna low remains selected for live/manual guidance, Ask Memory and post-call review. Local-model comparisons remain set aside. This plan authorizes no inference in the planning session and allocates no paid evaluation budget.

## Approved grilling decisions

| Decision | Agreement |
|---|---|
| Expression scope | Three separately labeled visible configurations: smile-like mouth corners, brow lowering, mouth-corner lowering. Describe combinations explicitly instead of using an undifferentiated frown label. |
| Human evidence | Three consenting participants: one development participant and two people unseen during tuning. |
| Human time | Approximately 15 minutes, 15 minutes and 20–25 minutes respectively; the last includes about 10 minutes of natural conversation. |
| Deadline fallback | Stop tuning September 23. If visual guidance does not pass accuracy, usefulness and performance gates, retain current visual behavior and release independently passing calibration changes and the honest evaluation report. |
| Calibration limit | The three targets above, at most two tuning rounds, no broad rewrite or model search. |
| Held-out scenarios | 24 fresh families: 12 visual and 12 calibration; two independent responses per condition. |
| Quality thresholds | User revised every proposed 90% threshold to 85%: expression precision, sustained-expression coverage and appropriate abstention. Other thresholds remain as proposed. |
| Token allowance | Mean added input allowance revised from 150 to 400 tokens per matched guidance request. The separate 10% total API-cost limit remains. |
| Production baseline | Add the unchanged production application on the twelve visual families, twice: 24 additional responses, 144 final comparison responses in total. |
| Timing evidence | Keep the ≤1-second onset/offset gate, measured on timestamped, independently annotated reusable clips. Verify suitable clips before implementation; calls provide expression accuracy, confound and usefulness evidence. |
| Silent expression changes | Local observations update continuously; automatic cloud guidance remains speech-triggered. A silent expression alone does not initiate a paid request. |

## Established evidence and implementation boundaries

Read AGENTS.md, CONTEXT.md, PLAN.md and docs/TESTING.md before implementation. Use this plan for F07 detail and Trello for execution status.

| Evidence / code | What it establishes for F07 |
|---|---|
| `conversation_copilot/video.py` | Existing CPU MediaPipe FaceProcessor produces 478 landmarks and 52 blendshapes for one selected face. Reuse its in-memory signal, tracking and loss/recovery boundaries. |
| `conversation_copilot/interpretation.py`: VisualAggregator, VisualBucket, `_compact_payload`, request preparation | Current two-second buckets hold mean absolute changes, not sustained expression levels. Brow groups mix upward and downward components. Mouth-corner lowering is not a distinct group. Reliability is a fresh-sample ratio, not expression precision. |
| `conversation_copilot/__main__.py`: poll_once, switch, audio conversion and snapshot creation | Visual aggregation uses UI observation time; audio supplies attributed turn timestamps and local vocal duration. Trace capture-to-observation and utterance timing before aligning them. Switch/Continue must invalidate expression state across analysis selections. |
| `interpretation.py`: INTERPRETATION_INSTRUCTIONS and `_cautious_policy`; `guidance.py`: interpret_guidance | Both prompt and local policy connect brief deflection plus general movement to discomfort/withdrawal. Fix the unsupported inference at these shared surfaces; a prompt-only change can leave the local override in place. |
| `guidance.py`, `memory.py`: retrieve, request construction, display/validation | Log retrieval, eligible candidates, actually transmitted candidates, raw selection, validation and display separately. Production supplies at most four memory candidates. Preserve sensitive local reminders and contact/lifecycle enforcement. |
| `memory.py`: EXTRACTION_INSTRUCTIONS and extraction; `post_call.py` | Existing instructions already caution against garbled attribution. Inspect actual failures before adding more wording. Keep uncertainty out of approved facts through omission or supported clarification; never silently repair source transcripts. |
| [F06 expanded comparison](../docs/F06-AGENT-API-EXPANDED.md) | Final cases 200 (boundary), 259 (rent/job alternatives), 256 (garbled full-call extraction) remain targeted evidence. Seven-memory cases bypass production retrieval and isolate use of supplied evidence. One final response per case does not establish reliability. |
| [F06 prompt regression](../docs/F06-NEW-PROMPT-REGRESSION.md), [memory blend](../docs/F06-MEMORY-PROMPT-BLEND.md), [Luna comparison](../docs/F06-LUNA-TERRA-COMPARISON.md) | Prior changes traded reminder recall against topic/ambiguity errors. Some real-call misses were absent retrieval candidates; others omitted supplied candidates. Earlier prompts/models cannot be treated as the current baseline. |
| [Fixture provenance](../conversation_copilot/assets/f04/PROVENANCE.md) | Basic fixture has exact turns, two separate audio stems and six authored poses. HeyGen adds compression/lip-sync stress but one animated speaker, static self-view and an omitted opening line. Neither establishes real-world emotional accuracy. |
| `benchmark.py`, `f06_resources.py`, existing tests and tools/evaluation | Reuse bounded replay, timing, memory and saved-output machinery. Read runners without executing/importing historical paid scripts: some start inference or overwrite historical paths. |

The private expanded corpus is under `build/agent-api-expanded-20260913/`; its manifest and `final-check/api.json` preserve exact records. Historical evaluated cases are tuning/regression material, not fresh holdout. Exclude the contaminated multi-case agent pilot. Preserve all old files and private archives.

## Expression observations and integration

Use existing local blendshapes first: mouthSmileLeft/Right, browDownLeft/Right and mouthFrownLeft/Right. Verify the installed model's actual categories. Treat numerical blendshape intensity as a local measurement, not a probability of emotion or an automatically calibrated expression confidence.

The smallest candidate adds bounded levels and event timing to the existing aggregation path. Keep separate left/right measurements only where useful to avoid hiding asymmetry; send compact summaries, never full landmark/blendshape histories. Record visible configuration, level, observed duration, onset/offset, observation confidence and availability/quality reason. Record combinations without assigning a shared emotional label.

Keep the following rules explicit:

- Persistence depends on observed level, not continued movement. Use a small amount of smoothing and separate onset/offset thresholds if tuning demonstrates a need. Freeze those parameters before holdout; avoid a new classifier or configuration framework.
- Observation confidence reflects freshness, visibility, stable selected-face tracking and agreement of relevant local signals. Low movement is not low confidence. Quality/visibility is not emotional meaning.
- Missing, stale or occluded evidence becomes unavailable, not neutral. Do not extend measured duration through unobserved gaps or carry an active expression across Switch face, tracking restart, Stop/Start or a changed selection. Preserve the six-second loss lock and explicit Continue tracking; healthy audio continues after visual loss.
- Speaking can obscure mouth-corner configurations. Downweight or withhold ambiguous mouth evidence using existing remote speech timing and mouth activity; retain a clearly visible held smile while speaking. Brow evidence remains separately assessable. No assumption that speech means no expression.
- Check head movement, crop/scale changes, lighting, partial occlusion, small faces, asymmetric configurations and frozen frames. Existing landmarks/face geometry may provide quality cues; add no model/dependency without a separate plan revision and measured need.
- Align derived intervals to actual utterance/capture time, not model completion time or merely the UI poll. Use the existing clock origins and retained remote duration where available. Exclude future evidence from a checkpoint. Uncertain alignment is explicit; do not invent exact timing for an imported transcript without duration.
- A contact's listening reaction may be observed during the user's speech, but it cannot be described as the contact's speaking behavior. Never analyze the user's face/prosody. Unknown/overlapping timing must not manufacture speaker ownership.
- Pass only bounded aligned observations through snapshot, compact request and existing evidence display. Verify token trimming does not change transcript or memory evidence across a purported matched comparison. A missing/trimmed visual row cannot support a citation.
- Show the observation and uncertainty through existing evidence text. Do not add a new emotion dashboard, persistent face profile or biometric identity inference.
- Continuously update local expression state, but preserve speech-triggered automatic interpretation. A silent expression change does not create an extra cloud request or bypass the existing cadence. The existing explicit manual check remains available within its budget. Test that a silent held expression persists locally and is available to the next eligible speech/manual request; document that silence alone does not refresh model guidance.

## Evaluation design and scoring

### Freeze before tuning

Create a new dated, Git-ignored F07 results directory. Freeze baseline source/configuration, authored case IDs and exact inputs, prompts, schemas, scoring rules, expected behavior and scenario-family split. For future human calls, freeze the protocol, participant allocation and checkpoint-selection rules before tuning; their actual observations/transcripts can only be frozen after collection. Do not tune on those held-out observations. Keep expected answers and other cases' outputs out of responding-model requests. Store source hashes and record any reconstruction explicitly.

Use a bounded tuning set of at most 18 selected cases (up to six visual and twelve semantic) plus existing directly affected regression tests. At most two candidate tuning rounds; group changes by causal target and retain rejected candidates and their reasons. Do not start a third round because budget remains.

Held-out set: twelve visual scenario families and twelve calibration families, with four calibration families per target. Vary context, wording, speaking/listening, neutral confounds, ambiguous/clear evidence and ownership; do not make superficial paraphrases of a tuning case count as independent families. Use different source clips/participants for visual tuning and holdout. Label which cases are actionable, which require abstention, and which require a reminder before tuning.

Historical examples and the existing basic/HeyGen fixtures are regression/stress evidence. New authored variants of those known media are still the same source family; do not count their faces as unseen-person evidence. The two held-out people supply the human generalization check.

### Matched comparisons

| Comparison | Fixed inputs / conditions | Final response count |
|---|---|---:|
| Visual | Twelve fresh families × no visual/current movement/improved expressions × two independent responses | 72 |
| Unchanged production | The same twelve visual families × the frozen unmodified production application × two independent responses | 24 |
| Calibration | Twelve fresh families × frozen baseline/final candidate × two independent responses, using the affected guidance or extraction endpoint | 48 |

Total: 144 final requests before exact reuse, not 144 independent scenarios. Two repeats probe variability; report results by family and repeat, never inflate the independent sample count. These counts are a workload plan, not spending authorization. Human calls and any method-specific API acceptance checks are separate, explicitly budgeted work.

For the three visual arms, keep finalized speech, local vocal data, approved memory candidates, sampling checkpoints, model/effort, output allowance and interpretation policy fixed. Supply a common instruction vocabulary capable of describing both formats, changing only the visual condition. Freeze the current movement reducer and fixtures for this purpose. Run the fourth, unmodified production arm on those same checkpoints to compare complete application behavior. Comparing old policy plus old observations against new policy plus new observations is an end-to-end comparison, not isolated visual uplift. Report useful/incorrect items, opportunity coverage and response/display behavior against this fourth arm; a material regression blocks shipping even when isolated visual uplift passes.

Do not remove speech/memory to make an improved observation payload fit. If optional evidence differs after trimming, label the test unmatched, shorten the observation representation and rebuild the pair before scoring. Exact saved-output reuse requires matching instructions/input/schema/model/effort/output limit and explicit provenance; a reused response cannot satisfy the second independent repeat.

Score raw output, validated output and displayed guidance separately. Primary usefulness is what the user could actually see at that checkpoint, including stale-result suppression and waiting fallbacks. Count rejected requests, unsupported IDs, timeouts and missing actionable guidance rather than dropping failed responses from success denominators. Use fixed-input comparisons for model selection behavior and paced production retrieval/display replays for integration; report them separately.

### Numerical quality gates

| Measure | Acceptance / denominator |
|---|---|
| Expression precision | **≥85% for each configuration**: correctly matched reported episodes / all reported episodes. One-to-one matching to independently annotated visible episodes; duplicate fragments count as extra detections. |
| Expression recall | **≥75% for each configuration**: detected labeled episodes / all clearly visible labeled episodes. Abstaining on a visible expression is a miss. |
| Human sample | At least **20 positive episodes per configuration** across the two held-out people, targeting ten each, plus neutral/speaking/head-motion/occlusion controls. Report counts and rates by person and condition; inadequate coverage is not established, not a pass. |
| Sustained-expression coverage | Report the correct configuration through **≥85% of each clearly visible hold lasting ≥3 seconds**. Include holds while speaking and after movement stops. |
| Onset/offset | **p95 absolute error ≤1 second**, reported separately for onset and offset on matched episodes in timestamped, independently annotated reusable clips. Do not hide undetected episodes; they remain recall failures. Human-call annotation times are supplementary, not the precision timing gate. |
| Useful displayed items | **≥80%**, with supported/helpful, supported-but-unhelpful and incorrect scored separately. A correct citation alone is not usefulness. |
| Useful opportunities | Useful displayed guidance on **≥75% of pre-labeled actionable opportunities**. Always abstaining or always returning a generic waiting action cannot pass this gate. |
| Incorrect displayed items | **≤5%**. Unsupported emotional meaning, wrong/irrelevant memory, factual/ownership invention and counterproductive advice count even when phrased tentatively. |
| Appropriate abstention | **≥85% of pre-labeled ambiguous/conflicting cases**. Tone abstention may coexist with a factual question or useful listening action. Do not require whole-output silence. |
| Visual uplift | Better next-action guidance in **at least two held-out families versus each baseline**, with no additional incorrect displayed items versus either. Require improvement in both repeats to credit a family; baseline comparisons may identify different improved families. More citations/confidence alone do not count. |
| Confidence | Zero unsupported high-confidence emotional/intent claims. Report observation and interpretation bins separately; fewer than five judgments in a bin means insufficient sample, not calibrated confidence. |
| Safety/integration | Zero wrong-contact/sensitive-evidence egress, biometric identity claims, raw-frame retention/upload, unavailable-evidence citations accepted as valid, silent face reselection, or audio interruption caused by F07 visual loss handling. |

Use a frozen event-matching rule (same configuration, overlapping labeled interval, intersection-over-union ≥0.5) and timestamped annotation protocol. Score unknown visibility separately from expression absence. Capture independent human annotations without showing detector labels to the annotator; a requested pose is not ground truth. Retain uncertain/disputed annotations and coverage; do not remove hard cases after seeing errors. Numerical rates are empirical sample results, not population accuracy guarantees or claims about real emotional truth.

The user grades guidance usefulness against the current conversational objective, with condition names hidden during matched output comparison. Present the same bounded source context, randomize output order, preserve judgments and disagreements. Each canonical repeated item counts once per displayed episode, while repeated/unhelpful resurfacing is separately recorded. Score family results and all emitted-item counts so verbosity cannot conceal errors.

For calibration, apply applicable item/opportunity/abstention/confidence gates to each target, rather than hiding one failing target in an aggregate. Report correct reminder selection conditional on the target being supplied, retrieval recall@4 where retrieval actually runs, irrelevant-selection rate, and overall displayed reminder opportunity coverage. An unavailable/wrong-contact memory is never a valid retrieval target. Ambiguous targets may require multiple low-confidence alternatives or omission according to the frozen expectation; an irrelevant extra alternative is still an error. Extraction claims require clear attributed source support and remain proposals awaiting review.

### Latency, resources, tokens and cost

| Measure | Gate |
|---|---|
| API processing / request-start to displayed-card p95 | **≤6 seconds / ≤7 seconds** |
| Eligible finalized-turn to displayed guidance p95 | **≤20 seconds**, including cadence wait and stale suppression |
| Local visual processing | **≥10 signals/second** and frame-age p95 **<500 ms** |
| Added CPU | **≤10% relative increase in process CPU time** for the same elapsed workload; report absolute CPU seconds and hardware, not an ambiguous percentage of all cores |
| Added working set | **≤100 MiB** at matched post-warm-up checkpoints; report peak as well |
| Post-warm-up growth | **≤2 MiB/min** |
| Concurrent transcription | **≤10% p95 slowdown** relative to matched current-code concurrent runs |
| Added input tokens | Mean **≤400 tokens per matched guidance request**; report exact API tokens and local estimates separately |
| Added API cost | **≤10% total increase** for matched requests/workload, including output/reasoning tokens and failed billed requests |

The token and cost gates both apply: permission for 400 additional input tokens does not authorize increased hard ceilings or spending. Preserve current combined guidance limits (4,500 estimated input, 1,200 output), the 1,300-token transcript allowance, existing manual interpretation ceilings and post-call/Ask limits. Preserve the $0.35 Assisted Call cap, $0.27 live portion, $0.08 post-call reserve and $0.15 warning. These application caps are not an F07 evaluation budget.

Reuse benchmark/resource measurement helpers, using three sequential matched baseline/candidate pairs of ten-minute runs (two-minute warm-up), alternating order. Include CPU face processing with the existing local transcription/BGE workload; isolate cloud variability from local resource measurement. Report every pair, median and worst result; unexplained run-to-run disagreement is inconclusive and cannot be selectively discarded. Require the stated resource gates on the median pair and investigate any safety, queue or teardown failure regardless of median. Record cold startup separately; F08 owns packaging/minimum-install claims.

For actual API tests, preserve request/response/finalized-turn/display timestamps, eligible opportunities suppressed as stale, p50/p95/max, errors and timeouts. A returned response that never displays does not count as delivered guidance. Keep the existing speech-triggered 10–15-second adaptive cadence/display behavior; introducing expression-only automatic paid requests is outside F07. Zero stale or duplicate replacement acceptance remains an affected integration check.

Compare cost both as actual billed/estimated usage with cache provenance and with a consistent uncached price calculation, so unequal cache warmth cannot manufacture savings. Verify current provider pricing before future paid work. Agent elapsed time/subscription usage cannot establish API latency, billing or enforced structured decoding. With agent-only evidence, those gates remain unverified; request explicit API method/budget or report a release blocker rather than silently changing method or marking them passed.

## Human checks and optional external clips

| Participant | Session | Timing and role |
|---|---|---|
| P1 | Approximately 15 minutes | After clean preliminary review: setup/consent, controlled positive and negative configurations, short conversational check. May inform the second tuning round. |
| P2 | Approximately 15 minutes | After tuning freeze and any required preliminary correction review: controlled held-out expressions, speaking/listening and tracking disruptions. |
| P3 | Approximately 20–25 minutes | Same held-out controls plus about ten minutes of natural conversation evaluating helpful and incorrect guidance. |

Use ten short occurrences of each configuration per held-out participant, including clearly visible sustained holds; interleave neutral speaking and head motion rather than running only positive poses. Include partial occlusion, brief loss, >6-second loss, Continue tracking, selected-face changes and interrupted visual capture with continuing audio. Mark actual visible expression intervals with local annotation timestamps and record uncertainty. Calls supply expression accuracy, sustained coverage, confound and usefulness evidence; do not claim one-second timing accuracy from approximate live notes.

Before implementation, verify reusable clips with independently annotatable visible onset/offset and precise playback timestamps for all three configurations. Label actual configurations rather than generation/emotion tags and freeze distinct tuning/held-out clip assignments. Run the ≤1-second timing gate on those sources. The existing approved synthetic fixtures can supply controlled timing evidence where suitable, with their synthetic limitation stated; appropriately licensed human clips can supplement it. This required timing-fixture feasibility check is separate from optional broad external stress-clip curation. If suitable timing evidence cannot be established, resolve that gap before implementing rather than quietly dropping the gate or retaining live-call frames.

Use one existing supported call platform per participant, selected for practical scheduling; this tests F07 and does not revalidate every F02/F03 platform or reopen earlier waivers. Explain bounded transcript/derived-observation use to participants before the call. Use fictional seed memories where memory scenarios are needed; never silently approve test facts in the user's real contact database. Private logs remain local and ignored. Do not upload private historical logs to a provider without explicit applicable permission.

For the natural conversation, record the user's actual examples of helpful/unhelpful/wrong guidance, missed opportunities and confusing confidence. Apply the item rubric and report its small sample separately from controlled results. A short call with no relevant expressions or actionable opportunities is insufficient coverage, not automatic success. Prepare an ordinary factual reply/listening example, a refusal, an ambiguous memory reference and a topic transition without pressuring the contact to disclose personal matters.

Public video is optional supplemental evidence for compression, lighting, natural mouth motion and camera changes, not a substitute for consenting participant checks or emotional ground truth. Prefer creator-provided files or appropriately licensed sources; record URL, author/license, segment times, hashes when a reusable file is available, and annotation provenance. YouTube supports a Creative Commons filter and CC BY attribution ([official guidance](https://support.google.com/youtube/answer/2797468?hl=en)). Do not build a downloader, retain new captured frames or broaden production selection to arbitrary browser windows. Existing project-owned synthetic files remain unchanged. Cap external clip curation at half a day; omit it if useful sources are not readily available.

No dataset or file transfer to another device is implied by Git publication. Preserve approved synthetic sources separately from runtime call media. Save compact event/observation traces and annotations for reproducibility, not full raw landmark histories or call video. Without retained human frames, later blind reannotation is limited; document that limitation.

## Small sequential implementation slices

Only F07 is active. Follow dependencies in order; reuse existing functions rather than introduce a second guidance pipeline or evaluator framework.

| ID / target | Work and direct surfaces | Dependency and exit gate |
|---|---|---|
| S0 — Sep 14–15 | Publish the approved plan/permanent Trello column. In the implementation session, freeze baseline, rubric, tuning/holdout families, source manifests and annotation protocol; verify precise reusable timing clips before code changes and establish future test-mode/budget decisions. Inspect reviewer availability without invoking a review in this planning session. | Final plan approval; timing-fixture feasibility established before code implementation. No code or inference merely to establish F06 status. All thresholds frozen before tuning. |
| S1 — Sep 15–17 | Add compact levels, event timing and quality/availability to the existing local aggregation. Handle persistence, missing samples, face-selection/reset boundaries. Main surfaces: interpretation.py, video.py and only necessary UI lifecycle hooks. | S0. Small deterministic checks for held level, onset/offset, stale samples, neutral speech-like motion and selection/loss reset; bounds/privacy preserved. |
| S2 — Sep 17–18 | Align observations to contact speech; pass through snapshot, compact serialization, trimming and existing evidence display. Implement the three matched visual arms plus the unchanged-production arm using the existing harness. | S1. Matched payload/clock checks, no future evidence or lost transcript context, honest missing modality, no cross-selection leakage; local expression updates during silence without automatic paid requests. |
| S3 — Sep 18–19 | Apply first bounded calibration candidate to the shared boundary rule/prompt and evidenced reminder/garbled-attribution defects. Trace every caller of changed shared functions. Change retrieval only with demonstrated missing-candidate evidence. | S2. Targeted regression checks and first authorized tuning round; candidate/baseline comparison preserves raw, validated and displayed output. |
| S4 — Sep 19–20 | Run affected feature/integration checks, resource measurements as authorized, and preliminary tool-disabled read-only Claude Opus 5 review. Correct accepted findings and obtain clean correction review. Supply concrete P1 script; record actual P1 outcomes. | S3 and clean preliminary review before any human test. Real reviewer identity recorded. |
| S5 — Sep 20–23 | Second and final tuning round using only tuning/P1 evidence. Freeze candidate and parameters by Sep 23. Recheck affected behavior and obtain refreshed preliminary review for material changes before P2/P3. | S4. No holdout feedback used for tuning; only passing candidate advances. If no viable visual candidate, choose approved fallback. |
| S6 — Sep 24–25 | Run frozen held-out comparisons, matched integration/resource/API acceptance evidence in the selected authorized method, P2/P3 calls and blinded user scoring. Draft limitations and demonstration script. | S5 and applicable method/budget permission. Report every gate as passed/failed/not measured; no fabricated pass or silent method switch. |
| S7 — Sep 26–27 | Correct accepted defects, do affected/user rechecks, obtain fresh final tool-disabled read-only Opus 5 review and correction follow-up. Audit/release verified final diff; update plan, report and board. | S6. Both review gates, actual user outcomes, corrections and verified publication complete before F07 completion. |

Any meaningful branch/parser/state change leaves the smallest runnable deterministic regression check in the existing test suite. Do not run inference merely by importing historical helpers. During implementation, complete affected tests first and the project's final required suite before review/release; this does not reopen old feature closure gates. Unit checks with fake model outputs do not constitute semantic evaluation. Preserve separate labels for saved-output validation, downloaded signal-model processing and new language-model responses.

## Test authorization, reviewers and preservation

Before future model-dependent evaluation, ask the user to select API, Codex agents or local models unless explicitly selected for that work. Never infer method from the selected production model. Local-model comparisons remain excluded unless the user changes that decision.

Paid API tests require a newly applicable explicit dollar cap covering proposed runs, live checks, retries and remaining reservations. Historical caps are not reusable authorization. Enforce cap before dispatch, preserve uncertain billing, avoid automatic retries and stop within the authorized cap. Budget exhaustion is not approval to use agents/local models instead.

Agent evaluations use actual `gpt-5.6-luna` at `low`, explicitly configured, no conversation-history fork and one fresh agent per distinct request. For a second independent repeat, use a new agent even if the request is identical. Keep expectations hidden and save raw answers. Report model unavailability rather than substitute. Agent results are preliminary quality evidence, not API parity, strict decoding, provider billing or deployed timing.

The required reviewer is **Claude Opus 5 (`claude-opus-5`)**, tool-disabled and read-only. Confirm and record the actual reviewer model. Preliminary review covers this plan, complete feature/direct-integration diff, automated evidence and known limitations before user testing. Refresh it when material corrections change the tested candidate. Final review is a fresh review after user outcomes/corrections, covering the final complete diff and evidence. Fix accepted findings or document evidence-backed rejection; obtain correction follow-up until no material findings remain. Do not substitute Sonnet/another model or treat F06's accepted review exception as an F07 waiver. If unavailable, report the blocked gate promptly; request an explicit user decision rather than silently skipping it.

Retain exact prompts, schemas, input/output limits, timestamps, model/version/effort, raw provider/agent responses, parsed output, validation/display outcome, expectations, human assessments, retrieval provenance, source/config hashes and token/cost ledgers. Keep baseline and every candidate in separate new directories. Update docs/TESTING.md when F07 evidence exists. Public reports use sanitized summaries; Git excludes private transcripts, test databases, logs, archives, credentials and personal files. No broad staging command that could include unrelated user PDFs.

## Deadline fallback and failed holdout handling

September 23 ends tuning; reserve September 24–27 for final evaluation, human evidence, review/corrections and publication. F08 retains September 28–October 1 for Windows delivery. Do not add an extra model, dependency or broad optimization to rescue a late gate.

If improved visual observations fail any applicable gate or do not improve next-action guidance, keep the existing production visual representation and retain the measured failed candidate only as evaluation evidence. Ship independently passing targeted calibration fixes plus the limitations report. Do not claim improved expressions shipped. If a single semantic target fails, retain that accepted F06 behavior and report it; do not obscure its failure with another target's score. If no changes qualify, an evaluation/report-only outcome can close F07 only with explicit user acceptance of that reduced result.

Opening a held-out failure consumes that case for future tuning. Correctness repairs can be verified on the original as regression and on new untouched equivalents; do not call the old case held-out again. If expression tuning used P2/P3 observations, those people are no longer unseen. Do not demand a fourth person silently: keep the failed visual candidate out of release or obtain an explicit revised validation agreement. Missing samples, unavailable reviewers, unverified API gates or absent actual human results cannot be labeled passed to meet the date; report the specific blocker and seek a scope decision.

## Trello, review artifacts and publication

After final plan approval, inspect the board again. Reuse or create the permanent **F07 — Evaluation and calibration** column; avoid duplicates by checking existing card titles/content before each creation. Keep the existing roadmap card in Feature Backlog, update its stale F06-active wording and link to this exact feature-plan filename (`F07-evaluation-calibration.md`, not the older card's proposed `-and-calibration` name). Keep PLAN.md high-level with a link to this plan.

Create/reuse these execution cards in sequence, carrying the slice dependency, target and acceptance gate above:

1. [F07.0 — Approved plan, frozen cases and scoring](https://trello.com/c/wLMJMPeN) (S0).
2. [F07.1 — Persistent local expression observations](https://trello.com/c/YMtmvP5E) (S1).
3. [F07.2 — Speech alignment and guidance evidence](https://trello.com/c/246bWQoI) (S2).
4. [F07.3 — Targeted semantic calibration](https://trello.com/c/VqrrWvd6) (S3).
5. [F07.4 — Automated checks and preliminary Claude review](https://trello.com/c/2NprtNRE) (S4 review).
6. [F07.5 — Development call, corrections and tuning freeze](https://trello.com/c/HsjOVbO5) (S4 call / S5).
7. [F07.6 — Held-out evaluation and consenting live checks](https://trello.com/c/Zk2SDoY6) (S6).
8. [F07.7 — Final Claude review, corrections and user rechecks](https://trello.com/c/k5pEfLFu) (S7 review).
9. [F07.8 — Limitations, demo handoff and verified GitHub publication](https://trello.com/c/xVE5pfXO) (S7 release).

Planning approval marks planning work complete only. Do not mark implementation/evaluation/review cards passed merely because their plan exists.

Create `docs/F07-VALIDATION.md` and a focused manual-test/demo script during implementation, linking ignored exact evidence through local manifests without publishing private contents. Report what shipped, metric counts/denominators, per-person limits, baseline/candidate differences, failed/rejected approaches, confidence/abstention behavior, actual timing/resources/cost, human outcomes and both review dispositions. No claim of emotion truth, broad demographic generalization, all-platform validation or minimum-PC support from these samples.

Reusable walkthrough: the same neutral wording with a held smile, lowered brows, lowered mouth corners and neutral face; show sustained visible evidence and cautious meaning. Add a verbal refusal with an ordinary reply/listening action, an ambiguous memory example and face loss with uninterrupted transcript. Demonstrate only a passing released behavior; if using the fallback, explain the failed uplift result. Preserve this as a future demo handoff, not a new presentation/recording gate. September 15 revision: F08 owns easy Windows installation and Claude review only. Final demo preparation and a recorded fallback are deferred; any future recording uses approved fictional/synthetic content, not newly retained call frames. Existing F07 live validation remains required.

After final review/corrections, inspect the exact final diff, stage only intended public files, commit and push to GitHub. Verify local main, origin/main and GitHub main resolve to the same release commit (refresh remote state and independently query GitHub). Record the SHA and verification on the existing F07 publication/roadmap cards. Preserve unrelated working-tree files. Mark F07 complete only after these checks and the applicable gates, or an explicit documented reduced-scope acceptance.

## Implementation-session handoff

Recommended implementer: GPT-6 Astra with high reasoning for the state/timing/evaluation integration. This is an implementer recommendation, not a change to Luna low in the product or the required Claude Opus 5 reviews.

Use this prompt in a separate implementation session:

> Implement the approved F07 plan in plans/F07-evaluation-calibration.md for Conversation Copilot. First read AGENTS.md, CONTEXT.md, PLAN.md, docs/TESTING.md, the F07 plan and its permanent Trello column; inspect relevant code and preserved evidence before editing. F01–F06 remain complete, Luna low stays selected, and local-model comparisons remain set aside. Follow the small sequential slices and approved numerical gates, including 85% expression precision/sustained coverage/appropriate abstention and at most 400 mean added input tokens while retaining the 10% cost-delta gate. Keep smile-like mouth corners, brow lowering and mouth-corner lowering separate. Preserve selected-face/privacy/audio boundaries and distinguish retrieval omissions from misuse of supplied evidence. Include all 144 planned final responses: three matched visual conditions, the unchanged-production comparison, and baseline/candidate semantic calibration, with two independent responses per condition. Verify timestamped reusable timing clips before implementing; keep continuous local expression observations but speech-triggered automatic cloud guidance. Ask for API/agents/local method before new model-dependent tests unless explicitly selected; paid API work needs a new applicable budget. Preserve isolated actual-model agent settings and all exact evidence. Complete preliminary verified tool-disabled Claude Opus 5 review before human testing, refresh it for material changes, then conduct the three consenting checks, final review/corrections and user rechecks. Freeze tuning September 23, finish F07 by September 27 using its approved fallback if needed, and protect F08's October 1 Windows deadline. Finish with commit/push and verification that local main, origin/main and GitHub main match; update the plan, test index and Trello honestly. Do not silently substitute reviewers/models, claim failed or unmeasured gates passed, or publish private logs/personal files.
