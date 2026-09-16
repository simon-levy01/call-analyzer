# September 15 long-call diagnosis

Status: development corrections implemented; offline checks passed. No new paid API inference, no production memory edits, no release/Claude-review clearance or F07 completion claim.

Later follow-up: [two-call real API comparison](TWO-CALL-API-COMPARISON-20260915.md) supplies fresh post-correction results under a new explicit $0.40 authorization. The no-paid-inference statement above describes this original diagnosis phase, not the later comparison. Semantic failures remain; review/live gates are unchanged.

## Evidence and method

The explicitly logged call contained 150 attributed transcript turns, 47 live guidance requests and one summary request. Memory extraction was separately recorded in the local database, but its raw request/response was **not** captured by the old logger. The app's source and original logs were preserved before editing.

Private evidence: `build/call-diagnosis-20260915/`. It contains the original log, call-time and pre-edit source snapshots, exact frozen requests, saved Luna responses, isolated Sol responses, root diagnostic responses, read-only record-scoped memory results, input/output hashes, and offline replay/test results. Do not publish this folder: it contains real conversation data. No video/audio was retained, so this cannot verify what was actually said or replay perception from original media.

Six fresh `gpt-5.6-sol`, `high`, no-history-fork agents answered five selected live requests (05, 06, 24, 31, 41) and the whole-call summary (47). Each saw only one frozen request's instructions/input/schema, not Luna's output, later turns or expected answers. The agent thread limit prevented additional isolated trials; agents were not reused. Five corresponding root outputs plus one reconstructed memory-extraction output were also saved. Root diagnostics were **not blinded**: this session knew the symptoms, other outputs and later transcript. Its backend model/effort were not independently reported by tools.

All 12 saved comparison outputs pass Pydantic schema and supplied-source-ID checks. This does not establish semantic truth, provider strict decoding, API latency, cost, or parity. Agent token limits were targets, not enforced API limits. No randomized benchmark or human emotion labels exist for this call. No Sol extraction, fresh amended-prompt inference or facial ablation was completed.

## Confirmed failures

| Finding | Recorded evidence | Correction |
|---|---|---|
| Reply starvation | New finalized speech arrived during 45/47 requests. Median recorded Luna response time was 7.91 s; maximum 14.03 s. Only one coordinator result and one rendered guidance event contained replies. Worker and UI both discarded ideas whenever context advanced; user speech also cleared visible cards. | Treat guidance as optional **recent-context ideas**, not a guaranteed turn-perfect script. Retain briefly, label accordingly, remove exact already-spoken suggestions, invalidate explicit topic/correction/refusal boundaries, and expire 24 s from source snapshot creation, including inference delay. |
| Waiting overrepresented | 26/47 requests ended with user speech. A heuristic review found 16/47 raw answers contained only waiting/listening/continuation actions. Empty displays independently presented waiting instructions during 4,972/4,990 status samples. These are polling samples, not independent judgments. | Remove the blanket user-last waiting preference, align required latest-turn citations, explicitly distinguish whose sentence is unfinished, permit empty outputs, and stop converting empty/filtered results into waiting advice. |
| Facial evidence removed by budget | Numeric facial buckets existed in every live snapshot, but only the first 12 requests retained any. The old limiter exhausted all visual rows before trimming vocal history. | Preserve a small recent sample from both sensors before eliminating an entire modality, within the unchanged 4,500 estimated-input-token ceiling and intact transcript allowance. |
| Visual overinterpretation | Only request 05 cited visual evidence in raw Luna output. Both Luna and Sol read an implausible transcribed fragment as a greeting and used movement to support warmth. Later user speech explicitly described a transcription error; that later correction was unavailable to either frozen request. | Clarify that movement variability is not smile intensity, gaze or interest. Ask the model to treat context-inconsistent fragments cautiously. These are prompt corrections, not validated recognition improvements. |
| Speaker/context mistakes | Luna gave contact-facing continuation replies while the user's sentence was unfinished. Sol handled that case better, but inferred current withdrawal from a refusal to interact with a third party and returned an unsupported user commitment in another case. | Tighten speaker perspective and distinguish third-party disputes from withdrawal from the present conversation; retain commitment/evidence filters. |

The guidance lifecycle change is intentional, not merely cosmetic. New utterances can make an earlier idea semantically obsolete even within 24 seconds; lightweight local rules cannot detect every answered question, contradiction or implicit topic change. The UI therefore says to use recent-context ideas only if still relevant. Generation/contact/revision checks, dismissal, bounded display and explicit resets remain. Human live testing must assess usefulness versus stale ideas; do not call this fully solved based on offline replay.

## What the model comparisons showed

- **Ambiguous acknowledgment (06):** Sol supplied a useful clarification alongside waiting; Luna only waited. Root supplied a clarification without asserting a negative emotion. Sol's high confidence about the referent of a brief answer was not established ground truth.
- **Apparent greeting/transcription artifact (05):** the stronger model did not rescue bad input; it also invented a confident social reading. Root abstained, but was unblinded and had seen later correction evidence, so that is not proof of runtime superiority.
- **Possible banter (24):** Sol offered a more contextual response than Luna's acknowledgment/waiting. Root kept literal-versus-joking uncertainty. No retained audio can settle intent; do not memorize the apparent activity as an established habit.
- **Third-party conflict (31):** Sol's output was not uniformly better: it mixed the third-party boundary with present-conversation withdrawal and invented a user promise. The existing local personal-commitment filter remains necessary.
- **Unfinished user sentence (41):** Sol kept speaker ownership straight where Luna did not. Neither answer proves a useful ready-to-say completion could safely be invented.
- **Summary (47):** Sol better retained substantive advice and omitted an ambiguous stopping remark. Root also omitted that ambiguity and compressed technical details. Stylistic and factual judgments remain a diagnostic review, not a scored blind competition.

## Memory and summary findings

During the call there was one approved older memory in the contact's corpus; retrieval supplied **none** of it to the 47 requests. That fact was unrelated to the current topics. This is not evidence that retrieval failed, nor a test of live recall of a relevant event. Keep the existing synthetic retrieval/Ask Memory evaluations; a new cross-call test with relevant approved facts is still needed.

The database contained seven extraction proposals. Problems included an already-completed action typed as a future commitment, a temporary third-party dispute typed as a standing relationship preference, routine greeting acceptance promoted to memory, inline source annotations wasting content space, and a contextual claim stronger than the wording established. Root's reconstructed extraction preserved useful shared-project feedback and substantive advice while avoiding those categories. Original extraction input equality is not claimed; no isolated Sol extraction ran. Existing approved memories were **not** altered or deleted.

Future extraction instructions now address these categories and keep citations in their dedicated field. Summary instructions caution against literalizing banter, guessing the object of “stop this,” and treating speaker claims as independent verification. Opt-in logging now routes extraction through the same request/response recorder, closing the evidence gap for future explicitly logged calls. No automatic logging was enabled.

## Verification and remaining gates

- Original offline replay reproduced total visual loss in 35/47 frozen snapshots before the limiter fix.
- Changed-code replay retains visual rows in 47/47 and respects the original transcript and 4,500-token ceiling (maximum observed estimate 4,498). A retained row is not necessarily usable facial evidence; missing/unreliable rows must still abstain.
- Replaying the **old** Luna answers through corrected filtering and historical-time reconciliation leaves some reply candidates in 42/47 cases. This is not a new model answer, useful-reply score, or full after-change GUI playback. Some retained answers still say to wait.
- Maintained offline suite: **294 passed**, including synthetic sensor-budget, source-age expiry, contextual retention/reset, repetition, empty-result, opt-in memory logging, existing Tk, privacy, storage, retrieval and lifecycle checks. The frozen-call replays are private supplements, not prerequisites for the public tests.
- Python compilation and `git diff --check` pass. No new dependency or raised request budget.

Next gates: independent Claude review of this change; explicit live/manual validation of contextual guidance and faces; later user-authorized Luna API acceptance if desired. Prompt-only improvements have **not** been demonstrated on new Luna outputs. Do not rerun paid inference on an old budget or mark F07 complete. Keep unrelated existing worktree changes intact; no automatic commit/push of this unreviewed checkpoint.
