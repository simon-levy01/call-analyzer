# F05 — Contact Memory and Personalization

**Status:** Complete — implementation, evaluation, consenting WhatsApp call, clean review, audit, and release gates passed
**Prepared and approved:** 2026-08-27
**Roadmap target:** 2026-09-16
**Repository baseline:** local main, origin/main, and GitHub main verified at 63c8c32cc850c7042e615734ee4fd1a9558eb4c3 before planning

## Outcome

F05 gives each explicitly selected contact a durable, local, reviewable memory. During an Assisted Call, the user can select or create the contact before the call or change that association while the call is running. Only then may approved memories for that contact enrich F04 interpretation.

After a call stops, or after the user explicitly analyzes an imported text conversation, the system proposes small atomic memories for review. Nothing inferred by AI becomes approved memory without the user. Approved memories remain traceable to their source, can be corrected without rewriting history, can be superseded, rejected, reopened, exported, or deleted, and never leak across contacts.

The minimum implementation is deliberately boring: one local SQLite database, the Python standard-library SQLite driver, existing OpenAI/Pydantic/cost-ledger patterns, and small additions at the current final-turn and F04 snapshot seams. Do not introduce a memory framework, vector database, graph database, ORM, event bus, provider hierarchy, plugin system, or speculative F06 scaffolding unless a measured gate in this plan proves the direct implementation insufficient.

## Approved product decisions

1. F05 owns contacts, aliases, contact association, persisted attributed text conversation records, memory proposals, approval and correction, provenance, lifecycle, retrieval, relationship-specific memories, and bounded memory enrichment of F04.
2. F06 owns live reply suggestions, reminders, follow-up questions, talking points, summaries, and the polished post-call presentation. F05 stores the approved facts those features will later use; it does not implement dormant providers or fake F06 surfaces.
3. Persist normalized, attributed text from confirmed text imports and Assisted Calls. Do not persist raw audio, raw video, frames, landmarks, blendshapes, or PCM.
4. AI-extracted items enter a proposal queue. A memory typed or corrected by the user becomes approved immediately.
5. Contacts have stable IDs, an editable display name, an optional disambiguator such as a last name, and multiple aliases or nicknames. Exact display-name uniqueness is not required.
6. Confirming an observed source name may add a removable, source-specific alias. An alias collision may point at several contacts; it must show candidates and never silently choose.
7. The user can select or create a contact before or during a call. Before confirmation, there is no contact-memory retrieval and no memory extraction.
8. Changing the contact during a one-to-one call reassigns the entire call. It invalidates stale memory context, pending interpretations, and pending proposals, then retrieves only for the corrected contact.
9. If a call ends unassigned, prompt the user to select or create a contact. Dismissing the prompt keeps it in Unassigned Conversations. It remains unavailable for retrieval and extraction until assigned.
10. Face recognition is not F05. The master plan records it as a separate post-MVP, opt-in biometric feature requiring consent, several reference samples, deletion controls, measured false matches and misses, and confirmation of every suggested identity. One screenshot is not sufficient evidence.
11. Memories are atomic and may have explicit connections. Relationship and communication style are reviewable, evidence-backed memory items rather than an opaque generated profile.
12. Near duplicates are never automatically suppressed or merged. Every possible duplicate reaches review, is labeled in text, shows the existing or peer item it resembles, and may additionally use color without relying on color alone.
13. Duplicate detection runs against approved memories and within the new proposal batch. Similar-looking facts with different values, such as two phone numbers, remain separate.
14. Correcting an approved memory creates a new immutable approved revision and supersedes the old revision. Retrieval uses only the current approved revision.
15. Deleting a memory erases the content, evidence, search row, and optional embedding for its full revision chain in one transaction. A content-free memory ID and deletion timestamp remain as a tombstone. Deleting the contact removes even those tombstones.
16. Deleting a Conversation Record first previews every derived memory. All are selected for deletion by default; the user can explicitly keep individual memories. Kept memories lose the deleted source text and retain only minimal provenance: source kind, approximate date, and that the source was deleted.
17. Rejected proposals remain local review history, never participate in retrieval, and can be reopened or permanently deleted. Contact deletion erases them.
18. Memories have normal or sensitive sensitivity. Sensitive memories stay local by default and need explicit, per-memory permission before any excerpt can be sent to a cloud model. The permission is reversible.
19. Confidence remains low, medium, or high after approval. User-authored memories default to high but are editable. A low-confidence memory alone cannot produce a high-confidence interpretation.
20. Extraction runs once after a call stops when its contact is confirmed and budget remains. An import runs only after the user confirms the preview and clicks Analyze after seeing the estimate.
21. Failed or budget-blocked analysis keeps the Conversation Record and offers manual retry. Large imports are processed in bounded chronological chunks with progress and resumability.
22. Date phrases preserve their original wording. The system stores a normalized date or time only when it can do so safely. It defaults to the Windows time zone, shows the assumed zone at import, and allows correction.
23. Phrases such as 7 my time may use approved contact-zone or current-location context when the wording is clear. If the reference remains ambiguous, keep the original phrase and mark time unresolved or low-confidence; do not guess.
24. Memories do not expire because they are old. Age may affect ranking. Changed facts become superseded only through review.
25. Retrieval is contact-first. The default search stays within one contact; all-contact search is an explicit action. Filters cover memory type, lifecycle, sensitivity, and date.
26. Ambiguous retrieval shows low-confidence possibilities, asks for clarification when appropriate, or abstains. It never turns a close score into a confident fact.
27. The initial controlled memory types are person, preference, event/date, commitment, follow-up, recurring topic, shared joke/reference, relationship preference, communication style, and other. The user may correct a type. Custom type systems are post-project work.
28. A contact merge previews all effects, selects one survivor, and transactionally moves aliases, records, proposals, memories, and revision history. Similar or contradictory memories stay separate and are marked for review.
29. Reassigning an old Conversation Record previews its derived memories. They are selected for deletion by default; explicitly chosen items may be reviewed and moved. The record is then eligible for re-extraction under the corrected contact.
30. Export defaults to one contact, with an explicit all-data option. Versioned JSON contains contacts, aliases, records, proposals, memory revisions and connections, lifecycle, provenance, and cloud permissions. It omits raw media, FTS tables, embeddings, and other regenerable internals.

## Verified starting point

- F01 through F04 are complete on the accepted baseline. The complete automated suite passed 126 tests before this planning-only change.
- There is no current database, contact-memory store, embedding model, or memory framework dependency.
- F04 receives finalized ConversationTurn values at the final-draft handoff in the combined application, builds an InterpretationSnapshot, and submits it through the existing coordinator.
- F04 already enforces strict Pydantic output, stateless OpenAI Responses calls, store=false, a usage ledger, one request in flight, a latest-pending snapshot, stale-result rejection, a 12-second automatic cadence, and a 12-second stable-card rule.
- The current F04 compact request uses t, v, and x fields and deliberately has no memory placeholder. F05 must add its real bounded memory input only after local retrieval succeeds.
- The F04 cautious local policy can return before a cloud call. The memory-aware path must be deliberate so a relevant approved memory is not accidentally ignored by a memory-free early return.
- The runtime currently uses window/source presentation as a contact-like label. That is not identity confirmation and must not become a memory key.
- The existing POC proves that local SQLite storage and recent-conversation context are viable, but its monolithic layout, exact-name identity, free-text JSON, automatic approval behavior, and missing provenance/deletion/retrieval rules are not reusable contracts.
- The Python environment provides SQLite 3.49.1 with FTS5. This is the default search foundation.

## Existing contracts that remain true

### F02 and F03

- Capture remains tied to the explicitly selected source and selected remote face.
- Raw frames, raw audio, PCM, landmarks, and blendshape history are not persisted or uploaded.
- Physical microphone and playback sources keep their existing user/remote attribution.
- Only ordered finalized turns enter persisted call records or interpretation.
- Visual loss never silently switches identity and does not stop a healthy audio/transcription session.
- F05 does not change English-only production transcription or the F03 ordering, bounded-queue, teardown, and source-priority rules.

### F04

- Tone and cue outputs remain cautious hypotheses, not declarations of true emotion or intention.
- Existing modality evidence, abstention, cadence, stale-result, duplicate-result, and card-stability behavior remains intact.
- Memory-free requests keep the current 1,650 estimated-input-token hard ceiling.
- Memory-aware requests may add up to 700 estimated tokens for at most four short approved excerpts, giving a 2,200-token hard ceiling. The higher ceiling is activated only when memory context survives trimming; the memory-free target stays 1,500, its hard ceiling stays 1,650, the transcript target stays 1,000, and output stays capped at 400.
- Manual Terra checks use the latest eligible snapshot and the same selected contact generation.
- A cloud failure cannot stop local capture or transcription.

## Scope

### Included

- Local contact creation, editing, aliases, disambiguation, merge, selection, and reassignment.
- Call-time select/create/change controls and the stop-time assignment prompt.
- Local attributed-text Conversation Records and Unassigned Conversations.
- Confirmed text import with preview, source metadata, time-zone assumption, and explicit Analyze action.
- One bounded post-call or import Proposal Batch.
- Atomic proposal review, user-authored memory, approval, rejection, reopen, correction, supersession, connection, deletion, and provenance.
- Potential-duplicate grouping across approved memories and batch peers.
- Contact-first search and retrieval using SQLite metadata/date filters plus FTS5.
- A measured semantic-search gate, and a tightly bounded cloud rerank fallback only when local evidence cannot separate candidates.
- Memory-aware F04 interpretation with immediate invalidation on identity or memory changes.
- Versioned JSON export, schema migrations, migration backup, and integrity checks.
- Deterministic tests, controlled model evaluation, large synthetic-store tests, and one consenting fictional-data WhatsApp manual gate.

### Excluded

- Face recognition, biometric enrollment, or saving a face screenshot for identity matching.
- Reply generation, reminders, follow-up questions, talking points, summaries, or polished F06 review flows.
- Automatic approval, automatic duplicate merging, automatic contradiction resolution, or hidden memory deletion.
- Raw-media persistence or egress.
- A general knowledge graph, arbitrary custom taxonomy, cross-user synchronization, cloud backup, multi-account permissions, or shared/team contacts.
- SQLCipher or application-level disk encryption. The local Windows account/device boundary is the accepted MVP protection.
- A vector database, graph database, ORM, event bus, dependency-injection container, plugin framework, generalized repository layer, or one-implementation interfaces.
- A framework adapter kept for later. If a framework loses the gate, remove the experiment and keep no abstraction for it.

## Domain and lifecycle contract

The names below may be adjusted to match the repository, but their semantics are fixed.

### Contact identity

- A Contact has a stable opaque ID, editable display name, optional disambiguator, timestamps, and optional reviewed time-zone context.
- A Contact Alias has its own stable ID, contact ID, displayed spelling, normalized lookup form, origin such as user nickname or observed source name, and removable state.
- Alias normalization helps lookup; it is not identity. The same normalized alias may exist on more than one contact.
- A Contact Association links one Conversation Record and current Assisted Call generation to zero or one confirmed Contact.

### Conversation records

- A Conversation Record is one imported or captured attributed-text conversation with source kind, local/UTC timing metadata, optional contact ID, and analysis state.
- Conversation turns preserve chronological sequence, user/contact attribution, finalized text, and available start/end times. They do not hold audio or video.
- An Unassigned Conversation is a Conversation Record with no confirmed contact. It cannot be searched as contact history, extracted, retrieved, or sent as memory context.

### Memory proposals

- A Proposal Batch belongs to one assigned Conversation Record and records model/profile, prompt/schema version, status, token usage, cost, and retry/failure metadata.
- A Memory Proposal is one atomic candidate with proposed content, controlled type, confidence, sensitivity, a `likely_generic` review flag, normalized/original date information, evidence references, and pending, rejected, or approved review state.
- Approval creates an Approved Memory and links the proposal to it. Rejection never changes retrieval because proposals are never retrieval candidates.

### Approved memory

- A Memory is the stable logical identity and lifecycle tombstone.
- A Memory Revision is immutable reviewed content. It carries type, confidence, sensitivity, cloud permission, date fields, author origin, approval time, and predecessor.
- Exactly one non-deleted revision is current for an active memory. A correction inserts the replacement and marks the former revision superseded in the same transaction.
- A Memory Source links the approved revision to its Conversation Record and, when useful, specific turn sequence numbers. Evidence shown to the user comes from these references.
- A Memory Connection links two approved logical memories with a small controlled relation such as related. Supersession is represented by revision lineage, not a general graph edge.
- Potential Duplicate is a review flag, not a lifecycle state. It may compare proposal-to-proposal or proposal-to-current-memory and includes a similarity reason or score for sorting only.

### Retrieval eligibility

A memory excerpt is eligible only when all are true:

1. its Contact ID exactly matches the Selected Contact;
2. the logical memory is active and the revision is current;
3. it is approved, not proposed or rejected;
4. it is not deleted or superseded;
5. the query filters permit its type, sensitivity, and date;
6. cloud use, if any, is allowed by the memory's sensitivity and per-memory permission; and
7. its source and evidence references have not been invalidated in a way that requires removal.

## Smallest reliable storage design

Use one SQLite database below the existing LocalAppData ConversationCopilot directory. Open it through one small storage module using Python's sqlite3 package. Enable foreign keys on every connection. Use WAL only if the existing UI/background access pattern measurably needs concurrent readers; otherwise keep the default journal mode. Keep writes short and transactional.

The minimal normalized schema should cover these concepts:

| Table | Purpose and essential constraints |
|---|---|
| contacts | Stable contact ID, display name, optional disambiguator/time-zone context, timestamps |
| contact_aliases | Contact FK, spelling, normalized lookup, origin; unique only within the same contact/origin where appropriate |
| conversation_records | Nullable contact FK, source kind, timing/time-zone metadata, import/call status, analysis status |
| conversation_turns | Record FK, increasing sequence, speaker role, finalized text, optional relative/UTC bounds |
| proposal_batches | Record FK, bounded-run state, model/schema version, usage/cost/failure fields |
| memory_proposals | Batch FK, atomic proposed fields, `likely_generic` review flag, review state, evidence/date data, approved-memory FK when accepted |
| memories | Stable logical ID, contact FK, current-revision FK, deleted_at tombstone |
| memory_revisions | Memory FK, predecessor FK, immutable approved fields, superseded_at, content nullable only after secure deletion |
| memory_sources | Revision FK, record FK nullable after kept-source deletion, turn references, minimal deleted-source provenance |
| memory_connections | Two logical memory FKs, controlled relation, uniqueness preventing duplicate direction where relevant |
| potential_duplicates | Proposal pair or proposal/current-revision comparison, group/reason/score, review display state |
| memory_search | FTS5 external-content or synchronized index for current eligible memory text only |
| memory_embeddings | Optional revision/model/vector rows, created only if the semantic-search gate passes |

Prefer database constraints and foreign keys over duplicated application checks. Keep a few direct query functions organized around actual use cases; do not wrap SQLite in an ORM or a generic repository/service stack.

Do not store every derived display field. Display labels, current lifecycle, search snippets, and duplicate grouping can be computed from the normalized rows. Persist only what is required for correctness, review history, budgets, migration, or resumability.

### Transaction boundaries

Each of these is one transaction:

- create or edit a contact and its explicit alias changes;
- associate or reassign a Conversation Record;
- approve or reject selected proposals;
- create a corrected revision and supersede the previous one;
- merge contacts;
- delete a source and apply the user's derived-memory choices;
- delete a memory revision chain and scrub its FTS/embedding/source content;
- delete a contact and all related content/tombstones;
- apply one schema migration step.

If any step fails, the prior durable state remains usable and no partial identity or lifecycle change becomes visible.

## Schema migration and recovery

- Track sequential schema versions with SQLite user_version and explicit migration functions.
- Before migrating, create a temporary local backup with SQLite's backup API in the same application data area, after confirming the resolved target paths.
- Run the migration transactionally, then reopen and verify foreign-key checks, expected user_version, essential tables, and a small read/write smoke check.
- On success, delete the temporary migration backup only after verification.
- On failure, retain the backup, leave the original unchanged or restore it, and prevent a writable memory session until the user retries or restores. Capture/transcription may continue without memory if safe.
- Never silently recreate an empty database after corruption or migration failure.
- Add no migration framework unless the small explicit sequence becomes materially difficult to maintain.

## Contact selection, association, and merge

### Before and during a call

- The Assisted Call UI has one compact Selected Contact control with search, recent matches, Create Contact, Change, and Clear.
- Matching may use display name, disambiguator, and aliases. Ambiguous matches show all candidates with enough identifying text.
- Selection is always explicit. A source title or participant label may be offered as an alias suggestion but never confirms identity by itself.
- Once confirmed, retrieval starts for the current call context. Previously finalized turns in that same one-to-one call may be used as the current retrieval query, but they are not reinterpreted as another contact's history.
- Creating a contact during the call immediately associates the whole current record and permits retrieval from any approved memories the new contact already has, if any.

### Correction during a call

- Increment a contact/memory generation.
- Cancel or ignore any in-flight result from the old generation.
- Clear pending snapshots, cached retrieved memories, and visible memory-derived guidance immediately.
- Reassign the complete current record to the new contact in one transaction.
- Retrieve again using only the new contact.
- Any unapproved proposal batch produced under the wrong contact is invalidated and must not be transferred silently.

### Stop-time prompt

When Stop completes, if no contact is confirmed:

- prompt to select or create a contact;
- explain that assignment enables memory analysis;
- if dismissed, save the normalized text record under Unassigned Conversations;
- do not run extraction;
- allow later assignment followed by explicit analysis.

### Merge

The merge preview names the survivor and counts aliases, records, proposal history, active memories, revisions, rejected proposals, and potential conflicts. The transaction moves ownership, deduplicates only identical redundant aliases, preserves record/revision IDs, and regenerates affected search rows. Similar or contradictory approved memories remain distinct and are flagged; no content is silently discarded.

## Import and Conversation Record flow

The import path accepts attributed text only. Reuse the existing speaker vocabulary and strict parsing style where possible.

1. Parse and preview participants, speaker mapping, chronology, source kind, time-zone assumption, and approximate size.
2. Require the user to map one participant to self and one to a selected or newly created contact.
3. Show validation errors without creating a partial record.
4. Persist the confirmed normalized record and turns locally.
5. Estimate the bounded analysis request count and maximum cost.
6. Run only after the user clicks Analyze.
7. For a large record, process chronological bounded chunks with stored progress. Retry continues from the last completed chunk rather than resending the entire history.

Never submit a full large history in one request. Never accept prompt-like transcript text as instructions.

## Extraction and proposal consolidation

Reuse the official OpenAI SDK, strict Pydantic parsing, stateless Responses calls, store=false, injectable fake-model pattern, and current usage ledger. Compare Luna reasoning none and low on the fixed extraction set; choose the cheapest passing profile.

The extraction prompt and schema must:

- treat conversation text as untrusted evidence;
- produce zero or more atomic proposals, not a profile or summary;
- restrict items to durable, future-useful information about the contact or this relationship;
- preserve direct facts separately when they can change independently;
- attach exact turn references and original date wording;
- mark confidence and sensitivity conservatively;
- avoid unsupported emotion, intention, diagnosis, or certainty;
- exclude non-contact-specific small talk and broad observations that would be true of nearly everyone;
- retain concrete contact-specific one-off or routine facts as proposals when otherwise supported, mark them `likely_generic`, and group them for easy rejection rather than silently suppressing them;
- exclude generic advice such as everyone sometimes avoids naming painful subjects;
- distinguish two similar values instead of collapsing them; and
- permit an empty result when nothing is worth remembering.

Useful proposal examples include a named person, stable preference, dated event, explicit commitment, follow-up obligation, recurring topic, shared reference, or observed communication preference supported by repeated/direct evidence.

### Bounded consolidation

For multi-chunk imports, consolidate proposals rather than resending raw history:

- keep source turn references;
- compare atomic fields deterministically first;
- use the same bounded extraction model only when wording cannot be reconciled locally;
- never auto-approve, auto-merge, or auto-delete;
- store one final reviewable Proposal Batch; and
- keep chunk progress/failure metadata for retry without exposing implementation clutter in the main review UI.

One post-call run shares the Assisted Call budget. If it cannot run, retain the assigned record in analysis-pending state and offer retry.

## Duplicate and contradiction review

Use simple layered detection:

1. exact normalized content and controlled-value comparisons;
2. FTS5 lexical candidate search within the same contact and current proposal batch;
3. optional embedding similarity only if the semantic gate passes; and
4. no cloud call solely to decorate duplicate groups unless fixed evaluation proves it necessary within the existing budget.

Potential duplicates are grouped for display but remain individually checkable. Each flag names the compared item, whether it is already approved or in this batch, and why it was flagged. Use a text badge such as Possible duplicate; optional group colors are secondary.

Different values, dates, people, phone numbers, addresses, or commitments do not become duplicates merely because their sentence templates are similar. Contradictions are displayed side by side and resolved through approval, correction, or later supersession.

## Retrieval design

### Framework gate

Before writing retrieval, make a short evidence table comparing:

- direct SQLite plus FTS5 and BM25: https://www.sqlite.org/fts5.html
- Mem0 open-source configuration: https://docs.mem0.ai/open-source/configuration
- Graphiti quick start: https://help.getzep.com/graphiti/getting-started/quick-start

Select direct SQLite unless another choice materially beats it on every required dimension: Windows setup, local-first privacy, exact lifecycle/deletion control, deterministic contact isolation, current dependency footprint, bounded cost, migration clarity, testability, and implementation size. Do not add an adapter around the winner. The expected selection is SQLite/FTS5.

### Local candidate generation

For each retrieval:

1. require a confirmed Selected Contact;
2. filter by exact contact ID and eligible lifecycle in SQL before ranking;
3. apply sensitivity/cloud and explicit type/date filters;
4. use FTS5 BM25 for lexical matches;
5. include narrow metadata/date candidates when the query contains a person, date, commitment, or time reference;
6. if the semantic gate passes, add local embedding candidates;
7. fuse independent ranked lists with a small deterministic rank-fusion calculation;
8. optionally expand at most one hop through explicit related-memory connections;
9. keep a small local candidate pool, recommended maximum 12; and
10. return at most four short excerpts to F04.

Ranking may use modest recency and confidence signals, but relevance dominates. For a purely indirect event reference, one uniquely newest normalized event date may supply a single cautious possibility; older events require an explicit lexical or date reference. Equal or missing dates remain ambiguous. Low confidence is never upgraded by ranking. Date age changes ordering, not lifecycle.

### Semantic-search gate

Benchmark FastEmbed with BAAI/bge-small-en-v1.5 on the target Windows CPU:

- https://github.com/qdrant/fastembed
- https://huggingface.co/BAAI/bge-small-en-v1.5

Add it only if it materially improves the fixed indirect-reference set over FTS5/metadata while meeting installation reliability, warm latency, storage, and offline-startup requirements. The model is an explicit setup/download step and never downloads at call start. If selected, store vectors in SQLite and score with existing NumPy; do not add a vector database.

If the model is missing, corrupt, or unavailable, visibly use reduced indirect-recall mode: metadata/date/FTS5 plus the bounded fallback below. Direct search and contact isolation must still work.

### Bounded cloud rerank

Use a cloud rerank only when the local candidates are close enough that local evidence cannot safely separate them:

- send the recent bounded conversation context and at most five short, cloud-permitted candidate excerpts;
- never send full contact history;
- reuse strict structured output and the current usage ledger;
- require select, possibilities, or abstain semantics with evidence;
- do not send sensitive memories without their explicit permission; and
- if unavailable, over budget, or still ambiguous, show possibilities or abstain.

The cloud model cannot make an ineligible memory eligible and cannot search another contact.

## F04 integration

Add memory only at the real bounded-snapshot seam; do not create a placeholder provider.

- Introduce one strict compact Retrieved Memory input carrying stable memory/revision identity, short excerpt, controlled type, confidence, sensitivity-safe status, and relevance evidence needed for traceability.
- Add a compact memory field to the F04 request only when at least one eligible memory was retrieved.
- Update the F04 prompt so memory is context that may explain indirect references, never proof of current emotion or intention.
- Mark memory as a contributing evidence modality when an output actually relies on it.
- Ensure the cautious local policy does not return a memory-free answer before eligible memory evidence is considered.
- Keep F04's existing no-memory path byte-for-byte or behaviorally equivalent where practical.
- Limit memory-aware requests to four excerpts and a 700-token memory allowance within 2,200 estimated input tokens. Drop the lowest-ranked excerpt first. Never increase transcript or output limits.
- Keep user-visible remembered-detail suggestions to three even when four excerpts are supplied.
- Reuse the 12-second request cadence, one-in-flight/latest-pending coordinator, and 12-second stable-card policy. Keep a locally matched possible-memory display for 24 seconds after its last matching snapshot so one brief retrieval miss does not make it flicker; identity and lifecycle invalidation still clear it immediately.
- Normal rank-score jitter does not replace a stable card. A contact change, memory correction, supersession, deletion, sensitivity/cloud-permission change, or source invalidation immediately clears affected guidance and invalidates stale results.
- Manual Terra uses the newest snapshot and current contact/memory generation.
- Log only content-free IDs, ranks, lifecycle decisions, usage, and failure categories unless an existing user-visible record view intentionally shows local text.

### Required F04 regression comparison

Run the fixed F04 interpretation set:

- without memory;
- with the correct approved contact memory;
- with a wrong-contact store that must contribute nothing;
- with low-confidence memory;
- with sensitive memory lacking cloud permission;
- after correction/supersession;
- after deletion; and
- under ambiguity.

Memory enrichment must improve the indirect-reference case without worsening the existing no-memory baseline or creating unsupported high-confidence conclusions.

## Relationship personalization and F06 boundary

F05 may approve atomic memories such as prefers direct answers, appreciates gentle check-ins after difficult topics, or uses Sommer as a nickname for Eitan when supported by evidence and reviewed by the user.

It does not synthesize a hidden style profile or produce replies. Retrieval exposes a small set of current approved relationship/communication memories through the same eligibility rules. F06 may later use them for suggestions, reminders, and follow-ups after its own plan adds explicit output contracts and evaluation.

Do not add a generic personalization engine, prompt-template registry, strategy objects, or dormant reminder/reply fields in F05.

## Privacy, deletion, and export

- Local text retention is explicit in the call/import UI and documentation.
- The database lives under the current Windows user's LocalAppData. No automatic cloud backup is added.
- Sensitive content is local-only unless the user enables cloud use on that exact current memory revision.
- Every cloud path filters first and serializes only the selected short excerpts.
- Deletion scrubs content and regenerable indexes in the same transaction before success is reported.
- A source deletion preview defaults all derived memories to delete. Keeping an item is an explicit opt-out for that item.
- A contact deletion preview names all records, proposals, memories, aliases, and tombstones that will be removed.
- JSON export is versioned and validated before reporting success. Export files are outside the app's later deletion control; warn the user clearly.
- Importing a future export version fails safely with an understandable version error. Import support is not required unless already needed for migration testing; do not build speculative two-way sync.

## Budgets and performance

### Cloud cost

- Post-call extraction shares F04's 0.25 USD Assisted Call hard limit. When insufficient budget remains, analysis waits for manual retry.
- Each explicit import analysis has a displayed estimate and 0.25 USD hard limit.
- Controlled F05 real-model extraction/retrieval evaluation has a 2.00 USD total hard limit.
- Use fake models for normal tests. Record profile, reasoning, input/output/reasoning tokens, estimated cost, and outcome for every real evaluation request.
- Revise caps only from recorded evidence and explicit user approval.

### Runtime limits

- Warm local retrieval on the large synthetic store: p95 at or below 250 ms on the target Windows machine.
- F04 memory-aware request starts still follow the existing 12-second cadence and cloud/display latency gates.
- Every memory-aware F04 request stays at or below 2,200 estimated input tokens.
- UI, capture, and transcription threads never wait on database search, extraction, embedding setup, or cloud rerank.
- Use bounded queues and cancel/stale-generation checks already present in the application rather than adding a second scheduler framework.

### Storage scale

Exercise at least:

- 1,000 contacts with colliding common names and aliases;
- 100,000 current and historical memory revisions;
- long imported histories split across many bounded chunks;
- duplicate groups containing several proposal pairs;
- source deletion with many derived memories; and
- contact merge/reassignment with rollback injection.

The performance fixture may use deterministic fake embeddings. Run the real embedding model only on the fixed small semantic-retrieval set.

## Failure and abstention behavior

| Failure | Required behavior |
|---|---|
| No contact selected | No retrieval or extraction; save/prompt as Unassigned |
| Ambiguous alias | Show candidates; never auto-select |
| Database unavailable/corrupt | Disable writable memory safely; preserve capture/transcription; show recovery path |
| Migration failure | Retain verified backup/original; no empty replacement database |
| Extraction failure | Keep record and prior completed chunks; offer retry |
| Budget exhausted | Skip cloud work, preserve local record/candidates, show reason |
| Embedding model absent | Use visible reduced indirect-recall local mode |
| No relevant memory | Continue memory-free F04 |
| Close retrieval scores | Show possibilities, clarify, or abstain |
| Sensitive memory without permission | Exclude it from every cloud payload |
| Contact corrected | Invalidate old generation and clear affected guidance immediately |
| Memory corrected/superseded/deleted | Remove old revision from retrieval and FTS/embedding immediately |
| Source deleted | Apply preview choices transactionally; scrub or detach provenance |
| Cloud rerank invalid/refused | Keep local ambiguity; never guess |

Privacy, deletion, wrong-contact isolation, lifecycle filtering, database integrity, and prohibited certainty are fail-closed requirements.

## Implementation slices

Implement and verify one vertical slice at a time. Do not build all tables and abstractions before the first user-visible path works.

### Slice 1 — Storage and migration

- Add the LocalAppData database path, direct sqlite3 connection setup, schema version 1, constraints, backup/migration verification, and transaction helpers.
- Add focused tests for clean creation, reopen, rollback, failed migration, foreign keys, and corruption behavior.
- Keep the module narrow; no ORM or generic repository interface.

### Slice 2 — Contact identity and call association

- Add contacts, aliases, disambiguation, explicit selection/create/change, current generation, and stop-time Unassigned flow.
- Persist attributed finalized turns without raw media.
- Test alias collision, two contacts named Alex, several nicknames, mid-call correction, stale invalidation, and no retrieval before confirmation.

### Slice 3 — Import and Conversation Records

- Add strict text import preview/mapping/time-zone confirmation, local persistence, explicit estimate/Analyze, bounded chunk state, retry, assignment, deletion preview, and reassignment preview.
- Test invalid input and partial-failure rollback.

### Slice 4 — Proposal lifecycle

- Add strict extraction output, bounded post-call/import orchestration, atomic proposals, review, user-authored memory, rejection/reopen, approval, correction, supersession, provenance, sensitivity, cloud permission, and deletion.
- Add within-batch and approved-memory duplicate flags without suppression.
- Test phone-number non-collapse, immutable correction, rejected exclusion, full-chain deletion, kept-memory source detachment, and contact cascade.

### Slice 5 — Local retrieval

- Add contact/lifecycle-first SQL filters, FTS5, metadata/date candidates, deterministic fusion, bounded connections, search filters, and ambiguity/abstention.
- Run the Mem0/Graphiti/SQLite decision gate and record the selected direct approach.
- Test exact contact isolation before any semantic work.

### Slice 6 — Optional semantic gate and cloud rerank

- Benchmark FastEmbed/BGE-small only after the lexical baseline is recorded.
- Add local vectors only if the gate passes; otherwise document the measured rejection and ship FTS5/metadata.
- Add the at-most-five-candidate cloud rerank only if the fixed ambiguity set proves it necessary.
- Test missing-model and budget/offline behavior.

### Slice 7 — F04 memory enrichment

- Add current-generation retrieved excerpts to the bounded snapshot/request.
- Preserve memory-free behavior and existing coordinator/card rules.
- Implement immediate invalidation for contact and memory lifecycle changes.
- Rerun the entire F04 automated suite and the approved memory comparison set.

### Slice 8 — Search, merge, export, and documentation

- Finish contact-first memory management, explicit all-contact search, merge preview/transaction, versioned JSON export, deletion warnings, setup, privacy, backup, limits, and recovery documentation.
- Keep visuals functional and accessible; rich styling and bulk-review polish are optional.

## Automated evaluation

### Storage and lifecycle

- migration success, rollback, retained failed backup, and post-migration integrity;
- contact/alias collisions and ambiguity;
- unassigned call and later assignment;
- whole-record mid-call and historical reassignment;
- merge rollback and preservation of IDs/history;
- proposal approve/reject/reopen and user-created immediate approval;
- immutable correction and current-revision-only retrieval;
- source-deletion preview defaults and explicit kept memories;
- full-chain memory deletion and contact deletion including tombstones;
- sensitive cloud permission enable/revoke; and
- JSON schema/version/export validation.

### Extraction quality

Use deterministic fakes for contract tests and a fixed fictional real-model set for profile selection. Measure:

- atomicity;
- evidence correctness;
- type/date/confidence/sensitivity correctness;
- durable usefulness;
- unsupported inference rate;
- generic-small-talk exclusion;
- concrete routine-fact retention with `likely_generic` set, grouped for easy rejection;
- duplicate flag recall without suppression;
- two-different-values preservation; and
- empty-result behavior.

No model profile passes if it invents sensitive events, diagnoses, intentions, or high-certainty facts.

### Retrieval quality

The fixed set includes direct lexical queries, indirect references, aliases, dates, commitments, recurring topics, shared references, relationship preferences, low confidence, sensitive permissions, duplicate/contradiction, superseded/deleted/rejected items, wrong contacts, and no-answer cases.

Required gates:

- Recall@4 at least 90 percent;
- mean reciprocal rank at least 0.80;
- 100 percent pass on tragedy, ambiguity, wrong-contact, rejected, superseded, deleted, and sensitive-permission safety cases;
- zero unsupported high-confidence outputs caused by memory;
- warm local p95 at or below 250 ms on the large synthetic store;
- every F04 request within its memory-free or memory-aware token ceiling; and
- existing F04 cloud/display latency and stability gates remain passing.

### Tragedy and ambiguity fixture

Reuse the approved fictional Maya/Alex dialogue and media timing, but do not reuse a generic seed that literally contains the phrase the event.

- Correct-contact seed: Maya's dog Pepper died, dated August 18.
- Later dialogue: an indirect reference such as since the event.
- Expected: the approved Pepper memory is retrieved cautiously and improves contextual interpretation without asserting Maya's true emotion.
- Competing-event variant: add another plausible event with an equal or unknown date. Expected: show low-confidence possibilities, request clarification, or abstain rather than selecting one confidently. With distinct normalized dates and no direct clue, show only the uniquely newest event as cautious possible context; an older event requires an explicit lexical or date reference.
- Wrong-contact variant: the same seed exists only under another contact. Expected: it is never a candidate.
- Deleted/superseded/sensitive variants: expected lifecycle and permission exclusions are exact.

The HeyGen asset remains media stress input only. Its single animated voice, static participant tile, watermark, and omitted opening line mean it cannot replace the exact dialogue fixture or a consenting live call.

## Manual validation

Run one short consenting WhatsApp call using fictional data:

1. start without a contact and verify there is no memory retrieval;
2. select or create the contact during the call;
3. refer indirectly to one approved memory;
4. confirm the F04 update stays stable and cautious;
5. change or correct the contact/memory and verify stale guidance clears;
6. stop the call and review a bounded proposal batch;
7. approve, correct, reject, reopen, and delete representative items; and
8. verify search, provenance, export, restart persistence, and sensitive cloud exclusion.

Zoom and Google Meet may remain user-waived during this feature, recorded exactly as WAIVED — not passed with residual risk. Quantitative or manual gates may be waived during testing only through the same explicit wording and risk record.

The following cannot be waived: privacy boundaries, full deletion behavior, wrong-contact isolation, lifecycle filtering, database integrity/migration safety, and the prohibition on unsupported certainty.

## Trimming order

Schedule is currently ahead, but if trimming becomes necessary:

1. optional color enhancement and visual polish;
2. all-contact global search, while keeping contact-first search;
3. rich export UI, while keeping validated JSON export;
4. bulk-review convenience.

Never trim explicit contact confirmation, aliases/disambiguation, lifecycle/deletion/provenance, wrong-contact isolation, hybrid local retrieval, tragedy/ambiguity tests, or F04 integration.

## Implementation workflow and review

1. Re-verify local main, origin/main, and GitHub main before implementation. Preserve unrelated user changes.
2. Implement the slices in order with the smallest direct design that satisfies the contracts.
3. After each slice, run its focused tests plus affected F02-F04 regressions.
4. Record technology/model gates and real-call evidence in project-owned documentation, including rejected options and measured reasons.
5. Keep Trello cards synchronized with evidence and links. A card is complete only when its checks and documentation are complete.
6. Run the full automated suite, dependency check, migration/recovery tests, large-store performance test, fixed extraction/retrieval evaluation, F04 before/after comparison, and consenting manual gate.
7. Request a fresh Claude review of the completed F05 diff and evidence. The review must cover correctness, privacy, deletion, identity isolation, SQLite transactions/migrations, token/cost/latency bounds, stale-result handling, overengineering, and missing tests.
8. Correct every accepted finding, rerun affected checks, and request follow-up review until no unresolved material finding remains. Record disagreements with evidence.
9. Inspect the final diff for accidental secrets, raw-media persistence, generated data, unrelated edits, dormant abstractions, and documentation drift.
10. Commit the completed F05 implementation, push it, and verify local main, origin/main, and GitHub main point to the same reviewed commit.
11. Mark F05 complete only after those checks. Update PLAN.md, this plan, README/docs as needed, and the Trello roadmap/card evidence with the final commit and verification.

## Definition of done

F05 is done only when:

- a user can create/select/change a disambiguated contact before or during a call;
- unassigned calls are safely retained without retrieval/extraction and can later be assigned;
- attributed text persists locally without raw media;
- AI output remains review-only while user-created/corrected memories approve explicitly;
- revision, rejection, duplicate, provenance, sensitivity, deletion, reassignment, merge, and export behavior matches this plan;
- retrieval is exact-contact and current-approved-first, meets the fixed quality/performance gates, and abstains under ambiguity;
- F04 receives no more than four eligible excerpts within a 700-token allowance and 2,200-token total ceiling, and preserves its no-memory behavior;
- tragedy, wrong-contact, stale, contradicted, duplicate, sensitive, rejected, superseded, and deleted cases pass;
- migration/backup/failure behavior is verified;
- documentation and Trello evidence are current;
- Claude review corrections and all required reruns are complete; and
- the final reviewed commit is pushed and all repository pointers match.

Planning approval does not mark F05 complete.

## Execution status — 2026-08-27

- [x] SQLite schema, transactions, migration backup/integrity/recovery, and corruption-safe failure.
- [x] Contacts, ambiguous aliases, explicit association, Unassigned Conversations, merge, and reassignment.
- [x] Attributed-text call/import records with no raw-media persistence.
- [x] Bounded extraction, resumable Proposal Batches, approval/rejection/reopen, immutable revisions, provenance, sensitivity permission, duplicate flags, and deletion.
- [x] Exact-contact/current-approved FTS5 plus metadata/date retrieval and deterministic fusion.
- [x] Semantic gate closed: lexical retrieval missed all 3 indirect employment references; bounded local FastEmbed/BGE-small passed 3/3 at ranks 1/2/2 and was selected. Cloud reranking was not added.
- [x] Memory-aware F04 snapshot integration with four-excerpt/700-token-memory/2,200-token-total limits and stale-generation invalidation.
- [x] Contact-first management/search, explicit all-contact search, merge/deletion previews, and versioned JSON export.
- [x] Automated retrieval/safety and 100,000-revision performance gates.
- [x] Capped fictional-data Luna `none`/`low` extraction comparison; Luna `none` selected by the corrected cache-neutral gate.
- [x] One consenting fictional-data WhatsApp call; it exposed the indirect-employment gap that selected the semantic gate, and the supplied transcript now passes progressive replay.
- [x] Fresh Claude Opus 5 review, accepted root corrections, measured reruns, and final CLEAN REVIEW.
- [x] Final diff audit, reviewed commit/push, pointer verification, Trello reconciliation, and roadmap completion.
- [x] September 3 follow-up: automatic cadence reduced to 12 seconds and possible remembered context held for 24 seconds after its last match; generated retrieval keywords were not added because the selected local semantic model already passed the indirect-employment gate.

Detailed measurements are recorded in [docs/F05-VALIDATION.md](../docs/F05-VALIDATION.md).
