# Different full-call prompt comparison — 24 September 2026

Completed the user-requested comparison: **94/94 real Luna low API responses**, **$0.041276 of the new $0.30 aggregate cap**, no failures, retries or pending requests. **Recommendation: keep the current prompt.** Combined produced more visible content but no increase in useful-or-partially-useful items, substantially more stale guidance and slower responses. Production prompt remains unchanged. Do not repeat the single-use runner or reset its ledger.

## Results at actual first display

| Measure | Current | Combined |
|---|---:|---:|
| Distinct rendered items | 25 | 33 |
| Useful | 8 | 7 |
| Somewhat useful | 8 | 9 |
| Unhelpful | 9 | 17 |
| At least somewhat useful | **64.0%** | **48.5%** |
| Clearly useful share | 32.0% | 21.2% |
| Useful novel additions | 4 | 3 |
| Median measured API response time | **4.92s** | **6.82s** |
| Actual usage cost, 47 requests each | **$0.020092065** | **$0.021183935** |

Combined showed 32% more distinct texts, but both arms had **16 useful + somewhat useful items**. It did not reproduce the quality/volume improvement from the earlier clothing-call experiment. The comparison does not prove either prompt is generally accurate: only 8/25 current items and 7/33 combined items were clearly useful under the root's strict, non-blinded rubric.

### What changed

| Category | Current | Combined |
|---|---:|---:|
| Tone texts | 6 | 6 |
| Social cues | 4 | 15 |
| Potential replies | 13 | 12 |
| Related memories | 0 | 0 |
| Follow-up items | 2 | 0 |

The increase was almost entirely social cues. Combined's cue panel was occupied for 195.4 seconds versus 49.4 seconds, but occupancy was not usefulness. Examples of failures were task-location and difficulty questions appearing after they were answered, old mouse/mouth teasing during a laptop discussion, and old interpersonal uncertainty/strain reappearing during agent-testing discussion. Both prompts also produced weak echoes and late acknowledgments.

Useful material included distinguishing situational tension from being mad at another person, cautiously identifying current teasing, qualifying speculative release claims and a safe alternative to using a laptop at a red light. Combined additionally highlighted the distinction between running an agent and understanding/reviewing its output. These gains did not offset its stale content.

For balance, combined did **not** produce more outright unsupported content in this sample. Primary reasons for unhelpful items were:

| Primary issue | Current | Combined |
|---|---:|---:|
| Unsupported assumption / role error | 4 | 2 |
| Stale or already resolved | 4 | 15 |
| Misaligned with expressed responsibility boundary | 1 | 0 |

Some items have more than one issue; the table assigns one primary reason per item. A statement can be historically true and still be poor current guidance. Novelty counts useful additions beyond acknowledgment/paraphrase, not surprising inventions; it is a qualitative judgment rather than an objective creativity score.

## Verification and limits

Reviewed all **57 distinct texts across both arms** against the transcript prefix at first appearance. The one shared greeting receives the same unsupported-ASR-greeting judgment at both arrival times. Exact item-level labels, reasons, onset/offset times and transcript context are private in `root-assessment.json` and `review-packet.json`. This is first-display usefulness, not useful screen-seconds; cards can become stale later. Counts are unique wordings, not independent conversational opportunities. No human gold ratings or confidence intervals are claimed.

Actual Qt labels were recorded through the complete call, with an offscreen screenshot visually inspected. Original frozen checkpoints while a request was busy were skipped in replay: current [3,29], combined [3,7,12,29]. All 47 checkpoints per arm still received API answers. Measured-latency differences therefore affect UI opportunity as well as freshness; this is the deployed-style outcome, not an equal-latency prompt-only causal claim. Coordinator delivery: current 28 accepted/17 duplicates; combined 34 accepted/9 duplicates. No simulated delivery errors. Both use the same unchanged production application hash.

**39 targeted guidance/Qt tests passed**, as did the offline runner check for cap-before-dispatch, timeout-reservation retention, no retries and overwrite refusal. Final audits verify exact frozen request inputs, raw-to-parsed responses, recorded usage charges, source/helper hashes and the shared $0.30 ledger. API settings and prices were checked using the OpenAI Docs skill and [official Luna documentation](https://developers.openai.com/api/docs/models/gpt-6-luna); existing local credentials were reused. The actual cost calculation includes cache reads/writes; cache usage differs naturally between requests and is preserved in the metrics artifact.

No production code, prompt, model default, personal memory or summary was changed. No additional inference, commit or push was performed or scheduled. Earlier $0.70 evaluation remains unchanged at $0.08055970.

## Frozen design

Selected the September 15 22:38–22:47 call, **150 turns, 47 original guidance checkpoints and 524.99 seconds from recorded call_start to call_stop**. This is not the September 16 clothing call used for prompt development. It covers development-task clarification, model updates, a mouse/mouth misunderstanding, joking, face/light setup, interpersonal frustration and division of project responsibilities. It has appeared in older project diagnostics, so it is a different-call transfer check, not a pristine unseen test.

Two fresh independent GPT-6 Luna low Responses API calls per checkpoint (94 total planned), alternating arm order, standard service, strict schema, 1,800 output-token cap, 15-second timeout and no retries. Reserve a conservative byte-based input/output maximum before each dispatch; retain uncertain failure charges. This ledger starts with this explicitly authorized new evaluation; all prior ledgers remain untouched. API credentials remain local.

Both arms receive byte-identical transcript, recorded sensor rows and memory inputs. Combined uses exactly the two compact paragraph replacements frozen in the earlier evaluation, without further tuning. Current production filters, source-age expiry, signature fix and user-question supersession are identical. All 47 snapshots have zero supplied memory candidates; this cannot measure memory-recall quality.

The actual Qt renderer is replayed at 100ms simulated intervals using measured API latencies, recorded speech times, current grounding, coordinator acceptance, 12-second stability and 24-second source-age expiry. Checkpoints while a request is busy are skipped in the UI replay and recorded, although all planned API checkpoints are evaluated. Stop the timeline at recorded call_stop, not an added tail designed to expose extra answers. This fixed-checkpoint simulation is not a new live audio/vision capture or exact reproduction of the adaptive scheduler. No new post-call generation, user clicks or memory approval.

Assess distinct actual rendered texts at their first appearance: useful / somewhat useful / unhelpful, with meaningful novelty separately. Unsupported facts, wrong speaker and outdated/resolved guidance do not count as useful. Prefer factuality over creativity. Non-blinded root assessment on an exposed call, not human acceptance or a statistical accuracy benchmark. Counts are wordings, not independent opportunities or useful screen-seconds.

Private evidence: `build/full-call-prompts-20260924/`; single-use runner `build/full_call_prompt_comparison_20260924.py`; offline audit `build/audit_full_call_prompts_20260924.py`. Exact source/helper hashes, requests, raw answers, usage/cost reservations and rendered UI traces are preserved. No production code/default changes or Git publication are part of this evaluation.
