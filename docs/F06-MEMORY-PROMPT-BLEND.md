# F06 memory prompt revision — September 13, 2026

The revised prompt restores useful reminder recall while retaining the improvement on explicit topic changes. It is a better recall result, but not a clean overall quality win: an unrelated exam reminder appeared during a scheduling/style discussion, and reminders sometimes linger after a verbal boundary. The revised paragraph is installed for further experimentation; it is not a release sign-off.

Only the memory-selection paragraph in `conversation_copilot/guidance.py` changed. Live guidance remains Terra/low with the 1,300-token transcript allowance. BGE-small, retrieval thresholds, cadence, response validation, 24-second card retention, and Luna review/Ask prompts are unchanged.

## Main comparison

| Check | Original prompt / smaller context | Previous priority / 1,300 | Revised blend / 1,300 |
|---|---:|---:|---:|
| Useful reminders, same five-memory sweep | 9/10 | 6/10 | **9/10** |
| Target found locally in that sweep | 10/10 | 10/10 | **10/10** |
| Old negative tone after book-topic switch, same ten checkpoints | 9/10 | 0/10 | **0/10** |
| Irrelevant reminders at generic-stress checkpoint | 2 | 0 | **0** |
| Late recorded-call transcript segments retained | 12 | 30 | **30** |
| First reminder in fixed job-loss walkthrough | 28.88 s | 39.73 s | **28.24 s** |

| Memory | Original reminders / 2 | Previous priority / 2 | Revised / 2 |
|---|---:|---:|---:|
| Job loss / rent | 2 | 2 | 2 |
| Loved-one loss | 2 | 2 | 2 |
| Photography prize | 2 | 2 | 2 |
| Voluntary resignation / relief | 1 | 0 | 1 |
| Exam preparation | 2 | 0 | 2 |

The remaining resignation miss occurs before the API: retrieval finds the target but withholds competing memories as ambiguous. At the stronger clue, the supplied resignation memory is now shown. Both exam misses were also recovered without changing embeddings or context size.

The fresh paired comparison held snapshots and supplied memories constant, alternated variant order, and repeated each variant twice. Across 16 positive opportunities, the previous priority prompt selected the useful memory **9/16**, versus **16/16** for the final blend. Generic-stress controls remained empty in both final-blend repeats. This is a small, deliberately diagnostic sample, not a general accuracy estimate.

Some seven-turn snapshots end with the user requesting a topic change. Those are excluded from positive-recall metrics: withholding a memory there can be correct. Two additional paired checkpoints stop at turn six, before that request, to measure stronger resignation/exam recall fairly.

## What changed and what was rejected

The installed paragraph permits relevant approved memories without requiring an exact name or event label, combines factual clues within the ongoing topic, and asks for “Possibly related:” when identity remains unconfirmed. Generic emotions and retrieval itself are explicitly insufficient evidence. These are general instructions, with no test names, employers, or specific events hard-coded.

An initial, more permissive blend recovered exam reminders but selected unrelated exam and layoff memories in both generic-stress trials. It was rejected. The tighter version restored the factual-clue requirement while preserving tentative recall. Both candidates and their outputs are retained in the audit.

## Live-feed behavior and remaining mismatches

All 14 paced scenarios ran, including the recorded call, original vague rent script, both newer vague/clearer variants, five memory categories, Pepper/corrections/preferences, competing losses, normalized-date recency, and generic stress followed by rent. Fictional messages arrived every four seconds while inference continued; the recorded call retained its original timing and observations.

The three adaptive rent variants first selected a possible layoff memory at **18.95, 16.27, and 16.53 seconds**. The separate fixed-cadence vague replay selected it at **17.08 seconds**. The spoken suggestions offered sympathy or practical support without claiming an unconfirmed employer. These are service response times; existing display retention is separate.

The following failures remain visible in the exact requests and outputs:

- **Irrelevant exam reminder:** selected at Pepper/style turn 17 in the paced replay and in one of two fixed turn-16 trials. Work scheduling and a preference for brief replies do not establish exam relevance. This is an observed false positive, despite the generic-stress control passing.
- **Boundaries and transitions:** Pepper is still displayed after the contact says they do not want to discuss the loss. Several memories remain after the user asks to move on, although they disappear from selection after the contact starts the book topic. The 24-second retained-card behavior is unchanged.
- **Repeated or presumptive speech:** the recorded project question repeats despite the earlier question being present. Friday scheduling questions repeat a stated dependency. Some suggestions assume a remaining shift or offer reassurance about available revision time without enough evidence.
- **Tone and evidence mismatches:** communication preferences or uncertainty are sometimes labeled calm; hesitation can acquire weak sadness/energy labels. One recorded-call job reminder cites user turn 13 instead of the contact's job-loss statement at turn 14. Existing ID validation cannot establish semantic support.
- **Retrieval omissions:** rent can remain in the full analysis transcript while the shorter retrieval query and ambiguity rules yield no supplied memory. A competing-loss case supplies only Ada after dropping Ruth, hiding ambiguity from the model. Normalized-date recency correctly supplies only the newer loss, still marked possible.

All 53 paced requests received API responses. One result was correctly rejected because a topic change arrived during inference. Ten of 32 available reply batches were suppressed by newer speech. Mean response time was **3.35 seconds**, essentially unchanged from the previous **3.36 seconds**. No transport or schema errors occurred across the paid runs.

## Review, Ask, and local checks

The original fixed/serialized protocols, ten diagnostic checkpoints with two repeats, controlled guidance/summary/Ask cases, and custom feedback fixtures were rerun. The controlled suite passed **60/60 automatic checks**; those checks do not cover every qualitative failure above. The previous 59/60 included a time-format false negative, so this is not evidence of a substantive Ask fix.

The actual Pepper review produced five pending memories and a prose summary retaining the loss boundary without inventing death, book enjoyment, corrected 4 PM appointment, unagreed Friday plan, and concise reply preference. The generic-only project exchange produced neither memories nor summary. The substantive project exchange produced a useful project memory and summary, but also reproduced the **unstated meeting date** bug: its extra generic meeting proposal has the call date despite null `original_date_text`. It remains pending. This is an unchanged Luna extraction problem, not caused or fixed by the live prompt revision.

Ask preserved approved facts, conflicts, corrections, scope restrictions, and unknown information. Three answers exposed raw source UUIDs. Summary S03 retained the reminder request this time; S08 still introduced an unsupported pronoun. These variations use unchanged Luna prompts.

**258 automated tests passed** in 23.32 seconds, including video/audio/transcript fixtures and existing UI, budget, cadence, and review tests. This was not a physical microphone/WhatsApp/Tk usability test. The separate resource benchmark was not repeated for a prompt-only change. Custom feedback inputs are equivalent reconstructions; their original exact inputs were not retained.

## Cost and embeddings

Completed **271 real API requests**: 112 paired candidate checks and 159 full regression requests; 230 Terra and 41 Luna requests overall. Estimated cost was **$0.92361810 — about 92 cents**. The tracked evaluation ledger is **$3.10406378 of the authorized $4 aggregate cap**. This includes cached reads and cache writes; it is not an account billing-dashboard measurement or other users' spending.

The same 47 paced checkpoints cost $0.21125 originally, $0.21072 with priority, and $0.19471 with the blend under observed caching. At an all-fresh cache-write assumption, priority versus blend is $0.38780 versus $0.39191, about 1% higher. The observed saving is therefore not proof the prompt is inherently cheaper. A five-minute conversation at 20–29 analyses is roughly **$0.09–$0.13 with similar caching**, or **$0.17–$0.25 with fresh inputs**, including a small review allowance; actual context, output length, and caching vary.

BGE-small is already finding all ten target memories in the diagnostic sweep. A different embedding model cannot directly fix Terra declining a memory that is already supplied. The next retrieval experiment should separate query-window/ambiguity failures from vector ranking. BGE-base is a larger same-family candidate supported by the installed FastEmbed library, but it has not been benchmarked on these conversations. Its model card reports stronger aggregate retrieval results than BGE-small; that does not establish better app-level recall or acceptable concurrent CPU cost. A change would also require rebuilding vectors and validating thresholds. [BAAI model comparison](https://huggingface.co/BAAI/bge-base-en-v1.5).

## Audit artifacts

- [Full request assessments](<C:/Users/Banan/Desktop/Programming/Final project call helper/build/memory-blend-regression-20260913/request-assessments.json>)
- [Paced comparison with original inputs and outputs](<C:/Users/Banan/Desktop/Programming/Final project call helper/build/memory-blend-regression-20260913/paced-comparison.md>)
- [Original diagnostic checkpoints versus previous priority](<C:/Users/Banan/Desktop/Programming/Final project call helper/build/memory-blend-regression-20260913/frozen-comparison.md>)
- [Legacy, review, and Ask comparison with both baselines](<C:/Users/Banan/Desktop/Programming/Final project call helper/build/memory-blend-regression-20260913/legacy-comparison.md>)
- [Fresh paired final-candidate requests](<C:/Users/Banan/Desktop/Programming/Final project call helper/build/memory-prompt-blend-v2-20260913/frozen-checkpoints.json>)
- [Paired stronger clues before topic change](<C:/Users/Banan/Desktop/Programming/Final project call helper/build/memory-prompt-blend-v2-strong-20260913/frozen-checkpoints.json>)
- [Rejected permissive candidate](<C:/Users/Banan/Desktop/Programming/Final project call helper/build/memory-prompt-blend-20260913/frozen-checkpoints.json>)
- [Per-request cost estimates](<C:/Users/Banan/Desktop/Programming/Final project call helper/build/memory-blend-regression-20260913/costs.json>)
- [Machine-readable totals](<C:/Users/Banan/Desktop/Programming/Final project call helper/build/memory-blend-regression-20260913/summary.json>)
