# Bulk review approval responsiveness — September 25

The UI performed review writes synchronously. Every proposal reread the source transcript and relinked every summary statement against all proposals/memories, then rebuilt the summary index. A large import made this repeated work block the Qt event loop for many minutes.

Approval now caches source eligibility within the write transaction, defers summary relinking to once per affected record and reindexes once after the batch. Existing single-memory creation/edit semantics, stale-selection checks, source exclusions and atomic rollback remain. Summary approval uses the same batch path and caches eligibility during statement validation.

Review approval/rejection and combined summary approval use the existing desktop worker with its own SQLite connection. The UI displays a saving status and disables repeat actions and closing/Escape until the transaction completes. Results return through the existing UI-thread queue. This uses cross-platform Python/Qt, not Windows threading APIs; physical macOS validation remains deferred.

Opus 5.5 high performed scoped read-only review (`build/approval-review-opus-20260925.json`). No data-loss issue found. Its write-contention concern was addressed with a worker-only five-second busy timeout and refusing review saves during an active/starting/stopping call or generation. The modal saving panel prevents starting another UI operation while saving; SQLite still serializes brief existing semantic-backfill writes. Lock failures roll back and restore review controls/selection. No database journal-mode migration was added. Its redundant-index finding was fixed by letting summary approval reindex only after updating summary state. Test gaps were covered with dependency/revision assertions, close and Escape checks and worker-error recovery.

## Offline verification

- Final full suite: **413 passed in 70.09s**; `git diff --check` passes. Reopened temporary Luna app responds normally; no generation was launched.

- Regression tests first reproduced per-memory full-summary relinking and approval blocking the UI thread.
- Tests cover batching, source caching, atomic rollback, worker thread ownership, responsive Qt timers, duplicate-click prevention and close/Escape guards. Existing approval/rejection tests wait for worker completion.
- Private saved-database replay: 489 current eligible proposals approved in 8.28 seconds. Actual offscreen Qt Review replay: 8.22 seconds, 229 event-loop timer ticks, all 489 approved cards present. No API inference, model calls or live-data approvals were performed by these tests.
- The earlier diagnostic count of 530 also included 41 proposals in a superseded batch. They are not current selectable proposals and remain preserved.
- Before restarting the frozen app, a consistent SQLite backup was created in ignored `build/before-approval-fix-20260925.sqlite3`, integrity checked. The uncommitted approval transaction was rolled back when the verified frozen process was stopped. Live database recheck: integrity OK, 8,713 transcript turns, all 530 proposals pending and 938 saved summary statements retained. No regeneration is needed to approve the current proposals.

The temporary Luna launch profile remains separate from normal product model defaults. Reopening Review does not dispatch generation; Retry generation is an explicit additional action. Existing unfinished summary-generation work is not marked complete by this fix. No commit/push or evaluation-budget reset.
