# Luna low versus Terra low — 2026-09-13

## Recommendation

Offer a live model choice: Luna low is a useful budget option, while Terra low is more reliable for the difficult memory-reminder checkpoints from the real call. Keep the live analysis, cues, replies and memory selection together in one request. A two-model pipeline needs more work before it is a worthwhile replacement. Neither model is consistently correct, and switching models will not repair an upstream retrieval omission.

The application remains configured for Terra low live guidance and Luna low Ask/post-call work. This task changed no production model settings and did not add a model selector.

## Scope and cost

Completed **329 real API responses: 304 Luna low and 25 Terra low**, plus **268 passing automated tests**, including both basic and HeyGen video/face replays, transcript fixtures, memory lifecycle/privacy, budget and UI integration tests. The video checks validate decoding/tracking and fixture behavior, not ground-truth human emotions.

Reused the earlier Terra responses instead of paying to repeat the whole Terra evaluation. The 25 fresh Terra calls were limited to the previously unmeasured post-call comparison (2), natural-language search comparison (15), split-model prototype (4), and current-prompt real-call checkpoint repeats (4).

Actual usage-based application API estimate: **$0.38175194**, about **38.2 cents**, within the separately authorized **$2** budget. Luna requests cost $0.19194694; Terra requests cost $0.189805. The conservative budget ledger holds $0.38502877 because two Windows logging collisions were charged at their reservation maxima. Both responses had arrived; the affected evaluations were rerun successfully. These were harness failures, not model failures. No uncertain amount was refunded from the budget ledger.

Coverage:

- All **159 requests in the previous full regression set**: 53 saved paced checkpoints across 14 cases, 20 repeated frozen checkpoints, and 86 legacy guidance/Ask/extraction/summary checks. Obsolete prompt-tuning variants were not rerun; their scenarios are covered by this regression set.
- The latest actual call: all 31 historical Terra request inputs replayed on Luna, then 31 current-production checks. Historical pairs preserve the recorded payload and instructions, isolating the model/profile as far as possible. Current-production rows include the later always-offer-a-next-step prompt and validation changes, so they are not isolated model-only comparisons with older Terra output.
- Twenty current-production frozen checkpoints; 15 full-history natural-language searches on each model; current full-call extraction and summary on both models.
- Real wall-clock production-coordinator replay of the latest 88-turn call, plus vague and clearer job-loss transcripts sent every four seconds. Thirty real-call requests and three requests per synthetic call; actual feed timing error was at most 31ms.
- Four two-stage Luna-analysis/Terra-guidance experiments, and two repeats per model at each of two current-prompt real-call memory checkpoints.

## Measured component costs

The live-call row is the matched 31-request replay of the approximately six-minute recorded call. The other rows are separate measured component tests; three-search cost is three times the measured 15-question mean. These are not ten-minute prices.

| Component | Luna low | Terra low |
|---|---:|---:|
| Live analysis, cues, guidance and memory selection together | $0.028744 | $0.201499 |
| Three natural-language memory searches | $0.002082 | $0.019889 |
| Create memory proposals from the full saved call | $0.001694 | $0.015714 |
| Generate its summary | $0.001840 | $0.016499 |
| Local transcription, embeddings and candidate retrieval | $0 API | $0 API |

Analysis/cues/guidance/reminders currently share one billable response, so assigning each an independent cost would be artificial. The separate split experiment below measures an actual two-request alternative.

Across all **149 matched historical guidance requests**, Luna cost **$0.09847945** versus Terra's **$0.66093010**, approximately 85% lower. This observed ratio includes differing output lengths and cache behavior; it is not simply a tenfold unit-price calculation.

For a **ten-minute call with three searches**, comparable speech density and roughly 50–60 live updates:

- Luna live + Luna search/review: approximately **$0.06–$0.09**.
- Terra live + Luna search/review (current combination): approximately **$0.37–$0.43** for uninterrupted live guidance.
- Roughly 80% Luna  / 20% Terra live updates, with Luna search/review: approximately **$0.12–$0.15**.

These are projections, not a paid ten-minute trial. A longer transcript can cross the whole-summary input ceiling and require several summary chunks/consolidations, so post-call cost does not scale smoothly. Current caps remain $0.27 for live work and $0.35 overall; Terra would pause paid live work before completing ten minutes at this pace. Local transcription/matching excludes electricity or any separately billed calling platform.

## Memory selection

| Check | Luna | Terra |
|---|---:|---:|
| Reviewed positive checkpoints in the first regression group | 12/12 | 12/12 |
| Varied-event checkpoints where the target memory was actually supplied | 7/9 | 9/9 |
| Old reminders retained after a user-requested topic change — lower is better | 2/8 | 5/8 |
| Old reminders retained after the contact explicitly started the new topic | 0/12 | 0/12 |
| Current-prompt McDonald's checkpoint repeats | **1/4** | **4/4** |

These are descriptive counts of specific, sometimes repeated checkpoints, not independent-population accuracy estimates. The first positive subset does not replace the broader results.

The two varied-event Luna misses were a clear layoff/paycheck reference and relief after voluntary resignation. The correct approved memory was in each request, so those omissions were model-selection failures.

On the real call's current-prompt repeat checks at turns 15 and 20, Terra selected the supplied McDonald's memory in all four responses, Luna in one. Terra's stronger recall did not guarantee a good reply: one response asked what kind of job it was, confusing the testing exchange with a new job outcome. Luna sometimes treated “good job” as a compliment instead.

**The earlier financial-trouble delay is a separate retrieval problem.** Neither model received the real McDonald's memory during the early “hard money-wise” exchange. It appeared only after “job” entered the transcript. The synthetic memory includes worry about rent; the real stored memory only says Yaheli lost his McDonald's job. That makes the synthetic match easier and is an important limit on generalizing its success.

## Live guidance, cues and timing

Luna often gave useful sympathetic replies, congratulations, short acknowledgments and waiting actions. It avoided some repeated project questions and irrelevant exam reminders that Terra produced. Current-production validation supplied a next-step/waiting suggestion in every completed fixed checkpoint.

Luna was more inclined to label routine corrections or brief acknowledgments as calm, and sometimes added emotional intensity without enough support. The production validator downgraded many high-confidence guesses to medium, but that does not make an unnecessary interpretation useful. Terra more often abstained on routine utterances, but also made attribution mistakes: one recorded Terra response called the user's “a little disappointing” statement an explicit contact feeling. Luna did not repeat that specific error in the matched replay. Neither output is ground-truth emotion evidence.

Recorded Terra median API latency was **2.32s**. Luna's matched-input median was **4.47s**, current fixed replay **5.56s**, and timed real-call replay **5.97s**. Provider load and caching were not experimentally controlled, so this is observed performance, not a universal speed ranking.

The timed call produced 30 Luna updates. Only 3 reply batches remained current on return, versus 6 under the corresponding freshness check on the old Terra log. This is a service-level comparison, not a new physical GUI test; the prompt and scheduling also changed. New speech correctly suppresses outdated wording. The UI's generic waiting/listening fallback remains available; a suppressed batch does not mean an empty guidance panel. Memory-card retention is separate from new model selection.

The timed real-call run selected no memory at its two supplied-memory checkpoints; that prompted the balanced current-prompt repeats reported above.

### Four-second vague job transcript

| Time | New finalized turn |
|---:|---|
| 0s | You: How have you been? |
| 4s | Contact: I feel stressed. |
| 8s | You: What has been on your mind? |
| 12s | Contact: I do not know how I am going to pay rent. |
| 16s | You: That sounds like a lot to deal with. |
| 20s | Contact: I was there for so long. It was such a big part of my life. |
| 24s | You: I am listening. |
| 28s | Contact: Now I am not sure what the future holds. I do not know what comes next. |
| 32s | You: Okay, we can talk about something else. |
| 36s | Contact: Changing the subject: I am enjoying a new mystery novel. |

Luna started the first analysis at 12.11s and returned the possible McDonald's/rent reminder at**17.83s**, choosing it over exam/resignation distractors. The earlier Terra test returned it at 17.08s. Luna omitted it in its next response despite it still being supplied; Terra retained it at that checkpoint. Both stopped selecting the old memory after the book-topic switch. Existing UI retention can outlast a new empty selection, as configured.

The clearer involuntary-loss variant also selected the right memory at 17.66s. Its later omission had no supplied candidate, so that one was upstream rather than a model miss. The raw trace keeps that distinction visible.

## Search, generated memories and summary

Both models met the frozen expected answer/clarification and citation criteria on **13/15** full-history questions in this run. They handled explicit older/newer losses, awards, trips, appointments and interview outcomes well.

- Luna: one mistyped source ID would cause the application to reject the answer; one vague loss question incorrectly chose the grandfather instead of asking which person.
- Terra: the same vague loss question chose the friend instead. It also answered an ambiguous appointment question with the upcoming appointment rather than the expected clarification. The latter is a reasonable disclosed assumption, but fails this fixture's stricter expectation. Terra had no invalid source IDs.
- Earlier legacy Ask inputs use an older prompt and produced several inline-ID answers that current guards would reject. The current full-history tests above are the more relevant comparison.

Post-call extraction generated six Luna proposals and five Terra proposals. Both included financial difficulty, the regulation/Eden discussion, user feedback and the model-selection plan. Luna still kept generic test/model-improvement material. Terra incorrectly described the landing-page reference as wrong even though the transcript explicitly says it shows CRA. Both could overinterpret garbled wording. More proposals is not automatically better coverage.

Luna's summary was broader but still called the retrieval issue unresolved after an apparent successful retrieval. Terra was more concise and preserved the regulation correction rule, but omitted the recovery and strengthened the garbled model-performance discussion. This single paired call does not establish an overall summary winner; paying about 9× more did not remove the factual-review requirement.

## Splitting models by task

Prototype: Luna low analyzes the current input, then Terra low receives the same grounded transcript/memories plus tentative analysis and generates replies/reminders. Four real two-stage cases were run.

- Luna analysis cost: **$0.00264315** across four cases.
- Terra guidance cost: **$0.02551750**.
- Combined observed cost: **$0.02816065**, compared with **$0.01701470** for the reused joint Terra responses.
- Two-stage latency: **5.3–7.8s**.
- No clear quality gain: the prize reminder was omitted and a previously asked project question reappeared. Some spoken suggestions also assumed more than the transcript established.

**Caching matters:** the old joint Terra requests benefited from cached input; the prototype requests were fresh. Repricing both sets of actual token counts with the same fresh-input assumption gives $0.03526750 joint versus $0.02816065 split, about 20% lower for the split. That is a calculation, not a second API run. The split can save expensive output/prompt work, but its real steady-state savings are not proven by this sample. It adds latency and complexity without a demonstrated quality advantage. Selecting one model for each complete live update is the simpler first option.

## Audit artifacts

All paths are relative to the project root:

- `build/luna-comparison-20260913/audit.md`: exact historical/current requests, expectations and paired outputs.
- `.../corpus.json`: frozen baseline inputs/provenance; `results.json`: main responses and usage.
- `.../paced/results.json`: full timestamped feeds, candidate retrieval, requests, raw/validated/delivered output.
- `.../critical/results.json`: balanced current-prompt repeated memory checkpoints.
- `.../split/results.json`: split prototype and Terra search outputs.
- `.../controlled-revalidated.json`: offline current validation of received controlled-case responses, with no additional API calls.
- `.../manual-paced-assessments.json`: assistant review notes; `ask-checks.json` / `final-accounting.json`: source/status checks and every measured request cost.
- `.../tests.xml`: 268 passing automated tests. The report is an assistant assessment against transcript evidence, not a blinded human study or a user acceptance test.
