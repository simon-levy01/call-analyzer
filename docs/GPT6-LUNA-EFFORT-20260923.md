# GPT-6 Luna low versus medium — September 23, 2026

**Keep low for now.** This small real-API comparison found no consistent quality gain from medium. Medium cost 73.5% more and took about twice as long overall; one medium response produced no answer under the frozen output limit. Production settings and prompts are unchanged.

## Method and cost

Four saved cases, two fresh responses per case per effort: **16 requests**, serial, alternating effort order between cases and repeats. Three live-analysis checkpoints (05, 17, 21) and full 88-turn memory extraction from the shortest recorded call. Same exact September 15 inputs, instructions, strict schema, verbosity and output caps as the September 22 replay. Only reasoning effort varies; model is `gpt-6-luna` throughout. No previous answer or assessment is sent to the model. No retry, fallback, prompt tuning or real-database writes.

| Measure | Luna low | Luna medium |
|---|---:|---:|
| Requests | 8 | 8 |
| Complete, locally validated answers | 8/8 | 7/8 |
| Median request latency, including incomplete response | 5.63s | 11.26s |
| Mean request latency | 5.95s | 11.24s |
| Median live request latency (6 each) | 4.93s | 11.26s |
| Extraction latencies | 7.06s, 9.17s | 10.74s, 12.65s |
| Total estimated cost | $0.00364469 | $0.00632319 |
| Output tokens, including reasoning | 3,730 | 9,087 |
| Reasoning tokens | 2,429 | 7,975 |

All timings are complete HTTP-response wall times, not first-token times or paced GUI latency. The incomplete medium response still consumed time and tokens and is included. Median among medium's seven complete answers alone is 11.63s.

New spend: **$0.00996788**, approximately **1 US cent**. Prior evaluation: $0.02759957. Cumulative: **$0.03756745 of the unchanged $0.30 cap**, leaving $0.26243255. These are response-usage-priced estimates, not invoice reconciliation. All 16 dispatches finished; the one incomplete model response is not an unfinished test or permission to retry.

Both arms consumed exactly 29,288 input tokens, including 16,354 cached reads and 12,910 cache writes. Thus aggregate cache differences do not explain this cost gap; medium generated more billed tokens. Verified using [official OpenAI documentation](https://developers.openai.com/api/docs/models/gpt-6-luna): standard per-million input/cached/cache-write/output rates $0.10/$0.01/$0.125/$0.50, with the same rates for low and medium. Reasoning is already included in output tokens, not charged twice.

## Results against the saved evidence

Non-blinded assistant assessment of exposed cases, not human gold labels or a general accuracy percentage. Repeat numbers below refer to independent API calls, not different scenarios.

| Case | Low, two runs | Medium, two runs | Assessment |
|---|---|---|---|
| 05: ambiguous job/memory reference | Both avoid unsupported affect and offer clarification. Run 1 keeps the tentative supplied memory; run 2 omits it. | Run 1 keeps the tentative memory without a reply. Run 2 exhausts all 1,200 output tokens on reasoning, with no answer. | No established quality gain; low is more reliably usable within this cap. Clarification is plausible, not necessarily needed during app testing. |
| 17: speaker ownership | Both suggest “You're welcome” in response to the user's own thanks, rather than the contact. | Run 1 makes the same mistake (“No problem”); run 2 abstains. | Medium avoids the error once, but does not reliably fix it. |
| 21: app commentary and disappointment | Both abstain from weak tone/reply guesses. | Run 1 also abstains. Run 2 infers calm from a factual remark and suggests repeating the user's own disappointment. | Medium introduces weak affect and redundant guidance in its second run. |
| Full-call memory extraction | 5 then 4 proposals. Model-switch commitment retained twice, specific-memory testing commitment once, user disappointment twice. Unsupported feminine pronouns in run 2. | 3 then 4 proposals. Model-switch commitment retained once; specific-memory testing omitted twice; user disappointment retained once. Unsupported feminine pronouns in both runs. | Low has better coverage of useful explicit commitments here. Neither mode eliminates unsupported personal details. |

All four extraction outputs retain financial difficulty as sensitive and the main regulation correction. None preserves the precise conditional correction rule in turn 32. None invents a new job acquisition. More memories is not automatically better; the coverage judgment concerns explicit, useful commitments, not raw proposal count. Low is also inconsistent and should not be called error-free.

## Limits and evidence

These are deliberately selected known problem cases from one noisy call, not a representative held-out benchmark. Only two repeats per effort/case. Historical speaker-null rows remain unchanged. The live cap is the historical **1,200 tokens**, not today's 1,800-token product allowance; extraction uses 2,400. The truncation establishes a failure under this test contract, not that medium would necessarily fail under the current product cap. No larger-cap follow-up was run. Ask Memory, summary generation, current retrieval, audio/vision and UI integration are not tested here. Memory generation in the product remains **Sol low**, unchanged by these evaluation-only Luna extraction calls.

Private evidence: `build/gpt6-effort-20260923/` contains the frozen cases/manifest/rubric, 16 exact requests and raw responses, cumulative reservations/results, metrics, single-use runner and offline inspection script. `runner.py audit` checks hashes, paired coverage, exact requests, raw/parsed integrity, schemas and cumulative accounting. `inspect_results.py` independently recalculates saved raw usage, checks model/output limits and cited-ID membership, and retains the incomplete response. Valid IDs and schema do not establish semantic correctness. Both offline checks passed. Original September 22 evidence remains byte-identical by its recorded hash; no ledger reset.

No fresh inference is authorized by this report. No prompt changes, default switch, release acceptance, commit or push is implied.
