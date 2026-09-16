# Old versus revised Luna prompts — September 17

The revised production requests improve specific speaker-attribution failures and the long-call summary, but do not consistently solve garbled attribution, repetition, intent or memory categorization. Luna low remains selected. This is an exposed diagnostic comparison, not F07 acceptance or release clearance.

## What was compared

The user explicitly selected real Luna-low API testing. We froze `75d5b27` (pre-fix) against `f68d5c8` (corrected branch), using the same source snapshots from three calls of 88, 150 and 240 turns. Instructions, serialization and cue schema intentionally differ between production versions; this is not an isolated prompt-text ablation.

**90 fresh independent API responses:** 16 guidance checkpoints ×2 versions ×2 repeats =64; four extraction chunks ×2 versions ×2 repeats =16; two whole-call summaries ×2 versions ×2 repeats =8; plus two revised whole summaries of the latest call. Extraction source boundaries match exactly between arms. Arm order alternated, each request used a fresh request context, and no prompt tuning occurred during the frozen run. Earlier results were preserved.

The old latest whole-summary request exceeded its 9,000-token ceiling. Its actual 23-stage historical result is the comparator for the two new whole-call summaries; it is explicitly unpaired. It was not regenerated with an unauthorized larger cap.

All 90 returned structured outputs with verified model `gpt-5.6-luna`, effort `low`. One revised guidance output subsequently failed application validation. That failure remains in the original results and denominator; its offline correction is described below. Schema-valid output is not synonymous with correct content.

The original ledger intentionally says `complete: false`: all 90 requests were dispatched and answered, but its completion rule also requires every application result to succeed. It does not mean the schedule was truncated. Some safeguards were deliberately fitted to these known failures: duration-question patterns and the show/clarify/rephrase exceptions to the personal-claim filter are literal rules. Other verbs and phrasings are not covered. In-sample improvements from these guards do not demonstrate generalization or isolate a prompt-only improvement. Existing local tone policies also use literal phrase rules; neither arm provides general semantic validation.

## Concrete results and agent comparison

| Area | Fresh old Luna | Fresh revised Luna | Saved agents and root assessment |
|---|---|---|---|
| User check-in mistaken for contact question | Wrong speaker and invented user feelings in 2/2 repeats | No invented reply in 2/2; weak or wrong-source calm cues removed by grounding | Confirms the problem identified independently by Astra low, Sol high and root, with a measurable improvement on this case |
| Elapsed call time invented from context window | False short-duration answer in 1/2 repeats | No duration answer in 2/2 | Matches Astra/Sol/root diagnosis. First repeat alone would have hidden the remaining old-arm failure |
| Immediate show/clarify actions | Old filter still discards generated harmless show actions | Requested show actions retained in both repeats of both selected action cases | Supports root's diagnosis of an overly broad first-person filter; raw generation was already often useful |
| Garbled fragment interpreted as greeting | Failure in 2/2 | Failure in 2/2; one revised warmth cue also survives | Saved Sol-high answer made the same mistake. Root's earlier abstention was unblinded and cannot establish model superiority |
| Third-party boundary | Confuses not speaking to someone with not discussing them; weak calm and unsupported promise appear | Avoids explicit dyadic-withdrawal label, but still conflates speaking-to with discussing | Saved Sol also mixed boundary/withdrawal and proposed a promise. This target is only partly improved |
| Ambiguous acknowledgment, banter, unfinished user thought | Some useful clarification, but ownership and intent errors vary by repeat | More grounded uncertainty; repetitive or contextually awkward replies remain, including a weak topic-opening question | Sol's clarification/banter/unfinished-thought handling was more useful in some saved cases, but its intent judgments were not verified truth |
| Latest summary | Historical chain conflated topics, lost project concern and final narrowing, strengthened ambiguous claims | Both new summaries separate the social plan from testing, preserve project concern/reassurance and narrowed choices; only 1/2 explicitly preserves the isolated-sentence complaint, neither names the final specific shirt | Substantially addresses Astra/Sol/root summary diagnoses, with remaining coverage omissions |
| Memory scope/categories | Temporary dispute typed as relationship preference 2/2; open repeat offer as commitment 2/2 | Dispute corrected only 1/2; repeat offer omitted 2/2, not retained with a better type; run-specific cost scoped 2/2 | Partial progress toward all reviewers' scope concerns, not a blanket memory-quality win |
| Remaining memory regressions | Undated same-occasion routine persists; completed work sometimes a commitment | Same routine persists 2/2; completed-work commitment still appears 1/2, nervousness mislabeled commitment 1/2; routine greeting clutter appears 1/2 | Category/temporal validation still needs work beyond prompt instructions |

The five saved isolated Sol-high live answers use matching source speech/IDs but older prompts/schema. Astra-low and Sol-high September 16 artifacts are independent diagnostic reviews, not alternative answers to every API request. Root's original call assessment preceded those reviews; this comparison is non-blinded and knows all earlier findings. No reused answer counts as a new inference or independent repeat. Earlier Terra API results remain historical context only; no Terra, agent or local-model inference ran in this evaluation.

We did not adopt Sol's blanket suggestion to clear replies after every new contact utterance: earlier live evidence demonstrated that this can starve guidance. The current bounded supersession check still requires a live recheck.

The sixth saved isolated Sol answer is a summary. It and root's saved summary retain specific advice about reviewing generated code that both fresh Luna summary versions omit in both repeats. Sol also avoids strengthening encountered merge conflicts into resolved conflicts. Root's reconstructed memory output keeps the temporary dispute and completed work as shared references and omits greeting clutter; its extraction input was not exact-equal, and root was unblinded. No isolated Sol extraction exists.

## Guidance, facial evidence and cost

| Metric,32 responses per arm | Old | Revised frozen version |
|---|---:|---:|
| Responses containing any reply before filtering |30|27|
| Responses containing any reply after filtering |26|25, plus 1 application error|
| Replies available in historical-arrival simulation |25|23, plus 1 application error|
| Raw tone/cue items |60|32|
| Accepted tone/cue items |60|18|
| Raw cue items citing visual evidence |0|0|
| Raw cue items with source turn IDs |0/60|32/32|
| Median measured request duration |6.99 s|6.53 s|

Fewer cues are not an accuracy score. All 32 revised raw cue items contain source IDs, but some IDs are stale or belong to the wrong speaker. Grounding removes 14 items. All selected guidance inputs preserve both sensor streams; unavailable signals remain unavailable. Zero visual citations across 64 responses does not prove zero internal visual influence or establish facial-recognition accuracy. No face/no-face ablation or human expression ground truth was added.

Mechanical citation audit: 2/32 revised raw cue items cite no contact turn,3/32 include a source at least 24 seconds old, and 0/32 cite an unsupplied ID. Among 18 accepted items, all have a contact citation and none have an old or unsupplied ID; 3 also cite user context. User context beside a contact anchor can legitimately support a cue and is not automatically an error. These properties still do not establish semantic entailment.

After the application correction below, revised reply availability is 26/32 immediately and 24/32 in arrival simulation. This simulation applies measured request duration and original later speech; it is not a GUI/live-user usefulness test. The comparison does not establish that more or fewer suggestions are better.

There is **no net reply-availability gain**: 26/32 versus 26/32 immediately, and 24/32 revised versus 25/32 old in arrival simulation. Extraction also becomes slower in these samples: median 6.61 s→8.46 s, maximum 8.83 s→10.72 s, with total output tokens 5,095→5,542 across eight requests per arm.

**Aggregate committed: $0.09749827/$0.30.** Returned usage accounts for $0.09493427; an additional $0.002564 reservation is conservatively retained for an initial local startup failure during credential-dependent client construction, before dispatch. The copied baseline initially resolved the key from its copied directory. The continuation supplied the existing repository credential through the child environment without writing or displaying it. Original failure/ledger remain intact. No API failure was silently retried, no budget reset occurred, and the cap did not stop the schedule. Remaining authorization for this same evaluation is $0.20250173, not a new budget.

The 44 matched requests per arm cost $0.04911135 old versus $0.04292048 revised (12.6% less). Pricing all input at the configured uncached input rate and retaining actual output gives $0.0663688 versus $0.0608176 (8.4% less); unequal cache use matters. Guidance input increased by 121 tokens per request on average, while outputs shortened. Extraction alone increases 4.7% under this uncached normalization despite slightly lower billed estimates. These are configured usage-priced estimates, not provider invoices or passes of the original F07 visual-only 10% cost gate.

The historical latest summary used 23 requests, about 147.55 summed request-seconds and $0.02026515. New whole summaries each used one request: 6.11 s/$0.00208360 and 7.14 s/$0.00081884; repeat caching lowers the second cost. These historical-versus-fresh conditions are not controlled latency or billing comparisons. All source text fits the existing summary cap; no further token-cap increase was needed.

## Application correction and verification

One model answer returned `status=updated` with empty cue lists. The wire schema accepted it, but the stricter application model rejected it, losing otherwise usable replies. After all 90 frozen API requests finished, the shared canonicalizer was changed to treat that exact empty result as insufficient evidence, preserving its explanation and independently grounded replies. It does not invent a cue or relax validation of supplied cue content.

The new regression failed before the fix and passes afterward. All 56 affected checks and the full 334-test suite pass. Offline replay of all 32 revised guidance answers verifies byte-identical model inputs/instructions/schema/caps and changes only the failed application result. Original raw answer, error, charges and frozen source remain preserved; no extra inference or retroactive success was invented.

Private reproducible evidence: `build/call-prompt-api-20260917/` contains frozen requests/criteria/schedule/source hashes, tested source copy, raw and parsed answers, original and continued ledgers, case-by-case root assessments, timing simulation, corrected replay and test XML. Original private logs and approved memories/summary were not modified. Echo remains excluded.

`verify_frozen.py before|after` regenerates all 16 distinct guidance requests per arm from the preserved source packages and checks input/instructions/schema/caps exactly, without inference. Both pass. All 22 source files per arm also match their named Git commits after newline normalization only (`git-source-verification.json`), beyond the artifact-internal hash checks. The original paid runner's working-tree hash check is intentionally invalid after the post-test correction; do not bypass it or rerun paid work. `preservation-check.json` verifies unchanged historical references/frozen inputs and confines the changed production file to `interpretation.py`; the git diff records its two added lines. The corrected replay separately records final source hashes.

The entire private evidence directory is Git-ignored, verified with `git check-ignore`, and must never be force-added. Commit only the reviewed source/test change, this sanitized report and its plan/context/test-index status updates on the separate branch; exclude private logs, credentials, model outputs, approved data and unrelated personal files.

Fresh post-API tool-disabled Claude Opus 5 review and its correction follow-up verified only `claude-opus-5`, one turn each, and returned **CLEAR FOR DIAGNOSTIC CHECKPOINT**. The first review's disclosure conditions are recorded and resolved; both raw reviews are preserved. CLI authentication was verified as the existing Claude subscription, separate from the Luna API ledger. Necessary live rechecks and final post-human review remain pending. Keep the separate correction branch; no merge/push to main or F07 completion is authorized by this diagnostic. The original 144-response acceptance design, held-out separation, three consenting checks, 85% thresholds, 400-token allowance, separate 10% cost gate, maximum two tuning rounds and September 23/27 deadlines remain unchanged; protect F08's October 1 Windows target.
