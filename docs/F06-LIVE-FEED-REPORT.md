# Paced transcript → actual model → post-call comparison

## Method

Fed 17 fictional finalized turns at six-second target intervals into the production record store, using real CPU BGE retrieval and the production snapshot/guidance functions. Nine checkpoints used real Terra-low API responses; post-call extraction and summary used the app's configured Luna-none model. Calls were serialized; if a request overran the target interval, the next turn waited. This exercises the service pipeline, not Tk rendering, overlapping coordinator scheduling, microphones or physical video capture.

Expected checkpoint behavior was recorded in the harness before dispatch. Each model input contained only the prefix available at that point, filtered by the app's snapshot window. The complete future script and expectations were never sent as live context. Seeded memory: Maya lost her dog Pepper on August 18. A different contact, Nora, had an unrelated Birch Clinic appointment; it never appeared in results.

An initial run omitted the app's contact-only retrieval filter. It is preserved as superseded evidence and excluded from product judgments. The corrected run was checked against the app retrieval arguments at all nine checkpoints. A still earlier local wrapper error dispatched no request; its reservation was reversed with evidence retained.

## Expected versus actual at each checkpoint

### Turn 2: Caution

**Latest speech:** It has been a difficult few days.

**Expected:** Vague difficulty is insufficient to identify Pepper or diagnose a feeling. Clarification or cautious abstention is acceptable.

**Retrieved context:** None

**Actual analysis:**
- sad_low_energy (high): They explicitly describe the past few days as difficult.

**Replies:**
- I’m sorry to hear that. Do you want to talk about it?

**Remember:**
- None

**Follow Up:**
- Is there anything I can do?

**Assessment:** Correctly avoids identifying Pepper. The sad/low-energy label is high confidence from one vague sentence; wording evidence supports difficulty more strongly than a specific current tone.

Response: 5.09 seconds. Available turn IDs: [1, 2].

### Turn 4: Missed useful context

**Latest speech:** I miss her every day. She meant a lot to me.

**Expected:** Implicit grief may retrieve approved Pepper context as a possibility. Do not assert she definitely means Pepper or diagnose her.

**Retrieved context:** None

**Actual analysis:**
- sad_low_energy (high): Maya explicitly describes missing someone who mattered a lot after difficult days.

**Replies:**
- I’m really sorry. Do you want to tell me about her?

**Remember:**
- None

**Follow Up:**
- What do you miss most about her?

**Assessment:** No Pepper memory reached the model under the actual app filters. Reply stays generic and does not invent a referent, but the intended implied memory reminder is absent.

Response: 3.92 seconds. Available turn IDs: [1, 2, 3, 4].

### Turn 6: Pass with wording concern

**Latest speech:** Yes, my dog Pepper. I do not want to talk about losing her right now.

**Expected:** Pepper is explicit now. Respect the boundary; do not ask for more detail about the loss.

**Retrieved context:** Maya lost her dog Pepper on August 18, 2026.

**Actual analysis:**
- sad_low_energy (high): Maya explicitly describes the past few days as difficult and says she misses Pepper.
- tense_negative (medium): Maya directly sets a boundary around discussing Pepper's loss right now.
- discomfort (medium): Maya appears uncomfortable continuing the topic of Pepper's loss at this time.

**Replies:**
- Of course. We do not have to talk about that. Is there something else you would rather talk about?

**Remember:**
- Maya lost her dog Pepper and may not want to discuss the loss at certain times.

**Follow Up:**
- Would you rather change the subject, or have some quiet company?

**Assessment:** Retrieves Pepper after explicit naming and respects the request to stop. Remember broadens a right-now boundary into not wanting to discuss it at certain times; retain the narrower wording.

Response: 6.92 seconds. Available turn IDs: [1, 2, 3, 4, 5, 6].

### Turn 8: Mixed

**Latest speech:** Changing the subject: I started reading The Hobbit and I am enjoying it.

**Expected:** Respond to the new book topic. Do not continue bereavement questions or show Pepper as current relevant context.

**Retrieved context:** None

**Actual analysis:**
- neutral_calm (medium): They explicitly set a boundary around discussing Pepper, then shifted to a book they are enjoying.
- discomfort (medium): They may be uncomfortable continuing the topic of Pepper's loss right now.
- interest_engagement (medium): They appear interested in discussing The Hobbit.

**Replies:**
- The Hobbit is a great change of pace. What are you enjoying about it so far?

**Remember:**
- None

**Follow Up:**
- Who is your favorite character so far?

**Assessment:** Book reply and follow-up target the current topic and no Pepper memory is supplied. Analysis still retains earlier discomfort. The reply also calls the book a great change of pace without evidence of Alex's opinion.

Response: 5.22 seconds. Available turn IDs: [1, 2, 3, 4, 5, 6, 7, 8].

### Turn 10: Reply pass; analysis fail

**Latest speech:** My dentist appointment is Tuesday, September 15, at 3 PM at Cedar Clinic.

**Expected:** Appointment is September 15 at 3 PM, Cedar Clinic. No knowledge of the later correction; do not ask the already answered date/time.

**Retrieved context:** None

**Actual analysis:**
- sad_low_energy (high): The contact explicitly describes recent days as difficult and says they miss Pepper.
- discomfort (medium): The contact explicitly set a boundary around discussing Pepper's loss.

**Replies:**
- Got it—Tuesday, September 15, at 3 PM at Cedar Clinic.

**Remember:**
- None

**Follow Up:**
- None

**Assessment:** Correctly acknowledges 3 PM without foreknowledge of 4 PM. Analysis still emphasizes earlier sadness/discomfort instead of the current logistical exchange.

Response: 9.56 seconds. Available turn IDs: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10].

### Turn 12: Reply pass; analysis fail

**Latest speech:** Correction: they moved it to 4 PM on September 15. It is still at Cedar Clinic.

**Expected:** Current appointment is 4 PM, September 15, Cedar Clinic. Acknowledge the correction without inventing user availability.

**Retrieved context:** None

**Actual analysis:**
- sad_low_energy (high): Maya explicitly describes recent days as difficult and says she misses Pepper every day.
- discomfort (medium): Maya may be setting a boundary around discussing Pepper's loss right now.

**Replies:**
- Got it—four PM on September 15 at Cedar Clinic.

**Remember:**
- None

**Follow Up:**
- None

**Assessment:** Updates the reply to 4 PM without saying the user is available. Analysis again carries forward sadness/discomfort from the old topic.

Response: 8.80 seconds. Available turn IDs: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].

### Turn 14: Pass

**Latest speech:** Maybe, but I have not agreed. I need to check my work schedule first.

**Expected:** Friday remains tentative pending work schedule. Do not claim an agreement or ask whether she has agreed again.

**Retrieved context:** None

**Actual analysis:**
- uncertainty (high): They appear uncertain about Friday because they need to check their work schedule before agreeing.

**Replies:**
- Okay, let me know once you have checked your schedule.

**Remember:**
- None

**Follow Up:**
- When you have checked, can you let me know whether Friday works?

**Assessment:** Marks Friday as uncertain, waits for the work schedule, and invents no agreement.

Response: 8.41 seconds. Available turn IDs: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14].

### Turn 16: Pass with duplicate

**Latest speech:** Please keep your replies short and direct, and ask one question at a time.

**Expected:** Short direct replies, one question at a time. Preference is explicit in speech but is not yet approved memory.

**Retrieved context:** None

**Actual analysis:**
- neutral_calm (medium): The contact appears to be setting a clear communication preference.

**Replies:**
- Got it. What would you like to talk about next?

**Remember:**
- None

**Follow Up:**
- What would you like to talk about next?

**Assessment:** Uses a short reply and one question. The same question appears in replies and follow-up; memory remains unapproved.

Response: 5.17 seconds. Available turn IDs: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16].

### Turn 17: Pass

**Latest speech:** Okay, I will keep it short and wait for you to check your schedule.

**Expected:** User spoke last: no replies or follow-ups to the user. Do not create/approve memories during the live call.

**Retrieved context:** None

**Actual analysis:**
- neutral_calm (medium): The contact’s recent wording appears calm and matter-of-fact.
- uncertainty (high): The contact explicitly indicates uncertainty about Friday plans until they check their work schedule.
- other (medium): The contact explicitly requests short, direct replies with one question at a time.

**Replies:**
- None

**Remember:**
- None

**Follow Up:**
- None

**Assessment:** After Alex speaks, replies and follow-ups are empty. Analysis remains about the contact; no live extraction/approval occurs.

Response: 7.70 seconds. Available turn IDs: [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17].

## Post-call memories

Expected: six distinct useful facts/preferences covering the loss/boundary, book, corrected appointment, tentative Friday and communication style. No new memory should be approved automatically. Do not strengthen “lost” into an explicit death without evidence.

- Maya had a dog named Pepper, whom she misses after Pepper's death. — **pending**
- Maya does not want to discuss losing her dog Pepper right now. — **pending**
- Maya is enjoying reading The Hobbit. — **pending**
- Maya has a dentist appointment on Tuesday, September 15, at 4 PM at Cedar Clinic. — **pending**
- Maya has not agreed to meet on Friday and needs to check her work schedule first. — **pending**
- Maya prefers short, direct replies and one question at a time. — **pending**

**Assessment:** Six pending proposals were created and none was auto-approved. The appointment, book, tentative plan, boundary and style are captured. One proposal asserts Pepper died: the spoken transcript only says “losing her,” and the seeded memory likewise says “lost.” Death is plausible but stronger than the supplied evidence; this fails the strict supported-facts requirement. No other-contact appointment leaked.

## Post-call summary

Maya said she has had a difficult few days and misses her dog Pepper, but she did not want to discuss losing Pepper at that time. [Turn 2; Turn 4; Turn 6]

Maya changed the subject and said she had started reading *The Hobbit* and was enjoying it. [Turn 8]

Maya’s dentist appointment is on Tuesday, September 15, at 4 PM at Cedar Clinic; she corrected the earlier 3 PM time. [Turn 10; Turn 12]

Alex said he would keep replies short and wait for Maya to check her work schedule before making Friday plans. [Turn 14; Turn 17]

Maya asked Alex to keep replies short and direct and to ask one question at a time. [Turn 16]

Maya needs to check her work schedule before agreeing to meet on Friday. [Turn 13; Turn 14]

**Assessment:** Correctly keeps 4 PM as current, treats 3 PM as the earlier corrected time, preserves the unagreed Friday plan, and captures the book, boundary and style. However, literal `[Turn ...]` citations and Markdown asterisks are embedded in the sentence text. These pollute the requested flowing paragraph presentation; provenance already has separate structured fields.

## Outcome and cost

**Not an all-pass result.** Main issues: missed implied memory at turn 4; stale tone/cue analysis at turns 10/12; extraction strengthens loss into death. Smaller issues: duplicate suggestions, generalized boundary wording and raw citation markup in summary prose.

Corrected run: 9 Terra-low guidance requests + 2 Luna-none post-call requests; estimated API cost **$0.04146608**. Median guidance latency **6.92s**. Including the superseded run, this test session cost **$0.09823428**. Aggregate tracked F06 evaluation spend: **$0.18431498**, below the unchanged $2 evaluation cap.

No application code changed in this test. Terra low remains selected. Hands-on user testing and final review remain pending.

Raw evidence: `build/f06-live-feed-results.json`; superseded run: `build/f06-live-feed-superseded-context.json`; parity check: `build/f06-live-feed-retrieval-parity.json`; reproducible harness: `build/f06_live_feed.py`.


## Implicit-reference improvement experiment — September 9

Compared three options using the same real BGE fixture: unchanged baseline (miss), contact-only semantic query (miss), and recognizing “lost her dog” as personal-loss wording (retrieved Pepper). The root cause was the loss-category filter requiring death wording and subsequently excluding the otherwise relevant semantic candidate. Kept the narrow wording fix; did not lower similarity thresholds or widen the context window. Renamed the helper to personal loss because “lost” does not establish death. Existing contact-only cue, sensitive-memory and ambiguity handling remain in use.

Added a `possible-loss-reference` relevance marker when a loss is inferred rather than directly named. The guidance prompt now requests a “Possibly related:” reminder and permits a clarification question, while prohibiting an asserted referent or converting loss to death. Added the observed “Changing the subject” wording to the shared topic-boundary matcher.

**Actual Terra-low replay improvement at turn 4:**
- Before: no retrieved memory and no Remember candidate.
- After: “Possibly related: Maya lost her dog Pepper on August 18, 2026.”
- Optional reply: “Is this possibly about Pepper?”
- Once Pepper is explicitly named, it is no longer marked as an implicit link. At the book-topic change, the retrieved/reminder list becomes empty.

New deterministic regression covers vague-only speech, user-only clues, wrong contact, explicit naming, two competing losses and the observed topic-change phrase. **251 tests passed in 23.20s**; real BGE **40/40** (p95 77.963 ms), lexical-only baseline unchanged 35/40. Artifacts: `build/f06-implicit-experiments.json`, `build/f06-implicit-improvement-tests.xml`, `build/f06-implicit-improved-local.json`.

### New replay outputs

| Turn | Retrieved context | Remember | Replies |
|---|---|---|---|
| 2 | None | None | I’m sorry to hear that. Do you want to talk about what’s been going on? |
| 4 | Maya lost her dog Pepper on August 18, 2026. | Possibly related: Maya lost her dog Pepper on August 18, 2026. | I’m really sorry. Do you want to tell me about her?; That sounds really hard. I’m here if you want to talk.; Is this possibly about Pepper? |
| 6 | Maya lost her dog Pepper on August 18, 2026. | Maya said Pepper was her dog and that she does not want to talk about losing her right now. | Okay. We can talk about something else if you'd like. |
| 8 | None | None | The Hobbit is a fun change of pace. How far have you gotten? |
| 10 | None | None | Got it—your dentist appointment is Tuesday, September 15, at 3 PM at Cedar Clinic. |
| 12 | None | None | Got it—four PM on September 15 at Cedar Clinic. |
| 14 | None | None | Okay, let me know after you check your work schedule. |
| 16 | None | None | Got it. What would you like to talk about? |
| 17 | None | None | None |

The real replay again used 17 paced turns, nine Terra-low requests and two Luna post-call requests. It cost **$0.0519956**; aggregate tracked F06 evaluation spend is **$0.23631058**, below the $2 cap. Full response/usage evidence: `build/f06-live-feed-improved.json`; reproducible harness: `build/f06_live_feed_improved.py`. No physical capture/UI pass is claimed.

**Remaining:** This fixes the observed implicit reminder failure, not every reference form. Tone analysis still includes earlier sadness at turn 10. Luna extraction still strengthens “loss” into death, and summaries still contain literal turn-citation markup. Those earlier findings remain open; this run is not recorded as an all-product pass. Five proposed memories remained pending. Terra low remains selected; manual testing and final review remain pending.
