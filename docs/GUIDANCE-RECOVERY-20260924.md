# Guidance recovery and historical configuration comparison — 24 September 2026

**Complete: 188 logged real API responses, $0.127793335 recorded charges. Including the conservative $0.100238875 interrupted-replay reservation, $0.22803221 of the $0.70 cap is committed.** Product defaults and production source are unchanged by this evaluation. Luna 5.6 low and Luna 6 low only. Do not rerun completed arms or reset the ledger.

**Best richer live result:** current prompt on Luna 5.6 with the narrow guard candidate: 57 displayed items, 11 clearly useful and 23 somewhat useful (34/57, approximately60%). The historical5.6 rollback shows89 items but only6 clearly useful and38 somewhat useful (44/89, approximately49%); it adds more clutter and stale affect. For lower-cost Luna6, retain the current prompt and use the narrow guard candidate, not the expanded-cue prompt. For the reproduced indirect-memory omission, uncertain-candidate delivery works on both models with the current prompt; Luna6 avoids the extra wrong-person exam reminder observed on5.6. These are recommendations from exposed single-run tests, not automatic product changes or release acceptance.

## What was recovered

The latest saved confirmed **supplied-memory selection** success located is final-check case 259 from the September 13–14 F06 acceptance evidence. Spoken context: uncertainty, rent, years behind a counter, and no paycheck; no spoken word “job.” The approved target memory says Maya lost her McDonalds job, without mentioning rent. The final Luna 5.6 response selected that memory plus an older Oak Cafe resignation as an ambiguous alternative. Seven memories were supplied directly: this was not an end-to-end retrieval success. See [the original acceptance report](F06-AGENT-API-EXPANDED.md).

The earlier paced end-to-end success is documented in [the Luna/Terra comparison](F06-LUNA-TERRA-COMPARISON.md) and [memory-prompt blend](F06-MEMORY-PROMPT-BLEND.md): the easier target memory itself mentioned rent. Those results cannot establish that the real shorter job-only memory was retrieved from all indirect wording.

The latest high-output configuration directly matching the requested original clothing log is the frozen September 16 call-audit source and requests. Its first half has 107 transcript turns, 35 analysis checkpoints, 107 raw items and 78 historically logged distinct visible items. Not every checkpoint had a cue: 18/35 did. Thirty-one of its 44 raw tones were neutral/calm. [Original counts and provenance](ORIGINAL-GUIDANCE-COUNTS-20260924.md).

## Root causes, separated

1. **Model selectivity:** the first new arm changed only the model in the unchanged current request sequence to Luna 5.6. It produced substantially more output than the saved current Luna 6 baseline.
2. **Local guards:** the current personal-claim guard rejects optional “bring it closer” and conditional “see if I have green.” The language-only neutral/calm guard demands literal calm/relaxed wording, hiding practical/matter-of-fact descriptions. An isolated candidate relaxes those specific cases, not attribution, source validity, topic reset or expiry.
3. **Retrieval/ambiguity:** the real cached BGE-small model is available. In scratch retrieval for case259 it finds exams, Oak Cafe and the McDonalds target, marks the set ambiguous, and the UI's background snapshot builder supplies none of those facts to Luna. Lexical-only retrieval finds nothing. This withholding also exists in the frozen September16 implementation: it is not a new Luna6 behavior or solely the Qt migration.
4. **Latency and relevance:** inference can finish after a clarification, rejection or topic change. More raw output is not the same as more useful displayed help. Every comparison uses measured response latency and actual Qt label contents, not raw JSON counts alone.

## Protocol and evidence

Private root: `build/guidance-recovery-20260924/`. Frozen request/input/schema/snapshot/turn files, raw API responses, usage, timings, source hashes, single-use dispatch locks, shared ledger, Qt timelines and screenshots are retained. The first paid arm was current56, exactly as requested. Clothing arms all cover the same107-turn half-call and35 checkpoints. A separate explicitly synthetic32-turn continuation of saved case259 covers the original indirect clue, financial discussion, explicit refusal, book-topic switch, exams, and generic stress. No spoken “job” appears anywhere in that32-turn script. It has16 checkpoints; turns and analysis requests are distinct counts.

The memory candidate changes only the snapshot treatment of ambiguous, approved, eligible retrieval candidates: supply up to four as **low-confidence uncertain candidates**, instead of dropping all of them. It does not fabricate a selected memory, alter approved content, assert event identity, or relax refusal/topic safeguards. The current prompt independently decides which candidates, if any, are relevant. Both models receive the identical candidate inputs.

The new clothing-prompt candidate permits specific observable clarification/comparison cues and neutral practical wording, plus optional immediate actions. Input evidence is held fixed. This is an isolated request experiment, not a production prompt rollout. Historical clothing arms restore the exact saved original instructions, input, schema and output ceiling, with only model routing changed; their saved original backend processes the outputs before replay into the **current Qt presentation**. This is not a reconstruction of the retired Tk widgets.

Quality assessment is non-blinded, by this assistant against transcript context at first display: useful, somewhat useful, or unhelpful (including stale, wrong-speaker and unsupported claims). Correct neutral descriptions and optional actions are allowed; generic accurate descriptions usually count as somewhat useful, not novel insight. Single runs and a reused baseline do not establish statistical superiority or generalization. No fresh acoustic/visual ground truth, microphone capture, computer-use session, or end-user acceptance is claimed.

## Harness incident and budget handling

An initial offline guard replay copied a function's globals, bypassing its model-call mock. It was interrupted immediately after detection; its unlogged outputs are excluded. Exact incurred cost is unavailable, so the shared ledger conservatively retains **$0.100238875**, covering all35 possible Luna6 requests in that interrupted arm. This reservation is not a claim that35 calls occurred. Corrected offline replays block OpenAI client construction and reproduce the existing current6 Qt timeline exactly. The single-use paid runner remains unchanged. Runnable offline checks cover cumulative caps, uncertain reservations, no retries/overwrite, optional-action false positives and unsupported claims. No historical ledger was reset.

## Results

First-display quality on the 107-turn clothing half-call:

| Configuration | Distinct UI items | Useful | Somewhat useful | Unhelpful | At least somewhat useful |
|---|---:|---:|---:|---:|---:|
| Current Luna 6, saved baseline | 18 | 6 | 3 | 9 | 50.0% |
| Current Luna 5.6, new API run | 43 | 9 | 13 | 21 | 51.2% |
| Current Luna 6 + narrow guard candidate, same answers | 21 | 8 | 4 | 9 | 57.1% |
| Current Luna 5.6 + narrow guard candidate, same answers | 57 | 11 | 23 | 23 | 59.6% |
| Observable-cue prompt + guards, Luna 6 | 34 | 8 | 8 | 18 | 47.1% |
| Historical backend, Luna 6, current Qt display | 48 | 3 | 24 | 21 | 56.2% |
| Historical backend, Luna 5.6, current Qt display | 89 | 6 | 38 | 45 | 49.4% |

Neutral descriptions explain much of the extra 5.6 volume. They are not automatically rejected, but usually supply little novelty. The expanded-cue prompt produces 19 distinct cues instead of 4, yet includes already-resolved clarification, completed headphone checks, unfinished-thought labels after the thought was completed, and stale clothing advice during the face-tracking interruption. Do not choose it by volume alone.

Memory-specific 32-turn control:

| Configuration | First job-memory label in Qt | Distinct memory labels | Wrong-person memory labels |
|---|---:|---:|---:|
| Current Luna6, ambiguous candidates withheld | 48.6s, after the later income clue | 4 | 0 |
| Same prompt, uncertain candidates supplied, Luna6 | 33.2s, original rent/paycheck clue | 2 | 0 |
| Same candidate inputs, Luna5.6 | 30.5s, original rent/paycheck clue | 3 | 1 |

The original clue finishes at24s. Thus candidate response-to-display delay is9.2s/6.5s respectively. No model asserted the Oak Cafe alternative or an unrelated bereavement. Both retrieved the target at the original clue. All three UI replays remove the old-job reminder by the explicit refusal and show no reminders during the book or generic-stress sections. The extra5.6 label says **you** have exams, incorrectly addressing the user instead of identifying the contact. The current6 four labels include three paraphrases of the same exam memory; distinct wording is not four distinct memories.

This narrow retrieval repair works with the current prompt on both models, so a rollback to the old memory prompt/affect rules is unnecessary for this reproduced omission. It would not remove the historical ambiguity gate anyway. The later September21 checkpoint05 source-cap success explicitly contains spoken “job,” so it is not evidence of later keyword-free retrieval.

## Cost, latency and verification

| New API arm | Responses | Recorded cost | Median response seconds |
|---|---:|---:|---:|
| Current Luna 5.6 | 35 | $0.03834312 | 6.00 |
| Observable-cue Luna 6 | 35 | $0.01643713 | 6.49 |
| Current memory path, Luna 6 | 16 | $0.00472664 | 6.66 |
| Uncertain memory candidates, Luna 6 | 16 | $0.003566305 | 7.10 |
| Uncertain memory candidates, Luna 5.6 | 16 | $0.01226820 | 4.99 |
| Historical configuration, Luna 6 | 35 | $0.01403098 | 5.01 |
| Historical configuration, Luna 5.6 | 35 | $0.03842096 | 5.95 |

Guard-only ablations reuse exact saved responses and latency, adding zero API cost. The current Luna6 baseline also reuses its saved responses; its previous charge is not rebilled to this evaluation. These sequential single-run latency observations are not a counterbalanced speed benchmark and include differing output lengths/cache behavior.

Two initial historical dispatch descriptors contained a local `schema` logging field rather than the SDK's strict wire format. Both failed in SDK argument binding before HTTP, reproduced with transport forbidden. Their rows and original reservations remain documented, charged at zero; separately named corrected arms used the equivalent strict schema from the frozen original Pydantic class. No paid response was retried, overwritten or repaired.

Passed offline checks:

- `build/check_recovery_20260924.py`: shared cap, uncertain timeout reservations, no retries/overwrite, optional immediate actions and conditional possession accepted, unsupported possession/feelings/commitments still rejected.
- `build/check_recovery_memory_results_20260924.py`: all32 turns/16 responses per memory arm, earlier indirect target display on both candidate models, refusal/book/generic-stress controls, separate wrong-person warning.
- `build/audit_recovery_20260924.py`: frozen requests/source hashes, actual model IDs, output schemas, raw-response/parsed equality, independent provider-usage cost recomputation, settled requests and cumulative accounting; live production source equals the initial frozen source.
- Actual offscreen Qt replay with HTTP client creation forbidden; current6 baseline timeline matches the prior audited replay exactly. Final clothing timelines/screenshots are in `ui-verified-4/`; memory timelines/screenshots are in each memory arm. Item-level assessments are in `clothing-assessment.json` and `memory-assessment.json`.

The original high-output setup is not the best overall choice: its neutral tones often merely restate the exchange, and it revives old encouragement/pauses after rejection, infers tension from ordinary clothing corrections, reverses whose face must stay in frame, and repeats already supplied color information. Targeted recovery improves coverage without reintroducing all those old behaviors. Even the best richer candidate still has23 unhelpful items; further work should target delivery-time relevance rather than demand a cue on every analysis.

No source/default switch, real-store mutation, commit, push, or old-memory-prompt rollback was made. The narrow memory repair resolved the reproduced problem before that conditional rollback was necessary. Candidate guards and uncertain-memory routing remain isolated evaluation code, requiring production integration and broader regression coverage before rollout.
