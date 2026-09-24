# GPT-6 real-API comparison — September 22, 2026

**Completed 35 real API requests for $0.02759957 under one $0.30 cap.** No retries, agents, fallback models, prompt tuning or writes to the real memory database. All 35 returned complete structured answers. This is usage-priced accounting, not a reconciled provider invoice.

The shortest of the three saved calls spans **5m 41.46s / 88 transcript turns**. GPT-6 Luna low received all 31 recorded live-analysis checkpoints, plus extraction and summary over all 88 turns. The comparison reuses September 15 paid GPT-5.6 Luna low answers; it does not mislabel the original live call's Terra guidance or September 21 agent outputs as Luna API results. The old replay had one failed live answer (checkpoint 20), retained as missing; no old-model inference was rerun.

## Quick complete-response timing

Same saved analysis request (checkpoint 05, with transcript, vocal/visual observations and a retrieved memory), standard processing, one serial request per arm. These are full-response wall times, not first-token times or a stable model ranking.

| Model / effort | Response time | Output tokens (includes reasoning) | Reasoning tokens | Cost |
|---|---:|---:|---:|---:|
| GPT-6 Luna low | 9.32s | 469 | 323 | $0.000659175 |
| GPT-6 Luna medium | 8.35s | 1,065 | 960 | $0.000957175 |
| GPT-6 Sol low | 6.52s | 371 | 125 | $0.012203500 |

Each used 3,398 input tokens, no cached reads and 3,395 cache-write tokens. Medium's faster single sample does not establish that medium is faster in general. It omitted a useful memory the low arm retained. Sol returned a weak calm hypothesis and a questionable new-job clarification; faster does not mean more accurate here. Luna low's timing response also serves as checkpoint 05 in the full-call replay, not a second independent response.

## Full-call Luna comparison

| Measure | Saved GPT-5.6 Luna low | New GPT-6 Luna low |
|---|---:|---:|
| Completed live answers | 30/31 | 31/31 |
| Extraction / summary answers | 2/2 | 2/2 |
| Median response time, 30 matched successful live cases | 8.23s | 3.70s |
| Range on those matched live cases | 4.81–16.70s | 1.99–9.32s |
| Paired checkpoints offering at least one raw reply | 28/30 | 12/30 |
| Memory proposals | 5 | 5 |
| Summary statements | 5 | 4 |

The observed median is about **55% shorter**. Old timing is historical, not a same-day controlled benchmark; network/server conditions, caching and generated length differ. The full new Luna pass cost $0.014438895. Reply counts measure availability, not correctness; the new model is considerably more selective.

### Accuracy assessment

All 31 live cases and both post-call answers were read against the frozen evidence. Non-blinded exposed-case assessment, not an accuracy percentage or a held-out release gate.

- **Clear live improvements:** checkpoint 07 no longer mistakes bringing up a saved job memory for acquiring a new job or congratulates the wrong person. Several checkpoints stop assigning calm to filler, carrying financial strain into later technical discussion, or inventing the user's remembered knowledge/confusion. At checkpoint 21 the model explicitly distinguishes the user's disappointment from contact affect and avoids an unnecessary wording-change suggestion.
- **Remaining live errors:** weak calm hypotheses persist; checkpoint 17 suggests answering the user's own thanks, a speaker-direction error. At checkpoint 26 the new model loses reasonable optimism and substitutes weak calm. It offers many fewer replies, including some lost reasonable acknowledgments; abstention is not automatically an improvement.
- **Memory extraction is mixed:** the new model separates actual commitments and drops an unsupported interpretation of noisy speech, but invents a gendered pronoun for the contact and omits a useful user opinion. No clear blanket memory-quality win.
- **Summary is mixed:** financial difficulty is now marked sensitive and actual plans correctly labeled as facts, but useful face-tracking/memory-troubleshooting detail is omitted. Neither version preserves the full conditional regulation-correction rule. Both avoid the original job-acquisition summary error.

**Conclusion:** promising live precision/selectivity and noticeably shorter observed response times, but not uniformly better accuracy or usefulness. Keep source/approval safeguards. One timing case does not justify switching to medium or claiming Sol is more accurate. Production memory/summary generation remains the configured higher-end **Sol low**; the Luna post-call requests here are evaluation-only.

## Exact scope and evidence

Requests preserve the September 15 instructions, input text, strict JSON schema, verbosity and output caps (live 1,200 tokens) exactly; only model/effort changes. They intentionally do not use today's newer prompts, four-item UI contract or current live 1,800-token allowance. This isolates the model on saved requests, not latest-product end-to-end behavior. Recorded speaker ambiguity, observations and retrieved candidates remain fixed. No audio/vision rerun, fresh retrieval, adaptive scheduling, UI delivery simulation or human gold labels. Valid source IDs/schema alone do not prove semantic accuracy.

Private evidence stays Git-ignored in `build/gpt6-api-20260922/`: immutable prepared manifest/cases, 35 exact requests and raw responses, cumulative reservations/results, metrics, per-case root assessment, runner and offline integrity checker. `check_results.py` passes coverage, exact request/schema/model/effort, raw/parsed integrity, original baseline hashes and accounting checks. Original logs/results/ledgers are unchanged. Old checkpoint 20 is excluded from paired timing, not silently repaired or scored as correct.

Current rates and API contract were checked with the OpenAI Docs workflow: [GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna), [GPT-6 Sol](https://developers.openai.com/api/docs/models/gpt-6-sol). Standard short-context input/cached/output rates are $0.10/$0.01/$0.50 for Luna and $2/$0.20/$10 for Sol, per million tokens; cache writes use 1.25x input. Reasoning tokens are already included in output billing.
