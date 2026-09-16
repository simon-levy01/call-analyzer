# Two-call API comparison — September 15 evaluation

## Outcome

The guidance changes substantially reduce automatic waiting, but do not yet deliver consistently correct, useful replies. Speaker ownership, old-topic carryover, repeated answers and transcription ambiguity remain important failures. Terra Low is cleaner on some memory categories, but is not a reliable factual upgrade across these two calls. Production remains **Luna Low for live guidance, Ask Memory, summaries and memory extraction**. No production code/model switch, memory approval, commit or push was performed in this evaluation.

## Scope, cost and reproducibility

User explicitly selected real API testing with **$0.40 aggregate authorization**. Attempted 94 requests: 78 Luna Low live snapshots (31 older, 47 recent), plus 16 post-call requests (two transcripts × summary/extraction × Luna/Terra × two independent responses). Both models received identical frozen post-call instructions, input, schema and output limit. Comparison order alternated; repeated inputs benefited from provider caching, so repeat billing is not representative of a new call.

**Committed cost: $0.21179406**, comprising $0.20923756 calculated from returned usage plus $0.00255650 conservative charge for one failed Luna answer. This is usage-priced accounting, not a verified provider invoice. No retries, agents, local LLM inference or fallback models. One SDK JSON parse failure stopped the initial run; an explicit continuation preserved every ledger record, retained its charge, skipped that case and continued the remaining schedule. No fresh budget was created.

93 responses passed structured schema validation; the failed live response was truncated JSON. All successful post-call citations reference supplied turn IDs, and successful live responses replay through current filtering without unavailable-source exceptions. Valid IDs and schema do not establish factual correctness. The first failed SDK parse did not expose a complete raw response; the partial failure trace and charge are preserved. Subsequent requests captured raw HTTP JSON before parsing.

Exact private evidence is in `build/two-call-api-20260915/`: original source hashes, frozen source and 82 distinct inputs, pre-run criteria, schedule, raw/parsed answers, usage, response time, before-continuation ledger, offline replay, projections, and non-blinded manual assessment of every successful live output and all 16 post-call outputs. Older Luna live baseline is reused from `build/luna-comparison-20260913/results.json` (`current/actual-call/0..30`); recent baseline is from `build/call-diagnosis-20260915/pairs.json` (0..46). Speech rows/turn IDs match each new snapshot. Old/new prompts and sensor pruning differ intentionally: this is a change comparison, not a model-only live experiment.

No private transcript or raw memory contents are included in this report. Keep build artifacts ignored and transfer them privately if needed on another machine. Do not rerun or reset this evaluation directory. The paid runner is a diagnostic, not a production service.

## Live guidance and facial evidence

| Diagnostic count | Older call | Recent call |
|---|---:|---:|
| Live requests attempted / valid outputs | 31 / 30 | 47 / 47 |
| Historical waiting/continuation-only answers | 14 / 31 | 16 / 47 |
| Revised waiting/continuation-only answers | 2 / 30 | 2 / 47 |
| Revised answers with any reply, before filters | 28 / 30 | 46 / 47 |
| Any reply after current immediate filters | 24 / 30 | 40 / 47 |
| Any reply after source-age/new-speech replay | 22 / 30 | 39 / 47 |
| Median API response time | 8.25 s | 8.34 s |
| Maximum API response time | 16.70 s | 42.34 s |

Waiting counts are a keyword heuristic including pause/listening/continuation, **not a correctness or usefulness score**. Empty replies are valid. Replay applies saved answers to historical snapshots plus measured response duration, source-age expiry and transcript changes; it is not full paced GUI playback or a prediction of exactly what a user would see. The 42-second answer correctly expires in replay. No response-time guarantee follows from these samples.

Examples of useful progress: concrete corrective acknowledgments, a clarification of an ambiguous denial, a contextually tentative humor reading, and recognizing that the USER rather than contact is mid-explanation in recent case41. But new answers also include:

- Congratulating someone on employment when the exchange concerned surfacing a stored job memory. Immediate filtering accepts it; a subsequent explicit topic switch clears it in historical-time replay.
- Treating the user's unfinished bug explanation as the contact's statement and asking the user to question their own explanation (recent13).
- Attributing the user's burden of managing a team to the contact and suggesting a sympathetic reply for the wrong person (recent34).
- Treating refusal to speak **to** a third party as refusal to discuss that person. Recent29/31 partly improve explicit withdrawal wording, but do not consistently preserve the distinction.
- Repeating already-answered questions/statements in paraphrase; exact-string duplicate guards cannot catch all of these.
- Inventing what the user sees, hears or knows; interpreting garbled fragments as greetings; carrying earlier negative tone into a newer topic.

The revised inputs retain visual rows in **all 47 recent snapshots**, versus 12/47 historically. Fourteen recent inputs contain an observable expression configuration. Nevertheless **0/77 successful new live answers cite visual evidence**, versus one historically. This confirms sensor delivery, not useful facial contribution. The old visual citation was itself questionable. No face/no-face ablation or human expression ground truth was obtained; no raw video/audio exists for these logs. Do not force emotion/interest claims just to produce visual citations.

Older live output proposed the supplied job-related memory twice, with one surviving contextual replay. Recent inputs contained no retrieved memories. These are supplied-context checks, not an end-to-end cross-call retrieval benchmark.

## Luna versus Terra after the call

| Area | Result across the two responses per model/call |
|---|---|
| Memory categorization | Terra correctly keeps the temporary third-party dispute as shared reference in both recent runs. Luna labels it a lasting relationship preference in both, despite the new instruction. |
| Routine clutter | Terra excludes greeting memories in both recent extractions. Luna includes one in its first extraction; its second summary also includes routine greeting follow-up. |
| Coverage | Both extract substantive project feedback and code-review advice. Terra misses an important marketing concern in one extraction and includes it on repeat. More proposals is not automatically better. |
| Ownership and grounding | Both make unsupported details or ownership inferences. Luna's repeated older extraction transfers the user's opinion to the contact. Terra's first older summary transfers the user's hope to the contact, corrected on repeat. Both first recent extractions overstate merge-conflict resolution. |
| Summary style | Terra generally stays more concise and avoids unsupported contact gender. Luna uses unsupported contact gender in both recent summaries. Terra still conflates adjacent tasks and reverses the guidance recipient in one summary. |

The completed-work-as-future-commitment error improved, but factual overstatement survives. Terra's narrow memory-hygiene advantage is real in these examples; **consistent factual superiority is not demonstrated**. This is a non-blinded diagnostic of two exposed real transcripts, not a statistical benchmark. Keep memory approval and source evidence visible whichever model is chosen.

## Cost of a 15-minute call

Current official per-million-token rates: Luna $0.20 input / $0.02 cached input / $1.20 output; Terra $2.00 / $0.20 / $12.00. Cache-write input is priced at 1.25× ordinary input by the current accounting; reasoning tokens are already included in output tokens and must not be counted twice. Sources: [Luna model pricing](https://developers.openai.com/api/docs/models/gpt-5.6-luna), [Terra model pricing](https://developers.openai.com/api/docs/models/gpt-5.6-terra).

Measured first-pass **summary plus extraction only**, with uncached inputs:

| Actual transcript | Luna Low | Terra Low |
|---|---:|---:|
| Older, 88 turns / 5.69 min between first and last transcript | $0.0034335 | $0.032511 |
| Recent, 150 turns / 8.51 min between first and last transcript | $0.0054668 | $0.052676 |

The older live pass cost $0.03640575 including the failed-response reservation; recent live cost $0.05143953. Scaling their observed checkpoint rates to 15 minutes gives approximately **$0.091–$0.096 for Luna live analysis alone**. This assumes similar speech, context size, cadence and caching; manual Ask Memory requests, retries and extra manual interpretations are excluded. Local transcription/vision/embedding have no provider per-request fee, but hardware is not free.

**Important long-call discontinuity:** both actual transcripts fit one whole-summary request, but a 15-minute continuation at their densities projects to approximately 232–265 turns and exceeds the existing whole-summary input allowance. Current code then creates 12–14 summaries of at most20 turns and 11–13 pairwise consolidation requests, plus approximately two extraction chunks. It is not just one summary and one extraction.

An offline token-cost scenario using those chunk counts, estimated bounded inputs, cold-cache post-call inputs, the observed mean output lengths for each model, and representative merge input sizes gives:

| Hypothetical 15-minute profile | Older-density scenario | Recent-density scenario |
|---|---:|---:|
| Luna Low live + Luna Low entire post-call stage | $0.125 | $0.133 |
| Luna Low live + Terra Low entire post-call stage | $0.348 | $0.455 |

Practical planning shorthand: **roughly 13–15¢ all-Luna, or 35–50¢ with Terra post-call**, at these speaking rates and under the stated assumptions. These are scenarios, not measured15-minute runs or validated expected-value forecasts. Different chunk output lengths, summary compression, caching and speech density change the bill. A sparse call that still fits a whole summary can be cheaper. No paid chunk/merge or actual15-minute completion was tested.

Conservative maximum reservations for the projected Terra post-call jobs are much higher ($0.883–$1.023, before live analysis), because they reserve full input/output limits. These are not expected charges. The current app call hard cap is $0.35, with a $0.27 live ceiling; a Terra switch would need correct model-aware estimates/reserves and resumable-review checks or processing could pause. Production extraction currently explicitly allows Luna only, and summary calls/default metadata also select Luna: **Terra is not enabled merely by this test**.

## Recommended next work

1. Prioritize explicit speaker ownership, latest-topic relevance and semantic repetition in live guidance. Use the saved failures rather than judging success by reply count. A simple explicit speaker label on every compact transcript row is a candidate to test, not a proven fix.
2. Correct/validate memory categorization and attribution with approval retained; do not assume a more expensive model removes this work.
3. Reduce the long-call summary/merge request count before considering Terra for all post-call processing. Reuse bounded chunks and preserve citations; do not raise production budgets silently.
4. Separately test whether valid, time-aligned facial evidence usefully changes interpretations. Raw signal arrival alone is not evidence of better emotion inference.

No new production fixes were applied during this comparison. **72 targeted offline tests passed**, including guidance lifetime/sensor pruning, memory integration, source filtering, UI and logging. Mock evaluation guards also pass for frozen input, model restriction, cap-before-dispatch, uncertain-charge retention, overwrite rejection and continuation without retry/reset. Claude review and live/manual checks of the earlier production corrections remain pending; this is not F07 completion or release clearance.
