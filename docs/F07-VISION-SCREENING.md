# F07 downloaded vision models — September 14, 2026

User authorized downloading and locally testing all shortlisted vision models, prioritizing RAM. This is separate from Luna guidance evaluation. No paid API inference, production model replacement, new tuning round or F07 release is authorized by the results here.

## Evidence and protocol

Private evidence: `build/f07-pretrained-20260914/`. Preserve `protocol.json`, original downloaded weights/source/license files, installation logs, `bench.py`, `monitor.py`, `score.py`, per-run stdout, raw numeric predictions and 100 ms process-tree resource samples. CPU-only runs use four configured math threads; the host is a Ryzen 9 3900X with 24 logical processors and an RTX 4060 Ti with 8,188 MiB VRAM. GPU results are not measured by a CPU run.

The original six DISFA development windows (582 frames, SN001–SN003) remain fixed. Human intensity >=2 is positive; 0 negative; weak intensity 1 is excluded. Unavailable observations are reported separately. No remaining held-out DISFA subjects are opened. External pretrained models may already have trained on DISFA, so these quality results are diagnostic, not independent validation.

Baseline uses current FaceProcessor and F07 persistence. LibreFace uses its matching ONNX encoder/intensity head and published alignment function with current selected-face landmarks. OpenGraphAU ResNet18 stage2 and OpenFace3 use that common alignment for integration screening. Those adapters are not equivalent to each toolkit's complete default pipeline. Py-Feat uses its modular XGBoost pipeline with emotion, identity and gaze disabled. Raw frames/crops stay in memory; original source videos remain private. No raw media upload.

Working set is resident RAM; private bytes include committed memory that Windows may page. Report both, with disk storage separately. OpenFace2 processes all three complete source videos; Python adapters score the six windows while decoding their source streams. Therefore total wall time is not directly comparable; Python frame processing percentiles exclude skipped-frame decoding, and the first 20 processed frames are excluded from those percentiles. OpenFace2's first exploratory run overlapped initial dependency preparation. These are not the approved matched ten-minute full-app/audio resource gates. OpenFace2 dynamically postprocesses AU predictions using the whole input sequence; its quality scores are not proof of causal live performance. The Python adapters use current selected-face landmarks; the native and Py-Feat detector paths still require selected-face integration checks before production use.

## Acquired models

- Existing MediaPipe assets retained as baseline.
- LibreFace AU encoder and intensity ONNX pair downloaded from official OpenSense storage.
- OpenFace 2.2 Windows x64 binary and all four CECLM patch scales downloaded from official release/script URLs; binary launches successfully.
- OpenGraphAU ResNet18 stage2 checkpoint downloaded from the official linked Drive ID.
- OpenFace3 AU/emotion/gaze checkpoint, RetinaFace and 98-point landmark weights downloaded from official Hugging Face repository. The AU head has eight outputs; no AU15 coverage or accuracy score is inferred without verified mapping.
- Py-Feat XGBoost v2 weights and required face/landmark dependencies downloaded; modular Detectorv1 initializes successfully. Installed in a private benchmark environment, not the app environment.

## External clips requiring user access

GFT: downloaded all 96 public human occurrence CSVs plus Supplemental.pdf and MetaData.xlsx, verifying OSF SHA-256 values. The public root lists annotations/documentation but no videos. The author access page and OSF page were opened in Codex. Put original video archives in `build/datasets/GFT/`; retain filenames and agreements. [Author access](https://jmgirard.com/datasets/), [OSF](https://osf.io/7wcyz/).

MMI: the official information page was opened. The checked portal returned 404; no video download succeeded. Put original videos/ZIPs and accompanying AU labels in `build/datasets/MMI/`. Prefer frame-coded AU4/12/15 and neutral sequences. [Official information](https://www.ibug.doc.ic.ac.uk/research/mmi-database/).

BP4D+: optional institutional-access backup. Official access page opened; no institutional agreement submitted and no multi-terabyte download attempted. Request only an appropriate labeled RGB/FACS subset, then store originals in `build/datasets/BP4D-plus/`. [Official access](https://www.cs.binghamton.edu/~lijun/Research/3DFE/3DFE_Analysis.html).

Each destination includes PLACEMENT.txt. ZIP files can remain zipped. No external clips with independent human AU ground truth have yet been obtained; labels alone cannot validate a detector. No manual-access forms or messages were sent.

## Additional downloaded conversation clips

Two videos from different sessions in [Meta Seamless Interaction](https://github.com/facebookresearch/seamless_interaction) are downloaded under `build/datasets/SeamlessInteraction/` (70,721,935 bytes total; 176 and230 seconds;1080×1920,30fps). Selection is frozen as the first two different sessions in the official improvised/dev file list, before examining detector outputs. CC BY-NC4.0 license and original file list/download hashes are retained locally. The first120 frames of each short compressed remux were verified byte-for-byte after decoding and matched original PTS. The original videos remain intact; no frame-image caches or raw media upload.

These clips support independent-source robustness/resource smoke checks. Their automatically generated facial features are not used as human AU labels, and no accuracy score is assigned to them. GFT/MMI access remains necessary for the planned independent annotated validation.

## Completed CPU screening results

Sampled peak memory is **resident working set / private committed MiB** (1 MiB=1,048,576 bytes). These are visual-runner processes, not whole-app requirements. Private committed memory can exceed physically resident RAM. Python speed columns are frame-processing p50/p95 milliseconds; native OpenFace2 reports whole-run FPS because per-frame latency was not instrumented. Do not compare native FPS as an equivalent measured p95. GPU/VRAM performance and low-end hardware were not tested. No overall accuracy winner or F07 gate pass is claimed.

| Visual pipeline | DISFA peak MiB | Portrait-clip peak MiB | DISFA speed | Portrait speed |
|---|---:|---:|---:|---:|
| MediaPipe + F07 | 199 / 321 | 258 / 385 | 13.0 / 14.0 | 23.5 / 25.5 |
| LibreFace ResNet18 ONNX | 293 / 506 | 356 / 569 | 35.8 / 38.9 | 49.5 / 52.0 |
| OpenGraphAU ResNet18 stage2 | 686 / 988 | 750 / 1049 | 94.3 / 103.4 | 107.4 / 116.3 |
| OpenFace3 AU backbone + MediaPipe | 684 / 971 | 756 / 1043 | 51.4 / 55.2 | 63.9 / 67.1 |
| Py-Feat XGBoost modular | 1076 / 1373 | 1326 / 1690 | 481.5 / 520.8 | 1312.1 / 1359.8 |
| OpenFace2 CECLM native | 890 / 1780 | 1044 / 1915 | 35.0 FPS end-to-end | 35.2 FPS end-to-end |

### Development-only per-AU results

Cells show **precision / recall / F1 (%)**, at frozen default thresholds. These are582 label-selected development frames, not a representative population or independent held-out test. OpenFace2 native predictions use whole-video postprocessing; specialist adapters use common alignment, which may differ from original evaluation preprocessing. Treat surprising scores as adapter/checkpoint diagnostics. No model or threshold was tuned after seeing these labels.

| Pipeline | Brow AU4 | Smile AU12 | Mouth corners AU15 |
|---|---:|---:|---:|
| MediaPipe + F07 | 98.7 / 80.8 / 88.8 | 85.1 / 100.0 / 92.0 | 100.0 / 7.1 / 13.3 |
| LibreFace ResNet18 ONNX | 100.0 / 3.3 / 6.4 | n/a / 0.0 / 0.0 | n/a / 0.0 / 0.0 |
| OpenGraphAU ResNet18 stage2 | 95.8 / 100.0 / 97.8 | n/a / 0.0 / 0.0 | 100.0 / 95.2 / 97.6 |
| OpenFace3 AU backbone + MediaPipe | Not scored: mapping unverified | Not scored: mapping unverified | Not scored: mapping unverified |
| Py-Feat XGBoost modular | 47.0 / 99.5 / 63.8 | 23.3 / 100.0 / 37.9 | 16.5 / 100.0 / 28.3 |
| OpenFace2 CECLM native | 98.9 / 97.3 / 98.1 | 81.6 / 100.0 / 89.9 | 48.3 / 100.0 / 65.1 |

Unavailable/weak/missing counts and recall including all positive labels are retained in screening-results.json. External clips have no human AU score; finite-output availability is recorded separately and does not establish correctness.

Practical outcome: retain current production. The existing pipeline remains the smallest and fastest tested runner. OpenGraphAU detects more mouth-corner-lowering examples here but fails the smile examples at its unchanged threshold and adds substantial runtime memory. LibreFace is the lightest specialist adapter but its default-threshold development scores are poor. OpenFace2 performs better on several development observations at a much larger memory cost, and its offline postprocessing must not be mistaken for live accuracy. Py-Feat is slow and memory-heavy in this full modular configuration. OpenFace3 remains ineligible for a three-target recommendation without a verified checkpoint label mapping.

These screens do not replace the three consenting human checks, independent annotated timing/accuracy, matched full-app/audio resource tests, or required reviews. No paid API inference ran; the prior aggregate commitment remains $0.07768505/$0.30. F07 is not complete and no commit/push or release is claimed.

Environment correction: the first Python pass inherited a global optional TensorFlow doc-generation import through MediaPipe. Those higher-RAM results remain diagnostic. Clean runs use a venv without system packages, confirm TensorFlow is absent, and load native inference runtimes before MediaPipe to avoid Windows DLL initialization failures. Initial failed runs remain preserved and excluded from ranking. The original app venv is unchanged.

### Download and runtime footprint

Model/checkpoint files on disk: MediaPipe 3.8 MiB; LibreFace 43.1 MiB; OpenGraphAU 45.8 MiB; OpenFace3 AU checkpoint 97.0 MiB; Py-Feat required AU/face/landmark weights 235.0 MiB. OpenFace2 extracted native distribution (models plus binaries/libraries) is 728.1 MiB. The shared clean environment containing all Python challengers is 1747.3 MiB logical file size, not a per-model shipping requirement. These are disk sizes, not RAM. OpenFace3 auxiliary detector/landmark files were downloaded but are not part of its measured AU-backbone runner.

The portrait smoke tests process240 frames per Python runner; native OpenFace2 processes244 because compressed packet cutting retains two additional display frames per clip. Its sample is therefore not an exactly identical per-frame throughput measurement. All first120 frames per clip were verified against the originals. Output availability is239/240 for the shared MediaPipe-based runners,240/240 for Py-Feat and244/244 for native OpenFace2; availability alone does not establish correct identity or AU predictions.

Offline integrity checks passed for14 completed Python prediction sets, including diagnostics: record counts, unique frame keys, monotonic timestamps, absence of retained frame-image caches, and TensorFlow absent in clean/external runs. Scorer checks confirm missing/nonfinite output cannot become a correct negative. Original failed runs remain excluded from ranking.
