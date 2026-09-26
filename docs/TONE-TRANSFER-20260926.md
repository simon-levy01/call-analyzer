# Frozen second-tone prompt:88-turn transfer

## Result

User liked the first experiment and requested testing the **unchanged candidate** on a different log before deciding whether to keep it. Full88-turn September13 log completed. It meets the75% any-item coverage target for tones, cues and responses, and preserves early job-memory delivery, but does **not** demonstrate an improvement over the saved baseline. The ASR-related humor mistake remains and reply usefulness declines. No candidate promotion or further tuning was performed.

The previous closeout was successfully published: local/remote main and the experiment branch were verified at **3ef7d2c**. This new follow-up runs on `codex/tone-coverage-experiment-20260926`; product source and candidate helper remain byte-identical to that checkpoint. Publication of the earlier experiment helper did not activate it in the product.

## Accounting and comparison

31/31 fresh Luna5.6low answers; **$0.04088409 new**. Same authoritative ledger `build/tone-coverage-20260926-v4/ledger.json` now **$0.10606108/$0.30**, carrying the prior47 requests/$0.06517699 unchanged.78 cumulative successful requests, zero pending/retries/failures, $0.19393892 remaining. Do not reset or automatically repeat. Other historical ledgers unchanged.

31 saved baseline responses reused from the earlier sections replay, no baseline API cost. Their original instructions, exact evidence bytes, model, reasoning, schema, output cap and other request fields match the candidate except for the single tone paragraph.6000 baseline input allowance plus positive instruction-token delta is honored; output1800 remains. No price/token/output-limit failure occurred.

Both sets were replayed offline in actual current Qt widgets with recorded turn timing and their measured request latency. Baseline is rerendered because humor is now also displayed in Tones: this adds one label to the old sections report without new inference. Whole-call duration353.563s. Candidate skips7 in-flight checkpoints versus4 baseline. Four-worker batch latency medians8.92s versus5.38s; not a controlled live latency benchmark. One sample per checkpoint, historical reused baseline, exposed log, nonblind judgments: do not infer broad statistical superiority.

## Candidate sparsity

| Section | Nonempty | Empty | Exactly1 | Full4 |
|---|---:|---:|---:|---:|
| Possible tones |82.6%|17.4%|34.5%|5.0%|
| Cues & context |82.6%|17.4%|0.0%|71.4%|
| Possible responses |88.7%|11.3%|0.0%|77.7%|
| Related memories |17.8%|82.2%|17.8%|0.0%|

Two/three-slot time is the remainder. These are time-weighted populated-widget counts, not independent insights, continuously useful seconds or a guarantee all text fits every viewport. Screenshot inspected at900x780; scrolling may be needed for longer content.

Baseline→candidate: tones nonempty87.5→82.6%; cues nonempty87.5→82.6%; responses87.5→88.7%; memories17.5→17.8%. Tone2+slots48.5→48.1%, full4 0.3→5.0%. Cues full4 80.9→71.4%, responses77.9→77.7%. The four-tone peak is not a quality gain: it combines retained downbeat/negative descriptions with an ambiguous good-job warmth inference.

First output16.3→18.6s. After candidate's first output, tones/cues nonempty87.2%, responses93.6%.75% any-item target passes for those sections; memory appropriately follows relevance rather than a fullness quota.

## Everything displayed assessed

Candidate61 distinct wordings:5 labels,26 cues/context,28 responses,2 memory spellings of **one underlying fact**.15 useful,29 partial/obvious,17 unhelpful:44/61=72.1% at least partial at first display. Baseline72 wordings:23 useful,35 partial,14 unhelpful,58/72=80.6% at least partial.71 unchanged baseline assessments were reused by exact category/text; the newly rendered unsupported humor label was separately assessed.

| Section | Baseline useful/partial/bad | Candidate useful/partial/bad | Baseline at least partial | Candidate at least partial |
|---|---:|---:|---:|---:|
| Tones |0/3/3|0/3/2|50.0%|60.0%|
| Cues & context |9/23/4|7/15/4|88.9%|84.6%|
| Responses |13/9/7|6/11/11|75.9%|60.7%|
| Memories |1/0/0|2/0/0|100%|100%|

Candidate clearly useful percentages: tones0%, cues26.9%, responses21.4%, memory spellings100%. These are primary-agent, nonblind first-display judgments against full transcript/source evidence, not independent human gold scores. Label-level aggregation hides per-episode differences. Repeated memory spellings and overlapping context descriptions are not independent gains.

## Important findings

- **Memory preserved:** first job reminder at27.0s/turn7, before explicit job wording58.7s/turn12. Baseline27.9s/turn7. Second spelling appeared53.6s/turn10, not a second fact. Clears at the topic switch. This checks delivery from frozen supplied memory candidates, not a fresh live retrieval/embedding startup test.
- **ASR warning did not solve the target error:** both arms call the ambiguous “EUA island” passage playful wordplay. Candidate also suggests laughing along. Without independent coherent support, this was rated unsupported, not proof of deliberate humor. Candidate humor label stays74.2s versus65.0s baseline.
- **Role/instruction error:** one reply says “Use the latest substantive contact turn only…” and continues with evidence/attribution instructions. It is model-facing advice, not a natural user response, and remains85.9s.
- **Useful output remains:** empathetic optional support, early uncertain job reminder, factual EU CRA correction, and camera-frame explanation. Optimistic cheaper/better acknowledgment is usable.
- **Stale suggestions remain:** Go ahead persists113.5s after initially fitting an unfinished thought; a proposal to clarify AI-versus-CRA repeats an already resolved correction and remains134.7s. Generic hopeful wording and older uncertainty cues outlast their conversational context.
- **No raw tone increase:** baseline31 raw tone candidates→candidate23; requests with two tones5→1, zero tones5→9. Raw replies/follow-ups43→39. Baseline raw kinds sad4/neutral21/positive4/energetic1/negative1; candidate sad4/neutral13/positive3/negative2/intense1. The intense candidate was not displayed in this timed replay. One raw humor cue each. Displayed labels6→5, not increased variety.

Recommendation: keep current production prompt unless the user explicitly chooses the tradeoff. The candidate is usable in parts but not demonstrably better on this transfer; the desired second-tone increase and ASR-humor mitigation are not established. No silent revised prompt, extra API arm or deployment was added.

## Verification

15 relevant offline tests passed; full446-test suite had passed for the same unchanged source in the prior experiment. Exact candidate prompt had already received tool-disabled Opus5.5high design review; no new independent review of this private transfer output is claimed. Raw usage/request matching, all31 unique new requests, prior47 ledger-prefix preservation, conservative reservations/cap, source hashes, both88-turn actual-widget timelines, four-slot bounds, no application failures and every-item assessments pass audit. Production diff versus main is empty.

Private evidence: `build/tone-transfer-20260926/` (baseline88/transfer88 packets, assessments, timelines/screenshots, prior ledger, audit); runners `build/tone_transfer_20260926.py`, `build/render_tone_transfer_20260926.py`, `build/assess_tone_transfer_20260926.py`, `build/rate_tone_transfer_20260926.py`, `build/audit_tone_transfer_20260926.py`. No live capture/interactive Computer Use, normal-store mutation, raw-log publication or acceptance implied.
