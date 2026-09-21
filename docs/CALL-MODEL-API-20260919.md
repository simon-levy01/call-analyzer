# Luna low / Terra low: prepared comparison, blocked by API credits

September 19: the user selected real Luna-low and Terra-low API testing, deferring stronger-model agents. Luna has the standing $0.30 cap for this requested evaluation; the user explicitly authorized $0.50 for Terra. These are aggregate per-model caps, separate from preserved earlier evaluations. Production remains Luna low.

The comparison is **not complete: zero model answers were returned**. The provider returned HTTP 429, `insufficient_quota`, code `credit_balance_exhausted`: the API account has no credits remaining. This is distinct from Codex subscription usage and from the authorized test caps. No fallback model, agent testing, production change or new quality conclusion is implied.

## Frozen design and checks

23 cases from three existing calls: 16 guidance checkpoints, four extraction chunks and three whole summaries. Each case has two independent requests per model, with alternating model order: 92 planned responses. Both models receive identical corrected-app input, instructions, strict schema and output limits, at low reasoning, without previous-response history or tools. Cases and source at correction-branch commit `a927b91` are frozen for later agent comparisons too.

All 23 requests regenerate exactly from the current application and retained snapshots/transcripts. The two guidance/interpretation suites pass 35 tests. Prior logs and source hashes remain unchanged. Known-case root judgments and earlier agent assessments are qualitative context, not blinded ground truth or new independent model arms. This exposed regression comparison does not replace the original F07 held-out, human or 144-response acceptance gates. No tuning occurred.

Pricing was checked against official [Luna documentation](https://developers.openai.com/api/docs/models/gpt-5.6-luna) and [model comparison](https://developers.openai.com/api/docs/models/compare): per million input/cached/output tokens, Luna $0.20/$0.02/$1.20 and Terra $2.00/$0.20/$12.00. The runner conservatively reserves full input ceilings and maximum outputs before each four-response case block. Its worst-case full schedule exceeds Terra's cap; completion would depend on actual usage releasing unused reservations. Any unfinished cases must be reported, not silently reduced after reviewing answers.

## Failed attempt and accounting

Twenty scheduled attempts (ten per model, five post-call cases) all returned SDK `RateLimitError`. The runner continued across failed cases instead of stopping at the first service failure, and unnecessarily retained outer reservations when the production request ledger had classified the errors as unbilled. It stopped at its reservation ceiling. This harness limitation is recorded, not presented as productive testing.

One subsequent bounded Luna diagnostic captured the precise HTTP status and provider error above. It also returned no model output. No automatic retry or paid-model substitution ran. There are 21 attempted requests and zero successful responses, not 21 comparison samples.

Original ledgers retain $0.04776 Luna and $0.47760 Terra as reservations, **not measured charges**. An append-only reconciliation releases those known `RateLimitError` reservations using the existing production helper's definitely-unbilled classification. The original files were not reset or overwritten. Returned usage is $0; effective committed amount is $0 per model under that classification, leaving the original $0.30/$0.50 caps available. This is not a provider invoice audit. The diagnostic's confirmed HTTP 429 is also classified unbilled.

## Continuation and evidence

API credits must become available before inference can proceed. No background retries are scheduled. On an explicit continuation, preserve all attempts and the reconciliation, keep the same aggregate caps, verify frozen source/inputs, and use a new continuation record that stops immediately on service errors and respects the production ledger's explicit unbilled disposition. Failed attempts do not satisfy either independent repeat. Do not rerun the locked original runner or overwrite its manifest.

Private, Git-ignored evidence: `build/call-model-api-20260919/` contains exact cases, criteria, source copy/hashes, single-use runner, offline checks/test XML, original results, individual rejection records, precise diagnostic, accounting reconciliation and blocked status. No raw call audio/video was retained or uploaded. Credential scan found no actual key in the new artifacts. No approved memories or summaries were changed.

No new Claude review was run for this blocked diagnostic; the earlier reviewed production checkpoint remains unchanged. There is no new human-testing or release clearance, commit/push, F07 completion, or model ranking.
