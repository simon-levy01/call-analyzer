# Half-call tone/cue coverage — 25 September 2026

Result: partial improvement only. The best tested revision triples cue texts and increases category occupancy, but does not increase distinct tone texts over the saved visible baseline. No experimental prompt/input revision was promoted this turn.

## Method

User authorized Luna5.6 low real API tests within the same cumulative $0.70 recovery cap. Used the first176.782 seconds of the same88-turn call shown in the preceding visible replay:46 actually ingested turns,14 frozen dispatch checkpoints per candidate. Three candidates made42 attempts:41 completed, one timeout retained conservatively without retry. Baseline14 saved responses were reused, not charged again.

Responses were replayed through the actual Qt label/display code offscreen, with measured API response delays, original transcript ingestion times, source freshness, retention, and single-inflight behavior. This is not another attended live microphone/computer-use run. Inputs were frozen from the previous visible run, not regenerated as a closed-loop adaptive conversation. Simultaneous source-feed turns can swap IDs on app ingestion; final `_display` artifacts use actual transcript events and app-assigned IDs, not original source-feed IDs.

Frozen success target: at least50% more distinct displayed tones and cues, with at least3 extra in each category (therefore15 tones and6 cues). No candidate meets both targets. These are distinct text strings after stripping `Earlier:`, not independent conversational opportunities; semantic paraphrases can still inflate totals.

| Configuration | Tones | Cues | Replies | Memories | Follow-ups | Tone visible seconds | Cue visible seconds |
|---|---:|---:|---:|---:|---:|---:|---:|
| Saved visible baseline |10|3|15|0|1|108.0|65.7|
| Previous-turn coverage changes |5|2|10|0|4|70.9|67.8|
| Explicit eligible-anchor revision |8|9|14|1|5|123.9|123.9|
| Balanced tone-first revision |10|9|14|0|5|137.8|137.8|

Visible seconds means at least one item in that category, including retained earlier items; it does not mean all four slots were full or the content remained useful throughout. Balanced revision: cues+200%, tone count unchanged, tone occupancy+27.6%, cue occupancy+109.7%. This is one realization per request, not a statistical reliability estimate.

## Relevance and limitations

Human inspection of rendered items against the transcript found grounded obvious additions such as financial disclosure, explicit confusion and factual correction. However, multiple financial descriptions repeat the same information. Praise from the ambiguous “good job” exchange is questionable in context. Some regulation observations arrive after the conversation has moved to tracking; garbled transcription remains a source of unsupported interpretations. Therefore the extra nine cues are not nine independently useful new insights, and volume alone is not quality acceptance. No blinded independent usefulness percentage is claimed.

The anchor revision makes the existing grounding requirement explicit to the model: language evidence must include the newest eligible substantive contact turn. Existing filters also reject inferred inner calm unless supported; factual neutral wording is permitted. These mechanisms explain some suppression; the same5.6 model was used throughout, so this comparison is not evidence of a model-version regression. Forcing two emotions per checkpoint would add unsupported content, not solve coverage.

All candidates preserve the exact original speech, memory and sensor payload fields. Anchor candidates only add an eligible-contact-turn ID and revise instructions. Existing source/privacy/freshness safeguards remain. The isolated memory item appears after the word job; no indirect-memory retrieval fix or runtime ONNX fix is demonstrated here.

## Accounting and evidence

Started at$0.35204399. New conservative charges$0.04670692: coverage$0.01772630 (includes$0.00573675 timeout reservation), anchor$0.01534329, balanced$0.01363733. Final cumulative **$0.39875091/$0.70**, leaving$0.30124909. Older reservations, including$0.100238875, remain unchanged. No pending dispatch or automatic rerun.

Private evidence: `build/guidance-recovery-20260924/ledger.json`, `half_visible_coverage_v1`, `half_visible_anchor_v2`, `half_visible_balanced_v3`, and the four `half_visible_*_display` directories. Each contains frozen requests, raw/validated answers or saved baseline provenance, actual-label timelines, screenshots and source hashes. Initial uncorrected render directories are retained but superseded by `_display` artifacts.

Offline check: `.venv/Scripts/python.exe -X utf8 build/audit_half_visible_20260925.py` verifies42 unique arm/case records, actual model/effort, unchanged supplied evidence,46 ingested turns per render and shared cap, and reports label counts/occupancy. No product code changed during this evaluation; previous working-tree changes remain. No commit/push or release acceptance implied.
