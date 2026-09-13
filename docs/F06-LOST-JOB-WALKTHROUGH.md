# Lost-job transcript walkthrough — current code, September 12

Actual Terra-low responses and real BGE retrieval using freshly seeded approved memories. This is a paced service-level transcript replay, not physical audio or GUI capture. Calls were serialized: the next turn waited if an API response overran its scheduled time. No future turns were supplied.

## Existing memories

- Maya was laid off from her job at McDonald's on September 1, 2026, and is worried about paying rent.
- Maya's mother Ruth died on August 20, 2026.
- Maya won first prize in a photography competition on September 5, 2026.
- Maya quit her job at Oak Cafe in June 2026 and felt relieved to leave a stressful manager.
- Maya has chemistry and mathematics exams next week and is stressed about preparing for them.

An additional wrong-contact memory was excluded by contact filtering.

## Transcript

| Scheduled time | Speaker | Words |
|---|---|---|
| 6s | You | How have you been? |
| 12s | Maya | Things have been difficult. |
| 18s | You | What has been on your mind? |
| 24s | Maya | They let me go, and now I need to work out how to pay the rent. |
| 30s | You | That sounds rough. |
| 36s | Maya | After all those shifts behind the counter, suddenly I have no paycheck coming. |
| 42s | You | Okay, let us talk about something else. |
| 48s | Maya | Changing the subject: I am enjoying a new mystery novel. |

Turn 7 was delivered after the preceding response at approximately 46.09s, later than its 42s schedule. These timings are a scripted test, not a latency guarantee.

## Expected and observed

Expected: vague difficulty alone should show no memory; job-loss/rent clues should surface the layoff as possible context; unrelated memories should stay hidden; a book-topic change should stop selecting the job memory, allowing the existing display retention to expire.

| Clue checkpoint | Model response arrived | Newly selected reminder | Context panel including retention |
|---|---|---|---|
| 12s | 18.38s | None | None |
| 24s | 28.88s | Maya was laid off from her job at McDonald's on September 1, 2026, and is worried about paying rent. | Maya was laid off from her job at McDonald's on September 1, 2026, and is worried about paying rent. |
| 36s | 46.09s | Maya was laid off from her job at McDonald's on September 1, 2026, and is worried about paying rent. | Maya was laid off from her job at McDonald's on September 1, 2026, and is worried about paying rent. |
| 48s | 52.45s | None | Maya was laid off from her job at McDonald's on September 1, 2026, and is worried about paying rent. |

The retained job context cleared at **70.14s** with no further model call. Current-topic replies already switched to the book at 52.45s.

## Full actual checkpoint outputs

### Through turn 2

**Candidates retrieved internally:**
- None

**Analysis:**
- sad_low_energy (medium): The contact may be conveying that they have been having a hard time.

**Remember:**
- None

**Replies:**
- I’m sorry to hear that. Do you want to talk about it?
- That sounds really hard. What’s been going on?

**Follow Up:**
- What’s been making things difficult?
### Through turn 4

**Candidates retrieved internally:**
- Maya was laid off from her job at McDonald's on September 1, 2026, and is worried about paying rent. — lexical+semantic
- Maya has chemistry and mathematics exams next week and is stressed about preparing for them. — semantic
- Maya quit her job at Oak Cafe in June 2026 and felt relieved to leave a stressful manager. — semantic

**Analysis:**
- tense_negative (medium): The contact may be feeling stressed or distressed about losing work and covering rent.
- discomfort (medium): The contact may be signaling a need for support around an immediate financial problem.

**Remember:**
- Possibly related: Maya was laid off from her job at McDonald's on September 1, 2026, and is worried about paying rent.

**Replies:**
- I’m really sorry. That sounds like a lot to have land on you at once.
- I’m sorry you’re dealing with that. Do you want to talk through what feels most urgent right now?
- That’s really hard. Is there anything I can do to help you think through next steps?

**Follow Up:**
- Have you been able to find out when your final pay will come through?
- Do you want to look at a few options for getting through rent this month?
### Through turn 6

**Candidates retrieved internally:**
- Maya was laid off from her job at McDonald's on September 1, 2026, and is worried about paying rent. — semantic
- Maya has chemistry and mathematics exams next week and is stressed about preparing for them. — semantic
- Maya quit her job at Oak Cafe in June 2026 and felt relieved to leave a stressful manager. — semantic

**Analysis:**
- tense_negative (medium): They may be expressing financial strain and pressure after losing work.
- sad_low_energy (medium): They may be feeling down about the sudden loss of their job.

**Remember:**
- Remember: Maya was laid off from her job at McDonald's on September 1, 2026, and is worried about paying rent.

**Replies:**
- I'm sorry you're dealing with that. Is there anything I can do to help right now?
- That is a lot to have land on you at once. Have you had any chance to look at what options you have?
- I'm sorry. Do you want to talk through what happened, or focus on what to do next?

**Follow Up:**
- Do you know when your last paycheck will come through?
- Have you been able to reach out to anyone about help with rent?
### Through turn 8

**Candidates retrieved internally:**
- None

**Analysis:**
- tense_negative (medium): The contact explicitly describes their situation as difficult and financially stressful.
- neutral_calm (medium): The contact may be redirecting toward a lighter topic.

**Remember:**
- None

**Replies:**
- What mystery novel are you reading?
- Nice—what are you enjoying about it so far?
- A mystery novel sounds like a good change of pace. What is it about?

**Follow Up:**
- Do you have a favorite kind of mystery?

## Result

At 24s the embedding/lexical retrieval found the McDonald's memory among exam and voluntary-quitting distractors. At 28.88s Terra selected only the layoff reminder and offered natural sympathy, without asking whether the speaker meant McDonald's. The reminder appeared before the employer was ever named in the transcript. With stronger evidence, the model returned two tone hypotheses (tense/negative and sad/low-energy); the vague opening still returned only one. This bounded run meets the tested reminder-selection behavior, not a universal quality guarantee.

Four paid requests: **$0.0262108 (2.62 cents)**. Aggregate recorded F06 evaluations: **$0.35695108**. Raw evidence: `build/f06-lost-job-current.json`; reproducible harness: `build/f06_lost_job_current.py`. No extraction or summary call was made in this test.
