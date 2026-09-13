# Varied implicit-memory test — September 9

## Setup

Five fresh approved memories were embedded with the existing real BGE model in an isolated database: losing a McDonald's job, mother Ruth's death, a photography prize, voluntarily leaving Oak Cafe with relief, and chemistry/mathematics exam stress. All five belonged to one contact so competing topics could interfere. Another contact held an unrelated memory for isolation. These were newly inserted approved facts, not memorized prompts or model-generated extraction in this run.

Five scripted conversations each fed eight finalized turns at six-second target intervals. Each had a vague opening (local retrieval only), an indirect clue, a stronger indirect clue, and a book-topic change. Fifteen actual Terra-low calls consumed only the current transcript prefix and the production-filtered memory context. Expected behavior was written in the fixture before calls. No new topic-specific retrieval rules or lower similarity thresholds were introduced for these cases. The guidance wording was adjusted to prefer natural support over asking “Is this about …?”, reflecting the user's preference.

## Results

**All five scenarios eventually produced the relevant model memory reminder.** The target appeared among retrieved candidates at 10/10 indirect-clue checkpoints; a model reminder appeared at 9/10. At the first quitting clue, an unrelated exam memory caused ambiguity and all memory context was withheld. The stronger clue resolved it. This is a small authored test set, not a general accuracy guarantee.

| Situation | Expected behavior | Observed result |
|---|---|---|
| job_loss | Support involuntary job loss and financial worry. Do not congratulate her for choosing to quit or name the employer without confirmation. | Correct layoff reminder at both clues; sympathetic replies, no confusion with voluntarily quitting. |
| loved_one | Offer gentle sympathy. A possible bereavement reminder is useful; do not ask if she means Ruth or claim the pronoun is confirmed. | Correct possible Ruth reminder; gentle sympathy without an identity-check question. |
| prize | Congratulate or share in the excitement; recall the photography prize as possible context without assuming the unspoken contest identity. | Correct prize reminder and congratulations. First reply redundantly asks which competition; stronger clue supports photography. |
| quit_relief | Acknowledge relief after voluntarily leaving stressful work. Do not treat this as being fired or worry about rent on her behalf. | First clue: retrieval ambiguity blocks the reminder, but reply recognizes relief. Stronger clue: correct reminder, no ready reply survives; a relevant follow-up remains. |
| exam_stress | Offer calm support for revision pressure; optionally suggest one manageable next step. Do not diagnose anxiety or guarantee exam results. | Correct exam reminder; supportive replies and manageable study suggestions. No diagnosis or guarantee. |

Tone/cue outputs broadly matched the stated contexts: low/distressed for the layoff, sadness for bereavement, positive tone for the prize and relief, and stress/uncertainty for exams. These were medium-confidence text-only hypotheses, not verified internal emotions.

All five explicit book-topic transitions returned zero retrieved memories and zero Remember candidates, with replies about the book. A separate real-BGE check with both mother and grandmother loss memories returned two ambiguous possibilities instead of choosing one (`build/f06-variety-ambiguity.json`).

**Remaining retrieval noise:** “week” alone pulled in the exam memory during two vague openings (prize and quitting). Several clue checkpoints included unrelated exam/work candidates. The model generally ignored those distractors, but the first quitting clue was blocked by a false ambiguity. The vague openings were not sent to Terra in this run; no claim is made that their model output would be harmless.

## Actual checkpoint outputs

### job_loss — through turn 2

**Expected:** No specific event is established.

**Retrieved:**
- None

**Ambiguous:** False

Local retrieval only; no model request at this vague opening.

### job_loss — through turn 4

**Expected:** Support involuntary job loss and financial worry. Do not congratulate her for choosing to quit or name the employer without confirmation.

**Retrieved:**
- Maya was laid off from her job at McDonald's on September 1, 2026, and is worried about paying rent. (lexical+semantic)
- Maya has chemistry and mathematics exams next week and is stressed about preparing for them. (semantic)
- Maya quit her job at Oak Cafe in June 2026 and felt relieved to leave a stressful manager. (semantic)

**Ambiguous:** False

**Analysis:**
- sad_low_energy (medium): They may be feeling low or distressed about losing work and rent pressure.

**Remember:**
- Possibly related: Maya was laid off from her job at McDonald's on September 1, 2026, and is worried about paying rent.

**Replies:**
- I’m sorry—you’ve got a lot to deal with. Is there anything I can do to help?

**Follow Up:**
- Have you had a chance to look into any support with rent yet?

### job_loss — through turn 6

**Expected:** Support involuntary job loss and financial worry. Do not congratulate her for choosing to quit or name the employer without confirmation.

**Retrieved:**
- Maya was laid off from her job at McDonald's on September 1, 2026, and is worried about paying rent. (semantic)
- Maya has chemistry and mathematics exams next week and is stressed about preparing for them. (semantic)
- Maya quit her job at Oak Cafe in June 2026 and felt relieved to leave a stressful manager. (semantic)

**Ambiguous:** False

**Analysis:**
- sad_low_energy (medium): They may be feeling low about losing their income and facing rent concerns.
- discomfort (medium): They may be under financial strain and seeking space to talk about it.

**Remember:**
- Possibly related: Maya was laid off from her job at McDonald's on September 1, 2026, and is worried about paying rent.

**Replies:**
- I’m sorry—you put in all those shifts, and now you’re having to worry about rent. Do you want to talk through what might help right now?
- That’s a lot to be hit with at once. Is there anything practical you need to sort out first?

**Follow Up:**
- Have you been able to find out what support or options are available for rent?

### job_loss — through turn 8

**Expected:** New book topic; do not carry old event reminders.

**Retrieved:**
- None

**Ambiguous:** False

**Analysis:**
- No tone/cue selected

**Remember:**
- None

**Replies:**
- What mystery novel are you reading?
- What are you enjoying about it so far?

**Follow Up:**
- Who is the author?

### loved_one — through turn 2

**Expected:** No specific event is established.

**Retrieved:**
- None

**Ambiguous:** False

Local retrieval only; no model request at this vague opening.

### loved_one — through turn 4

**Expected:** Offer gentle sympathy. A possible bereavement reminder is useful; do not ask if she means Ruth or claim the pronoun is confirmed.

**Retrieved:**
- Maya's mother Ruth died on August 20, 2026. (semantic+possible-loss-reference)

**Ambiguous:** False

**Analysis:**
- sad_low_energy (medium): They explicitly describe missing someone who mattered deeply.

**Remember:**
- Possibly related: Maya's mother Ruth died on August 20, 2026.

**Replies:**
- I’m so sorry. It sounds like she meant so much to you.
- I’m here with you if you want to talk about her.

**Follow Up:**
- What do you miss most about her?

### loved_one — through turn 6

**Expected:** Offer gentle sympathy. A possible bereavement reminder is useful; do not ask if she means Ruth or claim the pronoun is confirmed.

**Retrieved:**
- Maya's mother Ruth died on August 20, 2026. (semantic+possible-loss-reference)

**Ambiguous:** False

**Analysis:**
- sad_low_energy (medium): The contact may be expressing grief or sadness.

**Remember:**
- Possibly related: Maya's mother Ruth died on August 20, 2026.

**Replies:**
- That sounds really hard. I’m here with you.
- Do you want to tell me more about her?

**Follow Up:**
- What do you miss most about her?

### loved_one — through turn 8

**Expected:** New book topic; do not carry old event reminders.

**Retrieved:**
- None

**Ambiguous:** False

**Analysis:**
- positive_warm (medium): They explicitly say they are enjoying a new mystery novel.
- interest_engagement (medium): They may be open to discussing the novel after changing the subject.

**Remember:**
- None

**Replies:**
- What mystery novel are you reading?
- What are you enjoying about it so far?

**Follow Up:**
- Would you like to tell me what it is about?

### prize — through turn 2

**Expected:** No specific event is established.

**Retrieved:**
- Maya has chemistry and mathematics exams next week and is stressed about preparing for them. (lexical)

**Ambiguous:** False

Local retrieval only; no model request at this vague opening.

### prize — through turn 4

**Expected:** Congratulate or share in the excitement; recall the photography prize as possible context without assuming the unspoken contest identity.

**Retrieved:**
- Maya has chemistry and mathematics exams next week and is stressed about preparing for them. (semantic)
- Maya won first prize in a photography competition on September 5, 2026. (lexical)

**Ambiguous:** False

**Analysis:**
- positive_warm (medium): They may be excited and pleasantly surprised about coming first.
- interest_engagement (medium): They may be sharing news they are proud of.

**Remember:**
- Possibly related: Maya won first prize in a photography competition on September 5, 2026.

**Replies:**
- That’s amazing—congratulations! What was the competition?

**Follow Up:**
- What was the competition?

### prize — through turn 6

**Expected:** Congratulate or share in the excitement; recall the photography prize as possible context without assuming the unspoken contest identity.

**Retrieved:**
- Maya won first prize in a photography competition on September 5, 2026. (semantic)

**Ambiguous:** False

**Analysis:**
- positive_warm (medium): They may be feeling pleased and excited about the result.

**Remember:**
- Maya won first prize in a photography competition after putting significant effort into taking and selecting photos.

**Replies:**
- That is amazing—you earned it.
- What was the winning shot?

**Follow Up:**
- What was the winning shot?

### prize — through turn 8

**Expected:** New book topic; do not carry old event reminders.

**Retrieved:**
- None

**Ambiguous:** False

**Analysis:**
- positive_warm (medium): The contact explicitly says they are enjoying the new mystery novel.
- interest_engagement (medium): The contact may be offering the novel as a new topic after the subject change.

**Remember:**
- None

**Replies:**
- What is it about?
- What do you like about it so far?

**Follow Up:**
- Would you recommend it?

### quit_relief — through turn 2

**Expected:** No specific event is established.

**Retrieved:**
- Maya has chemistry and mathematics exams next week and is stressed about preparing for them. (lexical)

**Ambiguous:** False

Local retrieval only; no model request at this vague opening.

### quit_relief — through turn 4

**Expected:** Acknowledge relief after voluntarily leaving stressful work. Do not treat this as being fired or worry about rent on her behalf.

**Retrieved:**
- Maya has chemistry and mathematics exams next week and is stressed about preparing for them. (semantic)
- Maya quit her job at Oak Cafe in June 2026 and felt relieved to leave a stressful manager. (semantic)

**Ambiguous:** True

**Analysis:**
- positive_warm (medium): They explicitly describe relief about handing in their notice.

**Remember:**
- None

**Replies:**
- That sounds like a huge relief. What made it feel like the right time?

**Follow Up:**
- What are you thinking of doing next?

### quit_relief — through turn 6

**Expected:** Acknowledge relief after voluntarily leaving stressful work. Do not treat this as being fired or worry about rent on her behalf.

**Retrieved:**
- Maya quit her job at Oak Cafe in June 2026 and felt relieved to leave a stressful manager. (lexical+semantic)
- Maya has chemistry and mathematics exams next week and is stressed about preparing for them. (semantic)
- Maya was laid off from her job at McDonald's on September 1, 2026, and is worried about paying rent. (semantic)

**Ambiguous:** False

**Analysis:**
- positive_warm (medium): They explicitly say they feel relieved after choosing to leave their job.

**Remember:**
- Possibly related: Maya quit her job at Oak Cafe in June 2026 and felt relieved to leave a stressful manager.

**Replies:**
- None

**Follow Up:**
- What are you looking forward to most now that you’ve left?

### quit_relief — through turn 8

**Expected:** New book topic; do not carry old event reminders.

**Retrieved:**
- None

**Ambiguous:** False

**Analysis:**
- positive_warm (medium): The contact explicitly says they feel relieved about leaving their job.
- interest_engagement (medium): The contact appears to redirect the conversation toward a new interest after the subject change.

**Remember:**
- None

**Replies:**
- What mystery novel are you reading?

**Follow Up:**
- What are you enjoying about it so far?

### exam_stress — through turn 2

**Expected:** No specific event is established.

**Retrieved:**
- None

**Ambiguous:** False

Local retrieval only; no model request at this vague opening.

### exam_stress — through turn 4

**Expected:** Offer calm support for revision pressure; optionally suggest one manageable next step. Do not diagnose anxiety or guarantee exam results.

**Retrieved:**
- Maya has chemistry and mathematics exams next week and is stressed about preparing for them. (semantic)
- Maya quit her job at Oak Cafe in June 2026 and felt relieved to leave a stressful manager. (semantic)

**Ambiguous:** False

**Analysis:**
- tense_negative (medium): They explicitly describe feeling scared and overwhelmed about approaching exam dates and remaining revision.
- uncertainty (medium): They express worry about being unable to recall material during the exams.

**Remember:**
- Maya has chemistry and mathematics exams next week and is stressed about preparing for them.

**Replies:**
- That sounds really stressful. You have still got time to revise—what topic feels most daunting right now?
- I am sorry it is feeling so overwhelming. Would it help to break down what is left into smaller bits?

**Follow Up:**
- Which exam is coming up first?

### exam_stress — through turn 6

**Expected:** Offer calm support for revision pressure; optionally suggest one manageable next step. Do not diagnose anxiety or guarantee exam results.

**Retrieved:**
- Maya has chemistry and mathematics exams next week and is stressed about preparing for them. (semantic)
- Maya won first prize in a photography competition on September 5, 2026. (lexical)
- Maya quit her job at Oak Cafe in June 2026 and felt relieved to leave a stressful manager. (lexical)

**Ambiguous:** False

**Analysis:**
- tense_negative (medium): The contact explicitly describes feeling overwhelmed and scared about upcoming revision and exams.
- uncertainty (medium): The contact appears uncertain about how to prioritize their studying.

**Remember:**
- Maya has chemistry and mathematics exams next week and is stressed about preparing for them.

**Replies:**
- That is a lot to juggle. Would it help to pick one small topic to start with, then come back to the other?
- Maybe start with whichever exam is sooner, then make a short list for the other one?
- Do you want to talk through what is left for each subject and work out what to tackle first?

**Follow Up:**
- Which exam is first?
- What topics are still left for each subject?

### exam_stress — through turn 8

**Expected:** New book topic; do not carry old event reminders.

**Retrieved:**
- None

**Ambiguous:** False

**Analysis:**
- neutral_calm (medium): They explicitly say they are enjoying a new mystery novel.
- interest_engagement (medium): They may be engaging with the subject change by introducing a book they are enjoying.

**Remember:**
- None

**Replies:**
- Nice—what is it about?

**Follow Up:**
- What are you liking most about it so far?

## Evidence, cost and scope

15 Terra-low requests cost **$0.0741396 (7.41 cents)**. Aggregate recorded F06 evaluation spend is **$0.31045018**, below the $2 cap. No retries were requested. Relevant offline regressions: 20 passed in 1.46 seconds.

Fixture: `conversation_copilot/assets/f06/implicit-variety.json`. Harness: `build/f06_implicit_variety.py`. Raw outputs and usage: `build/f06-implicit-variety-results.json`.

This tests live-context retrieval/guidance through production services using scripted finalized text. It does not test physical capture, UI rendering, or extraction/summary generation. Earlier extraction and summary findings remain open. No general semantic relevance filter was replaced and no model was upgraded. Terra low remains selected.
