# Evaluation handoff and reusable history

Read ../AGENTS.md for the standing API-versus-agent choice rule. This index is project-wide, not chat-specific. No inference is authorized by merely reading a report or running a historical script.

## Start here

Run offline checks on Windows: `.venv/Scripts/python.exe -X utf8 -m pytest -q`.

Historical experiment scripts are in `build/`. Many execute paid inference immediately on import or launch, use fixed output paths, contain old prompt versions or reference historical budgets. Read them first; use a fresh output directory and a newly applicable budget for API mode. Do not import a paid runner to reuse its helpers. Tests in `tests/` are the maintained application checks, including fixture replay and lifecycle checks.

## Suite map

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
