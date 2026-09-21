# Complete shortest-call comparison — September 21

Completed **99 fresh isolated answers** for the shortest call: 88 transcript turns, 31 live checkpoints, one extraction and one summary per model. The user deferred the other two calls before any fresh requests for them started. Their 234 queued requests and 12 earlier saved answers remain preserved, not completed evaluations.

The fixes help, but stronger models do not consistently solve the remaining problems. Sol provides more usable reply ideas and the best concise summary in this call; it also produces unsupported or stale live suggestions. Terra is more selective but still invents some personal statements. Luna is sparse and retains interpretation errors. This is preliminary agent evidence, not overall accuracy or API acceptance.

| Measure | Luna low | Terra low | Sol low |
|---|---:|---:|---:|
| Fresh answers | 33 | 33 | 33 |
| Local schema/application passes | 31/33 | 33/33 | 33/33 |
| Live checkpoints with initially accepted replies | 12/31 | 18/31 | 25/31 |
| Correct supplied-memory reminders initially retained | 0/2 | 1/2 | 0/2 |
| Memory proposals | 7 | 5 | 10 |
| Summary statements | 7 | 5 | 5 |
| Complete post-call processing in scratch database | Pass | Pass | Pass |

Reply counts measure availability, **not correctness**. Luna's two schema failures were preserved without repair: four cue citations where three were allowed, and `uncertainty` incorrectly placed in the tone enum. Agent output lacks provider-enforced decoding, so these do not prove equivalent API failures.

## Live findings

**Grounding filters help.** Unsupported calm labels are removed. Several Luna answers assign the user's commentary to contact affect; the app rejects those cues. Current Luna/Terra abstain in landing-page cases where the original live response misassigned the user's disappointment. Bad replies can still survive after their accompanying cues are removed.

**Correct memories can disappear because of the application contract.** At checkpoint 05, Luna/Sol select the supplied memory but cite three transcript turns plus its memory ID. The app permits only three sources combined, while the schema separately allows three entries in each list. Sol/Terra encounter the same rejection at 07. Aligning these rules is a concrete application improvement. This is supplied-evidence/filtering failure, not retrieval omission. Luna's other reminder misreads memory surfacing as getting a new job; it passes initial filtering but disappears under historical-arrival replay.

**Personal-state and context checks remain incomplete.** Terra's invented expectation about a webpage survives; other invented commitments are correctly filtered. Sol proposes changing generic regulation wording despite supplied turn 32 saying it needs no change (checkpoint 20), and continues that topic after the user moves to app testing. Luna retains noisy-phrase misunderstandings and repetitive or sparse guidance. More suggestions are not automatically better.

**Transcription uncertainty varies.** Sol treats an ambiguous acronym phrase as a possible transcription error; Luna/Terra interpret wordplay. Without raw audio, that interpretation cannot be declared definitively false. All models appropriately abstain on an unfinished user sentence. Legitimate listening advice is distinguished from pathological waiting-only guidance.

**Visual contribution remains unproven.** All 31 requests contain visual rows; 28 pass the app's visual-evidence availability check. None of 93 generated live answers cites visual evidence. Sol has two vocal cue citations without naming a specific vocal observation. This measures supplied data and explicit citations, not causal use/non-use; no modality ablation was run.

## Memories and summaries

All three complete post-call paths pass using actual application functions and identical frozen requests in disposable in-memory databases. No generated result is approved or written into the real database.

- **Luna:** seven mostly grounded proposals and a broad seven-statement summary. Avoids historical job-acquisition confusion, but compresses the memory-surfacing problem and omits the precise regulation correction rule.
- **Terra:** five proposals and five summary statements. Omits tracking troubleshooting and landing-page disappointment from the summary. One memory introduces an unsupported gendered pronoun. Retains testing/model-selection plans.
- **Sol:** ten proposals and five summary statements. Best coverage here of the precise correction rule, app problems, tracking recovery and plans. Retains more transient material, including uncertain historical cost discussion; more memories are a selectivity tradeoff.

The original oldest log contains five extraction requests and repeated/intermediate summary processing, including failed reviews; it does not establish a successfully approved final summary. Its generated summaries repeatedly confuse memory surfacing with acquiring a job. All three new whole-call summaries avoid that confusion. This is consistent with the fixes, but different prompts/methods prevent isolating their causal effect.

## Comparison limits and evidence

The original shortest call used **Terra low for guidance and Luna reasoning none for post-call processing**. Later paid Luna replays are separate baselines, not original live responses. The [focused agent comparison](CALL-AGENT-COMPARISON-20260921.md) and [old/revised Luna API comparison](CALL-PROMPT-API-20260917.md) remain separate evidence.

Every fresh request used the actual requested model, low reasoning and no history fork. Agents saw only the frozen instructions, input, schema and stated output allowance, with other answers, expectations and later speech hidden. All 99 shortest-call outputs are fresh; 12 archived other-call reuses are excluded. This is one full pass, not two independent repeats.

The recorded conversation stays fixed, including commentary on the old app. Actual corrected-app filters run offline. A separate guidance-display replay uses original accepted delivery times, logged speech arrival, expiry, topic resets and display holds. It does not measure new latency, rerun audio/vision/retrieval, simulate adaptive scheduling, user dismissals, sensitive local-memory display or tone UI. Agent testing does not establish API billing, enforced token limits or deployed parity.

Root reviewed all 31 live cases across all three models and all six post-call answers. Judgments are non-blinded exposed development evidence, without human gold labels. Schema pass rates are not semantic accuracy.

Private evidence: `build/full-call-agent-replay-20260921/`, including frozen hashes, scope amendment, append-only dispatch provenance, raw outputs, original baselines, root notes, offline scripts/results, complete local comparison browser and final integrity audit. Source/input/log/prior-output hashes pass; no dispatch failures, retries, substitutions or paid API requests. All three full post-call checks pass; 97/99 local output checks pass with failures preserved.

Production remains Luna low, unchanged at `a927b91` on `codex/call-analysis-fixes-20260916`. No merge, push, new tuning or F07 completion. Original 144-response/two-repeat design, 85% gates, 400-token allowance and separate 10% cost limit, three participant checks, Opus 5 review gates and deadlines remain unchanged. The other two full-call replays are deferred by the user.