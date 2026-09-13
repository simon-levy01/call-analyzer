# F06: six prompt variants with 1,300 transcript tokens

September 13, 2026. Selected: **priority**, still **gpt-5.6-terra / low**. The source is updated; an already running app must restart to load it.

## What changed

The recent transcript now has its own 1,300 **estimated** token allowance within the existing 180-second window. Whole oldest segments are removed when it fills. The old 16-segment cap no longer cuts off short speech fragments first. Instructions/schema remain billable but do not consume this transcript allowance. F06 has a separate 4,500 estimated total-input ceiling and unchanged 1,200 output ceiling; optional observations and low-ranked memories trim before the transcript would be affected. Legacy standalone F04 request preparation keeps its existing total-input policy. No new dependency or paid context-summary call.

## Actual test coverage

120 real API requests: six frozen prompt variants, ten identical checkpoints each, two repeats per checkpoint. Cases include recorded-call prefixes, repeated questions, old/negated emotion, topic changes, general stress without cause, corrections/preferences, a loss boundary, two dated losses, vague rent wording, a prize and exam stress. Expectations were written before dispatch.

96 additional real API requests: all six prompts each replay the complete available recorded-call timeline plus two new ten-turn fictional conversations. New scripts feed every four seconds through the production adaptive coordinator; first dispatch at 12 seconds, subsequent spacing 10–15 seconds. Actual local BGE retrieval uses the five approved fixture events, including irrelevant exam/quitting/prize/loss distractors. Maximum feed timing error was 0.030 seconds. Recorded-call observations/memories were replayed from the log; the full available transcript prefix was rebuilt under the new budget. No future text was supplied. This is service-level live pacing, not new physical audio/video capture, GUI verification or post-call extraction.

All 216 exact requests, raw responses, validated results and assistant assessments are retained locally. The replay also records delivered results and retrieval at every feed. Five outputs were rejected for an invalid updated/empty interpretation: two checkpoint results and three replay results. These are counted as failures, not successes.

## Six-prompt comparison

Assistant scores: 2 clean/useful, 1 partial, 0 substantive mismatch/failure. These are small exploratory samples judged by the implementing assistant, not independent labels or proof of a universal winner. The memory column counts a relevant Remember card in six positive checkpoint opportunities (rent, prize, exams × two), even if its uncertainty wording needed improvement. False-positive memories are penalized separately in the scores.

|Prompt|Checkpoint score /40|Replay score /32|Memory cards /6|Cost for 20 checkpoint calls|
|---|---:|---:|---:|---:|
|Original|14|17|6|$0.10557|
|Priority-focused (selected)|25|26|4|$0.08961|
|Compact rewrite|20|26|0|$0.07392|
|Separate past/current state|27|19|1|$0.08782|
|Minimal output|29|24|1|$0.07237|
|Evidence self-check|26|20|3|$0.08957|

The minimal-output variant scored highest on frozen checkpoints but missed useful memories, including both new job scripts. Priority is the better fit for this task: it retained tentative layoff cards in both new scripts, avoided irrelevant general-stress memories in both checkpoint trials, and kept current book discussion separate from prior job distress. It produced 11 clean, four partial and one serious replay result. It was about 15% cheaper than the original in both the checkpoint and replay comparisons; checkpoint output averaged 259 versus 370 tokens. Repeated questions and occasional weak cue labels remain.

## New transcripts and memory timing

Both scripts use the same alternating user/contact pattern at 0, 4, 8, …, 36 seconds. Full dialogue, including user acknowledgments and all API output, is in the private replay report. Contact lines:

|Time|More vague script|Clearer script|
|---:|---|---|
|4s|I have been feeling stressed.|It has been a difficult week.|
|12s|I am not sure how I am going to cover the rent.|They said they do not need me on the team anymore, and rent is coming up.|
|20s|I spent so many years there. It was a huge part of my routine.|After all those shifts behind the counter, there is no paycheck coming now.|
|28s|Everything ahead feels uncertain. I cannot picture what comes next.|I did not choose this. I am trying to work out what to do next.|
|36s|Changing the subject: I started a mystery novel and I am enjoying it.|Changing the subject: I started a mystery novel and I am enjoying it.|

With priority, retrieval finds the layoff among distractors at 12s. The vague-script result delivers a **Possibly related** layoff card at **15.55s**, alongside “That sounds really stressful. I’m sorry you’re dealing with that.” The clearer-script card arrives at **17.86s**; its ready replies are suppressed because new speech has arrived. Neither suggested spoken reply names an unconfirmed employer or asks whether the speaker means that memory. The stored layoff memory also contains rent, so this demonstrates hybrid keyword/embedding retrieval, not embedding-only generalization.

At about 24s (through turn 7), both scripts become ambiguous upstream: the two-turn keyword query has lost rent, semantic candidates are close, and the current policy withholds all memories from the API. The API still sees rent in the transcript. This occurs for every prompt and cannot be solved by prompt wording alone. At 36s, the explicit book topic clears retrieval; priority returns book-focused replies/tone at 39.30s / 40.11s. UI card-retention expiry is not measured here.

## Remaining mismatches and price-conscious next steps

1. **Preserve useful retrieval clues locally.** Transcript context and retrieval context are different: keyword search uses two turns; semantic input uses up to eight turns/500 characters. A local experiment widening the keyword query to four/six turns sometimes recovers rent but also changes rankings and loses other useful matches; the first-12-keyword cutoff contributes. That naive change was not installed. A bounded current-topic clue carryover or reranking of ambiguous candidates deserves a separate regression run. It can use local embeddings without another API call.
2. **Question repetition needs explicit handling.** Your original project question is present in every relevant API input, yet four prompts deliver a repeated question in the full replay; a fifth produces a repeated question inside an invalid response. The compact prompt gives a patient acknowledgment in that replay, despite repeating the question in both frozen trials. More transcript alone does not fix it. A narrowly tested acknowledgment-only policy for filler after an unanswered user question could avoid redundant suggestions without another model call.
3. **Shorten explanations without disabling useful memory cards.** The minimal-output variant saves money but its strict remember threshold suppresses useful context. Keep priority’s memory behavior while testing shorter evidence clauses; do not assume fewer cards is automatically better. Stable instruction prefixes already enable caching and should remain stable.
4. **Avoid paid work with no meaningful new contact evidence.** User-only/filler stretches repeatedly trigger paid interpretations and sometimes resurrect old tone. A gate must account for meaningful new vocal/visual evidence and preserve responsiveness; it was not changed here. Across these replays, 23 of 47 validated reply batches were suppressed by newer speech.
5. **Normalize empty interpretation outcomes safely.** Some prompts label empty tone/cue arrays updated; app validation rejects them. A local conversion to evidence abstention could avoid losing otherwise usable guidance, but was not mixed into this prompt comparison. Communication preferences still sometimes become emotional labels, and invented user commitments are sometimes generated then removed.

## Cost and verification

Checkpoint evaluation: **$0.51886980**. Live replays: **$0.47837030**. This round: **$0.99724010**, within the authorized $4 maximum. Persisted F06 aggregate: **$1.70433478**. The aggregate includes earlier tests, not other users of the shared account.

Estimates use returned token usage and the existing configured rates: $2/M ordinary input, $0.20/M cached input, $12/M output including reasoning, and $2.50/M cache-write input. They are not an account invoice or balance. A five-minute conversation at 20–29 analyses projects roughly **$0.10–$0.15 for live guidance** with similar caching/traffic, or **$0.19–$0.28** conservatively if all input is charged at the configured cache-write rate. Post-call review is separate; normal application budget ceilings still apply. For an extra 300 billable transcript tokens, input cost is about $0.00060 ordinary input or $0.00075 cache-write input per analysis; the local transcript budget uses an estimate rather than exact provider tokenization.

All **258 local tests passed in 24.14s** after installing the selected prompt. Checks cover retaining a >1,000-token/30-segment transcript despite instruction growth and whole-turn trimming above 1,300. No implementation commit/release or new final Claude review was performed; manual testing and the existing final review gate remain.

Private artifacts (ignored build directory): `build/prompt-1300-evaluation/checkpoint-report.md`, `variants.json`, `combined-results.json`, `assessments.json`; `build/prompt-1300-live-replays/report.md`, `results.json`, `assessments.json`, `local-query-ablation.json`. Runners: `build/evaluate_1300_prompts.py`, `build/run_1300_live_replays.py`, `build/check_1300_retrieval.py`. Paid runners require updating/rechecking the aggregate cap before a future authorized rerun.