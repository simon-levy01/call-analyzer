# Guidance freshness and prompt follow-up — 24 September 2026

Completed the user-authorized continuation under the **same cumulative $0.70 Luna-low cap**: **105/105 new real API responses**, **$0.04701935 new spend**, **$0.08055970 cumulative**, carrying $0.03354035 forward including the earlier timeout reservation. No new failures, retries or pending requests. Do not rerun or reset its ledger.

## Results: actual rendered content

| Variant | Shown | Useful | Somewhat useful | Unhelpful | At least somewhat useful | Useful novel additions |
|---|---:|---:|---:|---:|---:|---:|
| Original UI, original prompt | 16 | 5 | 2 | 9 | 43.8% | 3 |
| Applied display fixes, original prompt | 18 | 6 | 3 | 9 | 50.0% | 3 |
| Display fixes + specific-cue prompt | 32 | 10 | 8 | 14 | 56.2% | 2 |
| Display fixes + next-reply prompt | 12 | 4 | 4 | 4 | 66.7% | 2 |
| Display fixes + combined prompt | 32 | 14 | 5 | 13 | 59.4% | 4 |

Root reviewed all **92 distinct rendered texts** against the transcript at actual first appearance. Both original baselines reuse the same saved API answers. The original baseline was regraded with this turn's explicit partial-usefulness category: a timely acknowledgment previously counted as useful now counts as somewhat useful. The earlier report's binary numbers are preserved, not silently replaced.

The **combined prompt is the strongest experimental volume/quality trade-off**: 14 clearly useful items instead of 6 with display fixes alone, and 19/32 at least somewhat useful instead of 9/18. Clearly useful share also improves (43.8% versus 33.3%). However, absolute unhelpful output rises from 9 to 13 and latency rises. The reply-only prompt is most selective but produces fewer useful items, so it does not meet the request for more helpful output.

Novelty is modest: combined has four useful additions beyond acknowledgment/paraphrase (side-by-side comparison, changing lighting, asking about shorts/shirt pairing, and trying a less-formal shirt), versus three in the baseline. This is not evidence of broad creative superiority. Useful cues often highlight a specific current distinction—formality, tentative evaluation or heat—without introducing new facts.

The display-only arm shows **2 tones, 4 cues and 12 replies**. Combined shows **2 tone texts, 16 cues and 14 replies**, but one tone text is the unhelpful literal “No supported hypothesis.” It is counted as unhelpful, not as a successful emotional interpretation. Cue-only shows 1 tone/18 cues/13 replies; reply-only 1/3/8. All arms have no memory or follow-up cards in this half. The model is not being rewarded for manufacturing emotions or memories to fill panels.

Remaining failures cluster around delayed suggestions to show/clarify something already handled, older shirt interpretations appearing during face-tracking setup, generic participation cues, and repeating a color list after the contact asks about green. Some individual suggestions remain useful on arrival but become stale later; the table is **not** a measure of useful screen-seconds. The unchanged 12-second stability delay is part of the measured path and can contribute to lateness. Fixed-checkpoint scheduling and differing measured latency also influence counts: skipped checkpoint indices are baseline [11], cues [11,20,34], replies [], combined [11,13,15,20,34].

**Applied:** narrow duplicate/freshness/supersession fixes below. **Not promoted:** experimental prompts or broader grounding changes. The combined candidate is promising on this exposed clothing call, but its 13/32 unhelpful items, slower delivery, and lack of memory-rich/emotion-rich held-out coverage do not justify silently making it the general default. No additional inference is scheduled.

## Cost and verification

| New prompt | Completed | Actual usage cost | Median API latency |
|---|---:|---:|---:|
| Specific cues | 35/35 | $0.016216860 | 6.65s |
| Next-turn replies | 35/35 | $0.014650745 | 4.53s |
| Combined | 35/35 | $0.016151745 | 7.49s |

Baseline reuse costs $0 this turn; historical baseline median was 3.91s. Costs use recorded usage including cache provenance, not a projection. Models remained GPT-6 Luna low; current [official model documentation](https://developers.openai.com/api/docs/models/gpt-6-luna) was checked. No model/provider fallback.

**373 offline tests pass**, including a Qt widget check of expiry during silence. Exact-input/raw-output/usage/cumulative-budget audits pass. Actual offscreen Qt screenshots and text timelines are saved; a screenshot was visually inspected. This is not native computer-use or a newly captured live call. Exact Opus 5.5 code reviews and follow-up are preserved privately in `build/guidance-freshness-review-20260924/` and `build/guidance-freshness-review-followup-20260924/`.

## Implemented changes

- Duplicate detection includes changed explanations and source IDs, so a genuinely different cue can replace an earlier cue of the same kind/confidence.
- Tone/cue rendering checks the existing 24-second source-age limit and explicit topic resets, including silent polling. No extension of stale content from arrival time.
- A conservative same-subject USER question retires an already-asked suggestion. It does not suppress arbitrary user continuations or alter the CONTACT matching rule.
- Existing grounding, speaker/source validation, calm safeguards and evidence requirements remain in place. No blanket filter bypass or production prompt expansion.

Three regression tests first reproduced failures; fixes passed. Exact Opus 5.5 reviews identified an enum-copy issue and shared-stopword risk; both corrected. Follow-up conditional findings were checked against production: evidence-free candidates are rejected before display, every production GuidedInterpretation sets context_at, and poll_interpretation now revalidates rendering unconditionally. A Qt regression verifies actual cue labels expire during silence. Identical old source IDs intentionally do not renew stale evidence.

## Evaluation design

Same first 410.8749705 seconds, 107 transcript turns and 35 historical checkpoints of the longest saved call. Reuse the previous 35 baseline answers and their measured latencies to isolate code effects without paying to sample a different baseline. Three new compact prompt variants target specific conversational cues, useful next-turn replies, and both together, interleaved by checkpoint (105 requests, Luna low, standard service, no retries, 15-second timeout, 1,800 output-token limit).

Evidence is held byte-for-byte identical to the prior baseline for every variant. Shorter prompts would otherwise allow the input-budget trimmer to retain more sensor rows, confounding the comparison. The variants fit the existing input ceiling with these frozen inputs. Two preparation-only directories (without dispatches) preserve that input-trimming discovery; the paid run is exclusively `build/half-call-followup-20260924-v3/`.

The actual Qt label renderer is replayed with production grounding, coordinator duplicate handling, 12-second card stability, 24-second source-age TTL, speech supersession and topic-reset handling. Simulated time is supplied to render-time checks; current turns are updated as speech arrives. Measured API latency determines arrival; frozen checkpoints while busy are skipped. This is not a fresh microphone/vision run or a reproduction of the adaptive scheduler. No user clicks or memory retrieval rerun. There are no supplied memory candidates in this half; empty Related memories is expected, not a recall-quality finding.

Assess every distinct rendered text against its transcript prefix at appearance: **useful** means grounded, timely, correctly attributed and adds an actionable next step or meaningful distinction; **somewhat useful** means grounded and timely but mostly acknowledgment/redundancy; **unhelpful** includes unsupported, stale/resolved or role errors. Novelty is judged separately, never rewarded over factuality. This is non-blinded development on an exposed call, not held-out accuracy or user acceptance. Unique wordings are not independent opportunities or useful screen-seconds.

Private artifacts preserve exact requests, raw/validated answers, usage, cumulative accounting, source hashes, UI timelines and assessments. No private logs are added to Git. No commit/push or release acceptance is implied.
