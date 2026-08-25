# F03 — Two-sided audio and transcription

**Status:** Complete and manually accepted for English; the post-completion local large-v3-turbo revision passes automated regression/replay gates and the user-approved real-call check; its corrected final Claude rerun was unavailable because the Claude account hit its session limit, and the user explicitly accepted commit/push without waiting for that rerun; Hebrew/Auto remain unsupported and Zoom/Meet remain waived as not passed
**Prepared:** 2026-08-19
**Roadmap outcome:** Capture microphone and call playback as separate sources and produce ordered, speaker-attributed `ConversationTurn` objects.
**Planning result:** The decisions in [Approval record](#approval-record) are approved. No implementation code was written during this planning task.

## Post-completion language outcome — 2026-08-25

English is the only supported transcription language. A local comparison used 50
human-recorded Hebrew FLEURS utterances (8 minutes 11 seconds) with identical decoding
settings and the five-second target. The best tested free local candidate,
`ivrit-ai/whisper-large-v3-ct2`, produced **22.2% word error**. Its turbo variant
produced 22.8%; the other tested free models ranged from 30.3% to 128.8%. The current
general large-v3-turbo model produced 34.4%. This is not sufficiently accurate for
project text, even when latency passes.

Hebrew and automatic English/Hebrew selection are therefore unsupported and excluded
from the application for now. The English large-v3-turbo path remains local and free;
its real-recording comparison produced approximately 3.8–5.1% word error. The benchmark
fixture remains for small regression checks. The 50-clip FLEURS matrix was a separate
external-corpus evaluation with an ad hoc local runner; the committed profile harness
does not reproduce that matrix and compares each linked application's model plus decoding
settings rather than model weights alone. Earlier clean synthetic Hebrew and Auto results
below are preserved as historical evidence and do not establish current language support.

| Free local candidate | Hebrew WER | Worst clip delay |
|---|---:|---:|
| `ivrit-ai/whisper-large-v3-ct2` | **22.2%** | 3.43 s |
| `ivrit-ai/whisper-large-v3-turbo-ct2` | 22.8% | 0.83 s |
| `ivrit-ai/faster-whisper-v2-d4` | 30.3% | 11.65 s |
| General Whisper large-v3 | 32.0% | 2.93 s |
| General/current large-v3-turbo, fair settings | 34.4% | 1.06 s |
| Original project small | 53.7% | 1.65 s |
| Stage Whisper base | 71.8% | 1.59 s |
| Faster-Whisper-Transcriber distil, unsupported Hebrew diagnostic | 128.8% | 2.94 s |

The first post-completion Claude Opus 5 review returned `NOT PASS`. Corrections pin the
production model revision, derive and verify its exact cache path, make benchmark failures
ineligible for accuracy ranking and return a failing process status, validate degraded-WAV
inputs, document the external FLEURS method honestly, and align the five-second code/plan
maximum. After correction, 83 tests and `pip check` pass; offline replay has zero network
attempts/audio artifacts and 0.828-second maximum inference. A fresh 60.2-second combined
F02/F03 run passes with 1.409-second single-source p95, 2.686/2.724-second overlap
p95/maximum, queue peak/final 1/0, zero saturation, 24.90 F02 signals/second, and 0/0
workers/results. A fresh Claude pass and manual English WhatsApp call remain required.

The second corrected-diff Claude Opus 5 review also returned `NOT PASS`. Its blocking
findings are corrected: partial benchmark failures cannot duplicate cases; local-cache
profiles must match the pinned production model/revision/compute type; complete wrong-
revision and legacy-small cache snapshots are negative-tested; and README makes production
model provisioning an explicit prerequisite. The focused audio/benchmark suite passes
49/49 after these corrections. A third exact verdict is required before the manual call.

The third Claude review returned `NOT PASS` on benchmark/cache boundaries. Corrections
require every CTranslate2 runtime file including `vocabulary.json`, make built-in profile
comparison English-only by default, exclude profiles that do not support the selected
language, preserve aggregate WER precision, and raise local-profile programming errors
instead of turning them into measurements. Tests now cover wrong/legacy/incomplete caches,
profile-label mismatch, actual audio degradation, and fixture language filtering. A fresh
exact verdict remains required before the manual call.

The fourth Claude review returned `NOT PASS` with three remaining blockers. Corrections
make cache readiness match faster-whisper's required core plus either tokenizer or
`vocabulary.*`, fail before execution when language filtering leaves zero compatible
profiles, and share one production decoding-options constant between live inference and
the current benchmark profile. The corrected focused/full suites pass 53/53 and 87/87;
the real current English fixture profile passes at 0% WER in 0.80 seconds. A fresh exact
verdict remains required before the manual call.

The fifth Claude review returned `NOT PASS` on three final data-integrity boundaries.
Corrections require the pinned snapshot's local `tokenizer.json`, aggregate exact integer
edit/word counts with a successful unequal-length multi-case test, accept Windows UTF-8
BOM reference files, and pin deterministic temperature for every comparison profile.
The post-correction offline replay measures maximum RTF 0.065, satisfying the 0.60 gate.
A fresh exact verdict remains required before the manual call.

The sixth Claude review returned `NOT PASS` because the first shared-options edit had
not reached the live worker and the external Hebrew runner was not reproducible. Every
live/replay production call now consumes `TRANSCRIBE_OPTIONS`, with a direct live-worker
kwargs test. The committed benchmark now accepts a validated external-corpus manifest and
includes the pinned ivrit.ai, general large-v3, current, original small, and Stage base
fair-settings profiles used by the matrix. Focused/full suites pass 57/57 and 91/91;
offline replay passes at maximum RTF 0.066 with zero network attempts/audio artifacts.
A fresh exact verdict remains required before the manual call.

The seventh Claude review returned `NOT PASS` and contradicted the fifth review about
vocabulary readiness. Inspection of the installed faster-whisper loader resolves the
question: its pinned snapshot download allow-list contains config, model, preprocessor,
tokenizer, and `vocabulary.*`; the exact pinned production snapshot contains the five
named files now required by `PINNED_MODEL_FILES`. This exact-revision contract supersedes
the earlier cache-rule iterations. Empty benchmark case lists are also rejected instead
of producing 0% WER. A fresh exact verdict remains required before the manual call.

The eighth Claude review returned `NOT PASS` on the final installer/cache contract. The
installer now verifies that the exact pinned snapshot is complete after download and
reports its missing runtime files. Tests reuse `PINNED_MODEL_FILES` as the single file-set
contract and prove both incomplete-install rejection and successful installer readiness.
A fresh exact verdict remains required before the manual call.

The ninth Claude review returned `NOT PASS` on benchmark evidence labeling and weak
boundary checks. Reports now identify built-in, single-media, or manifest provenance and
only name a winner when multiple profiles finish. The noScribe proxy reuses the pinned
model identifier, the English-only selector and start mapping share the audio contract,
the provisioned snapshot is checked on machines where it exists, and invalid manifest/CLI
inputs are regression-tested. Focused/full suites pass 70/70 and 104/104; offline replay
passes at maximum RTF 0.065 and 0.708-second maximum inference. A fresh exact verdict
remains required before the manual call.

The corrected Claude-only rerun was attempted with both Opus and Sonnet, but the account-
wide session limit prevented either model from receiving the diff. The user then tested a
real English call, reported that it had a couple of errors but was very good, and explicitly
approved the result. No call content, transcript, contact name, recording, screenshot, or
window title was retained. This approval waives only the unavailable corrected rerun for
this post-completion model revision; the ninth review's findings were corrected and the
104-test/replay gates above remain the automated evidence for commit/push.

## Goal and user-visible result

The user selects the existing call window, a microphone, and one playback device, then starts an English transcription session. The existing F02 visual loop continues while F03:

1. captures the microphone as `user`;
2. captures the explicitly selected WASAPI playback endpoint with PyAudioWPatch as `selected_contact`, with a visible warning that every sound routed to that endpoint is in scope;
3. transcribes both sources locally;
4. presents only finalized, chronologically ordered `ConversationTurn` objects; and
5. keeps a healthy audio/transcription session running if visual capture is lost mid-call, without silently selecting another video window; and
6. stops cleanly without saving raw call audio.

The visible controls remain deliberately small: microphone selector, playback-device selector and endpoint-scope warning, an English-only language selector, Start/Stop, per-source listening state, and a plain chronological transcript. When no selected-face thumbnail is available, its empty area collapses so the existing transcript and live audio state remain visible. A clean Stop keeps the two explicit choices in the same live enumeration context for the next Start. Refresh, device change/fault, or an in-process enumeration rebuild clears them and requires explicit reselection. An app restart never restores prior records/indices; its fresh initial enumeration may suggest that context's current Windows defaults. F03 adds no transcript editor, memory controls, social interpretation, reply suggestions, summaries, or polished UI.

## Verified starting facts

### Repository and F01/F02 health

- The repository was clean on `main` before this plan was created.
- Local `main`, `origin/main`, and GitHub `main` all resolved to `7035090ad1eac546850ed4c85e31518ba8bcfb78` after `git fetch origin main --prune`; ahead/behind was `0/0`.
- The latest commit is `7035090 feat: complete F02 video capture and facial signals`.
- `.venv` uses Python 3.12.10 and `pip check` reported no broken requirements.
- `pytest` passed: **32 passed in 2.52 seconds**.
- `python -m conversation_copilot --check` passed with 500 conversation turns and two speakers.
- `python -m conversation_copilot --check-video` passed with six selected-face signals, 478 landmarks, 52 blendshapes, and explicit face-loss behavior.
- `python -m conversation_copilot --check-video-capture` passed; the last processed callback was 114, an invalid callback at 115 did not replace it, both dimensions were exercised, target-close latency was 98 ms, and workers/retained frames ended at 0/0.
- F02 already keeps only the latest video frame, processes it off the Tk main thread, and returns bounded result state. F03 must coexist with that design; it must not introduce an event bus or replace the F02 capture loop.
- `ConversationTurn` already exists in `conversation_copilot.models` with `speaker_name`, `speaker_role`, `source`, `content`, `timestamp`, `display_order`, and `is_media`. Existing roles are exactly `user`, `selected_contact`, and `unclear`; no second transcript model is needed.
- The two existing ADRs remain applicable: Windows selected-window video capture is video-first, and transcripts/memory are local by default. F03 does not change either decision.

### Trello state

- The complete board was read, including all 30 cards present before F03 planning.
- The roadmap card **F02 — WhatsApp/Zoom window capture and facial signals** is complete.
- All 13 cards in the permanent F02 list are complete, including planning, implementation, validation, Claude review, and corrections.
- The roadmap F03 card exists and remains incomplete.
- A permanent list named **F03 — Two-sided audio and transcription** was created for this plan. Its work cards remain open until their own evidence is complete.

### Development machine and audio endpoints

- Windows 11 Pro 10.0.26200, AMD Ryzen 9 3900X (12 physical/24 logical cores), and 31.9 GiB RAM.
- NVIDIA GeForce RTX 4060 Ti with 8 GiB VRAM, driver 610.88, and compute capability 8.9.
- The machine has no system-wide CUDA toolkit. After the approved CPU-gate failure, the project installed pinned Windows CUDA 12 cuBLAS and cuDNN 9 wheels inside `.venv`; CTranslate2 GPU speech inference now passes without a system-wide toolkit installation.
- Working microphone endpoints include **Microphone (USB Audio Device)** and **Microphone (High Definition Audio Device)**.
- Working render endpoints reported by WASAPI include **Digital Audio (S/PDIF)**, **Speakers (USB Audio Device)**, **G27FC**, and **Big Speakers (High Definition Audio Device)**. The current WASAPI defaults are the USB microphone and Big Speakers.
- The installed `sounddevice` 0.5.6 can enumerate the endpoints but does not expose WASAPI loopback inputs. It is environment-only and is not a declared project dependency.
- FFmpeg 8.0 is installed, but its DirectShow input list exposes the microphones and no playback-loopback device.
- No Whisper model was cached before the planning spike. The approved `small` model is now provisioned under the application model cache for offline runtime. The machine had approximately 937 GiB free disk space at planning time.

### Local transcription planning spike

This was the initial disposable machine check using Windows SAPI-generated English speech, not live-call audio and not a repository change. It is preserved as historical pre-Gate-B evidence:

- `faster-whisper` 1.2.1, `small`, CPU `int8`, 12 threads.
- A 35.853-second synthetic file transcribed in 6.304 seconds: real-time factor **0.176**. It made one numeric-token error (`42` became `4.2` on one repetition), so this is a speed sanity check, not an accuracy pass.
- Ten transcriptions of a 3.554-second synthetic utterance had a **1.948-second median**, **2.108-second p95/max**, and maximum real-time factor **0.593** after a 1.898-second cached model load.
- The synthetic output otherwise matched the spoken sentence, but clean TTS cannot substitute for the required English/Hebrew fixture and live-call gates below.
- The CPU result is promising enough to test before installing a GPU runtime. It is not permission to skip the full two-source/F02 concurrency spike.

## Boundaries and explicit non-goals

F03 produces attributed transcript turns only.

- No emotion or tone analysis.
- No facial/audio fusion, social cues, interpretation, coaching, or reply suggestions.
- No contact memory, transcript approval workflow, summaries, or retrieval.
- No raw-audio recording, export, debug dump, test evidence, or Trello attachment.
- No live-call transcript or call content in Git, logs, screenshots, Trello, or review prompts.
- No OpenAI call unless local transcription fails the approved gate and the user separately approves audio egress and the revised implementation choice.
- No generic capture plugin, provider interface, provider factory, repository layer, event bus, or speculative abstraction.
- No process-wide audio router, software echo cancellation, speaker diarization model, process isolation, or selected-browser-tab isolation. Endpoint loopback includes every sound routed to the selected playback device.
- No F04 work and no refactor of the existing F02 video pipeline beyond the minimal lifecycle coordination needed to start and stop both loops safely.

F03 keeps transcripts in session memory only. A later approved feature may persist an approved transcript using the existing local-first policy, but F03 itself will not add persistence.

## Approved decisions

These decisions, including the approved Gate A v2 revision, are approved:

1. **Capture binding:** use only `PyAudioWPatch==0.2.12.8` for explicit microphone and endpoint-loopback enumeration/opening. The native process-loopback experiment failed the real WhatsApp assertion and was removed.
2. **Loopback scope:** bind playback to one explicitly selected render/loopback pair in the same live PortAudio enumeration context. Every sound routed to that playback endpoint is in scope. The UI and manual checklist require Chrome and other non-call audio to be closed or silent during WhatsApp/Zoom; Meet uses Chrome but requires every other tab/application to remain silent.
3. **Acoustic crossover:** do not require headphones. Test the user's actual microphone and speakers first. They pass when loopback speech does not create duplicate `user` turns; if crossover appears, adjust microphone gain/device routing and retest, with headphones remaining an optional mitigation. F03 does not add echo cancellation unless the tested setup cannot meet the attribution gate and the plan is explicitly revised.
4. **Local model:** the initial `faster-whisper` 1.2.1 `small` CPU `int8` candidate failed the repeated Auto-language latency gate. The user then separately approved the pinned CUDA 12/cuDNN 9 wheel runtime. The post-completion English path uses GPU `float16` `mobiuslabsgmbh/faster-whisper-large-v3-turbo` pinned at revision `0a363e9161cbc7ed1431c9597a8ceaf0c4f78fcf`, with no CPU or cloud fallback.
5. **Language:** offer English only and pass `language="en"`. Hebrew and Auto were removed after the 2026-08-25 free local model comparison found no sufficiently accurate Hebrew candidate. Transcribe rather than translate.
6. **Turn presentation:** show only finalized turns. While speech is open or inference is running, show source-specific `Listening`/`Transcribing` state, not unstable partial text.
7. **Cloud contingency:** if and only if the local candidate fails an approved accuracy or latency gate, stop and present the evidence. A separately approved revision may replace it with low-cost OpenAI `gpt-transcribe`; the product will not retain two transcription implementations merely as speculative fallback.
8. **Validation:** WhatsApp is required. Zoom and Google Meet require real validation or explicit user waivers recorded as `WAIVED — not passed`.
9. **Call-source priority:** an eligible WhatsApp `Video call` suppresses Chrome/Meet candidates. If one appears while Meet is already active, stop both audio sides and require explicit reselection; never switch automatically. An idle WhatsApp main window does not suppress Meet. Zoom remains independently selectable.

## Technology comparison

### Windows capture

| Candidate | Fit | Decision for spike |
|---|---|---|
| Native endpoint WASAPI COM | Maximum endpoint control; supports `IAudioCaptureClient`, endpoint IDs, device notifications, and endpoint-wide loopback | Not needed because the approved Gate A v2 behavior passes with PyAudioWPatch. |
| Native process loopback | Includes one target process tree on Windows build 20348+ and is independent of the render endpoint | **Rejected after live WhatsApp failure on 2026-08-25.** The exact active WhatsApp render-session PID and every related WebView PID returned digital silence (`peak 1`, RMS `0.479`) through both the bundled helper and a Microsoft-sample-style event-driven 44.1 kHz trial. The helper/source/binary were removed. |
| `PyAudioWPatch` 0.2.12.8 | Windows wheels support Python 3.12 and explicit WASAPI microphone plus render/loopback indices | **Selected for both production sources.** Gate A v2 proves the endpoint behavior and teardown; endpoint-wide scope is disclosed and controlled operationally. |
| SoundCard | Pure Python/CFFI WASAPI and loopback support | Not retained as fallback. Its documented Windows channel/block-size limitations make it a second choice only if the plan is revised. |
| `sounddevice` | Already installed and good for ordinary input/output | Rejected because upstream PortAudio does not currently expose loopback devices here. |
| FFmpeg/DirectShow | Already installed | Rejected because this machine exposes no playback-loopback input through DirectShow. |

Windows documents endpoint loopback through `AUDCLNT_STREAMFLAGS_LOOPBACK` in shared mode, capture through `IAudioCaptureClient`, stable endpoint identity through device properties, and device-change callbacks through `IMMNotificationClient`. Device invalidation must be recovered explicitly rather than silently switching sources. Sources: [Loopback Recording](https://learn.microsoft.com/en-us/windows/win32/coreaudio/loopback-recording), [Capturing a Stream](https://learn.microsoft.com/en-us/windows/win32/coreaudio/capturing-a-stream), [`IAudioCaptureClient::GetBuffer`](https://learn.microsoft.com/en-us/windows/win32/api/audioclient/nf-audioclient-iaudiocaptureclient-getbuffer), [Device Properties](https://learn.microsoft.com/en-us/windows/win32/coreaudio/device-properties), [`IMMNotificationClient`](https://learn.microsoft.com/en-us/windows/win32/api/mmdeviceapi/nn-mmdeviceapi-immnotificationclient), [invalid-device recovery](https://learn.microsoft.com/en-us/windows/win32/coreaudio/recovering-from-an-invalid-device-error), and Microsoft’s [process-loopback sample](https://learn.microsoft.com/en-us/samples/microsoft/windows-classic-samples/applicationloopbackaudio-sample/).

The retained microphone binding is documented at [`PyAudioWPatch`](https://github.com/s0d3s/PyAudioWPatch). The process path follows Microsoft's [Application Loopback sample](https://github.com/microsoft/Windows-classic-samples/tree/main/Samples/ApplicationLoopback) and `AUDIOCLIENT_ACTIVATION_TYPE_PROCESS_LOOPBACK`. The rejected alternatives are documented at [SoundCard](https://github.com/bastibe/SoundCard) and the open [`sounddevice` loopback request](https://github.com/spatialaudio/python-sounddevice/issues/281).

### Transcription

| Candidate | Privacy/offline | Expected fit | Decision |
|---|---|---|---|
| `faster-whisper small`, CPU `int8` | Local after model provisioning; no call audio leaves the process | Current machine sanity result is faster than real time; multilingual; word timestamps and Silero VAD available | **First candidate.** Must pass representative replay and live gates. |
| `faster-whisper` on RTX 4060 Ti | Local, but requires CUDA 12 cuBLAS and cuDNN 9 | Likely lower latency; adds a system-runtime prerequisite and deployment burden | Test only if CPU fails latency while meeting quality, and only after separate approval to install the runtime. |
| OpenAI `gpt-transcribe` | Sends call audio off-device; requires internet | Current low-cost transcription option: $0.0045/minute; supports completed files, streamed file transcripts, and committed Realtime turns | Contingency only after an explicit local-gate failure and separate privacy/cost approval. |
| OpenAI `gpt-live-transcribe` | Sends call audio off-device; requires internet | Lower-latency realtime deltas, but currently $0.017/minute | Not the low-cost default; consider only if the approved cloud path also fails the latency requirement. |
| `gpt-4o-mini-transcribe` / realtime Whisper alternatives | Cloud-only | Current alternatives, but neither is the recommended cost/requirement match | Not retained. |

The later 2026-08-25 free-model comparison supersedes the initial multilingual
assumption: Hebrew-tuned large-v3 was best at 22.2% word error on real FLEURS speech,
which the user rejected as insufficient. No tested free local Hebrew model is retained
for production. A paid/cloud candidate would require a separate privacy and cost decision.

Official local references: [`faster-whisper`](https://github.com/SYSTRAN/faster-whisper), [CTranslate2 installation](https://opennmt.net/CTranslate2/installation.html), [hardware support](https://opennmt.net/CTranslate2/hardware_support.html), [quantization](https://opennmt.net/CTranslate2/quantization.html), and [OpenAI Whisper model sizes](https://github.com/openai/whisper/blob/main/README.md?plain=1). Current cloud references: [OpenAI transcription models](https://developers.openai.com/api/docs/models), [`gpt-transcribe`](https://developers.openai.com/api/docs/models/gpt-transcribe), [`gpt-live-transcribe`](https://developers.openai.com/api/docs/models/gpt-live-transcribe), and the [OpenAI audio guide](https://developers.openai.com/api/docs/guides/audio).

### Explicit pass/fail spike

The spike is disposable evidence, not parallel production implementations.

### Gate A v1 implementation result — FAILED 2026-08-19

The approved `PyAudioWPatch` candidate failed Gate A v1's stable-endpoint-ID assertion and was removed without adding project code or dependencies. This evidence is retained. On 2026-08-19 the user approved Gate A v2, which replaces that implementation-specific assertion with the behavioral identity and no-silent-switch contract below.

- An isolated clean Python 3.12.10 environment installed `PyAudioWPatch==0.2.12.8`; `pip check` passed. The CPython 3.12 x64 wheel was 99,319 bytes with SHA-256 `fd163a6531c4e4969925e687ef1bc57fae8ecc1a95de7ba707a436622552d7fa` and declared Apache-2.0 licensing.
- The binding enumerated the two actual WASAPI microphones, four render endpoints, and four matching loopback devices by friendly name. The current defaults were `Microphone (USB Audio Device)` and `Big Speakers (High Definition Audio Device) [Loopback]`.
- Every WASAPI device record exposed only `index`, `name`, `hostApi`, channel counts, default sample rate/latencies, `isLoopbackDevice`, and `structVersion`. The complete public device-related `PyAudio` API and all returned record keys contained no Windows endpoint ID, GUID, or other opaque stable endpoint identity.
- The available `index` is a transient PortAudio enumeration position, not the Windows endpoint ID required by the approved device-selection and no-silent-switch contract. Friendly-name matching cannot repair this because names can be duplicated and the approved plan explicitly requires retaining the opaque endpoint ID internally.
- Because Gate A passes only if every assertion succeeds, live two-stream capture, silence, disconnection, and ten-minute stability checks were not run after this decisive failure. Per the approved hard boundary, no SoundCard/native COM fallback, project dependency, capture implementation, fixture, transcription spike, CUDA runtime, or cloud path was added.

**Gate A v2 — capture binding (approved revision)**

Pass only if one clean Python 3.12 environment can:

- enumerate friendly names plus session-scoped PortAudio indices and the complete device record used for selection;
- keep one enumeration context from selection through Start, explicitly open the chosen microphone and loopback indices together, and never open an implicit default;
- immediately before opening, revalidate each selected record's index, name, host API, direction/loopback flag, channel count, and sample rate; any mismatch or missing record must fail closed and require refresh/reselection;
- disambiguate duplicate friendly names with the current session index, without claiming the index is stable or persisting it across app restarts/new enumeration contexts;
- receive distinct callback streams at their reported native formats;
- represent silent loopback buffers as silence rather than stale audio;
- prove that a default-device change does not switch an active explicitly opened stream, and detect start-time unavailability, enumeration change, and mid-session disconnection by stopping and requiring reselection;
- run for 10 minutes with zero callback overflow, no unbounded allocation, and complete stream teardown; and
- do all of the above without writing audio files.

If Gate A v2 fails, remove the binding and spike code, document which behavioral assertion failed, and stop for plan revision. Do not quietly add SoundCard or native COM as a second backend.

### Gate A v2 implementation result — PASS 2026-08-19

- One clean Python 3.12.10 environment installed only `PyAudioWPatch==0.2.12.8`; `pip check` passed. Selection and Start shared one live enumeration context, retained complete device records, revalidated every approved field, and opened only explicit indices.
- The actual USB microphone opened explicitly at session index 20, stereo 48 kHz PCM16. The matching Big Speakers loopback opened explicitly at session index 25, stereo 192 kHz PCM16; the test stimulus used render index 19 explicitly.
- Changed and missing record preflight checks failed closed before opening. An atomic second-stream open failure using a valid index with an unsupported channel count left zero streams. Duplicate-label behavior produced the required session-only `[WASAPI #<index>]` suffix.
- A generated one-second in-memory tone produced loopback RMS 572.3 between digital-silence medians of 0.0 before and after. Microphone and loopback used separate bounded callback handoffs from their first callbacks onward.
- The 600.8-second dual-stream run received 28,142 microphone callbacks and 258 loopback callbacks, observed zero callback overflows, and reached queue-depth peaks of 1/94 and 2/375 blocks. Declared raw capacity was 1,921,024 bytes.
- Working set was 28.3 MiB at the start, 28.7 MiB peak, and 28.7 MiB at the end. Complete stream/consumer teardown took 0.106 seconds. Before/after scans found zero written audio artifacts.
- While the original explicit streams stayed active, Windows defaults were changed from the USB microphone/Big Speakers to the High Definition Audio microphone/USB Speakers. A fresh process observed new default indices 21/17 while the original streams remained on indices 20/25, delivered 19,746 microphone callbacks plus 258 callbacks for an explicit original-endpoint loopback stimulus, and tore down in 0.102 seconds. No active stream silently followed the defaults.
- For start-time unavailability, the USB audio device was removed after selection. A fresh enumeration confirmed the selected microphone and USB render/loopback records were absent. Start failed on the selected microphone before opening any stream, left zero streams, and required reselection. The binding reported PortAudio `-9992` (`Insufficient memory`) for the removed endpoint; the retained implementation maps this misleading backend text to the source-specific unavailable-device state.
- For mid-session disconnection, the USB microphone was removed while it and the non-USB Big Speakers loopback were active. A fresh enumeration confirmed removal; the active microphone stream became invalid immediately. The shared fault path stopped both audio sides, cleared both buffers, left zero streams, and required reselection; teardown took 0.109 seconds.
- Gate A v2 passes. The disposable spike harness/environment was removed, and the retained project may add only the pinned PyAudioWPatch dependency and minimum approved capture implementation.

### Gate C — process-isolated playback revision (approved 2026-08-24; failed live and retired 2026-08-25)

The user's live WhatsApp check proved the documented endpoint-wide limitation: intelligible Chrome/system playback routed to Big Speakers entered the contact transcript. The user then explicitly approved native Windows per-process capture so WhatsApp can exclude Chrome and Chrome can supply Google Meet when no WhatsApp call is active. This approval supersedes the production-playback portion of decisions 1–2 and Slice 3; Gate A v1/v2 remain preserved historical device evidence.

Pass only if the revised production path:

- takes the process ID from the exact selected eligible call-window record and includes that process tree;
- opens only the explicit microphone through PyAudioWPatch and the one native process-loopback source, with no endpoint-loopback fallback;
- captures selected-process audio while an equally audible unrelated process produces silence in the capture;
- exposes WhatsApp-over-Chrome selection priority before Start and stops/requires reselection if an eligible WhatsApp call appears during active Meet capture;
- treats target-process exit, activation/start failure, pipe failure, discontinuity, queue overflow, or reader failure as one shared two-sided fault with no silent source switch;
- emits fixed 48 kHz stereo PCM16 into the existing bounded callback/source-worker path, represents native silent flags as zero PCM, and writes no audio file;
- preserves source attribution, chronological final-only turns, privacy/offline behavior, visual-loss audio continuity, bounded memory, and complete teardown; and
- passes real WhatsApp and Google Meet validation before completion, unless Meet is explicitly waived as `WAIVED — not passed`.

Initial implementation evidence is content-free: the bundled x64 helper activated successfully and stopped cleanly against a live process. A four-second in-memory FFplay target produced 850,560 captured bytes with peak 2,892 and RMS 1,940.5. During an equally loud unrelated-process tone, a selected silent target produced 787,200 bytes with peak 1 and RMS 0.479, demonstrating process exclusion. Both probes used pipes only and created no audio file. The then-retained `native/process_loopback.cpp` source SHA-256 was `0e75cdc9286a80eb670b7a342db9cab024ee02e3885c98bb780e6492d8a9704f`; the packaged 153,600-byte x64 helper SHA-256 was `7fceeaa9a776cf786387bc7df28cadcf4be51745145f460b5398fea1a568d5c7`. Both were removed after the live failure below.

The revised focused/full suite passes 74/74 with clean dependencies and compilation. Direct checks prove exact process-ID revalidation, microphone-only PortAudio open, zero endpoint fallback, WhatsApp-over-Chrome list/runtime priority, both-side stop on priority change, and complete native-stream cleanup. F01, F02 deterministic, and F02 live WGC pass; target close took 129 ms with zero workers/frames. Offline F03 replay passes 4/4 attribution schedules with 12 chronological turns, 0.006-second maximum timestamp error, zero silence turns, zero network attempts, and zero audio artifacts. The 10.3-second combined smoke passes with 1.123-second single-source p95, 2.479-second overlap p95/maximum, queue 1/0, zero saturation, F02 at 24.38 signals/second, and zero workers/results.

A fresh 600.0-second combined run passes with 156 turns across 13 replays, 1.155-second single-source p95, 2.504/2.587-second overlap p95/maximum, queue 1/0, zero saturation, F02 at 24.99 signals/second with 13.8 ms frame-age p95, working set 307.1/872.7 MiB start/end, -6.61 MiB/min post-warm-up growth, and zero workers/results. Separately, the native helper drained 115,212,288 bytes of synthetic silent PCM over 600.1 seconds, held 9.2/11.0/11.0 MiB start/peak/end working set, exited zero after the explicit pipe stop command, and changed zero audio artifacts. Gate C's automated portion and fresh pre-manual Claude gate passed, but the required real WhatsApp assertion failed: the selected contact was audible to the user while the contact source remained at digital silence. Direct content-free probes against the exact active WhatsApp render-session PID and all seven related WebView PIDs each returned `peak 1`, RMS `0.479`. One final Microsoft-sample-style event-driven 44.1 kHz trial returned the same result. The session was stopped; no call/transcript content was recorded. This genuinely fails Gate C and invalidates its pre-manual PASS for the fallback revision.

### Gate D — explicit endpoint-loopback fallback (approved 2026-08-25; active)

The user authorized one final process-loopback correction attempt and, if it still failed, a return to the previously working playback-endpoint capture with an explicit rule not to use Chrome during WhatsApp. That attempt failed as recorded above. Production therefore returns to the already-passed Gate A v2 PyAudioWPatch path:

- one live enumeration context supplies the complete microphone and render/loopback records through Start;
- both selectors are explicit, both records are revalidated immediately before opening, and both exact indices are opened with `start=False` before either stream starts;
- a missing/changed record closes the catalog, opens zero streams when found during revalidation, clears both choices after rebuild, and requires explicit reselection;
- an active failure on either side stops both, clears buffers, and never switches to a new default or endpoint;
- a clean Stop closes both streams/workers but retains the current in-memory enumeration and selected records for an explicit restart; it never persists an index across Refresh, a rebuilt enumeration, or app restart;
- endpoint scope is displayed beside the playback selector: every sound routed there can enter the contact transcript;
- Chrome and every non-call audio application must be closed or silent during WhatsApp/Zoom; Google Meet requires Chrome for the call while every other tab/application remains silent;
- WhatsApp-over-Chrome call-window priority and visual-loss audio continuity remain unchanged; and
- the fallback needs fresh automated checks and a new F03/direct-integration Claude `PASS` before live validation resumes.

Gate D automated evidence is content-free. The retained code contains no native/process-loopback backend: it opens only the explicitly selected PyAudioWPatch microphone and matching playback-loopback indices after complete-record revalidation, starts neither until both opens succeed, and retains the existing shared two-sided fault path. Focused audio/window checks passed 47/47; the full suite passed 74/74; `pip check`, F01, deterministic F02, and WGC capture checks passed. A Windows target-close race exposed that `GraphicsCaptureSession.close()` can block after the target HWND is already gone; cleanup now revokes both handlers, closes the frame pool, and calls session close only while the target still exists. Four fresh full WGC checks passed with 0/0 remaining workers/frames; the latest target-close latency was 81 ms. The unchanged offline F03 pipeline passed 4/4 schedules with 12 turns, 0.006-second maximum timestamp error, zero silence turns, network attempts, and audio artifacts. A fresh 10.3-second combined smoke passed with 1.123-second single-source p95, 2.502-second overlap p95/maximum, queue 1/0, zero saturation, F02 at 24.34 signals/second, and zero remaining workers/results. The prior endpoint-loopback 600-second runs remain the applicable long-duration evidence because Gate D restores that exact capture design.

**Gate B — local transcription**

Run the exact same project-owned replay corpus through `small` CPU `int8` with a small sweep of 4/6/8/12 CPU threads. Select the lowest-resource setting that passes all acceptance thresholds while F02 runs at its normal 10 fps. Include simultaneous speech from both sources. The committed product pins one model, compute type, and tested thread count.

If CPU passes, do not install a GPU runtime. If CPU fails latency but passes accuracy, stop and ask before installing the current CTranslate2 CUDA/cuDNN prerequisites and testing one GPU configuration. If the best approved local configuration fails any accuracy or latency threshold twice on clean reruns, local transcription has explicitly failed. Present the corpus, normalized metrics, privacy impact, and current OpenAI price before asking whether to replace it with `gpt-transcribe`.

### Gate B CPU result — FAILED 2026-08-19

- The isolated candidate used Python 3.12.10, `faster-whisper==1.2.1`, `ctranslate2==4.8.1`, the multilingual `small` model, CPU `int8`, VAD, segment/word timestamps, translation disabled, greedy decoding (`beam_size=1`, `best_of=1`), and the approved 15-second utterance boundary. No CUDA or cloud transcription dependency was installed.
- The project-owned mono 16 kHz PCM16 corpus hashes were English `7f7ca0b47207d9ea0cf5f2617d7ffb5e8400100ffe20725ed9bc354be068b509`, Hebrew `8ac632e91478cf5b5bd7b64cc37e49d01c8fdd3fbe6c0cc45f57fd42de55f82a`, and long English `a92e8975fb44fc53be93a5a77197733fd0167cddc97f2ca47ca34a09da662e98`. Normalization treated spoken and digit forms of the scripted numbers as equivalent; no transcript text was logged or recorded as evidence.
- The 4/6/8/12-thread sweep found 12 threads fastest. At 12 threads, fixed English and Hebrew passed accuracy and latency: normalized WER was 0% for both, keyword recall was 100%/90%, and fixed-language latency was below 2.37 seconds. Auto independently detected both languages correctly with the same 0% normalized WER.
- The best configuration passed the other measured gates on two clean reruns: maximum RTF was 0.466/0.478, overlapping two-source p95/max and queue-drain time were 3.566/3.694 seconds, and all requested word timestamps were present.
- The same two clean reruns genuinely failed the single-source 3.0-second latency assertion in Auto mode. Auto English took 3.555/3.578 seconds and Auto Hebrew took 3.683/3.777 seconds, so single-source p95 was 3.683/3.777 seconds. The threshold was not lowered and Auto was not exempted.
- Gate B therefore stops at the first repeated behavioral failure before the F02-concurrency and remaining implementation slices. The isolated model/environment and disposable benchmark harness were removed. The Spike 2 card remains incomplete. Continuing requires separate approval to install and test the current CTranslate2 CUDA/cuDNN prerequisites, or an explicitly revised cloud decision; neither was inferred from this failure.

### Gate B GPU result — PASS 2026-08-19

- After reviewing the CPU evidence, the user separately approved installing the required CUDA/cuDNN runtime and testing one GPU configuration. The PC has an NVIDIA GeForce RTX 4060 Ti with 8,188 MiB and driver 610.88.
- The isolated Windows candidate used Python 3.12.10, `faster-whisper==1.2.1`, `ctranslate2==4.8.1`, NVIDIA `nvidia-cublas-cu12==12.9.2.10`, `nvidia-cudnn-cu12==9.24.0.43`, and its `nvidia-cuda-nvrtc-cu12==12.9.86` dependency. The single retained model configuration is multilingual `small`, `device="cuda"`, `compute_type="float16"`, greedy decoding (`beam_size=1`, `best_of=1`), VAD, segment/word timestamps, translation disabled, and a 15-second engine/utterance boundary.
- Two clean GPU runs passed. Normalized English/Hebrew WER was 0%/0%, keyword recall was 100%/90%, Auto independently detected both languages with 0% normalized WER, every requested word timestamp was present, and long-English normalized WER was 1.79%.
- Single-source p95/max was 0.791/0.644 seconds, overlapping two-source p95/max and queue-drain time were 0.791/0.644 seconds, and maximum RTF was 0.073/0.059 across the two runs.
- During a third replay, concurrent F02 CPU processing emitted 24.32 observations/second, frame-age p95 was 16.43 ms, retained frames remained bounded at 2 peak/0 final, and the concurrent F03 single/overlap maximum was 0.739 seconds with maximum RTF 0.068.
- No transcript text, call content, live audio, CUDA toolkit system installation, cloud transcription, or written inference audio was used. Gate B passes; the pinned GPU runtime/model configuration may proceed to implementation. The earlier CPU failure remains historical evidence and CPU is not retained as a fallback backend.

## Audio source selection and failure behavior

- List active microphones from one live PyAudio enumeration context. Retain the complete selected microphone record and its session-scoped index only until that context closes. Duplicate friendly names include `[WASAPI #<session index>]`; the label is explicitly not a persistent identity.
- Immediately before Start, re-read and compare the selected microphone record in the same enumeration context. A missing/mismatched record closes the context, clears the selector, and requires explicit reselection instead of opening another device.
- The UI preselects the current default microphone and render endpoint only on initial enumeration. It never silently follows a later default change during an active session. Duplicate friendly names use the session-only `[WASAPI #<index>]` suffix.
- Start requires an existing selected call window with a positive owning process ID, one microphone, and one language selection. The exact call-window record is revalidated before the visual/audio session opens.
- Start is atomic for F03: if either the explicit microphone or explicit endpoint-loopback source cannot open/start, close the other side, create no turn, and show the failing source and actionable reason. F02 remains independently startable only when F03 runtime/enumeration is genuinely unavailable; a usable microphone/playback pair with either choice missing blocks Start.
- If Windows microphone privacy blocks desktop apps, show a link/instruction to enable desktop-app microphone access; do not retry in a loop. Reference: [Windows microphone permissions](https://support.microsoft.com/en-us/windows/privacy/turn-on-app-permissions-for-your-microphone-in-windows).
- If the selected microphone or playback-loopback stream is removed, invalidated, or otherwise fails, stop the complete F03 audio session, close both sides, clear raw buffers, retain already-finalized in-memory turns, and require reselection.
- If F02 loses or closes its selected visual target after F03 audio has started successfully, release the visual session and continue the already-open microphone plus playback-loopback streams with a visible `transcription continuing` status. Do not infer that the call ended, do not switch video/audio targets, and keep Stop/close available. If no healthy audio session exists, retain F02's existing full-stop behavior.
- A device arrival/default change refreshes the inactive selectors with a new enumeration context and clears both prior choices. It never switches an active session. The explicitly opened microphone/loopback indices remain fixed until Stop/fault.
- While a WhatsApp call source exists, Chrome/Meet candidates are absent. If WhatsApp becomes eligible during an active Meet session, stop both audio sides with `WhatsApp call available — reselect`; do not switch to WhatsApp automatically.
- Ten seconds of no voiced audio changes that source’s status to `Listening — no speech detected`. Silence is not an error and creates no `ConversationTurn`.
- User Stop returns UI control within 250 ms, first closes capture, then finalizes an open voiced segment of at least 300 ms, drains accepted transcription work for at most five seconds, and reports if a final segment could not finish. All remaining PCM is then cleared.

## Source separation, segmentation, and turn construction

### Separation

- Keep the microphone and playback-loopback callbacks in two buffers from their first blocks onward.
- Microphone is hard-mapped to `SpeakerRole.USER`; selected playback-endpoint loopback is hard-mapped to `SpeakerRole.SELECTED_CONTACT`.
- Do not diarize or guess speaker identity from audio.
- Do not mix the streams before transcription.
- The loopback source includes the complete selected render-endpoint mix. Every application routed there can enter the contact source, so the UI and test procedure require non-call audio to be closed or silent. Speaker playback must still not leak acoustically into the microphone.

### Audio normalization and speech boundaries

- The capture callback only copies a small native-format block into its source’s bounded handoff and returns; it performs no model work, disk I/O, UI access, or blocking wait.
- A source worker uses the PyAV dependency already brought by `faster-whisper` to downmix and resample to mono 16 kHz PCM for speech segmentation and inference.
- Start an utterance after voiced energy remains above a calibrated source threshold for 100 ms. End after 600 ms of silence. The UI exposes one simple microphone sensitivity calibration because real microphones and rooms differ; system-audio uses a tested fixed digital threshold.
- `faster-whisper` VAD filters remaining non-speech inside each finalized utterance.
- Ignore voiced fragments shorter than 300 ms. Force a final boundary at seven seconds (below the approved 15-second ceiling) so memory and cross-source visible latency remain bounded; continued speech starts the next turn.
- Empty/whitespace output, VAD-only silence, and known no-speech tokens create no turn.

### Language, timestamps, and final turns

- Production uses `language="en"`. Hebrew and automatic language detection are excluded until a future free model passes a new representative accuracy comparison. Translation is disabled.
- Request segment and word timestamps from `faster-whisper` for boundary/accuracy checks. F03 does not expand `ConversationTurn`; transient word timestamps are discarded after construction.
- `ConversationTurn.timestamp` is an aware UTC wall-clock timestamp corresponding to the utterance’s first voiced capture sample. Ordering uses a monotonic capture timestamp plus a sequence number, never inference completion time.
- Microphone turns use `speaker_name="You"`, `speaker_role=user`, `source="microphone"`, and `is_media=False`.
- Loopback turns use the selected contact’s existing name, `speaker_role=selected_contact`, `source="system_audio_loopback"`, and `is_media=False`.
- `content` is the trimmed final transcript and `display_order` is assigned only when the ordered turn is released to the Tk-owned session list.
- A later-finished inference may not overtake an older active or queued utterance. Hold the newer final in a small reorder buffer until no older two-source utterance remains, then release by `(utterance_started_monotonic, capture_sequence)`.
- F03 shows no partial transcript. The only intermediate data is source status; a `ConversationTurn` is immutable/final once displayed.

## Queue, threading, buffering, and shutdown rules

Use the existing Tk ownership rule: only the main thread touches widgets and the in-memory displayed turn list.

- F02 keeps its existing video capture callback, one-frame slot, and video worker.
- F03 adds one PortAudio callback per explicit microphone/loopback stream, one lightweight normalize/segment worker per source, and one local transcription worker. Add no second inference worker unless one worker later fails the approved overlap gate.
- Each callback handoff holds at most two seconds of that source’s native audio.
- Each open utterance holds at most seven seconds of mono 16 kHz PCM.
- The completed-utterance queue holds at most four raw jobs total; the bounded final-result/reorder handoff holds at most 512 finalized text results and no raw audio.
- Every `put` from a callback is non-blocking. A full callback, utterance, or result buffer is a visible `Audio processing cannot keep up` session fault: stop capture and clear audio instead of blocking, growing, or silently dropping speech.
- Total raw PCM retained by F03 is hard-capped at 12 MiB. Any raw job older than 30 seconds is a fault and is cleared, not transcribed late.
- Tk polls a bounded status/result handoff with `after`; workers never call Tk.
- Start creates fresh stop events, buffers, and workers. No worker or buffer is reused after a fault.
- Stop order is: set stop intent; stop/close both capture streams; finalize eligible open utterances; drain accepted jobs within the five-second deadline; close segment/inference workers; release raw buffers and model references; publish the final state on Tk.
- Start/Stop is safe for ten consecutive cycles. On close-window, the same stop path runs before Tk destruction. A second Stop is harmless.
- Logs may contain session indices/device names, process IDs, durations, queue depths, latency, and error codes. They may never contain PCM, transcript text, contact names, window titles, API keys, or call content.

## Raw-audio lifetime and privacy checks

- Live audio exists only in bounded RAM from capture until its turn is finalized or the session faults/stops. Healthy-path maximum age is 30 seconds; teardown clears it within five seconds.
- Pass NumPy audio directly to `faster-whisper`; do not create temporary WAV/MP3/FLAC files.
- The local model is provisioned before a call. Runtime Start never downloads a model and never silently switches to cloud. If the model is absent, show `Local transcription model is not installed`.
- After one-time model provisioning, disconnect networking and run replay plus a session start/stop check. Local mode must remain usable.
- An automated privacy check snapshots the test working directory and system temp directory before/after replay and asserts that no audio artifact was created. A network-denial check asserts local inference makes no socket/API attempt after the model is cached.
- Generated test fixtures are the only audio committed to Git. Their exact scripts, generator/voice or recording consent, date, and license/ownership are recorded beside them. They contain no call audio, names, private content, or copied third-party recordings.
- Finalized transcripts remain in process memory for the current session only. Closing/restarting the app loses them in F03.
- If cloud is later approved, the privacy plan and ADR must be revised before implementation; no key or raw response may enter Git/Trello/logs.

## Implementation slices

Each slice has one matching Trello card and remains open until its acceptance evidence exists.

### Slice 0 — approve the feature plan — complete

- On 2026-08-19 the user approved endpoint-wide loopback, English/Hebrew/Auto, final-only turns, and planned WhatsApp/Zoom/Meet validation.
- The user revised the hardware rule: use and test the actual microphone/speakers instead of requiring headphones.
- This plan records those answers and is Approved. No implementation began during planning.

### Slice 1 — capture binding spike — complete

- Add `PyAudioWPatch` only in an isolated spike, exercise the actual endpoints, and run Gate A v2 with one enumeration context, explicit indices, record revalidation, default-change behavior, and no persisted device choice.
- Record package/wheel/Python compatibility and measured format/teardown results in this plan.
- Delete the spike if it fails; if it passes, add only the pinned runtime dependency and smallest capture code required by Slice 3. PyAudioWPatch is the sole retained capture backend after the later native process experiment failed live and was removed.

### Slice 2 — transcription and segmentation spike — complete

- Create safely generated, project-owned fixtures for the approved languages and source schedules.
- Run Gate B, including overlapping speech and F02 at 10 fps.
- Pin one local model/configuration if it passes. Keep no cloud client or second local engine.
- If it fails, stop for the explicit GPU/cloud decision path; a failure is not permission to expand scope automatically.

### Slice 3 — device selection and two-source capture — complete

- Enumerate/select session-scoped device records and implement fail-closed revalidation, atomic explicit-index two-stream start, silence state, disconnect detection, and stop.
- Preserve F02 as-is except for minimal lifecycle coordination.
- Add focused tests for selection, unavailable endpoints, disconnect, no silent switch, and bounded callback overflow.

Gate D reinstates the completed endpoint-loopback implementation after Gate C failed live. Revised Slice 3 requires an explicit microphone plus explicit render/loopback pair from one enumeration context, with WhatsApp-over-Chrome call-window priority, a visible endpoint-wide warning, and no native backend.

The approved 2026-08-25 UI follow-up retains those selector values only after a clean Stop while their original live catalog remains open. Refresh and every fault rebuild the catalog, clear both values, and require explicit reselection; no friendly-name remapping or cross-context index reuse is allowed.

### Slice 4 — local transcription and ordered turns — complete

- Implement source-specific segmentation, one chosen model instance/configuration, final-only inference, timestamp mapping, `ConversationTurn` construction, and chronological release.
- Add focused tests for silence, minimum/maximum utterances, attribution, timestamp/order, simultaneous speech, empty output, and inference failure.

### Slice 5 — Tk/F02 integration and user states — complete

- Add minimal selectors/status/transcript controls and bounded Tk polling.
- Collapse an unavailable/blank selected-face thumbnail so the prior finalized transcript and live microphone/playback state remain visible while audio continues.
- Implement responsive asynchronous shutdown and window-close teardown.
- Prove no widget access occurs off the main thread and F02 keeps processing during inference.

### Slice 6 — deterministic replay and privacy/offline validation — complete

- Run unit tests with a deterministic fake transcriber for state/failure branches.
- Run the full local model on the committed two-source corpus without live devices.
- Verify attribution/order, no hallucinated silence, no raw artifacts, cached-model offline operation, and no network calls.

### Slice 7 — performance and resilience validation — complete

- Run 10 minutes of dual-source replay with overlapping speech while F02 runs at 10 fps.
- Exercise unavailable devices, unplug/disable, queue saturation, model exception, Stop during speech/inference, visual-window close with no healthy audio (full stop), visual-window close with healthy audio (visual teardown plus transcription continuity), and ten restart cycles.
- Record only aggregate non-content metrics in this plan.

### Slices 3–7 implementation and automated evidence — PASS 2026-08-19

- At that pre-Gate-C stage, the retained implementation added one `conversation_copilot.audio` module, one focused audio test file, the generated fixture directory, minimal Tk controls, and the approved pinned dependencies only. Capture was exclusively `PyAudioWPatch==0.2.12.8`; transcription remains exclusively `faster-whisper==1.2.1`/CTranslate2 4.8.1 with the approved CUDA FP16 `small` configuration. The playback statement is preserved as historical evidence and was superseded by the approved process helper.
- Device choices retain complete WASAPI records plus session indices in one live catalog. Tests cover duplicate labels, changed-record zero-open invalidation, explicit microphone/loopback indices, atomic second-open cleanup, oversized native-format rejection against the 12 MiB cap, callback overflow faulting, and active-stream disconnection stopping both sides. No index or device choice is persisted.
- Source workers use PyAV to downmix/resample to mono 16 kHz PCM16. Tests cover silence, 100 ms start, 600 ms end, 300 ms minimum, seven-second maximum, fixed physical-source roles, capture timestamp retention, later-result ordering behind older speech, empty/failing inference, queue clearing, idempotent Stop, and ten restart cycles.
- A real production-path endpoint smoke opened two explicit streams with four workers, observed no fault, and ended with zero streams/workers/results. Ten real endpoint reopen cycles passed; maximum complete stop/teardown was 0.146 seconds with zero streams, workers, and jobs after every cycle.
- The cached-model offline replay passed with fixed English/Hebrew normalized WER 0%/0%, keyword recall 100%/90%, correct Auto detection, max RTF 0.089, fixed inference max 0.973 seconds, correct attribution/order 3/3, zero silence turns, zero network attempts, and zero audio artifacts.
- Same-process testing exposed a native load-order crash when MediaPipe loaded before CTranslate2. The shared audio module now preloads the pinned CTranslate2 runtime after registering the isolated NVIDIA DLL directories; a 10-second regression and the full 10-minute run both passed in the actual one-process F02/F03 arrangement.
- The 600.46-second run completed 966 timestamped GPU transcriptions. F03 p95/max latency was 1.051/1.847 seconds, maximum RTF was 0.111, job-queue peak was 1, process working-set start/peak/end was 265.3/904.9/832.6 MiB, post-warm-up growth was -7.66 MiB/min, and release ended at 812.1 MiB. Concurrent F02 ran 600.04 seconds at 24.06 observations/second with 18.88 ms frame-age p95 and 2 peak/0 final retained frames.
- Focused audio tests passed 12/12. The pre-manual rerun passed all 44 tests, dependency and compile checks, F01 headless, F02 deterministic, F02 live capture, and cached-model replay; replay recorded zero network attempts and zero audio artifacts.
- Computer Use inspection of a fresh corrected Tk process confirmed explicit default selections for `Microphone (USB Audio Device)` and `Big Speakers (High Definition Audio Device)`, clean idle controls, and no eligible call window. The inspected process was then closed completely.

### Slice 8 — pre-manual Claude Opus review

- Review only the approved F03 plan, the complete F03 feature/direct-integration diff, changed F03 tests, deterministic fixture provenance, and F03 evidence before asking the user to open any test calls. A whole-project Claude review is deferred to the later project-wide gate.
- Require the exact final verdict `PASS`; resolve every accepted finding and rerun affected checks until that verdict is obtained.
- This is the standard entry gate for manual app validation, so the user tests only a revision that has already passed independent review.
- The first tool-less Claude Opus 5 review returned `NOT PASS`. It identified one critical lock-order deadlock, three high-severity result-queue/runtime/replay gaps, and medium/low shutdown, device, timestamp, validation, diagnostics, UI, and reproducibility findings. No manual validation was requested.
- Accepted corrections removed the lock inversion and lossy four-item text queue; deferred callback faults to the monitor; added two-source processed-time watermarks; moved model validation/load before stream opening; made CTranslate2 preload explicit and failure-safe before MediaPipe; made PortAudio enumeration/close fail-safe; moved blocking stream teardown off Tk; added timeout reporting and daemon-safe exit; preserved F02 on an audio-only fault; cleared call transcripts and used the selected window label; pinned direct PyAV use; and committed the concurrent benchmark command.
- The offline check now feeds all scheduled native blocks through the production PyAV, resampler, segmenter, GPU worker, role mapping, and orderer. It passed 3/3 schedule groups, produced eight chronological turns, measured 0.024-second maximum first-voice timestamp error, rejected five minutes of digital silence plus seeded room noise/transient input, attempted zero network connections, and wrote zero audio artifacts.
- Corrected focused audio tests passed 23/23 and the full suite passed 55/55. Dependency, compile, F01 headless, F02 deterministic, and F02 live-capture checks all passed.
- The committed 600.0-second concurrent benchmark passed with 120 finalized turns across 15 full replays, F03 final-latency p95/max 0.521/0.668 seconds, job queue peak/final 1/0, F02 25.00 signals/second with 14.9 ms frame-age p95, working-set start/end 284.0/846.3 MiB, post-warm-up growth -6.19 MiB/min, and zero remaining workers/results.
- The second tool-less Claude Opus 5 review returned `NOT PASS`; no manual validation was requested. It found idle-loopback watermark starvation, mixed clock domains around an unregistered 100 ms speech candidate, latency measured before ordered release, replay formats that bypassed production resampling, and several truthful-metrics, diagnostics, refresh, and shutdown gaps.
- Accepted corrections advance an idle source with a safety margin while clamping at an unregistered candidate, use callback monotonic time for both source ordering and watermarks, record latency only after a successful final-result enqueue, replay 48 kHz stereo microphone plus 192 kHz stereo loopback input, and expose actual final queue/worker/result counts. The maximum utterance is seven seconds to keep an older open turn from hiding a newer completed source turn beyond the eight-second gate.
- The corrected replay adds a short loopback turn overlapping the long microphone fixture. It passed 4/4 production-pipeline schedule groups with 12 chronological final turns, 0.048-second maximum timestamp error, zero silence turns, zero network attempts, and zero written/modified audio artifacts. Focused audio tests passed 28/28 and the full suite passed 60/60; dependency, compile, F01, F02 deterministic, and F02 live-capture checks also passed.
- The first corrected 600-second rerun reached the benchmark assertion, but the command had accidentally compared maximum overlapping-source latency with a five-second value instead of the approved eight-second maximum. It emitted no transcript or call content. The assertion was restored to the approved p95/maximum thresholds and now reports only aggregate values on failure; no failed run is counted as passing evidence.
- The next 600-second rerun measured combined final-release p95/max of 3.861/3.957 seconds with queue peak 1. Those values pass the approved overlap limits, but the harness still incorrectly applied the three-second single-source p95 to the mixed single/overlap population. The schedule now contains distinct non-overlap and overlap intervals, and the harness reports and asserts their latency populations separately; this diagnostic run is also not counted as passing evidence.
- Corrected clean 600-second evidence run 1 passed with 156 finalized turns across 13 replays. Single-source final-release p95 was 0.592 seconds; overlap p95/maximum was 1.865/1.869 seconds; job queue peak/final was 1/0; F02 delivered 24.99 signals/second with 14.1 ms frame-age p95; working set start/end was 311.4/878.5 MiB with -6.53 MiB/min post-warm-up growth; and workers/results remaining were 0/0.
- Corrected clean 600-second evidence run 2 passed with 156 finalized turns across 13 replays. Single-source final-release p95 was 0.594 seconds; overlap p95/maximum was 1.861/1.879 seconds; job queue peak/final was 1/0; F02 delivered 24.99 signals/second with 14.0 ms frame-age p95; working set start/end was 311.6/877.8 MiB with -6.68 MiB/min post-warm-up growth; and workers/results remaining were 0/0.
- The third, explicitly F03-scoped tool-less Claude Opus 5 review returned `NOT PASS`; no manual validation was requested. It found two high-severity sparse-callback/open-utterance and failed-stream-start teardown defects, plus F03 integration findings covering F02-only Start, final Stop-result draining, native timestamp tolerance, callback/sparse replay fidelity, stream-close synchronization, truthful saturation and speech-end latency metrics, refresh failure handling, and selected-only revalidation.
- Accepted corrections finalize an active utterance after 600 ms of wall-clock callback inactivity, never join an unstarted monitor, keep F02 video independently startable when F03 is unavailable, drain final turns immediately before session release, drive replay through the real callback with sparse loopback delivery, enforce source-native timestamp tolerances, synchronize stream status/close, count saturation faults, measure from the last voiced block, catch enumeration failures at the Tk boundary, and revalidate only the complete selected microphone/render-loopback records. The reviewer suggestion to tolerate nonzero PortAudio callback flags was rejected because the approved no-silent-drop contract requires any capture-integrity flag, including overflow, to stop both sides visibly.
- Corrected focused audio tests passed 31/31 and the full suite passed 63/63. Dependency, F01, F02 deterministic, and F02 live-capture checks passed. The callback-driven sparse replay passed 4/4 schedule groups with 11 chronological turns, 0.006-second maximum native-block timestamp error, zero silence turns, zero network attempts, and zero written/modified audio artifacts. A concurrent smoke benchmark measured true speech-end-to-final p95 of 1.202 seconds single-source and 2.463 seconds overlap (2.463 maximum), queue peak/final 1/0, zero saturation faults, and zero remaining workers/results.
- Two fresh post-correction 600-second runs passed. Each completed 156 turns across 13 replays with job queue peak/final 1/0, zero saturation faults, F02 at 24.99 signals/second, negative post-warm-up memory growth, and zero remaining workers/results. Run 1 single-source p95 and overlap p95/maximum were 1.124 and 2.506/2.519 seconds; run 2 was 1.137 and 2.481/2.518 seconds. F02 frame-age p95 was 16.6/15.9 ms and working-set start/end was 309.9/877.0 and 310.1/876.8 MiB.
- The fourth F03-scoped tool-less Claude Opus 5 review returned `NOT PASS`; no manual validation was requested. It verified every third-review correction, then found two remaining direct-integration blockers: a rebuilt enumeration correctly cleared explicit device choices but Start could silently continue video-only, and the sole `TurnDraft` to `ConversationTurn`/Tk heartbeat path lacked direct construction coverage and exception-safe re-arming.
- Accepted corrections block Start with a visible selection prompt whenever an available catalog has no explicit microphone/render choices, while still allowing F02 video when the F03 runtime or enumeration itself is unavailable. The shared audio-draft conversion now has both-source `ConversationTurn` coverage; polling is split into one guarded update plus an unconditional 100 ms re-arm; and catalog close/rebuild failures remain inside the UI error boundary. Focused audio/direct-integration tests pass 32/32.
- The post-correction full suite passed 65/65 with a clean dependency check. F01, F02 deterministic, and F02 live-capture checks passed; target-close took 30 ms with zero remaining workers/frames. The callback/sparse F03 replay again passed 4/4 attribution, 0.006-second maximum timestamp error, zero silence turns, zero network attempts, and zero audio artifacts. Direct state coverage proves that a usable catalog with cleared choices blocks for explicit reselection, while a missing catalog or one with no usable pair leaves F02 video start available.
- The fifth F03-scoped tool-less Claude Opus 5 review returned `NOT PASS`; no manual validation was requested. It verified the immediately prior corrections, then found a sparse sub-100 ms candidate that could pin the source watermark, a microphone no-speech indicator checked only on queue timeout, two remaining unguarded catalog-close UI paths, and missing Windows desktop-app microphone-privacy guidance.
- Accepted corrections clear any stale sparse candidate after 600 ms without callbacks, evaluate the ten-second no-speech status on both continuous-block and sparse paths, contain every catalog close at the Tk boundary, add actionable Windows privacy guidance to the microphone-open error and README, disable face switching during asynchronous Stop, and preserve an enumeration-failure status instead of replacing it with a selection prompt. The existing F02 benchmark delegate already asserts the concurrent signal-rate and warm-memory thresholds before F03 prints them; they are not print-only gates.
- Focused F03/direct-integration tests passed 36/36 and the full suite passed 68/68 with clean dependencies. F01, F02 deterministic, and F02 live-capture checks passed; target-close took 120 ms with zero workers/frames. F03 callback/sparse replay passed 4/4 attribution with 0.006-second maximum timestamp error, zero network attempts/audio artifacts, and the concurrent smoke benchmark passed with 1.071-second single-source p95, 2.446-second overlap p95/maximum, queue peak/final 1/0, zero saturation, and zero workers/results.
- The sixth F03-scoped, tool-disabled Claude Opus 5 review independently rechecked the complete feature and its directly consumed `ConversationTurn`/benchmark contracts. It verified every fifth-review correction, found no blocker to manual application validation, and returned the exact final verdict `PASS`. The review recorded only aggregate/code evidence and no transcript, call content, contact name, recording, or window title.
- The first WhatsApp manual attempt began after that PASS and confirmed a healthy explicitly selected USB-microphone/Big-Speakers session with both audio indicators and F02 visual signals. Before the scripted acceptance sequence completed, visual-target loss ended the combined session and the user approved the revised audio-continuity behavior above. The attempt was stopped, contains no passing/failing manual evidence, and records no call content. The material lifecycle revision invalidates the sixth review as the current pre-manual gate.
- The correction releases a finished/lost F02 visual session while a healthy F03 session remains active, disables visual controls, clears visual metrics, shows `transcription continuing`, and preserves explicit Stop/close. It never rebinds video. A focused lifecycle check proves only a running audio session survives video end; absent/stopped audio retains the previous full-stop decision.
- Post-correction compile/dependency checks passed, focused F03/direct-integration tests passed 37/37, and the full suite passed 69/69. F01 and deterministic F02 passed. A chained F02 live-capture check had one teardown timeout and is not counted; the immediate isolated rerun passed with 117 ms target-close latency and zero remaining workers/frames.
- The offline production-pipeline replay passed 4/4 attribution schedules with 12 finalized turns, 0.006-second maximum timestamp error, zero silence turns, zero network attempts, and zero audio artifacts. A 10.3-second concurrent smoke passed with 1.158-second single-source p95, 2.460-second overlap p95/maximum, queue peak/final 1/0, zero saturation, F02 at 24.22 signals/second, and zero workers/results.
- A fresh 600.0-second concurrent run passed with 156 turns across 13 replays, 1.129-second single-source p95, 2.481/2.564-second overlap p95/maximum, queue peak/final 1/0, zero saturation, F02 at 24.99 signals/second with 14.5 ms frame-age p95, working-set start/end 309.9/876.8 MiB, -6.73 MiB/min post-warm-up growth, and zero remaining workers/results.
- The seventh F03-scoped, tool-disabled Claude Opus review rechecked the current complete feature/direct-integration bundle, the revised visual-loss contract, previously accepted explicit-reselection/`ConversationTurn`/Tk-heartbeat/no-usable-pair behavior, tests, provenance, plans, and aggregate evidence. It found no blocker to resuming manual application validation and returned the exact verdict `PASS`. No live-call content was included.
- The subsequent live endpoint-scope check correctly transcribed unrelated intelligible playback from the selected endpoint. That was a pass against the then-approved endpoint-wide limitation, but the user rejected that product behavior and approved process isolation on 2026-08-24. This material playback/source-priority revision invalidates the seventh review as the current pre-manual gate. No further manual acceptance request is made until Gate C automated checks and a fresh F03/direct-integration Claude review return exact `PASS`.
- The eighth F03-scoped, tool-disabled Claude Opus 5 review received the complete process-isolation revision and direct-integration bundle: native helper source/binary provenance, exact-PID and source-priority changes, latest explicit-reselection/`ConversationTurn`/Tk-heartbeat/no-usable-pair behavior, tests, plans, and aggregate content-free evidence. Canonical model `claude-opus-5` used zero web/tool requests, found no blocker to revised live application validation, and returned the exact verdict `PASS` on 2026-08-24. No camera, microphone, call content, transcript content, contact name, recording, or window title was included. The subsequent live WhatsApp digital-silence failure and approved endpoint fallback invalidate this as the current pre-manual gate; Gate D requires a fresh exact `PASS`.
- The ninth F03-scoped, tool-disabled Claude Opus review received the complete Gate D endpoint-fallback feature/direct-integration bundle, including explicit complete-record/index revalidation, atomic two-stream opening, endpoint-scope disclosure, WhatsApp-over-Chrome priority, visual-loss continuity, explicit reselection, `ConversationTurn`, Tk heartbeat, no-usable-pair behavior, privacy/offline/bounds, the WGC target-close correction, current tests, plans, provenance, and aggregate evidence. It had no tools, received no live call/transcript/contact/window content, and returned the exact verdict `PASS` on 2026-08-25. Gate D is cleared for the planned manual application validation; the separate post-manual exact `PASS` remains required before commit/push.
- The resumed WhatsApp validation confirmed both physical sources, overlapping speech, and per-utterance English/Hebrew switching in Auto mode. The user judged transcription functional but slightly improvable; the scripted accuracy count is still pending, so this is not the final accuracy pass. The session also exposed two UI gaps: an empty face area obscured live transcription visibility after video/face loss, and a clean Stop rebuilt enumeration and blanked both choices. No call content was recorded. The approved corrections collapse the empty thumbnail and retain the same session-scoped catalog/choices across only a clean Stop; faults, Refresh, and in-process rebuilds still clear both. App restart never restores prior selections, though its fresh initial enumeration may suggest current defaults. This material UI/lifecycle change invalidates the ninth PASS until a fresh F03/direct-integration review returns exact `PASS`.
- Post-correction checks pass: focused audio 41/41, full suite 75/75, compilation/dependencies/diff clean, F01 500 turns/two speakers, F02 replay 6 signals/478 landmarks/52 blendshapes, WGC target-close 101 ms with 0/0 workers/frames, and F03 replay 4/4 schedules/12 turns with 0.006-second maximum timestamp error, zero silence/network/artifacts. The fresh 10.3-second concurrent smoke measured 1.121-second single-source p95, 2.467-second overlap p95/maximum, queue 1/0, zero saturation, F02 24.35 signals/second, and 0/0 workers/results.
- The tenth F03-scoped, tool-disabled Claude Opus 5 review received the complete current F03/direct-integration bundle, with particular attention to blank-thumbnail collapse, same-context clean-Stop selector retention, fault/Refresh/rebuild clearing, explicit revalidation/reselection, `ConversationTurn`, Tk heartbeat, no-usable-pair behavior, endpoint warnings/priority, privacy/bounds, and WGC teardown. It received no live call/transcript/contact/window content, used zero tools/web requests, found no blocking scoped defect, and returned the exact final verdict `PASS` on 2026-08-25. The remaining manual validation may resume; a separate post-manual exact `PASS` is still required before commit/push.
- The user then narrowed Auto to English/Hebrew only. Production now chooses the larger `en`/`he` model probability for each finalized utterance before explicitly transcribing in that language; even when a fake model ranks French highest, the focused check selects the stronger approved language. Focused audio passes 42/42 and the full suite 76/76; replay remains 0%/0% fixed WER, 1.00/0.90 keyword recall, 4/4 schedules, 12 turns, 0.006-second timestamp error, and zero silence/network/artifacts. The fresh 10.3-second concurrent smoke passes at 1.127-second single-source p95, 2.475-second overlap p95/maximum, queue 1/0, zero saturation, F02 24.40 signals/second, and 0/0 workers/results. This behavior change invalidates the tenth PASS until another F03/direct-integration review returns exact `PASS`.
- The eleventh F03-scoped, tool-disabled Claude Opus 5 review checked the constrained Auto implementation and its direct integration surface. It verified per-finalized-utterance detection, filtering to exactly `en`/`he`, explicit fixed-language transcription, no translation/unrestricted fallback, visible fail-closed detection errors, fixed-mode behavior, final-only/order/attribution, local privacy, and current performance evidence. It used zero tools/web requests, received no live content, found no scoped blocker, and returned the exact final verdict `PASS` on 2026-08-25. Manual validation may resume. Its non-blocking long-duration recommendation is already covered by the required pre-final 600-second reruns before the post-manual gate/commit.
- The reviewed WhatsApp retest then confirmed that the finalized transcript and live transcription view remain usable when the selected face/video is unavailable, and that constrained Auto correctly handles English and Hebrew. This is aggregate pass evidence only; no transcript, call content, contact name, recording, screenshot, or window title was retained. Clean-Stop selection retention versus Refresh clearing and the remaining scripted teardown checks are still pending.
- The user confirmed that the prior consenting WhatsApp session also passed every remaining scripted check: ten seconds of silence produced no turn; speech longer than 15 seconds finalized; both physical sources, overlap, roles/order, and no acoustic duplicate worked; clean Stop retained both selectors; explicit restart worked without reselection; Refresh cleared both choices; and normal close completed. Together with the reviewed retest above, mandatory WhatsApp validation passes. The user characterized real-call transcription as working with minor possible accuracy improvement and accepted the tested behavior. Evidence remains aggregate and content-free. Zoom and Google Meet still require real validation or explicit `WAIVED — not passed` decisions.
- Two clean post-Auto 600.0-second concurrent benchmarks passed. Each completed 156 turns across 13 replays with queue peak/final 1/0, zero saturation, negative post-warm-up memory growth, and 0/0 final workers/results. Run 1 measured 1.152-second single-source p95, 2.479/2.508-second overlap p95/maximum, F02 24.99 signals/second with 13.3 ms frame-age p95, and working set 306.6/873.2 MiB. Run 2 measured 1.143-second single-source p95, 2.478/2.605-second overlap p95/maximum, F02 25.00 signals/second with 12.7 ms frame-age p95, and working set 307.0/871.7 MiB. These satisfy the constrained-Auto long-duration, bounds, concurrency, and teardown gates.
- The user explicitly waived both remaining live application checks on 2026-08-25. Zoom is `WAIVED — not passed`; Google Meet is `WAIVED — not passed`. These waivers complete the planned validation decisions but are not success evidence and leave application/layout/title/audio-routing risks for later retesting. No Zoom or Meet call was opened for F03.
- The final post-manual regression matrix passed before review: focused audio 42/42, full suite 76/76, compilation/dependencies/diff clean, F01 500 turns/two speakers, F02 replay 6 signals/478 landmarks/52 blendshapes, constrained-Auto F03 replay 4/4 schedules/12 turns with 0.006-second maximum timestamp error and zero silence/network/artifacts, and native WGC invalidation/resize/target-close with 106 ms teardown and 0/0 workers/frames. The two clean 600-second results above remain the current concurrent performance evidence because no production code changed afterward.
- The final post-manual F03-scoped, tool-disabled Claude Opus 5 review received the complete current feature/direct-integration bundle, current diff/status, content-free WhatsApp evidence, explicit Zoom/Meet waivers, replay/performance/teardown evidence, plans, tests, dependencies, and provenance. It verified capture identity/lifetime, atomic two-sided start/faults, endpoint disclosure/priority, turn order/bounds/Tk lifecycle, visual-loss continuity, constrained English/Hebrew Auto, privacy/offline behavior, WGC teardown, and waiver honesty. It received no live content, used zero tools/web requests, found no blocking scoped defect, and returned the exact final verdict `PASS` on 2026-08-25.
- One non-blocking reviewer note was accepted before commit: an internal five-second worker-join timeout already set a fault, but the Tk completion branch could re-enable audio before the late reaper closed the retained catalog. The corrected shared shutdown path immediately marks reselection required and closes the catalog; both explicit-Stop and fault-initiated Tk paths discard it, clear both choices, show persistent `restart the app` guidance, and prevent audio restart. A focused synthetic stuck-worker check locks the shared session behavior. Focused audio passes 43/43, the full suite 77/77, compilation/diff checks pass, constrained-Auto replay remains 4/4 with zero silence/network/artifacts, and a fresh 10.3-second concurrent smoke passes at 1.185-second single-source p95, 2.490-second overlap p95/maximum, queue 1/0, zero saturation, F02 24.40 signals/second, and 0/0 workers/results. This code correction invalidates the immediately prior final PASS until one fresh scoped review returns exact `PASS`.
- The fresh final correction-only, tool-disabled Claude Opus 5 review verified the session timeout state/order, idempotent catalog termination, late-reaper safety, explicit-Stop and fault-initiated Tk convergence, persistent audio lockout with approved video-only fallback, clean-Stop preservation, and restart/default documentation. It received no live content, used zero tools/web requests, found no scoped blocker, and returned the exact final verdict `PASS` on 2026-08-25. This is the reviewed result authorized for commit/push.

### Slices 9–11 — manual call validation

- Validate WhatsApp, Zoom, and Google Meet independently using consenting scripted test calls and the approved audio routing.
- Record app/version, device roles, duration, aggregate pass/fail counts, and teardown result only. Do not record/save audio or quote transcript content.
- Confirm that losing the face/video leaves the finalized transcript and both live audio states visible, and that a clean Stop/Start retains the explicit choices while Refresh or any device fault clears them.
- A user waiver is recorded as `WAIVED — not passed`; it is never described as successful validation.

### Slice 12 — post-manual Claude Opus review, corrections, commit, push, and Trello closure

- After manual evidence is recorded, review only the approved F03 plan, complete F03 feature/direct-integration diff, changed F03 tests, deterministic fixture provenance, F03 automated output, manual evidence, `git diff`, and status again. Do not expand this feature gate into a whole-project review.
- Require a second exact final verdict `PASS`; the pre-manual verdict cannot substitute for this final gate.
- The prompt specifically asks for accidental audio persistence/egress, speaker crossover, timestamp/reorder errors, unbounded buffers, callback blocking, Tk access, device invalidation/default switching, silence hallucination, model-download behavior, shutdown races, and F02 regressions.
- Resolve every accepted Claude finding; rejected findings receive a concrete rationale.
- Rerun focused checks, full `pytest`, all F01/F02 checks, F03 replay/privacy/offline checks, and the concurrent benchmark.
- Rerun the applicable Claude gate after material corrections until its final verdict is `PASS`.
- Update this plan with final evidence and known limitations.
- Commit the reviewed result on `main`, push to `origin/main`, fetch, and prove local `main`, `origin/main`, and GitHub resolve to the same commit with a clean status.
- Complete implementation/validation/review cards only when their evidence is present. Complete the roadmap F03 card only after the reviewed commit is pushed and every non-waived requirement passes; waived apps remain explicitly labeled as waivers.

## Automated replay and integration checks

The intended check surface extends existing project patterns without a new test framework:

- `pytest`: fast unit coverage with fake endpoints/audio/model for every state and failure branch.
- `python -m conversation_copilot --check-audio`: committed speech fixtures through the cached pinned model and the production PyAV/segmenter/orderer pipeline; networking is denied and only aggregate, content-free metrics are printed.
- `python -m conversation_copilot --benchmark-audio --seconds 600`: production two-source replay plus the existing F02 loop, aggregate latency/throughput/memory/queue/teardown metrics only.
- Existing `--check`, `--check-video`, and `--check-video-capture` remain required and unchanged in meaning.

The replay corpus contains separate microphone and loopback WAV inputs plus a schedule manifest with start times, silence, alternating speech, overlapping speech, a forced split below the 15-second ceiling, and exact reference text. The capture-device binding is covered by focused fakes and the real-device spike/manual tests; automated CI never needs a live call or physical microphone.

## Acceptance thresholds

All thresholds must pass twice on clean runs on the verified development machine unless stated otherwise.

### Functional, ordering, and accuracy

- 100% of replay turns have the role dictated by their physical source; no inferred role and no cross-source mixing.
- 100% of replay turns are ordered by first voiced capture time with stable sequence tie-breaking, including overlap and out-of-order inference completion.
- A changed/missing selected microphone or render/loopback record before Start opens zero streams and requires reselection; an active default-device change causes zero stream switches; no device index is persisted across a new enumeration context or app restart.
- A clean Stop reaches zero streams/workers while keeping the original live catalog and both selector values for the next explicit Start. Refresh, enumeration change, either-source fault, shutdown failure, and app close terminate that catalog; every in-process rebuild starts with both choices cleared. A later app launch uses a fresh context and may suggest only that context's current defaults, never prior records/indices.
- The exact selected microphone and loopback indices are opened explicitly. Endpoint-wide scope is visibly disclosed; Chrome and other non-call audio remain closed/silent during WhatsApp/Zoom validation, and only the Meet call is audible in Chrome during Meet validation.
- An eligible WhatsApp call removes Chrome/Meet from selection. If it appears during active Meet capture, both sides stop and require reselection; an idle WhatsApp main window does not block Meet.
- `ConversationTurn.timestamp` differs from the manifest’s first voiced sample by no more than one capture block plus 20 ms.
- Five minutes of digital silence on either source yields zero turns and zero non-silence text.
- Quiet synthetic English normalized WER is at most 15%, with at least 90% exact recall of the separate non-private keyword/number list.
- Production explicitly transcribes English (`en`). Hebrew and Auto cannot be selected; their retained fixtures remain offline regression and fixed-language benchmark inputs, not evidence of product support.
- The manual scripted call for each non-waived app has at least 90% materially correct utterances per source and zero role swaps. Evidence records counts, not content.
- No partial turn enters application state. Empty or failed inference produces a visible status/error and no fabricated turn.

### Latency and performance

- Single-source speech-end-to-final-turn p95 is at most 3.0 seconds.
- Across the overlapping two-source replay, speech-end-to-final-turn p95 and maximum are each at most 5.0 seconds; the completed-utterance queue returns to zero within 10 seconds after speech stops.
- Chosen local inference real-time factor is at most 0.60 per source on the representative corpus.
- While F03 inference runs, F02 still emits at least 10 video observations/second, keeps its one-frame slot bound, and shows no frozen stale frame.
- Tk heartbeat maximum gap is at most 250 ms during capture/inference and the Stop action acknowledges within 250 ms.
- Ten-minute replay/live dual-stream capture has zero callback overflow or silent drop, and every observed queue/buffer stays at or below its declared cap.

### Memory, privacy, and teardown

- Raw audio resident in F03 never exceeds 12 MiB and no raw job exceeds 30 seconds of age.
- After model warm-up, 10-minute process working-set growth is at most 100 MiB; total F03 working-set increase over the measured F02 baseline is at most 3.0 GiB.
- Stop, microphone/playback fault, and model fault each reach zero F03 streams, callbacks, workers, queued jobs, reorder entries, and raw buffers within five seconds. Visual-target loss or close releases F02 resources while a healthy F03 session continues; the later explicit Stop/close reaches zero F03 resources within five seconds.
- Ten start/stop cycles succeed and the selected devices can be reopened after every stop.
- Filesystem snapshots find zero live-audio artifacts. Logs and Trello/Git evidence contain zero transcripts or call content.
- With the model pre-provisioned and networking denied, the complete local replay and ordinary session start/stop pass with zero connection attempts.

Failing any threshold means the related Trello card remains open. Accuracy/latency failure follows Gate B; it does not silently lower the threshold or enable cloud.

## Manual application validation

Use a consenting second participant or a second controlled account, a non-private script, and the user's actual microphone and speakers. Never record the call. Headphones are optional, not required. For each application:

1. start F02+F03 and verify both source indicators;
2. use at least ten short English utterances, including simultaneous speech, 10 seconds of silence, one utterance longer than 15 seconds, and numbers/names from the non-private test list;
3. verify speaker playback does not reappear as a duplicate microphone/`user` turn, then verify each side’s displayed role, chronological order, and final-only behavior;
4. confirm the endpoint-wide warning is visible and follow it: close or silence Chrome and other non-call audio for WhatsApp/Zoom; for Meet, keep every other Chrome tab/application silent. Do not claim software exclusion of unrelated audio;
5. remove/disable the camera or otherwise lose the selected visual target while the call continues, confirm facial signals stop without stopping either audio side or finalized transcription, confirm the empty face area collapses so the prior transcript and both audio states remain visible, and confirm no replacement video window is selected silently;
6. stop during speech once, restart with the same retained microphone/playback choices, complete a normal stop, explicitly Refresh once to confirm both choices clear, reselect, and close the app once;
7. record only aggregate metrics and pass/fail behavior.

**WhatsApp:** mandatory before F03 completion.
**Zoom:** validate or record a user waiver as `WAIVED — not passed`.
**Google Meet:** validate or record a user waiver as `WAIVED — not passed`.

## Risks and limitations

- **Endpoint-wide playback scope:** every sound routed to the selected playback endpoint can be labeled as the contact. Mitigation: the selector displays the limitation; close or silence Chrome and every non-call audio app during WhatsApp/Zoom, and keep every other tab/application silent during Meet.
- **Speaker leakage:** loudspeakers can feed loopback speech into the microphone, creating duplicate/wrong-role turns. The user's current setup is expected not to leak and will be tested as-is. If it fails, tune microphone gain/routing and retest; headphones are optional. Echo cancellation requires an explicit plan revision rather than silent scope expansion.
- **Browser audio sharing:** Google Meet requires Chrome, but endpoint loopback cannot isolate the Meet tab. Use a dedicated Meet window and keep all other Chrome tabs silent.
- **Microphone device churn:** PortAudio indices are transient and can change whenever enumeration is rebuilt. Mitigation: keep microphone selection and Start in one context, revalidate the complete record, never persist/reuse an index, fail closed, clear buffers, and require reselection; never switch automatically.
- **Selection convenience boundary:** clean Stop/Start may reuse the still-live enumeration context and its exact selected records. This is session-only convenience, not persistence; Refresh, fault, or in-process rebuild clears both selectors rather than matching names or reusing indices. A new app process may preselect its newly enumerated current defaults but never restores the previous process's choices.
- **Process isolation unavailable for live WhatsApp:** the Windows process-loopback experiment returned digital silence for the active WhatsApp render session and was removed. Revisit only if Windows/WhatsApp behavior changes and a new approved spike passes the real call before integration.
- **Overlapping speech:** one GPU model worker serializes simultaneous finalized utterances. The measured overlap gate passed with a bounded queue; add another bounded worker only after a measured regression and an approved plan change.
- **Hebrew/code-switching:** unsupported. Real-recording tests found no sufficiently accurate free local Hebrew model; the best candidate produced 22.2% word error. Clean synthetic Hebrew/Auto passes were not representative enough. Re-enable only after a future free model passes a new real-speech comparison.
- **Model provisioning:** offline runtime works only after the pinned model is installed. Missing model state is reported before a call.
- **GPU deployment:** the retained Windows configuration depends on the pinned NVIDIA cuBLAS/cuDNN wheels and a compatible NVIDIA driver. The model and wheel payloads increase installation size; there is intentionally no silent CPU fallback.
- **Cloud privacy/cost:** any cloud replacement sends call audio off-device, needs internet, changes the privacy posture, and requires explicit approval plus updated documentation.
- **Synthetic accuracy:** clean generated speech is deterministic but easier than real calls. It complements rather than replaces mandatory WhatsApp and non-waived app validation.
- **Audio can outlive the selected window:** visual-target loss cannot prove that the underlying call ended. While both explicitly opened audio sides remain healthy, F03 continues endpoint-bound transcription with a visible status until the user presses Stop or closes the app; it never binds a replacement window or audio device silently.

## Trello card map

The permanent **F03 — Two-sided audio and transcription** list contains these open cards, one per plan slice:

1. Planning — Approve F03 feature plan
2. Spike 1 — Windows microphone and WASAPI loopback binding
3. Spike 2 — Local transcription, language, accuracy, and latency gate
4. Implementation 1 — Audio device selection and two-source capture
5. Implementation 2 — Segmentation, local transcription, and ordered turns
6. Implementation 3 — Tk/F02 integration, bounded runtime, and user states
7. Validation 1 — Deterministic replay, privacy, and offline operation
8. Validation 2 — Performance, resilience, memory, and teardown
9. Review — Claude Opus pre-manual and post-manual QA/code reviews return PASS
10. Validation 3 — Manual WhatsApp call
11. Validation 4 — Manual Zoom call or recorded waiver
12. Validation 5 — Manual Google Meet call or recorded waiver
13. Corrections — Resolve findings, rerun, commit, push, and close F03

No implementation or validation card is complete at planning time.

## Approval record

The user approved the plan on 2026-08-19 with these answers:

1. **Endpoint-wide audio scope — approved 2026-08-19, temporarily superseded 2026-08-24, reinstated 2026-08-25.** The implementation treats every sound routed to the selected playback endpoint as `selected_contact`. After the process-isolation attempt failed live WhatsApp, the user approved returning to this working behavior with the explicit rule to close/silence Chrome and other non-call audio.
2. **Headphones requirement — rejected and revised.** Headphones are not required. Test the user's microphone and speakers as-is and keep them when the zero-role-crossover gate passes. Adapt device gain/routing based on measured behavior if necessary.
3. **Languages — superseded 2026-08-25.** The original English/Hebrew/Auto approval is replaced by English-only support after no tested free local Hebrew model met the required accuracy. There is still no translation.
4. **Transcript behavior — approved.** Show source status and finalized `ConversationTurn` objects only; do not add unstable partial captions.
5. **Application validation — validation planned.** WhatsApp, Zoom, and Google Meet are currently scheduled for manual validation. The user may decide at the validation stage whether to test or explicitly waive Zoom and/or Meet; no waiver is granted now, and any later waiver is recorded as `WAIVED — not passed`.
6. **Gate A v2 device identity — approved.** Session-scoped PyAudioWPatch indices may replace stable Windows endpoint IDs because F03 persists no device choice. Selection must be revalidated and opened explicitly in one enumeration context; any mismatch, default change, disconnect, or rebuilt enumeration fails closed and requires reselection. Native WASAPI remains an unapproved contingency if this behavioral gate fails.
7. **Two Claude review gates — approved.** An exact `PASS` is required before requesting manual WhatsApp/Zoom/Meet testing, and a second exact `PASS` is required after manual evidence is recorded. This ordering is the standard for F03 and future manual validation work unless a later approved plan explicitly changes it.
8. **Claude review scope — approved.** Each feature gate reviews only the new feature and its direct integration surface. Whole-project Claude review is performed later at the dedicated project-wide gate, not repeated inside every feature gate.
9. **Visual-loss audio continuity — approved 2026-08-22.** If camera/selected-window capture is lost while the call and both explicit audio streams remain healthy, facial signals stop but transcription continues until explicit Stop/close. Video never switches silently. This material change invalidated the earlier pre-manual PASS; the required fresh F03-only pre-manual Claude review subsequently returned exact `PASS` before live validation resumed.
10. **Process-isolated call playback and source priority — approved 2026-08-24, capture portion retired 2026-08-25.** Native Windows process loopback passed synthetic applications but returned digital silence for the audible live WhatsApp render session and every related PID, including one final Microsoft-sample-style correction. The helper/source/binary were removed. WhatsApp-over-Chrome call-window selection/runtime priority remains retained because it is independent of the failed audio binding.
11. **One final fix, then endpoint fallback — approved 2026-08-25.** The user authorized one more root-cause process-loopback correction and, on failure, explicitly chose the previously working playback-endpoint implementation with a no-Chrome/no-other-audio operating rule during WhatsApp. The final correction failed with `peak 1`, RMS `0.479`; Gate D is therefore the current approved production path and requires a fresh pre-manual Claude `PASS` before retest.
12. **Live visibility and clean-stop selection retention — approved 2026-08-25.** When face/video output is unavailable, collapse the empty thumbnail so the prior finalized transcript and live audio state remain visible. Preserve the selected microphone/playback only across a clean Stop/Start using the same live enumeration context. Refresh, device/enumeration fault, shutdown failure, and in-process rebuild clear both and require explicit reselection. App restart restores no prior choice/index, though the new initial enumeration may suggest current Windows defaults; no PortAudio index is persisted or remapped by name.
13. **Auto language scope — retired 2026-08-25.** The constrained English/Hebrew Auto implementation passed synthetic checks but was removed from the product after representative Hebrew testing failed the accuracy requirement. Production passes English explicitly; legacy Auto helpers and Hebrew fixtures remain unreachable from the production UI for historical regression and fixed-language benchmark use only.
14. **Zoom and Google Meet validation — waived 2026-08-25.** The user chose to waive both remaining F03 live-call checks for now. Each is recorded as `WAIVED — not passed`, not as successful validation; WhatsApp remains the only passed live application gate.
15. **English model revision — accepted with Claude-limit exception 2026-08-25.** The user accepted the real-call result as very good despite a couple of transcription errors. Opus had reviewed only the staged transcription revision and its ninth-round findings were corrected; the corrected rerun could not start because the Claude account hit its session limit on both Opus and Sonnet. The user approved completion without waiting for that account reset. This exception applies only to the post-completion English model revision and does not change future review gates.

The original approval did not pre-approve CUDA installation or OpenAI audio egress. After the local CPU candidate failed its repeated latency gate, the user separately approved the pinned CUDA/cuDNN wheel runtime used here. OpenAI audio egress remains unapproved.
