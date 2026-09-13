# Memory creation audit: September 13 real call

I read all 88 finalized, attributed turns in `build/live-test-20260913-121412/events.jsonl`, then compared them with the two proposals in `build/visible-replay-20260913-130947/review-output.json`. These are human-reviewed candidate drafts, not new approved records or model-test results.

## Candidate memories

| Candidate wording | Evidence | Assessment |
|---|---|---|
| Yaheli said things had been rough lately, particularly financially. | 2–5 | Keep the existing financial memory. “A few days” is fragmented; do not invent an exact start date, employer or job loss. |
| Eden had corrected the project's regulation reference; Yaheli clarified that the relevant law was the EU Cyber Resilience Act rather than the EU AI Act. | 28, 30, 48, 52 | Enrich the existing regulation memory with who raised the correction. Linking Eden to that correction uses context across the two discussions; review that link rather than treating it as a verbatim quotation. |
| You expressed disappointment about the project landing page while discussing its regulation wording with Yaheli. | 48, 50, 52, 54, 55 | Useful shared-project feedback, explicitly attributed to You. The transcript does not justify asserting that Yaheli felt disappointed, or that the displayed page was objectively legally wrong. |
| You told Yaheli you would make the app's model selection changeable while discussing Terra and Luna. | 83, 85–87 | A concrete user commitment relevant to the shared project. Medium confidence: “make it so that you can change it” relies on the immediately preceding model discussion to resolve “it.” Do not invent a deadline or promise a specific pricing outcome. |

This is a target of roughly four useful memories, not a quota. The first two preserve/enrich existing proposals; the latter two broaden coverage to a shared discussion and a user commitment. A model may reasonably phrase or group them differently.

## What I would omit

- Turns 1, 21, 26: routine check-ins/questions; save the concrete answer or resulting issue instead.
- Turns 8, 44–45, 58, 76, 78: the user reading or discussing generated app guidance. In particular, turn 58 is not independent evidence that the contact was disappointed.
- Turns 12–20: testing whether a stored job memory appears. This does not newly establish a job loss or McDonald's employment.
- Turns 37–41 and 61: transient tracking/guidance failures, unless separately recorded as product issues; not contact life events.
- Turn 57, “Hopefully she will be good dude”: the identity of “she” and the meaning of “good” remain unresolved. Eden was mentioned earlier, but that does not establish the referent. No invented person, gender, role, health event or forecast.
- Turns 59–60: a nonspecific intention to test with a memory; less useful as lasting contact context than the concrete model-choice commitment.
- Turns 65–77: general speculation that improving models will improve the app. Summary material rather than a durable fact about Yaheli.
- Turns 79–85: uncertain quoted cost estimates and the user's model-cost comparison. Do not persist the guessed call cost as measured usage.

The logged speaker labels are evidence labels, not a verification of the original audio. Similar wording appears on both channels in a few places; the transcript alone cannot settle whether this was repetition or capture/transcription attribution error. The user's factual correction should take precedence during review.

## Why current extraction likely misses these

The extractor already uses the raw transcript independently of the summary. The current problem is therefore not summary compression.

The prompt repeatedly narrows eligibility to “contact-specific facts” and “actual contact facts.” It allows substantive project facts but heavily discourages testing observations. This likely suppresses specific shared-project criticism and commitments made by the user, even when they are useful future conversation context. This is a hypothesis from the wording and observed omissions, not a demonstrated model-internal cause.

Extraction also uses non-overlapping chunks of at most 20 finalized turns: 1–20, 21–40, 41–60, 61–80, 81–88. Many turns are tiny fragments. The regulation correction at 28–30 and Eden's role at 48 are separated. However, the landing-page discussion and disappointment are already together in 41–60, so chunking alone does not explain their omission.

The speech text is approximately 1,112 estimated tokens. With the current repeated per-turn metadata, instructions and schema, an all-88-turn extraction request is estimated at 6,502 tokens, above the existing 6,000-token ceiling. Simply removing the turn limit would not make that whole request fit.

## Recommended next experiment

1. Expand the extraction definition: contact facts, specific shared-project evaluations, and explicit user/contact commitments relevant to that relationship. Always identify whose experience, opinion or commitment it is. Routine questions, generated quotations and transient glitches stay excluded.
2. Preserve one self-contained fact plus its useful qualifiers: who, what, project/person identity, reasons and explicitly stated dates. Do not add contrasts with other stored memories for retrieval. Real corrections, such as changing a regulation reference, remain meaningful content.
3. Replace the arbitrary 20-fragment split with token-budgeted groups that retain adjacent context. Store stable speaker/date metadata once in the payload; keep source turn IDs. For long calls, use a small overlap and deduplicate proposals by shared evidence. Count the complete request against the budget, not just speech text.
4. Before returning proposals, have the same extraction request check whether it missed any specific opinion, commitment or named-person/project detail, and whether every proposal has correct speaker ownership. No extra paid “reviewer” request by default; no minimum number of memories.
5. Compare the current prompt with the broader prompt on these same frozen inputs, then compare chunking separately. Score coverage of the candidate facts above, correct attribution, specificity, unsupported claims and cost. Include negative controls from the omitted turns so recall does not improve by restoring low-value or fictional memories.

Luna Ask search remains unchanged. A better embedding model would not recover a detail that was never extracted and approved in the first place. F07 facial work is unrelated to this extraction fix.

## Search fixture revision and fresh test

Removed the celebration's “not the earlier photography win” phrase from both its source dialogue and memory. Also removed the cabin memory/dialogue's explicit comparison with the previous camping trip. The independent event names, event dates and source-call dates remain.

All 15 real Luna-low questions were rerun by the agent. Expected answer/clarification statuses: 15/15; returned source IDs valid in every case. Newer/older losses, awards, trips and health appointments still resolved as intended. The vague loss and appointment questions still requested clarification.

Two small quality observations: the rejection-remedy answer was factually correct but omitted the rejection-reason memory from its citations (it cited the project plan and progress); the distraction answer added the tentative suggestion that the bakery project could help channel energy, which was not an explicitly remembered coping benefit. These did not confuse the events, but source-ID validity alone does not establish complete claim-level citation coverage.

Fresh test cost: $0.01043070, about one cent. Aggregate OpenAI evaluation spend: $3.42618378, below the authorized $4 cap. Eight affected automated Ask tests passed. Raw requests and answers: `build/ask-history-20260913/agnostic-results.json`. Revised isolated fixture: `build/ask-history-20260913/memory-agnostic.sqlite3`.

Event dates and source-call dates serve different purposes. A memory saved today may describe a much older event; creation time alone must not make that event “the latest.” Missing or ambiguous dates should lead to a qualified answer or clarification.
