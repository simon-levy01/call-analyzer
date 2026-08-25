# F04 — Multimodal tone and cue interpretation

**Status:** Complete
**Prepared and approved:** 2026-08-25
**Roadmap target:** 2026-09-09
**Repository baseline:** local `main`, `origin/main`, and GitHub `main` verified at `96df95d8f92413efa095962768ab8b9de79a2996` before planning
**Reviewed implementation commit:** `2ad5851710cf0328e08cd06b6d1a5a3615f07397`, pushed and pointer-verified on 2026-08-26

## Outcome

F04 turns recent finalized English conversation turns plus compact local observations into one cautious, stable Interpretation Update. It may show:

- up to three hypotheses about the recent conversation atmosphere;
- up to three possible social cues from the remote participant;
- `low`, `medium`, or `high` confidence for each item; and
- a short explanation naming the language, vocal, or visual observations that contributed.

The result is a hypothesis, never a claim about true emotion or intention. The system can instead report `insufficient_evidence` or `conflicting_evidence`. It never displays 100% confidence.

The minimum UI is one replace-in-place interpretation card and one explicit **Check with Terra** action. Interface design beyond that belongs to later work.

## Approved decisions

1. **Language and F03 boundary:** F04 is English-only. Hebrew and language switching are excluded because the current local transcription is not accurate enough. F04 preserves F03 behavior but may make the minimum F03 integration change needed to expose bounded utterance timing and derived remote vocal observations; it does not redesign capture, transcription, attribution, or `ConversationTurn`.
2. **Interpretation subjects:** tone hypotheses may describe the recent conversation atmosphere. Social cues concern only the remote participant. The user's finalized words are context only; F04 does not infer the user's social cues, face, voice, emotion, or intention.
3. **Output:** an update contains zero to three tone hypotheses and zero to three remote social cues, or a top-level abstention/conflict status. Item confidence is only `low`, `medium`, or `high`.
4. **Live model candidate:** compare `gpt-5.6-luna` with reasoning `none` and `low`; the cheapest Luna profile that passes is the automatic live model.
5. **Stronger model:** compare `gpt-5.6-terra` with reasoning `none` and `low`, but never use it automatically. One Terra request can run only after the user clicks **Check with Terra** and chooses an evaluated reasoning level.
6. **Local vocal processing:** use existing NumPy/PyAV audio samples and F03 timestamps. Do not add a speech-emotion package unless the simple features fail the modality-uplift gate and the plan is revised.
7. **Memory:** F04 consumes no contact memory and adds no dormant memory field, hook, provider, or stub. F05 must later add bounded, approved memory enrichment and rerun interpretation evaluation.
8. **Privacy:** no raw video, video frames, raw audio, full landmark history, or full blendshape history is sent to OpenAI. Raw runtime frames and audio remain memory-only under the F02/F03 contracts.
9. **Cadence:** start after two finalized turns; require at least one new finalized turn; allow at most one automatic request per 15 seconds; coalesce rapid turns into one latest pending request.
10. **Stability:** keep a normal card visible for at least 12 seconds. Replace it only for a meaningful status, label, confidence, or contributing-modality change. Suppress duplicates and stale results.
11. **Budgets:** default session warning at `$0.15`, hard limit at `$0.25`, and real-evaluation hard limit at `$1.50`. All cloud use counts from API usage tokens and current configured prices.
12. **Validation:** deterministic fake-model tests are the normal test path. A fixed 12-scenario project-owned real-model set and one short consenting WhatsApp call are required before completion.

## Verified starting point

The planning pass read the master plan, F02/F03 plans, ADRs, README, glossary, dependency manifest, source modules, tests, recent Git history, live GitHub pointer, and the complete Trello board.

- F01 and F02 are complete.
- The previously reviewed F03 feature is complete at `96df95d`; WhatsApp passed; Zoom and Google Meet remain `WAIVED — not passed`.
- The working tree contains a separate post-completion F03 revision that makes the product English-only and changes the production model from `small` to `mobiuslabsgmbh/faster-whisper-large-v3-turbo`. That revision is not part of `96df95d`. F04 implementation starts only after the revision has passed its required regression/performance checks, review, commit, push, and pointer verification, and this plan records the accepted commit as its new implementation baseline.
- The current combined app owns final-turn delivery in the Tk polling path. F04 should attach at that narrow handoff instead of introducing an event bus.
- `ConversationTurn` already provides finalized text, speaker attribution, source, and time. F04 consumes finalized turns only.
- F03 already holds normalized mono 16 kHz PCM and monotonic utterance boundaries before discarding audio. Remote vocal features belong at that existing lifecycle point.
- F02 produces `FacialSignal` for the manually selected remote face. F04 needs only a narrow current-signal read and immediate aggregation, not retained raw signals.
- Pydantic models already use `extra="forbid"`; F04 structured outputs must follow that pattern.
- Existing tests already inject callable/model factories. The fake interpreter should reuse this pattern rather than introduce a provider hierarchy.

Planning verification on the then-current tree passed 78 tests, `pip check`, the 500-turn/two-speaker headless check, and F02 replay. These are planning evidence, not substitutes for implementation reruns.

## Contracts that must remain true

### F02

- Runtime frames remain in memory and are never saved or uploaded.
- Only the selected remote face receives landmark/blendshape processing; other detected faces remain boxes only.
- After six seconds without the selected face, visual tracking requires explicit **Continue tracking** and never silently chooses a replacement.
- Visual loss does not stop a healthy F03 audio/transcription session.

### F03

- Physical microphone/playback sources determine speaker roles; F04 does not add diarization or rewrite attribution.
- Only ordered finalized turns enter interpretation context.
- Production F03 exposes and passes English (`en`) only. Retained Hebrew/Auto fixtures, detection helpers, or benchmark profiles are evaluation-only and cannot be reached through the production session boundary. F04 does not detect, select, or infer transcript language.
- The accepted English model must preserve final-only delivery, source attribution, chronological ordering, timestamps, bounded queues, offline runtime, teardown, and the existing `ConversationTurn` fields.
- Playback remains endpoint-wide and visibly warned; WhatsApp-over-Chrome source priority remains unchanged.
- Raw audio and transcripts remain session-only and are not persisted by F04.
- F04 does not silently replace an audio or video source.

### Existing privacy decisions

[ADR-0002](../docs/adr/0002-keep-memory-local-and-video-derived.md) permits derived facial observations to leave the device, not raw frames. F04 narrows this further to compact aggregates. No new ADR is needed for the approved feature-level request/cadence choices. A future change that adds raw-media egress, persistence, a different trust boundary, or automatic expensive fallback requires a new explicit decision.

## Scope

### Included

- Strict interpretation input/output models.
- Remote-only local vocal features derived before PCM is discarded.
- Compact temporal aggregation of the selected remote face's current F02 signal.
- A bounded recent-turn/context builder.
- Stateless OpenAI structured interpretation with live usage/cost accounting.
- Cadence, coalescing, stale-result, duplicate-result, and card-stability policies.
- One interpretation card and one per-request manual Terra action.
- Replayable automated tests, fixed real-model comparison, and one manual WhatsApp validation.

### Excluded

- Contact memory, retrieval, personalization, or memory-aware evaluation; these are F05.
- Reply suggestions, reminders, follow-up questions, summaries, or memory proposals; these are F06.
- Text-chat product work.
- Analysis of the user's face, prosody, social cues, emotion, or intention.
- Facial identity recognition.
- Raw-frame retention, raw-audio retention, external vision, or external audio upload.
- Emotion/intent detection claims or 100% confidence.
- A new event bus, plugin system, provider framework, generalized settings system, or later-feature scaffolding.
- History, charts, feedback editing, or a polished final interface.
- Automatic Luna-to-Terra fallback.

## Domain contract

Use strict Pydantic models and controlled values. Names may be adjusted to match existing module style, but the semantics are fixed.

### Interpretation status

- `updated`
- `insufficient_evidence`
- `conflicting_evidence`

An abstention/conflict result has no tone or cue items and includes one short explanation. It is not a fourth confidence level.

### Tone hypotheses

Tone hypotheses describe the recent conversation atmosphere, using only these initial kinds:

- `positive_warm`
- `neutral_calm`
- `sad_low_energy`
- `tense_negative`
- `energetic_high_energy`
- `emotionally_intense`

Mixed or unclear evidence is handled through abstention/conflict, not an `unclear` tone.

### Remote social cues

- `humor`
- `sarcasm`
- `interest_engagement`
- `discomfort`
- `uncertainty`
- `disengagement_withdrawal`
- `other`, with a short plain-English summary

Every social cue is explicitly scoped to the remote participant. The schema has no `user` cue subject.

### Item fields

Each emitted item contains:

- controlled kind;
- `low`, `medium`, or `high` confidence;
- one short plain-English hypothesis;
- one short evidence explanation;
- the non-empty contributing modality set: `language`, `vocal`, and/or `visual`.

Use an F04-restricted confidence type containing only `low`, `medium`, and `high`; do not reuse any broader existing enum that also permits `unclear`. Insufficient or conflicting evidence belongs in the top-level interpretation status.

Evidence describes observations, not conclusions: for example, wording contrast, faster delivery relative to the remote speaker's session baseline, or increased mouth/brow movement. It does not invent an unavailable modality or state that a person truly feels or intends something.

## Smallest reliable architecture

```text
F03 finalized turns ───────────────┐
F03 remote PCM/timing → vocal data ├→ bounded snapshot → Luna → stable card
F02 selected-face signal → buckets ┘                    ↘ manual Terra check
```

### 1. Local evidence records

Keep `ConversationTurn` unchanged unless implementation proves a direct extension is smaller. A small F04 snapshot record joins existing turns with time-aligned remote vocal and visual aggregates. The minimal F03 integration may carry an internal utterance correlation key and start/end bounds until its final turn is released; it must not retain PCM afterward or expose benchmark-only language modes.

Remote vocal observations are derived while F03 still owns the utterance samples:

- utterance duration;
- relative RMS energy against a session-local remote baseline;
- voiced/silence ratio;
- words per voiced second after final transcription;
- pause/turn gap; and
- detected overlap with the user's finalized/capture interval.

These are signal descriptions, not emotion scores. If there is too little baseline speech, clipping, silence, capture failure, or unreliable timing, mark vocal evidence unavailable. Do not fabricate neutral values. Discard samples on the existing F03 lifecycle.

At the existing roughly 100 ms UI poll, reduce the current selected-face signal immediately into two-second buckets. Retain at most 90 seconds of compact aggregates describing:

- face availability/reliability;
- face-region movement relative to recent buckets; and
- relative change in a small documented smile, brow, eye, and mouth movement grouping.

Do not retain frames, full landmarks, full blendshapes, or locally named emotions. Missing/unreliable visual evidence is explicit and does not stop transcription.

### 2. Bounded snapshot builder

For each eligible request:

- select at most eight newest finalized turns within the newest 90 seconds, whichever bound is smaller;
- include the user's words only as language context;
- include remote vocal observations only;
- include compact selected-remote-face aggregates only;
- target about 1,000 estimated transcript tokens;
- target about 1,500 estimated total input tokens, including fixed instructions and compact signals;
- drop oldest complete turns first and never split speaker attribution; and
- cap model output at 400 tokens, including reasoning usage where the API accounts for it.

Use a small conservative English token estimator with fixed prompt overhead rather than adding a tokenizer dependency. API `usage` is authoritative after each real request. The evaluation and live guard must keep measured transcript input near 1,000 and measured total input at or below 1,650 tokens (10% above the 1,500 target); if the estimator crosses that ceiling, tighten it before continuing.

### 3. Coordinator

Add one small F04 coordinator, not a bus or service framework:

- first automatic request after two finalized turns;
- subsequent request only after at least one new finalized turn;
- minimum 15 seconds between automatic request starts;
- one request in flight and at most one latest pending snapshot;
- coalesce intervening turns into the pending snapshot;
- discard a result older than the last accepted snapshot/session generation;
- suppress output equivalent under normalized status, kinds, confidences, and contributing modality sets;
- never block Tk, F02 capture, or F03 transcription.

Cloud failure changes only interpretation availability. Local capture, facial processing, and transcription continue safely.

### 4. OpenAI call

Use the official Python SDK and Responses API structured parsing into the strict Pydantic result. Send text only, set `store=false`, provide no prior response/conversation identifier, use no tools, and keep every call stateless. The prompt must:

- delimit conversation content as untrusted evidence, not instructions;
- state the remote-only interpretation boundary;
- require hypotheses/abstention rather than true-emotion or true-intention claims;
- prohibit evidence from unavailable modalities;
- prefer fewer items over weak filler; and
- require the approved controlled schema.

The live candidate is the cheapest passing profile among Luna `none` and Luna `low`. Terra `none` and `low` are evaluation candidates and manual checks only.

Retry at most once for transient rate-limit or server failures, after a short bounded delay and only if the request remains current and within budget. Do not retry refusal, invalid structured output, cancelled/stale work, authentication failure, or hard-budget rejection.

### 5. Minimal card and manual Terra action

The single card shows:

- interpretation status;
- up to three tone hypotheses;
- up to three remote social cues;
- confidence and evidence for each item;
- last accepted update time;
- interpretation availability; and
- session estimated spend.

The **Check with Terra** action:

- is unavailable without eligible context/API key, during another cloud request, or at the hard limit;
- asks the user to choose evaluated reasoning `none` or `low` and shows the current maximum estimated request cost;
- runs once against the newest bounded snapshot;
- counts toward the same session warning/limit;
- may replace the card immediately when meaningfully different, after which the 12-second minimum applies; and
- reports a short `no meaningful change` completion without refreshing an equivalent card.

Normal Luna scheduling resumes afterward. Terra is never enabled periodically and never selected because Luna failed without a separate user action.

## Technology decision

### Selected

| Need | Choice | Licence / Windows / cost reason |
|---|---|---|
| Structured cloud interpretation | Official `openai` Python SDK, Responses API, strict Pydantic parsing | Apache-2.0 SDK; existing Pydantic pattern; supported on Windows; avoids hand-written response/schema handling |
| Vocal features | Existing NumPy, PyAV samples, F03 boundaries, and finalized word count | Already installed; negligible CPU, no GPU, no new native runtime, no audio retention |
| Visual aggregates | Existing MediaPipe output reduced with current NumPy/model code | Already installed; local CPU/GPU behavior unchanged; no external vision |
| Live model candidate | `gpt-5.6-luna`, evaluated at `none` and `low` | Current cost-sensitive model with Structured Outputs; quality must pass project data |
| Difficult explicit check | `gpt-5.6-terra`, manual `none` or `low` only | Stronger/costlier candidate; user approves each request |

### Rejected for F04

| Option | Licence | Windows/install and compute risk | Decision |
|---|---|---|---|
| `librosa` 1.x | ISC | Python-friendly but pulls SciPy/Numba/scikit-learn/soundfile/soxr and related packages; CPU-only features still add a large stack | Reject: simple duration/energy/rate/pause/overlap features need none of it |
| openSMILE 2.6 | Core research licence is not unrestricted product/commercial use | Windows binaries exist and eGeMAPS is useful, but native packaging/licensing add material risk; CPU, no GPU needed | Reject unless licensing is resolved and simple features measurably fail |
| Parselmouth/Praat 0.4.x | GPLv3 | Windows wheels exist, but compiled DLL packaging and reciprocal licence require review; CPU only | Reject: pitch/intensity sophistication is not yet justified |
| PyWORLD 0.3.x | MIT | Narrow F0/vocoder tool with compiled/native Windows risk; upstream describes Windows support as limited; CPU only | Reject: too narrow for the first feature set |
| Hume or another paid emotion API | Service terms/cost | Sends additional sensitive signals externally and adds another provider | Reject: no evidence it is needed and outside the approved privacy/budget path |
| Raw audio to OpenAI | Service terms/cost | Supported F04 text models do not accept audio; external audio changes privacy and cost | Reject: no need demonstrated; requires a separate user decision |

If the dependency-free vocal modality fails the uplift gate, stop and revise the plan. Do not silently add pitch extraction, a native package, or an audio service.

## Cost controls

As verified on 2026-08-25:

- Luna: `$0.20`/million input tokens, `$0.02` cached input, `$1.20` output.
- Terra: `$2.00`/million input tokens, `$0.20` cached input, `$12.00` output.

At the 1,500-input/400-output target, conservatively treating every input token
as a cache write:

- Luna request maximum: `$0.000855`;
- Luna maximum at one request every 15 seconds: `$0.2052` per conversation hour before suppression;
- Terra manual request maximum: `$0.00855`.

At the approved 10% input ceiling (1,650 input/400 output), the corresponding conservative figures are `$0.0008925` per Luna request, `$0.2142` per Luna conversation hour, and `$0.008925` per manual Terra request.

Track input, cached-input when reported, output/reasoning, request count, model, reasoning level, and calculated dollars per session. Store no conversation content in cost records. Compare calculations to API usage in tests with fixed fake usage and in the real evaluation report.

Defaults:

- warning at `$0.15`;
- hard session limit at `$0.25`;
- values configurable through environment configuration, not a settings screen;
- reject a request whose conservative maximum could cross the hard limit;
- interpretation becomes visibly unavailable at the limit while F02/F03 continue;
- current model prices are explicit configuration and must be reverified before implementation/real evaluation.

Terra at the automatic 15-second cadence would cost about `$1.872`/hour and is therefore prohibited. If the user later wants Terra as a live automatic model, that is a new approval covering the model and a revised session cap.

## Update stability

- A normal accepted card remains for at least 12 seconds.
- An automatic result waits until that minimum expires before replacement.
- A user-requested, meaningfully different Terra result may replace immediately; its replacement then receives the full 12 seconds.
- Cloud unavailable, authentication failure, refusal, or budget-limit state may replace immediately because continued availability information is more important than the display minimum.
- Duplicate results never replace or reset display time.
- Only the newest pending snapshot survives; stale completed results are discarded.
- Status, controlled kind, confidence, or contributing modality-set change is meaningful. Rewording alone is not.
- At 15 seconds minimum cadence, normal updates cannot exceed four per minute.

## Implementation slices

Each slice must keep the full existing suite green and add the smallest relevant check.

Before slice 1, finish and accept the English-only F03 revision. Run the full suite, offline audio replay, and the existing 600-second concurrent F02+F03 benchmark with the accepted model. Reconcile the benchmark's configured overlap-maximum threshold with F03's approved threshold instead of silently changing it. Record latency, F02 rate, Tk responsiveness, queue bounds, working-set/VRAM headroom, and teardown; evidence from the prior `small` model does not validate the new large-v3-turbo baseline. F04 then reruns the relevant combined resource and latency gates after integration.

1. **Contracts and deterministic coordinator — exact first slice.** Add strict interpretation/evidence models, bounded snapshot/cadence/stale/duplicate logic, a callable fake interpreter, and focused tests. No OpenAI call, UI, or signal extraction yet.
2. **Remote vocal observations.** Derive simple features at the existing F03 in-memory utterance boundary, join them to finalized remote turns, mark unreliable/missing evidence, and prove samples are discarded.
3. **Remote visual aggregation.** Expose only the current selected-face signal needed by the existing polling path, reduce it into two-second/90-second aggregates, and prove no frames/full signal history are retained.
4. **Luna integration and accounting.** Add the official SDK/bounded estimator, stateless strict Responses call, retry/failure behavior, usage accounting, budgets, and deterministic HTTP/model fakes. No real API call in normal tests.
5. **Stable card and manual Terra action.** Add the one card, availability/cost state, display timing, and one-shot Terra `none`/`low` control without a settings framework.
6. **Automated replay validation.** Complete modality, lifecycle, privacy, cadence, stale/duplicate, and failure coverage.
7. **Fixed real-model comparison.** Run only after automated gates pass and within the `$1.50` evaluation cap; select the live Luna profile or stop with evidence.
8. **Manual WhatsApp validation.** Run one consenting short scripted call and obtain explicit user acceptance.
9. **Review and finish.** Run the required Claude review, accepted corrections, complete reruns, correction review, final commit, push, and pointer verification.

## Execution status — 2026-08-25

- [x] Contracts and deterministic coordinator.
- [x] Remote vocal observations.
- [x] Remote visual aggregation.
- [x] Luna structured integration and accounting.
- [x] Stable card and manual Terra action.
- [x] Automated replay validation.
- [x] Fixed real-model comparison and modality uplift.
- [x] Manual WhatsApp validation — user explicitly approved the corrected live behavior on 2026-08-26.
- [x] Review, corrections, reruns, and final correction review.
- [x] Final commit, push, and pointer reconciliation.

Automated evidence: 126 tests pass with no API spend; `pip check`, bytecode compilation, and diff hygiene pass. The 500-turn foundation, selected-face replay, offline audio replay, and approved basic generated call-fixture checks pass with zero network attempts and zero audio artifacts. The post-integration 600-second concurrent benchmark passes with 1.348-second single-source p95, 2.696/2.767-second overlap p95/max, queue peak/final 1/0, zero saturation, 24.99 F02 signals/second, 14.8 ms frame-age p95, -6.44 MiB/min post-warm-up growth, and 0/0 workers/results after teardown. Twelve fixed synthetic English scenarios and the capped 96+24-call comparison runner are defined; the API key is loaded only from the environment or ignored `.env.local`, and the runner shares a $1.50 hard evaluation ledger.

Paid aggregate evidence: a complete 120-call comparison cost `$0.153844`; Luna `low` passed Stage A with 80% primary accuracy, 100% abstention, 88.9% acceptable items, 100% acceptable high-confidence items, and 4.654-second p95. Its then-current Stage B failed both designated recovery cases. After correcting the controlled sarcasm label and documenting the normalized visual threshold, both designated cases passed focused real calls. A final 96-call comparison on the corrected code cost `$0.1590704`; Luna `low` achieved 100% primary accuracy, 100% abstention, 100% acceptable items, and 100% acceptable high-confidence items, but its 5.585-second p95 exceeded the then-current five-second gate, so the runner selected no winner and did not start Stage B. A separate 24-call latency diagnostic measured 4.894-second p95 with one 12.621-second outlier. No private conversation content or raw media was used or recorded. On 2026-08-25 the user approved raising the p95 acceptance gate to six seconds; the succeeding final evidence is recorded below.

Cost reconciliation on 2026-08-26 found that these recorded run totals were
local estimates which omitted GPT-5.6 `cache_write_tokens`; the OpenAI dashboard
remains the billing source of truth. Accounting now records cache writes at
1.25× the uncached-input rate, reserves against the all-cache-write maximum,
and labels the UI counter as this call's estimated interpretation spend rather
than a project/account total.

Final paid evidence after the approved six-second gate, low text verbosity, and local deterministic preflight: 60 actual API calls across 120 scenario evaluations cost `$0.0809872`. Luna `none` was selected. Its Stage A primary accuracy, abstention, acceptable emitted items, and acceptable high-confidence items were all 100%, with 3.043-second p95. Stage B recorded the same four 100% quality rates with 4.166-second p95. Both designated modality-recovery cases passed, with zero additional unacceptable items and zero unsupported high-confidence items. All evidence modalities and input ceilings were valid, and prohibited claims remained zero. Validation 2 passes.

## Automated validation

Normal automated tests use a deterministic fake model and spend no API credit. Project-owned synthetic/replay fixtures contain no private conversation.

The user-approved `assets/f04/basic-video-chat` bundle is the permanent basic end-to-end replay input from 2026-08-25. It contains an 86.6-second fictional call, speaker-separated microphone/contact PCM, exact turn timing, six authored remote facial poses, indirect and direct memory references, and expected cue/memory coverage. Automated checks verify hashes, timing, zero speaker-stem crossover, remote-face landmarks/blendshapes, and pose variation. This generated fixture supplements the 12 controlled scenarios and manual WhatsApp validation; it is not real-call quality evidence, and its authored pose labels are never displayed as emotional truth.

The approved 53.85-second `assets/f04/heygen-video-chat.mp4` adds a more
naturalistic compressed-video replay with neural lip sync, speech, and changing
facial signals. Automated checks verify its hash, dimensions, duration, remote
face, landmarks, and blendshape variation. HeyGen produced only Maya as the
animated narrator, kept Alex static, added free-tier watermarks, and omitted the
opening `the event` line; therefore this is a realism stress fixture, not a
speaker-attribution or indirect-memory oracle, and it does not replace the basic
fixture or a consenting live call.

Generated-media replay evidence: the production transcriber recovered all 15
basic-fixture turns at 1.8% word error rate. Full-video processing detected the
remote face in 324/324 sampled frames and produced 44 bounded visual buckets.
After correcting stale direct-language cue precedence and two explicit sarcasm
phrases, the exact fixture transcript plus those full-video observations passed
5/5 checkpoints: discomfort, uncertainty, sarcasm twice, and warm relief. The
final replay needed one cloud call and cost `$0.0003852`; the other four results
used the local cautious policy. The HeyGen replay recovered every required
keyword, detected the face in 225/225 sampled frames, and produced 27 visual
buckets. Because HeyGen has only one animated narrator, its result remains media
and signal evidence rather than speaker-attribution evidence. The complete
zero-cost regression suite still passes: 126 tests, dependency check, bytecode
compilation, diff hygiene, and ignored-key-file verification.

The first consenting WhatsApp attempt on 2026-08-25 did not pass: the user's
microphone produced too few turns, and an ongoing joke changed among humor,
neutral, and other atmosphere labels. Deterministic repros confirmed that the
microphone default of 250 discarded quiet RMS-150 speech, the snapshot kept only
8 turns/90 seconds, and request fitting discarded conversation turns before old
visual rows. The corrected build uses a microphone threshold of 100, retains up
to 16 turns/three minutes within the unchanged 1,000-token transcript and
1,650-token request ceilings, omits repeated speaker labels, and trims old visual
then vocal rows before complete conversation turns. Luna `low` passed the fixed
24-case transcript/all-modality comparison with 100% quality rates and 3.706-second
p95 for `$0.004154`, so it is the live default. A full generated-video replay then
held humor across turns 6, 7, 10, and 11 and changed to sarcasm at turn 12, retaining
all 12 turns and detecting 324/324 face samples. Manual WhatsApp approval remains
open pending a corrected live retest.

After the corrected live behavior worked well, the user approved showing up to
two additional useful items. The wire boundary now keeps at most three distinct
tone/cue items total, ordered by confidence, while local cautious rules may still
return one clear item. The post-change Luna `low` 24-case gate passed: 10 results
contained multiple items, the maximum was two, primary accuracy and acceptable
high-confidence precision were 100%, acceptable emitted-item precision was 83.3%,
and p95 was 3.298 seconds for `$0.0042092`.

The required preliminary tool-disabled Claude Opus 5 review ran on 2026-08-26
against the complete tracked and untracked F04 patch. All 14 actionable findings
were accepted and corrected: no-remote abstention, stop/Terra stale-work guards,
newest-turn visual inclusion, vocal turn indexing, conservative retry billing,
partial evaluation reports, separate model-only metrics, Terra budget gating,
fixture sampling, package-media exclusion, bounded startup failures, token-safe
keyword matching, and the ignored local HeyGen log. The corrected zero-cost gate
passes 126 tests plus dependency, bytecode, and diff checks. Correction review is
still required before commit.

The first correction-review pass confirmed all 14 original findings resolved
and found three follow-ups. Two were accepted directly: malformed usage can no
longer leak a reservation, and exact-token matching now retains common live
inflections. The billing recommendation was accepted only for definite 4xx
rejections; ambiguous connection/timeouts remain conservatively charged so the
hard cap cannot undercount possibly completed requests. The UI now calls the
counter an estimate. The complete 126-test/dependency/bytecode/diff gate passes
again.

Final tool-disabled Claude Opus 5 correction review passed on 2026-08-26 with
`No actionable findings.`

Required checks include:

- strict accepted, insufficient, and conflicting schemas;
- maximum three distinct tone/cue items total; confidence limited to low/medium/high;
- neutral, clearly positive, clearly negative, high-energy, and emotionally intense cases;
- possible humor, sarcasm, interest, discomfort, uncertainty, and disengagement;
- transcript-only operation;
- each modality configuration: transcript only, transcript+vocal, transcript+visual, all available modalities;
- conflicting language/vocal/visual evidence and correct abstention;
- visual disappearance while finalized transcription continues;
- missing/unreliable vocal evidence;
- overlapping speech and delayed finalized turns;
- production session wiring permits only explicit English (`en`); F04 adds no language detection and cannot reach retained benchmark-only Hebrew/Auto paths;
- no-face, no-audio, cloud-unavailable, authentication/refusal, and hard-budget states;
- first/timed/completed-turn triggering, coalescing, one-pending bound, duplicate suppression, stale-session rejection, and card display timing;
- manual Terra gating, reasoning choice, cost display, equivalent result, and immediate meaningful replacement;
- no analysis of user vocal/visual signals or user social cues;
- no raw-frame/audio persistence or egress;
- local F02/F03 continuity when interpretation is unavailable; and
- cost/token accounting from fixed fake usage.

## Real-model evaluation

Use 12 fixed English, project-owned scenarios. Define acceptable primary hypotheses/cues, unacceptable interpretations, and required abstentions before running models. Scenarios may cover more than one requirement, but together must include neutral, positive, negative, high-energy, low-energy, humor, sarcasm, interest, uncertainty, discomfort/withdrawal, conflicting modalities, modality-dependent recovery, and insufficient evidence.

Operational failures that do not require model judgment remain deterministic replay tests rather than paid variants.

### Staged comparison

Stage A runs four profiles—Luna `none`, Luna `low`, Terra `none`, Terra `low`—on transcript-only and all-modality snapshots: at most 96 calls.

Stage B runs the winning profile on transcript+vocal and transcript+visual: at most 24 additional calls. Reuse Stage A transcript/all results.

At the approved 10% input ceiling, one full comparison is approximately `$0.62`; one complete correction rerun brings the total to approximately `$1.25`. Stop before `$1.50`. Do not spend the remainder merely to fill the budget.

### Recorded metrics and gates

Record aggregate results only—no private conversation content:

- acceptable primary interpretation within top three on at least 80% of clear scenarios;
- correct abstention/conflict on at least 80% of uncertain/conflicting scenarios;
- at least 70% acceptable emitted items overall;
- at least 85% acceptable high-confidence items;
- 100% evidence references an available modality;
- zero true-emotion/true-intention claims;
- calibration by confidence bin, with fewer than five items reported as `insufficient sample` rather than calibrated;
- API latency p50/p95, eligible-turn-to-card latency, token usage, estimated cost, duplicates, stale results, and replacements per minute.

Latency/stability gates:

- cloud processing p95 at most six seconds;
- request-start to displayed-card p95 at most seven seconds;
- eligible finalized-turn to display p95 at most 20 seconds when cadence waiting applies;
- zero duplicate or stale replacements;
- 12-second minimum display honored except approved immediate states; and
- no more than four normal replacements per minute.

### Modality uplift

Adding vocal or visual evidence must recover at least two predesignated cases that transcript-only misses or appropriately abstains on. A confidence increase alone does not count. The added modality may introduce no unsupported high-confidence result and at most one additional unacceptable item across the set.

If Luna fails a non-negotiable schema/privacy/safety gate or the approved quality gates, do not choose Terra automatically. Present the results. Terra remains a user-triggered check unless the user separately approves a different live model and budget.

## Manual WhatsApp validation

After automated and real-model gates pass, run one consenting, scripted 5–10 minute English WhatsApp call with at least six eligible updates. No call recording or content retention.

The user verifies:

- the remote participant is the only cue subject;
- conversation-atmosphere hypotheses and remote cues are not widely incorrect;
- no materially wrong high-confidence item appears;
- no more than one materially wrong displayed cue appears overall;
- ambiguity produces an appropriate insufficient/conflicting result;
- vocal and visual observations align with the intended scripted changes;
- visual loss, unreliable vocal data, cloud unavailability, and budget stopping are truthful;
- transcription/local processing continue when cloud interpretation stops;
- cards do not flash or replace on duplicates; and
- manual Terra behavior and charged cost are understandable.

The user's explicit interpretation-quality approval is the final subjective gate. Automated privacy, schema, lifecycle, attribution, budget, and prohibited-claim failures cannot be waived as a subjective preference.

Recorded result: after the failed first attempt and the documented corrections,
the user reported that the live behavior was working really well. After approving
the final up-to-three-item display and retesting, the user explicitly answered
`passed` on 2026-08-26. Validation 3 passes.

WhatsApp is the only required F04 live application. Zoom and Google Meet inherit `WAIVED — not passed` and must not be relabelled as passed.

## Stop conditions

Stop implementation and revise this plan if:

- the English-only F03 revision is not reviewed and committed, its production boundary still accepts Hebrew/Auto, or the accepted model fails the existing F03 accuracy, latency, concurrency, resource, or teardown gates;
- simple local vocal features fail the modality-uplift gate and a new dependency/service is proposed;
- any design requires raw audio or video to leave the device;
- measured total input repeatedly exceeds 1,650 tokens and the bounded estimator cannot be tightened reliably;
- no Luna profile passes and an automatic Terra model is proposed;
- the requested Terra action would bypass the hard budget;
- interpretation blocks or stops healthy local capture/transcription;
- a new event bus/provider/plugin/settings framework appears necessary;
- evaluation would exceed `$1.50` without explicit approval; or
- F02/F03 privacy, lifecycle, attribution, source-priority, or waiver contracts regress.

## Review and completion gates

F04 is complete only when all of these are true:

1. Every implementation slice and automated replay passes.
2. Real-model comparison and metrics are recorded within budget.
3. The manual WhatsApp validation passes with explicit user approval.
4. Zoom and Meet remain labelled `WAIVED — not passed`.
5. A tool-disabled, read-only Claude Opus 5 review examines this plan, the F04 changes, direct F02/F03 integration surfaces, tests, results, privacy/lifecycle behavior, and known limitations.
6. Findings are accepted or rejected with reasons; accepted corrections are implemented.
7. The complete relevant suite, replay/evaluation gates, and necessary manual checks are rerun after corrections.
8. The corrected result receives another review; unresolved accepted findings keep F04 open.
9. The final reviewed result is committed and pushed to GitHub, and local `main`, `origin/main`, and GitHub are verified at the same commit.
10. Only then are the plan, permanent F04 Trello list, and roadmap card marked complete.

## Trello execution structure

The permanent list `F04 — Multimodal tone and cue interpretation` contains cards for:

1. approved planning and baseline;
2. OpenAI/model/cost research;
3. local vocal-feature spike;
4. interpretation contracts and deterministic coordinator;
5. remote vocal integration;
6. remote visual aggregation;
7. Luna structured integration and budgets;
8. stable card and manual Terra action;
9. automated replay validation;
10. fixed real-model comparison;
11. manual WhatsApp validation;
12. tool-disabled Claude Opus 5 review;
13. corrections, reruns, and correction review; and
14. final commit, push, pointer verification, and completion reconciliation.

Execution status is tracked above and on the permanent Trello cards. F04 is complete.

## Primary references checked 2026-08-25

- [OpenAI GPT-5.6 Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna)
- [OpenAI GPT-5.6 Terra](https://developers.openai.com/api/docs/models/gpt-5.6-terra)
- [OpenAI model comparison](https://developers.openai.com/api/docs/models/compare)
- [OpenAI Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs)
- [OpenAI Responses create reference](https://developers.openai.com/api/reference/cli/resources/responses/methods/create)
- [Official OpenAI Python SDK](https://github.com/openai/openai-python)
- [librosa project dependencies](https://github.com/librosa/librosa/blob/main/setup.cfg)
- [librosa pitch/F0 documentation](https://librosa.org/doc/latest/auto_tutorials/01-intro/03-f0.html)
- [openSMILE licence](https://github.com/audeering/opensmile/blob/master/LICENSE)
- [openSMILE Python documentation](https://audeering.github.io/opensmile-python/)
- [Parselmouth/Praat](https://github.com/YannickJadoul/Parselmouth)
- [PyWORLD](https://github.com/JeremyCCHsu/Python-Wrapper-for-World-Vocoder)

## Approval record

The user approved the completed grilling decisions on 2026-08-25, including English-only scope, the controlled tone/cue catalogue with a distinct high-energy tone, remote-only cue analysis, conversation-atmosphere hypotheses, 1,000 transcript tokens, 400 output tokens, timing/stability values, budgets, 12 real scenarios, manual WhatsApp judgment, memory deferral to F05, and per-request manual Terra `none`/`low` checks. After paid latency evidence, the user explicitly raised the cloud-processing p95 gate from five to six seconds on the same date.
