# F02 — WhatsApp/Zoom/Chrome Meet window capture and facial signals

**Target:** 2026-08-23
**Status:** Complete — 2026-08-19
**Implementation gate:** Original plan, failed replacement, and the two-candidate recovery spike were approved by the user on 2026-08-14. Chrome-hosted Google Meet scope was approved on 2026-08-17.

## Goal

Build the smallest Windows visual-input slice for an Assisted Call. The user chooses one visible WhatsApp Desktop, Zoom, or dedicated Google Chrome window with an active Google Meet call, confirms which visible face is the remote participant, and sees that face followed while local MediaPipe processing produces current landmarks and blendshapes.

F02 produces observable Facial Signals only. It does not infer emotion, tone, intent, identity, or social meaning.

## User-visible result

Running `python -m conversation_copilot` retains the F01 foundation behavior and adds a minimal capture view that:

1. lists visible, non-minimized WhatsApp Desktop and Zoom windows plus dedicated Chrome windows whose active tab is Google Meet, and can refresh the list;
2. starts memory-only capture for the chosen window;
3. initially selects the largest detected face as the Remote Face Region;
4. shows a small thumbnail of that selected face and a **Switch face** control; after six seconds without the selected face, the same control becomes **Continue tracking** so recovery is explicit rather than a silent reselection;
5. shows the selected window name, `Tracking` or `Face lost`, achieved Facial Signal rate, and whether the current selected face produced 478 landmarks and 52 blendshapes; and
6. stops cleanly and returns to selection when the call window closes; for Chrome, it also stops if the active tab stops identifying itself as Google Meet.

**Switch face** assigns only a temporary role in the current Assisted Call: analyze this face and ignore the others. It does not name, recognize, or remember anyone.

No emotion label, interpretation, landmark dashboard, transcript, audio control, memory, or polished interface is added.

## Verified starting facts

- F01 is complete and healthy on the development computer: Python 3.12.10, `18 passed`, and `python -m conversation_copilot --check` reports 500 Conversation Turns from two speakers.
- The current application is a thin Tkinter shell with Pydantic models and no capture, media, persistence, network, or async framework.
- The development machine runs 64-bit Windows build 26200 and has an NVIDIA RTX 4060 Ti. CPU remains the required inference path.
- Installed validation targets are WhatsApp Desktop `2.2631.102.0`, Zoom Workplace `7.0.6 (43848)`, and Google Chrome `151.0.7922.110` running Google Meet.
- No .NET SDK is installed. F02 will not introduce C#, Rust, WinUI, browser automation, an extension, DevTools/DOM inspection, or a second desktop application unless this plan is revised after the Python capture spike fails. Chrome is only another explicitly selected top-level window source.

## Technology decisions

### Window discovery and selection

Use Python `ctypes` and native Win32 calls already present in Windows:

- `EnumWindows` for top-level windows;
- `IsWindowVisible`, `IsIconic`, and `DwmGetWindowAttribute(DWMWA_CLOAKED)` to exclude hidden, minimized, and cloaked windows;
- `GetWindowTextW`, `GetClassNameW`, and `GetWindowThreadProcessId` for display and capture targeting; and
- `QueryFullProcessImageNameW` to admit only the installed WhatsApp, Zoom, and Google Chrome executables.

For WhatsApp, require the full process path basename `WhatsApp.exe` or `WhatsApp.Root.exe` and the exact active call title `Video call`. Live WhatsApp Desktop `2.2631.102.0` uses `WhatsApp.Root.exe`; the ordinary same-process window titled `WhatsApp` must remain excluded.

The user chooses from this filtered list. A Chrome window is eligible only when its active-window title contains the provisional `Google Meet` marker. The planned real-call marker confirmation was user-waived on 2026-08-19, so version/localization reliability remains an explicit residual risk. The user must open Meet in a dedicated Chrome window; other tabs and generic Chrome windows are unsupported. Revalidate the exact HWND, Chrome process path, visibility state, and Meet title on every captured-frame callback before copying pixels. At the first ineligible callback, drop that frame, clear the pending raw-frame slot, stop the session, and show `Google Meet tab no longer active — reselect`; never follow another Chrome window or tab automatically.

WGC captures the whole Chrome top-level window, including its visible browser chrome, not a browser tab or DOM element. Do not add `pywin32`, a generic window-management layer, browser automation/extension/remote debugging, automatic background targeting, or title-only contact inference.

### Native window capture: short pass/fail spike

Use `Windows.Graphics.Capture` (WGC), the Windows API designed to capture an application window through a `GraphicsCaptureItem`. WGC is supported from Windows 10 1803; direct desktop-window targeting through `IGraphicsCaptureItemInterop::CreateForWindow` is supported from Windows 10 1903. F02 therefore supports Windows 10 1903 or later and must call `GraphicsCaptureSession.IsSupported()` or the selected binding's equivalent before offering capture.

The approved recovery spike compares exactly two candidates and retains the first one that passes every gate:

1. **OpenCV-optional `windows-capture==2.0.1` build.** Apply the smallest auditable patch to the pinned MIT source: remove the mandatory `opencv-python` dependency and make its unused image-save import lazy. Preserve exact-HWND capture, the upstream native extension, license, and source hash. Build a pinned local wheel; Rust is build-time only and must not become a runtime or clean-install requirement.
2. **Official PyWinRT plus stdlib `ctypes`.** Use pinned official WinRT projection wheels and native Windows APIs only. It passes only if Python can create a `GraphicsCaptureItem` for the selected HWND and obtain bounded, memory-only BGRA bytes with prompt teardown without adding a compiled helper, .NET, Rust component, generic COM framework, or second capture library.

Evaluate each in a separate clean environment with `mediapipe==1.0.0`. Reject duplicate OpenCV distributions, broken `pip check`, an unbounded queue, unclear native-buffer ownership, writer/encoder use, or any runtime toolchain. Application code must never call an image/video save helper.

The binding normally passes only if one implementation slice proves all of the following on the development computer. The user-approved 2026-08-19 validation exception later in this plan replaces the real Zoom and Meet portions with an explicit waiver and recorded residual risk; it does not convert those unexecuted checks into passes:

1. the exact user-selected eligible HWND is passed to the binding and capture never switches to another matching title/window;
2. real WhatsApp, Zoom, and dedicated Chrome-hosted Google Meet call windows each deliver changing BGRA frames for 60 seconds without writing a file;
3. capture continues while another window fully covers the call window;
4. resizing recreates or recovers the captured dimensions without corruption;
5. minimizing pauses with a clear `Restore the call window` state and restoring resumes, or permits a clean reselect;
6. closing/replacing the target ends capture and returns to selection;
7. capture runs off the Tk main thread, stops promptly, and leaves no capture/background thread; and
8. a normal clean-environment `pip install -e ".[test]"` remains sufficient.

For Chrome, the original spike additionally passed only if the active Meet title marker was reliable for the tested one-to-one call, a non-Meet Chrome window was never offered, switching the selected window to a non-Meet tab stopped capture on the first ineligible frame callback and cleared the pending frame, returning to Meet required an explicit reselect, and no Chrome extension, debugging port, URL/tab API, meeting credential, or DOM access was used. The 2026-08-19 user-approved revision waived that real-call gate and retains the provisional marker with its false-positive risk; it does not broaden capture to all Chrome windows or represent the marker as validated.

Inspect the installed wheel/source during the spike and record the exact WGC path, license, frame-buffer ownership, callback behavior, and teardown behavior. The native callback must copy at most one pending BGRA frame into the application's replaceable latest-frame slot and return immediately; inference must not run inside the native callback. Do not call any image/video save method.

If any criterion fails, remove the candidate and stop the capture slice with evidence. Do not silently add a second capture library, duplicate OpenCV distribution, .NET helper, Rust toolchain, monitor-region fallback, or screen-recording framework. Revise this plan with the user before choosing a larger fallback.

Primary references:

- [Microsoft screen-capture guidance](https://learn.microsoft.com/en-us/windows/apps/develop/media-authoring-processing/screen-capture)
- [`IGraphicsCaptureItemInterop::CreateForWindow`](https://learn.microsoft.com/en-us/windows/win32/api/windows.graphics.capture.interop/nf-windows-graphics-capture-interop-igraphicscaptureiteminterop-createforwindow)
- [Microsoft Win32 capture sample](https://github.com/robmikh/Win32CaptureSample)
- [Google Meet browser requirements](https://support.google.com/meet/answer/7317473)

### Local face location and Facial Signals

Use [`mediapipe==1.0.0`](https://pypi.org/project/mediapipe/1.0.0/) and two official on-device models:

| Purpose | Pinned model | Size | SHA-256 |
|---|---|---:|---|
| Locate all visible faces by bounding box only | [`blaze_face_short_range.tflite`, float16 version 1](https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/1/blaze_face_short_range.tflite) | 229,746 bytes | `b4578f35940bf5a1a655214a1cce5cab13eba73c1297cd78e1a04c2380b0152f` |
| Extract the selected face's signals | [`face_landmarker.task`, float16 version 1](https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task) | 3,758,596 bytes | `64184e229b263107bc2b804c6625db1341ff2bb731874b0bcc2fe6544e0bc9ff` |

Bundle the pinned model files and their provenance/license notice so live and replay paths require no download. Do not add a runtime model downloader.

- MediaPipe Face Detector locates bounding boxes for visible faces. Non-selected faces receive no retained landmarks or blendshapes.
- The largest box is the initial Remote Face Selection.
- **Switch face** changes that current-call role to the next visible box.
- Match later boxes to the selected box by geometric overlap/proximity only. This is region tracking, not identity tracking.
- MediaPipe Face Landmarker runs in synchronous `VIDEO` mode, with monotonically increasing millisecond timestamps, on only the selected crop. It must return 478 3D landmarks and 52 named blendshape scores.
- A single fixed crop margin and inference size may be tuned during the replay/live spike, then recorded as constants. Do not add a settings system for them.
- Preserve a selection through brief misses. After six continuous seconds without a match, stop emitting Facial Signals, show `Face lost`, and require explicit **Continue tracking** or reselection; never silently jump to the largest remaining face.

Use one current `FacialSignal` value containing its timestamp, selected normalized face box, landmarks, and blendshapes. Do not create a generic vision pipeline, backend interface, event bus, repository, or history store.

Primary reference: [MediaPipe Face Landmarker for Python](https://developers.google.com/edge/mediapipe/solutions/vision/face_landmarker/python).

### CPU and GPU decision

CPU is mandatory. Current MediaPipe Python documentation limits its GPU delegate to Ubuntu, and current MediaPipe Windows builds disable the OpenGL GPU path. A Windows GPU attempt is therefore expected to report unsupported, but the user wants the comparison to remain repeatable.

Provide one documented benchmark command:

```powershell
.\.venv\Scripts\python -m conversation_copilot --benchmark-video --seconds 600
```

It runs the same replay through CPU and then attempts GPU automatically. CPU failure fails the command. Unsupported GPU is a reported skip, not an F02 failure. Keep a live GPU option only if it:

1. initializes and completes the same replay on Windows;
2. passes the same structural/tolerance checks as CPU; and
3. improves end-to-end p95 processing time by at least 20%.

If GPU passes, live `auto` may prefer it while preserving automatic CPU fallback. If it fails or is slower, retain CPU only; do not add ONNX Runtime, DirectML, CUDA, or another face model in F02. The benchmark remains the automatic way to retest after a future MediaPipe upgrade.

### Runtime flow and frame lifetime

The direct flow is:

`selected window → WGC BGRA frame → latest-frame slot → face boxes → selected crop → MediaPipe VIDEO result → latest Facial Signal → Tk status/thumbnail`

- Tk owns UI changes on its main thread.
- Background work may use the smallest thread arrangement proven safe by the capture spike. There must be no unbounded queue.
- Capture may own its documented native frame-pool buffers. Application code may own at most one replaceable latest frame and the frame currently being processed.
- A new capture replaces a stale pending frame. Freshness wins over processing every frame.
- Release native capture frames, NumPy views/copies, selected crops, and `mp.Image` references promptly after inference.
- Retain only the latest Facial Signal and non-image counters. No landmark/blendshape history exists in F02.
- Use Tkinter's existing image support for the small thumbnail where practical; do not add a UI/image dependency merely for display.

## Deterministic replay and automated checks

Create two clearly labeled, project-owned synthetic portrait assets with recorded provenance. They are test inputs, not frames saved from an Assisted Call. Compose the replay frames in memory; do not commit or generate a replay video.

Do not download or depend on a YouTube/video-call recording. A remote video adds network availability, copyright/licensing, browser UI, ads, and changing encodes without testing anything F02 needs. The project-owned fixtures provide a stable two-person call layout without using a real person's call footage.

The replay must cover:

1. two visible faces with one initially larger;
2. largest-face initial selection;
3. movement of the selected face across successive frames;
4. a brief miss shorter than six seconds followed by reacquisition;
5. a deterministic **Switch face** action that locks the other face even when it is not the largest; and
6. loss of six seconds or longer that produces `Face lost` without jumping to the remaining face.

Provide a short headless command:

```powershell
.\.venv\Scripts\python -m conversation_copilot --check-video
```

The check uses fixed frames and timestamps, performs no real capture, opens no window, requires no call or network, and exits non-zero unless:

- the expected face boxes are found;
- selection/follow/switch/loss transitions match the fixture manifest;
- selected results contain exactly 478 finite landmarks and 52 finite blendshape scores in `[0, 1]`;
- timestamps are ordered;
- no non-selected Facial Signal is retained; and
- output values meet recorded tolerances rather than requiring bit-identical floating-point results.

Keep the existing `python -m conversation_copilot --check` and all F01 tests unchanged and passing.

Also provide a desktop integration check:

```powershell
.\.venv\Scripts\python -m conversation_copilot --check-video-capture
```

This command launches a uniquely titled, test-only Tkinter **mock call** window, renders the same two synthetic portraits with deterministic movement and loss states, captures that visible window through the retained WGC binding, and closes automatically. It also changes the mock title from eligible to ineligible and proves that the next frame callback is dropped, the pending frame is cleared, and capture stops. Test-only targeting may address that unique HWND/title directly; it must not weaken the production WhatsApp/Zoom/Chrome eligibility rules. The command exits non-zero unless it observes changing BGRA frame checksums, correct dimensions after a resize, at least two face boxes, selected-face landmarks/blendshapes, title-invalidation shutdown, prompt target-close shutdown, zero remaining application-owned frames/workers, and no image/video artifact written to application-controlled paths.

`--check-video` remains the fast headless logic/model check. `--check-video-capture` proves the native capture-to-signals integration without a call. Neither replaces application-specific manual validation. WhatsApp was validated; Zoom and Google Meet-in-Chrome were explicitly waived by the user, so their real window/title replacement, tab switching, minimization, protected-content, and self-preview behavior remain residual risks rather than passed evidence.

## Performance, privacy, and retention checks

The ten-minute benchmark above must measure CPU and any available GPU delegate using the same replay loop and report:

- achieved current Facial Signals per second;
- p50 and p95 end-to-end frame age;
- processed and replaced/stale frame counts;
- p50 and p95 inference time;
- process working set; and
- current retained application-frame count.

The CPU path passes when:

- it sustains at least 10 current Facial Signals per second;
- p95 frame age remains below 500 ms;
- Tk remains responsive to Stop and **Switch face**;
- the application retains no more than one pending raw frame plus the frame being processed;
- after a two-minute warm-up, working-set growth is no more than 2 MiB/min and the final working set is no more than 100 MiB above the post-warm-up baseline; and
- stopping returns all application-owned frame references to zero and terminates worker threads.

Privacy/retention acceptance requires all of the following:

- run replay successfully with networking unavailable;
- production capture/vision code contains no image/video writer, encoder, HTTP client, upload, or external vision call;
- model assets are local and hash-verified;
- no call frame, crop, thumbnail, landmark set, or blendshape set is written to the repository, temp directory, logs, screenshots, cache, or database;
- before/after filesystem checks find no new image/video artifacts in application-controlled paths; and
- diagnostics contain only window/status names, counts, timings, memory, and errors—not pixel or Facial Signal payloads.

MediaPipe states that image processing occurs on-device and frames are not sent to Google; its separate performance/utilization metrics notice must be documented. F02 application code must make no network call and must never send frames or derived Facial Signals externally.

## Implementation slices

1. **Technology spike:** verify the selected WGC binding with Python 3.12/Tk, dependency cleanliness, buffer ownership, and teardown; normally include WhatsApp, Zoom, and Google Meet application behavior. Under the revised gate, retain the binding after the WhatsApp pass and explicit Zoom/Meet waiver while preserving those application-specific items as residual risk.
2. **Models and replay:** add the two pinned MediaPipe models, provenance, synthetic portrait fixtures, in-memory replay generator, smallest Facial Signal value, and `--check-video`.
3. **Window selection and capture:** add the stdlib Win32 eligible-window list, including the narrow Chrome/Meet process-and-title rule and per-frame revalidation, Refresh/start/stop behavior, and memory-only WGC frames without blocking Tk.
4. **Remote-face tracking and correction:** add bounding-box-only multi-face location, largest initial selection, geometric following, six-second loss behavior, selected-face-only landmarks/blendshapes, thumbnail/status, and **Switch face**.
5. **Automated validation:** preserve F01 checks; add the deterministic WGC mock-call check; run replay, offline/privacy checks, `--benchmark-video`, CPU thresholds, GPU attempt, memory plateau, frame-count, and clean shutdown checks.
6. **Manual application validation:** execute and record the WhatsApp checklist without saving call imagery. Record the user-approved Zoom/Meet waiver, substitute smoke evidence, and remaining risks without presenting either waived checklist as passed.
7. **Claude Review Gate:** provide the complete evidence bundle for independent QA/code review and receive a pass/fail verdict with numbered findings.
8. **Corrections and completion:** resolve accepted findings, record justified rejections, rerun every affected check, update this plan/Trello evidence, and close F02 only when every gate passes.

Only F02 implementation slices may be active. Do not begin F03 or refactor F01 beyond the minimum integration required by F02.

## Technology spike record

### Rejected candidate

`windows-cap==0.1.2` **failed** the mandatory binding spike on 2026-08-14 and was removed before any later F02 slice began.

- The CPython 3.12 x64 wheel installed cleanly, declared no runtime dependency, passed `pip check`, and included the MIT license (copyright Akase Cho, 2024).
- The inspected PyPI 0.1.2 source distribution had SHA-256 `2d74a904b848295fc06d4014446e89073952d2c041e6430b0bbdb7a56240b086`.
- Source inspection confirmed the intended native path: `FindWindowW` title/class lookup, `IGraphicsCaptureItemInterop::CreateForWindow`, a free-threaded `Direct3D11CaptureFramePool`, BGRA8 staging-texture copy into a reusable in-memory `Vec<u8>`, explicit per-frame `Close`, and session/frame-pool/device cleanup in `Drop`.
- The binding uses `std::sync::mpsc::channel()` for capture frames. Rust documents this channel as having an infinite buffer, and the frame-arrival callback queues every native `Direct3D11CaptureFrame`. This violates F02's bounded latest-frame rule and can retain arbitrarily many native frames when inference is slower than capture.
- Its only receive API calls blocking `recv()` inside a PyO3 method without releasing the Python GIL. It exposes no stop/close method; cleanup is available only from `Drop`, which cannot promptly unblock a worker waiting in `next()` when a target stops producing frames. The callback also unwraps a failed send after receiver teardown.
- These source-level failures violate the mandatory off-main-thread, prompt-stop, bounded-frame, buffer-lifetime, and teardown criteria. Real WhatsApp/Zoom capture checks were therefore not run: the approved plan requires immediate removal and revision after any mandatory spike failure.

No alternate capture library, helper, framework, screen-region fallback, or toolchain was introduced. F01 remained green before the spike (`18 passed` and the unchanged foundation headless check).

### Rejected replacement candidate

`windows-capture==2.0.1` **failed** its mandatory clean-dependency gate on 2026-08-14 before installation. Its published/source API addresses the first binding's specific blockers with exact-HWND targeting, `start_free_threaded()`, GIL-detached native blocking operations, explicit `stop()`/`wait()`, target-closed notification, BGRA output, and native mapped-frame ownership tied to the Python buffer view.

However, a joint clean-environment resolver check for `windows-capture==2.0.1` and `mediapipe==1.0.0` would install both `opencv-python==5.0.0.93` and `opencv-contrib-python==5.0.0.93`. Both distributions provide the same `cv2` package, creating the duplicate OpenCV installation explicitly forbidden by this revision. Installing with `--no-deps` would make `pip check` fail and is not an acceptable workaround.

No candidate package, MediaPipe package, alternate binding, helper, or implementation code was installed or added. Real/mock capture testing was not reached because the approved plan requires immediate stop on this dependency failure.

### Approved two-candidate recovery spike

On 2026-08-14 the user explicitly approved checking both the minimal OpenCV-optional `windows-capture==2.0.1` build and the official PyWinRT/stdlib route, then using the one that passes. The candidates are evaluated independently; a failed candidate is removed before the other is tried. If neither passes, F02 stops for another plan revision.

### Two-candidate comparison result

The OpenCV-optional `windows-capture` candidate passed the local mock-capture behavior checks but **failed the normal clean-install gate** and is not retained.

- The exact PyPI `windows-capture==2.0.1` source archive had SHA-256 `2c2b394f4587b067cf520456f7f64c11b00380851b077a4d061fe5356a9a7645` and declared the MIT license.
- The minimal patch removed the mandatory `opencv-python` dependency, moved the image-save-only `cv2` import into that unused method, and produced `windows_capture-2.0.1+conversationcopilot.1-cp39-abi3-win_amd64.whl` with SHA-256 `8805fb3e9c5519eb3d9b9dceb7c2d92f120272542f9fba936d2f246232c9601f`.
- In an isolated Python 3.12 environment with `mediapipe==1.0.0`, `pip check` passed and only `opencv-contrib-python==5.0.0.93` supplied `cv2`. Exact-HWND mock capture delivered changing BGRA frames, continued while fully covered, recovered dimensions after resize, paused while minimized, resumed after restore, reported target closure, and stopped in under 32 ms. Source inspection found a one-buffer WGC frame pool and no capture-frame channel.
- A fresh ordinary resolver run could not install `windows-capture==2.0.1+conversationcopilot.1` because that private build is not available from the configured package index. Retaining it would require an extra wheel-install/find-links step or a runtime/build toolchain, so `pip install -e ".[test]"` would not remain sufficient as required.

Official PyWinRT `3.2.1` is the **retained capture binding under the user-approved revised gate**.

- The clean candidate environment uses pinned MIT-licensed PyWinRT runtime, Foundation, Graphics, Capture, Capture.Interop, DirectX, Direct3D11, Direct3D11.Interop, Imaging, and Storage.Streams wheels. With `mediapipe==1.0.0`, `pip check` passed and only `opencv-contrib-python==5.0.0.93` supplied `cv2`; there is no compiler or runtime toolchain.
- The public `winrt.windows.graphics.capture.interop.create_for_window(hwnd)` helper creates the exact `GraphicsCaptureItem`. A stdlib `ctypes` call creates the native BGRA-capable D3D11 device, and the public Direct3D11 interop helper projects it. A one-buffer free-threaded WGC frame pool bounds native frames. `SoftwareBitmap.CreateCopyFromSurfaceAsync` plus a WinRT `Buffer` exposes memory-only BGRA bytes through Python's buffer protocol; application code will replace one latest-frame slot and never invoke a writer or encoder.
- A uniquely titled Tk mock delivered 105 changing BGRA frames across original and resized dimensions, continued changing while fully covered, emitted no frame while minimized, resumed after restore, and shut down without errors. A separate animated target-close run delivered 27 frames, exactly one close event, one callback at a time, and clean teardown after explicit session/frame-pool/device close, reference release, and COM apartment uninitialization.
- No visible WhatsApp, Zoom, or Chrome-hosted Google Meet call window was present at the end of this comparison. At that historical point the original 60-second real-call checks remained open. Implementation later proceeded at the user's direction; WhatsApp passed, and the user waived Zoom/Meet on 2026-08-19 with the residual risks recorded below.

### Implementation and automated evidence — 2026-08-17

The user explicitly directed implementation of the full approved F02 plan and Chrome revision before setting up the real calls. PyWinRT was provisional during automated implementation. It became the retained binding after the real WhatsApp pass and the user's explicit Zoom/Meet validation waiver; no waived live result is inferred from automated work.

- The implementation reuses the exact-HWND PyWinRT WGC route, a one-item replaceable raw-frame slot, Tkinter, and local MediaPipe. Chrome admission requires the full resolved process path to end in `chrome.exe`, a visible/non-minimized/non-cloaked top-level window, and the case-insensitive title marker `Google Meet`. Each frame callback checks eligibility before the native frame copy and again immediately before publishing the copied pixels, closing the title-change race.
- The deterministic replay passed with two detected fixture faces, largest-face initialization, geometric following, user-requested switching, brief reacquisition, six-second loss without silent reselection, and selected-face-only outputs containing 478 finite landmarks and 52 finite blendshapes.
- The final clean-environment native WGC check passed after changing the mock title: invalid callback `84` was dropped, inference ended at callback `83`, the pending slot was empty, two dimensions were observed after resize, and all application workers/frame references reached zero. Target-close fallback stopped in `69 ms`. Development failures remain recorded: the first same-process mock setup blocked because Tk was not pumping while a worker queried its title, so the harness now starts capture while the Tk owner keeps pumping; the WGC close notification alone did not arrive for one destroyed Tk target, so exact-HWND `IsWindow` fallback was added; and a later close/ineligibility classification race was fixed by rechecking HWND existence before choosing the status. Each affected check and the full suite passed afterward.
- A fresh Python 3.12 environment installed with the documented editable command. `pip check` passed; only `opencv-contrib-python==5.0.0.93` supplied `cv2`; the current 32-test suite, F01 `--check`, `--check-video`, `--check-video-capture`, and a short benchmark all passed.
- Offline replay passed with Python socket creation disabled. Asset hashes match `assets/PROVENANCE.md`. Static inspection found no production image/video writer, encoder, network client, upload, database, or payload logging. The native mock's before/after filesystem check found no new image/video artifact.
- The 600-second CPU benchmark passed: `24.54` current signals/s, `12.5 ms` p95 frame age and inference, 18,001 processed/0 replaced, peak/final retained runtime frames `2/0`, working set `111.5/136.5 MiB`, and post-warm-up growth `-5.15 MiB/min`. The automatic Windows GPU attempt reported unsupported and no GPU path is retained.

### Preliminary Claude Opus 5 review — 2026-08-17

A preliminary review was run before live-call validation using canonical model `claude-opus-5` in a tool-disabled, read-only session. The supplied bundle contained the approved plans, complete diff/files, automated and privacy evidence, asset provenance, known limitations, and pending live gates. No Claude tools, web requests, or repository writes were available. This was intentionally not the final gate.

- Verdict: `PRELIMINARY FAIL`. Accepted corrections cover MediaPipe-before-capture construction, idempotent processor teardown including stop-before-start, synchronized WGC callback diagnostics and first-invalid-callback accounting, start failure when capture becomes ineligible before readiness, tracker-state locking without changing tracking decisions, accurate Windows working-set errors, finite benchmark duration, explicit GPU failure diagnostics, equal CPU/GPU duration, and end-to-end frame-age p95 comparison.
- The proposed Meet-title suffix was deferred to the mandatory real-call title spike. The approved requirement says to use the marker confirmed by that spike; guessing a suffix before observing Chrome could reject the real Meet window. Generic Chrome titles containing the provisional text remain an explicit open live-gate item, not a passed criterion.
- The proposed alternate minimize message was rejected because the approved Chrome revision explicitly requires the first callback that fails any eligibility check, including minimized state, to stop and show `Google Meet tab no longer active — reselect`. Restore therefore requires explicit reselection for Meet.
- Private imports and Tk pumping in the deterministic mock were recorded as non-blocking harness coupling. The reviewer’s real-layout, compression, occlusion, protected-content, title-marker, and face-retarget risks were assigned to live application checks rather than speculative code changes. WhatsApp later passed; Zoom/Meet risks remain explicitly accepted under the user's waiver.
- Post-correction evidence: 14 focused tests and 32 full tests pass; F01 replay remains at 500 turns/2 speakers; offline F02 replay passes; and WGC title invalidation drops callback `116`, ends inference at callback `115`, clears all pending frames, observes resize, closes the second target in `134 ms`, and leaves zero workers/frames. The affected 600-second CPU rerun passes at `24.54` signals/s, `12.1 ms` p95 frame age/inference, 18,001 processed/0 replaced, peak/final retained frames `2/0`, working set `110.9/137.8 MiB`, and post-warm-up growth `-5.19 MiB/min`. The isolated GPU attempt now reports its exact unsupported reason: MediaPipe's build flags disable GPU processing.

At that preliminary-review point, the final Claude Review Gate still required the complete post-validation bundle and a separate tool-disabled Claude Opus 5 `PASS`; the two final attempts below satisfy that history.

### Final Claude Opus 5 review attempt 1 — 2026-08-19

Canonical model `claude-opus-5` reviewed the 195,246-byte final bundle in a tool-disabled, read-only session and returned `FAIL` with two blocking findings. Both were accepted: the UI's **Continue tracking** label still called the face-switch action, which could advance to the self-preview in a two-face layout, and deterministic recovery coverage used only one returning face. The correction now gives continue its own tracker/processor/session action, clears the loss lock, and resumes normal geometric matching to the previously selected face. Replay and the focused tracker test restore both faces after loss and prove recovery stays on the previously selected side. The focused suite passes with 9 tests; `--check-video` now emits 6 selected-face signals; native WGC invalidation drops callback 109 after inference 108, closes in 62 ms, and leaves zero workers/frames.

Accepted minor cleanup removed unreachable/unused tracker code, moved full-frame checksum work behind the deterministic mock's explicit check flag, classified a destroyed target as closed inside the ineligible callback path, and closes MediaPipe after stop failures whenever no worker still owns it. The reviewer’s proposed stricter Chrome title rule was rejected: without the waived real-Meet title spike, guessing a suffix could reject the actual call and would contradict the approved provisional substring rule. The acceptance text instead states the exact false-positive risk. A stuck live inference worker cannot be force-closed safely from another thread; it retains ownership and closes the processor in its own `finally`, while the non-daemon thread deliberately prevents a false clean exit. The filesystem check remains scoped to application-controlled paths; static inspection proves production code has no writer or temp-file path. Benchmark evidence is explicitly 800×450 replay input and is not represented as a 1920×1032 live-path benchmark.

### Final Claude Opus 5 review attempt 2 — PASS on 2026-08-19

Canonical model `claude-opus-5` reviewed the complete 198,550-byte correction bundle in a tool-disabled, read-only session and returned `PASS`. It verified that **Continue tracking** is a separate action which clears the loss lock and resumes geometric matching to the existing selected face, and that both focused and end-to-end replay coverage restore two faces while remaining on the previously selected side. Fresh reviewed evidence was 32 passing tests, F01 500 turns/2 speakers, 6 selected-face replay signals with 478 landmarks/52 blendshapes, WGC invalid callback 115 after last inference 114, two resized dimensions, target-close stop in 82 ms, zero workers/frames, clean `pip check`, privacy scan, and `git diff --check`.

The reviewer confirmed the exact-HWND and Chrome pre-copy/pre-publish race handling, bounded frame ownership, selected-face-only processing, Tk thread boundary, cleanup, privacy, dependency use, scope boundary, honest waiver record, and prior 600-second benchmark. Non-blocking residual risks remain: title changes can lag content changes; one post-shrink frame can contain stale same-window padding; eligibility is callback-driven if an ineligible Chrome window stops producing frames; brief misses still label the state `Tracking` while signals are blank; Zoom admission is executable-only and can list a non-call Zoom window; and worst-case synchronous Stop can block Tk for its configured join bounds. These do not replace the waived live Zoom/Meet checks and should be revisited when those checks are eventually run.

## Acceptance checks

- [x] The user explicitly approved the original plan before implementation started.
- [x] The user explicitly approves the `windows-capture==2.0.1` revision before implementation resumes.
- [x] The user explicitly approves the two-candidate recovery spike.
- [x] The user explicitly approves Chrome-hosted Google Meet scope — confirmed on 2026-08-17.
- [x] F01 remains green: 32 total tests pass (the original 18 F01 tests plus 14 F02 tests), plus the unchanged foundation headless summary.
- [x] A clean Python 3.12 environment installs through the documented command with no broken or unused direct dependency.
- [x] WhatsApp exposes only its verified call window, and generic Chrome windows without the provisional `Google Meet` marker are excluded. A non-call page whose title contains that marker can be admitted and remains an explicit user-waived Meet-title risk; Refresh/cancellation are safe.
- [x] Real WhatsApp and a test-only generic Chrome YouTube smoke target deliver memory-only frames through WGC while production continues excluding generic Chrome. Real Zoom/Meet capture was explicitly waived by the user on 2026-08-19.
- [x] Deterministic WGC title invalidation drops the first ineligible callback, clears pending pixels, stops capture, and prevents subsequent inference. The corresponding real Meet tab-change check was explicitly waived and remains a documented residual risk.
- [x] Resize, minimize/restore, target close/replacement, stop, and reselect pass in the real WhatsApp call and deterministic WGC check without freezing Tk or leaking a thread. Zoom/Meet variants remain user-waived risk.
- [x] The largest detected face is selected initially.
- [x] **Switch face** changes only the current Remote Face Selection and never establishes identity or memory.
- [x] Other faces produce location boxes only; only the selected crop produces retained Facial Signals.
- [x] The selected result has exactly 478 finite 3D landmarks and 52 named finite blendshape scores in `[0, 1]`.
- [x] The selected face remains followed through movement and brief misses; a miss of six seconds or longer pauses output instead of selecting another face.
- [x] The UI shows the selected window, thumbnail, tracking/lost state, signal rate, landmark/blendshape availability, explicit `Continue tracking` recovery after loss, and no interpretation.
- [x] `--check-video` passes deterministically without a window, real call, capture device, network, or paid service.
- [x] `--check-video-capture` passes against the local mock-call window through WGC without a real call, network, or retained frame artifact.
- [x] The ten-minute CPU benchmark meets the rate, latency, bounded-frame, memory-plateau, responsiveness, and teardown thresholds.
- [x] The GPU attempt is automatically measured or clearly reported unsupported; it is retained only if it meets the correctness and 20% improvement gate.
- [x] No runtime call frame or Facial Signal is persisted, logged as payload, or sent externally.
- [x] Real one-to-one WhatsApp validation passes; the user explicitly waived real Zoom and Google Meet validation for F02 completion on 2026-08-19 and accepted the recorded residual risks.
- [x] The implementation contains no audio, transcription, interpretation, OpenAI, memory, polished UI, later-feature scaffolding, or unused abstraction/dependency.
- [x] Claude Review Gate passes and all accepted corrections are resolved.

## Manual WhatsApp validation

Using a real one-to-one WhatsApp Desktop video call:

1. Confirm only the visible WhatsApp call window is offered and can be selected.
2. Start capture and confirm changing frames, selected-face thumbnail, `Tracking`, and landmark/blendshape availability.
3. Show both the remote participant and self-preview. Confirm the largest face is initially selected; use **Switch face** if it chose the self-preview and confirm only the corrected remote region remains selected.
4. Move/resize the call window and change the relative self-preview size; confirm the selection follows its region rather than jumping to the currently largest face.
5. Fully cover the call window with another window and confirm WGC continues.
6. Briefly hide the remote face, then hide it for at least six seconds; confirm reacquisition then `Face lost` behavior.
7. Minimize/restore and confirm the stated pause/recovery behavior.
8. End/close the call window and confirm clean stop and return to selection.

**Live result — PASS on 2026-08-19.** WhatsApp Desktop `2.2631.102.0` exposed the real call as the visible, non-minimized, non-cloaked `WhatsApp.Root.exe` top-level window titled `Video call`; the ordinary `WhatsApp.Root.exe` window titled `WhatsApp` was excluded. This corrected the older `WhatsApp.exe`-only discovery assumption at the shared filter and left exactly one selectable call HWND. Exact-HWND WGC showed changing frames, roughly 36–40 signals/s, one safely selected large remote face, 478 landmarks, and 52 blendshapes. The small corner self-preview was below detection size, so **Switch face** correctly had no alternate target and never displaced the large remote portrait. Move/resize, full visual occlusion by another window, brief face loss/reacquisition, minimize/restore with explicit reselect, and end/close with return to selection all behaved as specified. At the user's explicit request, long-loss behavior was revised from two seconds to six seconds: at six seconds `Face lost` clears the thumbnail and blocks silent reselection; after the face returns, the button reads **Continue tracking** and explicit activation resumes tracking. Only these textual results are recorded here; no call imagery or frame payload is included in project evidence.

## Manual Zoom validation

Using a real one-to-one Zoom Workplace video call:

1. Repeat the WhatsApp checks for selection, tracking, correction, occlusion, resize, brief/long loss, minimize/restore, and close.
2. Change between the relevant one-to-one speaker/layout views and verify that a layout replacement either preserves the selected region or safely pauses for correction; it must never silently switch to the self-preview.
3. Confirm no Zoom private API, plugin, meeting credential, or audio permission is used.

**User-waived on 2026-08-19 — not executed and not represented as a pass.** The user accepted the residual risk that Zoom `7.0.6 (43848)` may differ in executable/window admission, DirectComposition behavior, speaker/layout replacement, self-preview geometry, minimize/restore, or close/reselect behavior. No Zoom private API, plugin, meeting credential, or audio code exists in the implementation.

## Manual Google Meet validation

Using a real one-to-one Google Meet call in a dedicated Google Chrome window:

1. Confirm the visible Meet window is offered using its Chrome process path plus the verified Meet title marker; unrelated Chrome windows are not offered.
2. Repeat the WhatsApp checks for capture, selected-face tracking/correction, occlusion, resize, brief/long loss, minimize/restore, and close.
3. Switch the selected Chrome window to a non-Meet tab. Confirm the first callback observed with an ineligible title is dropped, pending pixels are cleared, capture stops with `Google Meet tab no longer active — reselect`, and the non-Meet page does not reach face inference.
4. Return to Meet and confirm capture does not resume until the user explicitly reselects the window.
5. Confirm the app captures only the top-level Chrome window through WGC and uses no Chrome extension, debugging port, URL/tab API, DOM access, Google Meet private API, meeting credential, or audio permission.

Record textual results, application/browser versions, the accepted Meet title marker, timings, and limitations only. Do not save screenshots or call frames as evidence.

**User-waived on 2026-08-19 — real Meet call not executed and no title marker accepted.** The user accepted the residual risks around Chrome `151.0.7922.110` Meet title format, dedicated-window admission, multi-face layout, tab-change timing on a real call, minimize/restore, and close/reselect. A substitute smoke check verified only the shared visual path: a YouTube tab in a visible `C:\Program Files\Google\Chrome\Application\chrome.exe` top-level window was visually observed with a face, then a test-only eligibility override captured that exact HWND in memory for six seconds. It processed `161` frames, detected one face, produced 478 landmarks and 52 blendshapes, and ended with zero workers/frames. Production admission simultaneously returned `production_generic_chrome_offered=0`, so the smoke test did not weaken or bypass the Meet-only filter in shipped behavior.

A second YouTube smoke on 2026-08-19 visually showed four large portrait tiles. Exact-HWND WGC delivered full 1920×1032 frames and ended with zero workers/frames, while the production full-window detector reported zero faces; memory-only diagnostic quadrant crops of the same frame detected three of the four portraits. This isolates a detector-scale/layout ceiling rather than a capture failure: grid faces at roughly this size are below the retained full-window detector's practical threshold. The deterministic replay still proves multi-face selection and **Switch face**, but this smoke does not prove live Chrome gallery behavior. Per the approved scope, no region capture, alternate detector/model, or browser-specific path was added. The supported live case remains a sufficiently large remote portrait, and real Meet behavior remains unvalidated.

## Risks and controls

- **Capture binding is small and alpha:** gate it on real applications, source inspection, unique target mapping, ten-minute stability, clean installation, and teardown. Fail and revise rather than layering fallbacks.
- **Closed or reused HWND:** bind only the explicitly selected eligible HWND, verify its process/window state before start, and stop on target closure; never fall back to a title match or silently capture a replacement window.
- **Chrome is a browser window, not a tab target:** WGC captures all visible content in the selected Chrome top-level window. Require a dedicated Meet window, reject generic Chrome titles, revalidate eligibility before every frame copy, and stop/clear on tab-title change. Document that visible browser chrome and notifications may be present in the in-memory frame.
- **Meet title-marker churn/localization:** the current Chrome/Meet title may change across versions, accounts, languages, or call states. Record the tested marker and fail/revise if it is not reliable; do not broaden to all Chrome windows or add browser automation.
- **WGC limitations:** protected/excluded content can be blank, minimized windows may stop updating, and a call app may replace its window. Report, pause, and reselect; do not bypass platform protection.
- **MediaPipe GPU is probably unavailable on Windows:** CPU is the required path; preserve only the automatic comparison, not an unused GPU architecture.
- **Small/compressed/profile faces:** the four-person Chrome smoke showed a concrete scale ceiling: full-window detection found no grid faces while memory-only diagnostic quadrant crops found three. Require a sufficiently large remote portrait and report `Face lost` rather than emitting stale or guessed data; revisit the detector/model only if a later real-app gate requires smaller gallery tiles.
- **Region matching is not identity:** large layout jumps can break overlap matching. Pause for correction instead of adding facial recognition.
- **Synthetic replay is not a live-call guarantee:** use it for deterministic logic/regression. WhatsApp has live evidence; Zoom/Meet remain waived and must be validated later before treating their application-specific behavior as proven.
- **Tk/thread interaction:** only the Tk thread updates widgets; stop/join behavior is an acceptance gate.
- **Model/package churn:** pin package/model versions and hashes for F02. Upgrade only through the replay and benchmark commands.

## Explicit non-goals

- Audio capture, microphone/system-audio separation, transcription, diarization, or Conversation Turns from calls.
- Emotion recognition, Tone Hypotheses, Social Cues, confidence interpretation, OpenAI analysis, or any external vision service.
- Contact recognition, facial recognition, biometric identity/profile, automatic contact confirmation, or remembering faces.
- Conversation Memory, databases, history, analytics, summaries, guidance, replies, reminders, or follow-up questions.
- Raw-frame recording, screenshots, video encoding, replay recording, cloud storage, or debug frame dumps.
- Group calls, gallery tracking, more than one analyzed Remote Face Region, or hidden/minimized capture guarantees.
- A polished UI, overlay, installer, second desktop framework, native Zoom/WhatsApp integration, or F03 scaffolding.
- Generic browser-window capture, inactive/background Meet tabs, Firefox/Edge/Safari Meet support, browser extensions, DevTools/remote debugging, DOM/tab inspection, or a Google Meet private integration.
- ONNX Runtime, DirectML, CUDA, alternate emotion models, or a generic pluggable vision backend.

## Claude Review Gate

Before F02 can be marked complete, hand an independent Claude Opus 5 reviewer all of the following in a tool-disabled, read-only review session. F02 preliminary reviews and the final required gate must use Opus 5 unless the user explicitly approves another model:

- `PLAN.md`, `CONTEXT.md`, both ADRs, `plans/F01-foundation.md`, and this approved plan;
- the complete F02 diff and list of changed/new files;
- the capture-binding spike record, source/license/dependency findings, and pass/fail evidence;
- clean-environment installation output, `pip check`, full pytest output, F01 headless output, `--check-video` output, and `--check-video-capture` output;
- CPU/GPU benchmark results, frame-age/drop/count results, working-set evidence, and thread/frame teardown evidence;
- privacy/offline/filesystem-retention evidence;
- textual WhatsApp manual-validation results plus the explicit Zoom/Meet waivers, substitute Chrome smoke results, unexecuted Meet title-invalidation status, and residual risks; and
- known limitations and every acceptance-check mapping.

Ask Claude to return `PASS` or `FAIL`, followed by numbered findings with severity, file/line evidence, violated acceptance criterion, and the smallest correction. The review must specifically inspect:

- accidental frame/signal persistence or egress;
- wrong-window and wrong-face selection;
- generic Chrome admission, Meet-title invalidation races, or non-Meet frames reaching inference;
- silent self-preview switching;
- stale-frame queues, native-buffer lifetime, memory/thread leaks, and Tk cross-thread calls;
- dependency duplication, unnecessary abstractions, model provenance/licensing, and unused code; and
- scope leakage into identity, emotion, audio, memory, OpenAI, or later features.

A `FAIL` blocks completion. Claude does not convert the waived Zoom/Meet checks or substitute Chrome smoke into live-call evidence; it must assess whether the revised gate and residual risks are represented honestly.

## Corrections and completion workflow

1. Triage every Claude finding as accepted or rejected with concrete evidence.
2. Apply only accepted F02 corrections; record why any finding is rejected.
3. Rerun the smallest affected check immediately, then the complete F01/F02 automated suite.
4. Repeat performance, retention, or live-app validation when a correction touches that behavior.
5. Send the correction diff and new evidence back to Claude until the verdict is `PASS`.
6. Complete every acceptance checkbox and add concise implementation evidence to this file.
7. Mark each F02 Trello card complete, then mark the F02 roadmap card complete.
8. Set this plan to `Complete`. Do not plan or implement F03 in the same session.

## Approval and completion record

- [x] **Feature plan approved by user** — approved explicitly on 2026-08-14.
- [x] **Replacement capture decision approved by user** — confirmed explicitly on 2026-08-14.
- [x] **Two-candidate recovery spike approved by user** — confirmed explicitly on 2026-08-14.
- [x] **Chrome-hosted Google Meet scope approved by user** — confirmed explicitly on 2026-08-17.
- [x] **Zoom/Meet live validation waiver approved by user** — confirmed explicitly on 2026-08-19; neither waived check is represented as passed.
- [x] **Technology spike passed under the revised gate and one capture binding retained.**
- [x] **F02 acceptance checks passed under the explicitly revised user-approved gate.**
- [x] **Claude Review Gate passed and corrections resolved.**
- [x] **F02 marked complete in this file, its permanent Trello Feature Column, and roadmap card.**

## Copy-ready prompt for a new implementation session

> You are the implementation agent for F02 — WhatsApp/Zoom/Chrome Meet window capture and facial signals. Work only after the user has explicitly approved `plans/F02-video-capture.md`; this prompt is not approval. Before editing, read `PLAN.md`, `CONTEXT.md`, both ADRs, `plans/F01-foundation.md`, the complete approved F02 plan, current code/tests, Git status/history, and the full Trello board. Run the existing F01 checks and confirm they remain green. Use the existing permanent Trello column `F02 — WhatsApp/Zoom window capture and facial signals`, keeping only the current implementation slice active and updating cards with evidence as work completes.
>
> Implement the approved F02 slices in order and no more. Follow Ponytail/full discipline: understand the complete affected flow, reuse current code and Tkinter, prefer stdlib/native Windows features, keep the smallest working diff, add no speculative abstraction or later-feature scaffolding, and leave a focused runnable check for non-trivial logic. Start with the pass/fail WGC binding spike. If it fails, remove the candidate, record evidence, and stop for plan revision; do not silently introduce another capture library, UI/runtime, or toolchain.
>
> Preserve all privacy and scope boundaries: runtime call frames remain in memory only; no frame, crop, thumbnail, landmark, or blendshape payload may be written, logged, uploaded, cached, or sent to an external vision service. Analyze Facial Signals only for the user-selected Remote Face Region. Detection of other faces is bounding-box-only and exists solely for largest-face initialization and **Switch face**. After six seconds without the selected face, enter `Face lost`, clear current output, forbid silent reselection, and require **Continue tracking** for explicit recovery. Google Meet is supported only in a dedicated Google Chrome window whose active title passes the plan's process-and-title rule; revalidate before every frame copy, stop and clear pending pixels on the first ineligible callback, and never add generic browser capture, browser automation, an extension, debugging/DOM/tab access, or a Meet private API. Perform no facial identity, emotion/tone interpretation, audio, transcription, OpenAI call, memory, polished UI, or F03 work.
>
> Run and record every automated replay, deterministic WGC mock-call/title-invalidation integration check, CPU/GPU benchmark, performance, memory/frame-retention, offline/privacy, clean-install, and F01 regression defined in the plan. Record the real WhatsApp acceptance result and the user-approved Zoom/Meet validation waiver, substitute Chrome smoke evidence, and residual risks without presenting waived checks as passes. Before completion, perform the exact Claude Review Gate described in the plan using a tool-disabled read-only Claude Opus 5 session. Resolve accepted findings, document justified rejections, rerun affected and full checks, obtain Claude Opus 5 `PASS`, update the plan/Trello completion evidence, and stop with F02 complete. Do not begin F03.
