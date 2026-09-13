# Fictional three-call Ask Memory test

This is fictional, hand-authored test data: 18 approved memories with evidence in three scripted calls. It tests search and answer generation, not automatic memory extraction.

Select **Alex Morgan — FICTIONAL ASK TEST**, type a question, and click **Use cloud help** for Luna low. A local search is optional. The estimate is shown before each request. Results show supporting memories; select one and click **Open exact source** to see the original fictional dialogue.

The revised demo database is isolated in `build/ask-history-20260913/memory-agnostic.sqlite3`. Real contacts are not modified. Restart with `.venv\Scripts\python.exe -X utf8 build/open_ask_history.py`. An already-open older test window retains its older fixture until restarted. Manual cloud requests and responses are logged in `build/ask-history-20260913/manual-questions.jsonl`.

Evaluation reference: September 13, 2026, Asia/Jerusalem. The real UI uses its displayed current date, so upcoming/past answers can change when testing later.

## Searches and actual model answers

| Search | Actual result | Supporting fixture items |
|---|---|---|
| Did he get the position he was preparing for? | answered: No. He was rejected by Northstar Studio after the interview. Harbor Labs had not replied as of September 13, 2026. | rejection, bakery_progress |
| What is he doing to address the reason they turned him down? | answered: He is building a booking page for his aunt’s bakery to gain the shipped client-project experience Northstar said he lacked. The prototype works, and his aunt will test it on September 15, 2026. | next_step, bakery_progress |
| What could help him take his mind off things soon? | answered: His upcoming film-award celebration on September 16, screening on September 18, and relaxing Galilee cabin trip with Ben from September 19–21 could give him a change of focus. Testing the bakery prototype with his aunt on September 15 may also help him channel energy into a practical project. | new_trip, new_prize, bakery_progress, celebration |
| Who is the more recent person he lost? | answered: Maya—the more recent loss. She died on September 5, 2026; Arthur died on February 12, 2026. | old_loss, new_loss |
| Who used to help him get ready to speak in front of people? | answered: His grandfather, Arthur, used to help him rehearse presentations. | old_loss |
| What happened to that person he misses? | clarification: Do you mean Alex’s grandfather Arthur, who died on February 12, 2026, or his friend Maya, who died in a cycling accident on September 5, 2026? | old_loss, new_loss |
| What did he win most recently? | answered: Alex most recently won the Maple community festival award for his short film on September 11, 2026. | new_prize |
| Which success involved a picture taken early in the day? | answered: Alex’s success in winning the Riverside photography contest, with a harbour sunrise photograph, involved the early-day picture. | old_prize |
| What went wrong on the earlier getaway, and how is the next one different? | answered: The earlier getaway was camping at Pine Lake with Ben on July 18; rain and a leaking tent spoiled the weekend. The next one is a booked cabin stay in Galilee with Ben from September 19–21, which Alex is looking forward to as a chance to relax. | old_trip, new_trip |
| Where is he going to have his teeth checked? | answered: Cedar Clinic. The September 10 dental checkup went fine. | dentist, physio |
| Which health visit is still ahead of him? | answered: His shoulder physiotherapy at Harbor Health on September 17, 2026, at 11:00 is still ahead. | physio |
| When is his appointment? | clarification: Which appointment do you mean: his dental checkup on September 10 at 15:00, or shoulder physiotherapy on September 17 at 11:00? | dentist, physio |
| Should I offer solutions when he brings up his riding companion? | answered: No—when Alex brings up Maya, listen rather than offering solutions. He has specifically said he wants listening, not advice, about her death. | support, new_loss |
| Has the other company offered him a meeting yet? | answered: No. Harbor Labs has not replied, and there is no interview invitation as of September 13, 2026. | new_application, bakery_progress |
| How much will his new role pay? | no_match: There’s no approved information about Alex having a new role or what it would pay. |  |

## Assessment and limits

Latest run without comparison hints: all 15 expected answer/clarification statuses and valid source IDs. One remedy answer omitted the rejection-reason memory from its citations despite a correct answer; a distraction answer included a tentative bakery-project suggestion not explicitly stated as a coping benefit. Valid source IDs alone do not guarantee complete claim-level support. See [the creation audit](F06-MEMORY-CREATION-AUDIT.md) for the agent's full assessment and proposed extraction improvements.

I reviewed all 15 answers against the complete input evidence. All 15 gave the expected substantive answer or clarification; all returned source IDs were valid. The recent-loss question compared Maya with Arthur; the presentation clue selected Arthur despite the newer loss. The same distinction worked for the older photo award versus newer film award, earlier camping versus upcoming cabin trip, and past dental versus upcoming physiotherapy appointments.

The model combined rejection reason with the bakery project and its progress. It clarified the vague loss and appointment questions rather than selecting the newest event automatically. It did not invent a salary or job offer.

Two first-pass answers printed internal source IDs in prose despite valid structured citations. The prompt was clarified; both targeted real-model rechecks removed those IDs and retained correct answers. This is a small fixed scenario evaluation, not a guarantee for every question or large histories.

Review corrections also removed the 400-character display restriction from cloud evidence, exercised the real large-history fallback, kept question quotations valid in no-match/clarification answers, and corrected fixture permission seeding so memories are not mislabeled as factual corrections. The complete 15-question real-model rerun passed after these fixes, with no IDs in answer prose.

Latest revision removes the explicit comparison to the older photography win from both dialogue and memory. The cabin dialogue/memory also no longer explains its relationship to the older camping trip. The model still distinguishes the dated events. One distraction answer additionally suggests the bakery project might help channel energy; that is a tentative suggestion, not an explicitly remembered coping benefit.

47 real Luna-low requests total across these Ask iterations: $0.0328780. Latest 15-question run without comparison hints: $0.0104307 (about one cent). Aggregate OpenAI evaluation spend after these checks: $3.42618378, below the authorized $4 cap. Raw requests, responses, token usage and costs are in the results JSON files beside the demo database. These are application API evaluation costs, not Codex/Claude subscription usage.

265 automated tests passed after corrections, including the real existing retriever and bounded-dispatch large-history path. Full-input history is bounded to 4,400 estimated evidence tokens inside a 6,000-token input ceiling. Larger histories use a ranked selection and disclose limited coverage. The output can cite up to four sources.

## Fictional source calls

### 2026-09-01 — Preparing for an interview

**You:** What is coming up with work?

**Alex:** I have a junior designer interview at Northstar Studio on September 4. It's my first design interview.

**Approved memory (interview):** Alex has a junior designer interview at Northstar Studio on September 4, 2026; it is his first design interview.

**You:** What part worries you?

**Alex:** Explaining my portfolio out loud. Could we practise together on September 3 at seven in the evening?

**Approved memory (preparation):** Alex is nervous about explaining his portfolio aloud and asked to practise with the user on September 3, 2026 at 19:00.

**You:** Does practising remind you of anyone?

**Alex:** My grandfather Arthur used to rehearse presentations with me. He died on February 12 this year. I still miss our Sunday chess games.

**Approved memory (old_loss):** Alex's grandfather Arthur died on February 12, 2026. Arthur helped him rehearse presentations; Alex misses their Sunday chess games.

**You:** Have you had any encouraging feedback?

**Alex:** I won the Riverside photography contest on June 20. The winning picture was a sunrise over the harbour.

**Approved memory (old_prize):** Alex won the Riverside photography contest on June 20, 2026 with a harbour sunrise photograph.

**You:** Did you go away over the summer?

**Alex:** I went camping at Pine Lake on July 18 with Ben. It rained the whole weekend and our tent leaked.

**Approved memory (old_trip):** Alex camped at Pine Lake with Ben on July 18, 2026; rain and a leaking tent spoiled the weekend.

**You:** How can I help while you get ready?

**Alex:** Give me specific feedback rather than just telling me I'll be fine. I don't drink coffee after lunch either; it keeps me awake.

**Approved memory (preference):** Alex prefers specific feedback to generic reassurance and avoids coffee after lunch because it keeps him awake.

### 2026-09-07 — Rejection and a recent bereavement

**You:** How did the Northstar interview turn out?

**Alex:** They emailed a rejection on September 6. They wanted someone who had shipped client projects. I felt disappointed, but they said the portfolio itself was strong.

**Approved memory (rejection):** Northstar Studio rejected Alex on September 6, 2026 after his September 4 interview, citing lack of shipped client projects. Alex felt disappointed; they praised his portfolio.

**You:** What do you want to do next?

**Alex:** I'll build a booking page for my aunt's bakery to get a real client project. I want a working version by September 25.

**Approved memory (next_step):** Alex plans a booking page for his aunt's bakery, targeting September 25, 2026, to gain client-project experience after Northstar's rejection.

**You:** Has anything else made this week difficult?

**Alex:** My friend Maya died in a cycling accident on September 5. We rode together most Saturdays. Her memorial is on September 12.

**Approved memory (new_loss):** Alex's friend Maya died in a cycling accident on September 5, 2026. They rode together on Saturdays; her memorial is September 12, 2026.

**You:** Would you like advice about everything?

**Alex:** Right now I mostly want someone to listen about Maya. With the work stuff, practical suggestions are welcome.

**Approved memory (support):** Alex wants listening rather than advice about Maya's death, but welcomes practical suggestions about his work setback.

**You:** Anything else on your calendar?

**Alex:** A dental checkup at Cedar Clinic on September 10 at three in the afternoon.

**Approved memory (dentist):** Alex has a dental checkup at Cedar Clinic on September 10, 2026 at 15:00.

**You:** Are you waiting on another employer?

**Alex:** I sent an application to Harbor Labs yesterday, September 6, but they haven't invited me to an interview.

**Approved memory (new_application):** Alex applied to Harbor Labs on September 6, 2026 and had no interview invitation as of September 7.

### 2026-09-13 — Something enjoyable ahead

**You:** Is there something you're looking forward to?

**Alex:** Ben and I booked a cabin in the Galilee for September 19 to 21. I'm looking forward to switching off.

**Approved memory (new_trip):** Alex and Ben booked a Galilee cabin for September 19–21, 2026. Alex looks forward to relaxing.

**You:** You sound pleased about something else too.

**Alex:** My short film won the Maple community festival award on September 11. They're showing it at a screening on September 18.

**Approved memory (new_prize):** Alex's short film won the Maple community festival award on September 11, 2026; its screening is September 18.

**You:** How are you going to mark the win?

**Alex:** Dinner with my sister at Olive Kitchen on September 16, at eight.

**Approved memory (celebration):** Alex will celebrate the film award with his sister at Olive Kitchen on September 16, 2026 at 20:00.

**You:** How was yesterday?

**Alex:** Maya's memorial was hard. I talked to her brother afterwards. I still don't want to go on our usual Saturday ride.

**Approved memory (memorial):** Alex found Maya's September 12, 2026 memorial difficult, spoke with her brother afterwards, and does not yet want to resume their Saturday ride.

**You:** Did you start the bakery page?

**Alex:** The first prototype is working. My aunt will try it on September 15. Northstar hasn't changed its decision, and Harbor Labs still hasn't replied.

**Approved memory (bakery_progress):** As of September 13, 2026, Alex's bakery prototype works; his aunt will test it September 15. Northstar's rejection stands and Harbor Labs has not replied.

**You:** Do you have any other appointments?

**Alex:** Physiotherapy for my shoulder at Harbor Health on September 17 at eleven in the morning. The dental checkup last Thursday went fine.

**Approved memory (physio):** Alex has shoulder physiotherapy at Harbor Health on September 17, 2026 at 11:00. His September 10 dental checkup went fine.
