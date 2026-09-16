# Local memory evaluation — implementation checkpoint

Date: September 15, 2026. **Incomplete experiment; no adoption or release pass.**

Recommendation: **retain current memory** while the remaining gates are unresolved.
Luna low, production SQLite/FTS5/BGE-small, and the active F07 changes are unchanged.
This checkpoint implements historical evidence preservation and initial feasibility;
it does not claim completion of the [evaluation plan](../plans/local-memory-evaluation.md).

## Frozen baseline and limits

Private evidence: `build/memory-evaluation-20260915T083732Z/` (Git-ignored).
The baseline is commit `28e843f3e2efbfa5f494f8c40c759705e720bfe1`
**plus the actual working-tree source**, including the pre-existing F07 changes.
The folder preserves 119 source/configuration/test/report files with SHA-256 hashes,
the working-tree patch and initial status. The one-off builder used Git's ignored-file
filter and an extension allowlist that excludes PDFs but permits JSON/TXT/TOML. A scan
of all 119 manifest paths found no credential-shaped filenames or PDFs; this is not a
secret-content scan and the reviewer has not independently verified that exclusion.
The recorded commit identifier is metadata, not proof that every frozen byte
matches that commit (the working tree is intentionally different).

`frozen-defaults.md` preserves the plan's entire numerical-default table before tuning.
`ledger.json` preserves the 500-request/4-hour model-runtime caps and original request
allocations. Engineering is limited to eight hours, with four hours maximum for Hindsight
setup. September 23/27 F07 and October 1 F08 deadlines remain unchanged.
Accounting is currently manual: no programmatic inference/runtime limiter exists yet.
The source snapshot was made by an initial one-off preparation command; the maintained
runner verifies it but does not yet create source freezes. Extra non-cache files in the
snapshot are rejected. Private folders carry explicit do-not-publish markers.

| Configuration | Frozen value / observation |
|---|---|
| CPU / system RAM | Ryzen 9 3900X; 63.91 GiB total, 49.84 GiB available at preflight |
| GPU | RTX 4060 Ti; 8,188 MiB VRAM, 814 MiB used at preflight |
| Free disk | About 794 GiB on C: at preflight |
| Local answer model | Existing `qwen3.5:4b`, Q4_K_M; 3,389,983,735 bytes |
| Model digest | `2a654d98e6fba55d452b7043684e9b57a947e393bbffa62485a7aac05ee4eefd` |
| Answer settings | 16,384 context, 1,000 output ceiling, temperature 0, seed 42, thinking disabled; two stateless responses planned |
| Server | Ollama 0.31.2, `127.0.0.1:11436`, `OLLAMA_NO_CLOUD=1`, one parallel request/model |
| License | Qwen's exact Apache-2.0 license returned by local model metadata is preserved |

The Qwen choice uses prior Ask evidence, not a new tournament: the historical report
records 42 schema-valid Ask responses and 1.71-second median, alongside factual and
ownership errors. Neither that timing nor model metadata establishes this experiment's
answer-quality, context-fit, or coexistence gates. No new LLM answer has been dispatched.
The earlier 42 schema-valid Ask responses are saved **Qwen responses**, distinct from
the 42 historical **Luna request rows** counted in the corpus below.

## Existing transcripts and tests reused

The new standalone [runner](../tools/evaluation/memory_evaluation.py) copies the named
historical evidence into the fresh ignored folder and checks hashes. It refuses an
existing evidence destination and does not import historical inference runners.
The two original call logs also pass chronological checks: every saved offer uses
already-finalized turn IDs. This validates saved inputs; it is not a new paced replay.
Preservation makes a second private copy of 17,952,357 bytes of historical evidence.
Both copies are retained locally for provenance; no automatic cleanup or external sync
is configured. The run root and historical-copy directory carry private markers.

| Historical evidence | Observed counts |
|---|---|
| Saved model corpus | 258 rows, 226 canonical-JSON request representations, 32 duplicate rows |
| Component counts | 200 guidance, 42 Ask, 12 summary, 4 extraction |
| Supplied evidence | 82 guidance requests contain memories; all 42 Ask requests contain evidence |
| Recent recorded call | 88 finalized turns, 84 offers, 6 offers containing memory |
| Earlier recorded call | 33 finalized turns, 32 offers, 30 offers containing memory |

Saved candidates are not the full eligible database. Their absence cannot establish
whole-store retrieval failure. Their presence also does not establish relevance.
The F07 report's supplied-memory findings remain evidence-use findings.
Both call logs contain the memory field in every offer: the remaining 78/84 and 2/32
offers explicitly contain no memory. These are different calls, not a paired change in
retrieval performance. In the model corpus, 118 guidance inputs omit the optional `m`
field; the audit labels that absence separately and emits observed payload keys.
These counters concern the named `m`/`evidence` fields, not all possible historical
field aliases. Object key ordering is normalized for deduplication. JSON-string and
object inputs remain different representations; these are not byte-identity counts.
Eight historical files are copied and hashed; only the corpus and two call logs have
structural/content counters in this runner. Its inference flag declares the audit's
code path, not network instrumentation.

The existing **40-question fictional F06 fixture** was replayed against frozen source,
with outbound socket connections blocked and cached BGE loading forced offline.

This replay used a one-off command importing the existing `f06_evaluation.evaluate_local`
helper from frozen source. The external reviewer has not independently verified that
command or its socket guard. Exact saved results support the table; the new preservation
runner does not itself execute or certify this replay.
The inspected frozen helper opens a new `MemoryStore(":memory:")` for every case.
`default_database_path()` is used only to locate the existing BGE cache; the real
memory database is not opened by this replay. Fictional approvals stay in those
temporary in-memory stores.

| Existing development regression | Passed | Answerable-source recall |
|---|---:|---:|
| Lexical-only profile | 35/40 | 18/23 |
| Cached BGE profile | 40/40 | 23/23 |

These are 80 profile/check executions, **not 80 distinct families**. The 6.69-second
whole-replay wall time is conservatively charged as model runtime, including indexing,
queries and non-model work. The old helper's small-sample latency fields are preserved
privately but do not satisfy this plan's 100-query performance protocol.
The saturated BGE regression scores cannot serve as A's new S2 recall@4 baseline or pass
the new held-out 85% gate.

Affected maintained memory/Ask/summary checks: **106 passed in 8.54 seconds**, including
the initial evidence-harness check. A later focused check validates the additional
future-turn rejection. This does not reopen F01–F06 closure.
After review corrections, six focused harness checks pass. They cover missing/future
turns, duplicate encodings, missing evidence, ignored destination checks, traversal and
source-manifest corruption/extra files. Copy intent is journaled before each file copy,
so a partial run retains provenance and must use a fresh destination to retry.
The entire affected selection was rerun after the latest code corrections: **111 passed
in 7.44 seconds**. The real repository ignore rule is also exercised, alongside mocked
failure paths.

## Hindsight feasibility

Source pinned at `bef1e5ff3d61157b8207f8ad6b5a6777eac1c939`, version 0.10.0,
MIT license. Exact source and inspected-file hashes are private. The pinned
[installation documentation](https://github.com/vectorize-io/hindsight/blob/bef1e5ff3d61157b8207f8ad6b5a6777eac1c939/hindsight-docs/docs/developer/installation.md)
supports native Windows with embedded PostgreSQL (`pg0`). Docker is installed but its
engine was unavailable; that does **not** establish Hindsight infeasibility.

A dependency dry-run resolved in a separate experimental virtual environment.
No Hindsight dependencies were installed into the application environment, and no
Hindsight database/server or ingestion was started. The pinned configuration defaults
to OpenAI for LLM work, so its quick-start is unsuitable for this experiment.
It supports explicit Ollama and local embedding/reranking settings; tracing is disabled
by default. See the pinned
[configuration](https://github.com/vectorize-io/hindsight/blob/bef1e5ff3d61157b8207f8ad6b5a6777eac1c939/hindsight-docs/docs/developer/configuration.md).

H remains **unverified**, not inaccurate or ruled out. Before running it, finish the
exact local reranker/model-license freeze, local endpoint/egress checks, ingestion
request accounting including startup and background work, and canonical-source mapping.
No default cloud route, automatic retry, or uncounted consolidation call is acceptable.

## Remaining sequential gates

| Slice | Status |
|---|---|
| S0 | Source/defaults/history frozen; BGE offline path tested; local LLM runtime metadata verified. End-to-end Hindsight feasibility and model resource stops not yet verified. |
| S1 | 24 development and 40 distinct fictional held-out **drafts** saved privately, with 12 proposed live checkpoints. Drafts are not frozen/scored; annotation, lifecycle sequences, realistic turn ownership, historical-date coverage and equivalence-group checks remain. |
| S2 | New matched retrieval experiment not run. No B fix proposed from the old regression fixture. |
| S3 | Matched Ask, 40 oracle and live-checkpoint responses not run. No end-to-end uplift claim. |
| S4 | Complete resource measurements, human output assessments, fresh final Opus review and publication pending. No Ask-only or live suitability pass. |

Provider/API spend: **$0**. New local LLM requests: **0/500**. Embedding computation
is separately recorded; electricity, full process-tree peaks, cold/warm runtime and
concurrent transcription impact remain unmeasured. No paid/hosted/agent benchmark
model was used. Model downloads were not needed for the baseline.
Cumulative conservatively accounted model runtime is **6.69 / 14,400 seconds** so far.

Review and publication status will be recorded below. Do not ask the user to grade
outputs before the full relevant preliminary review clears. A review of this first
slice is not the complete S1–S4 preliminary or post-human gate. Nothing has been
committed or pushed; only reviewed, sanitized artifacts may be published.

### Initial actual review

Tool-disabled, read-only **Claude Opus 5** (`claude-opus-5`, firstParty, only model
reported) reviewed the first slice through the authenticated subscription. No benchmark
model or paid API was used. The review's reported token cost is not a new provider bill;
subscription review usage is separate from the local-model request ledger.

Accepted findings: distinguish declarative audit behavior from measured inference counts;
split missing/future-turn errors; expose absent payload fields; qualify exact-encoding
deduplication; explicitly exclude old fixtures from the new gates; disclose manual caps;
journal partial copies; fail missing history; test path/source checks; validate copied
paths; add private markers; disclose the one-off snapshot builder and reject extra files.
The original audit and ad hoc `historical-audit-v2.json` are retained. The revised runner
now reproduces these counts from hash-verified copies, checks for extra historical files,
validates guidance/Ask object payloads, and emits explicit zero counters. Its literal
stdout and `historical-audit-v3.json` supersede v2 as reproducible evidence. Extraction
and summary schemas are counted separately without assuming object-shaped input.
The latest `historical-audit-v6.json` emits observed offer/payload keys and canonical-JSON
counts. Versions v3, v4 and v5 remain preserved alongside the original and v2.
The earlier Python command bodies were reconstructed from the session transcript into
`executed-freeze-command.txt` and `executed-replay-command.txt`; hashes cover that
reconstruction, as recorded in `executed-command-provenance.json`. They were not rerun.
The replay text retains historical output paths and must never be rerun in place.

To re-audit without copying or overwriting history:

```powershell
.venv/Scripts/python.exe -X utf8 tools/evaluation/memory_evaluation.py build/memory-evaluation-20260915T083732Z --audit-history historical-audit-NEW.json
```

Actual tool-disabled **Claude Opus 5** returned **CLEAN for this private first-slice
checkpoint** in `slice-checkpoint-review.json`, after correction reviews. It explicitly
did **not** clear S0 completion, S1–S4, human testing or publication. Its remaining
non-blocking documentation notes are corrected here; test-hygiene notes remain in the
private review. This is not full preliminary or post-human clearance.
The candidate shareable file list is exactly `tools/evaluation/memory_evaluation.py`,
`tests/test_local_memory_evaluation.py`, `docs/LOCAL-MEMORY-EVALUATION.md`, and this
experiment's insertion in `docs/TESTING.md`. No file under the ignored run is publishable.

For an interrupted audit, the completed-copy manifest is written before parsing, so a
corrected runner can re-audit the copies. An interrupted copy retains its intent journal;
use a fresh run for another copy attempt. Malformed required keys fail with Python
exceptions; no parser recovery or silent skipping is attempted. Git is a required S0
prerequisite, including for the repository-ignore check.
The named historical evidence set is fixed for this protocol; S1 cases must not change
that set. Hash checks detect copy corruption, not coordinated malicious replacement of
both a manifest and its copies. No cryptographic authenticity claim is made.

No evidence is deleted by this work. If the user later chooses to remove an abandoned
run, first verify that any needed private evidence is preserved elsewhere, then remove
only that exact `build/memory-evaluation-TIMESTAMP` folder. Historical originals and
other run directories must remain untouched.
