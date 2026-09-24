# Prompt search and third-call transfer — 24 September 2026

Completed **203/203 new real Luna low API responses**, **$0.086914715 of one $0.30 cumulative cap**, with no failures, retries or pending requests. **Recommendation: keep the current prompt.** None of the three new prompts improved useful volume and useful share together on the first call; the selected freshness candidate also lost to current on the third call. Production prompt and application remain unchanged; previous evaluation ledgers are untouched.

## First stage: full 150-turn call

All **141/141 new Luna low API calls succeeded**, costing **$0.06078156**. Reused the exact 47 previously paid current-prompt answers and measured latencies, with identical request input verified. The Qt replay exactly reproduced that baseline's prior timeline. Baseline cost below is historical, not charged again.

| Prompt | Shown | Useful | Somewhat useful | Unhelpful | At least somewhat useful | Useful novel | Median API time | Cost |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Current (reused) | 25 | 8 | 8 | 9 | 64.0% | 4 | 4.92s | $0.020092065 historical |
| Freshness-focused | 22 | 3 | 10 | 9 | 59.1% | 3 | 5.24s | $0.019476130 |
| New-information-focused | 17 | 4 | 2 | 11 | 35.3% | 2 | 6.65s | $0.020965555 |
| Minimal response | 29 | 7 | 7 | 15 | 48.3% | 4 | 4.54s | $0.020339875 |

The frozen factuality-weighted selection score was `useful + 0.5*partial - unhelpful - unsupported`, with unsupported a subset of unhelpful receiving an extra penalty. Scores: current -1, freshness -2, new-information -8, minimal -8.5. **Freshness won among the NEW candidates, but did not beat current.** Selection was frozen before dispatching fresh third-call requests. This is not a post-hoc choice based on transfer results.

Freshness reduced unsupported items from four to one but had eight stale items versus current's four; many other outputs were merely acknowledgments or paraphrases. Useful additions included verifying the claimed announcement with its source, qualifying speculation, and suggesting replay of an ambiguous hearing exchange. The minimal variant added visible cues but often too late. More output was not better output.

| Category | Current | Freshness | New information | Minimal |
|---|---:|---:|---:|---:|
| Tone texts | 6 | 2 | 2 | 6 |
| Social cues | 4 | 7 | 7 | 10 |
| Potential replies | 13 | 13 | 8 | 12 |
| Related memories | 0 | 0 | 0 | 0 |
| Follow-up texts | 2 | 0 | 0 | 1 |

## Third-call stage

All **62/62 fresh paired responses** completed across the 31 checkpoints of the complete 88-turn September 13 call. New stage cost **$0.026133155**, carrying first-stage spend forward to **$0.086914715/$0.30**.

| Measure | Current | Selected freshness prompt |
|---|---:|---:|
| Distinct rendered items | 19 | 18 |
| Useful | 4 | 2 |
| Somewhat useful | 8 | 8 |
| Unhelpful | 7 | 8 |
| At least somewhat useful | **63.2%** | **55.6%** |
| Useful novel additions | 3 | 1 |
| Median measured API time | **5.29s** | **5.67s** |
| Cost, 31 requests each | $0.013271895 | $0.012861260 |

Both displayed four tone texts, three cues and eleven potential replies, with no follow-up texts. Current additionally displayed one relevant supplied memory; freshness displayed none. **Freshness returned an empty `remember` array at both memory-bearing checkpoints**, so this absence was not caused by a UI filter hiding a generated reminder. The second memory-bearing checkpoint was skipped as busy by both UI replays, but current displayed a reminder from the first.

Current's useful material included optional practical support, the relevant historical memory and verifying wording in a partially explained regulation mix-up. Freshness offered a useful listening-versus-practical-help choice and a qualified difficulty interpretation, but other content was mostly repetitive or late. Both turned a garbled transcription into apparent wordplay; freshness additionally assumed a landing-page clarity problem despite the transcript saying the full act name was present. Primary unhelpful reasons were current five stale/two unsupported versus freshness six stale/two unsupported. This is a judgment of usefulness at arrival, not a claim that all historical statements were false.

The small observed API-cost saving (about 3.1%) does not compensate for less useful guidance here. There is no evidence from these two calls to promote the candidate. **No new prompt was applied.** The current prompt is still imperfect: only four of nineteen third-call texts were clearly useful; eight were merely somewhat useful. More prompt verbosity or more emitted cues alone has not solved the stale/repetitive guidance problem.

## Method and limits

- GPT-6 Luna low, standard service, strict structured output, 1,800 output-token limit, 15-second timeout, no retries. Only two prompt paragraphs vary; transcript, supplied memories, recorded sensors, schema, grounding and UI rules remain identical. All exact prompts, requests and raw answers are preserved privately.
- Search uses 47 original checkpoints over 524.99 seconds; transfer uses 31 over 353.56 seconds. Both run through recorded call stop, without adding a tail to expose extra guidance. These are complete saved calls, not new audio/vision capture.
- Actual Qt labels are replayed at 100ms simulated intervals using measured API latency, current validation/grounding, coordinator acceptance, stable-card handling and expiry. Busy checkpoints are skipped in UI replay even though every checkpoint receives API evaluation. Consequently timing affects both visible opportunity and freshness; this is not a pure equal-latency prompt-only causal comparison or an exact adaptive-scheduler reproduction.
- Non-blinded root assessment of every distinct rendered text at its first display, against the transcript prefix available then. Shared wordings with different timing can receive different arm ratings. Novelty means a useful additional distinction/action, not creativity for its own sake. Counts are unique wordings, not independent opportunities or useful screen-seconds. No human gold standard or statistical accuracy claim.
- Both logs have appeared in historical project diagnostics; the third is a different-call transfer check, not a pristine holdout. Prompts were not revised after either stage began. Search baseline labels were reused unchanged.
- Search has no supplied memory candidates. Transfer has one recorded approved-memory excerpt supplied at two checkpoints; this tests display from those frozen candidates, not fresh retrieval/embedding quality. Real personal memory data was not changed.

**Checks:** 39 targeted offline guidance/Qt tests passed. Offline money-path simulation checks protected transfer allowance, shared spend across stages, retained timeout reservations, disabled retries and refusal to overwrite a dispatched stage. Exact-input/raw-answer/usage/source-hash audits and search baseline renderer parity passed. API settings/prices were checked using the OpenAI Docs skill and [official Luna documentation](https://developers.openai.com/api/docs/models/gpt-6-luna). No new dependency or production implementation was needed.

All 90 distinct search texts and 34 distinct transfer texts were reviewed; shared texts are graded per arm where timing differs. Actual Qt screenshots from both stages were visually inspected. No application-validation failures occurred. Search busy-checkpoint indices: current [3,29], freshness [3,12,29], new-information [3,7,12,32], minimal [3]. Transfer: current [7,16,20,28], freshness [7,16]. They are recorded rather than counted as displayed output. Near-identical acknowledgments remain distinct wordings, so these totals should not be interpreted as independent successful interventions. Borderline praise/acknowledgment ratings are explicitly labeled partial in the private assessment.

Private evidence: `build/prompt-search-transfer-20260924-v2/` (one cumulative `ledger.json`, frozen `selection.json`, stage-specific cases, requests, raw responses, UI traces, screenshots and item ratings). Preparation-only directory without `v2` has no dispatch. Runner: `build/prompt_search_transfer_20260924.py`; offline renderer/audit/assessment/check scripts share that prefix. Never rerun/reset a dispatch or ledger. No commit, push, automatic additional inference or production prompt adoption is authorized by this experiment.
