# Memory answer comparison — September 15, 2026

**Retain Luna low and the current memory system.** This diagnostic completed 48 fresh Luna low API requests and compared 48 matching historical local outputs. No production code, database, retrieval configuration or historical result was changed.

## Results

These are the current assistant's judgments on existing development cases, not blinded or held-out benchmark scores. An Ask pass means a supported answer without a material factual/temporal error or unnecessary abstention; citation membership is checked separately from relevance. Guidance has separate reminder and structural checks, not an overall pass claim.

| Measure | Luna low API, fresh | Gemma 3 4B, saved | Qwen 3.5 4B, saved |
|---|---:|---:|---:|
| Outputs reviewed | 48 | 24 | 24 |
| Ask supported answers | 12/12 in each pass (24/24) | 4/12 | 7/12 |
| Useful target Remember items | 3/8 | 0/4 | 1/4 |
| Schema-valid outputs | 48/48 | 24/24 | 24/24 |
| Outputs with only supplied identifiers | 48/48 | 23/24 | 23/24 |
| Outputs citing unavailable vocal/visual modalities | 0 | 1 | 3 |
| Guidance outputs missing the required latest-turn reply citation | 0 | 6 | 0 |

The unequal repeat counts are intentional: Luna has two fresh observations per case, each local model one historical observation. These small dependent samples do not establish statistical superiority, especially for reminders (3/8 versus Qwen's 1/4). Retention also reflects fewer factual/ownership errors and avoids a production change.

Schema validity does not establish semantic correctness. A supplied identifier can still be irrelevant. The modality count checks explicit modality tags; Qwen also invented speech-rate evidence inside prose, which this count does not capture.

### Luna findings

- All 12 Ask cases passed on both requests: rejection, project progress, future events, losses, awards, trips and appointments. The ambiguous missing-person question preserved both possibilities. The appointment question alternated between identifying the upcoming visit and asking which visit was intended; both are acceptable under the frozen rubric.
- Of four useful reminder targets, grandmother/January appeared in both repeats; photography/March appeared once; job loss and short-film award appeared in neither. The other photography response cited the memory in its replies but omitted the separate Remember item. **These five omissions are evidence-use failures: the relevant memories were already in every input.** They do not show retrieval failure.
- No unrelated Remember item appeared. Both repeats kept puzzle discussion separate from the user's rent stress, avoided stale exam anxiety, and did not execute the quoted instruction to list private memories.
- Remaining faults include high-confidence emotion labels without explicit emotion, attributing the user's topic change to the contact in both repeats, and a repeated offer of help alongside a correct wait action in one repeat. One found-keys alternative assumes the keys repeatedly end up in the coat. Passing Ask does not clear guidance.

### Historical local findings

Both local models chose the older photography award when asked for the most recent award. Qwen unnecessarily asked for clarification when dates resolved the more-recent loss and denied a trip comparison despite naming both trips. Gemma invented a bakery health appointment, mixed completed and upcoming visits, and often cited unrelated evidence. Each model fabricated one identifier.

Both confused user stress with contact affect. Qwen linked found keys to job loss, invented vocal evidence, and reintroduced exams after the topic change. Gemma invented visual evidence in the ambiguous-loss case. Both avoided executing the quoted memory-list instruction, but that single test does not establish injection resistance.

### Assistant reference

The current assistant authored and schema-validated 24 reference answers before reading the new Luna or selected saved local outputs. Their hash was frozen before dispatch. `authorization-freeze.json`, including the rubric, was written at 2026-09-15 09:42:33 UTC; its SHA-256 is `06e368a528ea1b3b4c06573baab4021780013088d14a555e761a04571c56947e`. This is local filesystem/provenance timing, not independent timestamp attestation. They provide examples of correct factual answers and tentative reminders, including the job-loss and film connections. They are **not independent model runs**: this conversation already included earlier reports and some expectations, the author also judged responses, and there is one reference per case. No self-awarded accuracy, latency, API parity or cost comparison is claimed. Reference omissions and inference choices remain open to human disagreement.

## Protocol and provenance

- 12 Ask cases from the existing September 13 fictional history corpus, plus all 12 authored guidance challenges from that date. Existing transcripts and expected behavior were reused; real private call recordings were not sent.
- Luna `gpt-5.6-luna`, reasoning `low`, two sequential passes of 24 stateless requests; no conversational carryover, retry or fallback. Actual response metadata reports `gpt-5.6-luna`; no more specific provider build is exposed.
- Identical frozen historical instructions and evidence; Ask output cap 1,000, guidance cap 1,200, input estimate ceiling 15,000, 30-second timeout, `store=false`, SDK retries zero. Existing budget reservation/usage machinery was reused.
- Saved `gemma3:4b` and `qwen3.5:4b` each contribute one output per case from the original full/new runs. Exact system instructions, evidence payload, JSON schema and output limits match. Local schema text is appended to the user message and Ollama decoding differs from OpenAI structured outputs; this is matched content, not identical transport. No new local inference was run.
- The private authorization supplement supersedes the preparation protocol's pending-budget status and planned repeat count for reused local outputs. No old protocol, spend ledger or output was overwritten.
- This tests supplied evidence, not retrieval. Guidance inputs contain seven memories, unlike the production four-memory budget. Historical prompts precede active F07 changes. No migration, retrieval fix, challenger adoption or deployment occurred.

## Resource accounting

Fresh Luna usage: **$0.02322885 estimated against the authorized $0.30 aggregate cap**; $0.27677115 unused. All 48 calls completed, with zero timeout/invalid-output replacements and no outstanding reservations. Estimates use the frozen repository rates: $0.20/M input, $0.02/M cached input, $1.20/M output, with the existing 1.25 cache-write multiplier. This is recorded usage pricing, not a provider invoice.

107,456 input tokens include 73,885 cached-read tokens and 33,427 cache-write tokens. Output tokens total 11,138, including 4,179 reasoning tokens (do not add reasoning again). The ledger carries reservations before dispatch and persists usage after every completion.

Fresh request timing: 4.125 s median, 8.563 s nearest-rank p95, 208.471 s summed request duration including local processing and persistence. Historical selected Gemma timings were 5.757 s median / 7.072 s p95; Qwen 6.634 s / 10.402 s. Different dates, hardware/cache state and one versus two repeats prevent a controlled speed comparison. Reusing old outputs incurred no new local inference/API cost. Local electricity, depreciation and peak resource measurements are unavailable for this comparison, not zero. Assistant judgment and any review consume subscription usage; these are not included in Luna's API ledger.

## Checks and gates

The standalone offline check covers 48 mock calls with exact cached/cache-write pricing, tiny-cap rejection before dispatch, one uncertain-billing timeout without retry, overwrite rejection, altered model/input/instructions rejection before the mock provider, and lock-only resume rejection even if the result file is absent. Reviewed runtime guards now use explicit exceptions, so optimized Python cannot remove them. No further inference was run after this hardening; the original executed runner is preserved in the source freeze. Raw output was validated against schemas and supplied IDs. Production/input/reference hashes match the dispatch freeze; the check was subsequently made self-contained with synthetic mock inputs and rerun successfully. The new runner/check files have reviewed changes after that freeze, recorded separately. Production source hashes remain unchanged.

Exact requests, raw provider responses, references, historical matches/hashes, case-level Ask assessments covering both repeats, individual guidance judgments and per-response structural checks, frozen rules/source/prices and ledger are preserved in ignored `build/memory-answer-comparison-20260915T093115Z/`. Do not publish that directory. The report contains aggregate results and fictional examples only.

**Review status: actual Claude Opus 5 reviewed this diagnostic; corrections are recorded, a focused correction review is complete, followed by three offline corrections.** The reviewer independently recomputed the exact Luna cost. I replaced assertion guards, added exact pricing and altered-request checks, and replaced generic Ask judgments with case-specific evidence notes, finalized in `assessments-final.json`. The follow-up reviewer closed the pricing, request-guard and disclosure findings and withdrew the proposed lifetime budget. I then explicitly labeled the Ask notes as case-level (both repeats), removed the constant citation-relevance field, and added a passing lock-only resume test with an explicit error. These final offline edits have not had a third Claude review. No public release clearance is claimed. The Harbor Labs citation questioned in review is valid: the cited update explicitly includes Harbor nonresponse as well as bakery progress. Ask project answers do omit the separate rejection-reason citation; the reason is present in supplied evidence.

The reviewer also proposed a permanent $0.30 clamp and repository-wide cumulative budget. Those conflict with the user's per-request budget with explicit overrides and would combine unrelated evaluations. The maintained runner enforces one prepared run's cap and prevents resuming it; it does not aggregate arbitrary separately created directories. Creating another directory is not authorization to restart this evaluation or reset spend. This is a documented operational limit, not a cross-directory enforcement claim. Only this one 48-request run was dispatched.

Claude review used subscription authentication with API-key variables removed and no tool access. Its first response reports 38,866 cache-creation input tokens and 9,271 output tokens, with $0.620445 equivalent `costUSD` metadata; that is not evidence of an extra paid API charge and is separate from the authorized Luna API ledger. The correction review reports 13,965 cache-creation input tokens, 3,312 cached-read tokens, 2 uncached input tokens and 7,472 output tokens; its equivalent cost metadata is $0.328116. Together the two reviews report $0.948561 equivalent usage, separate from Luna charges. Exact review responses and usage are retained. The earlier initial local-memory checkpoint review does not approve this new run. No human user-testing results, post-user-test review or publication clearance are claimed. The original local-memory plan remains incomplete (including distinct held-out evaluation and Hindsight). This API diagnostic is separately authorized by the later user instruction and does not replace or complete that local-only experiment.

The standing instruction is now in `AGENTS.md`: an explicit Luna low API test request has a $0.30 total cap unless the user specifies another amount. It does not authorize unrequested tests or reset an existing evaluation ledger.
