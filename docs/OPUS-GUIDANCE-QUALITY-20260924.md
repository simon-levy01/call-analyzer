# Opus guidance-quality experiment — September24

User requested a committed checkpoint, separate branch, high-effort Claude advice and candidate-versus-current testing.

- Baseline committed as `0488b20` on `codex/qt-ui-migration`; experiment branch `codex/opus-guidance-quality-20260924`. No push. Unrelated CV files and private evidence excluded.
- Baseline full offline suite: **390 passed in60.41s**.
- Exact **claude-opus-5-5**, **high** effort, subscription CLI, tools disabled; actual returned model verified. Supplied current source and the150-turn search call's displayed outputs/annotations. The88-turn transfer transcript was withheld from the consultation. Claude performed a source/evidence review and six hypothetical behavioral comparisons, not an executed Luna test.

## Claude's recommendation

Replace only `GUIDANCE_INSTRUCTIONS`: consider a contact turn handled once the user substantively responds, suggest a grounded next move rather than rephrasing that answer, explicitly track speaker/pronoun ownership, avoid assigning affect to likely transcription fragments, and distinguish a third-party refusal from ending this discussion. Preserve uncertain memory grounding and safety rules. Claude warns that equal output volume is plausible but not assured, and disputes several previous subjective grades.

Claude also noticed that the existing broad refusal reset can clear guidance when the contact refuses to speak to a third party. That is a separate unimplemented observation, not part of its one-prompt candidate.

## Actual offline comparison: candidate rejected before API

The exact proposed replacement was tested through real request preparation on all80 frozen snapshots from both complete calls, with OpenAI construction blocked. Existing schema,5000-token input ceiling, source payload and model settings were preserved.

| Measure | Current | Exact Opus proposal |
|---|---:|---:|
| Guidance-instruction estimated tokens |1376|2101|
| Snapshots preserving original payload |80|11|
| Additional evidence pruning, request still prepares |0|50|
| Input-ceiling exceptions |0|19|

The proposal fails its own no-additional-evidence-pruning gate. It was **not applied** to product code. No fresh Luna calls were made; there is no measured candidate suggestion count or usefulness score. Hypothetical improvements from Claude are not results.

## Remaining work and authorization

Shorten the proposal, recheck evidence preservation, then freeze and evaluate it. User selection of API versus subscription-agent comparison is pending. The offered API option continues the same recovery ledger at **$0.31991499/$0.70**, including the unchanged uncertain reservation; no reset or new spending is authorized by this report. Both complete-call baseline outputs already exist and can be reused exactly with explicit provenance.

The evaluation must report actual UI-rendered text, separate useful/partial/bad judgments, cue usefulness, duplicates, memory safety, latency and cost. Require same-or-more volume on **both** calls; Claude's suggested90% transfer-volume threshold is weaker than the user's request and is not adopted. No experiment promotion or push is implied.

Private artifacts: `build/opus-guidance-quality-20260924/` contains the full consultation prompt, verified raw response, manifest, exact proposed prompt,80-case preflight and frozen comparison plan. Helpers: `build/opus_quality_consult_20260924.py` (single-use consultation) and `build/check_opus_prompt_20260924.py` (offline preparation check). Never rerun the single-use consultation directory or upload private call evidence to Git.
