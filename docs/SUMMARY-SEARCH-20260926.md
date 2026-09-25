# Conversation summaries and unified contact information

## Changes

- Summary instructions have no word, sentence, paragraph or statement-count target. They ask for substantive topic/outcome/decision coverage, remove repetition and small talk, and distinguish offers from agreements. The former 80–160-word target, 500-word total limit and 16-statement limit are removed. Summary editing has no overall length limit either.
- A 16,000-token **transport output ceiling** and bounded request inputs remain for reliability and budget accounting; these are not a requested summary length. An overlarge merge retains saved summary statements with a partial flag instead of cutting them to 500 words. This is not a claim of unlimited provider context/output.
- Schema 6 removes the 280-character summary-row constraint. Complete statements and edited paragraphs remain intact for display and quoting. Existing IDs, row order, evidence, dependencies, approvals and search contents survive migration; migration failure restores the existing backup.
- Home/Live now open **Contact information**. **Conversation history** is inside it; the separate Home History button is removed. Contact edit/alias/merge/export/delete and memory edit/delete remain. Returning from History refreshes the parent.
- Natural-language search already supported approved summaries internally. It now visibly searches both types, shows exact cited summary passages with a link to the conversation, and retains associated-memory controls. Long answers/quotes scroll within the result area instead of forcing an oversized window.
- Approved summary offers/suggestions are searchable with an explicit “not an agreement” source label; ordinary factual eligibility stays conservative. The answer model paraphrases, while the UI renders literal stored quotations. Existing quote/source/contact/deletion validation remains.
- Incomplete summary checkpoints are hidden from the main summary, approval and search. Review explains that generation is unfinished and retains checkpoints for explicit resume. Only current-generation versions are selected; old user-edited versions cannot block a new generation.

## Real API evaluation

User selected **Luna 5.6 low, $0.30 total** for summary/memory generation and search. Normal product defaults were not changed. Three complete previously used call logs were replayed into an isolated database, not the live contact store. The large 8,713-message import was **not** resumed.

| Saved call | Transcript words / turns | Summary words | Proposed memories |
|---|---:|---:|---:|
| Outfit / project discussion | 1,751 / 240 | 194 | 10 |
| Team / project discussion | 1,082 / 150 | 234 | 5 |
| Regulation / model discussion | 621 / 88 | 148 | 7 |

### Assessment

Manual, non-blinded assessment against the full saved transcripts: summaries cover the principal subjects and are substantially shorter than the source without uniformly targeting a length. They are **not error-free**:

- First summary slightly misattributes the speaker of a preparation step.
- Second reverses who needed the task from whom and incorrectly says tracking would continue when the closing transcript says to stop. These need correction before relying on the summary.
- Third overstates an indirect work reference as difficulty finding work rather than retaining the narrower explicit financial difficulty.
- Most of the 22 memory proposals are grounded and understandable. Two need particular scrutiny: a stronger-than-explicit claim that merge conflicts were resolved, and an unsupported gender pronoun. Several clothing/preparation/testing details are short-lived or repetitive, so factuality alone does not make all of them valuable long-term memories.

This is a diagnostic sample, not a blinded improvement claim against the old prompt. No further summary prompt tuning or generation was performed to improve these observed scores.

### Search and visible UI results

Final real-API set: three questions whose requested fact existed only in a summary, three only in memories, three with corroborating memory+summary evidence, and three missing-information/cross-contact questions.

- **9/9 supported questions answered correctly** in manual review, with the required supporting evidence available and cited.
- **3/3 unsupported questions declined**, including asking for another contact's train details.
- All three summary-only cases cited summaries; all three memory-only cases cited the supporting memory. One memory-only answer also cited a topic-related summary unnecessarily.
- All three corroboration cases cited **both** source types.
- All 12 final results passed current-source validation and were replayed through the actual Qt interface: Enter searches without closing, exact summary quotes appear, memory associations appear, History is nested, and complete summaries remain available through Review. Screenshots were inspected after registering the installed font for the offscreen renderer. This is Qt/offscreen automation, not a native computer-use session or physical macOS test.

Initial search testing exposed a hidden approved-offer filter and an invalid model-written quotation. Both failed attempts remain recorded. The filter was narrowed by preserving source type, not treating advice as fact. Exact quoting moved to the UI without weakening quote validation. An intermediate full search run passed; the final run repeated search after complete statement storage was fixed. Original generation responses were replayed locally into intact storage, **not regenerated**.

**Cost: $0.02751291 / $0.30**, 34 API responses: seven generation requests, three initial search requests, twelve corrected search requests and twelve final intact-storage search requests. Zero outstanding reservations. Two early configuration preflights failed before dispatch and cost nothing; their records are retained. All charges use recorded token usage and the application's model price table. Historic ledgers were not reset or reused.

Private evidence: `build/summary-search-20260926/` contains transcripts, request/schema/input snapshots, raw outputs, receipts, costs, timing, isolated databases, questions/expectations, earlier failures, final answers, Qt screenshots and migration/audit checks. Do not commit or upload these private files.

## Safety and review

Offline verification: the full suite passed **420 tests**. After the final answer-area scrolling adjustment, all **34 UI tests** passed again, as did the 12-case saved-answer Qt replay and the API ledger audit. `git diff --check` passed.

Opus 5.5 was invoked with `--effort high` for two scoped read-only reviews. Findings led to complete-statement storage, current-generation selection, stale-parent refresh, historical-kind fallback handling, preservation of unchanged advice metadata on edits and explicit suggestion labels. Migration tests cover linked v5 data and rollback. A private copy of the existing user's saved database also migrated with identical row IDs and hashes across nine data tables; all 489 eligible proposals remained and its unfinished summary was correctly hidden. No live data was migrated, approved, regenerated or deleted during this task.

The running app needs a restart to load the new interface and perform the backed-up migration. Existing saved memories do not need regeneration. Completing the previously interrupted large import remains an explicit generation action with its existing cost considerations; this change does not mark it complete.
