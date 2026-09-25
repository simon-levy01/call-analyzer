# Visible Luna5.6 replay — September24

User explicitly requested another visible, computer-use-observed real API replay on Luna5.6 low, continuing the same $0.70 recovery cap. Product baseline remains0488b20; Opus's oversized proposed prompt was not applied. No commit/push or quality acceptance implied.

Runner `build/visible_luna56_20260924.py` uses the existing replay audio/video classes, original88-turn arrival timing, actual Desktop retrieval/coordinator/API/rendering, disposable SQLite/QSettings and a shared-ledger adapter. It does not capture microphone, camera or vocal/visual sensor evidence. Summary generation is deliberately suppressed because this request authorizes Luna, while summaries use Sol. The source, exact model requests/outputs, usage and actual QLabel timeline are saved privately under `build/visible-luna56-20260924/`.

Computer Use started the call in the actual Windows interface, observed changing tones/cues/replies/follow-ups and Earlier retention, and opened/closed a real response popup while the call continued. One accessibility click became stale during a live update; subsequent coordinate-backed observation/action opened the popup successfully. Not every text fits the compact viewport; recorded render-state counts are not proof every text was simultaneously above the fold. No human semantic-accuracy acceptance is claimed.

## Memory failure discovered

The isolated database initially pointed at an empty adjacent model cache. A local junction to the already-installed cache and one scratch-memory embedding backfill corrected that test setup, without a download or API call. The early replay is therefore not valid indirect-recall evidence.

The warning nevertheless returned. A separate offline subprocess reproduced a deeper Windows runtime issue: importing audio/video/desktop and constructing QApplication before invoking FastEmbed causes `onnxruntime_pybind11_state` to fail with **DLL initialization failed**, despite the ready marker existing. Loading `onnxruntime` before those UI modules makes the same probe succeed with a384-dimensional embedding. These probes used only the synthetic text `local retrieval runtime probe`, no API.

This explains unavailable semantic retrieval in the observed UI process; it is not evidence that Luna5.6 caused the lost memory. The runtime startup-order fix has **not** been applied to product code in this testing-only request. The misleading install-model message also remains. Lexical matches can still reach the model, and no irrelevant memory should be forced into the panel.

## Accounting and verification

The shared ledger is `build/guidance-recovery-20260924/ledger.json`, starting at$0.31991499/$0.70 with every previous row and uncertain reservation preserved. The adapter reserves maximum exposure before dispatch, permits only Luna5.6 with bounded output, records completed usage or uncertain charges, and releases only known unbilled requests. Offline disposable-ledger checks cover cap-before-dispatch, preservation, completion, release, model restriction and interrupted reservation retention. Production retries remain disabled.

`build/audit_visible_luna56_20260924.py` verifies actual model/effort, shared accounting and displayed-text counts without inference. The settled audit records **88 turns,28/28 API responses,46 distinct rendered texts:14 tones,4 cues,25 replies,0 memories,3 follow-ups**. New charge **$0.032129**, shared cumulative **$0.35204399/$0.70**, no pending requests. These are displayed wordings, not46 useful independent interventions.

The initial `complete.json`/UI banner captured the last request's conservative reservation just before its settlement, reporting27 complete and$0.35341581. Preserve that provisional snapshot; `audit.json` and the shared ledger contain the settled totals above. This is a test-harness completion-observation race, not an extra charge. The app is left open for inspection; no automatic repeat is authorized.
