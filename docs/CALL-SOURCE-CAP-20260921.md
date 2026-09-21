# Luna source-limit experiment — September 21

**Raise the live citation allowance, but retain token budgets.** The combined three-source rule demonstrably removes a correct reminder. Removing all source/output caps does not consistently improve meaning and produced a misleading job-acquisition memory in this run. Production is unchanged; the candidate exists only in the ignored diagnostic package.

Recommended bounds for a future reviewed change:

| Output | Suggested citation allowance |
|---|---|
| Each reply, reminder or follow-up | Up to 3 transcript turns **plus** 3 memory IDs; remove the conflicting combined-three check |
| Each tone/cue | Up to 4 transcript turns |
| Style preferences | Retain the separate existing maximum of 2 eligible preference IDs |
| Each memory proposal or summary statement | Retain the existing maximum of 20 transcript citations |

The live suggestion schema already permits three IDs in each list; keeping those bounds avoids introducing a new memory restriction. These are maxima, not quotas. Do not reserve a shared pool across the whole answer or require the model to fill slots. Every item needs its own relevant support. Even without a token constraint, the best evidence set is the smallest sufficient set of relevant, unique sources; adding unrelated citations does not improve grounding. These limits concern citations to evidence already supplied, not additional retrieval or call history.

All 42 available current/no-cap live answers, including separately labeled supplementary attempts, fit the proposed per-field bounds, including the existing four-citation cue that failed current validation. This is an offline compatibility check, not fresh inference with the proposed bounded prompt. No global production relaxation has been applied.

## Scope and method

The first two-thirds of the shortest call spans approximately 3 minutes 48 seconds from first speech. It contains **21 recorded analysis checkpoints and 57 delivered turns**. The next turn arrived after the cutoff and is excluded. Extraction and summary were generated at this stopping point for every arm; later conversation content was hidden.

Three Luna-low agent arms compare the pre-fix package (`75d5b27`), current corrected package (`a927b91`), and current package with citation ceilings and the requested output-token allowance removed. The last arm retains the same supplied live evidence, item counts, text-field lengths, concise-output preference, grounding and source-eligibility rules. It does not expand retrieval or input context. The agent platform still has finite limits; “no application cap” is not literally unlimited inference.

**55 fresh isolated agents ran in total: 48 initial requests and seven supplementary attempts.** Every agent explicitly used `gpt-5.6-luna`, low reasoning and no history fork. Current live requests reuse 21 exact saved answers with hashes and provenance; those are not new independent inferences.

The first 48 agents yielded 41 readable JSON answers, four missing files and three empty files. Together with the 21 reuses, that first pass has 62 readable answers and 61 local passes across 69 planned observations; one reused current answer fails its schema. Only 14 live checkpoints have valid first-pass answers in every arm. The table below preserves those first-pass outcomes.

After disclosing the delivery gap, seven fresh agents answered the same packets as separately labeled attempt2. They returned raw final JSON for the coordinator to save, avoiding the leaf file-writing step. Original failures were not repaired or overwritten. Every requested output now has an answer. One supplementary answer introduces a genuine schema error by putting `uncertainty` in the tone enum. With supplements, local passes are **23/23 pre-fix, 22/23 current and 22/23 no-cap**, with 19 fully valid matched live checkpoints. The changed saving protocol further limits strict comparability.

| Measure | Pre-fix | Current fixes | No application source/output cap |
|---|---:|---:|---:|
| Locally valid outputs / 23 planned | 18 | 22 | 21 |
| Agent save failures | 5 | 0 | 2 |
| Schema failures | 0 | 1 | 0 |
| Checkpoints with initially accepted replies / 21 planned | 11 | 7 | 12 |
| Correct supplied-memory reminders initially retained / 2 opportunities | 2 | 0 | 2 |
| Memory proposals | 5 | 6 | 6 |
| Summary statements | 6 | 6 | 4 |
| Complete post-call processing in disposable database | Pass | Pass | Pass |

Availability and schema success are **not semantic accuracy**. Missing files are test-delivery failures, not evidence that a model chose to abstain. Reply totals are not quality rankings, especially with unequal missingness. Both reminder opportunities supplied the memory; this tests its use, not retrieval recall. The original live call used Terra for guidance and is not mislabeled as a Luna baseline here.

## Findings

**A mechanical fix is warranted.** At checkpoint05, the saved current answer cites three speech turns plus one memory ID and loses a correct reminder. Replaying that exact answer through the relaxed filter restores it without new inference. Fresh no-cap Luna independently uses the same four-source pattern and retains a correct reminder. The current07 reminder instead misreads app memory surfacing; extra sources alone do not repair that answer. Its historical-arrival replay removes it after a context reset.

**Existing fixes help, with remaining gaps.** Pre-fix answers repeatedly label factual speech calm and retain old financial affect after app commentary. Current grounding removes several such cues. No-cap answers still reverse speaker roles in replies, repeat questions and use the user's words as contact evidence. At checkpoint10, an uncertainty cue survives despite weak mixed-speaker attribution. At16, two four-citation cues are removed by grounding. More citations do not guarantee correct ownership.

**Unlimited post-call output did not win.** The current summary explicitly retains the exact regulation correction exception that the pre-fix summary omits. The no-cap summary is shorter and less precise about that rule, and omits explicit disappointment. Its extraction stores the isolated phrase about “getting the job” as a high-confidence fact, missing the adjacent clarification about bringing up an app memory. Current extraction avoids that error but still retains a transient reaction as a preference and a vague pronoun as generic memory. These remain selection/context problems. Every complete post-call pipeline passes locally despite these semantic defects.

## Token evidence and limits

The existing application estimator gives these **visible-output estimates**, including supplemental answers, not provider token counts:

| Output | Pre-fix | Current | No cap |
|---|---:|---:|---:|
| Live median | 306 | 207 | 237 |
| Live maximum | 561 | 353 | 408 |
| Prefix extraction | 559 | 612 | 641 |
| Prefix summary | 580 | 542 | 401 |

No readable live answer approaches the current 1,200-token allowance under this estimator. No-cap live answers use at most four transcript citations per cue and one memory ID per suggestion. The longest summary evidence list uses 12 turns, already below the existing 20-source limit. This supports a small live allowance increase; it does not demonstrate a need to raise output caps. Hidden reasoning, tokenizer differences and provider enforcement are unmeasured, so real API fit, latency and the separate 10% cost gate remain unverified.

This is one exposed, non-blinded development comparison. Old/current input serialization differs; current/no-cap generation changes prompt, schema and requested output allowance together. Fresh-answer differences therefore do not isolate citation count causally. Only the same-output replay establishes the mechanical recovery. No raw answers were repaired or overwritten; supplementary attempts are separately labeled. No memories were approved and no paid API calls were made. Original F07 acceptance design, tuning limits, held-out/human checks, Opus 5 review gates and deadlines remain unchanged. This diagnostic does not establish a passing production candidate or F07 completion.

Private evidence and runnable checks: `build/source-cap-agent-20260921/` contains frozen packages/packets, selection cutoff, append-only dispatch audit, exact reused/raw outputs, rubric/root assessment, offline validation, comparison browser and final integrity audit. `check.py` verifies four-source retention, unknown-source rejection, required memory evidence and preserved item caps. `evaluate.py` and `report.py` replay and summarize without model calls. Other two calls remain deferred.
