# Richer Luna 5.6 rollout and full-log transfer — September 24, 2026

Applied on `codex/qt-ui-migration`, at the user's explicit request. No commit, push or release acceptance is implied. This supersedes the earlier recommendation-only status, not its historical evidence.

## Applied behavior

- All product Luna routes now resolve through `LUNA_MODEL = gpt-5.6-luna`, low effort: live interpretation/guidance and Ask Memory. Sol remains the higher-end selectable option and the independent summary/memory-generation default. Historical model IDs and both Luna price records remain intact. The home estimate uses the selected model's price; its logged workload remains an illustrative proxy, not a new billing guarantee.
- Keep the current prompt. Apply the tested optional-immediate-action and neutral/practical-description guard changes, tightened after review to reject invented chained/future commitments and unsupported claims of internal calm.
- Supply approved, cloud-eligible ambiguous retrieval candidates as explicitly uncertain, low-confidence context. Do not expose ambiguous matches as confirmed direct memories. Memory-backed tones/cues also inherit low confidence. The UI marks uncertain connections; existing uncertainty wording is not prefixed twice. Private/local-only facts stay local, and source/approval checks remain.
- All five categories retain up to four entries, fresh items first. Older entries fill unused slots for up to **48 seconds from source support**, marked **Earlier**. Omission and repeated old evidence do not renew them or move them above new entries; repeated evidence can lower confidence. Different wordings citing the same remembered fact occupy one slot. Dismissal, source changes, topic resets and refusals still remove entries. Incoming results older than 24 seconds remain rejected.
- First automatic analysis is eligible after **6 seconds**, instead of 12, subject to available contact speech and the existing coordinator. This is request timing, not a promise of a result at six seconds. First rendered content was at 12.0/12.6 seconds in these replays.
- Check every newly arrived turn for invalidation, including batched speech. Wrapped suggestion rows now reserve their actual text/button height rather than clipping as retained rows accumulate. The existing small-window scroll fallback remains; this is not a guarantee that twenty long suggestions fit simultaneously in a compact window.

## Full other-log results

The complete 150-turn and 88-turn calls were replayed through actual Qt labels, current guards, measured API latency, busy-request suppression, expiry, dismiss/source rules and fresh local retrieval. These are saved-call simulations, not a newly recorded microphone/video call.

The previous column is the saved current-prompt **Luna 6** baseline from [the earlier transfer evaluation](PROMPT-SEARCH-TRANSFER-20260924.md). Multiple components changed here, so this is not an isolated model-only A/B test.

| Measure | 150-turn call: previous → applied | 88-turn call: previous → applied |
|---|---:|---:|
| Distinct rendered texts | 25 → **78** | 19 → **45** |
| Tone texts | 6 → 21 | 4 → 12 |
| Cue texts | 4 → **14** | 3 → **8** |
| Potential replies | 13 → 37 | 11 → 21 |
| Memory texts | 0 → 0 | 1 → 3 |
| Follow-up texts | 2 → 6 | 0 → 1 |
| Clearly useful | 8 → 3 | 4 → 5 |
| Somewhat useful | 8 → 29 | 8 → 24 |
| Unhelpful/late/unsupported | 9 → 46 | 7 → 16 |
| At least somewhat useful | 16/25 (64.0%) → **32/78 (41.0%)** | 12/19 (63.2%) → **29/45 (64.4%)** |

Among the new cues, **6/14** in the first call and **5/8** in the second were at least somewhat useful. These were modest grounded observations, not clearly novel insights under the rubric. More cues does not automatically mean better cues.

**Bottom line:** the requested richer setup supplies substantially more material and more at-least-somewhat-useful items. It is **not a consistent quality improvement**: precision and clearly useful additions deteriorate on the first call. Late responses, repetitive acknowledgments, garbled transcription interpreted as greetings/jokes, and occasional speaker-role confusion remain important weaknesses. Longer retention can keep these weak suggestions visible too. The user-requested setup is applied, but these results do not justify claiming it is universally better or reliable enough to infer feelings as facts.

### Memory result

The second call displayed a **possible job-loss memory at 22.6 seconds**, while the first spoken occurrence of “job” was at **58.7 seconds**. Its three memory texts are three phrasings of **one approved fact**, not three recalled facts or independent successes; same-memory variants no longer occupy multiple slots at once. The first call's late marketing/job lexical match did not produce an irrelevant job-loss reminder.

Initial frozen-retrieval replay produced no displayed memories in the second call: one raw reminder arrived at a checkpoint skipped as busy. Therefore a second, local-only retrieval pass used the current semantic model and the known approved corpus in an in-memory store, over each complete historical prefix. The single corpus record was proven to exist before both calls using the September 13 pre-call retrieval and the September 15 corpus/approval evidence. No future call content, real contact database mutation, or invented memory was introduced. Semantic retrieval was available throughout.

Fresh retrieval changed six requests (one first-call, five second-call). Those six received new API responses; the other **74 exact requests reused their saved raw responses and latency**, with explicit bindings. This verifies the current end-to-end retrieval-to-display route. Neither real log produced an ambiguous retrieval verdict, so the transfer improvement does **not isolate the ambiguity patch**. Its low-confidence delivery/privacy behavior is additionally covered by regression tests and the earlier paid 32-turn [uncertain-candidate control](GUIDANCE-RECOVERY-20260924.md).

## Cost, method and limitations

- **86/86 new real API responses completed**, no retries/failures: 48 + 32 initial full-log checkpoints, then six changed-input checks. Earlier first-eligible checkpoints were added to the historical schedules. Median observed response time: **5.58 seconds**.
- New charge: **$0.09188278**. Original shared recovery ledger is now **$0.31991499 / $0.70**, including the unchanged **$0.100238875 uncertain reservation** from the earlier interrupted replay. No ledger reset or reservation release. No further automatic API calls authorized.
- Frozen requests, strict schema, raw responses, standard-service model identity, low effort, token usage, prices and exact reuse bindings were audited. Paid dispatch remains single-use with pre-request budget reservation, 15-second timeout and zero retries.
- Final replay busy checkpoints: first call `[4, 8, 13, 16, 37]`; second `[1, 8, 17, 20]`, zero-based in their final manifests. Outputs from those checkpoints were not counted as displayed. Call ends were not extended to expose more results.
- Timing uses historical checkpoints plus the earlier eligible first checkpoint, not a complete reconstruction of live adaptive scheduling. Actual sensor capture, recognition quality and the operating-system window compositor were not retested.
- Counts are distinct rendered wordings per category, not independent interventions. The **Earlier** prefix is stripped only for counting; the exact labels are preserved. Paraphrases can still increase counts. A label may be below the existing scroll viewport in a small window; these are render-state counts, not eye-tracking or proof every text was simultaneously on screen.
- Every distinct text was assessed against the available transcript prefix at its first display. This is a non-blinded root assessment: useful next step / somewhat useful grounded but modest text / unhelpful, late or unsupported. Correct neutral wording is allowed. It is not independent human validation, a statistical accuracy estimate, or a measure of relevance for every second of later retention.

## Verification and evidence

**390 offline tests pass**, including model routing/prices, timing wiring, real Qt dismissal, uncertainty labels, batched reset handling, private local-only memory removal, source invalidation, retention without renewal, lower-confidence updates, same-memory slot deduplication, source-age freshness, optional-action guard negatives and wrapped-row geometry. `git diff --check` passes. Actual Qt screenshots of both final replays were inspected. Opus **5.5** reviewed the changes with tools disabled across four reviews; concrete findings were corrected and regression-tested. Its final findings also led to matching direct-memory display against the analyzed snapshot rather than a newer retrieval result, and treating freshly re-endorsed sensor-only cues as fresh support rather than omission. No independent human acceptance is claimed.

Private evidence remains under `build/guidance-recovery-20260924/`: original shared ledger; initial `rollout_search`/`rollout_transfer`; `retrieval_delta_search`/`retrieval_delta_transfer`; final `current_retrieval_search`/`current_retrieval_transfer` with exact reuse maps, source hashes, raw-label timelines, screenshots and item assessments; `rollout-audit.json`. Review artifacts: `build/richer-review-20260924*`. Call logs, screenshots containing private facts and credentials were not added to tracked documentation. Existing unrelated worktree edits were preserved.
