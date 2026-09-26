# Supported second tone and ASR-humor mitigation experiment

**Closeout:** After reviewing these results, the user explicitly accepted this iteration as done and authorized commit/push. The production prompt remains unchanged; the candidate is retained for reference only. Earlier no-publication statements below describe the evaluation state before that authorization. Private raw evidence remains local, not part of Git publication.

## Decision

**Keep the saved production prompt. Do not promote this candidate.** More retained labels were visible together, but raw tone production fell and the extra label was unsupported. The user's75% goal, interpreted as at least one populated item, was already met by the saved baseline for tones/cues/responses on this log. Occupancy is not equivalent to useful guidance.

Current working product saved to local main **0ea3584**, no push. Experiment isolated on `codex/tone-coverage-experiment-20260926`. Product Python files remain identical to main. `tools/evaluation/tone_coverage.py` is evaluation-only; nothing imports it during normal app use.

## Candidate and input rules

Only the existing tone paragraph changed: explicitly check for a second distinct supported kind; no quota; factual wording may coexist with warmth/sadness/criticism/emphasis; require coherent independent evidence of deliberate humor/irony when ASR error is plausible. Odd names, homophones, fragments, corrections or another person's reported joke are insufficient. Never repair garbled words into a joke. Existing schema, source grounding, four slots,180s retention, sarcasm vocal-evidence rule and all other instructions unchanged.

User subsequently instructed that **extra prompt-revision tokens must not consume the prior input allowance**. For future comparisons use the existing6000 allowance plus any positive increase in instruction tokens over the frozen baseline; do not remove evidence to accommodate a longer experimental prompt. Output cap1800 and actual API billing/dollar cap remain unchanged. This candidate already fit the old total ceiling with **byte-identical baseline input evidence**, so no restart or extra inference was needed. This is not an implementation of unlimited production input; production instructions are unchanged.

Preparation directories without v4 contain only zero-spend offline checks, no dispatch locks or API answers. The first checks caught different optional trimming and a two-token overflow; the final shorter paragraph fits while evidence is explicitly frozen. These preflight attempts are not inference retries.

## Paid test and provenance

Full150-turn September15 project log,47 recorded checkpoints, Luna5.6low.47/47 fresh candidate replies, **$0.06517699 of one NEW $0.30 cap**, no retries/failures/pending reservations; $0.23482301 remains but is not automatic repeat authorization. Prior saved47 baseline replies reused from `build/humor-replay-20260926/`, whose$0.06201733 ledger is unchanged, as are earlier ledgers. This evaluation's ledger is `build/tone-coverage-20260926-v4/ledger.json`.

Exact request audit confirms identical evidence bytes, model, reasoning, schema, output cap and other request fields; only instructions differ. Both batches used four concurrent workers. Current Qt offscreen replay applies recorded transcript timing, measured arrival latency, in-flight skips, source freshness and180s retention. Not live capture or interactive Computer Use; no raw audio/video analysis. Candidate skips11 busy checkpoints versus4 baseline, so UI differences include latency, not just wording. Raw checkpoint counts below separate this confound. The524.989-second whole-call denominator includes startup and topic resets. No memories were supplied; retrieval/memory quality cannot be assessed here.

## Candidate display and first-display quality

| Section | Nonempty | Empty | Exactly1 | Full4 | Clearly useful | Useful or partial |
|---|---:|---:|---:|---:|---:|---:|
| Tones |93.0%|7.0%|27.4%|0.0%|20.0% (1/5)|80.0% (4/5)|
| Cues & context |93.0%|7.0%|2.2%|83.9%|16.3% (7/43)|60.5% (26/43)|
| Responses |93.0%|7.0%|6.9%|73.7%|2.8% (1/36)|33.3% (12/36)|
| Memories |0.0%|100%|0.0%|0.0%|N/A|N/A|

All84 distinct rendered wordings were individually assessed against the full transcript and supporting source IDs: **9 useful,33 partial/obvious,42 unhelpful**. Scores are primary-agent, non-blinded first-display judgments, not human gold labels, continuous accuracy or independent emotion episodes. Identical label text aggregates repeated events. Numerical precision does not imply generalization beyond this one exposed log.

First output20.3s; tones/cues/responses nonempty96.8% after first output. Any-item75% target passes for those three sections, not for memories, which have no supplied corpus. This does not establish75% useful-time: some retained items are stale or wrong.

## Same-log baseline comparison

| Metric | Saved baseline | Candidate |
|---|---:|---:|
| Tones nonempty |93.3%|93.0%|
| Tones2+ slots |52.1%|65.6%|
| Cues/context nonempty |93.3%|93.0%|
| Responses nonempty |83.8%|93.0%|
| Cues/context full4 |87.0%|83.9%|
| Responses full4 |62.5%|73.7%|
| Distinct rendered labels |4|5|
| Rendered cues/context wordings |73|43|
| Rendered response wordings |33|36|
| Raw tone candidates |47|41|
| Raw replies+follow-ups |41|56|
| Requests with two tones |3|1|
| Requests with no tones |3|7|
| Neutral-plus-another requests |3|0|
| Median batch request latency |5.94s|8.65s|
| Output tokens, including reasoning |21,025|23,660|

Raw tone kinds baseline→candidate: neutral38→30, positive3→5, negative6→5, intense0→1. One sarcasm cue in each, no humor in either. Candidate also returned a withdrawal cue (not enough on its own to infer a valid boundary). More simultaneous retained tones is **not evidence the model generated more tones**: it generated fewer. Retention, timing and a new persistent label explain the fuller panel.

Historical baseline first-display at-least-partial percentages were100% of4 labels,74.0% of73 cue/context texts and33.3% of33 response texts; candidate80.0%,60.5%,33.3%. These are nonblind diagnostic scores, not statistical estimates. Both are single samples per checkpoint; differing latencies/skips and denominator sizes limit causal claims. No post-result prompt tuning or success-threshold invention was used to call this an improvement.

## What was good, and what was wasted

- **Good:** cautious sarcasm for the coherent laptop-at-red-light exchange; current correction/visibility interpretations; a reflection distinguishing not being mad from not wanting to talk to a third party; a concrete reviewable-marketing-output cue.
- **Failed extra label:** “Strongly expressed” justified itself with profanity and self-respect. Its cited contact turns99/103/107 do not contain that profanity; the profanity was in USER turn100. The new label overstates contact affect and remains for144.6s until call end. This is not a useful increase.
- **Wrong facts:** a suggested To Do card location contradicts the user's Deployment answer. Another reply says no difficulty level is listed after the user twice says very high.
- **Role/repetition waste:** product advice to the user rather than user-voice words for contact, old marketing/coding replies after explicit topic shifts, and repetitions of already-spoken explanations.24/36 response wordings were unhelpful initially.
- **ASR guard limit:** neither baseline nor candidate labeled the mouth/mouse confusion as humor. Candidate still greeted a likely misrecognized Mary-hi fragment and invented “I was joking” as a reply to model-name speculation. Therefore this run neither proves humor mitigation nor eliminates invented joking intent outside the cue field. Genuine contextual sarcasm remained, but broader humor recall is untested.
- **Retention:** sarcasm stayed59.5s into lighting/third-party discussion; negative tone persisted111.5s across neutral later material; several cues described questions already answered by delivery. Long retention improves filled time without ensuring relevance.

Next candidate, only if separately requested: explicitly restrict the ASR abstention to humor/sarcasm, prohibit invented joking intent in replies too, and require any second tone to cite contact-owned evidence independently. Avoid treating generic emphasis as emotionally intense. Do not promote this tested prompt merely for fuller panels.

## Verification and review

446 offline tests passed. Evaluation-only regression confirms exactly one paragraph is replaced and the product default remains unchanged. Raw request/usage/hash audit verifies47unique complete requests, conservative reservations, cap accounting, prior-ledger preservation, all150 rendered turns, no application failures, four-slot bounds and all84 assessment entries. Screenshot inspected at900x780; populated slots do not guarantee all text fits every viewport without scrolling.

Exact tool-disabled **Opus5.5 high** reviewed the candidate/evaluation design, no private transcript. No stop-worthy issue; warned about accidental quotas, ambiguous ASR abstention scope, emphasis mapping, nonblind scoring and measured-latency confounds. Those concerns match the caution above. It did not independently assess model answers or audit runner code. Old cue paragraph already said up to two clear cues; candidate's two-cue wording is not a new category limit. Nonblind primary-agent scoring was explicitly requested and remains disclosed.

Private evidence and scripts: `build/tone-coverage-20260926-v4/`, `build/tone_coverage_20260926.py`, `build/render_tone_coverage_20260926.py`, `build/assess_tone_coverage_20260926.py`, `build/rate_tone_coverage_20260926.py`, `build/audit_tone_coverage_20260926.py`, `build/tone-coverage-review-20260926.json`. No automatic repeat, budget reset, main change, push, release acceptance or normal-store mutation.
