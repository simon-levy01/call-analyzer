# F07 pretrained models and external validation — September 14, 2026

Historical research findings; the subsequent user-authorized downloads and CPU screening are recorded in [F07-VISION-SCREENING.md](F07-VISION-SCREENING.md). This research snapshot is not an approved production replacement. No model weights were installed, no inference ran and no additional API budget was spent. Existing MediaPipe/F07 code and all prior evidence remain intact. We calibrated observations from an already pretrained model; we did not train a new neural network on DISFA.

## Downloadable candidates

The target outputs are AU12-like lip-corner pulling, AU4 brow lowering and AU15 lip-corner depression. AU17 chin raising is not interchangeable with AU15. Presence scores, FACS intensity and animation blendshapes must not be treated as the same numerical scale.

| Candidate | Verified evidence | Recommended role |
|---|---|---|
| Existing MediaPipe + F07 persistence | Local code uses downloaded Face Landmarker and BlazeFace assets. Measured file sizes: 3,758,596 and 229,746 bytes, totaling 3.804 MiB. These are asset sizes, not runtime RAM. | Required baseline; freeze current thresholds/persistence and selected-face behavior. |
| LibreFace | Pretrained CPU/GPU paths and ONNX exports are provided. The official intensity output explicitly includes AU4/12/15 on a 0–5 scale. | First specialist challenger; test AU encoder/intensity head without unused emotion/gaze models. |
| OpenFace 2.2 | Official Windows binaries and pretrained models; AU4/12/15 have occurrence and intensity outputs. | Established independent implementation for comparison; older native integration. |
| Py-Feat XGBoost AU model | Downloadable pretrained HOG/XGBoost detector, including AU15. Its probabilities are detections, not a FACS intensity regression. | Third challenger for presence and resource comparisons. Pin the modular model, not a changing default pipeline. |
| OpenGraphAU ResNet-18 | Released checkpoints and 41 action categories including all three targets. | Reserve challenger if the first two do not suffice. Published high FPS uses RTX 3090, not our CPU. |
| OpenFace 3.0 | Official weights and CPU inference examples exist, but inspected source defaults to eight AU outputs without establishing the downloadable checkpoint's complete label order/AU15 coverage. | Hold until checkpoint-to-label mapping is verified; do not infer coverage from the toolkit name. |

Sources: [MediaPipe task](https://developers.google.com/edge/mediapipe/solutions/vision/face_landmarker), [LibreFace implementation/download routes](https://github.com/ihp-lab/LibreFace), [LibreFace intensity labels](https://github.com/ihp-lab/OpenSense/blob/master/Utilities/LibreFace/ActionUnitIntensityOutput.cs), [OpenFace AU outputs](https://github.com/TadasBaltrusaitis/OpenFace/wiki/Action-Units), [Windows binaries](https://github.com/TadasBaltrusaitis/OpenFace/wiki/Windows-Installation), [Py-Feat models](https://py-feat.org/pages/models/), [XGBoost weights](https://huggingface.co/py-feat/xgb_au), [OpenGraphAU](https://github.com/lingjivoo/OpenGraphAU), [OpenFace 3 weights](https://huggingface.co/nutPace/openface_weights), [eight-output source](https://github.com/CMU-MultiComp-Lab/OpenFace-3.0/blob/main/model/MLT.py).

LibreFace's [NuGet package](https://www.nuget.org/packages/LibreFace) includes downloadable ONNX files (80.08 MB full package); its version 2.0.0 is dated February 2024. Do not confuse that package number with the May 2026 LibreFace 2.0 research update. Pin exact file hashes and model architecture. The intensity ONNX head consumes features, so the matching encoder is also required. Its documented aligned RGB input is 224×224. The high-level Python video wrapper writes temporary intermediates; a production adapter must instead process selected-face crops in memory. CPU availability does not establish that the existing resource limits will pass.

The [USC license](https://github.com/ihp-lab/LibreFace/blob/main/LICENSE.rst) permits educational/research/nonprofit use subject to its terms and directs commercial users to USC. OpenFace also has research-use and training-data restrictions; [OpenFace 3's license](https://github.com/CMU-MultiComp-Lab/OpenFace-3.0/blob/main/LICENSE) restricts distribution. Py-Feat's modular AU model is described as MIT, but other bundled components have separate restrictions. OpenGraphAU code is Apache-2.0; dataset/checkpoint rights still need checking. These are published terms, not a claim that every model can be bundled into an unrestricted commercial release.

## Validation clips to obtain

**First choice: GFT (Sayette Group Formation Task).** Real unscripted three-person conversations: 96 participants, 172,800 frames, approximately 1.4 GB in the paper. Human occurrence coding includes AU4/12/15 and speech; intensity coding covers only five AUs, including AU12 but not AU4/15. Good for conversational presence, false alarms and occlusion. AU4 is relatively rare, so count positive episodes before freezing a subset. Split by whole conversation group, not just individual faces. [Author paper](https://www.ri.cmu.edu/pub_files/2017/5/fg17_gft.pdf), [project](https://osf.io/7wcyz/), [author access page](https://jmgirard.com/datasets/). Public OSF project metadata was verified; file listing timed out, so immediate video download/access was not confirmed. Participant-specific usage restrictions must be retained.

**Second choice: MMI's frame-coded AU subset.** Covers complete neutral/onset/apex/offset cycles and single-AU examples. The collection has over 2,900 videos/stills from 75 people, but only part has frame-level phase annotations. Obtain the actual AU4/12/15 clips and their frame-level labels, not merely video-level emotion tags. [Official research description](https://www.ibug.doc.ic.ac.uk/research/mmi-database/). Current download-site access was not confirmed; published scientific access is not proof of an immediately downloadable archive.

**Backup: BP4D+ RGB and corresponding FACS labels only.** Larger spontaneous collection with 140 people. The full multimodal release is enormous and the official route requires institutional agreement; students must involve their supervisor. Ask whether the labeled 2D subset can be supplied separately. Confirm participant/checkpoint overlap with BP4D before treating it as independent. [Official dataset/access page](https://www.cs.binghamton.edu/~lijun/Research/3DFE/3DFE_Analysis.html).

**Do not select DISFA+ as an automatically independent replacement.** Its paper explicitly recruited nine of the original 27 DISFA participants. It can add controlled temporal clips, but not unseen identities for a model trained on all DISFA. This sharpens the earlier conditional recommendation in F07-DATASETS.md. [Original paper](https://www.cv-foundation.org/openaccess/content_cvpr_2016_workshops/w28/papers/Mavadati_Extended_DISFA_Dataset_CVPR_2016_paper.pdf).

**Do not pool FEAFA+ blindly.** Part B is relabeled DISFA. Part A provides different participants, but the [actual protocol](https://www.iiplab.net/feafa+/protocol-2021-en.pdf) uses its own 24-channel animation numbering; channel 15 is a right lip-corner stretch, not FACS AU15. It is not a verified three-target validation set without further mapping/annotation. Emotion-only movie datasets and AU scores generated by another detector are also not independent human AU ground truth.

Training overlap is a model-by-dataset matrix, not a property of a dataset alone. LibreFace's released inference configuration names DISFA and `fold=all`; [OpenFace](https://github.com/TadasBaltrusaitis/OpenFace/wiki/Datasets), Py-Feat XGBoost and OpenGraphAU also list DISFA in training. Consequently our remaining DISFA subjects are not automatically held out from those external weights. GFT/MMI are promising external sources, not yet proven clean for every checkpoint. Unknown training overlap must be reported as unknown, including for MediaPipe.

## Proposed comparison, before choosing a winner

Use the same timestamped frames, selected identities and whole-person/group splits for every system. Freeze model versions, preprocessing, output-label maps and thresholds before scoring. Preserve development-only calibration and untouched final subjects; do not spend a third F07 tuning round. First screen unchanged pretrained checkpoints. A production replacement is a material plan/code change requiring its own review and applicable gates; research alone does not enact it.

| Measurement | What to report |
|---|---|
| Detection quality | Per-AU precision, recall, F1, confusion counts, PR-AUC and false positives per minute; subject/group uncertainty intervals. Never rank by raw accuracy on mostly-negative frames. |
| Continuous observations | Sustained coverage, missed holds, onset/offset p50/p95 error, jitter and gaps. Score timing only where human frame labels actually support it. |
| Intensity | MAE/concordance only for compatible human intensity labels and regression outputs; do not invent intensity from classifier confidence. |
| Memory | Model files and full dependency footprint separately; cold/warm/peak process-tree working set and private bytes; GPU VRAM separately; growth after warm-up. Disk size is not RAM. |
| Speed/load | Cold load time, full decode/crop/alignment/inference/persistence p50/p95, sustained FPS, frame age/drops, CPU seconds and GPU utilization. Separate CPU-only and GPU results. |
| App integration | Same concurrent transcription workload; slowdown, stalls, face-loss/switch safety and unchanged speech-triggered cloud behavior. No raw-frame retention/upload. |

Detected local hardware: Ryzen 9 3900X (24 logical processors), RTX 4060 Ti. No new model speed/RAM measurements were taken. Reuse the approved three sequential matched ten-minute resource pairs with two-minute warm-up, alternating order; include child processes rather than comparing a Python process against only an OpenFace launcher. Keep classifier-only and complete-pipeline measurements separate.

Selection rule: first satisfy the existing per-target quality/safety/timing gates, then compare RAM, latency and integration cost among qualifying candidates. If none qualifies, report that and retain the approved fallback; do not declare the smallest inaccurate model the winner. This local visual benchmark is separate from the Luna guidance comparison and does not by itself fix reminder or ownership errors.

Recommended next acquisition: GFT, then MMI's frame-coded target-AU subset. Keep original downloads and licenses under ignored `build/datasets/<dataset>/`, with no redistribution. No access forms were submitted or messages sent in this research session.
