# Corrected requests: Luna, Terra and Sol low agent comparison

**The fixes helped specific failures, but have not made Luna consistently reliable. Sol and Terra improve some answers; neither removes all model or application problems.** This run used 36 fresh isolated agents: six selected cases, three actual configured models (`gpt-5.6-luna`, `gpt-5.6-terra`, `gpt-5.6-sol`), low reasoning, two independent responses each. All 36 outputs pass local Pydantic validation; 24 guidance outputs also replay through unchanged corrected-app filtering with exact requests verified.

The focused scope was stated while the optional full-versus-focused question remained unanswered, to respect the user's limited subscription usage. The full 23-case/138-response agent comparison was not run. Cases cover garbled attribution, a third-party boundary, wrong-speaker check-in, call duration, memory extraction and the latest whole-call summary. This is exposed regression evidence, not held-out accuracy or an F07 acceptance result.

## What the comparisons show

Counts below refer to two independent responses per model for each selected case. Judgments are the root assistant's non-blinded source review, not human scores.

| Case | Luna low | Terra low | Sol low |
|---|---|---|---|
| Garbled fragment amid technical discussion | Literal greeting reply 2/2 | Literal greeting reply 2/2; one acknowledges inconsistency but still says hello | Avoids greeting reset 2/2; offers context continuation or clarification |
| Third-party boundary | Avoids current-call withdrawal 2/2; one redundant acknowledgment, one no reply | Avoids current-call withdrawal 2/2; keeps third-party referent, though reply is generic | Explicitly distinguishes speaking to the third party from this conversation 2/2; more useful questions, but inaccurate cue citations |
| User asks how contact feels | Invents user self-description 1/2; one unsupported reply survives filtering | No invented personal-state reply 2/2 | No invented personal-state reply 2/2; waiting advice appears as a follow-up 1/2 |
| User asks elapsed call time | No invented duration 2/2; one reply speaks as the assistant about its excerpt rather than a natural user reply | No invented duration 2/2 | No invented duration 2/2 |
| Temporary dispute in memory | Misclassified as relationship preference 2/2 | Correct shared reference 1/2, omitted 1/2 | Correct shared reference 2/2 |
| Completed work / merge conflicts | Overstates encountered conflicts as resolved 2/2 | Omits the completed-work fact 2/2; absence is not a corrected extraction | Accurate first repeat, overstates resolution second repeat |
| Advice to read generated code and understand the product | Omitted 2/2 | Retained 2/2 | Retained 2/2 |
| Final clothing options in summary | Specific shirt retained 1/2, brown/gray options 1/2; does not clearly preserve the final pairing together | Specific shirt plus narrowed brown/gray pairing retained 2/2 | Specific shirt plus narrowed brown/gray pairing retained 2/2 |
| Project concern and supporting response in summary | Both retained 2/2 | Broad concern retained, supporting response omitted 2/2 | Concern retained 1/2; supporting response omitted 2/2 |

All six summaries keep the art outing distinct from testing, avoid inventing a definite final outfit decision, and avoid the historical ambiguous relationship-advice attribution. All retain the approximate train plan without inventing a normalized timezone. Sol preserves the isolated-evidence criticism most explicitly in both repeats, but its second summary loses the user's nervousness; extra capability does not guarantee complete coverage. Luna's first summary compresses an open repeat-call offer into an agreement, and its second omits the offer. Terra and Sol preserve it as an offer in both repeats.

Luna's second extraction additionally stores apparent driving-related banter too literally. Both Luna and some Sol outputs assume gender; Terra's extraction uses neutral pronouns. Several outputs combine independently reviewable facts into one memory proposal. Terra's first extraction adds an unsupported letter prefix to a task identifier. These are remaining fidelity/scope issues, not repaired or silently edited outputs.

## Did the application changes help?

The earlier [real API old/revised comparison](CALL-PROMPT-API-20260917.md) remains the strongest direct evidence about the changes: old Luna invented a check-in answer in 2/2 repeats versus revised 0/2, and invented duration in 1/2 versus revised 0/2. Optional immediate actions survived filtering more often, and whole-source summaries avoided recursive drift. That same comparison also documented inconsistent memory categories and no net reply-availability gain.

Today's corrected-request agent results support the duration protection and improved whole-summary structure, but expose a surviving check-in failure in Luna. They also show useful model differences on identical requests: Sol handles the garbled fragment better; Terra and Sol retain substantive memory advice and summarize the final clothing alternatives better. This is **not** a new causal before/after test: no fresh old-prompt agent arm ran, and comparing today's agents with historical API outputs confounds method and time. Do not label the observed counts an overall accuracy ranking.

The stronger models also reveal application weaknesses:

- Grounding requires a current contact anchor, but does not establish that cited words support each claim. Sol's boundary cue quotes statements absent from its cited IDs; adding the latest contact denial lets the cue survive. In the second repeat, an older uncertainty claim similarly survives with an unrelated current anchor. Some selected IDs belong to user context. Context IDs can be legitimate, but cannot substitute for the quoted contact evidence.
- Conversely, Sol recognizes the garbled fragment and uses substantive recent contact turns, but its cues are removed because the application still treats the garbled final fragment as the required anchor. Its useful reply survives. More capable interpretation alone cannot resolve this disagreement with filtering.
- The personal-claim filter removes one invented Luna response but lets another formulation through. Source ownership and actual support need checking beyond literal phrases.
- Neutral/calm is filtered conservatively, while stronger models sometimes rephrase weak acknowledgment as supportive/warm and pass. This is not proof of a genuine emotional signal.
- Waiting advice can appear under follow-ups despite improved speaker ownership. Avoid treating more output, more confidence, or successful parsing as usefulness.

These are findings for later bounded corrections, not new code or an additional tuning round. Echo remains excluded.

## Structural results and limits

| Metric | Luna | Terra | Sol |
|---|---:|---:|---:|
| Responses / locally valid | 12/12 | 12/12 | 12/12 |
| Guidance responses | 8 | 8 | 8 |
| Raw cue items / accepted cue items | 8/2 | 8/4 | 15/9 |
| Guidance responses with a reply after filtering | 5/8 | 4/8 | 4/8 |
| Raw visual-evidence citations | 0 | 0 | 0 |
| Memory proposals, repeat 1 / 2 | 6/8 | 6/4 | 6/10 |
| Summary statements, repeat 1 / 2 | 5/5 | 5/5 | 6/5 |

These are counts, not accuracy scores. Unsupported greetings and invented self-description contribute to Luna's reply count. Missing or unavailable facial data remain so; zero visual citations does not prove no internal visual influence. No new visual ablation, expression ground truth, retrieval recall, GUI delivery, paced latency or human usefulness test ran. The chosen live cases supplied no memory candidates, so they do not establish retrieval omissions or reminder recall.

Agents used fresh `fork_turns=none` contexts, one case per agent, no prior-answer reuse. Each received the exact frozen corrected request instructions, input, strict schema and textual output cap from the prepared API comparison. File transport and the surrounding agent environment differ from API execution: generation caps/strict decoding, reasoning-token usage, actual API latency and billing are unmeasured. Two equivalent transport wrappers were used; within each case/repeat the wrapper was identical across models except the output path. Later stronger-model testing should reuse these frozen packets, not previous answers as shared conversation history.

## Preservation and status

Private evidence: `build/call-agent-models-20260921/` contains packets, frozen criteria, model/effort/fork dispatch provenance, all 36 raw files and hashes, offline validation/replay, metrics and final audit. Production source still matches reviewed correction commit `a927b91`; original API cases and historical evidence hashes are unchanged. No approved personal memories/summaries were modified, no raw media retained/uploaded, and no API requests or spending occurred in this agent run.

The API account was separately rechecked earlier September 21 and still returned `credit_balance_exhausted`. Its preserved Luna $0.30/Terra $0.50 comparison remains pending; no automatic retry or budget reset. Production remains Luna low. No new Claude review, release, commit/push, human-test clearance or F07 completion is claimed. Original F07 gates, two-round limit and September 23/27 deadlines remain; F08's October 1 Windows target stays protected.
