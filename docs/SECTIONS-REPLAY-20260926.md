# Section rollout and background replay — 26 September 2026

## Applied on the existing branch

- **Possible tones:** short conservative labels: Positive/warm, Neutral/factual, Downbeat/sad, Negative/tense, Energetic, Strongly expressed. These summarize the existing grounded model kind; no new inference or claim about hidden feelings. Repeated labels collapse visually, retaining the original typed observations and citations.
- **Cues & context:** actual cues carry `Cue:`; original tone descriptions carry `Context:`. No tone is converted into a SocialCue or counted as newly inferred information. Newest support leads; real cues win equal-time ties; four shared slots. Exact duplicate wording is merged. Descriptions remain available in tone popups even if the context panel is full.
- **Possible responses:** existing replies and follow-up questions still share four newest-first slots.
- **Related memories:** unchanged retrieval, eligibility and uncertainty presentation.
- Retention extends **90 → 180 seconds**, without renewing old evidence on omission. Existing topic/correction resets, source invalidation, dismissal, supersession and24-second delivery freshness remain.
- Tone-view dismissal removes all currently retained copies of that displayed label, preventing an older hidden copy reappearing. Dismissing a specific Context observation removes that underlying tone observation from both views. Original model results remain untouched; popups are non-modal frozen copies with existing source checks.

The previous experiment helper remains isolated. This rollout does not apply either experimental prompt rewrite or its overly strong Frustrated mapping. All changes remain on `codex/tone-label-evaluation-20260926`; local main checkpoint9f8b61d is unchanged. No commit/push or user acceptance is implied.

## Fresh API test and accounting

User explicitly requested one additional background API replay under the **same** tone-evaluation cap. Full88-turn log,31 recorded checkpoints, real Luna5.6low, unchanged prompt and evidence,6,000 shared estimated input allowance /1,800 output cap. All31 requests succeeded without retries. Four checkpoints would be skipped while another result was in flight in the recorded-timing UI replay; these paid answers are retained but not falsely counted as displayed.

- New cost **$0.02336722**.
- Prior committed **$0.49871297**.
- Shared cumulative **$0.52208019 / $0.70**; remaining **$0.17791981**.
- All original385 ledger rows, including the earlier timeout reservation, are unchanged. Zero pending requests; no new price, token or output-limit failure.
- Authoritative ledger: `build/tone-eval-20260926-v6/ledger.json`. New rows have stage `sections88`; this is not a reset or a second allowance.
- Private evidence: `build/sections-replay-20260926/`: exact requests, raw/parsed answers, usage, frozen inputs, prior-ledger snapshot, both UI timelines, every-item assessment, occupancy and audit. Single-use runner `build/sections_replay_20260926.py`; do not automatically repeat.

Both90s and180s retention were rendered **offline in actual Qt widgets using the same new paid replies and measured latency**, so the retention comparison incurred no additional API cost. This was background/offscreen replay, not live capture or interactive Computer Use. Whole-call occupancy below describes populated rendered slots, not independent insights or a guarantee all text fits every physical viewport.

## Empty, sparse and full time

“Sparse” means **one item**; “full” means **four items**. Two/three-item time is the remainder. Denominator is the entire353.563-second logged call, including startup and topic resets.

| Section,180s retention | Empty | One item | Four items |
|---|---:|---:|---:|
| Possible tones |12.5%|57.3%|0.3%|
| Cues & context |12.5%|0.0%|80.9%|
| Possible responses |12.5%|0.0%|77.9%|
| Related memories |82.5%|17.5%|0.0%|

After the first displayed result at16.3s, cue/context and response panels were full **84.8% /81.7%** of the time. They were nonempty **91.7%**. Their whole-call four-slot occupancy rose from **75.0% /72.1%** at90s retention to **80.9% /77.9%** at180s. This is approximately20.8 additional seconds of full occupancy in each panel, not90 seconds of new useful information.

The shared empty intervals are startup0–16.3s and topic-reset89.9–117.9s. The latter preserves the explicit subject change; recorded request cadence, in-flight skips and missing useful new output leave a28s gap. Longer retention cannot fill a deliberate invalidation gap without bringing back old-topic items.

Tones usually show one label because the discussion is predominantly factual. Four simultaneous retained tone labels were present for only0.9s and included questionable inferences; filling that panel is not a sensible accuracy target. Do not invent extra feelings merely to use all slots.

The supplied memory corpus has one relevant prior fact for the opening financial topic. It first appears at **27.9s / turn7**, before the first explicit job mention at **58.7s / turn12**. It remains visible for62s and is cleared by the topic reset. No memory is relevant to most subsequent software discussion; longer retention correctly does not make that panel full.

## Every displayed text assessed

71 distinct texts:5 tone labels,36 cue/context texts,29 responses,1 memory. All are individually recorded with first appearance, transcript context, total displayed seconds, Earlier-labelled seconds, first-display grade and lifecycle notes in private `assessment.json`.

Primary-agent, non-blinded judgment against the full transcript:

| Section |Useful|Obvious/partial|Wrong/unhelpful|
|---|---:|---:|---:|
|Tones|0|3|2|
|Cues & context|9|23|4|
|Responses|13|9|7|
|Memories|1|0|0|
|**Total**|**23**|**35**|**13**|

58/71 (81.7%) were at least partially useful **at first display**. This is not a continuous accuracy rate, human gold assessment, per-episode tone accuracy, or proof of improvement. Cue/context paraphrases and labels appear in the displayed-text denominator despite conveying overlapping information.

Useful examples include acknowledging a disclosure, clarifying a factual correction, offering optional support, and the early uncertain memory connection. Failures include ASR corruption interpreted as humor, an ambiguous job-related echo interpreted as praise, a brief exclamation treated as energetic tone, and assistant-like responses directed at the user rather than words the user could say.

### Longer-retention downside

The first-display grade does not excuse later staleness. A waiting suggestion (“Let them finish the thought”) persisted104s after the contact completed the thought. A question about what was rough outlasted the financial explanation that answered it. Landing-page descriptions remained true but lost usefulness during intervening app discussion. These were explicitly annotated rather than counted as useful for their entire lifetime.

Recommendation for a separately approved follow-up: shorter/event-based expiry for tactical waiting instructions and answered questions, while allowing general relevant context and optional responses to use the longer retention. Do not remove topic resets or add unsupported memories/emotions to eliminate blank space. A fuller panel is not necessarily a better panel.

## Verification and review

Qt interaction tests cover labels, context routing, original descriptions in popups, non-modal behavior, dismissal, hidden same-label duplicates, source preservation and tone/cue text deduplication. Updated retention tests preserve boundary/newest-first/no-renewal assertions. Full suite: **428 passed**. Exact Opus5.5high review and follow-up found no confirmed material blocker. Follow-up assumptions were checked: callbacks capture original source indices, existing dismissal has no additional stale-index guard, and tone dismissal removes exactly the indexed original item. A regression assertion covers a second visible label following merged duplicates. New evidence with a new description may legitimately reintroduce a dismissed label.

Opus review found no confirmed material blocker, but caught the hidden-label dismissal issue. That interaction-only fix was applied after inference; original paid source and manifest are preserved in `paid-source/` and `paid-manifest.json`, with an explicit post-inference amendment. Replaying the saved results gives **byte-identical passive UI timelines** at both retention settings. No additional inference was used for the fix. Review also confirmed that known stale waiting advice is a disclosed limitation, not a reason to silently broaden this change.

Raw billing/request hashes, original ledger-prefix preservation, four-slot bounds, all88 turns, no application failures and every-item assessment coverage pass. No release acceptance, normal-store mutation, production ONNX startup repair, additional budget or further automatic evaluation is implied.
