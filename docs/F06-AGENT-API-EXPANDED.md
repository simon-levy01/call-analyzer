# Expanded Luna agent / recorded API comparison — 13 September 2026

**Closure update, 2026-09-14:** User accepted F06 as complete for now with documented Luna limitations and authorized publication. No additional final Luna live call or fresh final Opus review is claimed; latest review was Sonnet 5. This closure supersedes older pending-gate statements below. See the master plan closure record.

Status: pre-live checks completed 14 September 2026. Luna low is now configured for live guidance and the manual check. Existing API answers were reused. The user dropped local-model comparisons and the 68-case extension.

Completed: 258 historical agent answers (226 distinct requests plus 32 exact reuses), 12 new isolated-agent answers, six revised-prompt agent answers, and 24 new Luna-low API calls. All 276 mapped isolated-agent answers pass the application schemas; this does not mean they are semantically correct. The diagnostic batched pilot remains excluded.

New API cost estimate: **$0.02118703**, comprising $0.00812038 for the twelve frozen new cases, $0.00643198 for six revised checks, and $0.00663467 for six final checks. Aggregate cap was $0.03. No old API case was recalled. Claude used the signed-in subscription; its token-equivalent cost field is not an additional OpenAI API invoice.

**270 automated application tests passed**, including new cross-turn reply-filter and stale-manual-display regressions. No new human live call has been performed.

## Frozen scope and controls

258 existing Luna API cases (200 guidance,42 Ask,12 summary,4 extraction) and twelve new synthetic guidance cases are frozen in build/agent-api-expanded-20260913/inputs/. Expected answers, prior outputs and local-model results are excluded from those input files. The earlier local Gemma3/Qwen3.5 results and existing Luna API responses remain unchanged.

The twelve new cases each used a fresh actual gpt-5.6-luna / low agent, with no history fork. For the old corpus, 226 distinct request/instructions/schema/output-limit combinations represent258 cases; exact duplicates reuse one agent result with recorded provenance. Such reused answers are not additional independent inference or a test of repeat variability. The dispatch log records accepted model/effort configuration, not a guarantee of identical backend snapshots to the API.

Agent runtime instructions/tool context, token-limit enforcement and structured-output decoding differ from the Responses API. Do not treat agent elapsed time as application API latency or subscription usage as free/unlimited API access. The initial comparison used twelve new Luna API cases. Two six-case prompt acceptance rounds followed within the aggregate cap. Production live/manual routing was then set to Luna low.

## Why the batched pilot was stopped

The diagnostic pilot answered96 old cases in12 agents, eight cases per agent. In case017, the request supplied no memories, yet the answer reused the Ruth bereavement from case016 in the same agent. This is cross-case contamination, not legitimate retrieval. Four of96 pilot answers also failed application schema validation. The pilot is retained separately; it is excluded from the isolated-agent comparison. The project instruction now requires a fresh agent per distinct request for API comparisons.

## Twelve new isolated-agent cases

All12 outputs passed the application schema. The agent distinguished found keys from loss, selected McDonalds without rent in the memory, selected the older grandmother/January and photography/March events despite newer alternatives, separated user stress from the contact, respected resolved exam stress, suggested waiting after the user spoke, followed the book-topic change, distinguished a colleague's anger from contact affect, and ignored the instruction embedded in transcript text.

It missed the film-award reminder for “judges picked our short” plus an upcoming screening. In the ambiguous female-bereavement case it offered both tentative memories, which the frozen expectation permits but may be excessive in the UI. The older photography celebration reply asked how the club marked it despite the question being about what is coming up. Another reply advised giving the angry colleague space without evidence that this was needed. These are useful improvements over several local-model failures, not a perfect result; the completed API comparison performed differently.

## Isolated recorded-case findings

The first current-prompt screen found all three distinct positive reminder opportunities (rent, prize, exams), but also retained Pepper after an explicit refusal to discuss losing her. The saved Luna API screen found5/6 positive opportunities and0/14 negative reminders across repeated inputs. Agent duplicate reuse means counts must be reported by distinct requests as well as mapped cases; it cannot establish superior repeat reliability from this small screen.

The API runner has an offline mock check covering cap-before-dispatch, Luna-low-only routing, new-cases-only coverage, no retry after an uncertain-billing error, and conservative cost retention. Those mock calls have no network/API cost and are not model evaluations.

See docs/TESTING.md and the raw expanded directory for preparation, dispatch, collected outputs and validation. The findings below describe the frozen baseline unless marked final.


## Frozen comparison results

| Frozen screen | Saved Luna API | Isolated Luna agent | Saved Gemma3 4B original | Saved Qwen3.5 4B original |
|---|---:|---:|---:|---:|
| Useful target memory, six mapped positive checkpoints | 5/6 | 6/6 (three distinct inputs) | 0/6 | 2/6 |
| Unwanted reminder, fourteen mapped negative checkpoints | 0/14 | 2/14 (one of seven distinct inputs) | 0/14 | 8/14 |
| New cases: four required target reminders | 1/4 valid-ID reminders (2/4 content matches) | 3/4 | 0/4 | 1/4 |

The new-case exam reminder is optional context and is excluded from the four required opportunities. Different wording, extra relevant sources, or a cautious clarification is not automatically a failure. All local columns reuse the previous completed run; no local inference was repeated here.

In the current actual-call checkpoints, isolated agent case218 returns to old financial sadness after a project/regulation switch; the saved API remains on the current turn. Case236 anchors its explanation on an apology for not listening even though the contact has since agreed that models will improve; the API uses the newer contribution. Both methods sometimes overstate affect confidence, and both ask about the biggest part after the unfinished phrase “The biggest...”. Later agent responses usually suggest waiting and correctly separate the user's disappointment from the contact's affect.

Ask results are broadly similar on interview outcomes, newer versus older bereavements, older photography versus newer film success, and upcoming travel. Agent case250 describes the dental appointment as still happening, whereas the saved API includes the later completed-checkup update. Both find the upcoming physiotherapy visit. In case246 the agent asks which deceased person was meant; the API chooses Arthur, whose memory explicitly says he is missed. That is an ambiguity-handling difference rather than an automatic accuracy failure. In case242 the saved API answer has a one-character error in a source ID, despite a factually reasonable answer; the agent's citations are valid.


For the entire88-turn call, agent extraction proposed seven memories versus six in the saved API output. It captured finances, the regulation/Eden correction and the user's testing/model-switch commitments, but promoted Yaheli's observation about the landing page into high-confidence criticism and attributed the user's cheaper-Luna observation to Yaheli using an unclear final transcript fragment. The API extraction preserved the user's disappointment and the shared expectation that models would improve more faithfully. More proposals therefore did not mean better memories. The agent summary had four statement objects versus six API statements, with broadly coherent coverage and correct user attribution of disappointment; it omitted the camera interruption and unresolved guidance issue. Concision alone is not an error. The summary and extraction are independent stages, and their speaker-attribution quality differed.


Applying the current application guards offline does not remove every semantic defect. In cases029/063/200 the unsupported discomfort cue survives, although its confidence is reduced; the unwanted Pepper reminder in200 also survives. Case218 still carries the old financial tone after the project switch. These are raw-output issues that could remain visible, not merely formatting failures repaired by the app. Historical USER-last empty replies do receive the current waiting fallback. Legacy cases without a saved snapshot cannot receive this exact guard replay and are labeled as raw comparisons only.


The twelve new cases deliberately supply seven memories as a controlled distractor test. Production retrieval supplies at most four; these tests isolate the model's choice among supplied memories and do not measure embedding recall or prove production retrieval would supply the same candidates. The previous local report separately contains actual timed/application replays; this expanded run reuses their evidence and does not claim a new live UI or speech-transcription measurement.


## Final prompt acceptance and remaining limitations

The revised prompts explicitly prioritize a contact's refusal over an otherwise relevant memory, require supported indirect reminders, keep affect on the current topic, and recheck attribution and app-testing context during extraction. The first longer version exceeded the existing input ceiling in a regression fixture; it was shortened rather than shrinking transcript context. The 1,300-token transcript allowance remains.

Final six API cases: Pepper's unwanted reminder was suppressed; the call's regulation topic no longer revived financial sadness; the film-award and older grandmother reminders appeared with valid IDs. The rent case offered both McDonalds job loss and the older Oak Cafe resignation, so target recall improved with an extra ambiguous candidate. The final seven-memory extraction preserved the user's disappointment and stopped inventing a new job, but still overinterpreted the garbled final model comparison. The boundary case still labelled a verbal refusal as discomfort. These are remaining model-quality limitations, not completed fixes. One sample per changed prompt cannot establish repeat reliability.

The original twelve-case API screen omitted job and film reminders and corrupted the older photography memory ID. Its content-level recall was 2/4 required targets, but only 1/4 had a usable target citation. The application rejects unavailable evidence IDs; this is a visible failed update, not a silently repaired reminder. All twelve final/revised API responses had valid supplied citation IDs.

No new summary inference was needed: summaries were unchanged and their historical comparisons plus application tests were reviewed. The full-call extraction was rerun independently without paying for mid-call analysis. Actual live timing, device interaction, and subjective usefulness remain for the user's live call.

## Claude review and dispositions

Claude Sonnet 5 completed a tool-less static review. Its full response is preserved in build/agent-api-expanded-20260913/claude-review-sonnet.json. The configured Fable default first returned a credits-required error without inference; it was not reported as a successful review.

Confirmed and fixed: normalized reply matching no longer joins separate user turns or matches partial words; stale manual guidance cannot replace a newer snapshot or regress its watermark. Two regression tests cover these changes.

Verified concerns that required no change: `_cautious_policy` returns an insufficient-evidence object when no contact speech exists, so the suspected None crash is not reachable; summary consolidation explicitly deletes consumed review-chunk rows before inserting the merged row. Current local-policy constructors do not produce the over-cap combination needed for the suspected negative-slice issue. Local sensitive-memory reminders have a separate existing privacy purpose; their priority was not redesigned here. Attribution and topic relevance remain partly model-dependent, as the real acceptance results demonstrate. No speculative refactor or global settings change was made.

## Preserved handoff

The private archive evaluation-history/f06-pre-live-luna-20260914.zip contains this run, source/test snapshot and evaluation helpers, with hashes in evaluation-history/pre-live-luna-manifest.json. Earlier private archives are unchanged. Copy the ignored evaluation-history directory privately for another computer; Git does not transfer it automatically. Live-call readiness means completed pre-call checks with the limitations above, not guaranteed model accuracy.
