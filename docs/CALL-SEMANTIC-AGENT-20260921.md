# Full-call semantic correction comparison — September 21

Current fixes plus independently bounded citations were reviewed by actual tool-disabled Claude Opus 5 and published on main as `addfe9ba16b433344354c9f7f19fa27fad3e0a76`. Local main, origin/main and GitHub main were verified identical. See [checkpoint review](CITATION-MAIN-20260921.md). The requested follow-up is isolated on `codex/call-semantic-fixes-20260921`; main remains the switchable baseline. Candidate code is committed as `088e50665e11edca477e87c5d4cac885d580c68d`. Only reviewed reports/status updates are copied to main after testing; its application and test code remain identical to `addfe9b`.

## Candidate

The shared cue guard rejects language citations belonging to the user; the shared prompt specifies contact-only evidence and four IDs maximum. Both speakers remain supplied as context. This conservative boundary can suppress a legitimately contextual mixed-citation cue; it does not prove the meaning of contact-only evidence is correct. Nonverbal checks remain unchanged.

Guidance instructions order speaker ownership, adjacent clarification and useful-next-response checks. Memory extraction uses an ordered context/owner/value/scope/citation check, discourages low-value proposals, retains specific project feedback and commitments, and requires the clarifying turn when an ambiguous fragment needs context. Summary instructions distinguish completed events, future agreed actions and unresolved questions, preserving substantive exceptions. No lexical patches tied to the recorded call were added. Echo handling, models, source limits and token ceilings remain unchanged.

This user-requested semantic candidate consumes the second and final authorized calibration round. No third tuning round is implied by the replay or its results. Original F07 144-response/two-repeat, held-out, three-participant, 85%, 400-token allowance plus separate 10% cost gate and September 23/27 deadlines remain. F08's October 1 Windows deadline remains protected. This exposed diagnostic does not pass those gates.

## Method and verification

The complete shortest call supplies 88 turns and all 31 recorded guidance request snapshots, plus full extraction and summary. Two arms: published main with the citation fix, then this candidate. Every distinct request uses a fresh actual gpt-5.6-luna agent, low reasoning, no conversation-history fork, frozen input/instructions/strict schema/output limit and no expected answers. All 64 fresh requests completed, plus two exact baseline post-call reuses; those reuses are not new independent inference. One pass per arm, not two independent repeats or API parity. No paid API testing.

Both arms preserve causal recorded snapshots, source attribution, supplied memories and local observations. All transcript IDs, memory rows, schemas and output caps match. Seven guidance payloads retain one additional existing visual/vocal row under the candidate's shorter prompt; comparisons therefore measure actual application request behavior, not perfectly identical trimmed payloads. No extra tokens were authorized or needed. Neither fresh retrieval nor new audio/vision inference or adaptive live scheduling is simulated. Historical original response arrival is only a separate counterfactual display check.

336 offline tests pass, including the added mixed-speaker citation rejection. An initial long prompt failed the input-budget regression; it was shortened before freezing and inference. All 64 focused checks then passed. Initial failures and final passing evidence are preserved separately.

Private frozen packages, packets, request comparison, original raw answers, dispatch/reuse provenance, scratch stores, rubric and test reports are retained in ignored `build/call-semantic-agent-20260921/`. Private logs and approved memories are not edited. Previous model/API results and unrelated personal PDFs remain unchanged.

## Results and recommendation

**Do not merge the whole candidate into main.** The ownership guard has a concrete benefit, but the prompt rewrites do not show a consistent improvement. This is one exposed pass, not an accuracy estimate or an acceptance result.

| Observed result | Published baseline | Candidate |
|---|---:|---:|
| Local application/schema passes | 32/33 | 32/33 |
| Valid guidance responses | 30/31 | 30/31 |
| Checkpoints with accepted reply candidates | 15 | 7 |
| Accepted reply candidates | 17 | 8 |
| Checkpoints with accepted tone/cue candidates | 14 | 12 |
| Accepted tone/cue candidates | 15 | 14 |
| Initial accepted memory reminders | 2 | 1 |
| Memory proposals | 7 | 4 |
| Summary statements / words | 7 / 156 | 5 / 128 |
| Complete scratch post-call processing | Pass | Pass |

Counts measure coverage and validation, **not correctness**. Baseline checkpoint01 returned malformed JSON; candidate checkpoint07 returned a correct memory fact in text exceeding the existing 180-character limit. Both raw failures are preserved without repair or retry. No output cap was raised to make them pass. All 66 expected outcomes remain in the denominator; 64 pass locally.

### Guidance, cues and implied intent

The candidate avoids a reply answering the user's own thanks (17), a reply written as an AI assistant addressing the user (22), and some redundant suggestions (19–20). It also avoids an unsupported negative cue during an unfinished contact phrase (18). The new guard rejects candidate10's use of the user's confusion as evidence of the contact's state, despite the model ignoring the ownership instruction.

Regressions remain: an additional weak intensity label on a fragment (06), an overlong reminder that rejects the entire response (07), a stronger interpretation of an ambiguous transcript fragment (11), and treating a corrected issue as unresolved while adding a negative tone (12). A correctly cited phrase is still assigned to the wrong topic (15). Candidate14 loses a plausible uncertainty cue because it cites the wrong speaker's turn. Several replies disappear because the latest-turn citation is missing; these are not automatically useful improvements. There is no separate ground-truth intent label: intent-related assessment concerns invented commitments, role reversals, premature next steps and topic interpretation.

Applying the candidate guard to the **same saved baseline answers**, without inference, removes mixed-speaker cues in11,12,18,28. The last case has plausible contact evidence alongside an erroneous user citation, demonstrating the conservative loss tradeoff. This isolates guard behavior from sampling variation. It does not prove the new prompts improved the model.

### Memories and summary

The candidate drops a generic model-improvement prediction and keeps specific financial/project context and the model-selection plan. However, it also omits an explicit memory-testing commitment and a named person's correction, despite having all 88 turns and returning only four of twelve permitted proposals. These are extraction omissions, not retrieval limits. It also loses the brief duration qualifier. Neither full-call arm invents a new job; the earlier prefix/no-cap failure is historical evidence, not a reproduced baseline failure in this run.

The candidate summary improves section discipline and preserves the regulation correction's important exception. However, it presents an uncertain spoken cost estimate as a roughly definite call cost and introduces a comparative performance claim unsupported by the garbled ending. The baseline was more cautious about those details. Better structure and fewer words do not offset unsupported facts.

### Evidence supply and comparison limits

Both arms receive the same transcript IDs and memory rows; only seven additional individual sensor rows differ. The relevant stored memory is supplied at05/07. Initial reminder loss at07 is the candidate's text-length failure, not retrieval omission; on the historical-arrival counterfactual both arms retain one reminder. No memories are supplied at other checkpoints, so missing reminders there cannot automatically be called model misuse. All post-call omissions occur with the full transcript supplied.

Each arm returns one raw cue citing vocal evidence and none citing visual evidence. This does not establish that visual input had no internal influence; it provides no demonstrated improvement in cited facial evidence use. Visible guidance-output token estimates peak at430 baseline and364 candidate, excluding hidden reasoning. Agent tests cannot measure provider billing, API latency or strict API decoding; original 400-token and separate10% cost gates remain unverified. All 33 configured input/output caps match across arms. The app's ordinary-schema guidance estimate peaks at4700; the frozen strict-schema estimate peaks at4735 in BOTH arms, a pre-existing 35-token estimation difference, not a newly increased cap. Total app input estimates are151004 baseline versus150779 candidate; these are estimates, not billed usage.

The full offline display replay uses each frozen application, all88 speech receipts, original accepted-delivery times and half-second ticks. Baseline offers29 responses and records25 visible guidance changes; candidate offers30 and records16 changes; both finish empty. Baseline01 is invalid and07 has no historical accepted delivery; candidate07 is invalid. These are historical-schedule counterfactuals, not new API latency, adaptive scheduling, user dismissal/expansion or tone-UI tests. Fewer display changes are not an accuracy metric.

Original live guidance for this shortest call used **Terra low**, while the earlier full-call Luna/Terra/Sol agent answers used older requests. Those remain distinct historical references, not identical-condition controls. The earlier source-cap diagnostic covered only the first two-thirds. The private comparison view includes every current pair, original live output and prior model answer alongside raw versus application-filtered results.

Private evidence: frozen packages/packets, 64 unique dispatches, two exact reuses, final queue audit, per-arm validation, full scratch post-call results, same-answer filter comparison and root assessment under `build/call-semantic-agent-20260921/`. Fresh read-only, tool-disabled Claude Opus5 review and an evidence follow-up both cleared the experimental branch checkpoint and documentation-only publication to main, with no blockers. Returned model usage identified only claude-opus-5. The reviewer retracted an incorrect claim that the four-ID schema bound was missing and corrected its sensor-confound examples:06/12/18 have identical payloads, while10/11/14/25/27/29/30 differ. Sampling variance and bundled prompt changes still prevent causal attribution. The reviewer also withdrew citation pruning as a generally safe fix, because it can hide the original ownership error. Untested suggestions remain for explicit 180-character instructions, stronger citation wording, less aggressive memory omission, restoring final-scan emphasis and preserving numeric hedges. None was applied or tested as a third round. Raw reviews, commands and hashes are preserved under opus-final/ and opus-followup-complete/ in the private evidence directory. This technical review does not replace pending post-human F07 release review. No candidate merge, human approval, API test, third tuning round or F07 acceptance is claimed.
