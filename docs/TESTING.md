# Evaluation handoff and reusable history

**September 22 Qt UI checkpoint:** `python -m pytest -q`: 354 passing offline tests (14 Qt integration tests plus 340 existing checks). QtTest exercises real widget mouse/key events with disposable data and fake capture/model responses; screenshots inspected in both themes. An earlier 13-test UI set also passed simulated `QT_SCALE_FACTOR=1.5` and `2`. This is not native computer-use, physical scaling, screen-reader, Mac or live-call acceptance. Both WinRT/Qt import orders pass subprocess checks with pinned PySide6-Essentials 6.8.3. No fresh product-model evaluation ran. Verified Claude Opus 5 code review/follow-ups addressed persistence, lifecycle and UI boundaries. [Details](F10-QT-MIGRATION.md).

**September 21 accepted F07 checkpoint:** [Closeout and deferred gates](F07-CLOSEOUT-20260921.md). User accepts current main and moves on; no new inference, no experimental semantic merge, no API/held-out/participant pass claimed. Retained code has 335 passing offline checks. Preserve all historical evidence and budgets; future API testing requires explicit resumption. Earlier entries below retain their original historical scope.

September 21: reviewed current fixes/citation checkpoint published on main `addfe9b`, with local/origin/GitHub equality verified. Further semantic fixes isolated on `codex/call-semantic-fixes-20260921`, consuming the second/final calibration round; 336 offline tests pass. Full shortest-call Luna-low agent comparison completed: 64 fresh answers +2 exact reuses, 32/33 local passes per arm, both full post-call scratch checks pass. The candidate reduces some role/repetition errors but loses useful memories and adds unsupported summary details; do not merge the whole candidate. Verified tool-disabled Opus5 review/follow-up cleared the experimental checkpoint and docs-only main publication; the mistaken missing-schema-bound finding was retracted, citation pruning remains unvalidated, and remaining suggestions are untested hypotheses. No further calibration round remains. [Report](CALL-SEMANTIC-AGENT-20260921.md). No F07 acceptance or candidate merge claimed.

September 21 publication request: user explicitly authorized current fixes plus the bounded citation correction on main, then further semantic work on a new branch. 335 offline tests pass; fresh verified tool-disabled Opus 5 review cleared checkpoint publication; baseline addfe9b was published with local/origin/GitHub equality verified. This is a checkpoint, not F07 acceptance. [Scope and evidence](CITATION-MAIN-20260921.md).

September 21 [Luna source-limit experiment](CALL-SOURCE-CAP-20260921.md): 48 fresh isolated agent dispatches, 41 saved JSON answers, 7 tool/save failures, 21 exact prior live reuses; 61/69 planned local passes. All three prefix post-call pipelines pass in disposable stores. Same-output replay recovers correct four-source reminder; uncapped generation retains semantic errors and a job-memory regression. Private frozen evidence/checks: `build/source-cap-agent-20260921/`. No API spend, production change or acceptance pass.

Supplementary delivery follow-up: seven separately logged fresh Luna-low attempts fill the save gaps; all raw JSON is preserved. Total 55 fresh dispatches plus 21 exact reuses. With supplements, 67/69 requested outputs pass locally; two schema failures remain. First-pass failures and denominators are unchanged; no repairs or third attempts.

September 21 [complete shortest-call replay](CALL-FULL-AGENT-REPLAY-20260921.md):99 fresh isolated Luna/Terra/Sol low outputs,31 live checkpoints plus extraction/summary each.97 local output passes;two Luna schema failures preserved without retry. All3 complete post-call processing replays pass in scratch databases; source/input/log/prior-output hashes verified. Private evidence: `build/full-call-agent-replay-20260921/`. User deferred the other two calls before fresh requests (234 queued,12 prior reuses preserved). No API spend, production edits, API parity or F07 pass.

September 21 user-selected agent comparison: [36 isolated Luna/Terra/Sol low responses on six frozen cases](CALL-AGENT-COMPARISON-20260921.md). Two independent repeats/model/case, no history forks;36 local schema passes and24 exact-request corrected-guidance replays. Mixed gains: no duration fabrication, but Luna check-in and memory errors remain; Terra/Sol improve selected coverage with their own omissions/citation errors. Private raw evidence: `build/call-agent-models-20260921/`. No API spend, production edits or new F07 pass; API credit exhaustion still blocks the separate paid comparison.

September 19 requested Luna-low/Terra-low API comparison is **blocked by exhausted API account credits**, with zero model answers.23 exact corrected-app cases frozen,92 responses planned;35 offline checks pass. User caps: Luna $0.30, Terra $0.50. Twenty rate-limit failures plus one precise diagnostic preserved; original reservations reconciled append-only as known unbilled errors, no ledger reset. [Design, failure and continuation instructions](CALL-MODEL-API-20260919.md). Do not rerun the locked private runner or claim a model comparison occurred. Stronger-model agents remain deferred.

September 17 real Luna-low comparison: [old/revised requests, saved agents and root findings](CALL-PROMPT-API-20260917.md).90 structured API responses with two repeats; one downstream application validation failure retained. $0.09749827/$0.30 committed including the preserved startup reservation. After frozen inference finished, a two-line shared empty-cue canonicalization fix passes 56 affected/334 full tests; 32 saved revised guidance answers replay with exact model requests and only the failed result changes. Private evidence: `build/call-prompt-api-20260917/`. Original logs/ledgers and approved data unchanged. Verified tool-disabled Opus 5 review/follow-up cleared the diagnostic checkpoint; no human/held-out/F07 release pass.

September 16 isolated correction branch: [implementation and offline comparison](CALL-FIXES-20260916.md). Pre-fix checkpoint `codex/pre-call-fixes-20260916` (`75d5b27`); fixes on `codex/call-analysis-fixes-20260916`. Private preserved evidence/runner: `build/call-fixes-20260916/`. 333 offline tests pass. Three calls,149 request captures,146 saved Luna outputs and five saved Sol live answers replayed offline; no fresh semantic inference or release pass. Echo is excluded by user instruction. Method selection and final review remain pending.

September 16 completed-call diagnostic: user explicitly selected isolated Astra low and Sol high agent testing, with an independent root assessment; no new paid API inference. Private frozen evidence, exact tester instructions and raw assessments are in `build/call-audit-20260916/`. The 240-turn call has eight approved memories, one pending proposal and an approved seven-statement summary. Source hashes and log sequence continuity were verified. This is analysis only: no production changes or edits to approved personal data. Findings concern speaker/echo uncertainty, grounding and staleness, visual availability, draft-only summary consolidation and transient-memory scope. The selected-contact retrieval corpus was empty during this call, so it does not establish a retrieval omission. Final agent comparison is in the private `REPORT.md`; these exposed failures are development evidence, not a held-out pass or F07 completion.

September15 two-call real API follow-up: [comparison and cost projection](TWO-CALL-API-COMPARISON-20260915.md). 78 Luna live checkpoints plus16 paired/repeated Luna/Terra summary/extraction requests;93 structured answers, one truncated-JSON failure; $0.21179406 committed under the single explicit $0.40 cap. Saved evidence, source/input hashes, non-blinded assessments, replay and cumulative ledger are private in `build/two-call-api-20260915/`. Initial failure was not retried; continuation retained its full charge and all previous records. No production changes/model switch/memory approvals.72 targeted offline tests and runner mock guards pass. Read the report before claiming guidance quality, facial contribution or a Terra win. The previous diagnosis's “no new paid inference” describes that earlier phase only; this follow-up supplies fresh API evidence but not live GUI acceptance or review clearance.

September 15 long-call diagnosis: [findings, isolated Sol/root comparisons and guidance corrections](LIVE-CALL-DIAGNOSIS-20260915.md). Private exact evidence: `build/call-diagnosis-20260915/`. No new paid inference. Read the report's limits before treating agent answers or replay as API acceptance. The new guidance semantics retain source-aged, optional recent-context ideas; empty results are no longer waiting advice. Sensor pruning preserves a recent sample from both modalities. Future opt-in extraction logging now includes raw bounded requests/responses. This is an unreviewed development checkpoint, not F07 closure.

September 15 live diagnostic logging: explicitly launch with `COPILOT_TEST_LOG=1` to write a fresh private `build/live-evidence-*/events.jsonl` and exact Python source snapshot. Logging is off by default. Records include selected-face numeric blendshapes/box, expression durations/uncertainty, recent aggregate buckets, transcripts and vocal features, retrieval query/results/current selected-contact memory corpus, bounded model inputs/schema/raw responses, usage/releases, candidate-filter reasons, coordinator acceptance/staleness and displayed/waiting guidance. No raw frames, landmarks, raw audio or credentials are recorded. Existing evidence is never overwritten; local evidence copies persist independently of later in-app deletion. This supports numeric/text replay and supplied-evidence diagnosis, not rerunning a vision/audio model without original media or proving causal visual influence. A missing queue record/serialization failure/disk error marks the title LOG FAILED; do not treat that session as complete evidence. Resource samples, when launched alongside the app, are separate process CPU/resident/private snapshots, not calibrated full-app benchmarks. 52 affected offline checks pass (`tests/test_live_log.py` plus guidance/budget/expression/UI suites). Private review evidence: `build/live-logging-review-20260915/`; actual tool-disabled Opus 5 cleared the corrected instrumentation for preliminary live diagnostics; no final F07 acceptance implied. Active September 15 evidence began under `build/live-evidence-20260915-220254-7287a894/`, with launch/resource logs in `build/live-logged-launch-20260915-220252/`.

Local memory diagnostic started September 15: [first-slice report](LOCAL-MEMORY-EVALUATION.md).
Fresh private evidence is under `build/memory-evaluation-20260915T083732Z/`.
`tools/evaluation/memory_evaluation.py RUN --preserve-history` verifies the frozen source
and copies/audits named historical evidence without inference; it refuses an existing
history destination. This is initial preparation, not the complete evaluation runner.
The existing 40-question F06 fixture passed 40/40 with cached BGE (35/40 lexical-only)
in a one-off replay; its socket guard has not been independently verified by the reviewer.
111 affected tests passed after harness corrections. New held-out evaluation, Hindsight execution, complete resource
costs, human testing and final reviewed publication remain pending. Production stays unchanged.
Actual Opus 5 cleared the private initial checkpoint only, not the complete experiment.
The new repository-ignore check requires Git and a repository checkout when running pytest.

Latest user-authorized local vision downloads/screening: [F07-VISION-SCREENING.md](F07-VISION-SCREENING.md). Private scripts, models, numeric predictions and process-tree RAM samples are under `build/f07-pretrained-20260914/`. CPU diagnostic results are separate from the Luna API comparison and do not pass full-app resource or independent accuracy gates.

Read ../AGENTS.md for the standing API-versus-agent choice rule. This index is project-wide, not chat-specific. No inference is authorized by merely reading a report or running a historical script.

## Start here

Pretrained visual-model comparison research: [models, external validation clips and resource metrics](F07-PRETRAINED-MODELS.md). Proposed challengers are LibreFace, OpenFace 2.2 and Py-Feat XGBoost against existing MediaPipe/F07. GFT/MMI access and checkpoint overlap need verification. That research snapshot precedes the completed local screening linked above; no production replacement or independent accuracy winner is claimed.

Latest F07 before-P1 comparison: **144 independent API responses, 143 validated; 279 offline tests passed**. [Results](F07-VALIDATION.md) include boundary/attribution failures and the visual-only cost excess. Aggregate committed cost **$0.07768505/$0.30**, remaining **$0.22231495**; do not reset the ledger. Exact evidence: `build/f07-implementation-20260914/api-comparison-before-p1-v2/`; malformed interrupted attempt remains separately preserved. Actual tool-disabled Opus 5 cleared the corrected harness, not final release. Human checks and after-human repeat remain pending.

Reusable runner: `tools/evaluation/f07_comparison.py`, regression check `tests/test_f07_comparison.py`. `prepare` is offline; `run` is paid. Use the original freeze and a new `api-*` child. For the later comparison, prepare with `--stage after-human`; explicitly choose `--later-reserve-usd` for `run` to draw from the reserve while carrying all prior charges. Do not run a paid repeat before its authorized human/correction sequence, or treat exposed families as fresh holdout. Frozen requests, conditions, failures and independent-repeat denominators must remain intact. The private output-review packet has **no human scores**.

F07 first candidate: [validation report](F07-VALIDATION.md), `tests/test_f07_expressions.py` and `tools/evaluation/f07_api.py`. Private exact evidence/source freezes: `build/f07-implementation-20260914/`. Twenty-four API tuning responses at Luna low cost $0.010754 under the newly authorized $0.30 aggregate cap; carry that spend forward. Dataset replay exposed poor mouth-corner recall; extraction prompt candidate produced an attribution error. No release or human-test clearance is claimed. The final 144-response design remains pending.

Latest F07 correction: **278 passed** (`tests-clock-correction.xml`), extraction candidate reverted, and actual tool-disabled **Opus 5 only** follow-up cleared P1 development (`clock-review.json`). Earlier failures/reviews remain preserved. [Participant script](F07-MANUAL-CHECK.md) has remaining consent/budget/evidence setup requirements; no human outcome or final release gate is claimed passed.

Run offline checks on Windows: `.venv/Scripts/python.exe -X utf8 -m pytest -q`.

Historical experiment scripts are in `build/`. Many execute paid inference immediately on import or launch, use fixed output paths, contain old prompt versions or reference historical budgets. Read them first; use a fresh output directory and a newly applicable budget for API mode. Do not import a paid runner to reuse its helpers. Tests in `tests/` are the maintained application checks, including fixture replay and lifecycle checks.

## Suite map

DISFA local development probe (September 14): [dataset assessment](F07-DATASETS.md); `tools/evaluation/disfa.py`, `tests/test_disfa.py`; ignored exact sources/labels/probe evidence in `build/datasets/DISFA/` and `build/f07-disfa-20260914-v2/`. Three development subjects, 24 reserved, six windows, 582 local MediaPipe signal samples. This is downloaded signal-model processing, not new Luna inference or calibrated accuracy evidence.

F07 S0 preflight started September 14: [validation status](F07-VALIDATION.md), [timing annotation protocol](F07-TIMING-PROTOCOL.md), exact local evidence in `build/f07-preflight-20260914-033817/`. Source baseline and media timestamps/hashes preserved; independent expression annotations are missing. No F07 application implementation, model evaluation, human testing or review pass is claimed.

Later September 14: [dataset feasibility and seven assistant-authored podcast point annotations](F07-DATASETS.md). The user authorized this provisional route before implementation; independent timing remains unverified rather than blocking code start. No comparative Luna inference, dataset download or human validation was performed.

| Coverage | Report | Scripts / artifacts |
|---|---|---|
| F05 transcription, media and live validation | F05-VALIDATION.md; F05-LIVE-TEST-SCRIPT.md | tests/ and fixture instructions in README.md |
| F06 controlled models, policies, budgets and UI | F06-VALIDATION.md; F06-MANUAL-TEST.md | build/f06-controlled-model*.json; build/f06*correction*; tests/ |
| Paced transcript, indirect memory selection | F06-LIVE-FEED-REPORT.md | build/f06_live_feed*.py; build/f06-live-feed*.json |
| Job loss, vague rent/tenure cues every 4 seconds | F06-LOST-JOB-WALKTHROUGH.md; F06-VAGUE-JOB-4S.md | build/f06_lost_job*.py; build/f06-lost-job*.json |
| Bereavement, job loss, resignation relief, awards, exams | F06-VARIED-MEMORY-REPORT.md | build/f06_implicit_variety.py; build/f06-implicit-variety-results.json |
| Dynamic cadence, transcript context, six prompt variants | F06-PROMPT-COMPARISON.md | build/run_dynamic_api_audit.py; build/evaluate_1300_prompts.py; build/run_1300_live_replays.py; build/run_context_ablation.py; build/dynamic-api-audit-20260913/; build/prompt-1300-*/ |
| Full old/new prompt regressions and memory blend | F06-NEW-PROMPT-REGRESSION.md; F06-MEMORY-PROMPT-BLEND.md | build/run_new_prompt*.py; build/run_memory*blend*.py; corresponding build/*regression* and *blend* folders |
| Actual calls, guidance restart, visible replay | F06-MANUAL-TEST.md and relevant reports | build/f06_monitor_test.py; build/replay_logged_call_ui.py; build/live-test-*/events.jsonl; build/live-call-fixes-20260913/ |
| Ask Memory, natural questions, older/newer events | F06-ASK-HISTORY-TEST.md | build/evaluate_ask_history.py; build/ask-history-20260913/ |
| Detailed memory extraction and summary-only replay | F06-MEMORY-CREATION-AUDIT.md; F06-POST-CALL-CONTEXT-TEST.md | build/test_memory_scope.py; build/regenerate_replay_review.py; build/memory-scope-20260913/ |
| Luna/Terra, actual paced replay and split pipeline | F06-LUNA-TERRA-COMPARISON.md | build/compare_luna*.py; build/luna-comparison-20260913/ (corpus, exact inputs, outputs, accounting, assessments) |
| Subscription-funded agent/API comparison | F06-SUBAGENT-API-COMPARISON.md | build/subagent-model-comparison-20260913/ (3 blinded cases, baselines, actual Luna/Terra answers, check.py) |
| Offline small models, full regressions and timed/UI replay | F06-LOCAL-MODEL-COMPARISON.md | tools/evaluation/; build/local-model-comparison-20260913/ (completed: 1,023 returned local requests, 268 application tests) |
| Prepared synthetic provider comparison, NOT executed | No results yet | build/free-model-comparison-20260913/synthetic-paired-cases.json |

All report paths above are relative to docs/. The artifact manifest described below enumerates exact historical filenames and hashes, including reports, test sources, scripts and saved results, rather than relying on this table alone.

## Reproduce and extend

1. Establish model test method with the user if unspecified. Separate ordinary offline checks from new inference. For API mode confirm the applicable budget; for local mode distinguish no API fee from hardware/runtime costs.
2. Freeze the transcript available at each checkpoint, approved memory candidates, speaker IDs, exact prompt and schema. Judge expected behavior using only evidence available then. Keep expectations hidden from responding models. Distinguish failure to retrieve a candidate from failure to use a supplied candidate.
3. Replay identical inputs for a model-only comparison. Use production retrieval/cadence for integration tests and label them separately. Reuse saved Luna/Terra baselines only when inputs and prompts match; don't mix old and new prompt results as if model were the only variable.
4. Score relevant/irrelevant memory selection, temporal disambiguation, topic changes, speaker attribution, emotional calibration, useful user-style replies and waiting actions, repeated questions, evidence IDs, summary coverage and specific transcript-grounded memories. Save manual mismatches as well as automatic schema checks.
5. Use summary/memory-only replay when testing post-call changes; skip mid-call analysis expense. Paced replay must log actual arrival/request/response/delivery times; an accelerated batch is not a live latency measurement.
6. Save a new dated results directory, source scripts, complete configuration and report; update this index for a new method. Never overwrite baseline files or silently approve test memories in the user's real database.

## Offline Ollama evaluation

An explicit offline/local request selects this method; it is not a paid API or subscription-agent test. Run only one inference job at a time when comparing latency. The Windows helper `tools/evaluation/Start-LocalEvaluation.ps1` starts a separate hidden, cloud-disabled server at loopback port 11436. Download the chosen weights using Ollama; the evaluation adapter refuses remote models and undersized context. Model downloads require internet, inference does not.

Use a fresh `CALL_HELPER_LOCAL_EVAL_DIR` environment variable for a new experiment, especially after changing prompts, source or model digests. The default points to the preserved 13 September experiment and resumes existing IDs; it must not be mistaken for a fresh rerun. Keep the private historical Luna corpus available before preparing pairs.

```powershell
$env:CALL_HELPER_LOCAL_EVAL_DIR = "build/local-evaluation-new-run"
.venv/Scripts/python.exe -X utf8 tools/evaluation/local_models.py --prepare
.venv/Scripts/python.exe -X utf8 tools/evaluation/prepare_local_challenges.py
.venv/Scripts/python.exe -X utf8 tools/evaluation/prepare_local_coverage.py
.venv/Scripts/python.exe -X utf8 tools/evaluation/check_local_harness.py
.venv/Scripts/python.exe -X utf8 tools/evaluation/local_models.py --model gemma3:4b --phase full
.venv/Scripts/python.exe -X utf8 tools/evaluation/local_models.py --model gemma3:4b --phase coverage
.venv/Scripts/python.exe -X utf8 tools/evaluation/local_models.py --model gemma3:4b --phase new
```

Replace the model deliberately. `--readable`, `--compact`, `--brief` and `--think` are separate experimental configurations, not equivalent model-only comparisons. `--output-multiplier` changes the generation allowance, including thinking tokens. All actual instructions/inputs and raw responses are retained.

`local_paced.py --model MODEL --recorded recent` (or `earlier`) uses original finalized-turn timing and historical memory candidates. `--synthetic` uses four-second turns and fresh BGE retrieval. `local_visible_replay.py --model MODEL` opens the actual Tk app against a copied database with saved transcript/evidence and logs visible text; it blocks external network connections and deliberately skips post-call inference. `local_resource_check.py --model MODEL` compares GPU, CPU and GPU-plus-Whisper. These runners also accept the prompt-variant flags. The resource runner requests `num_gpu=0` but checks actual placement: multimodal projector buffers can still occupy GPU memory. For strict CPU measurements, start the separate server with `Start-LocalEvaluation.ps1 -Cpu` in a fresh PowerShell process, then run `local_cpu_only_check.py`; it asserts zero model GPU allocation at port 11435. Run resource and CPU probes sequentially, not alongside another inference job. `audit_local.py` and `summarize_local.py` inspect saved results without inference; automatic indicators are not a substitute for manual semantic review.

## Private history preservation and cross-device access

`evaluation-history/f06-history-20260913.zip` is a private local snapshot of historical build artifacts plus docs/, tests/, plans/, native/, application Python source and root project configuration at preservation time. It excludes credentials, installed dependencies, Python caches and wheel/build duplicates. `evaluation-history/manifest.json` lists archive entries, sizes and SHA-256 hashes. `evaluation-history/` is Git-ignored because it contains private call transcripts and test databases/media.

Future sessions on THIS checkout can use the originals or archive. A fresh Git clone or a different computer DOES NOT receive these ignored files automatically. Copy the private evaluation-history folder along with the project using the user's private transfer method; do not publish it. Extract the archive into a separate directory first to inspect/recover the historical source and build paths. Do not overwrite a current checkout with the historical source snapshot. External model caches and large media dependencies outside build/ must still be provisioned using README.md.

The root AGENTS.md, this index and reports are ordinary repository files eligible for version control. They have been written locally; no commit, push or cross-device transfer is implied.


The completed offline comparison is additionally preserved in `evaluation-history/f06-local-models-20260913.zip`, with SHA-256 entries in `evaluation-history/local-models-manifest.json`. It includes the new local runners/results, full visible replay and smoke logs, current source, and available earlier-manifest artifacts. The earlier archive is retained unchanged. Do not treat 1,023 returned requests as independent scenarios: the report separates paired, screening, timed, resource and failed-output counts.


## Expanded agent/API comparison (completed pre-live checks)

`build/agent-api-expanded-20260913/` freezes 258 recorded Luna API cases plus twelve new cases from the offline-model comparison. `inputs/` contains blinded requests/schema; the manifest maps case IDs and hashes. The isolated queue deduplicates exact requests (226 representatives for258 old cases). `isolated-dispatch.json` records real agent model/effort/fork settings and exact-duplicate reuse. New cases258–269 were each answered by a fresh Luna low agent. Agent output limits are textual instructions, not provider-enforced structured decoding or token caps.

A 96-answer batched pilot is retained separately in `luna-NNN.json`; it demonstrated cross-case memory leakage and must not be used as the isolated-agent baseline. Use `luna-isolated-NNN.json` for the fresh-agent results. `collect_agent_comparison.py` assembles saved answers without inference; set `CALL_HELPER_LOCAL_EVAL_DIR` to this expanded directory to run the existing offline audit afterward. Check completion status before drawing conclusions.

`agent_api_new_cases.py --api-cap USER_APPROVED_CAP` invokes only Luna low and only the twelve new frozen cases, with no retries and a fresh output file. Never launch it without the current user's API authorization and applicable cap. Existing API answers are reused; there is no reason to pay for them again. `check_agent_api_runner.py` exercises cap-before-dispatch, model restriction and uncertain-billing retention using mock responses, without reading credentials or making network calls.


September14 completion: all258 historical agent answers,12 new agent answers and6 revised agent answers are preserved.24 fresh Luna low API requests cost an estimated $0.02118703 under the $0.03 aggregate cap. The68 local-only extension was dropped by the user. Final source passes270 tests; Claude Sonnet static review and dispositions are in F06-AGENT-API-EXPANDED.md. `revised/` and `final-check/` preserve changed prompts, exact outputs and separate cumulative ledgers; never rerun their paid scripts in place. The remaining step is the user's live call, with known semantic limitations called out in the report.

A private snapshot is in `evaluation-history/f06-pre-live-luna-20260914.zip`, with hashes in `evaluation-history/pre-live-luna-manifest.json`. This archive supplements the earlier history/local archives and is not automatically synced by Git.

F06 closure (2026-09-14): user accepted the current work and known Luna limitations as complete for now and authorized publication. Another live call is optional future work. F07 remains unstarted. See PLAN.md for the explicit closure exception and Trello for the release SHA.


## September 15 supplied-evidence API comparison

See [MEMORY-ANSWER-COMPARISON.md](MEMORY-ANSWER-COMPARISON.md): 24 existing fictional cases, two fresh Luna low API responses each, $0.02322885 estimated total under the explicit $0.30 cap; 48 matching historical Gemma/Qwen outputs reused. The current assistant supplied frozen reference answers and non-blinded judgments. This is not a retrieval, held-out, live-user or Hindsight completion gate.

Exact evidence is private in `build/memory-answer-comparison-20260915T093115Z/`. Do not rerun that directory. `memory_answer_comparison.py --api-cap USER_APPROVED_CAP --run-dir FRESH_PREPARED_DIRECTORY` requires 24 frozen numbered inputs and a reference file, uses the shared reservation ledger, disables retries, and rejects an existing result/dispatch lock. It does not resume interrupted runs or prepare a new case set. An interruption retains its reservations; never reset the ledger to restart. The standing cap for explicitly requested Luna low API testing is $0.30 total unless overridden by the user.

Run `.venv/Scripts/python.exe tools/evaluation/check_memory_answer_comparison.py` for self-contained offline cap/no-retry/overwrite checks. This sends no requests and needs no private case archive. See the report for review and publication status.
