# F05 validation record

**Date:** 2026-09-01
**Status:** complete — automated, paid fictional-data, isolated UI/workflow, consenting WhatsApp, clean review, and release gates pass

## Selected implementation

F05 uses Python's standard `sqlite3` module, one local database under
`%LOCALAPPDATA%\ConversationCopilot\memory.sqlite3`, and SQLite FTS5. Foreign keys,
sequential `user_version` migrations, pre-migration backup, integrity checks, and
transactional lifecycle operations are enforced directly.

| Candidate | Decision |
|---|---|
| SQLite + FTS5 | Selected as the authoritative store and first retrieval stage. It passed exact-contact lifecycle safety, Recall@4, MRR, Windows latency, storage, offline, migration, and deletion gates. |
| Mem0 | Rejected. It adds configuration and dependency surface without improving direct lifecycle, deletion, isolation, or testability. |
| Graphiti | Rejected. A graph/database stack is unnecessary for atomic memories and bounded one-hop reviewed connections. |
| FastEmbed + BGE-small | Selected for bounded local candidates after lexical retrieval scored 0/3 on indirect employment references and local semantic retrieval scored 3/3 at ranks 1/2/2. The 67,181,383-byte model works offline; no vector database was added. |
| Cloud reranking | Not added. The fixed competing-event case safely returns possibilities/abstention locally. |

## Automated and local evaluation

Command: `python -m pytest`

On 2026-08-30 the user approved a 1,500-token base request target plus up to 700
estimated tokens for memory, giving memory-aware requests a 2,200-token hard ceiling.
The memory-free 1,650 hard ceiling, 1,000-token transcript target, 400-token output cap,
and output behavior are unchanged. The live path now supplies all four allowed excerpts.
Measured against the real compact payload with short fixture IDs and `date/type`
relevance, four 180-character excerpts plus fixed memory instructions use about 529
tokens. An adversarial four-row case with near-maximum revision and relevance fields uses
about 1,249 tokens before trimming; the explicit 700-token guard retains only the
highest-ranked row. The compact speaker codes `u` and `c` save about 48 tokens in a
16-turn alternating exchange compared with `user` and `selected_contact`.
Optional visual/vocal data trims first. Older transcript turns then trim only until the
memory-free request fits its separate 1,500-token target; a relevant memory is removed
only if its own measured allowance still cannot fit. The visible transcript uses the
confirmed contact's name instead of the call-window title; contact IDs still define
memory isolation.

At the configured model prices, a maximum Luna request is about **$0.00092** with
ordinary uncached input or **$0.00103** under the ledger's conservative all-cache-write
reservation. At the absolute 17-second cadence that is about **$0.195/hour** ordinary or
**$0.218/hour** conservatively reserved. One manually confirmed maximum Terra request is
about **$0.0103**. Real cost is normally lower because outputs are usually shorter than
400 tokens and automatic requests require a new finalized turn.

- 195 tests passed with fake models and zero cloud cost after review corrections and
  manual-call usability fixes.
- `pip check` passed.
- Migration creation/reopen, backup restoration, injected rollback, corruption,
  foreign-key, merge rollback, reassignment, lifecycle, sensitivity, deletion,
  contact cascade, import, resumable extraction, export, and contact-isolation cases pass.
- Recall@4: **1.00** (gate: at least 0.90).
- MRR: **1.00** (gate: at least 0.80).
- Safety: **11/11, 100%** across tragedy, competing-event ambiguity,
  wrong-contact, rejected, superseded, deleted, sensitive permission and revocation,
  and both F04 token ceilings.
- Unsupported high-confidence results caused by memory: **0**.
- Leakage-free Pepper tragedy rank: **1**. The competing-event variant returns
  possibilities rather than a selected fact.
- F04 before/after request estimate: 1,268 tokens without memory and 1,537 with
  one correct-contact excerpt. Wrong-contact memory rows: 0.
- Large store: 1,000 contacts with colliding names/aliases, 100,000 revisions,
  50,000 current FTS rows, 42,729,472-byte database, integrity clean, correct
  exact-contact production-shape and explicit-date results, **150.116 ms**
  warm retrieval p95, **126.283 ms** open-plus-retrieve p95, and **0.753 ms**
  indirect temporal retrieval p95 with a correct uniquely-newest result (gate: at most 250 ms).

Command: `python -m conversation_copilot --evaluate-f05-local`

## Paid fictional extraction comparison

Command: `python -m conversation_copilot --evaluate-f05-real`

All data was fictional. Sixteen API calls compared Luna `none` and `low` in
alternating first/second order across
preference, two independently changeable phone numbers, sensitive Pepper tragedy,
generic small talk, transcript prompt injection, dated commitment, normalized date,
and atomic-fact cases. No request used cached or cache-write input tokens. The final
JSON recorded pass/fail, tokens, cost, and latency for every request.

| Profile | Passed | Input | Output | Reasoning | Estimated cost | p95 |
|---|---:|---:|---:|---:|---:|---:|
| Luna `none` | 8/8 | 3,566 | 629 | 0 | $0.001468 | 6.313 s |
| Luna `low` | 8/8 | 3,566 | 934 | 302 | $0.001834 | 2.727 s |

Final-run estimated cost was **$0.003302**. Total measured cost across the original
comparison and two review-driven reruns was **$0.00992375**, below the $2.00 hard
limit. Luna `none` is selected because it was the cheaper passing cache-neutral profile.
Forbidden diagnoses, intentions, and unsupported sensitive claims: 0.

## Claude review

The first Opus findings-only review (`6a934fba-9559-48fc-b2af-1880c82b0814`)
identified stale proposal approval, evaluation self-scoring, memory-policy bypass,
contact-change invalidation, worker integrity-scan latency, sensitive search display,
cross-contact mutation, retrieval fallback, retry/budget gaps, duplicate-scan bounds,
cache-order bias, date triggering, disclosure wording, merge alias handling, stale UI
snapshots, excerpt truncation, and missing regression coverage. Accepted findings were
fixed at their shared seams and covered by focused tests. The suggestion to send
ambiguous memory candidates to F04 was not accepted because the approved plan permits
clarification/abstention and prohibits unsafe candidate selection.

The fresh full-diff review (`7daa0002-6c68-4970-a328-8bc8ab781b16`) then found and
triggered root fixes for single-contact export scope, alias-preserving merge, lexical
versus generic temporal fusion, dialog contact capture, active-call deletion
invalidation, re-entrant finalization, extraction token/cost bounds, duplicate retry,
proposal foreign keys, real cloud-eligibility validation, complete tombstone scrubbing,
current-revision source previews, worker-open guards, portable export parameter counts,
deterministic duplicate flags, search filters, and UI error paths. WAL was not added:
the plan requires measured need, the concurrent-reader test passes, writes are short,
and WAL would not remove writer-versus-writer serialization; the connection wait is
instead bounded to 250 ms.

The first follow-up confirmed those fixes and found remaining active-record management,
short-lock retry, stop-time contact-label, oversized-import persistence, and modal Stop
access edges. They were corrected and the full suite rerun. After the reset, a fresh
tool-disabled Sonnet review (`c0a3ebdc-ba22-463a-88b5-ee658b202a8d`) found a trimmed-memory
instruction mismatch, incomplete mutation error handling, an unsafe exact-date no-match
fallback, duplicate approved proposals in management, silent partial-name assignment,
and missing store-level contact enforcement for memory connections. All six were fixed
at their shared seams; focused tests pass 24/24 and the complete suite passes 151/151.
The required clean Opus 5 follow-up remains pending; no clean-review claim or waiver is
recorded.

The subsequent tool-disabled Opus 5 review (`c1f8597f-fe5b-431d-ad6f-7aede3811238`)
identified memory-first trimming/disclosure, non-temporal score ambiguity, incidental
date filtering, long duplicate scans inside a write transaction, reassignment connection
ownership, conservative merge-preview wording, and missing isolation coverage. Accepted
findings were corrected at the shared seams: optional visual/vocal rows trim before memory,
the UI snapshot reflects excerpts that survive request preparation, close same-type lexical
candidates return possibilities, call-time date filtering uses latest-turn intent, duplicate
discovery runs outside `BEGIN IMMEDIATE`, cross-contact edges are removed on reassignment,
the merge preview names same-type review items accurately, and regression tests cover these
paths plus unaffected-contact FTS retention. The proposal-flag deletion suggestion was not
accepted because deletion must scrub the approved proposal's content and evidence; retaining
its comparison text would violate the non-waivable deletion contract. The cautious-model path
is intentional after local hard-safety checks, and the direct extraction schema is supported
by all 16 recorded live fictional calls. After these corrections, focused tests pass 27/27,
the full suite passes 154/154, and the measured retrieval and safety gates above still pass.

A fresh final-diff Opus 5 pass (`5f7caae8-4584-4ed3-829d-79999c268f84`)
then found that generic `event` retrieval mixed commitments into the base Pepper case,
merge invalidated same-person pending proposals, the large-store measurement used a shorter
query than production, retrieval errors could be overwritten by a no-match label, and active
unassigned calls appeared in historical management. The retrieval type cue now selects the
single event-date possibility before the competing event exists; the evaluation counts only
non-ambiguous hits; merge preserves batch generation and review state while previewing pending
proposals; the large gate uses the full 12-token production bound; and both smaller UI/state
paths are corrected. Opus's import-name concern was disproved by the module-level parser import,
and analysis results are drained unconditionally before the optional coordinator branch. The
corrected focused suite passes 28/28, the full suite passes 154/154, and the 100,000-revision
production-shaped timing above remains within its gate. A clean Opus correction review is still
required.

The next Opus pass (`91ca7695-2f69-41ac-994d-d0baa3dc94b5`) identified that
non-temporal ambiguity used RRF rank spacing rather than lexical separation, active-contact
deletion could cascade a live record, the contact-memory fallback could leave a stale F04 card,
the 250-token allowance was not scoped strictly to memory, related expansion lacked deterministic
ordering, and the fixed set lacked alias/low-confidence/no-answer coverage. Ambiguity now uses
normalized BM25 separation, active-contact deletion is blocked transactionally, snapshot-limit
failures replace the stable card correctly, the request target adds only measured memory payload
tokens, related rows have a stable order, and all missing cases are evaluated. The vague
`since then` variant intentionally abstains when both an event and commitment remain plausible;
choosing Pepper there would violate the approved uncertainty rule. Permission toggles remain
immutable user-approved revisions, so their revision approval time intentionally changes while
source/event dates do not. Focused tests pass 30/30, the full suite passes 156/156, and the stricter
large-store gate now asserts production does not withhold the measured result. A clean Opus
correction review is still required.

Opus review `d0e2c811-0311-4b53-82fa-9b315ee82914` then found the extraction
schema allowed more proposals than its output cap could encode, unmatched explicit dates
discarded strong lexical commitment matches, and the real extraction client lacked automated
contract coverage. Extraction is now bounded to 20-turn chunks and eight atomic proposals per
2,400-token response; pure unmatched date questions still abstain, while strong non-date lexical
evidence survives after date tokens are removed; and fake-client tests cover `store=false`, the
cap/schema, success accounting, transient retry, authentication release, and invalid structured
output with zero cloud cost. The same pass confirmed the remaining isolation, deletion,
transaction, stale-result, and trim paths. Focused tests pass 32/32 and the complete suite passes
158/158. A clean Opus correction review is still required.

Opus review `4f62b9f3-9c8a-421d-b701-277e56b91458` found that temporal words could
bypass the close-score ambiguity guard, offset datetimes were compared as UTC calendar
dates, and removing date tokens also removed unrelated numeric identifiers. The shared
retrieval guard now applies whenever a prior metadata ambiguity check has not fired;
normalized event dates persist as their stated local calendar date; and lexical parsing
removes only the matched date span. Focused memory tests pass 25/25, the complete suite
passes 159/159, and the rerun 100,000-revision gate passes at 147.487 ms warm p95.
A clean Opus correction review is still required.

Correction review `843b35b5-83c4-4f3a-bee8-b994cb63b9ce` found that the real
F04 caller supplies an explicit `date_query`, which bypassed date-span removal, and
that a non-modal management dialog could clear a different contact selected after the
dialog opened. Retrieval now removes date spans whenever `date_query` parses, with a
regression using the production caller shape, and contact deletion clears the current
selection only when it still names the deleted contact. The full suite remains 159/159.
A clean Opus correction review is still required.

Correction review `37a088dd-cbce-4557-8402-be2289eb6a3a` found that merging
the main window's newly selected contact through an older non-modal dialog could leave a
deleted selection pointer, the strict eight-proposal schema could exceed its earlier output
cap, and the retry dialog trusted a stale record-state snapshot. Merge now redirects a selected
merged ID through the existing contact-change seam; retry re-reads the record immediately
before starting; and the output cap uses the existing conservative 2,400-token schema/protocol
allowance without changing the 6,000-token request reservation or $0.25 run limit. The complete
suite remains 159/159. A clean Opus correction review is still required.

Correction review `62771f24-fff9-4f59-9351-cee09b34145a` found that the larger
extraction output cap was still priced through F04's 400-token default, healthy verified
opens repeated the integrity and foreign-key scans, and contact deletion removed FTS rows
one revision at a time. The existing cost functions now accept a caller-specific output cap,
and both extraction estimation and ledger reservation price all 2,400 possible output tokens;
current-schema open runs one verified scan; and contact FTS deletion is one set-based statement.
Focused memory tests pass 26/26 and the complete suite passes 160/160. A clean Opus correction
review is still required.

Correction review `2aab157a-6961-4fff-965d-fbdb1817ac54` found that closing the
app during daemon extraction could leave a batch and record permanently marked running,
preventing manual retry. Verified main-app startup now transactionally marks interrupted
running batches and records failed; worker opens do not reconcile an active sibling run.
The existing retry path resumes the same batch from its completed chunk count. The focused
restart regression passes and the complete suite passes 161/161. A clean Opus correction
review is still required.

Final tool-disabled Opus 5 correction review
`a50698be-89c1-49ef-bc71-2ad3b044cb94` returned **CLEAN REVIEW** with no
unresolved material finding. It explicitly re-verified wrong-contact SQL isolation,
full-chain deletion, source detachment, migrations and recovery, transaction boundaries,
thread-local stores, generation/snapshot stale-result rejection, extraction reservation,
and the then-current 1,650/1,750-token ceilings. Its non-blocking maintenance notes do not affect the
approved F05 behavior or current gates; no review waiver is used.

After the UI and mock-call additions, fresh tool-disabled Opus 5 review
`6bb55a51-77d1-4409-beab-eb66140d7f83` found two release blockers. A crash could
leave a call record permanently `active`, hiding its text and preventing contact
deletion; verified startup now transactionally stops stranded active records while
worker opens leave a live sibling alone. Temporal intent also inherited `event` or
`since` from the full six-turn lexical window; both temporal intent and lexical recall
now use only the current two-turn exchange. Regressions cover crash
recovery/deletion, stale event wording followed by lunch, and a date question in the
immediately previous turn.

The corrected full diff then received a fresh tool-disabled Opus 5 review
`4b1f1fe2-f4b2-48be-9b90-a4509c5071ca`, which returned **CLEAN REVIEW**. It explicitly
re-verified the two fixes plus contact-ID isolation, ambiguity and wrong-contact
abstention, full revision-chain/FTS/source/connection deletion, reassignment and merge
invalidation, SQLite transaction/migration/recovery behavior, stale snapshots,
lifecycle and sensitive-cloud filters, F04 token/cost ceilings, bulk UI actions, and
mock/manual coverage. No review waiver is used.

After the isolated UI/workflow and real fictional interpretation evidence was recorded,
final tool-disabled Opus 5 session `050adb79-770a-4681-b5d5-474269337747` returned
**CLEAN REVIEW**. It cross-checked the code/tests rather than accepting evidence prose,
and confirmed the crash/temporal fixes, isolation, ambiguity, full deletion, migration
and transaction boundaries, stale results, lifecycle/sensitive filtering, token and cost
caps, bulk actions, and documentation alignment. It also confirmed that the consenting
WhatsApp gate and final commit remain correctly incomplete.

After the dated multi-call expansion, tool-disabled Opus 5 review
`b2518944-4a2a-429f-b9b7-30fd4f1b8760` found that manual Event/date entries lacked
the normalized date needed by the recency rule, database path/open failures could
escape the unavailable-memory fallback, statement-form event cues were punctuation
sensitive, and fixed/large evaluation did not fully exercise the production temporal
path. The editor now accepts and corrects an optional `DD/MM/YYYY` date; store startup
wraps path and connection failures; temporal intent uses word tokens; fixed evaluation
uses the production query builder; unknown-date ordering is pinned as ambiguous; and
the 100,000-revision gate times the indirect temporal path. The corrected suite passes
172/172 and the measured gates above pass.

Correction review `f8b75794-95ea-4c29-994d-adc4268c51df` found one remaining
UI-row blocker: the correction dialog requested a normalized date column that the
management list/search queries did not select. Both shared queries now return original
and normalized dates, unchanged dates preserve original model/user wording, and a
focused regression exercises rows from both query paths. A clean correction review is
covered by the full 173-test rerun. Fresh tool-disabled Opus 5 session
`9c1d7e1d-a371-4af2-92e4-e1f898aa3872` returned **CLEAN REVIEW** with no unresolved
material finding. It rechecked the UI row shapes and immutable date revisions plus
contact isolation, ambiguity/sensitivity cloud exclusion, deletion, transactions and
migrations, stale results, token/cost bounds, tests, documentation, and unnecessary
complexity. No review waiver is used.

After the then-approved memory-aware input ceiling was raised from 1,750 to 1,900,
focused Opus 5 correction review `21946bac-86c0-4fd2-bda0-73b35d528a25`
returned **CLEAN REVIEW** with no unresolved material finding. It confirmed that the
boundary regression exceeds the former ceiling while retaining all three maximum-length
live excerpts, all then-active contract references used 1,900, and the memory-free 1,650,
transcript 1,000, and output 400 limits remain unchanged. The complete suite passes
174/174 and no review waiver is used.

Opus 5 follow-up review `1e882947-7619-4eee-aa98-d22e97e97e0c` found that
mid-call contact changes did not relabel existing visible turns, the 700-token memory
allowance depended on current field-size bounds instead of direct enforcement, and the
three-item visible-suggestion cap lacked an explicit regression. Contact changes now
relabel all visible contact turns and the active audio label while preserving the call
window fallback; an explicit memory-overhead guard drops lowest-ranked rows above 700;
speaker-role encoding uses an exhaustive map; and regressions pin all three behaviors.
The focused four-file suite passes 35/35 and the complete suite passes 177/177.
Subsequent Opus review `f4e5d639-7a4c-48eb-b240-e188b27fd89c` prompted one shared
append/replace transcript renderer, explicit callback-turn rendering, displayed-label
change handling, and clearer normal-versus-adversarial token measurements. Its remaining
questions were resolved from the full code: contact selection is deliberately visible and
sticky for repeated calls; whole-record reassignment intentionally relabels the one remote
participant; the renderer's common tail is the only visible-memory consumer; preparation
trims a copy and recomputes its target; and snapshots exclude unclear speakers. The resumed
final Opus 5 session `07ba3f4d-3415-4ecc-b1b9-0d74731e0604` returned **CLEAN REVIEW**
with no unresolved material finding. No review waiver is used.

## Privacy and generated-data check

The local database retains normalized attributed text and, after explicit model setup,
regenerable 384-dimensional memory vectors. Runtime audio, PCM, video, frames,
landmarks, blendshapes, screenshots, model files, vectors, and generated evaluation
databases are not persisted in the repository. Export omits FTS/vectors and other regenerable
internals and warns that the exported file is outside later deletion control.

## Manual gate

The consenting fictional-data WhatsApp call passed contact creation/selection, live
attributed transcription, proposal quality, later same-contact memory use, and cautious
interpretation. It also exposed that lexical retrieval did not surface Yaheli's job-loss
memory until the conversation explicitly said “job.” That defect is corrected and the
supplied transcript now has a permanent fictionalized progressive regression. F05 and
its roadmap item remain incomplete until final review, commit, push, and pointer checks.

An initial Yaheli call on 2026-08-29 confirmed exact-contact Pepper retrieval for
indirect “the thing / the event” wording, but exposed two usability gaps: retrieved
context was not stated clearly unless the model happened to cite memory, and deletion
processed only the first selected memory. The correction now shows up to three local
approved details as cautious possible remembered context, labels approved memory as an
evidence source when it contributes alongside present conversation evidence, and makes
multi-proposal review and multi-memory deletion transactional. The manual gate must be
repeated against this corrected build before it can pass.

The reusable `f05-mock-memory-calls-v1` fixture now runs eight fictional call
scenarios through the production query builder, exact-contact SQLite retrieval,
bounded F04 request, and user-visible interpretation formatter. It covers Pepper by
“the event,” “after that,” competing events, wrong contact, sensitive permission on
and off, unrelated conversation, and no confirmed contact. The first run caught a
false positive where unrelated “today” wording selected an arbitrary event; the
shared metadata fallback now requires an explicit date or a genuine event-reference
cue. All eight scenarios pass without cloud use. The fixture reuses the approved F04
video and does not add generated faces or call media.

An additional four-call dated-memory sequence uses three approved events for one
contact plus a distinct newer event for another contact with the same display name.
Generic “the event” and “after that” wording returns only the uniquely newest dated
event as cautious context; explicitly naming Pepper or the job loss retrieves the
corresponding older event. Equal-date events still return possibilities, and the
other contact's newer event never crosses the contact-ID boundary.

The 86.555-second basic video transcript now also replays progressively at the real
17-second analysis cadence. Six authored checkpoints receive only the turns finalized
by that time and use an independent, prewritten fake-model response sequence to assert
the expected visible tone/cue, memory evidence, topic change, and stable-card replacement.
Actual video decoding and face-motion handling remain covered by the separate F04 video
tests; this replay does not claim progressive visual-model evaluation. A second
progressive replay covers eight checkpoints
across three calls: indirect wording selects Yaheli's newest dated event, explicit
Pepper and job-loss wording selects the older matching event, a later Yaheli call
recalls the newest event again, Noa receives only her ceramics-prize memory, and an
explicit Pepper question to Noa returns no memory. The replay exposed and corrected
weak shared-name matches, statement-form `when` being mistaken for temporal intent,
old-exchange carry-over, and relevant memory being dropped before the base transcript
was trimmed to its separate allowance.

A longitudinal fixture adds two different contacts both named Maya and four calls.
The first call produces five evidence-linked proposals; three are approved together
and two rejected together. The workflow corrects the tea memory immutably, verifies
that later calls retrieve only the corrected tea and Pepper event for the original
contact, verifies that the second Maya retrieves her distinct Pepper prize memory,
and then deletes two selected memories while preserving the phone memory and every
memory belonging to the other Maya.

On 2026-08-29, an isolated `%LOCALAPPDATA%` profile was exercised through the actual
desktop UI and production store paths, leaving the user's real contacts untouched.
The visible run created and explicitly confirmed a fictional contact, verified the
wide left-controls/right-transcript layout, the large memory editor, selector labels
without underscores, the `Other` option, bulk-action buttons, selection hint, and
near-duplicate display. The same isolated database then approved three proposals in
one transaction, rejected three in one transaction, created an immutable correction,
retrieved tea in a later same-contact call, retrieved the Pepper tragedy through
indirect “the event” wording, kept a second same-name Maya isolated with her distinct
Pepper prize memory, and deleted two selected memories together while preserving the
phone and other-contact data. Exact rejected proposal contents remained absent from
retrieval. Restart cleared contact confirmation and required explicit selection again.

One real fictional `store=false` interpretation request used the corrected Pepper
memory with “How have you been since the event?” / “It still hurts, and I do not want
to name it out loud.” The visible card identified sadness and discomfort from current
language and separately stated the cautious link “The recent words may refer to” the
Pepper event. Usage was 959 input tokens, 148 output tokens, zero cached/reasoning
tokens, **$0.0003694**, and **6.220 s**. Measured F05 evaluation spend through that run
was **$0.01029315**.

After the 700/2,200 budget and `u`/`c` prompt change, a second fictional `store=false`
Luna `none` spot-check used the same indirect Pepper pattern. It returned an updated
medium-confidence sad/low-energy hypothesis, used language plus memory, described the
Pepper link as tentative rather than proof, and leaked neither speaker shorthand into the
visible result. Usage was 937 input tokens, 196 output tokens, zero cached/reasoning tokens,
**$0.0004226**, and **7.994 s**. Total measured F05 evaluation spend is now
**$0.01071575**. These isolated runs are pre-live evidence only; they do not replace the
required consenting WhatsApp call.

A six-checkpoint real Luna replay of that progressive transcript completed after API
credit was restored. It revealed that one model response marked memory as an evidence
source even though that checkpoint contained no memory row. The shared output boundary
now derives eligible modalities from the exact post-trimming JSON request and discards
an entire item if any cited source was unavailable, so unsupported prose or confidence
cannot survive by merely stripping its label. Request fitting also preserves at least
one selected-contact turn and removes lowest-ranked memory only when the 2,200-token
hard ceiling requires it. Focused trimming and modality regressions cover mixed,
fully unsupported, and valid items plus hard-ceiling eviction.

That real rerun completed all six checkpoints. The first indirect-loss exchange
retrieved only the approved Pepper event and the model used it tentatively alongside
current language. The remaining five checkpoints retrieved no memory and every emitted
item cited language only. Four checkpoints used local cautious rules; the two real Luna
requests used 1,926 input tokens and 411 output tokens for **$0.0008784**. The
automated suite at that stage was **185 passed**, and `pip check` reported no broken requirements.
Including two earlier complete progressive reruns and one successful request whose
reporter crashed before recording its ledger row, measured F05 spend is **$0.01341335**
and total estimated spend is approximately **$0.01379695**.

Fresh Claude Opus 5 review session `5118c055-1732-4817-a3d0-1323741062e7` found no
runtime defect in contact isolation, confirmation gating, ambiguity handling,
lifecycle/sensitivity filtering, transactional deletion, request bounds, stale-result
protection, SQLite recovery, or the independent progressive tests. It identified only
stale validation numbers and an incorrect statement that lexical recall still used six
turns. The record was updated with that run's test and large-store measurements and
correctly states that both lexical and temporal retrieval use the current two-turn
exchange. A final correction review follows this documentation-only fix.

Post-replay Claude Opus 5 review accepted and corrected three root issues: validation
against the prepared request rather than the pre-trim snapshot, whole-item rejection
when any claimed modality is absent, and preservation of a selected-contact turn while
fitting the request. It also prompted explicit hard-ceiling memory-eviction coverage.
Two subsequent final-clean invocations produced no stdout or stderr and timed out; this
is recorded as an open review-service gate, not as approval. The prior complete F05
review remains clean, but a final post-correction CLEAN response is still required.

## 2026-09-01 live-call semantic correction

The consenting Yaheli WhatsApp call used fictional job-loss data and passed contact
creation/confirmation, contact-named transcript display, proposal review, and later-call
memory use. The user liked the proposal style and identified three improvements:
indirect employment language needed earlier recall, one-off routine activity should not
be proposed as durable memory, and dates should display as `DD/MM/YYYY`.

The supplied transcript was replayed transiently, one finalized turn at a time, through
the production query builders and store; it was not committed or retained. Lexical-only
retrieval scored 0/3 on “let me go / need money,” “newspaper or online,” and “pay the
rent.” The measured FastEmbed/BGE-small gate scored 3/3 at ranks **1, 2, 2**, so the
plan's optional semantic path was selected. Setup is explicit, the local cache is
**67,181,383 bytes**, offline startup passed, and warm end-to-end semantic retrieval p95
is **92.513 ms**. Retrieval remains SQL-first and read-only during calls: exact contact,
current revision, lifecycle, and sensitive-cloud filters run before cosine scoring.
All eligible vectors for that one contact are scored locally, then only the best 12
enter deterministic fusion. Background maintenance fills
missing vectors; call startup never downloads a model.

After filtering generic single-word lexical matches and adding bounded topic-boundary
reset, the exact progressive replay returns no job memory on the first three
days/years/“Now” lines, first returns it at “they let you go,” keeps it within the top
four through every indirect employment line including newspaper and rent, and removes
it after “Besides that.” A permanent fictionalized regression covers the same sequence,
including another same-name contact. The extraction instructions now exclude one-off
routine activities unless they establish a durable preference, commitment, milestone,
or recurring topic; a real `store=false` spot-check for “I took a normal walk after
lunch” returned zero proposals.

Current local gates: **195 passed**, `pip check` clean, Recall@4 **1.00**, MRR **1.00**,
safety **11/11**, and unsupported high-confidence memory results **0**. The
1,000-contact/100,000-revision database is **42,729,472 bytes**, integrity-clean, with
warm retrieval p95 **150.116 ms**, open-plus-retrieve p95 **126.283 ms**, and temporal
p95 **0.753 ms**. The large fixture uses deterministic/no semantic vectors as permitted
by the plan; the real model is measured on the fixed indirect set.

Four paid progressive interpretation checkpoints used the correct job memory cautiously
at the first three employment checkpoints; the fourth relied on the explicit current
conversation. The captured rerun cost **$0.0020198**. The routine-activity extraction
spot-check cost **$0.0001108**. Including an equivalent completed four-call run whose
reporter failed before serializing the ledger, total known measured F05 spend after the
implicit-grief follow-ups below is **$0.01721345** and total estimated F05 spend is
**$0.02003265**, below the $2.00 cap.
Fresh tool-disabled Claude Opus 5 session
`64681e39-7835-4629-8283-d3b86b64511c` reviewed the complete diff and initially
found that pre-score `LIMIT 12` made an older semantic memory unreachable after 12
newer items. The limit moved after exact-contact scoring, a 13-newer-item regression
pins the fix, and contacts without vectors now skip model loading. The fixed evaluation
also stopped adding artificial question marks. Its stable-card concern was withdrawn
after tracing the public displayed update versus private queued update and the existing
5/11.9/12-second regression. The disposable semantic gate remains beside the installed
model cache by design and deletes its seven fictional rows in `finally`; moving it would
require an otherwise-unused cache override. After the measured reruns, the
same session returned **CLEAN REVIEW** with no unresolved material finding. No review or
release waiver is claimed.

## Grief-language verification

On 2026-09-01, the production local BGE model was replayed progressively against four
fictional ways of referring to an approved Pepper-loss memory: “the tragedy,” “the
recent sad event,” “the event” followed by “they meant everything to me,” and pronoun-only
“she meant so much to me, and I miss her every day.” Each target ranked first. The
tragedy/event cases stayed absent through their neutral preambles and appeared on the
first indirect cue; the pronoun-only case appeared when the complete grief statement
arrived. An unrelated pottery exchange excluded Pepper, another contact never received
Maya's revision, and two plausible losses returned possibilities rather than a silent
choice. A permanent fake-vector regression locks the production query/retrieval/request
seam; the full suite is **195 passed**.

Two additional real `store=false` Luna checks cost **$0.000772** total. The tragedy case
used current language for the grief/tone result while the visible panel cautiously said
the words may refer to Pepper. The pronoun-only case cited conversation words plus
approved memory and explicitly said that the Pepper link was tentative because “her”
was not identified. A memory marked sensitive must still have its per-memory cloud
permission enabled before it can enter F04 interpretation.

A follow-up replay used no explicit dog, death, tragedy, event, or Pepper wording. The
user asked only “How are you feeling after the whole thing?”; retrieval stayed empty
through “Honestly, it has been difficult,” selected only Pepper at “She meant a lot to
me,” and retained only Pepper at “I miss her every day.” Real BGE distractors included
job loss, moving, tea, pottery, a dead laptop, death metal, a connected tea memory, and
another contact. User-spoken copies of the grief phrases and mundane “I missed her
call / that meant a lot” wording retrieved nothing. Two undated plausible losses
returned possibilities; two normalized losses selected only the uniquely newest one
indirectly while the older remained directly retrievable. Sensitive loss context stayed
out of cloud retrieval without permission, and missing embeddings failed closed.

The final real `store=false` F04 check retrieved only Pepper and used conversation words
for the high sadness/low-energy tone. Its memory-aware cue said the words indicate an
ongoing loss and that approved memory only tentatively links the reference to Pepper;
the visible panel repeated that the memory was possible context, not proof. It used
1,011 input tokens, 178 output tokens, no reasoning tokens, cost **$0.00041580**, and
took **5.668 seconds**. One equivalent request completed before a reporter-signature
error prevented ledger serialization, so **$0.00041580** is included conservatively in
estimated rather than measured spend. The immediately preceding implicit check cost
**$0.00048170**. All calls used `store=false`.

Five focused tool-disabled Claude Opus review passes found and drove root corrections
for unrelated semantic/date candidates, speaker attribution, mundane phrase matches,
two-loss ambiguity, sensitive and degraded paths, explicit-topic preservation, dated
newest-event selection, and both directions of connected-memory leakage. The closing
session `5ab72da1-4949-4223-9776-28b2bd4a8bdd` returned **CLEAN** with no unresolved
material finding. The full suite remained **195 passed** with `pip check` clean.

## Release audit

The complete diff contains no API key/secret pattern, raw-media or database/model
artifact, user transcript, or dormant provider/factory/repository/event-bus scaffold.
The four unrelated untracked CV PDFs were explicitly excluded. The reviewed F05 files,
including the approved PLAN/CONTEXT/canonical-plan changes, were committed and pushed;
final local/origin/GitHub pointer evidence is recorded on Trello F05.13. No waiver is
used.
