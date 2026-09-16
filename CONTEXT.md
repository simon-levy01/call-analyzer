# Conversation Copilot

**September 15 two-call API evaluation:** Completed the user-authorized $0.40 comparison: 94 requests attempted, 93 structured answers, $0.21179406 committed including one failed-answer reservation. [Results](docs/TWO-CALL-API-COMPARISON-20260915.md). Waiting-only guidance is reduced, but speaker/context/repetition failures remain. Visual rows reach all recent snapshots; no new successful response cites visual evidence. Terra improves some memory categorization but is not a consistent factual upgrade. Production stays Luna low for all stages; no new production changes, memory edits or release. At recorded speech density, current long-call chunk/merge behavior materially increases hypothetical Terra post-call cost. Preserve the private evidence and ledger in `build/two-call-api-20260915/`; do not rerun/reset it.

**September 15 long-call correction checkpoint:** User requested isolated Sol High and root diagnostics without API spend, and fixes prioritizing guidance. See [diagnosis](docs/LIVE-CALL-DIAGNOSIS-20260915.md). Live replies now remain as optional recent-context ideas (24-second source-age bound, explicit resets/repetition removal), instead of clearing on every utterance. No automatic waiting fallback; facial rows no longer lose all budget before older vocal rows. Prompt changes are not yet fresh-Luna-validated; Claude review/live acceptance remain pending. Preserve the ignored private source/input/output evidence and unrelated dirty work; no F07 completion or automatic release is implied.

**September 14 vision-model revision:** User explicitly requested downloading and locally benchmarking the pretrained visual-model shortlist, prioritizing RAM, plus external validation clips. This selects local vision inference; Luna low remains selected and local language-model comparisons stay set aside. Private downloads/results: `build/f07-pretrained-20260914/`; [vision screening](docs/F07-VISION-SCREENING.md). This does not replace the production model, spend API budget or waive F07 review/human/acceptance gates.
Completed CPU screening: all six pipelines tested on DISFA development data and two new conversation clips; portrait peak resident memory ranged from 258 to 1,326 MiB. Current pipeline retained; independent annotated validation and full F07 gates remain pending.

A private assistive application that helps an autistic user interpret and respond during a selected one-to-one conversation while preserving long-term, contact-specific context.

## Language

**Conversation Copilot**:
The application that provides cautious, contact-aware guidance during conversations chosen by the user.
_Avoid_: Autistic Analyzer, emotion detector, people reader

**Assisted Call**:
A one-to-one video or voice conversation that the user has explicitly selected for live support.
_Avoid_: recording session, monitored call

**Selected Call Window**:
The visible WhatsApp Desktop, Zoom, or dedicated Google Chrome window with an active Google Meet call that the user explicitly chooses as the source for an Assisted Call.
_Avoid_: desktop recording, hidden capture, automatic window target

**Selected Contact**:
The person whom the user confirms as the other participant before or during a conversation. Contact memory is not used or changed until that confirmation.
_Avoid_: detected person, target, subject

**Contact Suggestion**:
A proposed match derived from visible window text, saved aliases, or conversation context that the user must confirm or replace.
_Avoid_: automatic identity, facial recognition

**Contact Alias**:
A platform name, nickname, or other non-biometric identifier linked to one contact with the user's confirmation. One contact may have many aliases, and ambiguous aliases never select a contact automatically.
_Avoid_: username identity, biometric match

**Contact Association**:
The user-confirmed link between a Conversation Record and one Selected Contact, established before or during the conversation and correctable by the user.
_Avoid_: automatic identity, face match, inferred ownership

**Contact Merge**:
The user-confirmed consolidation of two contact records that represent the same person. One contact survives and receives the other's aliases, Conversation Records, and memory history; similar memories remain separate until reviewed.
_Avoid_: alias match, automatic deduplication, memory merge

**Contact Reassignment**:
The user-confirmed correction that moves a Conversation Record to a different contact. Derived memories are reviewed rather than silently transferred, and extraction reruns for the corrected contact.
_Avoid_: contact merge, automatic memory transfer

**Conversation Turn**:
A bounded spoken or written contribution attributed either to the user or the selected contact.
_Avoid_: audio chunk, message blob

**Conversation Record**:
A locally retained sequence of normalized Conversation Turns from one confirmed text import or Assisted Call, associated with a Selected Contact and kept as memory provenance until the user deletes it. It contains no raw audio or video.
_Avoid_: recording, raw call archive, conversation memory

**Unassigned Conversation**:
A retained Conversation Record whose contact has not yet been confirmed. It cannot retrieve or produce contact memory until the user associates it with an existing or newly created contact.
_Avoid_: unknown contact, guessed contact, anonymous memory

**Temporal Reference**:
A date or time expression retained with its original wording, source time zone, and a normalized instant or interval only when the context supports one. Windows local time is the default; explicit contact/location context may override it, while ambiguity remains unresolved.
_Avoid_: guessed date, silent time-zone conversion

**Speaker Role**:
The attribution of a Conversation Turn to the user, the selected contact, or unclear when attribution is not reliable.
_Avoid_: detected speaker identity, assumed sender

**Remote Face Region**:
The single visible area believed to contain the selected contact's face, normally initialized from the largest face in the Selected Call Window and correctable by the user. Other visible faces, including the user's self-preview, are not analysis subjects.
_Avoid_: face identity, biometric profile

**Remote Face Selection**:
The user's temporary choice of which visible face belongs to the other participant in the current Assisted Call. It assigns an analysis role only and does not name, recognize, or remember a person.
_Avoid_: facial identity, biometric recognition, remembered face

**Facial Signal**:
A local, time-bounded measurement of visible geometry or movement from the Remote Face Region before any interpretation.
_Avoid_: detected emotion, facial truth, self-analysis

**Vocal Signal**:
A local, time-bounded measurement of vocal behavior, such as relative energy, speaking rate, pauses, or overlap, derived from in-memory audio before any interpretation.
_Avoid_: voice emotion, emotion score, vocal truth

**Observation**:
A time-bounded piece of visible, vocal, or linguistic information produced during an assisted call before interpretation.
_Avoid_: emotion, conclusion

**Visible Expression**:
A time-bounded visible facial configuration of the selected contact, including smile-like mouth corners, lowered brows or lowered mouth corners. These configurations may occur separately or together without establishing an inner emotion or social meaning.
_Avoid_: detected feeling, frown emotion, emotional truth

**Observation Confidence**:
The strength of support that a visible configuration was actually observable during the stated interval. It is separate from confidence in any emotional or conversational interpretation of that configuration.
_Avoid_: emotion probability, certainty of meaning, movement amount

**Tone Hypothesis**:
A cautious possible description of the recent conversation atmosphere using the controlled F04 kinds positive/warm, neutral/calm, sad/low-energy, tense/negative, energetic/high-energy, or emotionally intense.
_Avoid_: detected emotion, emotional truth

**Conversation Atmosphere**:
A cautious description of the recent exchange supported by the remote participant's words and local vocal/visual observations, with the user's words used only as context. It is not an interpretation of the user's emotion or social cues.
_Avoid_: both people's emotion, user analysis, shared emotional truth

**Social Cue**:
A possible conversational meaning or change in engagement supported by current observations and context.
_Avoid_: intent, diagnosis, proof

**Interpretation Update**:
A stable current result containing up to three Tone Hypotheses and three Social Cues, or an explicit abstention when evidence is insufficient or conflicting.
_Avoid_: emotion verdict, analysis feed, card refresh

**Interpretation Status**:
The outcome of an interpretation attempt: updated, insufficient evidence, or conflicting evidence. It is separate from an individual hypothesis or cue's Confidence Level.
_Avoid_: confidence, emotion state, system error

**Evidence**:
The observable words, vocal behavior, facial movement, or eligible reviewed context supporting an interpretation, suggestion, summary statement, or Ask Memory answer.
_Avoid_: certainty, proof

**Confidence Level**:
The qualitative strength of support for an interpretation, guidance item, summary statement, or Ask Memory answer: low, medium, or high. Insufficient or conflicting evidence describes an outcome rather than another confidence level.
_Avoid_: certainty percentage, probability

**Live Guidance**:
The limited set of current tone hypotheses, cues, replies, reminders, and follow-up questions offered during an assisted call.
_Avoid_: dashboard feed, instruction

**Ask Memory**:
The user's question-and-answer experience over Approved Memories and Approved Summaries, including short follow-up questions about an explicitly identified contact or event. Each answer rests on current eligible evidence rather than previous generated answers.
_Avoid_: general chatbot, automatic contact inference, answer history as evidence

**Summary Draft**:
A generated account of a Conversation Record awaiting the user's review. It is not approved evidence for Ask Memory and does not approve any Memory Proposal.
_Avoid_: approved memory, searchable history, automatic approval

**Approved Summary**:
A summary the user has explicitly reviewed and approved, distinct from its separately reviewed Atomic Memories. Only its current eligible statements can support Ask Memory answers.
_Avoid_: approved memory, unreviewed summary, automatic fact approval

**Summary Statement**:
An individually supported part of a conversation summary that can be reviewed, corrected, retained as history, or removed. A suggested follow-up is distinguished from a factual statement or actual commitment.
_Avoid_: atomic memory, unqualified fact, inferred agreement

**Prior Statement**:
A summary statement the user chose to keep after related information was corrected, labeled with its original date and linked correction. It records earlier wording or plans without claiming they remain current.
_Avoid_: current fact, restored superseded memory, hidden correction

**Ask Scope**:
The contact or explicit all-contact discovery context chosen for Ask Memory. Changing it does not change the contact assigned to an Assisted Call.
_Avoid_: call reassignment, inferred identity, global memory pool

**Conversation Memory**:
Long-lived, locally stored context associated with a selected contact and available across imported text and assisted calls.
_Avoid_: transcript archive, cloud profile

**Atomic Memory**:
One independently reviewable and correctable fact, preference, event, commitment, follow-up, shared reference, relationship preference, or communication-style observation. It may be connected to related Atomic Memories without combining their content or lifecycle.
_Avoid_: contact profile, compound summary, conversation dump

**Useful Memory**:
An Atomic Memory that is contact-specific, actionable, relationship-specific, or meaningfully useful in a later conversation. Generic human behavior, temporary small talk, and unsupported emotion or intention inferences are not Useful Memories.
_Avoid_: conversation summary, trivia dump, inferred personality

**Memory Type**:
The controlled category of an Atomic Memory: person, preference, event/date, commitment, follow-up, recurring topic, shared joke/reference, relationship preference, communication style, or other. The user may correct the category; custom category systems are outside F05.
_Avoid_: free-form tag hierarchy, personality category

**Memory Connection**:
A bounded link between related Atomic Memories, including an explicit supersession link. Shared provenance connects memories from the same source without turning the memory store into a general-purpose knowledge graph.
_Avoid_: inferred social graph, graph database edge

**Memory Proposal**:
A model-generated candidate addition, correction, supersession, or removal that requires user review before changing conversation memory. A memory explicitly created or corrected by the user does not need a second approval step.
_Avoid_: automatic memory, inferred fact

**Proposal Batch**:
A bounded group of Memory Proposals extracted after a confirmed text import or Assisted Call ends. It is reviewed as a stable set rather than updated continuously during the conversation.
_Avoid_: live memory feed, automatically approved analysis

**Approved Memory**:
A memory explicitly created or corrected by the user, or a Memory Proposal accepted or edited by the user, retained until corrected, superseded, or deleted.
_Avoid_: model belief, permanent truth

**Memory Confidence**:
The qualitative strength of support for a memory: low, medium, or high. Approval means the memory should be retained and does not automatically increase its confidence.
_Avoid_: certainty, approval status, probability

**Memory Relevance**:
The query-time fit between an Approved Memory and the current confirmed contact, words, dates, and conversational context. Relevance may change over time without changing the memory's lifecycle state or confidence.
_Avoid_: approval, memory confidence, automatic expiration

**Memory Match**:
A bounded Approved Memory candidate retrieved locally for the confirmed contact and current context. A match is not proof that the current words refer to that memory.
_Avoid_: selected truth, confirmed reference, cross-contact result

**Retrieval Ambiguity**:
The state in which multiple Memory Matches remain plausible after bounded retrieval and optional reranking. It produces low-confidence alternatives, a clarification request, or abstention rather than a silent choice.
_Avoid_: closest match, inferred certainty

**Sensitive Memory**:
A memory marked as sensitive by the model or user. It remains available to local search but is excluded from cloud requests unless the user explicitly permits bounded cloud use for that memory.
_Avoid_: hidden memory, automatically shared memory

**Superseded Memory**:
An approved memory kept as history but excluded from current guidance because newer approved information replaced it.
_Avoid_: deleted memory, current fact

**Memory Revision**:
One immutable version in the correction history of an Approved Memory. Correcting a memory creates a new approved revision and supersedes the previous one; deleting the memory erases the complete revision chain.
_Avoid_: in-place edit, duplicate memory

**Potential Duplicate**:
A Memory Proposal marked as similar to one or more Approved Memories or proposals in the same review batch. It remains available for user review and is never automatically discarded or merged.
_Avoid_: confirmed duplicate, suppressed proposal

**Likely Generic Proposal**:
A supported concrete contact detail that may be too routine or one-off to be useful later. It remains a normal pending proposal, is grouped and visibly flagged for easy rejection, and never becomes an Approved Memory automatically.
_Avoid_: discarded fact, automatically rejected memory, low-confidence fact

**Rejected Proposal**:
A Memory Proposal the user declined. It remains only in local review history, never participates in retrieval or guidance, and may be reopened or permanently deleted.
_Avoid_: deleted memory, negative evidence, approved memory

**Deleted Memory**:
A memory whose content, evidence, and search derivatives have been erased at the user's request. A content-free identifier and deletion time may remain to prevent accidental restoration; deleting the contact removes that tombstone too.
_Avoid_: archived memory, hidden memory, soft-deleted content

**Interaction Style**:
The reviewed pattern of how the user and a particular contact communicate with each other, used to tailor suggestions for that relationship.
_Avoid_: user personality, global writing style

**Feature Plan**:
The implementation agreement for one feature, created immediately before that feature begins and bounded by the master plan.
_Avoid_: master roadmap, speculative design

**Feature Column**:
The permanent Trello column containing the planning, implementation, validation, review, and correction work for one feature.
_Avoid_: temporary status column, sprint

**Claude Review Gate**:
The independent QA and code-review checkpoints before user testing and after user testing and corrections, both required before a code feature is complete.
_Avoid_: optional review, final polish

## Roadmap priority — 15 September 2026

F07 remains active with its existing acceptance gates. The user narrowed F08 to easy Windows installation and Claude review, including necessary clean-install/startup checks, corrections and reviewed publication. Final presentation/demo preparation and a recorded fallback are deferred, not completion gates. F09 macOS implementation follows immediately after the reduced F08 so the user can test on their MacBook; do not wait until October 1 or for a polished demo. Keep one implementation feature active at a time. October 1 remains the Windows installation delivery target; no Mac completion date is committed. See PLAN.md for the current F08/F09 scope; older demo dependencies are superseded.

## F07 working state — 14 September 2026

Latest user sequence: evaluate before live checks, then again afterward. First full provisional comparison completed **144 independent Luna-low responses / 143 validated**, with **279 offline tests passed**. Aggregate committed spend is **$0.07768505 of $0.30**, leaving **$0.22231495**, including the preserved interrupted fixture attempt and its unresolved reservation. No new cap. Opus-5-only tool-disabled correction review cleared the harness; production preliminary review remains clear for P1. Boundary/attribution failures and visual-only cost excess prevent release acceptance. P1/P2/P3, permitted corrections, after-human comparison and final review/publication are pending. Exposed families used for changes become regression cases; a rerun does not restore holdout status. Details in [F07 validation](docs/F07-VALIDATION.md). The paragraph below records the earlier tuning checkpoint.

The approved F07 plan is being implemented. A persistent-expression/shared-calibration candidate exists, with frozen unchanged-production source and private DISFA/API evidence. Luna low remains selected. User authorized real API evaluation with a new **$0.30 aggregate cap**; $0.010754 has been consumed, and every later test/live reservation must carry that spend forward. One tuning round has run; final held-out comparisons and human results are pending. No release or F07 completion is claimed. See [F07 validation](docs/F07-VALIDATION.md) for the candidate's poor mouth-corner recall, rejected extraction prompt, verified Opus review findings/corrections and current test evidence. Keep final 144 comparisons/two repeats and all deadlines/gates unchanged.

## F06 closure — user accepted 14 September 2026

F06 is **complete for now by explicit user acceptance**. After reviewing the remaining Luna-quality limitations, the user instructed: “consider everything done for now”, commit/push, and update the plan. This supersedes pending closure requirements for another final Luna live call and another final Opus review; neither is reported as passed. Earlier manual calls and preliminary Opus reviews remain historical evidence. The latest independent review was Claude Sonnet 5, with two confirmed code findings fixed and covered by tests.

Current configuration: Luna low for live guidance, manual interpretation, Ask Memory and post-call review. 270 automated tests pass. Completed comparison: 258 historical agent answers (226 distinct requests plus32 exact reuses),12 new agent answers,6 changed-prompt agent checks, and24 new Luna API calls costing an estimated $0.02118703. Existing API results were reused. Local-model experiments are set aside, with results preserved.

Known accepted limitations: occasional ambiguous job reminders, overreading a verbal boundary as discomfort, and uncertain attribution/meaning from garbled speech. These remain evaluation/calibration work for F07; no claim of perfect memory recall or agent/API equivalence. F07, including planned facial-expression improvements, is next but has not started. No F07 implementation is authorized by this closure.

Evidence: [completed checks and review dispositions](docs/F06-AGENT-API-EXPANDED.md), [test index](docs/TESTING.md). Private raw logs, databases and archives remain Git-ignored; future devices need a private archive transfer. Exact publication SHA and verified main pointers are recorded on the existing Trello release/roadmap cards to avoid a self-referential commit hash.

