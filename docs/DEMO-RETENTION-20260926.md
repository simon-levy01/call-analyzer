# Thirty-turn replay: memory diagnosis and display follow-up

## Recorded demo (before display changes)

First30 turns of the88-turn September13 log, original arrival timing plus20 seconds to settle. Real Luna5.6low, new$0.30 cap:10/10 completed responses, $0.01007066, no pending reservations or retries. Native Computer Use started the demo, observed guidance and opened/closed a response popup. Private inputs, raw results, rendered label transitions, ledger, transcript and readable item list are in `build/visible-30-20260926/`. No microphone/video or post-call inference. Frozen source preserves the exact runner used.

Distinct rendered strings after removing Earlier prefixes, not independent useful observations:

| Saved run, cropped to through-turn30 and145.543s | Tones | Cues | Replies | Follow-ups | Memories |
|---|---:|---:|---:|---:|---:|
| Older visible baseline |7|2|10|1|0|
| Previously tested balanced candidate |7|6|10|4|0|
| New visible demo |7|7|9|3|0|

Earlier rows are cropped saved timelines, not new paired inference; request timing differs. Same tone count, more cue strings, not proof of improved usefulness. Paraphrases inflate counts; some stale responses persisted. Rendered labels can extend below the viewport.

## Why the job memory was absent

1. The isolated demo's main store used a subclass pointing to the installed embedding cache. Desktop retrieval creates another `MemoryStore` in its worker; that binding still used the isolated database's empty cache path. All recorded retrieval results have semantic_available=false. The product cache marker exists; a fresh UI-first local384-dimensional embedding probe passes. Therefore this run does not demonstrate a missing installed model or a current ONNX failure in the normal application. The demo harness override now also covers the worker class; the original frozen runner remains unchanged. No paid rerun.
2. After the explicit job mention, snapshots14–16 and19–20 retrieved the correct approved job-loss memory lexically. It was included in actual API payloads for latest turns15 and20. Luna omitted it for15. For20 it returned the correct low-confidence possible connection, but the conversation switched to regulation during the approximately9-second request. The coordinator rejected snapshot20 as stale. It was not lost by the UI renderer. Do not disable topic/source safeguards to force an outdated reminder onto the screen.
3. Not a cap failure: all10 responses have completed status, zero API errors, and total cost is approximately one cent. The1800-token transport ceiling did not truncate a response. No caps raised.

The saved-output assertion reproduces no displayed memories; tracing its request and coordinator boundaries explains why. An end-to-end paid rerun with the corrected cache has not been performed or claimed.

Offline reproduction on a private disposable copy: the original worker path has no indirect matches. With the corrected worker cache and normal local embedding backfill (one memory indexed), the exact first-five-turn lexical/semantic/contact queries retrieve the job-loss memory semantically before any job keyword. `build/check_demo_worker_cache_20260926.py` verifies this using real local embeddings, without cloud inference or modifying live data. The first probe correctly showed that cache availability alone is insufficient when the isolated database has no embedding index; normal backfill is also required.

## Requested display changes

- Follow-ups and replies share one Potential responses section with four combined slots, newest support first. Equal-age items alternate between the two source categories; duplicate dismissal applies to both. Overflow is removed rather than reappearing after a dismissal. Pop-outs retain source evidence and use the same section title.
- All guidance categories retain supported items for90seconds instead of48. Empty updates do not clear them or extend their age. Explicit topic changes, corrections, supersession, source invalidation and dismissals still remove obsolete guidance early. New API results still have the existing short delivery freshness checks.
- No model, prompt, pricing, generation, live data or API cap changes. Restart required to load UI changes. The prior demo process retains its old loaded code.

Opus5.5high read-only review identified cross-category dismissal, equal-time selection and hidden-overflow issues; all addressed with regression checks. No private logs or credentials were sent to the review.

Final offline suite:422 passed. Includes actual Qt merged-section rendering, follow-up pop-out/dismiss routing,75-second survival/90-second expiry, cross-category duplicate dismissal, tie ordering and no resurfacing of overflow. No additional paid API requests. The new demo ledger remains$0.01007066/$0.30; earlier ledgers unchanged.
