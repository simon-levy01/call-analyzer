# Luna low versus Sol low — September 23, 2026

**Sol improved speaker handling and summary fidelity in this sample, but was not uniformly better.** Twelve fresh real API requests covered six saved cases, one independent answer per model per case. All returned complete, locally validated answers. No prompt changes, retries, repairs, fallback, real-memory writes or product-default changes.

## Timing and cost

| Measure | GPT-6 Luna low | GPT-6 Sol low |
|---|---:|---:|
| Complete answers | 6/6 | 6/6 |
| Median complete-response time | 6.10s | 4.49s |
| Mean complete-response time | 5.88s | 4.41s |
| Median live-analysis time, four cases | 5.53s | 4.42s |
| Total estimated cost | $0.002628685 | $0.067117100 |
| Input tokens | 23,345 | 23,345 |
| Cached-read tokens | 14,726 | 3,568 |
| Cache-write tokens | 8,601 | 19,759 |
| Output tokens, including reasoning | 2,809 | 1,697 |
| Reasoning tokens | 1,658 | 369 |

Sol's median was **26.3% shorter**, while its observed cost was **25.5 times higher**. These are six serial samples per model, not a stable latency ranking. Requests alternated which model went first. Luna had more cache hits, so 25.5x is the observed bill estimate for these requests, not a universal per-request multiplier. Sol produced fewer tokens, particularly fewer reasoning tokens; that can contribute to shorter response time without establishing causation.

Rates checked through official OpenAI documentation: [Luna](https://developers.openai.com/api/docs/models/gpt-6-luna) input/cached/cache-write/output $0.10/$0.01/$0.125/$0.50 per million; [Sol](https://developers.openai.com/api/docs/models/gpt-6-sol) $2/$0.20/$2.50/$10. Sol's corresponding token rates are 20x Luna's. Reasoning tokens are already part of output billing. Costs are derived from returned usage, not reconciled invoices.

| Saved case | Luna seconds / cost | Sol seconds / cost |
|---|---:|---:|
| 05 — ambiguous memory relevance | 6.71 / $0.000238250 | 4.55 / $0.011303500 |
| 07 — app commentary versus life event | 7.07 / $0.000540510 | 4.59 / $0.007310200 |
| 17 — speaker attribution | 4.35 / $0.000198350 | 4.28 / $0.010918500 |
| 26 — optimism/tone | 4.13 / $0.000386395 | 3.46 / $0.006777900 |
| Full-call extraction | 7.55 / $0.000419380 | 5.15 / $0.015011000 |
| Full-call summary | 5.48 / $0.000845800 | 4.44 / $0.015796000 |

This comparison cost **$0.069745785 (about 7 US cents)**. Carrying prior $0.03756745 forward gives **$0.107313235 of the same $0.30 aggregate cap**, leaving $0.192686765. The runner conservatively reserved both arms before each pair, then settled reported usage. All six pairs fit without expanding the cap. No unresolved reservations remain.

## Quality review

Assistant, non-blinded review against exact saved inputs; exposed known cases, not a human gold-label accuracy score. Schema validity and valid citation IDs are separate from meaning.

- **Memory relevance, case 05 — mixed.** Sol retained the supplied job-loss memory that Luna omitted, but inferred weak calm from an ambiguous brief reply and asked whether the contact had found a job. That is a clarification, not an outright new-job assertion, but introduces a poorly supported possibility in an app-testing context. Luna's clarification was more neutral and it abstained on affect. Neither is an unqualified win.
- **App text versus real events, case 07 — broadly comparable.** Both retained a tentative saved memory and did not congratulate anyone or claim a new job. Both abstained on tone/replies. Luna linked the reminder to the user's ambiguous app-memory wording; Sol used earlier job-related turns. Valid IDs do not prove which linkage is most useful.
- **Speaker attribution, case 17 — Sol better.** Luna suggested “No problem” in response to the user's own “Thank you.” Sol acknowledged uncertain speaker attribution and offered a clarification about the contact's regulation-correction remark instead. It avoided the wrong-direction reply without inventing the user's remembered knowledge.
- **Optimism/tone, case 26 — still weak in both.** Both labeled explicit improvement/optimism as neutral calm rather than retaining the clearer positive interpretation. Sol also offered a plausible acknowledgment; Luna offered no reply. Sol's acknowledgment partly repeats what the user just said and its cited turns do not establish the entire “uneven guidance” clause, although that context exists elsewhere in the supplied transcript. Luna names vocal evidence without a specific vocal explanation. More output is not automatically more accurate.
- **Memory extraction — mixed, five proposals each.** Both retained sensitive financial difficulty, the regulation correction and both explicit user commitments. Neither invented gender or a new job in this run. Luna preserved the “a few days” wording and the conditional AI-to-CRA correction rule; Sol omitted these details. Sol preserved the user's disappointment and more app-testing context; Luna omitted that opinion and over-expanded the incomplete “The biggest...” fragment into a definite description. Sol is cleaner on that fragment, but loses useful specificity. Some proposals in both combine multiple facts; no blanket memory-quality winner.
- **Summary — Sol better.** Luna incorrectly transferred the user's disappointment to the contact. Sol avoided that attribution error, retained more of the conditional correction and explicitly described memory/guidance troubleshooting. Both retained the financial disclosure as sensitive and the two user plans, and neither claimed a new job. Both omitted face-tracking troubleshooting; the bounded summary instructions permit compressing minor technical details, so omission alone is not a failure. Sol states the positive correction condition but not the explicit “EU Act alone needs no change” exception. Neither summary is exhaustive.

**Practical reading:** this provides some evidence for Sol when summary fidelity and speaker handling matter, while Luna remains substantially cheaper and sometimes preserves more detail. It does not justify claiming Sol fixes the known tone/attribution problems generally. Keep current defaults: Luna low for Live/Ask, Sol low for memory/summary; nothing was switched by this evaluation.

## Reproducibility and limits

Inputs come from the same shortest saved call (88 turns). Four frozen live checkpoints plus extraction/summary over the full transcript; not six independent calls. Exact historical September 15 instructions, input, schema, verbosity and output caps were kept from the September 22 freeze: live 1,200, extraction 2,400, summary 1,600 tokens. Only model ID changes; both use low effort, default service tier, no storage and zero automatic retries. Previous answers were not fed to either model or counted as fresh samples. Existing paid baselines remain preserved for context; fresh Luna requests provide same-session timing pairs.

Historical null-speaker rows, retrieved memory candidates and numerical vocal/visual observations are unchanged. No new retrieval, audio/vision run, current 1,800-token live-cap test, Ask Memory test, paced delivery or GUI integration. One answer per model/case cannot establish repeatability or an accuracy percentage. Earlier effort comparison already demonstrated variability on these exposed inputs. No extra sampling or prompt tuning was done after inspecting results.

Private evidence is Git-ignored in `build/gpt6-luna-sol-20260923/`: frozen manifest/rubric/cases, all 12 requests/raw outputs, timestamped cumulative reservations/results, metrics, runner and source-ID inspection script. `runner.py audit` passed immutable-source hashes, paired request coverage, exact input/model/schema, raw/parsed consistency, Pydantic validation, independently recalculated raw usage and cumulative accounting. `inspect_results.py` passed supplied-ID membership checks; it does not claim semantic citation correctness. Prior results and ledgers are unchanged by hash. Product code is unchanged in this follow-up; no full application acceptance or commit/push claimed.
