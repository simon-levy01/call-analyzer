# Call-analysis correction branch

Status: implementation and offline regression checks complete; actual tool-disabled Claude Opus 5 cleared the corrected source for preliminary offline use. Fresh semantic comparison, user rechecks and final release review remain pending. No F07 release pass or human-test clearance is claimed here.

The user requested analysis of prior calls, a switchable baseline/fix branch, application of non-echo fixes, and comparison against saved Luna, Astra low, Sol high and root assessments. Echo/audio pickup is explicitly excluded. Each input/output cap may grow by at most 200 tokens where needed; this does not increase an API spending authorization or waive the separate 10% cost gate.

## Branches and preserved evidence

- `codex/pre-call-fixes-20260916`, commit `75d5b27`, preserves the exact pre-fix app and previously uncommitted project work as a local checkpoint. It is not a reviewed release. Original main was `28e843f`.
- `codex/call-analysis-fixes-20260916` contains the isolated corrections. Do not merge to main as part of a comparison.
- Private evidence and reproducible offline runner: `build/call-fixes-20260916/`. Existing call logs, agent answers, budget ledgers and approved database records remain unchanged. Personal PDFs are excluded from both commits and analysis.
- Earlier-call analysis was saved before creating the branches: `previous-log-analysis.md`. Original evidence SHA-256 references are in `baseline-references.json`; all references were rechecked.

## Corrections

Every compact transcript row now states its speaker explicitly. Tone/cue evidence carries exact turn IDs and must include a current substantive contact contribution. Unavailable, old, wrong-speaker and memory-only evidence cannot establish a current cue. An old sarcastic remark no longer overrides a later topic; factual fragments and absence of tension cannot establish calm.

Reply filtering distinguishes optional immediate show/clarify actions from unsupported personal states and commitments. Cited user wording can support a personal claim; contact wording cannot. Call-duration answers cannot be inferred from a rolling context window. In-flight and displayed suggestions share a bounded lexical supersession check; unrelated continuation and the existing 24-second expiry remain. This is not a semantic guarantee for paraphrases or ambiguous referents.

Whole-call summaries deduplicate speaker/date metadata while preserving all eligible text, explicit roles, source IDs and name/date changes. The three regression calls now fit the existing 9,000-token whole-summary limit. Longer-call consolidation receives original cited text plus adjacent eligible turns, prior confidence and sensitivity. Confidence cannot increase through merging. Existing permission, generation, deletion and resumable-checkpoint checks remain. Oversized merges first drop optional adjacent context; if cited source still cannot fit, they retain bounded original draft sentences verbatim with partial=True. They never send a source-free paraphrasing request or retry the same impossible merge.

New extraction checkpoints persist exact source-turn boundaries so future cap/prompt changes cannot silently skip completed work. Previous v1 framing is held at its pre-correction token allowance. Recording-date runs retain full ISO timestamps/offsets and relative wording is not replaced by invented local dates.

Extraction instructions distinguish same-occasion advice, open offers and run-specific measurements from standing preferences or firm commitments. These semantic changes still require fresh model evaluation. Approved memories are not rewritten. The existing face-lost status now explicitly says tracking is paused and identifies Continue tracking; selected-face behavior is unchanged.

## Offline comparison

The baseline passed 294 tests. After initial corrections the suite passed 317 tests. Actual tool-disabled Opus 5 reported five blockers plus additional findings; corrections added negative/quoted-source, related-continuation, nonverbal-freshness, oversized-merge and extraction-resume regressions. The final corrected full suite passes **333 tests** (`final-corrected-tests.xml`). The final offline replay preserves every original transcript ID and both sensor streams across149requests with zero errors. Refreshed Opus 5 review returned CLEAR (preliminary, offline only); exact production-source hashes match the final replay.

The offline runner captured all 149 requests across 88-, 150- and 240-turn calls. It replayed 146 saved Luna answers; three historical failed requests remain missing, not synthesized or retried. All requests fit their bounds without errors and retain both sensor streams. This verifies request construction and postprocessing, not fresh model responses or causal use of facial data.

| Whole summary input estimate | Baseline | Corrected |
|---|---:|---:|
| Earlier 88-turn call | 5,658 | 4,027 |
| Earlier 150-turn call | 8,657 | 5,683 |
| Latest 240-turn call | 12,881, requiring chunks | 8,054, one whole-source request |

For the latest saved Luna outputs, replay removes the unsupported personal-state, uncertain possession and invented-duration examples identified by both agents/root. Four immediate show-action suggestions previously rejected are restored. Timing replay also retires matching suggestions when intervening contact speech addresses their subject. These are exposed regression examples, not held-out accuracy scores. Old outputs lack the new cue citation fields: rejecting those cues is schema enforcement, not evidence that a newly prompted model is more accurate.

Five saved isolated Sol-high live answers from the earlier call were replayed against matching source IDs/text. Their candidate counts are retained. Their old uncited cues cannot establish post-fix cue quality. The sixth saved Sol answer is post-call, not a guidance request. Saved Astra-low/Sol-high diagnostic assessments and root's independent analysis are compared by finding in the private report; reuse is not independent inference or API parity.

## Token and spending limits

| Input allowance | Before | After | Reason |
|---|---:|---:|---|
| Combined guidance | 4,500 | 4,700 | Explicit attribution and source-citation schema |
| Interpretation hard ceiling | 1,650 | 1,850 | Same grounding fields; target 1,500 → 1,700 |
| Memory-backed interpretation | 2,200 | 2,400 | Same grounding overhead; memory allowance remains 700 |
| Extraction reservation | 9,000 | 9,200 | Existing call measures 9,043 with scope instructions; avoids extra chunk |

Summary input limits and all output limits are unchanged. The guidance maximum reservation rises about 1.95%; this is not a measured end-to-end provider cost comparison or a pass of the F07 cost gate. No new paid model tests have run for this correction task. Fresh inference awaits the requested method selection; a selected Luna-low API evaluation uses one cumulative $0.30 cap, not a cap per call or retry.

The original F07 independent-repeat design, three consenting checks, tuning limit, September 23 freeze/September 27 fallback and F08 October 1 installation target remain. These exposed call regressions do not replace those acceptance gates.

## Review follow-up

The second Opus review found a source-change retry issue and an ASR punctuation assumption; both are corrected and tested. Obsolete extraction checkpoints are preserved as invalidated when a fresh batch begins. Review estimates remain available after source changes. Supersession accepts unpunctuated answers but rejects questions and trailing fragments. The summary fallback also enforces the existing500-word maximum. Owned sensitive drafts remain usable only inside the same authorized review job; future cloud permission is not granted. Sensitive labelling across a merge is deliberately conservative.

`offline-comparison.json` preserves the final saved-answer differences and source hashes. All historical reference hashes still match. Local main, origin/main and GitHub main were read-only verified at `28e843f3e2efbfa5f494f8c40c759705e720bfe1`; no merge or push has occurred.

## Final offline review and known limits

Actual Claude Opus5, medium effort, one turn, tools disabled and strict empty MCP, returned CLEAR (preliminary, offline only). Evidence: private `opus-offline-final/` and `review-verification.json`. No reviewer substitution occurred. Previous blocker reviews and all corrections remain preserved. This is not the final review after fresh semantic tests and necessary human rechecks.

- New language cues require populated source IDs; saved pre-fix outputs cannot test whether Luna will supply them correctly. Measure citation population, anchor coverage, useful guidance and false abstention in fresh inference.
- Fresh numeric visual payloads meeting the new24-second/.5availability/.5reliability gates occur in23/31,42/47 and33/71snapshots respectively. This measures available evidence, not facial accuracy or causal model use. All149requests preserve their original transcript IDs and both sensor streams.
- Personal-claim support is intentionally exact-clause based and can suppress useful paraphrases; the lexical rules also have uncovered agreement/negation phrasings. Track rejection reasons and reply usefulness in fresh tests. Supersession and duration detection are bounded lexical safeguards, not general semantic validators.
- A sensitive long-call draft conservatively makes all merged statements sensitive. After approval, their cited turns become unavailable to later cloud review until the user explicitly grants permission. This may restrict the entire record; it prevents unintended reuse. The latest call uses a single whole-source summary and does not take this merge path.
- Frozen extraction boundaries survive cap/prompt changes, but a future prompt large enough to make an individual frozen chunk exceed the current extractor cap can require a new analysis. No such oversized chunk appears in the current three-call corpus. Previous v1 framing is tied to the preserved pre-correction1288-token prompt.
- Summary compaction preserves text, source order and date-run timestamps/offsets, but omits per-turn within-day recording times. Spoken event times remain verbatim. Oversized summaries can lose middle-topic coverage in the explicitly partial fallback; original source and checkpoint drafts remain local.

Fresh model tests remain pending the requested API/agents selection. Existing agent answers are reused with provenance, never counted as independent repeats. Original F07/F08 gates and deadlines remain unchanged.
