# Local memory evaluation and bounded improvement

Date: 2026-09-15  
Status: implementation handoff; no experiments run by this planning session.  
Objective: determine whether a free, fully local memory method improves Conversation Copilot enough to justify a change. Keeping the current implementation is a successful outcome when challengers do not earn their complexity.

## Scope and standing decisions

- This is a bounded evaluation alongside F07, not a new closure requirement for F01–F06 or permission to replace the product's memory architecture.
- Preserve F07's September 23 tuning freeze and September 27 completion target, F08's October 1 Windows delivery, and F09's later macOS work. No memory migration is a dependency of those deadlines.
- Production remains SQLite/FTS5/BGE-small with Luna low for guidance, Ask Memory and post-call review. The experiment may use a local LLM without reopening the broad F06 language-model competition or changing those settings.
- Qualifying alternatives have no subscription, provider quota or per-request API fee. All extraction, embeddings, reranking, storage and answering used in the experiment must operate locally. Hardware, electricity, disk space and finite model context remain costs/limits.
- No paid API or subscription-agent model comparison is authorized by this plan. Historical API caps are irrelevant. The accompanying implementation prompt explicitly selects local inference for this experiment; without that instruction, follow AGENTS.md and clarify the method before model-dependent runs. BGE embedding computation also counts as model inference.
- Use fictional fixtures by default. Do not load the real user database into a challenger, upload private logs, or turn generated facts/summaries into approved product evidence.
- Work in an isolated checkout or experimental files. The current working tree contains active F07 changes and unrelated personal PDFs. Preserve them; do not reset, broadly stage, or commit another session's work. A Git worktree excludes uncommitted changes: record or privately snapshot any working-tree source required for the baseline rather than silently testing an older commit.

## What the repository establishes

Read AGENTS.md, CONTEXT.md, PLAN.md, docs/TESTING.md and the latest F07 status before work. Later dated status takes precedence over older historical "not started" paragraphs.

| Existing surface | Reuse and implication |
|---|---|
| `conversation_copilot/memory.py` | `MemoryStore.retrieve`, `memory_retrieval_inputs`, `memory_semantic_input`; SQL eligibility first, lexical/date/semantic ranking, reciprocal-rank fusion, bounded reviewed links and ambiguity handling already exist. Do not reimplement these as a new framework. |
| `conversation_copilot/semantic.py` | FastEmbed BGE-small, 384 dimensions, two threads, offline loading; vectors stored with revisions in SQLite. Query embedding failure can fall back, so record whether semantic search actually ran. |
| `conversation_copilot/ask_memory.py` | Local source-based Ask plus `cloud_sources` and source validation. Cloud Ask already packs all eligible selected-contact evidence when it fits; it ranks when it does not. Test both small and overflowing evidence sets before claiming ranking solves Ask problems. |
| `conversation_copilot/f05_evaluation.py`, memory/Ask tests and assets | Reuse fixture conventions and relevant safety assertions, not historical paid entry points. Some evaluation modules contain both offline and paid operations; inspect before importing/executing. |
| `tools/evaluation/local_models.py`, `Start-LocalEvaluation.ps1` | Reuse validated loopback/cloud-disabled patterns. Their default historical output paths and server logs are unsafe for a new run; provide fresh paths and avoid launching another server on an occupied port. |
| `docs/F05-VALIDATION.md` | The small indirect employment test improved from 0/3 lexical hits to 3/3 with local embeddings. Mem0/Graphiti rejection recorded architectural reasons, not a controlled quality victory over them. |
| `docs/F07-VALIDATION.md` | Relevant memories were supplied in the recent semantic requests. Reported omissions/misinterpretations are evidence-use findings; retrieval recall remains unmeasured there. |
| `docs/F06-LOCAL-MODEL-COMPARISON.md` | Preserve all prior local-model results. Recorded hardware: Ryzen 9 3900X, RTX 4060 Ti 8 GB, about 64 GB RAM. Reconfirm current hardware; do not assume a 20B model fits in VRAM or runs acceptably beside transcription. |

## Why these candidates

Hindsight's paper reports 83.6% LongMemEval accuracy with GPT-OSS-20B for retention and answering, versus 39% for the same full-context model. It is a useful hypothesis for temporal and multi-call recall, not a benchmark against our hybrid retriever. Some cross-system comparisons use external scores/different judges, and the paper's retrieval-budget description is incomplete. Do not promise reproduction on this hardware. [Paper](https://arxiv.org/html/2512.12818v1), [implementation](https://github.com/vectorize-io/hindsight).

Mem0's advertised 92.5/94.4 LoCoMo/LongMemEval scores explicitly include proprietary managed-platform optimizations. They do not establish free SDK performance. A limited independent Graphiti/Mem0 study found no statistically significant accuracy difference; it does not establish equivalence. [Mem0](https://github.com/mem0ai/mem0), [comparison](https://arxiv.org/html/2601.07978v1).

Start with these arms, at most three:

1. **A — Current baseline:** frozen actual production retrieval, including query construction, eligibility, source packing and ambiguity behavior.
2. **B — One small local change, conditional:** only after baseline diagnosis identifies a repeated retrieval failure. Prefer a correction to existing query/date/ranking logic. Consider a small local cross-encoder only if relevant items enter the candidate pool but rank poorly. A reranker cannot recover evidence never retrieved. Do not add another fusion algorithm: one already exists.
3. **H — Hindsight, experimental only:** one pinned version and one local configuration in a separate environment/database. No production dependency, migration, service startup or UI option. Mem0 and Graphiti are deferred; do not silently substitute them if Hindsight is infeasible.

## Sequential implementation slices

### S0 — Freeze scope, source and feasibility

Record the source commit plus hashes/patches for relevant uncommitted files, hardware, installed runtimes/models, available RAM/VRAM/disk, and current memory limits. Inspect saved results without inference first. Create a unique ignored `build/memory-evaluation-<timestamp>/` directory; fail rather than overwrite an existing run.

Inspect the pinned Hindsight license and all model licenses, local provider support, database/runtime requirements, telemetry and default endpoints. Ensure there are no hidden hosted embeddings, rerankers, judges or extraction calls. Keep dependencies out of the application's `.venv` and `pyproject.toml`. Do not install Docker/WSL or enable Windows features merely to rescue the experiment; report that prerequisite if it is missing and no simple supported route exists.

Use one already downloaded suitable local instruction model where possible, chosen from saved context/quality evidence. Freeze its digest, quantization, context, generation limits and reasoning configuration for every answering arm. A different model from the Hindsight paper is a project-specific comparison, not a paper reproduction. Do not initiate a 20B download or a model tournament by default.

**Gate:** source and configuration manifest, actual local-only configuration, bounded setup path and frozen evaluation defaults. Hindsight setup gets at most four hours of engineering effort; infeasibility becomes a documented result. Continue baseline diagnosis even if H cannot run.

### S1 — Failure taxonomy and frozen cases

Prepare 24 development families and 40 new held-out families: eight categories with three development and five held-out families each.

1. Direct fact, preference, shared reference and commitment recall.
2. Indirect wording, paraphrases and topic changes.
3. Dated plans, corrections, supersession and historical versus current questions.
4. Questions requiring evidence from multiple calls, including approved summaries.
5. Two plausible events or people: preserve alternatives or ask for clarification.
6. No relevant evidence and tempting but irrelevant reminders.
7. Contact/lifecycle/privacy boundaries: wrong or unassigned contact, pending/rejected/deleted evidence, correction, permission revocation and stale search derivatives.
8. Speaker ownership and garbled/uncertain wording: avoid inventing who did what.

Use past F05/F06/F07 families only for development/regression; paraphrases of exposed families do not become fresh holdout. Held-out contacts, event histories and situations must be distinct. Include small histories and histories exceeding the existing 4,700-token Ask evidence allowance; freeze distractor counts and lengths. Public benchmark subsets are optional context, not an extra benchmark project or substitute for these cases.

For each family freeze source turns, timestamps/time zones, speaker roles, approved memory revisions/summary statements, allowed evidence IDs, required evidence groups, acceptable alternatives, prohibited claims and expected action. Some questions allow several equally valid supporting sources: score those equivalence groups rather than exact wording. No facts from a later checkpoint may enter an earlier index. Treat lifecycle mutations as a sequence and test retrieval both before and after the change.

Keep expectations outside model requests and retrieval corpora. Development labels may guide the bounded fix. Held-out labels are for scoring only; do not tune after seeing its results. Human review must resolve uncertain annotations before final scoring; unresolved items remain explicitly unscored and cannot support a pass.

Assign failures to **capture/extraction**, **eligibility**, **candidate retrieval**, **ranking/packing**, **answer/evidence use**, or **reminder timing/usefulness**. Record multiple contributing causes when supported. Seeing a relevant memory in a saved prompt rules out its retrieval omission for that request.

**Gate:** reproducible fixtures and scoring checks that catch missing evidence, stale/wrong-contact leakage, and denominator mistakes without invoking models.

### S2 — Matched retrieval experiment

Run A first. Log query construction, eligible evidence, candidate IDs/ranks, final packed evidence, ambiguity/status, exact source revision and semantic availability. Do not fake a retriever improvement by giving a challenger more history, a longer excerpt or future evidence.

Run H on the same approved evidence, with original source IDs and contact boundaries preserved. Its extraction/entity linking is part of the candidate system and must be timed and saved. Do not also give H raw unreviewed conversations that A cannot search. If H derives or merges facts, retain links to every supporting approved source; unsupported synthetic facts cannot become answer evidence. Report this as a representation-plus-retrieval comparison where applicable, not a pure ranking ablation.

Map H results back to canonical approved source excerpts and revalidate eligibility before packing. Generated graph text is not a substitute for approved evidence. Retain raw search results and mapping failures so the adapter cannot hide leakage. Contact deletion/correction must remove or invalidate affected vectors, facts, summaries and graph derivatives, including warm caches. If the experimental integration cannot do this safely, mark it ineligible for adoption.

Compare live retrieval at the existing maximum four memories and the same current excerpt/token budget. For Ask, compare within the current 4,700 evidence / 6,300 total input / 1,000 output limits; include the baseline's complete-history path. Log truncation and final evidence at the model boundary, not just pre-packing recall.

Create B only for a demonstrated development failure, with one focused runnable regression check. Permit at most two development rounds total and one conceptual fix. No held-out tuning. Stop adding candidates when A already meets the gates and remaining errors occur after retrieval; the report may recommend retaining A without further challenger inference.

**Gate:** paired retrieval metrics and error attribution, with no production behavior changed.

### S3 — Separate retrieval benefit from answer quality

For Ask, use one fixed local answer model, prompt, schema, sampling settings and output budget for every arm. Only the supplied evidence changes. Use fresh stateless requests, no conversation-history carryover. Preserve the product's role labels and source rules; identify the harness as a local diagnostic, not deployed Luna validation.

Use the first 20 held-out families (the four answerable categories) for an additional **oracle-evidence diagnostic**: supply their minimal sufficient canonical evidence to the same model. If the answer still fails, a new retriever alone has not fixed that case. Do not compare locally generated answers against old Luna answers as if the memory engine were the only difference.

Run two independent answers per final case/arm. Count invalid outputs, timeouts and refusals in attempted-request denominators; do not replace them silently. A duplicate replay is not an independent response. Use exact factual/source checks where possible and human review for correctness and useful versus intrusive reminders; another model judge is not required.

For live guidance, designate twelve of the forty held-out families before freezing as additional matched turn-checkpoint tests: eight actionable and four requiring waiting/clarification. Run the same local model twice per surviving arm, with expected "mention / wait / clarify" behavior. These are additional requests, not additional independent families. Local answer-model quality is preliminary; better retrieval alone does not establish that Luna will give better reminders. Do not change Luna prompts or perform new Luna requests here. A later product adoption decision may require a separately selected and budgeted Luna check.

Plan the request ledger before dispatch: at most 72 first-round development answers, 24 changed-arm second-round answers, 240 held-out Ask answers, 40 oracle answers and 72 live-checkpoint answers. That leaves 52 of the 500-request cap for Hindsight ingestion and failures. Reduce optional development work before reserving final requests; never consume the final reserve on ingestion or retries. If the measured chunking requirements do not fit, stop H as out of this experiment's budget rather than truncate its evidence silently.

**Gate:** evidence that improvement reaches answers/useful reminders, or a clear report limiting the finding to retrieval.

### S4 — Resource checks, review and conclusion

Separate indexing, warm retrieval, cold start and generation. Measure p50/p95 wall time, peak process-tree RAM, incremental service RAM, CPU, VRAM, model/index disk size, input/output tokens and all local inference calls. Include databases, model servers and Docker/WSL processes where relevant; Python-only memory is not the full footprint. Report zero provider spend separately from unmeasured electricity cost.

Time at least 100 warm retrieval queries from fixed fixture replays per surviving arm and one cold start. These repetitions measure performance, not independent accuracy. If claiming live suitability, run one 10-minute paced synthetic replay with existing transcription/visual load and compare its resource/latency impact against baseline sequentially. Do not rerun old F01–F06 closure suites to establish status.

Before asking the user to assess outputs or try a changed behavior, obtain the project's actual tool-disabled, read-only Claude Opus 5 preliminary review of the harness/diff, evidence and limitations; fix accepted findings and review corrections. Give the user a short shuffled A/B output packet and a manual script covering successful recall, ambiguity, no-match, correction/deletion and contact switching. Record actual assessments; silence is not a pass. Obtain the fresh final Opus 5 review after testing/corrections. If unavailable, report the missing review; never substitute silently. These are code/QA reviews, not memory-model benchmark responses.

Conclude with exactly one recommendation: **retain current memory**, **propose the bounded local fix**, or **propose a separate Hindsight integration**. Separate Ask-only suitability from live suitability. A winning experimental adapter does not authorize a database migration or default switch. Keep any proposed product change reviewable as a separate patch and preserve the baseline.

Publish only sanitized harness/fixtures/report after required review and corrections, with an explicit file list. Follow the repository's commit/push workflow and verify the reviewed commit on GitHub against local and remote branch pointers; never force-push or include unrelated work. If active F07 work prevents clean integration to main, preserve the reviewed branch and report the pending merge rather than claiming main publication. Update `docs/TESTING.md` with the new method/report when implemented. Keep roadmap changes high-level; do not create a new numbered feature or duplicate F07 Trello cards for this diagnostic.

## Numerical defaults to freeze before tuning

These are proposed engineering decision thresholds for this experiment, not existing measured results or user-approved F07 gate changes. Record them before development runs; any revision must precede final holdout access and explain its reason.

| Measure | Decision threshold |
|---|---|
| Eligibility, provenance and deletion | Zero wrong-contact, deleted, unapproved, stale-current or unauthorized cloud-export sources; every returned source validates against the current canonical revision. Sensitive sources remain eligible for genuinely local use. |
| Recall@4 | At least 85% macro recall of required evidence groups on answerable live cases; report multi-source completeness separately. An ambiguous candidate can count as retrieved without being a correct confident selection. |
| Packed Ask evidence | At least 85% of answerable questions retain every required evidence group within the equal budget. Report small-history and overflowing-history results separately. |
| Candidate relevance | At least 85% of returned candidates are relevant or explicitly acceptable alternatives. Show total returned count and answerable coverage, so returning nothing cannot pass. |
| Abstention/clarification | At least 85% correct decisions on insufficient/ambiguous cases; zero unsupported high-confidence ownership claims. Show counts, not percentages alone. |
| Answer usefulness | At least 85% correct supported answers on answerable Ask cases; at least 80% useful displayed reminders, at most 5% incorrect/intrusive reminders, and at least 75% coverage of actionable reminder opportunities. Evaluate each repeat and family-level results. |
| Meaningful uplift | At least 10 percentage points on the targeted retrieval/answer metric and at least three distinct held-out families rescued versus A, with no increase in incorrect answers or safety failures. Report all paired regressions; no category may lose more than one family. Small sample results remain provisional. |
| Live retrieval | Warm p95 at most 500 ms and added p95 at most 100 ms versus A; additional persistent memory-service RAM at most 500 MiB. No more than 10% transcription p95 slowdown during the paced replay. |
| Ask-only option | Retrieval p95 at most 1 second; local answer p95 at most 15 seconds; memory services add at most 4 GiB RAM excluding the separately reported answer model. Failure of live limits permits an Ask-only recommendation, not a live pass. |
| Hard resource stop | No out-of-memory/system instability; retain at least 8 GiB available system RAM. Experiment process-tree RAM at most 24 GiB. Record actual VRAM allocation and contention; never infer fit from parameter count. |
| Usage | Exactly $0 provider/API spend. Maximum 500 local LLM requests across ingestion, development, oracle and held-out answers, including failures; maximum 4 hours of cumulative model-run wall time. Embedding/reranker work is recorded separately and still counts toward runtime. No automatic retries beyond the cap. |

Historical F07 thresholds remain unchanged. A challenger that only improves a leaderboard-style metric but fails product safety/usefulness/resource gates is not adopted. Held-out failure ends tuning for this experiment; any later attempt requires genuinely fresh cases and a new bounded plan.

## Timebox and fallback

Budget at most eight engineering hours for this diagnostic, including at most four for Hindsight setup. Prioritize S0/S1, A diagnosis and one supported small fix; stop unsupported infrastructure work early. Before September 23, spend this time only where it does not interrupt the active F07 sequence. After that freeze, defer unfinished challenger work until after the October 1 Windows demonstration. Preserve partial evidence and report inconclusive results honestly; do not reduce gates to meet the timebox.

If a shared local model cannot answer the oracle cases adequately, finish the retrieval report and state that end-to-end uplift is unestablished. Do not launch a search for a stronger model. If Hindsight cannot run entirely locally within the setup/resource limits, record it as infeasible here, not inaccurate. If no repeatable retrieval deficit appears, keep SQLite/FTS5/BGE-small and direct remaining calibration work to evidence use under the existing F07 plan.

## Deliverables and evidence preservation

- Small standalone evaluation runner under `tools/evaluation/`, a focused offline harness check and sanitized fictional fixtures; prefer extending suitable existing helpers over adding a general plugin framework.
- `docs/LOCAL-MEMORY-EVALUATION.md`: configuration, paired counts/metrics, individual regressions, resources, applicability to Ask/live guidance, limitations, review/manual outcomes and explicit recommendation. Missing stages must be labeled.
- A unique ignored run folder containing source snapshot/hashes, exact corpora/prompts/schemas, raw outputs, source mappings, expectations, separate assessments, complete configuration/model/license provenance, timings, token counts, request ledger and errors. Preserve original Hindsight output even when canonical-source filtering rejects it.
- Optional bounded product patch only when justified, kept separate from this evaluation's default behavior; no automatic migration, new user-facing engine selector or production LLM change.
- Reviewed publication references for shareable artifacts; never commit private databases, conversations, output archives, model weights or credentials.

This planning session writes this document only. It does not install dependencies, run inference, alter production code, migrate memory, create Trello work or publish a commit.
