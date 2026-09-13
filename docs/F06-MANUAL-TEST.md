# F06 manual test — updated after user feedback

**Closure update, 2026-09-14:** User accepted F06 as complete for now with documented Luna limitations and authorized publication. No additional final Luna live call or fresh final Opus review is claimed; latest review was Sonnet 5. This closure supersedes older pending-gate statements below. See the master plan closure record.

The earlier preliminary Opus 5 gate passed. Reply direction, Terra-low live guidance, scrolling and linked paragraph/memory review have since changed in response to user feedback. Retest the items below; a fresh final Opus 5 review follows actual results and fixes.

## Setup

From the project directory, launch `.\.venv\Scripts\python.exe -m conversation_copilot`.
Use new contacts named **F06 Test Yaheli** and **F06 Test Alex**, so the test does not edit existing personal memories. Keep the application's normal contact-confirmation step. Use English, the accepted local transcription model, and a consenting role-play participant for the live section.

## Local questions and summary review

1. Select F06 Test Yaheli. Import `conversation_copilot/assets/f06/review-chat.txt`; identify **You** as your participant. Inspect the estimate before accepting extraction. This is fictional data.
2. Open **Review conversation**, choose this imported record, and generate its summary after checking the bounded-run estimate. Confirm loading remains visible until completion, then says draft. The paragraph summary and pending memories should both appear in this window. Before approving anything, Ask Memory should not answer from the pending proposals/draft.
3. Open exact summary sources. Check the appointment date, **3 PM**, **Cedar Clinic**, the concise/direct preference and the unconfirmed Nora follow-up against their numbered original turns. No meeting should be invented. Before approval, reject any unwanted linked proposal. Approve the summary: the confirmation must list its linked pending memories, and both the summary and those memories should become approved together. Unrelated proposals stay pending and rejected items stay rejected. Its supported facts should now be available in Ask.
4. In Ask Memory select F06 Test Yaheli explicitly. Ask “What time is the dentist appointment?” and “Where is the dentist appointment?” Expect the correct date/time/venue, labeled source and confidence. Open the exact source. Choose that event, then ask “and where?” Close/reopen Ask or press New question; “and where?” must require event selection again.
5. Change only Ask's scope to F06 Test Alex. Yaheli's appointment must disappear, while the main window's selected contact remains Yaheli. Try explicit all-contact discovery: sources must be labeled by contact, and cloud help must require returning to one contact/event. Never accept silent cross-contact answering.
6. Use a fresh draft to test a rejected proposal: reject it before approving the summary. Its linked statement must stay excluded; summary approval must not reverse the rejection. Explicit summary-only restoration does not approve a rejected proposal.
7. Click the appointment sentence, choose Edit / Save changes, change 3 PM to 4 PM, and confirm the linked memory to update. Verify both views change. Then Edit linked memory to 5 PM and choose to sync its sentence; verify both views again. Pending items stay pending until approval. Cancel an edit and verify neither changes. When retaining old wording on an approved-memory correction, Ask must label it as prior history.
8. Mark a statement sensitive and block cloud use. Local evidence should remain available; explicit cloud help must withhold it. Allowing its summary statement alone must not override a linked memory's blocked cloud permission. Check the prompt/estimate before any paid action.
9. Leave an appointment answer/source preview open, then delete the test dentist memory. The displayed stale answer must clear; dependent summary text must be scrubbed. Generate another summary for that record: the deleted appointment must not return from the retained transcript. Note that conservative shared-turn suppression can remove other facts from the same turn.

Additional lifecycle checks: Start/Stop before any speech, then open Review conversation; the empty record must be selectable without an exception. If a bounded summary run is interrupted, edit/remove the partial draft before approving; this closes its model checkpoint and later regeneration creates a separate draft. If merging the two fictional contacts, inspect the withholding notice and multi-select memories for one source review. For an existing legacy quarantine, use Review legacy source exclusions only if you can personally establish that selected exact turns contain no previously deleted facts; otherwise leave it quarantined.

Date check: ask for the imported appointment recorded 08/09/2026 using Recorded date. During the live role-play say an appointment is “tomorrow”; verify the source date and derived event date use the displayed local date, including the original timestamp. Unknown source zones must remain unresolved.

## Consenting live role-play

10. Use WhatsApp Desktop or the dedicated Chrome Meet configuration already tested on September 7. Do not treat this as new support for other clients. Confirm the role-play contact and verify both speakers' attributed finalized words. Talk normally for several turns using only fictional plans and the approved preference.
11. Grade acknowledgment coverage: first-person commitments such as “I will” or “See you Tuesday” are conservatively withheld unless already supported by your recent wording; some checkpoints can have no candidate. Inspect Reply, Remember and Follow up: up to two visible alternatives per category, optional More for an already prepared third. Nothing is sent automatically. Dismiss a candidate; paraphrases should stay suppressed until a topic reset or Suggest now. A distinct suggestion should remain available; report paraphrases that reappear or distinct suggestions that are incorrectly suppressed.
12. Observe automatic updates and stability. They must not churn faster than the 12-second policy; unsupported guidance should disappear around 24 seconds even during silence. Say “Correction: four PM, not three” or “Moving on, let's discuss the book”; misleading old guidance must clear. Suggest now is one explicit refresh and shares the call budget; once it returns, its candidates should appear immediately even inside the automatic stability interval. Tone uncertainty must remain cautious while supported factual replies can still appear.
13. Open Ask while the call continues; switch its scope and query a test memory. Capture/transcription and speaker attribution must continue. Check pending/error behavior, focus/keyboard navigation, legibility, panel resizing and access to every control. More must not trigger another paid request. Do not spend down the budget solely to test exhaustion; that branch has fake-client coverage.
14. Stop. Live guidance must clear and no new live request should begin. Summary/extraction stays tied to that stopped record and the original call allowance. Review the paragraph draft and its memories side by side. Summary approval includes only the linked pending memories listed in its confirmation. If work remains pending, inspect the explicit continuation estimate and $0.25 run cap before deciding whether to continue.

Ask follow-up scope is deliberately explicit: choose an event before “and where?” or “what time?”. Previous generated answers and stored question history are not retrieval evidence or cloud context. The multiple-preference notice requests a human conflict review; it does not claim automatic conflict detection. After closing Ask or stopping the call, paused local embedding backfill should resume. Guidance category order must stay Reply, Remember, Follow up as categories empty and return.

Ask retains the existing conservative bereavement filter: an indirect, semantic-only loss query can return no match. Use a direct subject query and inspect the approved source rather than infer a missing fact.

## Report actual results

Send the platform used, steps passed/failed, exact unexpected behavior and any displayed error. Rate usefulness, distraction, wording naturalness, and confidence/source clarity from 1–5. Report missing or wrongly attributed turns and slow/blocked controls. Screenshots are optional; omit real personal information.

Cleanup is optional: delete only the two deliberately created F06 Test contacts after recording results. Do not delete existing contacts or the unrelated CV files.

After these actual results, fixes may require targeted rechecks. A fresh tool-disabled verified Opus 5 final review and verified commit/push are still required before F06 completion.

Approved style preferences may influence guidance without matching the current topic. Sensitive approved memories may appear locally in Possible remembered context and Remember; cloud permissions must still be respected. Please grade relevance and discretion of these local reminders.

Sensitive local-only memories share the four live retrieval slots and can displace cloud-eligible context, leaving fewer memories for the model. Report whether that reduces guidance usefulness. If you change an Ask question, ask locally again before Use cloud help.

An empty record has no attributed text, so generating its review may report that honestly. During guidance updates, check whether keyboard focus moves unexpectedly.

## Focused recheck for the reported reply-direction issue

Restart the app to load **Live guidance: Terra · low reasoning**. Ask the contact a question, then pause: no candidate should answer you as if it were the contact. Let the contact reply; suggestions should now be things you could say back, using your wording style and avoiding questions you already asked. Speak again: old reply/follow-up candidates should clear, including an in-flight stale response. Grade actual relevance and wording; fewer/no candidates remains possible under the commitment guard.

Generate a fresh summary to see the new prose instructions. Existing stored summaries are not silently regenerated. Check the loading indicator, sentence editing, linked-memory editing, combined approval, scrolling and visibility of both panels. No remaining manual step is treated as passed until you report its outcome.
