# F07 reusable-clip annotation protocol

Prepared September 14 before detector changes. This is fixture preparation, not a participant test of the application and not annotation results. The three application participant checks still require clean preliminary Opus 5 review first.

**Later user revision, September 14:** Assistant-authored screenshot annotations are permitted as provisional development evidence without waiting for independent human annotations before implementation. See [the dataset investigation and seven actual point annotations](F07-DATASETS.md). The independent protocol below remains the method for an independently measured timing result; it is no longer a code-start blocker. Point samples have unknown episode boundaries and cannot establish continuous duration or the original <=1-second gate.

1. Select approved reusable sources, record license/approval, SHA-256, selected remote face, exact source segment and tuning/held-out assignment. Keep different source families across splits. Existing basic/HeyGen media are historical regression/stress sources; differently cut segments do not make their faces unseen.
2. An independent human annotator views source media without detector labels, scores, generated emotion tags or candidate guidance. Use frame stepping and the decoded frame PTS, not wall-clock playback time. The saved `*-pts.json` files in the private preflight directory index decoded frames from zero.
3. Mark actual visible smile-like mouth corners, lowered brows and lowered mouth corners independently. Combinations get separate rows. For each episode record the first clearly visible frame and first frame where the configuration is absent; intervals are half-open. Record uncertain transition ranges and unknown visibility separately. Do not treat an instructed pose, low movement, or silence as a label.
4. Record speaking/listening/unclear timing, asymmetry and confounds (head movement, crop/scale, lighting, occlusion, small face, frozen image). Clip-start/end-truncated episodes have censored boundaries: retain them for eligible coverage, but do not invent onset/offset times. If uncertainty prevents a precise timing judgment, retain and report it separately.
5. Preserve the original annotations, annotator identifier/date, revisions and disagreements. Freeze their hash before looking at detector results. Verify clearly observable episodes of all three configurations with usable onset and offset boundaries before declaring timing-fixture feasibility established. Inadequate coverage blocks the gate.
6. Match reported/labeled episodes one-to-one for the same configuration with overlap and IoU >=0.5; maximize match count, then total IoU, resolving ties by earlier onset then stable episode ID. Duplicate fragments are extra detections; unmatched labels remain recall misses. Report onset and offset absolute errors separately using nearest-rank p95. Unknown visibility is not neutral and is not silently discarded.

Store one CSV row per labeled episode, using this header (no rows have been labeled yet):

```csv
source_sha256,source_segment,split,annotator_id,annotated_at,episode_id,configuration,onset_frame,onset_pts_seconds,offset_frame,offset_pts_seconds,onset_uncertain_from,onset_uncertain_to,offset_uncertain_from,offset_uncertain_to,visibility,censored_start,censored_end,speaker_timing,confounds,notes
```

Keep annotations and exact evidence in the new Git-ignored F07 directory. Reuse an existing frame-stepping player; no new downloader, annotation framework, call recording or raw-frame retention is needed. Model timing traces are collected only after the source annotations and applicable S0 freezes are ready.
