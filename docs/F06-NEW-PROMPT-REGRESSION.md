# F06: new prompt versus the previous results — September 13, 2026

The selected priority prompt with 1,300-token transcript preparation improves current-topic focus and rejects more irrelevant memories, but useful reminder recall regressed. I would keep the larger context and address memory selection before treating this prompt as an overall quality upgrade.

Completed 159 actual API requests: 118 Terra/low live-guidance requests and 41 Luna/none summary, extraction or Ask requests. All 159 have individual assistant assessments against the supplied evidence, with exact inputs and raw outputs retained. This run cost an estimated **$0.47611090 (about 48 cents)**. The persisted F06 aggregate is **$2.18044568**, below the authorized $4 ceiling. These are token-price estimates including cache writes, not an account billing-dashboard reading.

The previous 12 adaptive replay scenarios were rerun, including the recorded call, original vague rent script, five varied memory scenarios, Pepper/corrections/preferences, competing losses, structured-date recency, and generic stress followed by rent. Both newer vague/clearer job variants were rerun too. Fictional messages arrived every four seconds during actual inference; the recorded call used its original arrival times. All 47 old adaptive request prefixes have a matching new prefix. Ten diagnostic checkpoints also received two fresh trials each. The original serialized/fixed-cadence protocols, controlled guidance/summary/Ask cases and custom feedback checks were rerun separately.

| Comparison | Previous results | New results |
|---|---:|---:|
| Old negative tone remains after explicit book-topic switch, 10 matched checks | 9/10 | 0/10 |
| Useful reminders in five-memory sweep, two meaningful checkpoints per scenario | 9/10 | 6/10 |
| Target found locally in that sweep | 10/10 | 10/10 |
| Generic stress-only checkpoint: unrelated memories selected | 2 | 0 |
| Repeated project question at recorded-call turn 5 | Repeated | Still repeated, including both fresh fixed-prefix trials |
| Transcript segments kept at recorded-call turn 30 | 12 | 30 |
| Validated reply batches suppressed by newer speech, matched adaptive scenarios | 12/27 | 9/28 |
| Mean API/service response time, matched adaptive scenarios | 3.98 s | 3.35 s |
| Estimated cost of the same 47 adaptive requests | $0.2112502 | $0.2107187 |

These are observed small-sample results. Historical comparisons combine prompt changes, context preparation, intervening application guards and API variability; they are not a randomized estimate of context size alone. Summary and Ask still use their own Luna instructions, so their changes cannot be credited to the live priority prompt.

The strongest improvement is topic handling. Earlier job strain, grief and exam pressure stopped contaminating the book discussion in all ten matched topic-switch checks. The model also stopped selecting application/course memories in the recorded-call replay, and rejected exam/job distractors when the contact only said “stressed” and “unsettled.” The latter result held in both fresh fixed-prefix trials. Some new tone labels remain weak: enjoyment or a topic change is sometimes called calm, and the explicit two-tone test returned two labels but explained positive_warm using calmness.

The important regression is reminder selection:

| Stored event | Old reminders / 2 | New reminders / 2 |
|---|---:|---:|
| McDonald's layoff / rent | 2 | 2 |
| Loved-one loss | 2 | 2 |
| Photography prize | 2 | 2 |
| Voluntary resignation / relief | 1 | 0 |
| Chemistry/math exams | 2 | 0 |

The initial resignation clue was already blocked upstream as ambiguous in both runs. At the stronger resignation clue, the memory was supplied but the new model omitted it. Both exam memories were also supplied and omitted. The early exam miss repeated in both fresh fixed-prefix trials and in the adaptive replay; the adaptive replay selected it later. This is not a shortage of transcript context: these short prefixes fit both context sizes, and the raw API outputs themselves contain no Remember candidate.

Layoff recall is variable too. The original fixed walkthrough selected its first card at 28.88 seconds previously; this rerun omitted the card at the first strong clue and selected it at 39.73 seconds. In the concurrent vague four-second test, however, the possible layoff card arrived at 16.44 seconds versus the old 20.05 seconds. The adaptive original vague script selected it at 15.72 seconds; the two newer variants did so at 15.86 and 17.56 seconds. Replies offered natural support without naming an unconfirmed employer or asking whether the person meant that memory. Existing retention still kept the walkthrough's last card for about 24 seconds after selection.

The larger context restores useful information, but does not by itself prevent repetition. At the late recorded-call checkpoint the old payload had turns 19–30 and no memory, voice or face data after total-budget trimming. The new payload had turns 1–30 and retained those additional inputs. Its transcript estimate was only 630 tokens; the old segment and total-input limits were also binding, so this is more than a 1,000-to-1,300 token comparison. Total actual input rose from 1,819 to 3,946 tokens at that checkpoint. Across all 47 matching requests, input grew 26%, output shrank 22%, and observed cached cost stayed nearly equal. Charging all input as fresh cache writes would cost $0.3878 versus $0.3697, about 5% more.

Several problems remain visible in the exact-request review:

- Project questions are repeated despite the earlier question being present. Style preferences sometimes become unsupported calm/engagement labels, or lead to another question about the already stated Friday scheduling dependency.
- One raw live response invented “Pepper died” from loss/missing wording. It also emitted transcript-derived reminders without approved memory IDs. The app removed those reminders; they were not delivered or saved. Some high-confidence sadness labels still survive on inferred evidence.
- Retrieval can drop a relevant memory even while its earlier rent clue remains in the full transcript. A competing-loss case also hides one alternative before the model sees it. Structured-date recency correctly supplied only the newer Ada memory, which the model kept explicitly possible; recency does not establish pronoun identity.
- The new post-call project test invented a meeting date equal to the call date, despite no stated meeting date and null original_date_text. That generic-flagged event remains pending. If approved, its guessed date could distort future recency selection. This is a Luna extraction issue, separate from the live prompt.

Post-call and Ask results otherwise preserved the main facts. The Pepper replay produced five pending memories and a prose summary retaining the corrected 4 PM appointment, unagreed Friday plan and short/direct/one-question preference. It did not invent Pepper's death this time, and the summary removed the old inline citation clutter. The generic-only project question produced no summary or memories; the substantive answer produced a project summary/memory. Minor review issues: S03 lost the explicit request to be reminded, and S08 introduced an unsupported pronoun. Ask's 40 cases had correct substantive answers/abstentions and valid sources. Four answers included raw source UUIDs in text, a readability issue also seen previously.

The controlled suite reports **59/60 automatic checks**. Q10 is a false negative: the answer says “3:00 PM” instead of the exact expected substring “3 PM.” The original result is preserved. Automatic checks do not cover all the behavioral issues above.

Local verification completed **258/258 tests** in 25.18 seconds, including basic and HeyGen video decoding/face tracking, audio and progressive transcript fixtures, cadence, stale results, UI scrolling/loading, linked edits/approval and budget checks. Real local BGE Ask passed **40/40**; lexical-only remained **35/40**, with the same five paraphrase misses. Actual GPU transcription plus concurrent CPU face/BGE processing completed 36 baseline and 36 concurrent transcriptions with identical text and no worker failures. This sample had 8.42% p95 slowdown and 90.86 ms concurrent Ask p95. Earlier samples ranged from 6.26% to 13.00%, so consistent performance below the 10% target remains unproven.

The service replays used actual API calls; they were not a physical microphone/WhatsApp/Tk live-use test. The older serialized scripts can delay later transcript delivery while an API call runs; the separate four-second coordinator tests continued feeding independently. New adaptive feed error stayed below 0.071 seconds. The four custom feedback fixtures are equivalent reconstructions because their original exact custom inputs were not retained. All earlier unique scenario families are covered; rejected prompt variants and diagnostic context arms were used as saved baselines rather than rerun as current settings. No application code was changed in this test round.

My next priorities would be to preserve the new topic-focus rules while restoring discriminating exam/resignation reminders, stop semantic question repetition, and reject unstated event dates before they can affect recency. Additional context or a more expensive model is not yet justified by these findings.

Full artifacts:

- [manifest.json](<C:/Users/Banan/Desktop/Programming/Final project call helper/build/new-prompt-regression-20260913/manifest.json>)
- [summary.json](<C:/Users/Banan/Desktop/Programming/Final project call helper/build/new-prompt-regression-20260913/summary.json>)
- [paced-comparison.md](<C:/Users/Banan/Desktop/Programming/Final project call helper/build/new-prompt-regression-20260913/paced-comparison.md>)
- [frozen-comparison.md](<C:/Users/Banan/Desktop/Programming/Final project call helper/build/new-prompt-regression-20260913/frozen-comparison.md>)
- [legacy-comparison.md](<C:/Users/Banan/Desktop/Programming/Final project call helper/build/new-prompt-regression-20260913/legacy-comparison.md>)
- [request-assessments.json](<C:/Users/Banan/Desktop/Programming/Final project call helper/build/new-prompt-regression-20260913/request-assessments.json>)
- [costs.json](<C:/Users/Banan/Desktop/Programming/Final project call helper/build/new-prompt-regression-20260913/costs.json>)
