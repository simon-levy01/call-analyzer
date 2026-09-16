# F07 dataset feasibility — September 14, 2026

Local pretrained vision screening is complete; two unannotated Seamless Interaction videos and96 GFT human label files were downloaded. See [CPU results and exact manual-access folders](F07-VISION-SCREENING.md). No external human-annotated video validation or production substitution is claimed.

Latest follow-up: [pretrained model and external-validation research](F07-PRETRAINED-MODELS.md). Prioritize GFT conversational clips and MMI's frame-coded AU subset. DISFA+ reuses nine original DISFA participants; it is not automatically an independent subject test. FEAFA+ channel numbering also needs care. No new data/model inference ran during this research.

## Downloaded DISFA assessed and used locally

The user supplied eight files under `build/datasets/DISFA/` and authorized development use. All originals remain intact and Git-ignored. Inventory/hashes, parsed-label coverage and extracted development videos are in `build/f07-disfa-20260914-v2/manifest.json`. The first five-window probe remains separately preserved in `build/f07-disfa-20260914/`; v2 adds a short AU15 window without changing subjects or production code.

Read the supplied PDF. Its twelve actions include AU4, AU12 and AU15. All 324 label files parse with consecutive 1-based frame numbers and intensity 0–5; every subject has the complete twelve-action set and matching label lengths. Both camera archives contain 27 video entries; left-camera subject IDs match labels. Archive hashes are recorded, not compared with an external publisher checksum. Only the three extracted development videos have been fully decoded/CRC-checked; no all-video integrity claim is made.

Split fixed before label/detector inspection: **SN001–SN003 development; the other 24 subjects reserved**. Only the left camera is used; the right view does not create independent subjects. Reserved-subject label counts were inspected for coverage, but no reserved videos or detector outputs were examined. This is a dataset-subject split, not completion of the separate 24-family language-model comparison design.

For this preparation only, intensity >=2 is a clear-action proxy, intensity 1 remains weak evidence, and 0 denotes annotated absence. Maximal contiguous runs are counted without gap filling; these counts are not scored detector episodes or validated visibility judgments.

| Action | Positive frames | Contiguous episodes | Holds >=3 seconds |
|---|---:|---:|---:|
| AU4 brow lowering | 19,933 | 207 | 63 |
| AU12 smile-like corners | 16,851 | 192 | 108 |
| AU15 mouth-corner lowering | 2,682 | 55 | 16 |

Six label-selected development windows comprise one positive window per action and one absence control per development subject. The first three subjects have no >=3-second AU15 hold, so its longest positive run (SN003, zero-based frames [1677,1719), 2.1 seconds) is used without changing the subject split. The smile window begins at the clip boundary; its onset is censored. Windows do not establish complete onset/offset timing coverage.

The **unchanged local MediaPipe FaceProcessor** decoded all 4,845 frames of each development video, confirmed 20 fps, strictly increasing timestamps equal to frame_index/20, and exact label/video count alignment (last PTS 242.2s). It returned a selected-face signal on **582/582 sampled frames**, including all six required left/right expression categories. Compact scores and timestamps were saved; no frames, thumbnails or full landmark histories were retained as probe output, and no cloud requests were made. Original/extracted licensed dataset videos remain local.

On labeled positive probe frames, mean paired blendshape scores were 0.3848 for brows (182 frames), 0.4681 for smiles (120), and 0.0256 for mouth-corner lowering (42). This small, selected sample shows why one shared score threshold is unsuitable; it does not establish calibrated cutoffs, accuracy or causality. No expression thresholds or production behavior have been changed, and **zero candidate tuning rounds** have been consumed.

Use [the local runner](../tools/evaluation/disfa.py) with a **new** ignored output directory for preparation, then `--probe` on that directory for local MediaPipe only. It refuses evidence outside `build/`, never imports historical inference runners, and extracts only whitelisted development-video basenames. A regression check covers label validation and half-open episode indexing: `python -m pytest -q tests/test_disfa.py` (1 passed). The original AAM landmark RAR, camera calibration files and stimulus video are unnecessary for the existing MediaPipe path. The PDF explains that the XLS lists old AAM landmark-tracking errors; its rows were not imported or used to exclude cases.

**No further dataset download is needed now.** DISFA+ may help later if controlled sustained mouth-corner holds are needed, but existing reserved DISFA subjects already contain 16 AU15 holds of at least three seconds across the whole dataset. Dataset checks supplement, not replace, later consenting live checks, Opus reviews or the 144-response guidance comparison. Preliminary/final reviews and human gates remain unrun.

## Decision

The initial investigation below preceded the user's download. DISFA has now been supplied and used as described above; statements about access below record that earlier investigation. The podcast annotations remain provisional development evidence, not independent precision, recall or <=1-second onset/offset proof. Live user checks remain later work.

The relevant FACS actions are AU12 (lip corner puller), AU4 (brow lowerer), and **AU15 (lip corner depressor)**. AU17 is chin raising, not a substitute for AU15. These actions describe configurations, not feelings. MediaPipe blendshape scores are not numerically interchangeable with FACS intensity labels. [AM-FED paper, Table 2](https://imotions.com/wp-content/uploads/2025/04/Affectiva-MIT-Facial-Expression-Dataset-AM-FED.pdf).

| Dataset | What the primary sources establish | F07 decision / access |
|---|---|---|
| DISFA | 27 adults; stereo facial video; frame-level 0–5 intensity scores by two FACS experts. Includes AU4/AU12/AU15 among twelve AUs. | Best fit for spontaneous configurations. Official research agreement/request required; video not obtained. [Official page](https://www.mohammadmahoor.com/pages/databases/disfa/), [access form](https://www.mohammadmahoor.com/pages/databases/disfa/forms/disfa/), [published AU annotation columns](https://github.com/dkollias/Fair-Consistent-Affect-Analysis). |
| DISFA+ | Extension combining posed and spontaneous expressions with manual frame-level intensity annotations. | Useful controlled complement, but a separate agreement is required. Do not count the same people as independent across DISFA variants. [Paper](https://openaccess.thecvf.com/content_cvpr_2016_workshops/w28/html/Mavadati_Extended_DISFA_Dataset_CVPR_2016_paper.html), [official access notice](https://www.mohammadmahoor.com/pages/databases/disfa/). |
| AM-FED | 242 webcam videos; independently coded actions/smiles. Published Table 2 reports only **one AU15-positive frame in one video**. Video frame rate is nonuniform. | Potential smile/brow stress evidence, insufficient mouth-corner-lowering coverage. Research use and no redistribution; original access route was not verified as currently working. [Original paper](https://imotions.com/wp-content/uploads/2025/04/Affectiva-MIT-Facial-Expression-Dataset-AM-FED.pdf). |
| EEV | Public CSVs pair stimulus-video IDs/times with model-generated expected **viewer reactions**; the repository describes 8 million annotations / 5,153 videos / 370 hours. | Wrong evaluation target: these are not human-coded actions of the people visible in each source video. Open CSV access does not solve our fixture need. [Official repository](https://github.com/google-research-datasets/eev). |
| DFEW | Movie clips with a seven-dimensional emotion distribution and a discrete emotion label per clip. | Does not provide the claimed frame-level AU onset/offset ground truth. May supply stress clips, not our three-action timing labels. [Official dataset](https://dfew-dataset.github.io/). |
| TalkCuts | Speech-generation dataset with textual descriptions, 2D keypoints and 3D motion. Access requires approval; research/noncommercial use, no redistribution. | No verified independent frame-level AU4/AU12/AU15 timing labels. VLM descriptions, if used, remain machine annotations. Not a shortcut to an independent timing gate. [Paper](https://arxiv.org/abs/2510.07249), [official access/terms](https://github.com/UMass-Embodied-AGI/TalkCuts). |
| FEAFA+ | Manually labeled floating-point actions; combines FEAFA with re-labeled DISFA. | Possible alternative, but requires a signed investigator agreement and approval by email; action definitions need explicit mapping. Re-labeled DISFA is not a new subject population. [Official page](https://www.iiplab.net/feafa+/). |

No forms were submitted, agreements accepted, emails sent, credentials collected or datasets republished. DISFA use would be local, with subject-separated tuning/holdout, source/label hashes, frame-to-video alignment checks, and frozen label-intensity thresholds before tuning. It evaluates facial observations, not guidance usefulness, conversation interpretation or API behavior. The 144-response comparison is a separate experiment.

## Assistant annotations of the supplied podcast

The supplied Markdown link's destination is `l-X6GxmoR8s`, although its display text names `vJsLDzNW6iQ&t=2443s`. Inspected the actual destination, **Jesse's Back and He's Played Games! | Geekenders Podcast Ep 141**, published by Jesse Cox, near the displayed link's 40:43 time. Selected only the **left tile**, with white headphones and a pink top, throughout. No identity matching or analysis of the other face was used.

Method: paused browser screenshots, five-second keyboard seeks, verified player time. Browser displayed whole seconds; subsecond PTS/frame identity was not recovered. Initial pause landed at 40:48. No video download or local screenshot files were retained. Source licensing for redistribution was not established; retain notes/links only. Screenshots are present in the task's tool history, so this is not a claim that no image ever left the browser.

Annotator: this Codex assistant, September 14. No detector output or MediaPipe values were shown during annotation. This is **assistant-authored development evidence**, not independent human coding, and this person/source is consumed for development rather than held out. All speaking/listening ownership is **unclear**: static mouth shape and muted playback do not establish speech attribution.

| Player time | Smile-like corners | Brow lowering | Mouth-corner lowering | Visible evidence / confound |
|---|---|---|---|---|
| [40:48](https://www.youtube.com/watch?v=l-X6GxmoR8s&t=2448s) | Uncertain/subtle | Not clearly present | Not clearly present | Closed mouth; slight corner elevation; partially lowered eyelids are not brow lowering. |
| [40:53](https://www.youtube.com/watch?v=l-X6GxmoR8s&t=2453s) | Present, mild | Not clearly present | Not clearly present | Closed lips with visibly raised corners; downward gaze. |
| [40:58](https://www.youtube.com/watch?v=l-X6GxmoR8s&t=2458s) | Present | Not clearly present | Not clearly present | Raised corners, cheek creasing, slight lip separation. |
| [41:03](https://www.youtube.com/watch?v=l-X6GxmoR8s&t=2463s) | Present, clear | Not clearly present | Not clearly present | Broad raised corners and visible teeth; head turns; hands rising below face. |
| [41:08](https://www.youtube.com/watch?v=l-X6GxmoR8s&t=2468s) | Present, clear | Unavailable/ambiguous | Not clearly present | Hands touch brow/temple areas, potentially changing geometry; smile remains visible. Do not infer a shared emotional label. |
| [41:13](https://www.youtube.com/watch?v=l-X6GxmoR8s&t=2473s) | Uncertain | Not clearly present | Not clearly present | Open, asymmetrically shaped mouth; possible articulation confound, speech attribution unverified. |
| [41:18](https://www.youtube.com/watch?v=l-X6GxmoR8s&t=2478s) | Present | Uncertain | Not clearly present | Raised corners, narrowed eyes and head tilt; do not turn eye narrowing into confident brow lowering. |

These are seven **point samples**, not seven expression episodes. They do not prove continuous holds between samples, onset/offset boundaries, or positive coverage for brow/mouth-corner lowering. No emotion, intent or psychological state is annotated. This small podcast sample supports smile persistence/confound test design only; it is not a passing F07 accuracy result.
