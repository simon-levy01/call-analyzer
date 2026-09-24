# GPT-6 model update — September 22, 2026

On `codex/qt-ui-migration`; no main merge.

| Workload | Previous | Current |
|---|---|---|
| Default Live / Ask | GPT-5.6 Luna low | GPT-6 Luna low |
| Higher-end Live / Ask | GPT-5.6 Terra low | GPT-6 Sol low |
| Memory extraction, import, summary / consolidation | GPT-5.6 Terra low | Higher-end entry in the shared ordered model list, currently GPT-6 Sol low |

The UI model labels and Review generation labels use the same registry. Generation remains independent of the user's Live/Ask selection. Medium reasoning is only requested for the comparison, not added to the UI. No prompt, schema, endpoint, token limit, retry, source-validation or approval behavior is changed.

Official model pages verify `gpt-6-luna` and `gpt-6-sol`, Responses structured output, low/medium reasoning, and standard short-context token prices. Per million tokens: Luna input $0.10 / cached $0.01 / output $0.50; Sol $2 / $0.20 / $10. Cache-write pricing remains 1.25 times input. Old GPT-5.6 rates remain available for historical accounting; saved outputs, ledgers and evaluation profiles are not relabeled. Sources: [Luna](https://developers.openai.com/api/docs/models/gpt-6-luna), [Sol](https://developers.openai.com/api/docs/models/gpt-6-sol).

Compatibility: existing calls use stateless Responses structured outputs with explicit low reasoning, no function tools or sampling parameters. No endpoint or prompt migration is needed from the documented contracts; account access and actual new-model responses still require the requested live test. OpenAI Docs guided this scoped migration. Its general Astra migration page could not be fetched; the exact Luna/Sol model pages provided the relevant contracts and prices.

Verification covers picker routing, Ask/Live model forwarding, generation provenance, new pricing and preserved historical pricing. Final combined offline suite: **356 passed in 33.87 seconds** (`python -m pytest -q`). This is not a new-model inference result or response-time measurement. `git diff --check` passes.

Tool-disabled Claude Opus 5 review completed (private `build/gpt6-migration-review.json`). Grep/full-suite checks ruled out speculative missing imports and string-assertion failures. Historical labels remain raw model IDs, so no legacy lookup is needed. Frozen F04 IDs are explicitly retained, but that old paid harness is not claimed runnable against the current product-only allowlist; use its archived source for old-model reproductions. No old evaluation was run. Interrupted extraction after a model change starts a new correctly attributed batch; the old partial batch remains retained and invalidated, not relabeled. Existing summary checkpoints/versions retain their original model provenance; newly generated consolidation records the new generating model without pretending its old inputs came from that model.

## Requested quick timing comparison

Use one saved real-call guidance checkpoint from `build/call-model-api-20260919/cases.json`, replayed identically across GPT-6 Luna low, Luna medium and Sol low. Preserve exact instructions/input/schema/output limit and raw responses privately. Report complete-response wall time, token usage, cost and validation status; one response per arm is only a quick sample, not a stable latency benchmark. No product prompt tuning or memory-store writes are part of this test.

**Completed:** user selected the real API and added the entire shortest-call Luna comparison. [35-request results](GPT6-API-COMPARISON-20260922.md): $0.02759957/$0.30 combined cap, all new responses complete; historical Luna answers reused without inference. Faster observed live responses and several precision improvements, but mixed memory/summary quality and fewer replies. No prompts or product defaults changed during evaluation; historical ledgers remain intact.
