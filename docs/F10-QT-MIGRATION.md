# F10 Qt migration — 22 September 2026

Branch: `codex/qt-ui-migration`. User visual acceptance and post-user-test review remain required; this is not a full F10 acceptance claim.

## Technology decision

Selected **PySide6 / Qt Widgets**, retaining Python and SQLite. Qt provides Python bindings, cross-platform controls, layouts, accessibility roles, stylesheets and deployment tooling. It avoids adding a JavaScript/Python protocol, web server or Rust shell to this Python-heavy project. Check Qt LGPL/commercial packaging obligations during F08 distribution work. [Qt for Python](https://doc.qt.io/qtforpython-6/).

Compared pywebview and Tauri: pywebview provides a JavaScript/Python bridge; Tauri can package Python as a sidecar. Both support customizable web interfaces, but introduce a front-end runtime and cross-language lifecycle boundary here. This is a project-fit decision, not a claim that Qt is universally faster. [pywebview](https://pywebview.flowrl.com/guide/), [Tauri sidecars](https://v2.tauri.app/develop/sidecar/).

The UI toolkit is portable; Windows audio/capture is **not** thereby a working Mac backend. WinRT dependencies now have platform markers. Non-Windows discovery reports capture unavailable while local memories/history remain accessible. Native macOS installation and binary dependency validation remain F09.

## Implementation

Product Tk construction and its theme are removed. The launch command remains `python -m conversation_copilot`. Historical standalone test utilities may still use Tk. `desktop.py` owns Home/Live, workers and the ported coordinator; `desktop_data.py` owns data dialogs; `qt_theme.py` owns shared styling. Existing schemas and model prompts are unchanged.

Discovery, runtime preparation, capture startup/shutdown, retrieval, Ask and generation use workers. The GUI timer consumes results; workers never mutate Qt widgets. Guidance is rebuilt only when content changes. Main Start/End controls remain outside scrolling content, editors resize, and dense guidance has a scroll fallback rather than clipping controls. Qt color-scheme hints/DWM blend Windows captions with dark mode.

The previous code had redundant redraw work and synchronous startup paths. Removing those hazards is **not proof that they explain every reported freeze**. New delayed-work tests verify that GUI clicks/timers continue responding. Real-call resource/latency acceptance is not claimed.

Finalized audio results drain before record finalization. Persistent cloud/save errors have independent labels. Settings never reveals a key or performs paid validation. Readiness refreshes key presence periodically and after Settings changes. Source/revision/ownership and approval boundaries remain in the existing backend.

Normal End call starts generation after successful saving. Exiting the application does not start fresh paid generation; the retained record remains available in History for Generate/continue. Failed transcript persistence/finalization also does not silently generate from partial data. The in-memory transcript remains reachable through a recovery button, and clearing it or exiting requires a warning confirmation. A source-store failure during stop must still return Home rather than strand the Live page.

## Verification and review

Combined offline suite: **354 passed** (14 Qt integration tests and 340 existing checks). The earlier 13-test UI set also passed simulated Qt scaling factors 1.5 and 2. `python -m conversation_copilot --check` passed its 500-turn/two-speaker check; `pip check` reported no broken requirements.

Pinned `PySide6-Essentials==6.8.3` (only the modules the app uses). The initial 6.11.2 spike passed isolated UI tests but crashed the combined Windows suite: `import winrt.runtime; from PySide6.QtCore import Qt` produced a native access violation. The same minimal reproduction passes with 6.8.3 in an isolated environment and the project environment. Both capture/Qt import orders now have subprocess regression checks; no import-order workaround is used. This is a newly caught migration compatibility issue, not a claim about the old Tk freeze's cause.

Qt tests use fictional contacts/disposable stores, QtTest mouse/key events and fake devices/model answers. Coverage includes readiness negatives, dropdowns, modal routing, key masking, Ask/edit/delete, resizable editors, history without inference, checkboxes and bulk approvals, stale corrections, import attribution, aliases/export, delayed discovery, final-turn flush, popup invalidation, store errors, merge confirmation and non-Windows capture guarding.

Fictional rendered screenshots are ignored local files under `build/qt-ui-check/`. Native computer-use access is unavailable: Qt event simulation and rendered image inspection are substitutes, **not an independent computer-use pass**. Physical 150%/200% desktop scaling, screen readers, native Mac and live inference quality are not claimed tested.

Preliminary tool-disabled review used verified **claude-opus-5**. Accepted fixes: persistent errors, merge confirmation, startup failure dialog, source-safe popups, generation source-limit preflight, quoted asset paths and busy-store handling. Rejected assumptions: `audio.py` has no top-level WinRT import; removed broad memory/diagnostic actions were expressly excluded by the user; key readiness follows current F10; automatic import generation is approved behavior and does not need a new permission prompt. CLI audio-to-turn helpers moved to the model module to avoid importing the entry module twice. Follow-up results are recorded after verification.

## Pending user walkthrough

Review follow-up initially reported no material findings. Subsequent targeted lifecycle review found two save-error paths: record finalization could strand Live, and record creation failure could misleadingly display “Call saved.” Both now retain persistent recovery messaging, return Home and suppress generation; fault-injection tests exercise both. The review's request to auto-generate on exit was rejected in favor of the documented no-fresh-generation-on-exit policy. Raw code-review evidence is retained locally under ignored `build/qt-review*.json`; no private call data was sent for this review.

Check Home/dropdowns in both themes, resize a memory editor, open/close nested dialogs, and confirm Start requires all selections. During a consenting call, check compact Live, red End call, popouts, source access and transcript behavior. No live call is started by the UI test suite. Visual approval and post-user-test review remain outstanding.
