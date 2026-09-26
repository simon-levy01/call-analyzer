# Tone labels and section audit — 26 September 2026

## Status and preservation

The user-requested checkpoint is committed to **local main at `9f8b61d`**. Experiments are on `codex/tone-label-evaluation-20260926`. No push was requested or performed. Unrelated CV PDFs were excluded. Real contact data, previous ledgers, saved summaries and imports were not regenerated or modified.

The subsequent user-approved live input allowance is **6,000 estimated tokens shared across instructions, schema and context**. Live preparation no longer prematurely applies the legacy separate memory allowance; the final shared trim still protects the transcript, uses existing sensor floors, and discards lowest-priority memory rows first. Output remains 1,800 tokens. This is not a 6,000-token output allowance or an input-plus-output ceiling. All comparison arms used the same new allowance. Standalone legacy interpretation retains its earlier limits. Snapshot size, privacy, contact eligibility, four-item limits and retention are unchanged.

**No experimental tone prompt or presentation has been promoted into normal UI behavior.** The experiment helper is deliberately isolated in `tools/evaluation/tone_labels.py`.

## Experiment

Real `gpt-5.6-luna`, low effort, one new **$0.70 aggregate cap**:

- Search: full 240-turn outfit log / 71 recorded checkpoints, and full 150-turn project log / 47 checkpoints.
- Arms: current prompt; explicit label-first prompt; independently separated affect/conversation-meaning prompt. Every arm receives the exact same bounded evidence at each checkpoint.
- Fourth arm: display-only mapping of current answers into short labels, retaining original descriptions in the cue panel. Reuses baseline answers and latency, not additional model calls.
- Winner selected and assessment hashes frozen before validation: display-only mapping.
- Validation: full third 88-turn log / 31 checkpoints. Current versus mapped reuse the same new paid responses, appropriately isolating the presentation change. Local retrieval uses the previously approved pre-call corpus identically for both.
- Actual Qt label widgets replayed with recorded turn timing, measured response latency, busy-checkpoint skips, grounding, delivery expiry, retention and topic resets. This is an offline saved-response UI replay, not a fresh microphone/video call or interactive Computer Use acceptance test.

Private evidence: `build/tone-eval-20260926-v6/`. Earlier preparation directories contain no dispatches. Runners: `build/tone_eval_20260926.py`, `build/continue_tone_20260926.py`, `build/render_tone_20260926.py`, `build/review_tone_20260926.py`, `build/assess_tone_20260926.py`, `build/select_tone_20260926.py`, `build/audit_tone_20260926.py`. Do not repeat any dispatch or reset the ledger.

## Results

Numbers below are distinct displayed wordings, with the `Earlier:` prefix normalized. Short labels collapse many descriptive tone sentences into fewer distinct labels, so these are **not comparable counts of independent tone detections**.

| Log / arm | Tone wordings or labels | Cue-panel texts | Responses | Memories |
|---|---:|---:|---:|---:|
| Outfit / current | 45 | 48 | 66 | 0 |
| Outfit / mapped | 2 | 93 | 66 | 0 |
| Outfit / labels prompt | 3 | 79 | 68 | 0 |
| Outfit / split prompt | 3 | 65 | 49 | 0 |
| Project / current | 29 | 39 | 48 | 0 |
| Project / mapped | 4 | 68 | 48 | 0 |
| Project / labels prompt | 4 | 59 | 42 | 0 |
| Project / split prompt | 4 | 61 | 37 | 0 |
| Validation / current | 18 | 16 | 28 | 1 |
| Validation / mapped | 4 | 34 | 28 | 1 |

Mapped adds **no new model information**: its cue-panel increase is relocated tone wording, not independently inferred/validated social cues. All baseline tone descriptions survived in the mapped processed updates in these logs. Exact response and memory timelines are identical on all three logs. Tone occupancy is identical too: approximately 94%, 93% and 81% of each full log. The historical near-empty UI is not reproduced by these current-code replays; this does not prove all real capture paths are healthy.

The third-log job memory first appears at **55.8 seconds / turn 11**, before the first explicit job mention at **58.7 seconds / turn 12**. It remains visible for 34.1 seconds before context handling removes it. This confirms preservation in this recorded-checkpoint replay, not a new claim about production ONNX startup or every indirect-memory case. Earlier successful live-demo timing was different and is not overwritten.

### Relevance assessment

Primary-agent, non-blinded assessment of each distinct first-displayed text against transcript context. Useful=2, correct but obvious/redundant=1, wrong/unsupported/stale=0; false tone claims have an extra penalty. Relocation preserves the original wording's grade. These are descriptive judgments, not human gold labels, per-episode emotion accuracy, significance tests or independent evaluations.

| Two-log pooled arm | Useful | Obvious/partial | Wrong/stale | At least partial |
|---|---:|---:|---:|---:|
| Current | 96 | 135 | 44 | 84.0% |
| Mapped | 100 | 135 | 46 | 83.6% |
| Labels prompt | 75 | 141 | 39 | 84.7% |
| Split prompt | 71 | 106 | 42 | 80.8% |

Frozen selection scores: current319, mapped331, labels287, split242. The scoring advantage for mapped is substantially a presentation/counting artifact, **not improved reasoning**. Prompt revisions did not provide a compelling joint volume/quality improvement. The outfit labels arm includes one timeout; it is separately retained, so this is not a fully matched successful-answer comparison.

Third-log assessment: current20 useful /29 partial /14 wrong (77.8% at least partial); mapped22/29/16 (76.1%). The two added supported labels and two overly strong labels explain the difference; all original wording remains. **Validation does not establish an accuracy improvement.** Examples of failure classes include interpreting ASR corruption as a joke, treating an ambiguous job-related echo as praise, mapping financial difficulty to frustration, and occasional user/contact role reversals in replies.

## Section recommendations

1. **Possible tone:** concise, cautious wording labels, not claims about hidden feelings. Neutral/factual, warm/appreciative, downbeat/sad, negative/tense and energetic are a safer starting set. Happy/pleased, worried, excited and hesitant need specific supporting evidence; asking a question alone is not proof of curiosity or anxiety. Avoid automatically translating every negative observation into “frustrated,” or personal wording into “emotionally intense.”
2. **Cues & context:** retain relevant disclosures, corrections, requests, boundaries, uncertainty and short conversational observations. Distinguish an inferred social cue from a relocated factual observation; do not count both copies as extra insight. Tone reasons that merely repeat a cue should be merged or remain accessible as detail rather than filling another slot.
3. **Possible responses:** keep follow-up questions and optional actions together, as currently implemented. Do not reintroduce a separate follow-up panel. The tests still show speaker-role errors; changing tone prompts is not a reliable fix for those.
4. **Related memories:** keep separate, with the existing uncertain-connection language and provenance boundaries. No changes are recommended from this experiment.

**Humor / possible sarcasm** fit as communication-style cues, not emotions. The project log already produces a cautious sarcasm cue with the current method; both prompt variants also produced one. The validation log exposes an ASR-as-joke error. Therefore no automatic sarcastic/happy label should be inferred from mere praise, isolated fragments or text punctuation.

Recommended next implementation: retain the current prompt and add conservative tone labels with explicitly categorized Context observations. Do not ship the experimental mapping unchanged. It can overstate labels, accepts only one exact label separator, and can omit a relocated detail if all four cue slots are already occupied. No such detail overflow occurred in the audited mapped runs, but the hypothetical failure remains. Tone-derived observations have not undergone independent cue-specific grounding and must not be advertised as new validated cues.

## Cost and verification

- **385 attempts, 384 responses, one un-retried timeout.**
- Recorded response charges: **$0.49173747**.
- Uncertain timeout reservation retained: **$0.00697550**.
- **Total committed: $0.49871297 / $0.70**; zero pending requests.
- First search paused at $0.29589581 because it reserved all future validation maximums simultaneously. A separately locked continuation dispatched only the116 never-attempted search jobs under the same ledger, retaining all prior charges/reservations and full per-request worst-case reservations. Its smaller validation planning hold did not raise the hard cap. Validation added31 requests.
- Raw requests match frozen inputs; source/case hashes, model/effort, output allowance, usage counts, no duplicate dispatch, accounting and UI response/memory parity audited.
- **425 offline tests pass**; the mixed memory/sensor boundary test also checks exact transcript text, low-rank trimming and the real request preflight without dispatch. Opus5.5high code/design and correction reviews performed through tool-disabled Claude Code with code and aggregate findings, not private call logs. Its list-price usage estimate is not part of this separately authorized Luna API ledger. No confirmed product blocker was found. The shared input-budget change is a product-code change on the branch and was used by all paid arms; experimental tone prompts/presentation remain isolated. All claims of mapped parity describe a controlled reuse of identical answers/latency, not independent model behavior. Hypothetical sensor-order/absolute worst-case snapshot boundaries were not exhaustively enumerated by this evaluation; existing failure handling and snapshot bounds remain unchanged.
- Native UI behavior outside saved-response rendering, emotion accuracy, and product acceptance remain unverified. No further inference is authorized automatically by the unused cap.
