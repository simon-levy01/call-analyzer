# F06 — Live Guidance, Ask Memory, and Post-call Review

**Status:** Approved feature plan — implementation not started

**Planning started:** 2026-09-07

**Final approval:** 2026-09-08, including explicit Claude Opus 5 gates before and after the user's manual testing

**Target completion:** 2026-09-22

**Windows project deadline:** 2026-10-01

**Inspected baseline:** `e0af1553fe63b333008f2f3ab227a7c0cb71942e`

**Existing roadmap card:** https://trello.com/c/ljon1I03/26-f06-live-guidance-and-post-call-review-target-sep-22

## Planning boundaries

F01–F05 are complete and accepted as tested. Planning inspects their implementation and recorded evidence without rerunning tests or reopening their completion gates. Later F06 implementation must test its changes and affected integration surfaces. This session produces documentation and Trello planning updates only; no F06 implementation.

Preserve the master plan's Windows-first platform commitments, English-only transcription, one confirmed contact per Assisted Call, audio continuity after visual loss, explicit source selection, local text/memory ownership, sensitive-memory cloud permissions, and no raw audio/video retention or automatic sending of replies. Preserve historical validation exceptions and the later September 7 Meet evidence without expanding its claims. F09 remains after F08 without a committed date.

## Approved decisions from the interview

### Round 1 — display and Ask Memory interaction

- **Q1, user decision:** Show two suggested responses in **Reply**, two relevant details/reminders/talking points in **Remember**, and two questions in **Follow up** by default. Each category supports up to three candidates, with the third accessible through **More**. These are capacity limits, not a requirement to invent enough items to fill the display. Existing tone/cue interpretation remains available.
- **Q2, user approval of recommendation:** Ask Memory supports short conversational follow-ups. Keep the selected contact and explicitly identified event as context while the panel is open; **New question** clears that context. Every answer retrieves current eligible evidence again. Earlier generated answers are never evidence.

### Round 2 — automatic guidance and display lifecycle

- **Q3, user approval of recommendation:** Generate guidance automatically after meaningful new finalized speech, no more frequently than the existing 12-second cadence. Provide **Suggest now** for an explicit fresh request. Automatic and requested cloud work share the call budget. Categories may remain empty when no useful supported suggestion exists. Shared scheduling and request limits are specified below; this does not authorize an additional unbounded request loop.
- **Q4, user approval of recommendation:** Keep a suggestion stable for at least 12 seconds unless new evidence makes it misleading or its contact/source becomes invalid. Remove it after 24 seconds without renewed supporting context. **Dismiss** hides the suggestion and ordinary refreshes cannot immediately restore the same suggestion. **More** reveals an already prepared third candidate without another API request. **Suggest now** explicitly requests fresh candidates. All candidates, including hidden ones, remain subject to current evidence and lifecycle checks.

### Round 3 — budget and manual summary approval

- **Q5, user decision:** Increase the Assisted Call hard budget to **$0.35**, reserving **$0.08** for post-call summary/extraction. Paid live work therefore has a **$0.27** ceiling, including committed spend and in-flight reservations; unused live funds remain available after Stop. Keep the existing $0.15 warning unless subsequently changed. Explicit requests take priority over queued automatic suggestions within the same limits. Local search and transcription continue when paid work stops. This is an approved F06 implementation change, not a claim that current code already enforces it.
- **Q5, long-call decision:** If post-call work cannot fit the remaining call budget, retain it as pending. Offer an explicit button showing the cost estimate for processing the remaining work. Reuse bounded, resumable processing; no automatic over-budget continuation. The final contract below reuses the existing separately capped manual-analysis limit.
- **Q6, user decision:** Generate and save a local summary draft after Stop; require an explicit review/approval action before it becomes searchable. The user can correct/remove statements before approval. Summary approval and Memory Proposal approval are distinct manual actions; neither approves the other. Only Approved Summaries and Approved Memories may supply Ask Memory search evidence. Unreviewed drafts and proposals are excluded. Automatic approval is a possible later change and is outside F06.

### Round 4 — summary content and rejection

- **Q7, user approval of recommendation:** Use four short summary sections, omitting empty ones: **Discussed** (key topics/details), **Plans and commitments** (appointments, agreed actions, responsible person, stated dates/times), **Open questions** (unresolved points), and **Follow-ups** (explicitly agreed actions distinguished from suggestions worth considering). Every factual statement links to supporting turns. Exclude inferred feelings, diagnoses, and invented agreements. Present existing Memory Proposals alongside the summary through the existing review queue.
- **Q8, user decision:** Rejecting a Memory Proposal also excludes its linked summary statement from Ask Memory. The same fact must not return through summary search merely because it has a different representation. Only an explicit restoration/approval during summary review may reverse that rejection for the summary statement. Rejection and deletion are distinct; this approval does not permit silently restoring deleted content.

### Round 5 — local selection strategy and controlled cloud fallback

- **Q9, user approval of recommendation:** Start Ask Memory with structured/source-based answers plus existing local semantic retrieval. Evaluate an optional small local LLM only if fixed F06 appointment, paraphrase, or follow-up cases expose meaningful failures. Adopt it only if measured improvement justifies complete download/install size, runtime RAM, CPU latency, packaging effort, and concurrent-call impact. No particular new model is selected. Do not build a large handwritten language parser to avoid evaluating a small model.
- **Q10, user decision:** Cloud fallback requires a **Use cloud help** action for each request with an estimate shown first; never invoke it automatically. The hard ceiling is **$0.04 per cloud-assisted answer** and **$0.13 per outside-call Ask session**. During a call, cloud-assisted Ask also shares the live portion of the $0.35 call budget, preserving the $0.08 post-call reserve. These are ceilings rather than expected spend; record actual cost during testing, and lower them only if the user subsequently requests it. Cloud fallback cannot manufacture missing evidence or bypass sensitive-memory permissions.

### Round 6 — in-call availability and temporary history

- **Q11, user approval of recommendation:** Ask Memory remains available during calls in a separate panel initially scoped to the call's confirmed contact. An explicit Ask contact change does not reassign the Assisted Call. Capture and transcription have priority; busy local processing makes Ask wait or offer available simpler local search. It never silently switches to cloud processing.
- **Q12, user approval of recommendation:** Retain Ask questions, answers, and follow-up context only in memory while the panel is open. Closing it clears that content; nothing becomes a memory automatically. Keep content-free outside-call spend totals for the current app run: closing/reopening the panel, **New question**, and contact changes do not reset the $0.13 allowance. Restarting the app starts a new allowance. Call-funded and outside-call usage remain distinguishable so changing UI scope cannot reset or evade either budget.

### Round 7 — personalization and summary lifecycle

- **Q13, user approval of recommendation:** The two replies are useful alternatives suited to the exchange (for example acknowledgment and clarification), both respecting approved contact-specific communication preferences. With no approved preference use clear, neutral, concise language. Relationship labels alone do not imply formal/casual/gentle style. Conflicting approved preferences are flagged for review rather than silently resolved.
- **Q14, user correction to recommendation:** Correcting a memory must prompt the user about whether related obsolete summary statements should be removed; an edit does not necessarily make those statements irrelevant. Do not automatically delete them merely because their linked memory revision changed. Q15 resolves current-versus-historical search treatment of kept statements.
- **Q14, remaining recommendations approved:** **Save changes** on an approved summary explicitly approves the edited version. Label user corrections honestly rather than representing original transcript wording as the correction. Memory deletion removes affected summary content from search, and regeneration cannot restore it. **Delete summary** removes its content and search derivatives while retaining the Conversation Record and independently Approved Memories. **Delete conversation** removes its summaries and uses F05's existing preview for deleting or explicitly retaining derived memories.

### Round 8 — retained historical statements and optional local-model limits

- **Q15, user approval of recommendation:** During memory correction show old/new memory and affected summary statements together with explicit **Keep / Remove** choices. Kept statements remain searchable. If the edit leaves a statement accurate, it remains ordinary summary evidence; if it contradicts the correction, label it as a dated prior statement with a linked correction rather than use it silently as the current fact. An original 3 PM appointment statement may remain useful history while the current approved appointment time is 4 PM.
- **Q16, user approval of proposed limits:** An optional local LLM must add at most **1 GB total download** (model, tokenizer, runtime), at most **1.5 GB peak RAM**, and meet **3-second p95 warm answers** on the development machine. Concurrent use must produce no dropped transcription work or capture failures and worsen transcription p95 by no more than **10%**. Measure total application footprint too. These are future F06 acceptance limits, not measured results. A model that fails these limits or provides no material answer improvement is not adopted.
- **Q16, user preference:** Prefer cloud in general so people with less capable PCs can use the application; the user is still willing to evaluate a local model. Treat an additional local LLM as optional and keep it out of the required installation. Q17 confirms the relationship to existing local search and per-request cloud control.

### Round 9 — preferred enhancement and historical summaries

- **Q17, user approval of recommendation:** Existing free local search and source-based answers remain the default. Explicit **Use cloud help** is the preferred enhancement for difficult answers. Any additional local LLM remains an optional experiment excluded from normal installation; it is not a prerequisite for F06 completion. Per-request cloud confirmation and the approved limits remain unchanged.
- **Q18, user approval of recommendation:** Automatically draft a summary after a new call within its budget. Offer **Generate summary** for one selected historical call or imported Conversation Record, with an estimate before processing. Do not automatically summarize an entire contact history. Historical summaries require the same manual review and approval before search.

## Inspected reuse and planning implications

- Extend the current Tkinter application; there is no web UI to replace.
- Reuse `MemoryStore` contact/alias confirmation, approved revisions, provenance, lifecycle transactions, extraction, proposal review, and explicit all-contact search controls.
- Reuse SQLite/FTS5 and FastEmbed/BGE-small before proposing another retrieval system. F05 recorded lexical 0/3 versus semantic 3/3 on indirect employment references. Documented model cache is 67,181,383 bytes; 500-character local retrieval p95 is 207.455 ms. These are existing F05 results, not new F06 measurements. Total dependency size, peak runtime RAM, and concurrent-call performance are not established by those figures.
- The live eight-turn/500-character semantic context and topic-transition pause are designed for calls, not independent Ask Memory queries. Preserve lifecycle and relevance protections without forcing a one-shot question to supply four conversation turns.
- Calendar-day normalization currently discards clock time; exact appointment time survives in source/content wording. Decide the minimum precise temporal representation before implementation.
- Correction/deletion of a memory leaves the original Conversation Record intact. Independent summary indexing could revive obsolete information. F06 needs dependency-aware invalidation and regeneration suppression; correction additionally requires the Q14 user choice about keeping related summary statements rather than automatically deleting them.
- A deliberately retained Approved Memory whose source was deleted has only minimal provenance. It cannot supply an original-source quotation or functioning source link.
- Reuse F04 bounded structured requests, `store=false`, usage reservations, one-in-flight/latest-pending work, stable cards, and generation invalidation. Inspected code uses $0.15/$0.25 warning/hard limits and post-call extraction shares that ledger; Q5 approves changing the F06 hard limit to $0.35 with an $0.08 post-call reserve. The 400-token F04 output limit does not establish sufficient capacity for F06's additional candidates.
- Reuse the basic and HeyGen fixtures within their recorded limitations. No existing result establishes F06 answer quality or useful-suggestion acceptance.

## Query-approach comparison — evidence before selection

This comparison does not select a new model or authorize installing one during planning. The inspected Windows host has an AMD Ryzen 9 3900X (12 cores/24 logical processors) and 68,624,113,664 bytes of physical RAM (about 64 GiB). The generous development host does not replace lightweight deployment targets.

| Approach | Usefulness and limitations | Downloads/packaging | Runtime and call impact | Per-query API cost |
|---|---|---|---|---|
| 1. Existing SQL/FTS5, structured fields, modest rules, source snippets/templates | Strong for exact appointments and factual quotations; weaker for paraphrases; avoid an expanding handwritten language parser | No new model/runtime dependency over F05; F06 data/schema/UI work still required | F06 answer-path RAM/latency unmeasured; lowest added processing is the expected starting point, not a measured claim | None |
| 2. Existing local BGE-small retrieval plus modest query/follow-up handling | F05 demonstrated indirect-reference uplift; retrieval still cannot safely manufacture an answer or resolve ambiguous identities | Reuses installed FastEmbed/ONNX/NumPy; recorded model cache 67,181,383 bytes, not the complete dependency footprint | Recorded F05 500-character retrieval p95 207.455 ms; F06 answer latency, peak RAM, cold start, all-contact search and concurrent-call contention remain unmeasured | None |
| 3. Optional small quantized local LLM for rewriting or grounded wording | Must beat approaches 1+2 on fixed F06 paraphrase/follow-up cases; generative factual errors remain possible | Requires model/tokenizer plus pinned compatible runtime and Windows/offline packaging; total compressed download and expanded install size must be measured | CPU p50/p95, peak working/private RAM, context/cache overhead, cold load/unload and transcription/video interference must be measured; model weight alone proves none of these | None |
| 4. Explicit inexpensive OpenAI fallback | May help grounded wording or difficult query handling only over bounded eligible candidates; cannot create missing evidence or relax scope/permissions | Reuses current SDK/key/structured-output/ledger path; no new local model package | Network latency and token reservations; local retrieval still required; F06 measured usefulness/latency/cost gate remains necessary | Explicit bounded paid request; never silently substitute for local mode |

Primary technical references checked 2026-09-07: [FastEmbed throughput controls](https://qdrant.tech/documentation/fastembed/fastembed-optimize/) describe independent batching/thread/process controls; the existing code sets two embedding threads. [llama.cpp](https://github.com/ggml-org/llama.cpp) documents local C/C++ inference and quantized model support, making it a possible runtime to compare rather than an approved dependency. The [official SmolLM2-360M model card](https://huggingface.co/HuggingFaceTB/SmolLM2-360M-Instruct) is one example of a sub-billion-parameter instruction model with CPU usage and stated limitations; it is not selected, and its general model-card results do not establish appointment-answer accuracy in this project.

No new model inference, performance benchmark, installation, paid request, or accepted F01–F05 test was run during this comparison. F06 must record complete-stack download/install measurements and process-level runtime measurements rather than filling gaps with model-size estimates.

## Outcome, scope, and non-goals

Deliver a demonstrable loop: confirm a contact, receive useful memory-assisted replies/reminders/questions, stop and review a grounded summary and existing memory proposals, then ask natural-language questions outside or during another call with precise supporting sources.

Include the existing desktop shell, contact-scoped local search, short Ask follow-ups, explicit all-contact discovery, approved summary search, source previews, manual review/correction/deletion, measured cloud assistance, and stable live updates. Live personalization uses Approved Memories; summaries initially supply Ask Memory and post-call review, not another automatic live-context feed. English is the F06 evaluated query/guidance language; names and aliases retain Unicode. Do not claim Hebrew semantic/question support from English-model or synthetic-Hebrew fixture results.

Exclude automatic approval, automatic reply sending, external reminders/calendar creation, persistent Ask chat history, raw transcript search as an independent Ask evidence corpus, automatic whole-history backfill, cross-contact synthesized profiles, a new memory extraction pipeline, general chat, web lookup as answer evidence, new embedding/vector/graph systems, mandatory local LLM installation, a web UI rewrite, and F07/F08/F09 implementation. A reminder is an on-screen suggestion, not a scheduled notification.

## Concrete user flows

### Live guidance

1. Keep F05 contact confirmation. Before confirmation, existing memory-free tone/cue interpretation may continue; personalized F06 categories stay unavailable with a contact-selection prompt. Do not infer identity from a face or name alone.
2. After meaningful new finalized speech, retrieve current contact facts plus relevant approved communication/relationship preferences. Use one combined cloud interpretation/guidance request, not an independent paid loop per category. At most one automatic start every 12 seconds across the combined stream.
3. Show up to two candidates each under **Reply**, **Remember**, and **Follow up**, with confidence and a compact evidence control. **More** reveals an available third, already generated candidate. Do not render empty placeholder cards or pad weak categories to reach two/three. Existing F04 tone/cue presentation and cautious calibration remain intact.
4. Prefer two genuinely useful alternatives over paraphrases. Remember includes relevant facts, reminders, or talking points; a follow-up based on uncertainty should ask rather than assume. A relevant approved style may influence wording, but cannot invent a new preference or generalize behavior to other contacts. Reserve at most two of the four memory excerpt slots for relevant approved style; do not expand the memory allowance to build an opaque profile.
5. **Suggest now** refreshes the newest evidence explicitly, shares the live budget, and is disabled while its equivalent request is pending. Repeated clicks coalesce rather than queue charges. Keep existing explicit Terra checks available under the same live ceiling; Terra never becomes an automatic guidance model.
6. Stable display: a normal item remains for at least 12 seconds, expires 24 seconds after its last fresh supporting match, and is checked by a timer even during silence. Repeated wording or score jitter does not reset its lifetime. An old transcript snapshot does not count as fresh supporting context. Contact/source/permission invalidation, a material contradiction, Stop, or a new topic that makes the item misleading overrides the display floor immediately.
7. Dismissal applies to the category, source identities/revisions, and normalized suggestion meaning for the current topic. It survives automatic paraphrasing. Clear it on explicit **Suggest now**, a newly established topic, or a new call; never let a lifecycle change resurrect invalid evidence. Prefer a bounded per-call fingerprint set and existing topic evidence, not a new semantic topic model.
8. Visual loss keeps audio-led guidance usable from remaining evidence. No face means no facial-evidence claim. Stop clears live/hidden guidance and invalidates late workers, then opens post-call review after finalization.

### Ask Memory

1. Open the nonmodal panel outside or during a call. Show its scope prominently. In-call initial scope is the confirmed call contact; outside a call require an explicit contact selection unless the user already selected one in the current UI. Ask contact changes never reassign the call.
2. A name/alias in a question may suggest an existing contact; a different or ambiguous name cannot silently override the visible scope. Offer labeled contact candidates with disambiguators. Resolve identity before retrieving content. Never create a contact merely because a question names someone.
3. **All contacts** is an explicit local discovery mode. Search approved eligible memory and summary indexes with contact labels on every result; show at most 12 ranked results, with ordinary paging for more. Choose a contact/event before conversational continuation or cloud answer generation. This avoids blending people into one answer and keeps cloud scope concrete. Initial all-contact discovery uses FTS5/structured filters; label that scope's reduced paraphrase recall and offer contact selection for semantic retrieval. No unbounded embedding fan-out over every contact.
4. Accept a bounded natural-language question. Resolve obvious follow-ups from an explicitly chosen event and up to the last three user questions; do not feed prior generated answer prose back as factual context. Keep at most six exchanges visible in memory and expose **New question**. If reference resolution is uncertain, ask which event rather than guess.
5. Retrieve locally, validate current approval/contact/lifecycle/permission/source state, and return an answer, possibilities, clarification, no match, conflict, or unavailable. A grounded quote with a short template introduction is a valid answer; do not require fluent generation when the quote directly answers the question.
6. Show source type (**Approved memory**, **Approved summary**, **User correction**, or **Prior statement — corrected**), contact, conversation/source date, event date/time when known, and confidence. Open the exact local record and supporting turns in one shared source preview. Links use stable local IDs, not arbitrary model-generated file paths/URLs. Construct labels and targets locally.
7. **Use cloud help** shows the bounded request estimate and requires a click for that question. Only the question, resolved scope/follow-up context, and permitted evidence snippets are sent, using `store=false`. No evidence means no paid factual-answer attempt; suggest refining the question. Filter permissions again immediately before serialization and before showing the result.
8. Changing scope or **New question** clears conversational context and invalidates late replies. Closing the panel erases its questions/answers. Content-free spend accounting survives until app exit. A request started during a call stays charged to that call even if it finishes after Stop; an outside-call request cannot evade limits by starting a call mid-flight.

### Post-call and historical review

1. Finalize and persist attributed text once, using F05's existing call-finalization/assignment flow. Unassigned records remain unsearchable and do not enter cloud summary/extraction until assigned. Empty or unusable records produce a clear unavailable/empty result rather than fabricated content.
2. Use bounded chronological source chunks to generate the four approved summary sections. Run existing `analyze_record()` extraction once and expose its batch in the same review experience. F06 adds summary generation; it does not duplicate extraction, approve proposals, or treat an extraction batch as a summary. Link statements and proposals through their source turns before search approval is possible.
3. Estimate the whole pending summary/extraction job, including consolidation, before starting automatic post-call processing. Reuse completed chunks after failure. If the remaining call funds cannot cover it, retain the record/job as pending and offer an explicit **Process remaining review — estimated $…** action. Each separately authorized continuation has a $0.25 hard cap, reusing the established manual-analysis limit; show both expected cost and conservative maximum. If the job exceeds that cap, offer a bounded resumable portion, never silently raise the cap or reset it in a loop. Permit only one running review job per record/ledger; duplicate buttons cannot start another extraction or summary job.
4. Show **Summary draft — not searchable** alongside the existing proposal batch. Review/edit/remove individual statements, inspect evidence, then **Approve summary**. Proposals retain separate approve/edit/reject/reopen controls, duplicate flags, and likely-generic grouping. No approval preselection or background approval.
5. Summary sections distinguish actual commitments from suggested follow-ups. Suggested actions are advice, not facts or commitments and cannot answer factual Ask queries. Approved factual statements become searchable individually. Keep at most 16 factual/advice statements per summary, up to four per section and 500 words total; omissions/partial coverage are explicit. Completeness is measured against salient facts, not every conversational detail.
6. Regeneration creates a separate draft without silently overwriting the approved version. Approval replaces the current summary version and updates its indexes transactionally. **Save changes** on an approved summary is explicit approval of the edited version; changed factual values are labeled as user corrections, with correction time and original-source context rather than fabricated transcript quotations.
7. **Generate summary** also works on one explicitly selected stopped historical call or confirmed import with estimate/approval controls. It does not trigger a second extraction if that record's current batch already exists. No whole-contact backfill or automatic indexing of past raw transcripts.

## Evidence, dates, and failure behavior

| Situation | Required behavior |
|---|---|
| One appointment matches | State the supported time and identify the appointment, contact, event date (if known), source date and source reference. Quote rather than invent missing precision. |
| Two appointments fit | Show up to three dated alternatives and ask which; similarity or recency alone cannot silently identify the event. Expand candidates through bounded local paging if needed. |
| Follow-up such as “where?” | Requery the selected event's current approved evidence. If venue is absent, say so; never infer it from a previous answer. |
| No match | Say no approved evidence was found in the displayed scope. Offer narrower wording/contact/date choices. Distinguish reduced semantic availability and incomplete corpus coverage from a definitive absence claim. |
| Conflicting current facts / `needs_review` memory | Show the disagreement or request review. Do not pick by confidence score alone. Exclude unresolved reassigned items from assertive F06 answers/live personalization until reviewed. Add an explicit **Confirm reviewed memory** action that shows the current content/contact/provenance and clears `needs_review` transactionally, invalidating results; existing F05 has no clearing action. Editing alone does not silently resolve it. |
| Old fact without a correction | Say “As of [source date]…” when current validity matters. Age does not delete or supersede memory. |
| Sensitive approved memory | Available in local Ask under existing permissions. Local Remember may display a directly relevant approved excerpt without cloud processing. No sensitive content or derived paraphrase enters cloud prompts without the relevant current permission. |
| Summary sensitivity | Inherit the most restrictive linked evidence permission. Newly sensitive summary statements are local-only by default, using the same explicit per-item cloud permission semantics. Summary approval never grants cloud permission. A permissive summary flag cannot override a linked sensitive memory's refusal/revocation. Filter source spans linked to known cloud-forbidden sensitive memories before initial summary generation, regeneration, consolidation or cloud Ask, not merely after a summary exists; omit the whole turn if safe span separation is unavailable and show partial coverage. |
| Source deliberately deleted, memory explicitly retained | An answer may quote the current approved memory as a memory, labeled “Original source deleted” with approximate date; no reconstructed transcript quotation or working source link is claimed. |
| Missing source unexpectedly / invalid turn ID | Withhold the unsupported statement, report source unavailable, and offer source review. Never invent a replacement citation. |
| Cloud failure, refusal, invalid/truncated output, timeout | Keep valid local results with an honest status. Never display an unvalidated partial answer. Conservatively account for uncertain billing; retry only within the existing bounded retry and request/session caps. |
| Local model unavailable / busy / DB lock | Keep local FTS/structured search when safe and label reduced capability; otherwise show busy/unavailable. UI/capture never block, no surprise downloads or paid fallback. |
| Untrusted source or question instructions | Treat text as data. It cannot change contact, permissions, budget, output schema, or access arbitrary files/network resources. |

Temporal rules reuse the glossary's Temporal Reference: preserve original wording; distinguish source/recorded date from event date. Source-relative “tomorrow” is anchored to the cited turn's timestamp and source zone, not the day the user asks or the start date of a call that crossed midnight. Use a record date only as a visibly labeled fallback when exact turn timing is unavailable; ambiguity remains unresolved. Query-relative “yesterday/last week” uses the query's displayed local reference date/zone; last week means the preceding Monday–Sunday calendar interval. If recorded-date versus event-date intent is unclear, ask or expose the existing date filter explicitly. ISO dates and the app's displayed DD/MM/YYYY are supported; ambiguous numeric forms require confirmation rather than a US-format guess. An omitted year crossing plausible years is unresolved rather than silently forced to this year.

Store a clock time only when AM/PM or 24-hour meaning is supported. Keep “7 my time” unresolved unless an approved source/contact zone supplies enough context; missing zone means a wall-clock quote, not an invented UTC instant. Use `datetime`/`zoneinfo` for supported known-zone conversion, retaining original text and zone; unsupported zone/DST ambiguity stays unresolved. Minimal date/field handling may use existing helpers and native controls; do not grow a general language parser. A small local rewrite model or explicit cloud help must preserve, not guess, unresolved fields.

## Summary dependencies, correction, rejection, and deletion

Search eligibility is enforced before ranking and again at emission for memories **and** summaries. Being in an approved summary cannot bypass contact, source, revision, rejection, deletion, sensitivity or cloud permissions. A summary is a reviewed account of a specific conversation, not an automatically approved atomic fact store.

- Every statement has stable identity, exact record/turn references, source generation, author origin, approval state and any linked proposal/memory identities/revisions. Establish links before approval; shared-turn overlap is conservatively linked when precise claim matching is uncertain. Do not use semantic similarity alone as a deletion/retention authorization.
- On memory correction, preview linked statements with old/new memory and explicit Keep/Remove choices. Cancel leaves the correction unapplied. Commit the approved memory revision and resolved statement choices together. Keep with unchanged meaning preserves normal evidence. Keep with a changed factual value marks the prior statement as historical and links the new revision. It can answer “what was originally said?” but cannot override the current fact. Unknown compatibility remains historical/conflicting until explicitly reviewed; it is not auto-deleted.
- On rejection, immediately exclude linked statements from Ask indexes and mark them visibly excluded in review. Summary approval cannot accidentally restore them through a bulk action. Explicit restoration of that statement is separate, intentional approval and does not approve the rejected Memory Proposal.
- On memory deletion, scrub dependent summary text in all retained draft/current/old summary versions and their FTS/vector/source-derived caches. Record content-free source-turn suppression **before** F05 deletes memory provenance. Source records themselves retain F05's existing separate lifecycle. Regeneration excludes suppressed source spans; it cannot re-create the deleted fact from the retained transcript. Conservative suppression may omit another fact from the same turn; state that limitation and allow fresh user-authored information, not hidden restoration.
- Source/contact deletion covers all summary versions, pending chunks, dependencies, exclusions and derived indexes as appropriate in the same transaction. Explicitly retained memories follow F05's deleted-source provenance behavior; summaries are deleted with their record. Reassignment invalidates summaries for review under the corrected contact; merge preserves same-person ownership but revalidates links, permission and current generations. No old Ask context survives either operation.
- An F05-era tombstone may retain only contact ownership and deletion time, not enough provenance to know which historical record/turn was deleted. Do not pretend migration can reconstruct it. For a contact with such tombstones, quarantine that contact's pre-migration retained records from automatic summary generation/search until explicit source review establishes eligible turns; if contact ownership itself is uncertain, use the broader conservative affected-store boundary. If safety cannot be established, offer current approved-memory answers and report that historical summary coverage is unavailable. Include a legacy-deletion scenario in migration/evaluation. This is a conservative limitation, not permission to revive deleted data.
- Generation/race handling applies to hidden third candidates, source previews, Ask follow-ups, paid results, summary approval, exports and pending summary workers. Recheck record/contact/revision/permission generations before committing or displaying. Validation success is not permission to use a later-invalidated item.

## Minimum data and code changes

Keep the current SQLite store, direct transactions, FastEmbed/NumPy and Tkinter worker/poll pattern. Extend the real seams in `memory.py`, `semantic.py`, `interpretation.py`, and `__main__.py`; small `guidance.py`/`ask_memory.py` modules are justified only by actual cohesive logic. Do not introduce an ORM, provider hierarchy, vector DB, event bus, general scheduler or new frontend.

**General implementation discipline, reaffirmed 2026-09-08:** Do not overengineer. Trace the actual flow and every caller before changing shared logic; reuse existing code, then standard-library/native capabilities, then installed dependencies. Prefer the smallest cohesive implementation that satisfies the approved contract. No speculative abstractions, duplicate pipelines, framework replacement, or scaffolding for later features. Fix root causes, not individual symptoms. Keep validation, privacy, accessibility, data-loss prevention and requested behavior intact; simplicity is not permission to skip tests or review. Follow F05's general pattern of slices, focused checks, evidence, Claude findings/corrections, final audit and verified release.

Minimum migration from schema v3 (final physical names may follow current conventions):

| Data | Minimum purpose |
|---|---|
| Summary run/version rows | Record FK/generation, draft/approved/current state, schema/model version, timestamps, bounded resumable chunk coverage and job usage metadata. Retain only versions needed for current review/history; deleting removes all content versions. |
| Summary statement rows | Summary FK, stable statement ID, section, bounded text, fact/advice/historical status, confidence, approval/exclusion, user-correction origin, sensitivity/cloud permission, original/normalized temporal fields. |
| Statement evidence/dependency rows | Exact source record/turns and links to proposal/memory/revision identities; enough to perform correction prompts, permission intersection, rejection/deletion and citation lookup. |
| Content-free source exclusion rows | Record/turn range, exclusion reason, opaque lifecycle identity/time; survive deletion of original memory provenance and prevent regeneration. Remove with the source/contact. Do not retain deleted text in this table. |
| Summary FTS5 index | Current approved eligible factual/historical statements only; historical results clearly typed. Synchronize transactionally. Add existing-BGE summary vectors only if the F06 baseline shows useful paraphrase uplift; no new embedding model. |
| Optional temporal columns on existing proposal/revision rows | Preserve original date/time wording; add nullable validated clock-time and zone fields where needed while retaining current day-range columns. Existing date-only rows remain date-only; never fill midnight/zone by guess. |

No durable Ask question/answer table. Reuse content-free usage accounting and keep app-run outside-call totals in memory. Source URLs, display timestamps and candidate labels are derived rather than persisted repeatedly. Exports extend the existing versioned JSON format to include summaries, review state, dependencies, permission and content-free exclusions; omit search/vector caches and Ask history. Bump the export version only if the shape changes and test version rejection. No speculative import/sync feature.

Also add the explicit `needs_review` resolution transaction/UI action above; otherwise the new F06 exclusion would be permanent. Historical summary generation must not bypass sensitive-memory permissions by using the original raw text as an alternate source. New call-text submission follows the existing bounded transcript permission; once restrictive linked memory evidence is known, F06 summary/cloud paths enforce it. Do not change or rerun F05 extraction as a workaround for a withheld summary source.

Use F05's transactional migration/backup/restore/integrity safeguards. Mutation-side dependency cleanup must be shared by direct deletion, bulk deletion, source deletion, reassignment and contact cascade; inspect every caller before editing. Plan/test both current v3 stores and older supported migrations, rollback after injected failure, and preserved unrelated rows. Do not silently recreate a corrupt store.

## Output contracts and request bounds

Use existing strict Pydantic validation and small immutable worker inputs. These are concrete fields/limits, not a requirement to create a generic framework.

| Contract | Required fields and limits |
|---|---|
| Evidence reference | Kind, exact contact/record/turn and/or memory revision/summary statement IDs, source generation, source/event date and original wording, current/historical/user-corrected/deleted-source state. Returned IDs must be a subset of supplied evidence. Quotes must exactly match eligible stored text. |
| Guidance update | Call/contact/generation/snapshot IDs; existing InterpretationUpdate plus `replies`, `remember`, `follow_up` arrays, each 0–3. Each candidate has stable ID, text ≤180 characters, low/medium/high confidence, 1–3 evidence references, and preference references if tailoring relies on them. Locally record supporting-time/dismissal identity. |
| Ask request | Query ≤500 characters; explicit one-contact scope (or all-contact discovery); reference date/zone; up to three prior user questions within a 1,000-character combined context cap; explicitly chosen event/evidence identities; generation and requested local/cloud mode. |
| Ask result | `answered`, `possibilities`, `clarification`, `no_match`, `conflict`, or `unavailable`; bounded answer ≤600 characters, confidence where an answer is asserted, up to three possibilities, up to four cited sources, scope, coverage/capability status, locally computed backend/cost. No numeric-confidence percentages. |
| Summary output | Four controlled sections, ≤16 statements/500 words total, each statement ≤280 characters with exact source-turn references and fact/advice distinction; bounded coverage and truncation/partial status. Proposal links are validated locally; output never contains an automatic approval action. |

The existing canonical F04 output permits at most three tone/cue items total even though its wire schema has per-category maxima. Preserve that accepted behavior; F06's three-candidate capacity applies to the new categories. Do not reopen F04 to fill more tone/cue cards.

Live requests retain F04's bounded recent transcript target (about 1,000 tokens, ≤16 turns/180 seconds), existing local vocal/visual observations, and at most four 180-character approved-memory excerpts within a 700-token memory allowance. Add compact source/preference IDs and F06 instructions, with a **3,000 estimated-input-token hard ceiling** and **1,200 output-token hard ceiling** for the combined F06 response. The old F04-only path keeps its 1,650/2,200 input and 400 output caps. Count serialized instructions/protocol and schema overhead conservatively; record actual usage, not just text length. Trim optional observations and low-ranked context before dropping evidence needed to substantiate a candidate; never cut dates/times into misleading fragments. If a response cannot fit, return fewer candidates rather than silently raise caps or retry for decoration.

Ask uses at most 12 locally fused candidates and four evidence excerpts, each ≤400 characters, before answer construction. Local candidate selection keeps current SQL lifecycle/contact filters; embeddings rank eligible records and do not turn the newest rows into an arbitrary recall cutoff. Cloud Ask: **2,500 estimated input / 600 output tokens**, one grounded answer only. Sensitive filtering occurs before serialization. Summary chunk: reuse ≤20 chronological turns and a **6,000 estimated input / 1,600 output-token ceiling**; consolidation reads bounded draft statements with ≤6,000 input/1,600 output and preserves source IDs. Split work explicitly when these bounds cannot hold. Existing extraction retains its ≤20 turns, ≤8 proposals, 6,000 input reservation and 2,400 output cap.

Use existing Luna `none`/`low` profiles as the initial cloud comparison for F06 generation; select the cheapest passing profile on the new fixed cases, reverify configured model availability/prices before paid evaluation, and record the winner. No new cloud provider. No automatic Terra escalation. Request schema failures or truncation fail closed; the combined path must preserve existing tone/cue abstention without unnecessarily suppressing a useful factual reply/clarifying question supported by words.

## Cost, scheduling, and resource limits

| Work | Limit and accounting |
|---|---|
| Assisted Call | $0.35 total, warning $0.15; paid live ceiling $0.27 preserves $0.08 for post-call work. These include in-flight conservative reservations and uncertain-billing failures. |
| In-call Ask / Suggest now / Terra | Share the same live ceiling; Ask also ≤$0.04 for the whole user-authorized answer, including any retry. No new sub-budget from contact changes or opening panels. |
| Outside-call cloud Ask | ≤$0.04 per answer and ≤$0.13 per app run, including retries/reservations. Local requests cost no API tokens. Restart begins a new allowance as approved. |
| Post-call automatic | Use remaining call funds, including unused live funds. Check the complete conservative job estimate against spend plus outstanding reservations before starting; reserve each actual request once immediately before sending. Serialize jobs per ledger and record rather than double-reserve an entire job and its child requests. |
| Explicit historical/long-call continuation | Visible estimate and conservative ceiling; $0.25 per authorized resumable run. No automatic continuation when exhausted. |
| F06 controlled paid evaluation | **$2.00 aggregate hard cap**, including failed attempts and correction reruns, within the master $30 development budget. Log content-free usage/model/profile/outcome. If insufficient, record pending work and request a concrete revised evaluation budget rather than silently proceeding. |

At **the inspected code's prices**, a maximum 3,000-input/1,200-output Luna request is $0.00204 with ordinary input or $0.00219 under the existing all-cache-write reservation. At the absolute 12-second cadence this is $0.612/$0.657 per hour, so $0.27 live funds cover roughly **25–26 minutes** if every request consumes its maximum. Typical spend may be lower; this is not a promise of an hour of cloud guidance. Demonstrate exhaustion and pending review honestly. Recalculate after price verification and measured output usage. The higher per-answer Ask ceilings are safety caps and do not require using expensive profiles.

F05's existing whole-extraction estimate covers one attempt per chunk. F06 must show that basis and reserve any retry separately under the same answer/run/call limits; an ambiguous timeout may consume its conservative reservation and leave remaining work pending. Do not promise the whole job will finish merely because its no-retry estimate fits. For a stopped call, no new live request may begin; all pre-Stop in-flight reservations remain charged while its single post-call job runs. This permits direct per-request accounting without a new hierarchy of nested budgets.

Use one bounded cloud work slot for call-funded tasks: explicit requests take priority over queued automatic work, but do not cancel already billed work to jump the queue. Keep only the newest pending automatic snapshot and newest pending Ask question; repeated manual clicks coalesce. Post-call jobs remain tied to their original ledger/record and pause between chunks when a new call needs resources. Never reset ledgers by reusing the current-call global for a previous record's worker.

Local retrieval/embedding work is bounded too: replace the per-snapshot thread-spawn path with one active local retrieval job and bounded latest-pending live/Ask slots at the shared seam. Do not preempt a running embedding batch unsafely. Pause bulk backfill during active calls/interactive Ask and shrink batches only if measured latency requires it. Run SQLite/embedding/cloud work outside Tk/capture/transcription threads. Keep the existing two-thread BGE setting as the baseline and record actual contention. No model download or optional LLM startup at call start.

F06 resource gates on the development Windows host:

- Local one-contact Ask warm p95 ≤500 ms, including candidate retrieval/citation validation; selected optional-LLM warm answer p95 ≤3 seconds. Busy/slow behavior remains visibly pending, not a false no-match.
- One-contact BGE/call retrieval should preserve F05's ≤250 ms p95 target on the comparable bounded workload, measured only as an affected F06 integration check later.
- With Ask + guidance + transcription/video, no dropped finalized turns, attribution corruption, unbounded queues, or capture failures; transcription p95 increases by ≤10% against the same F06 fixture without concurrent Ask work.
- Keep the Q16 optional-model limits: complete additional package ≤1 GB download and additional peak RAM ≤1.5 GB. Measure total installed application size and total peak memory, including runtime, tokenizer, caches and context/KV overhead, plus incremental values. An optional model passing on this 64 GiB host does not prove low-memory-PC support.
- For normal installation, measure cold-start time, warm CPU p50/p95, process working/private memory, total compressed download and expanded dependency/model size using the selected stack. Report CPU-only Ask behavior independently from the existing transcription GPU commitment. Record limits honestly; do not claim a new minimum-PC specification without its measurements.

## Bounded local-model experiment

Do not require the optional experiment to finish the core demo. First score structured/FTS answers and the existing BGE path on the same fixed F06 question set. If both meet acceptance, record **extra local LLM not needed** and stop. If meaningful paraphrase/follow-up failures remain, compare the explicit cloud enhancement first, as the user's preferred enhancement; optionally trial at most two small quantized local candidates in an isolated experiment, with no required runtime added to normal installation.

Freeze candidate versions/quantization/context/thread settings and the test set before timing. Use public primary model/runtime documentation for licensing, Windows packaging and model details. Record exact download manifests including shared versus additional dependencies, cold startup, peak memory, CPU latency, offline startup, cleanup and simultaneous-call effect. General model benchmarks or parameter counts cannot substitute for this record. A local candidate must improve usable grounded-answer rate by at least 10 percentage points or rescue at least two predeclared baseline failures, with no new safety failure and all Q16 limits passing. If not, reject it and retain local retrieval plus explicit cloud help. Limit investigation to one working day before trimming it.

## Implementation slices and dependencies

Only F06 may be active in implementation. Dates are scheduling targets, not evidence of completion. Keep September 21–22 for correction/release buffer and October 1 unchanged.

| Slice / target | Work and exit evidence |
|---|---|
| F06.1 — Planning / Sep 8 | Approve this contract, glossary/master reconciliation, permanent Trello column and source links. No implementation in the planning session. |
| F06.2 — Evidence and lifecycle / Sep 10 | Add summary/temporal migration, shared source preview and eligibility/dependency/exclusion handling. Prove correction Keep/Remove, deletion/rejection regeneration, legacy provenance failure, rollback and export. |
| F06.3 — Local Ask vertical slice / Sep 12 | Appointment answer and source links from Approved Memories, one-contact selection, clarification/follow-ups, temporary context and all-contact discovery. Fixed lexical/BGE comparison plus source/time/conflict checks. |
| F06.4 — Summary and review / Sep 14 | Bounded stop/historical summary jobs, existing extraction integration, manual approvals, correction/history/rejection/deletion and Approved Summary Ask retrieval. Full call→review→Ask fixture. |
| F06.5 — Live guidance / Sep 16 | Combined output, two-visible/three-cap categories, approved style, Suggest now/More/Dismiss, timers and stale invalidation. Demonstrated useful memory-assisted responses and unchanged audio-led lifecycle. |
| F06.6 — Budgets/cloud/resource integration / Sep 18 | Shared reservation/priority gates, explicit cloud Ask, long-call estimate/resume controls, concurrent CPU/queue behavior, selected Luna profile. No unbounded paid loops. |
| F06.7 — Optional local-model decision / by Sep 18 | Record baseline pass/skip or bounded comparison; no mandatory dependency. Can overlap only as a bounded experiment after local Ask exists, not as a second product feature. |
| F06.8 — Automated evaluation and demo preparation / Sep 19 | Fixed answer/summary/guidance quality, affected regressions, footprint/concurrency/spend report, basic/HeyGen limitations and reproducible manual-test script. Finish agent-run testing before handing the feature to the user. |
| F06.9 — Claude Opus 5 review before user testing / Sep 19 | Tool-disabled/read-only review of the complete F06 diff and agent-run evidence. Correct accepted findings, rerun affected checks and obtain a clean follow-up before asking the user to test. |
| F06.10 — User manual testing / Sep 20 | After F06.9 passes, give the user the prepared call→guidance→review→Ask script; record actual outcomes, useful-suggestion ratings and any explicit waivers. Fix reported issues and rerun affected checks. |
| F06.11 — Claude Opus 5 review after user testing / Sep 21 | Fresh tool-disabled/read-only review of the final complete diff, manual evidence and corrections, scoped to F06/direct integrations. The preliminary pass does not replace this gate. |
| F06.12 — Final corrections and reruns / Sep 22 | Correct accepted findings at shared roots, rerun affected checks, re-review until no unresolved material findings; document evidence-based rejections. Ask for targeted manual rechecks only when fixes affect already-tested user behavior. |
| F06.13 — Release / Sep 22 | Final audit, documentation/Trello reconciliation, commit/push, local/origin/GitHub main equality, final evidence links and completion status. |

## Acceptance and evaluation

Planning ran no F01–F05 tests. Implementation begins from their accepted baseline and tests F06's changes and directly affected integration surfaces. Do not redo unrelated completed live gates or a whole-program Claude review. Reuse the existing pytest/fake-client infrastructure; add a small fixed fixture set and focused tests, not a new framework. Run focused checks per slice; one complete offline regression suite before final review is appropriate for the shared store/UI/coordinator changes. After corrections rerun affected tests; repeat wider tests only for a changed shared surface or unresolved risk.

Create `docs/F06-VALIDATION.md` during implementation with exact commit, hardware/configuration, commands, frozen fixture IDs/expected outcomes, actual outputs, token/cost counters, raw timing samples, limitations and review verdicts. Use fictional data for committed fixtures and cloud comparisons.

### Fixed question set and factual safety

At least 40 predeclared cases spanning direct/paraphrased appointment time, venue, date, follow-up, historical correction and non-appointment questions; include at least 10 paraphrase/follow-up variants. Use separate expected facts/source IDs, not model self-grading or grading against its own summary. Record answerable, ambiguous, unavailable and adversarial strata separately.

- At least 90% correct useful answers on the answerable local baseline set and Recall@4 ≥0.90; report failures rather than counting safe abstention as a correct factual answer. Explicit cloud enhancement must rescue measured failures or improve clarity without reducing grounding. If local baseline misses the floor, fix the smallest query/source issue or perform the approved comparison; do not declare local search complete merely because cloud can answer.
- 100% of ambiguous/no-match/wrong-contact/rejected/deleted/unapproved/cloud-forbidden cases must avoid unsupported factual answers; unsupported high-confidence outputs: zero. Conflicting event selection, stale correction, fabricated citation and leakage are hard failures, independent of aggregate quality.
- 100% emitted citations resolve to the exact eligible contact/record/turn/revision represented; quotations match the named source type. Source date and event date are independently verified. Deliberately missing source and retained-memory provenance are explicitly tested.
- Required appointments: “Yaheli's dentist appointment is Tuesday at 3 PM”; source date distinct from event date; “what time was his visit?”; “and where?”; correction to 4 PM; Keep historical versus Remove; a second appointment with a different date; same-name other Yaheli; no time; ambiguous AM/PM; relative dates across midnight/week/year; explicit source zone and unknown zone.
- Required lifecycle tests: rejected proposal after summary approval, approval attempt after rejection, explicit summary-only restoration, memory deletion before/after summary generation/approval, regeneration from retained source, legacy tombstone without provenance, source/contact deletion, correction while cloud work runs, permission revocation, contact change/merge/reassignment, hidden third candidate and source-preview races. An unchanged-meaning edit must preserve a statement when the user chooses Keep.
- Ask temporary follow-ups: selected event maintained, changed scope resets it, ambiguous pronouns clarify, previous generated answers cannot become sources, last-three-question bound, panel-close clearing and spend retention, outside/in-call request attribution.

### Guidance, summary and integration quality

- At least 12 scripted live checkpoints across basic/F05 fictional scenarios plus appointment/style fixtures. User grades candidates useful/neutral/unhelpful. At least 80% of supported checkpoints have a useful reply and at least 80% of memory-relevant checkpoints have a useful Remember or Follow up item. Track irrelevant and repetitive suggestions separately; no harmful certainty or wrong-contact suggestion is acceptable. Strong fixtures demonstrate two visible candidates and a third via More; unsupported cases demonstrate fewer or zero.
- At least eight summary scenarios covering commitments, appointments, changed plans, small talk, missing/unclear speaker, conflicting statements, source exclusions, and a long multi-chunk call. Every summary factual statement must be supported or visibly user-corrected; zero invented agreements/feelings. Retain at least 90% of predeclared salient facts/commitments within the bounded summary. Drafts/advice never enter factual search before appropriate approval; extraction runs once and proposals remain independently reviewable.
- Timer tests at 12/24-second boundaries, silence expiry, ordinary paraphrase/dismissal suppression, fresh evidence, topic shift, material contradiction, manual refresh, Stop and lifecycle invalidation. No frame/token-driven update flood; one-in-flight/latest-pending bounds remain true under rapid speech/clicks.
- Cost tests use fake usage for exact equality/over-limit, cache-write reservation, uncertain billing, retries, queued jobs, new calls during post-call work, and simultaneous manual/automatic requests. A per-answer cap covers all attempts, and no request may reserve against only one of two applicable ceilings. More costs zero. Measure actual real-model p50/p95 latency and spend; generated live guidance p95 should appear within 12 seconds of eligible dispatch (excluding cadence/stable-display waits); timeout/failure stays bounded and visible.
- Resource samples: at least 100 warm local queries after recorded cold starts, with/without video/transcription, same fixture/clock workload; record median/p95/max, peak working/private RAM, download/install manifests, CPU settings, actual candidate corpus/vector counts and queue bounds. The old 100,000-revision fake-vector timing is context, not proof of large all-contact semantic or concurrent F06 performance.
- Migration/dependency/final diff checks: affected store migration/rollback/export/search tests, `pip check`, appropriate import/package checks if dependencies change, `git diff --check`, and secret/raw-media/generated-database/model/user-data audit. Preserve the four unrelated untracked CV PDFs.

### Demo scenarios and fixture limits

1. **Appointment outside a call:** approve Yaheli's 3 PM appointment with source; ask its time and venue; correct to 4 PM and Keep the original statement as history; verify current answer 4 PM and “what was originally said?” shows dated 3 PM with correction. Repeat with Remove.
2. **Identity and uncertainty:** two contacts named Yaheli and two appointments for one; disambiguate contact/event, demonstrate no match and explicit all-contact discovery without blended answers.
3. **Memory-assisted live exchange:** use approved relationship style and a relevant event/commitment; show two reply/Remember/follow-up candidates where supported, More, Dismiss and a topic change. Demonstrate appropriate clarification rather than an invented preference.
4. **Post-call review:** Stop, see draft + existing proposals, edit and approve independently, reject a proposal and verify linked summary exclusion, then Ask using only approved content after restart.
5. **Privacy and resource fallback:** sensitive local answer with cloud exclusion, source deletion with an explicitly retained memory, deletion during pending cloud work, unavailable BGE, exhausted live budget with local transcription continuing, and a long-call continuation estimate without automatic overspend.

Reuse the basic project-owned MP4 and its separate speaker stems for exact turns/timing/attribution; extend fictional F05 JSON for appointment and longitudinal approval cases. HeyGen is a secondary compression/face-motion/semantic-audio stress fixture: one animated narrator, static Alex, watermark and omitted opening line; it cannot prove two-sided speaker accuracy, exact basic dialogue or true emotion. Neither replaces user-rated usefulness or a consenting live demonstration. Do not regenerate these media merely for F06.

Run one short consenting fictional-data F06 call-to-review-to-Ask demo on a currently accepted call path, preferably WhatsApp or the tested dedicated-Chrome Meet configuration. Keep historical Zoom waivers and earlier F02/F03 waivers accurately labeled; the September 7 Meet evidence remains specific to its tested configuration. Test F06 UI/lifecycle integration with no face/visual loss and surviving audio, but do not reopen unrelated capture/transcription completion gates. Record a synthetic demo fallback; no real raw audio/video retention.

The user's manual session is gated by the clean preliminary Claude Opus 5 review and its corrections/reruns. Prepare the script and evidence first; do not make the user discover known agent-test or review failures. Record the user's actual response instead of inferring a pass from silence. A fresh post-manual Claude Opus 5 review remains mandatory even if the user reports no defect.

## Trimming order

1. Additional local LLM experiment/install option; explicit cloud enhancement is preferred and existing local search remains required.
2. Cosmetic polish, animations, rich summary layout and extra copy/export conveniences.
3. Semantic all-contact expansion and cross-contact synthesis (already excluded); keep explicit labeled FTS discovery and one-contact semantic Ask.
4. Rich timezone conversion and advanced query language; keep original wording, safe explicit times, clear dates and clarification.
5. Extra historical batch convenience and extended summary history browsing; keep one-record generation, source preview, necessary correction links and all deletion cleanup.

Never trim two-visible/three-cap support, basic appointment/follow-up usefulness, approved-only evidence, manual review, contact confirmation/isolation, uncertainty, source accuracy, Keep/Remove correction choice, rejection/deletion regeneration safety, bounded spend/resources, stable updates, affected testing or the Claude/release gate. If a core gate cannot pass by September 22, report it and propose a concrete reduction; do not silently relabel incomplete work as accepted.

## Claude review and release gate

1. Verify local main, origin/main and GitHub main before implementation; preserve unrelated work. Resolve unexpected pointer differences before baselining the diff. Do not restart F01–F05 completion testing.
2. Review F06 and its direct integration surfaces only: contact/source/revision eligibility, summary approval/dependency/suppression, precise temporal/source answers, resource and budget reservations, scheduler races, UI accessibility/nonblocking behavior, migrations/export and affected tests.
3. **Before user testing:** finish agent-run automated, replay, controlled-model and affected integration checks. Provide **Claude Opus 5** (`claude-opus-5`, the user-requested newest Opus 5), tool-disabled/read-only, the complete F06 diff, approved plan, validation evidence, fixtures/provenance and known limitations. Verify and record the actual reviewer model identifier; do not silently use an older Opus, Sonnet or another model. If unavailable, report the blocked review rather than claiming a substitute pass. A subagent factual check is not this gate.
4. Correct every accepted preliminary finding at the shared root, record justified rejections with evidence, rerun affected checks and obtain a clean correction review before asking the user to test. Then provide the prepared test script, record the user's manual results, fix accepted user-reported issues and rerun their affected checks. Do not send private call content to reviewers.
5. **After user testing:** obtain a fresh tool-disabled/read-only **Claude Opus 5** review of the final complete F06 diff, automated evidence, actual user-test outcomes, limitations and corrections. The earlier clean review cannot substitute for this one. Fix accepted findings, rerun affected checks and request follow-up review until no unresolved material finding remains. If a correction changes manually tested behavior, obtain its targeted user recheck and include that evidence in closing review.
6. Audit final changes for secrets, real user text, raw media, generated model/DB artifacts, unrelated edits, accidental scope growth and stale documentation. Update plan/README/validation/Trello evidence consistently.
7. Commit and push the reviewed F06 result. Verify exact local main = origin/main = GitHub main SHA through independent local/ref/API reads. If the implementation used a branch, finish the agreed integration before claiming main equality. Record code/evidence commit pointers without inventing a self-referential commit hash inside its own contents.
8. Mark implementation cards and roadmap complete only after evidence, both Claude gates, user testing, corrections and release checks pass. A planning card may complete earlier; the F06 feature remains not started until its separate implementation session.

## Trello finalization

Board: https://trello.com/b/XeJEDPBa/conversation-copilot-final-project. Permanent column **F06 — Live Guidance, Ask Memory, and Post-call Review** was created on 2026-09-08 with list ID `ari:cloud:trello::list/workspace/6a78831e3dacf14c9ce15a62/6a9f271654b1cdf3fe6023a4`. Existing open/archived board cards were inspected first; the original roadmap card is retained in Feature Backlog and no duplicate roadmap was created. Target dates use Asia/Jerusalem end of day. Only the planning card completes in this session; all implementation, test, review and release cards remain not started.

| Card | Link |
|---|---|
| F06.1 — Planning | [Open card](https://trello.com/c/9Y2YX01Q/92-f061-planning) |
| F06.2 — Evidence and lifecycle | [Open card](https://trello.com/c/cJ93EeyM/93-f062-evidence-and-lifecycle) |
| F06.3 — Local Ask vertical slice | [Open card](https://trello.com/c/0WBr1p50/94-f063-local-ask-vertical-slice) |
| F06.4 — Summary and review | [Open card](https://trello.com/c/gMFgcb3S/95-f064-summary-and-review) |
| F06.5 — Live guidance | [Open card](https://trello.com/c/o1RyqPH4/96-f065-live-guidance) |
| F06.6 — Budgets, cloud and resource integration | [Open card](https://trello.com/c/UVoUJ9wc/97-f066-budgets-cloud-and-resource-integration) |
| F06.7 — Optional local-model decision | [Open card](https://trello.com/c/GmPFKFiX/98-f067-optional-local-model-decision) |
| F06.8 — Automated evaluation and demo preparation | [Open card](https://trello.com/c/cCfMPkCO/99-f068-automated-evaluation-and-demo-preparation) |
| F06.9 — Claude Opus 5 review before user testing | [Open card](https://trello.com/c/SwYsoSvk/100-f069-claude-opus-5-review-before-user-testing) |
| F06.10 — User manual testing | [Open card](https://trello.com/c/TgCscW6t/101-f0610-user-manual-testing) |
| F06.11 — Claude Opus 5 review after user testing | [Open card](https://trello.com/c/4i5ds49x/102-f0611-claude-opus-5-review-after-user-testing) |
| F06.12 — Final corrections and reruns | [Open card](https://trello.com/c/yc9OLpO9/103-f0612-final-corrections-and-reruns) |
| F06.13 — Release | [Open card](https://trello.com/c/cwNd42SP/104-f0613-release) |

Repository plan: https://github.com/simon-levy01/conversation-assistant/blob/main/plans/F06-live-guidance-ask-memory-post-call-review.md

## Separate implementation-session prompt

```text
Implement F06 — Live Guidance, Ask Memory, and Post-call Review for Conversation Copilot.
Workspace: C:\Users\Banan\Desktop\Programming\Final project call helper
Read PLAN.md, CONTEXT.md, plans/F06-live-guidance-ask-memory-post-call-review.md,
docs/F05-VALIDATION.md, relevant code, and the permanent F06 Trello column first.
Board: https://trello.com/b/XeJEDPBa/conversation-copilot-final-project
Roadmap: https://trello.com/c/ljon1I03/26-f06-live-guidance-and-post-call-review-target-sep-22

Follow the approved F06 plan; it is the implementation agreement. F01–F05 are
complete and accepted as tested. Do not reopen their completion gates or rerun
unrelated old live tests. Test F06 changes and directly affected integration surfaces.
F06 target September 22, 2026; Windows project deadline October 1. Preserve platform
commitments, prior waivers and the specific September 7 Meet evidence. F09 remains later.

Do not overengineer. Understand the real flow and all callers, then reuse existing
code, standard-library/native capabilities and installed dependencies. Implement the
smallest cohesive change that satisfies the plan. No speculative abstractions,
duplicate extraction/retrieval pipelines, new frameworks or future-feature scaffolding.
Fix root causes. Never simplify away privacy, validation, accessibility or requested tests.

Deliver two visible candidates each for Reply, Remember and Follow up, up to three
through zero-cost More; automatic meaningful updates at least 12 seconds apart,
Suggest now, Dismiss, 12-second stability and 24-second unsupported expiry, with
immediate invalidation of misleading or invalid evidence. Reuse approved contact style.
No automatic sending, invented preferences, raw-media retention or certainty claims.

Implement local-first Ask over Approved Memories and Approved Summaries, short temporary
follow-ups, independent in-call Ask contact scope, explicit all-contact discovery,
appointment/time/venue answers with exact source/date, safe ambiguity/conflict handling,
and per-request Use cloud help. Existing BGE/FTS/source answers are the default;
cloud is the preferred enhancement. Any additional local LLM is optional, evidence-gated
and excluded from normal installation. Respect all plan resource and request limits.

Generate bounded local summary drafts after Stop and for one explicitly selected
historical record. Integrate existing extraction/proposal review without duplicating it.
Require separate manual summary and memory approval. Rejection excludes linked summary
statements. On memory correction prompt Keep/Remove; kept contrary statements are dated
history linked to the correction, never silently current truth. Deletion must scrub
dependent summary content/indexes and prevent regeneration from retained transcript text.
Handle legacy missing deletion provenance conservatively. Preserve F05 source deletion,
reassignment, merge, sensitivity, revisions, migration integrity and stale-result controls.

Budget: $0.35 per call, $0.08 reserved for post-call work, $0.27 paid-live ceiling,
$0.15 warning. Cloud Ask ≤$0.04 per answer and ≤$0.13 outside-call per app run;
in-call Ask shares live budget. Long/historical continuation needs an estimate and
explicit action, ≤$0.25 per bounded resumable run. F06 paid evaluation ≤$2 aggregate.
Reservations, retries and uncertain billing count. Reverify actual prices before spending.

Implement the plan's slices; keep Trello synchronized. Use fictional fixtures/fake clients
first, basic and HeyGen media only within documented limits, then controlled real-model
checks. Record evidence in docs/F06-VALIDATION.md. Preserve unrelated CV PDFs and user
changes. Verify repository pointers before work.

Use the general F05 workflow with BOTH required Claude gates:
1. Complete agent-run testing and affected integration checks. BEFORE asking me to test,
   obtain tool-disabled/read-only Claude Opus 5 QA/code review of the full F06 diff,
   plan and evidence. Use claude-opus-5 (the newest Opus 5 requested here), verify and
   record the actual model, and never silently substitute an older Opus or Sonnet.
   Fix accepted findings, rerun affected tests and obtain a clean correction review.
2. Give me a concrete manual-test script. Wait for and record my actual results;
   fix reported defects and rerun affected checks. Do not treat silence as a pass.
3. AFTER my testing, get a fresh Claude Opus 5 review of the final complete diff,
   test evidence, manual outcomes and corrections. Keep both reviews focused on F06
   and its direct integration surfaces. Fix accepted findings and repeat affected
   tests/correction review until no material finding remains. Obtain targeted manual
   rechecks if a fix changes behavior I already tested. Document rejected findings.
4. Audit the final diff/privacy/docs, commit and push the reviewed implementation,
   verify local main = origin/main = GitHub main, and record the exact SHA on Trello.
   Only then mark F06 complete. Do not implement F07–F09 or silently broaden scope.
```

## Planning completion record

The user approved the full contract on **2026-09-08** and explicitly reaffirmed minimal engineering plus Claude Opus 5 review before and after their manual testing. Interview Q1–Q18 decisions are recorded above. PLAN.md, CONTEXT.md and this plan form the documentation-only planning release. The permanent column/cards and repository links are listed above; exact final commit/push and local/origin/GitHub pointer evidence is recorded on the F06.1 planning card after publication, avoiding a self-referential commit hash in this file. No F06 implementation or accepted-feature tests were run in this planning session. The four unrelated CV PDFs remain excluded.
