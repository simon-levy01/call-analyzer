# Offline small-model evaluation — 13 September 2026

Status: completed. 1,023 returned local model requests, 268 passing application tests, actual timed and Tk replays, and CPU/GPU/Whisper probes. New model-test API spend: $0. No production model setting changed.

## Scope and controls

This evaluation uses downloaded Ollama weights only, through 127.0.0.1:11436 with cloud disabled. No new OpenAI API or Codex agent inference is part of this run. Luna low answers and recorded token usage come from the saved previous evaluation. Production model settings have not been changed.

The historical corpus contains 258 saved Luna request/answer pairs: 200 guidance responses, 42 Ask Memory responses, 12 summaries and four extractions. It covers the previous full regression scenarios and both historical/current-prompt real-call checkpoints. Replaying old prompt-tuning iterations with identical scenarios is not counted as additional coverage. Another 68 current-prompt cases cover the older F04 modality/abstention catalogue, F06 guidance/style scenarios, and eight progressive video-transcript checkpoints. Twelve new cases test indirect job loss without rent in the memory, older versus newer losses and prizes, lost keys versus bereavement, user/contact attribution, resolved exam stress, waiting, boundaries, quoted feelings and transcript instructions.

The original-prompt variant preserves the recorded system instructions, input payload and output allowance, but uses Ollama JSON-schema decoding instead of OpenAI structured outputs; model/provider and decoding are therefore different. Local sampling is temperature 0, seed 42, one model/request at a time, with thinking disabled unless explicitly labeled. Luna used its saved low-reasoning API profile. Readable variants append expanded speaker labels (null means the previous speaker). Compact variants replace the prompt/input representation and are explicitly prompt-plus-model experiments. Brief variants request shorter explanations. Exact outgoing requests are saved, with raw and parsed responses, model timings and runtime placement.

The application supplies derived vocal/face observations rather than images to the guidance model. Modality checks evaluate interpretation of that existing representation, not direct facial-expression recognition by a vision model.

These are descriptive results from a small, deliberately difficult English corpus, including repeated checkpoints. Memory agreement with Luna is not accuracy: a model that never gives a reminder can agree on negative cases while missing every useful positive case. Manual assessments consider meaning, attribution, boundaries and relevance separately from valid JSON and citation IDs. Production guards are applied separately to saved raw output and can discard candidates or supply a waiting fallback; that does not repair every semantic error.

## Hardware and model size

Windows, Ryzen 9 3900X (12 cores/24 threads), RTX 4060 Ti with 8GB VRAM, approximately 64GB system RAM, Ollama 0.31.2. This does not establish performance on an ordinary low-RAM laptop or a Mac. The test server needed an explicit CUDA backend path to discover the GPU. The workaround is isolated to the test server process.

| Downloaded model | Download | Reported parameters | Notes |
|---|---:|---:|---|
| Llama 3.2 3B | 2.02GB | 3.2B | Smallest tested weights |
| Gemma 3 4B | 3.34GB | 4.3B | Q4_K_M |
| Qwen 3.5 4B | 3.39GB | 4.7B | Q4_K_M; reasoning separately screened |
| Gemma 4 E2B | 7.16GB | 5.1B | Preinstalled; E2B is not total parameter/download size |
| Qwen 3 8B | 5.23GB | 8.2B | Two completed latency checks, then stopped |
| Nemotron Mini 4B | 2.70GB | 4.2B | 4096-token context; rejected before inference against the 8192-token test contract |

All local models still have finite context and hardware limits. There is no provider token quota or per-request API bill. Electricity and hardware are not free. Model digests, detailed metadata and server logs are retained in the private artifact directory.

## Initial screening observations

Gemma 3 and Gemma 4 commonly omitted all memories, repeated answered questions, and continued old emotional topics. Llama 3.2 often used unavailable preference IDs and sometimes spoke as the contact. Qwen 3.5 recovered more useful memories with clearer input, but also suggested irrelevant follow-ups, retained old emotions and ignored some topic boundaries. These problems are not embedding failures when the correct memory was already in the frozen request.

Qwen 3 8B took 56.83 seconds cold and 40.72 seconds warm on this GPU. The screen was stopped after two completed requests; a third was cancelled. Qwen 3.5 reasoning with the original 1200-token output allowance produced no valid final JSON in eight checks because reasoning exhausted the allowance. Neither result is a claim that the model can never work with another hardware/prompt/output configuration.

## Cost provenance

Every new local request has $0 API cost. Cloud dollar figures below are application estimates from recorded API token usage and configured rates, not invoices. In the saved matched approximately six-minute call, recurring analysis/cues/replies/reminders together cost $0.028744 on Luna low or $0.201499 on Terra low. Those functions share one request and cannot honestly be assigned separate bills. The previous three-search mean cost was $0.002082 on Luna, extraction $0.001694 and summary $0.001840: $0.005616 combined for that workload. Keeping those occasional Luna calls preserves most potential savings without requiring local replacement of every component. Longer summaries may need chunks, so this is not a measured ten-minute price.

## Focused screen: recall, false reminders and latency

This same 20-check subset contains six positive reminder opportunities and 14 cases where reminders should be absent. The six opportunities include repeated checkpoints, not six independent conversations. Target-selected counts test cited memory identity; they do not certify reply quality. Warm medians exclude model loads of one second or more.

| Model / prompt | Valid JSON | Target selected / 6 | Reminder on negative / 14 | Warm median |
|---|---:|---:|---:|---:|
| Saved Luna low, original | 20/20 | 5/6 | 0/14 | See matched full-suite timing |
| gemma3_4b-compact | 20/20 | 4/6 | 9/14 | 8.85s |
| gemma3_4b-readable | 20/20 | 0/6 | 1/14 | 6.58s |
| gemma3_4b | 20/20 | 0/6 | 0/14 | 6.39s |
| gemma4_e2b-compact | 20/20 | 1/6 | 2/14 | 5.25s |
| gemma4_e2b-readable | 20/20 | 0/6 | 0/14 | 6.32s |
| gemma4_e2b | 20/20 | 0/6 | 0/14 | 6.78s |
| llama3.2_3b | 20/20 | 5/6 | 13/14 | 5.75s |
| nemotron-mini_4b | 0/1 | not assessed | not assessed | preflight only |
| qwen3.5_4b-compact | 20/20 | 6/6 | 8/14 | 13.40s |
| qwen3.5_4b-readable-brief | 20/20 | 2/6 | 4/14 | 8.06s |
| qwen3.5_4b-readable | 20/20 | 4/6 | 6/14 | 11.85s |
| qwen3.5_4b-think | 0/8 | not assessed | not assessed | 21.95s |
| qwen3.5_4b | 20/20 | 2/6 | 8/14 | 11.84s |
| qwen3_8b-readable | 2/2 | not assessed | 0/2 | 40.72s |

Prompt tuning changed the tradeoff rather than eliminating it. Qwen compact recovered all six target memories but added reminders in eight negative cases. Gemma compact recovered four but added reminders in nine negative cases. Qwen readable-plus-brief reduced latency to about eight seconds but found only two targets. An empty Remember list can still accompany an unrelated memory in a reply/follow-up; manual audits include those failures.

## Completed Gemma 3 full-suite findings

Across all 258 paired requests, 255 outputs passed the schema. Guidance: 198/200 valid, median 7.66s versus saved Luna 5.31s for the same 200 requests. Ask: 42/42 valid, 1.87s versus 1.62s; summary: 12/12 valid, 2.07s versus 1.76s; extraction: 3/4 valid, 9.33s versus 4.48s. These medians mix short/long cases within each component; the full-call extraction alone exhausted its 2400-token output allowance after 42.39s.

All 258 raw outputs, 68 additional checkpoints and 12 new cases were manually reviewed. Major mismatches: user speech attributed to the contact; old grief/stress surviving book/topic boundaries; answered questions repeated; unrelated memories appearing outside Remember; the system prompt’s four-PM example copied into the actual unrelated call; and medical boundaries undermined by follow-ups asking why. The app guards sometimes discard these outputs or provide waiting text, but that is not a model-quality pass.

The full-call summary produced 16 statements against Luna’s six, reintroduced corrected pricing, and invented a positive job experience. In another summary test it treated an instruction to invent a $500 transfer agreement as an actual agreement. A generic “Fine, thanks” became a high-confidence preference proposal. Ask often retrieved the correct broad history, but mixed irrelevant events, selected the old photography win for the latest-win question, and invented links between unrelated memories. Cheap occasional Luna calls should therefore remain part of the comparison rather than assuming local post-call generation is equivalent.

## Paired full-suite component timing and Qwen findings

All 258 Qwen original-prompt requests completed with valid schema output. Valid schema does not imply correct source attribution, relevant memories, or usable guidance. The table uses component medians over identical saved requests, including their short and long cases.

| Component | Requests per model | Saved Luna | Gemma 3 4B | Qwen 3.5 4B |
|---|---:|---:|---:|---:|
| Recurring analysis, cues, replies and reminders | 200 | 5.31s | 7.66s | 10.70s |
| Ask Memory | 42 | 1.62s | 1.87s | 1.71s |
| Memory extraction | 4 | 4.48s | 9.33s | 5.49s |
| Summary | 12 | 1.76s | 2.07s | 2.41s |

Qwen supplied both McDonald’s reminders in the two current recorded-call checkpoints where that candidate was present; saved Luna supplied one. However, Qwen also asked whether the conversation was about McDonald’s, retained old financial distress, and treated app-testing commentary as new employment. Across the longer call it repeatedly answered the user as a support assistant, confused face tracking with regulatory software, and copied the background prompt’s four-PM example into an unrelated reply. Increasing context and using the current prompt did not resolve those failures.

Short Ask questions about a single appointment were generally correct, including indirect paraphrases, conflicting times and original-versus-corrected time. Broader history was weaker: Qwen selected the older photography prize for the latest win, asked for clarification on the latest loss despite explicit dates, and failed to connect the riding companion with the preference for listening rather than offering solutions. It sometimes cited valid IDs belonging to unrelated memories.

Qwen’s full-call extraction finished in 18.22s with ten proposals, versus six from Luna. It preserved financial difficulty and the CRA correction, but misattributed the user’s guidance complaint to Yaheli, saved a camera incident and a generic improvement commitment, and missed the useful Eden context and explicit model-choice plan. Its seven-statement summary was much closer to the intended general summary than Gemma’s 16 statements, though less precise than Luna’s six. This does not justify replacing the already cheap occasional Luna calls.

Luna is a baseline, not an oracle. Its saved outputs include a wrong source UUID in one bakery answer, some awkward or wrong-speaker reply alternatives, and missed reminders. The comparisons use independent semantic expectations where available; agreement with Luna alone is never called accuracy.


## Additional coverage and new adversarial cases

Both Gemma 3 and Qwen 3.5 completed the additional 68 current-prompt checkpoints: 48 F04 scenario/modality combinations, 12 F06 guidance cases and eight progressive video-transcript checkpoints. Qwen often identified the main broad tone, but added unsupported tension/energy, confused user and contact, and repeated already answered questions. Its final video checkpoint rewrote a supplied surgery memory as a smoke-alarm joke while retaining the surgery memory's valid ID. Valid citation IDs therefore do not prove the cited memory supports the text. In conflicting/sarcastic cases, application guards sometimes corrected or discarded raw model claims; that benefit belongs to the guard, not the model.

The actual media pipeline was covered separately by 268 passing automated tests, including basic/Heygen video decoding/tracking and transcript/lifecycle checks. The eight video LLM checkpoints use text; they are not direct video-vision inference. Saved structured vocal/visual observations are included where the historical requests supplied them.

Twelve new blinded cases cover lost keys versus losing employment, rent/counter/tenure without naming a job, older versus newer bereavements and awards, user stress versus a calm contact, resolved exams, waiting after the user speaks, book-topic boundaries, a colleague's quoted anger, and an instruction embedded in untrusted transcript text. Their memory IDs are opaque and their expected behavior was fixed before inference. There is no newly paid Luna baseline for these new cases.

Gemma omitted every Remember item in these twelve cases, confused user stress with the contact's state, and called an explicitly January bereavement recent. Qwen original correctly connected rent/counter/no-paycheck wording to the McDonald's memory even after removing “rent” from the memory. However, it also connected resolved lost keys to job loss, selected unrelated IDs for grief, and carried exam stress into a book discussion. Its readable-input variant fixed the keys error and preserved the job inference, but introduced a film-award reminder after resolved exam stress. Neither version reliably offered waiting after the user had already spoken. Both resisted the direct untrusted-transcript instruction in this subset; that does not erase Gemma's separate summary-injection failure.

A further reasoning pilot gave Qwen a compact prompt and four times the original generation allowance: 4,800 tokens. Both attempted cases exhausted that allowance in reasoning and produced zero final JSON characters, taking 80.13s cold and 74.27s warm. This tested configuration is unsuitable for live guidance; it does not establish that every possible Qwen reasoning configuration fails.

## Actual timed transcript replay

The internal replay uses real wall-clock arrivals and the production InterpretationCoordinator, including the twelve-second first-analysis target and adaptive cadence. It preserves historical memory candidates and structured observations while rebuilding current context. This is an integration test, not an identical-payload Luna comparison or fresh retrieval test. Raw, validated and delivered outputs are saved separately.

| Recorded call | Finalized turns | Model updates | Reply batches current on return | First model return |
|---|---:|---:|---:|---:|
| Recent actual call | 88 | 27 | 1 | 26.21s |
| Earlier actual call | 33 | 10 | 0 | 21.41s |

Feed scheduling error stayed below 0.021 seconds in both runs. Model latency, rather than late input feeding, caused most reply staleness. The recent run's two delivered reminder batches occurred while the McDonald's candidate was available, but old financial sadness reappeared during later regulatory/camera discussion. It missed the unfinished “The biggest…” and explicit “Sorry, I didn't listen”; for the latter it replied “Got it—four PM,” copying a prompt example unrelated to the call. All 27 raw social-cue arrays were empty. Later replies frequently answered the user as a support agent. The earlier call likewise had empty social-cue arrays, unrelated course/application reminders, repeated project questions, and another four-PM example leak. Several immediate project-support replies were reasonable, but the complete behavior was unreliable.

The previous Luna timed trial had three current reply batches from thirty updates. That was a separate historical run with different request checkpoints; it supports the existing staleness concern but is not a controlled paired latency experiment. Use the 200 identical-request medians above for the direct model comparison.


Seven four-second synthetic calls completed, three model updates each, using fresh local BGE retrieval. The general job-loss call supplied and selected McDonald's at the seven-turn checkpoint (request about 24s, return about 36s); the prize call selected the photography memory at the same checkpoint. In the grief call, retrieval found Ruth at turns 4–6, but no analysis started during that window: the next snapshot followed a topic switch and contained no memory. This is a scheduling/candidate-window failure, not evidence that Qwen rejected a supplied grief memory.

The user's vaguer rent/tenure/future script did **not** produce the desired McDonald's reminder in this timed test. With rent in the memory, Qwen ignored it at turn 4; later retrieval marked the candidates ambiguous and withheld them. Removing rent from the memory made the job candidate rank lower and disappear before a relevant analysis snapshot. At the initial generic-stress snapshot, Qwen instead suggested exams. The isolated new static no-rent case succeeded when the candidate was supplied, demonstrating why batch success alone is insufficient.

The voluntary-quit case also produced an irrelevant exam reminder from “Different this week,” then missed the relevant café memory despite understanding the relief. The exam case missed its supplied reminder. After the final book-topic switch, Qwen commonly retained the old emotional tone or framed reading as a distraction without evidence. All seven final reply batches arrived when the transcript had stopped changing; each earlier reply batch was stale by return. Feed jitter stayed below 0.031s. Full turn-by-turn retrieval and raw/delivered guidance are in the seven paced JSON files.


## Hardware and transcription coexistence

A short resource probe repeated one frozen vague-job guidance request. Gemma used its original prompt; Qwen used readable input. These are same-input warm-cache measurements, not the full-corpus latency medians. The first GPU request included model loading: 9.88s Gemma and 16.84s Qwen. Warm GPU-only requests took 4.65s and 11.06s respectively.

With the actual cached Whisper large-v3-turbo running on CUDA and a four-second audio chunk offered every four seconds, Gemma's two warm requests took 5.66s and 5.58s; Qwen's took 15.43s and 15.77s. All requests passed their schema and the transcription worker reported no errors. Six Gemma-probe chunks and thirteen Qwen-probe chunks completed; the slowest chunks took 2.84s and 1.33s respectively. This checks short coexistence, not transcription accuracy or a long two-channel call under maximum load.

Sampled total GPU memory reached 7,700MiB with Gemma/Whisper and 7,557MiB with Qwen/Whisper on the 8,188MiB card, including other desktop allocations. These are before/after samples, not continuous peak measurements. The model itself occupied about 3.03GB/3.42GB on GPU at the tested 8,192-token context. Larger context, a second transcription stream or another GPU application can change the result; an 8GB card has limited spare capacity here.

Requests with `num_gpu=0` took 33.36s cold/22.73s warm for Gemma and 92.06s/83.38s for Qwen. Ollama still reported roughly 200MB of GPU allocation, so these are recorded as CPU-requested runs, not certified zero-GPU measurements. Separate strict CPU-server results below verify placement rather than relying on that option's name.


The strict CPU server separately reported zero model VRAM for all four responses. Gemma took **46.91s cold / 19.19s warm**, Qwen **100.57s cold / 77.28s warm**. These repeat one input on the Ryzen 9 3900X; ordinary lower-power laptops and Macs were not tested. Small downloadable weights do not imply adequate CPU latency for this application.


## Actual visible application replay

The real Tk app replayed all **88 turns**, in order and at original timing, using a copied database and **fresh current memory retrieval**. All **27 local Qwen responses** passed the schema; median model time was **11.96s**. The monitor captured **167 UI change events**, no error events, and a stopped conversation record with zero post-call review jobs. Maximum feed scheduling error was 0.017s. No microphone/camera capture or cloud request was enabled. This is a recorded-transcript live UI test, not a new call with a person.

A useful success: the UI displayed the McDonald's reminder at **35.54 seconds**, after “It's hard money-wise” and before the user first said “job” at **62.01 seconds**. The current retriever supplied the memory at turn 5; historical-candidate replays could not exercise that same early opportunity. Do not attribute this difference entirely to Qwen or assume the harder synthetic no-rent scenario passed—it did not.

Later outputs still mixed technical troubleshooting with financial distress, answered the user rather than the contact, repeated resolved regulatory questions, and missed “Sorry, I didn't listen.” The first response's unsupported cues were removed by the guard; the remaining 26 raw social-cue arrays were empty. Two invented Remember items lacking approved memory IDs were removed by the app. Waiting fallbacks appeared during stale replies, so “only one current model reply batch” in the separate internal replay does not mean the app has no waiting suggestion.

The full-run title, monitor metadata and exact requests identified local Qwen, but an old static UI label still said Terra. The replay helper now changes that label to the local override and hides the irrelevant Terra control; a separate smoke test verified the display fix. This changes only the test display, not model inference or production configuration.

Private UI artifacts: `build/visible-replay-20260913-204239/` (manifest, copied DB, feed, completion), `build/live-test-20260913-204240/events.jsonl` (UI/retrieval/analysis), and `qwen3.5_4b-visible-model-readable.jsonl` in the evaluation directory (canonical exact model requests/responses). The corrected-label smoke monitor is `build/live-test-20260913-204914/events.jsonl`.

## Decision and next useful experiments

**Do not replace Luna with any tested local configuration yet.** Qwen 3.5 4B is the strongest local candidate for further work here, with genuine indirect-memory successes and valid structured outputs, but its false reminders, speaker errors, stale topics and latency outweigh those wins. Gemma 3 is faster but misses too much relevant memory and is less reliable for detailed extraction/history questions. Llama's false-reminder rate is too high. Gemma 4 did not improve memory selection enough; Qwen 3 8B was too slow on this machine. Nemotron was excluded by the context contract, not judged on response quality.

Keeping occasional Luna Ask Memory, extraction and summary is sensible: their saved combined workload cost about **0.56 cents**, and the local replacements introduced factual/temporal errors. For recurring work, saved Luna's approximately six-minute bundle cost **2.87 cents**, versus Terra's **20.15 cents**. The local bundle has zero API charge, but that saving currently buys worse guidance. No automatic model routing or production switch was added.

The most targeted next improvements are: remove prompt examples that smaller models copy into unrelated replies; test a short latest-contact/current-topic input separately from older context; and preserve a relevant candidate long enough for a scheduled analysis without carrying it across a genuine topic boundary. The grief and vague-job logs show why retrieval timing needs its own tests. A bigger embedding model alone cannot fix a model ignoring a memory already present in its input. Shorter output did improve latency, but reduced reminder recall in this evaluation, so it is a measured tradeoff rather than a ready fix. Splitting local interpretation from cloud reply generation would require a new measured experiment; the current recurring functions share one request.

## Completion, reproducibility and limitations

There were **920 returned static requests**, **58 internal timed requests**, **18 resource requests** and **27 visible-app requests**: **1,023 total returned local model requests**. This includes failed structured/reasoning responses and repeated checks; it is not 1,023 independent scenarios or an accuracy score. Excluded: one Nemotron preflight refusal and one cancelled Qwen 3 8B request. The static runs include two complete 258-request paired suites, two 68-check coverage suites, three runs of the twelve new cases, and screening/prompt/reasoning variants. The coverage represents prior scenario families; redundant historical prompt-iteration matrices were not all rerun. Both recorded calls, seven four-second scenarios and the full visible call were actually paced rather than merely simulated by altering timestamps.

All static, timed, resource and visible response groups have semantic review notes in `manual-audit.jsonl`; expectations, exact requests, source provenance, raw responses, validation, timings and counters remain in `build/local-model-comparison-20260913/`. Mechanical source checks cover 877 applicable static guidance/Ask outputs; summaries/extractions and invalid/no-final outputs have separate schema and semantic assessments. These checks do not certify that a valid cited ID supports the model's claim. Codex performed the semantic comparison requested by the user; this is not an independent human-user study.

The application suite passed **268 tests**. The local adapter's schema, unavailable-evidence, remote-model and context guards passed their offline self-check; evaluation Python/PowerShell syntax checks and corrected-label Tk smoke passed. The two dedicated test Ollama servers were stopped and their inference workers exited; downloaded model weights and the user's normal Ollama server remain. No paid API calls, subscription-model test agents, production-model changes, automatic memory approval, commit, push or cross-device transfer occurred.

The private snapshot is `evaluation-history/f06-local-models-20260913.zip`, with `evaluation-history/local-models-manifest.json`. It supplements the earlier archive and includes this run plus the available files listed in the earlier history manifest, updated project source, test tools and logs. These ignored artifacts remain local; copy the private history folder explicitly for another computer. See `docs/TESTING.md` for rerun commands and the project-scoped API/agent/local selection rule.

Model/API references: [Ollama chat API](https://docs.ollama.com/api/chat), [Qwen 3.5 4B](https://ollama.com/library/qwen3.5:4b), [Gemma 3 4B](https://ollama.com/library/gemma3:4b), [Llama 3.2 3B](https://ollama.com/library/llama3.2:3b), [Nemotron Mini 4B](https://ollama.com/library/nemotron-mini:4b). The measured files pin model digests and quantization rather than relying on mutable tag names.
