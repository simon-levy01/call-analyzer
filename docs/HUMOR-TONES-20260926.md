# Humor/sarcasm tone presentation and different-log replay

## Applied

Existing validated humor/sarcasm social cues now also display as **Playful / humorous** and **Possibly sarcastic** in Possible tones. Their explanations remain in Cues & context and tone popups. Original types, evidence and model answers remain unchanged. All eight labels share four newest-first slots with label deduplication. Dismissal removes retained observations of that label from the original category and both presentations. Context dismissal still removes only the selected underlying observation.180-second retention and topic/source/correction safeguards remain unchanged.

This is a presentation change, not a prompt or detection improvement. Humor is not inferred from sarcasm. No extra API request is required in normal use. Applied on `codex/tone-label-evaluation-20260926`, not committed/pushed.

## Fresh evaluation

The user authorized a **new $0.30 total cap** on a different log. Replayed all150 turns of the September15 project-discussion call (524.989 seconds), instead of the last88-turn call.47/47 fresh Luna5.6low requests succeeded, **$0.06201733**, zero retries/failures/pending reservations. Remaining allowance $0.23798267 is not authorization for automatic further inference. Earlier ledgers, including the $0.52208019/$0.70 tone experiment, are unchanged.

Frozen historical checkpoints retain their supplied sensor/transcript context. Current request preparation matches the earlier baseline requests exactly:6000 shared estimated input allowance,1800 output cap. The log supplies **zero memory candidates**; this run cannot evaluate current retrieval or memory accuracy. No invented memory was inserted to fill the panel.

Saved fresh answers were replayed offline through actual Qt widgets, grounding/reconciliation, expiry, recorded transcript timing and measured request latency. Four checkpoints (3,29,32,45) would be skipped while a prior request was in flight; their paid replies are preserved but not counted as visible. This is a background recorded-timing replay, not live capture or interactive Computer Use. Request timing came from a four-worker batch and is not an isolated live latency benchmark.

## Sparsity and usefulness by section

Whole-call time includes startup and resets. Full means four populated slots; one item means exactly one; two/three-item time is the remainder. Percentages describe rendered slots, not independent insights or viewport-fit guarantees.

| Section | Empty | One item | Full (4) | Clearly useful | Useful or partly useful |
|---|---:|---:|---:|---:|---:|
| Possible tones |6.7%|41.3%|0.0%|25.0% (1/4)|100% (4/4)|
| Cues & context |6.7%|0.0%|87.0%|15.1% (11/73)|74.0% (54/73)|
| Possible responses |16.2%|10.0%|62.5%|9.1% (3/33)|33.3% (11/33)|
| Related memories |100%|0.0%|0.0%|N/A|N/A|

Usefulness is **non-blinded primary-agent judgment of distinct displayed wording at first appearance**, not independent human scoring, continuous accuracy, or a measured improvement over the previous different call. Labels merge repeated observations;4/4 does NOT mean every tone episode was correct. All110 wordings have individual grades and reasons:15 useful,54 partial/obvious,41 unhelpful (62.7% at least partial overall). The full transcript was inspected for attribution, already-answered questions, ASR noise and delivery staleness. Labels and descriptions can convey overlapping information.

First result appeared20.6s into the call. After it, Cues & context was full90.6% of the time and responses65.1%. Tones had two labels46.8% of the whole call and three5.3%; never four. There is no accuracy reason to force four simultaneous moods into a predominantly factual discussion.

## Which labels appeared?

| Label | Seen in API/UI replay | Distinct-label first-display assessment |
|---|---|---|
| Neutral / factual |Yes|Partly useful; mostly obvious factual discussion|
| Positive / warm |Yes|Partly useful; explicit positive evaluation|
| Negative / tense |Yes|Partly useful; critical wording, later retention can be stale|
| Possibly sarcastic |Yes,25.3s total|Useful cautious interpretation of the laptop-at-a-red-light exchange|
| Playful / humorous |No|No humor candidate returned by the model|
| Downbeat / sad |No|Not inferred; no usefulness denominator|
| Energetic |No|Not inferred; no usefulness denominator|
| Strongly expressed |No|Not inferred; no usefulness denominator|

**All eight labels were verified in offline model-output fixtures and actual Qt rendering/popup/dismissal tests.** That proves their presentation paths work, not that all eight occur in this real conversation. The raw model emitted one sarcasm cue and no humor cue; absence of humor is not a UI filter hiding it. We did not change prompts or fabricate feelings to make the coverage look complete.

## Quality limitations

- Cue/context occupancy is high, but many items merely describe obvious wording. Some questions were already answered by delivery; some ASR fragments became overconfident observations.
- Replies are the main weakness:22/33 were unhelpful. Frequent errors were assistant-style advice addressed to the user, repetition of what the user already said, or late replies to earlier topics.
- The sarcasm label fits this exchange; the accompanying suggested reply claiming the user was kidding was rated unhelpful because it invents user intent.
- Long retention preserves stale content. A bag/laptop clarification outlasted its answer; earlier negative tone persisted into neutral discussion. Usefulness percentages do not credit all retained seconds as useful.
- Compared with the previous88-turn report, cue/context fullness is higher (87.0% vs80.9%) and reply fullness lower (62.5% vs77.9%). This is a different conversation and fresh answers, not evidence that adding the labels caused either difference.

Recommendation: retain this requested display change, but next address delivered-response role/answer freshness and tactical retention. More filled slots alone is not a quality improvement. No additional prompt or retention changes were applied in this request.

## Checks and review

437-test full offline suite passed, followed by8 additional actual Qt label/popup/dismissal cases (445 checks total). Unit fixtures cover all8 labels at179/180-second expiry, source identity, newest-first ordering, duplicate humor group dismissal without deleting unrelated cues/tones, and topic invalidation.

Exact tool-disabled **Claude Opus5.5 high** review found no confirmed material bug in the supplied source. The generic Claude skill wrapper was unavailable because its required AskUserQuestion tool was absent; the existing direct CLI review path was used. Review noted intentional shared dismissal, competition for four slots, and old dismissal-cap/stale-row risks; inspected production tick/offer/invalidation paths synchronously render changes. Review did not independently audit the paid runner or private outputs. Private call logs were not included in the review prompt.

Offline audit verifies source/request hashes, all47 raw usage records, no duplicate dispatch, conservative reservation bounds, cap accounting, preserved historical ledgers, all150 turns, four-slot bounds and all110 assessment entries. Screenshot inspected at900x780. This is not release acceptance, a production ONNX startup fix or normal-store mutation.

Private evidence: `build/humor-replay-20260926/` contains ledger, requests/raw outputs, manifests, actual widget timelines, occupancy, every-item assessment and screenshot. Single-use runner `build/humor_replay_20260926.py`; do not repeat/reset. Review `build/humor-review-20260926.json`. None of these private logs should be committed or uploaded.
