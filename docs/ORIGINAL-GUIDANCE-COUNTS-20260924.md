# Original versus current guidance volume — 24 September 2026

Read-only diagnosis from saved evidence; **no API requests or production changes**. The user correctly remembered substantially more output in the original clothing-call test. The earlier answer comparing 16 versus 18 items was about the **recent GPT-6 baseline before/after display fixes**, not the original September 16 GPT-5.6 live run. Calling that recent baseline “original UI, original prompt” without identifying the model/date obscured the much larger historical reduction.

## Same first half: 107 turns, 6m51s, 35 analysis checkpoints

The diagnostic asserts all 35 underlying source snapshots match exactly. Prepared prompts, speaker encoding, schema, sensor trimming and model changed, so this is a historical whole-system comparison, not a model-only causal experiment.

| Category | Original GPT-5.6 raw items | Original logged display, distinct texts | Current GPT-6 raw items | Current Qt replay, distinct texts |
|---|---:|---:|---:|---:|
| Tones | 44 | 33 | 3 | 2 |
| Social cues | 18 | 14 | 5 | 4 |
| Potential replies | 43 | 29 | 15 | 12 |
| Follow-ups | 2 | 2 | 0 | 0 |
| Related memories | 0 | 0 | 0 | 0 |
| **Total** | **107** | **78** | **23** | **18** |

Original: all 35 successful analyses returned something; 34 had tones, 18 had a social cue, 34 had replies. Current: only 18/35 returned anything; 3 had tones, 5 had cues, 15 had replies. Thus there was almost always a **tone**, not a social cue specifically, in the original analysis answers.

For the **entire original 240-turn call**, 71 attempts produced 69 successful guidance answers and two errors. Those answers contained **195 items**: 87 tones, 26 social cues, 79 replies, three follow-ups, zero memories. All 69 successful answers contained something; 68 had tones, 26 had cues. There were 193 distinct raw wordings, because two reply wordings repeated. Original display logs contain 145 distinct texts across the five categories (63/22/57/0/3 in tone/cue/reply/memory/follow-up order). Current full-original-call output has not been measured; do not double the half-call count.

Raw totals count each generated item, including repeats; displayed totals deduplicate wording within category. Original display totals come from `display_interpretation`/`display_guidance` events and inspection of the original formatter, excluding interpretation updates whose explanation replaces their tone/cue body. Current totals come from actual recorded Qt labels with measured API latency. These are not counts of independent useful interventions or simultaneously visible cards; the original 78 items have not all received a fresh quality assessment here.

## Where the large drop happened

**Most occurs before rendering:** 107 original raw items versus 23 current raw items. UI filtering cannot recover the missing 84 generated-item occurrences because the current model never returned them. This is not a formal percentage attribution: model, request format and instructions differ and raw totals can repeat wording.

1. **A measured model effect exists.** A separate already-completed identical-request comparison on the shortest call held prompt/input/schema/output cap fixed. Across 30 paired successful answers, GPT-5.6 versus GPT-6 returned tones in **29 versus 14** cases, social cues in **9 versus 5**, and replies in **28 versus 12**. Its exact-request/provenance checker passed again in this diagnosis. This establishes much lower output frequency in that saved sample, not that every omission is correct or that it explains the entire clothing-call reduction.
2. **Instructions/schema became stricter too.** The actual request diff adds exact contact-turn citations, current substantive-contact anchoring, explicit avoidance of calm inferred from factual fragments, and stronger restrictions on first-person claims/filler. Older compact transcript rows sometimes used null speaker markers; current rows keep explicit roles. The item cap was increased, not decreased. Neither the current four-item cap nor a reduced output-token allowance explains the decline: live output allowance increased from 1,200 to 1,800.
3. **The original model overproduced calm.** Of 44 original half-call tones, **31 were neutral/calm**, 10 positive/warm, three energetic. Examples justify calm by a straightforward request for repetition, a brief pause, a short response or matter-of-fact clothing advice. Current wording specifically disallows inferring calm from those facts alone. The original 18 cues comprised 14 engagement and four uncertainty descriptions. Some are repetitive; some identify reasonable conversational behavior that the current output declines to describe. Fewer outputs cannot automatically be called a quality improvement.

For example, original cues described requesting repetition, comparing clothing options and asking to see a button more closely. Current raw explanations say those clear requests do not support a distinct social-cue hypothesis. That is model abstention, not a hidden UI removal. A useful distinction is needed between speculative emotion claims and plainly observable conversational requests/engagement.

## Exact current 23 → 18 trace

Only five generated items did not reach the current half-call display:

- One cue's checkpoint (index 11) was skipped in the measured-latency simulation because the preceding request was still busy. Its saved API answer exists but would not be requested at that fixed checkpoint under the simulated busy gate.
- One matter-of-fact/neutral-calm tone (index 13) was removed by current evidence grounding.
- Three replies (indices 10, 16, 34) were rejected as `unsupported personal claim`: a repair quoting “I have a—”, “Sure, I'll bring it closer”, and “Let me see if I have green”. The latter two are optional actions/checks, not assertions of an existing personal fact. The shared regex permits “I'll show/clarify/rephrase” but not “I'll bring”, and matches “I have” even inside a conditional “see if I have”. These are concrete over-broad-filter cases, not proof every filtered reply should be restored.

All 18 distinct texts that survived those stages appear in the saved Qt timeline. Although the coordinator recorded ten duplicates and the UI has stability/expiry rules, **they do not explain additional loss of distinct surviving texts in this particular replay**. The broad statement “the UI must be hiding most of it” is not supported here. Other calls and display durations can still be affected by those rules.

## Verification and next step

The diagnosing-bugs skill led to a deterministic saved-trace check before causal interpretation. `.venv/Scripts/python.exe build/trace_original_guidance_counts_20260924.py --expect-no-cue-loss` deliberately fails the no-reduction assertion (5 current cue-bearing answers versus 18 original); plain invocation reports counts successfully. `--details` diffs instructions, lists lost cue examples and replays the four filtered cases with the model request mocked, asserting exact equality with saved pipeline results. No network or new inference is used. The separate `build/gpt6-api-20260922/check_results.py` exact-request audit also passes.

Recommended—not implemented here: correct the narrow optional-action false positives, and evaluate recovering grounded conversational cues separately from emotional labeling. A new controlled old/new-model × old/new-request test would be needed to quantify how much of the clothing-call change comes from each factor. It would require explicit test authorization/budget; no remaining historical budget is automatically reused.

Private evidence: original `build/call-audit-20260916/events.jsonl` and its preserved source; current raw answers `build/half-call-variants-20260924/ledger.json`, current display `build/half-call-followup-20260924-v3/base-ui.json`; model-only comparison `build/gpt6-api-20260922/`. Historical ledgers and outputs remain unchanged. No fixes, reruns, commit or push performed.
