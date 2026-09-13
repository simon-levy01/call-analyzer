# Saved-call post-call generation — 2026-09-13

Replayed all 88 attributed turns from `build/live-test-20260913-121412/events.jsonl` into an isolated stopped Conversation Record. Only memory extraction and summary generation ran; no live analysis, guidance, audio, or video requests. All outputs remain unapproved test drafts.

## Changes

- Extraction now covers specific shared feedback, named corrections and commitments by either speaker, with explicit attribution and source turns. It uses a 9,000-token reservation ceiling (previously 6,000), max 200 turns, and up to three overlapping turns for longer inputs. The proposal ceiling is now12 (previously8), with unchanged2,400 output tokens. Existing interrupted jobs retain their legacy chunk layout.
- Post-call extraction and summary use Luna low. Live analysis settings are unchanged.
- A complete eligible transcript is summarized directly when its input fits 9,000 tokens. Longer or already-checkpointed reviews retain bounded chunk/consolidation processing. Existing privacy, approval and budget checks remain.
- Ask Memory evidence allowance increased from 4,400 to 4,700 tokens, and total input allowance from 6,000 to 6,300. The small fictional history already fit; this increase benefits larger histories.

## Actual comparison

| Variant | Requests | Cost | Observed quality |
|---|---:|---:|---|
| Broader exceptions appended to old extraction prompt; chunked summary, none | 10 | $0.00769635 | Missed user feedback/commitment; summary lost the regulation resolution |
| Standalone broader extraction prompt; chunked summary, none | 10 | $0.00789650 | Captured user feedback, but guessed pronouns and invented a job outcome |
| Standalone prompt; chunked summary, low | 10 | $0.00971850 | Better memory coverage; consolidation still invented a job outcome |
| Final: standalone prompt; whole-transcript summary, low | 2 | $0.00265096 | Covered all four manually identified fact groups; no invented job outcome or guessed gender |

Total application API cost including the final 12-proposal-cap replay: **$0.03041486** (about 3.0 cents). Aggregate controlled evaluation ledger: **$3.45659864 / $4**. Costs are usage-based estimates, not a billing invoice. The first run’s raw request log was overwritten during iteration; its isolated database record remains. The other runs retain request/output logs.

This is one real conversation and one final candidate run, not a statistical quality benchmark. The first whole-transcript candidate produced eight proposals: all four desired fact groups are represented, but some are redundant or too generic. The twelve-proposal output limit can still omit details in dense calls (raised from eight after code review). Model citations are structurally checked, not a guarantee that every claim is fully supported.

## First whole-transcript candidate summary

Yaheli said things had been rough financially, and You expressed hope that Yaheli would find something soon.
The conversation included testing an app’s guidance, memory retrieval, face tracking, and emotional analysis; the guidance was inconsistent, while the face tracking briefly stopped and then resumed.
They corrected the project terminology from the EU AI Act to the EU Cyber Resilience Act, or EU CRA Act, and noted that the landing page prominently displayed the CRA wording.
You planned to test the system with specific memory content and make the model selectable so the cost and performance trade-off between the cheaper and more expensive options could be managed.
The system’s inconsistent guidance quality and the practical cost difference between the available models remained concerns, although both speakers expected performance to improve as models improve.

## First whole-transcript candidate proposals

1. Yaheli said things have been rough financially (“hard money-wise”).
2. In the shared project, Yaheli corrected that the relevant regulation is the EU Cyber Resilience Act (EU CRA Act), not the EU AI Act.
3. Yaheli recalled that Eden had corrected you both about the EU Act.
4. Yaheli’s feedback was that the EU CRA Act is the first and most prominent thing visible on the project’s landing page.
5. You found the landing page’s prominent EU CRA Act presentation disappointing.
6. You planned to test the system with a specific memory and continue working on improving its guidance.
7. You noted that the project’s results vary, with guidance sometimes better and sometimes worse; you expect improvement as models get better.
8. You said Luna is very cheap while Terra is not, and planned to make the system switchable between them.

## Manual assessment

- Recovered the useful missing material: Eden’s correction, your landing-page feedback, and your plan to switch models. Financial difficulty remains correctly attributed without inventing an employer or a newly obtained job.
- The regulation and Eden items could be combined. Generic testing intentions and predictions about model improvements are weaker memories and should be rejected in review if not useful.
- The landing-page memory’s citations do not include every contextual turn needed to resolve the acronym. The transcript supports the context, but citation completeness still needs improvement.
- Keep the transcript as the factual source. Live model analysis is another interpretation and can introduce guesses. In this experiment, preserving the whole transcript fixed a false outcome that survived both chunked-summary profiles; adding generated analysis was unnecessary.

## Verification

268 automated tests passed. This includes legacy extraction retries, overlap recovery without silently dropping facts (possible duplicates use existing review flags), whole-transcript summary input, checkpoint ranges, and the existing privacy/budget/approval integration checks. Claude Opus5 full-diff review and correction review completed. Correction review found no remaining code-level regression; its remaining stale-cap documentation note is corrected here. Final documentation-only verification could not run because Claude returned429/session limit (reset7pm Asia/Jerusalem). The final clean preliminary gate is therefore still pending, as are user retest and post-user release review.

Raw final requests, responses, usage and draft output: `build/memory-scope-20260913/whole/results.json`. Isolated database: `build/memory-scope-20260913/whole/memory.sqlite3`.

## Final code replay: 12-proposal ceiling

Two requests, **$0.00245255**. It returned six pending memories rather than filling the new ceiling. All four target fact groups are represented, but this is not a clean factual-quality pass: the summary incorrectly calls memory retrieval unresolved despite turns19–20 suggesting it surfaced. One proposal calls Yaheli’s landing-page observation criticism without explicit wording establishing that judgment; another repeats the garbled “deeper option” comparison. These remain unapproved test outputs. The preceding candidate was better on those details, demonstrating model variability rather than guaranteed improvement. No further model requests were run.

### Actual summary

Yaheli said things had been difficult financially, while the conversation also touched on a job and project work.

They clarified that the relevant regulation was the EU Cyber Resilience Act, not the EU AI Act, which resolved part of their confusion about the project.

The conversation included testing an app’s face tracking, memory retrieval, conversational guidance, and emotional-analysis features, with inconsistent guidance and occasional tracking interruptions.

They noted that performance should improve as models become better and that different models involve tradeoffs between cost and quality.

You planned to test the system using the specific memory and continue working with the available guidance.

You planned to make the model choice changeable to address differences in cost and performance.

The app’s failure to surface the requested memory or provide consistent guidance remained unresolved during the conversation.

### Actual proposals

1. Yaheli said things have been rough for a few days and specifically difficult money-wise.
2. Yaheli corrected the project’s regulation reference: it was the EU Cyber Resilience Act (EU CRA Act), not the EU AI Act.
3. Yaheli recalled that Eden had previously corrected the team about the EU Act.
4. Yaheli criticized the project landing page because the regulation reference is the first thing visitors see there; You described this as disappointing.
5. You planned to test the system using a specific memory after it failed to provide enough guidance.
6. You said you would change the project so users can switch between models; the discussion contrasted cheaper Luna with more expensive Terra and noted worse performance with the deeper option.

Final raw requests/output/usage: `build/memory-scope-20260913/final12/results.json`.

Known review limit: potential-duplicate flags are visible during individual proposal review; approving a summary can approve multiple linked copies together. Inspect the confirmation list for duplicates on multi-chunk calls.
