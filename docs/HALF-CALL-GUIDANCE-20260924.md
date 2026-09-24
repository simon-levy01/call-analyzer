# Half-call guidance and rendered-UI comparison — 24 September 2026

Completed the user-authorized Luna low API comparison: **70 attempts, 69 complete answers, one un-retried timeout; $0.03354035 committed under one $0.70 cap**. Known usage cost is $0.030460975; the timeout retains a $0.003079375 conservative reservation. No pending requests, automatic repeat, production changes, commit or push.

## Scope and method

Used the first **410.8749705 seconds (6m51s), 107 turns and 35 recorded analysis checkpoints** of the longest of the three previously evaluated saved calls (240 turns, 13m42s). Original recorded vocal/visual measurements were included. No audio, vision or retrieval rerun. This half contains clothing advice, color/camera disagreements and face-tracking interruptions; it has **no supplied memory candidates**. Empty Related memories is expected and cannot establish memory-recall quality.

Two API prompt families were interleaved by checkpoint, using GPT-6 Luna low, standard processing, strict structured output and a 1,800-token output cap. Baseline answers were reused exactly across post-processing variants; these are not independent additional model samples. The added prompt encouraged specific engagement/clarification and useful optional replies without filler. It retained the same input evidence. Its expanded instructions would exceed the current app's 5,000 estimated-input-token ceiling in 28/35 checkpoints (maximum 5,383); deploying it would require compacting the prompt or explicitly changing that allowance. Neither was changed in production.

Actual production grounding, response reconciliation, coordinator acceptance/duplicate handling, display state and Qt label rendering were exercised offline. The timeline records actual QLabel text at 100ms simulated intervals, including empty periods. Measured API latency determines arrival; historical checkpoints occurring while a simulated request is busy are skipped (baseline case 11; revised prompt cases 16 and 22). This is a controlled fixed-checkpoint simulation, **not** a new live capture or a reproduction of the current adaptive scheduler. No user dismiss/refresh clicks were simulated. Qt ran offscreen with explicit Windows font registration; source-code and request/input hashes are preserved.

## Results judged at display time

The root assistant assessed every one of the **57 distinct texts rendered across variants**, using the transcript prefix at first appearance. “Useful” requires correct attribution, support and current relevance; other labels distinguish stale/resolved, unsupported/role errors and redundant/generic items. This is a non-blinded, exposed-case qualitative assessment—not a human gold set, accuracy benchmark or user acceptance. Counts are unique wordings, not independent conversational opportunities or useful screen-seconds.

| Variant | Visible texts | Useful | Stale | Unsupported | Redundant/generic |
|---|---:|---:|---:|---:|---:|
| Current baseline | 16 | 6 | 8 | 1 | 1 |
| Bypass newer grounding | 17 | 6 | 8 | 2 | 1 |
| Gentler grounding | 16 | 6 | 8 | 1 | 1 |
| Revised prompt | 28 | 11 | 12 | 3 | 2 |
| Revised prompt + gentler grounding | 28 | 11 | 12 | 3 | 2 |
| Display handling only | 18 | 8 | 8 | 1 | 1 |
| Prompt + gentler grounding + display handling | 39 | 15 | 15 | 3 | 6 |

Gentler grounding allows cited substantive contact evidence within 45 seconds rather than requiring the latest contact anchor within 24 seconds; other speaker/source/modality checks remain. The display experiment includes changed explanation/source IDs in duplicate detection and starts the guidance expiry clock at arrival. Those two display changes were tested together, not independently. All arms retain ordinary empty-result replacement, speech supersession and topic-reset handling.

Baseline had **1 tone, 3 cues, 12 replies** visible; the combined version had **1 tone, 24 cues, 12 replies and 2 follow-ups**. Cue-panel occupancy rose from **47.1 seconds to 293.2 seconds**. That is availability, not relevance: several extra cues were generic restatements, stale requests to show an item already assessed, or clothing suggestions continuing through face setup. Useful combined cues included tentative evaluation, concrete participation in comparing alternatives and the current formality concern. The bypass-only extra tone was unsupported calm inferred from ordinary practical advice.

The current minimum-display/queued-update behavior, stale evidence in some recorded snapshots and response latency can make a valid-at-request-time suggestion obsolete on arrival. Longer retention alone does not solve this. Some items judged useful at first appearance also became stale later; the complete timeline preserves this and the count table does not claim otherwise.

## Recommendation

1. **Do not disable grounding wholesale.** It added no useful output here and admitted an unsupported tone. Gentle grounding did not increase distinct useful output either.
2. **Prioritize refreshing genuinely changed explanations.** The bundled display experiment added two useful items without additional bad ones in this segment. Before shipping, isolate the duplicate fix from expiry changes; do not indiscriminately lengthen stale cards.
3. **Use a narrower cue-focused prompt, not the entire expanded prompt as-is.** Specific engagement and hesitation cues have promise, but generic restatements, stale suggestions and speaker-direction errors increased. Fix display-time freshness/topic handling before adding more volume. This next refinement is a recommendation, not a tested or implemented winner.
4. **Do not force more emotional tones.** This practical conversation offers much stronger evidence for conversational engagement than emotion. Evaluate memory recall separately with genuine approved-memory context.

The display-only variant is the cleanest observed incremental improvement; none of the variants is a complete quality fix. No production prompt/filter/default changes were applied.

## Cost and evidence

Baseline: 35/35 complete, **$0.01474436**, median successful response **3.91s**. Revised prompt: 34/35 complete, **$0.01879599 committed** including the timeout reservation, median successful response **5.41s**. These are single serial samples per checkpoint with differing caching, not a stable latency benchmark. Pricing follows [official GPT-6 Luna documentation](https://developers.openai.com/api/docs/models/gpt-6-luna); totals are usage-priced estimates, not provider-invoice reconciliation.

Private Git-ignored evidence: `build/half-call-variants-20260924/` contains the frozen manifest/rubric/source, 70 requests, 69 raw responses, ledger, per-variant `*-ui.json`, screenshots, `rendered-timeline.html`, all 57 item judgments in `root-assessment.json` and aggregate `assessment-metrics.json`. Do not upload these private call records. The original historical ledgers are unchanged.

Offline checks: `build/audit_half_call_variants_20260924.py` verifies source/input/request integrity, response/parsed equality, provider usage accounting and the cap. `build/render_half_call_variants_20260924.py` regenerates actual Qt content without inference; `build/assess_half_call_variants_20260924.py` preserves explicit root judgments. Never rerun the paid dispatch command or remove its single-use lock.
