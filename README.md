# Conversation Copilot

The desktop interface uses PySide6/Qt. Use the source setup below, then launch with `.venv\Scripts\python.exe -m conversation_copilot`. See [F08 validation](docs/F08-VALIDATION.md) for current results and remaining gates.

For model evaluation choices, historical tests and reusable logs, read [project instructions](AGENTS.md) and the [testing index](docs/TESTING.md).

The current application targets Windows. F10 is accepted; **F08 — Polish, QA and reliable Windows setup** is active, followed by **F09 — macOS support**. GitHub does not bundle the runtime or downloaded models. October 1 remains the Windows MVP/submission target, including the video, PDF and `finalproject.zip`; dedicated-installer and Mac completion dates are deferred.
The user will run F09 on a Mac for implementation and real-device validation;
Mac installation and operation are not supported yet. See the [master plan](PLAN.md#f09--macos-support-planned-not-started).

## Setup (Windows PowerShell)

Use **64-bit Python 3.12**, pinned **Qt 6.8.3**, and a compatible NVIDIA GPU/driver
for the current CUDA transcription backend. CPU-only Windows is not validated;
minimum GPU memory has not been established by F08. The metadata's `>=3.12` does
not establish support for every newer Python. Open PowerShell in the extracted
source directory containing `pyproject.toml`; quote paths containing spaces.
No environment activation or execution-policy change is needed.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[test]"
.\.venv\Scripts\python -m pip check
.\.venv\Scripts\python -m conversation_copilot --check
```

Installation requires internet and several gigabytes for dependencies/models.
Pip installs pinned NVIDIA runtime wheels; the GPU driver is a machine prerequisite.
`--check` validates only the included fictional foundation transcript; it needs no
downloaded model. Then provision models as described under
[local transcription](#two-sided-local-transcription) and
[contact memory](#contact-memory-and-personalization).
Start never downloads models. A fresh venv on a development PC is not a clean-machine
or physical-device pass.

## Run

```powershell
.\.venv\Scripts\python -m conversation_copilot
```

## Headless check

```powershell
.\.venv\Scripts\python -m conversation_copilot --check
```

## Video checks

The app lists only visible WhatsApp Desktop, Zoom, and dedicated Chrome windows
whose active title identifies Google Meet. It captures the selected top-level
window in memory, including visible Chrome browser controls. Switching that Chrome
window away from Meet stops capture and requires explicit reselection.
While an eligible WhatsApp call is present, Chrome/Meet is not offered. If a
WhatsApp call appears during an active Meet session, both audio sides stop and
require explicit reselection. The ordinary idle WhatsApp window does not block Meet.
The largest visible face is selected initially. **Switch face** chooses another
detected face; after 18 seconds of loss, **Continue tracking** explicitly resumes.
Small gallery tiles may be below the detector threshold, so use a layout with a
sufficiently large remote portrait.

Once two-sided audio is running, a lost or closed visual-capture target stops facial
signals but does not stop transcription. The status says that transcription is
continuing; use **End call** when the call ends. No replacement video window is selected
automatically. When a face thumbnail is unavailable, its empty area collapses so the
existing final transcript and microphone/playback states remain visible.

```powershell
.\.venv\Scripts\python -m conversation_copilot --check-video
.\.venv\Scripts\python -m conversation_copilot --check-video-capture
.\.venv\Scripts\python -m conversation_copilot --benchmark-video --seconds 600
```

MediaPipe processing is local. This application makes no network request for
vision processing and never writes captured frames or Facial Signals. Google's
[LiteRT in Google Play services privacy notice](https://developers.google.com/edge/litert/android/play_services#privacy_and_data_collection)
separately describes on-device input processing and performance/utilization
metrics for that Android service. This Windows Python application does not use
Google Play services and contains no metrics or network client.

## Two-sided local transcription

Before the first assisted call, use a supported NVIDIA GPU/driver and provision the
multilingual large-v3-turbo checkpoint pinned at revision
`0a363e9161cbc7ed1431c9597a8ceaf0c4f78fcf` plus the pinned CUDA wheel runtime once:

```powershell
.\.venv\Scripts\python -m conversation_copilot --install-transcription-model
```

Choose a microphone and playback device explicitly. The microphone threshold defaults
to 100; lower values are more sensitive if quiet speech is missed. Duplicate names show a temporary
`[WASAPI #index]` suffix; it is not a persistent identity. Playback capture is
endpoint-wide: every sound routed to the selected device can enter the contact
transcript. Close or silence Chrome and every other non-call audio app during
WhatsApp/Zoom. For Google Meet, use Chrome for the call and keep other Chrome tabs
and applications silent. The app shows this warning beside the playback selector.
English is the supported transcription language. Hebrew and automatic language
selection are currently excluded because their measured accuracy is not reliable
enough for the project text.
If microphone opening is blocked, enable **Let desktop apps access your microphone**
under Windows Settings > Privacy & security > Microphone, then reselect the device.
A clean **End call** keeps the explicit choices while device enumeration remains
live. An app restart clears device selections and requires explicit reselection;
temporary indices are never persisted or matched by name. **Refresh call windows**
updates the visual-window list, not the audio-device enumeration.

Finalized transcript text is saved locally. Raw audio remains in memory and is
not written to disk or sent to a cloud service. Start never downloads the model.
Validate the cached offline path with:

```powershell
.\.venv\Scripts\python -m conversation_copilot --check-audio
.\.venv\Scripts\python -m conversation_copilot --benchmark-audio --seconds 600
```

## Multimodal interpretation

The app sends only bounded English transcript excerpts and compact derived remote
vocal/visual observations to OpenAI. It never sends raw audio, video frames,
landmarks, or full blendshape history. Live/Ask select `gpt-5.6-luna` low or
`gpt-6-sol` low. Summary/memory generation uses Sol low independently. Normal product
operation has **no dollar cap**; displayed usage is accounting, not a balance.
Live uses a shared 6,000-token input allowance including instructions/schema and
1,800-token output limit. First analysis becomes eligible after six seconds once
speech is available; network/model latency is additional. The compact cloud payload uses
`u` and `c` for the user and confirmed contact; the visible transcript continues to
show `You` and the confirmed contact's name.

Save your API key through **Settings**, which writes ignored `.env.local` in the
editable source directory, or set `OPENAI_API_KEY` in the environment (takes precedence).
A blank Settings save preserves the existing key. Manual file format:

```text
OPENAI_API_KEY=replace-with-the-approved-key
```

`.env.local` and `.env` are ignored by Git. Do not commit, paste into source code,
or include the key in logs/source ZIPs. Start call, End call, Detect participants, Ask, changed
summary saves and Retry may dispatch cloud requests. Tests need fake/saved providers
or a newly applicable method/budget authorization. Historical paid commands are
research tools, **not setup checks**; their old caps do not authorize new runs:

```powershell
.\.venv\Scripts\python -m conversation_copilot --evaluate-f04
```

## Contact memory and personalization

Contact memory is local and unavailable until you select a contact. Use Home to
select or create a contact; open **Contact information** for saved facts and history.
Names and aliases are suggestions only; ambiguous aliases show candidates and
never select automatically. Calls that stop without a confirmed contact remain
under **Unassigned** and cannot retrieve or extract memory.

Concrete one-off routine activity may still appear as a proposal, but it is grouped
first and labeled **Likely generic — easy to reject**. It never becomes memory unless
you approve it. For example, carrying heavy things may be flagged as generic while
still helping retrieve an approved apartment-move memory. Vague references use only
the confirmed contact's bounded words after the latest vague cue. Weak matches
abstain and close matches appear as possibilities. Live shows **Possible tones**,
**Cues & context**, **Possible responses** and **Related memories**. Items may remain
up to 180 seconds, subject to source/topic/supersession checks; labels and their
underlying context share dismissal.

The app stores normalized attributed text in
`%LOCALAPPDATA%\ConversationCopilot\memory.sqlite3`. When the optional local model
is installed, the same database also stores regenerable memory vectors. It never
stores call audio, PCM, video, frames, landmarks, blendshapes, or face screenshots. After
an assigned call stops, bounded attributed-text chunks may be sent to OpenAI with
`store=false` to create proposals for review. Model output is never approved
automatically. **Contact information** provides approved memories, source-based Ask,
conversation history, correction, aliases, merge/delete and contact-scoped JSON export.
Transferred memories require review before retrieval. Current product permissions
allow otherwise eligible sensitive content in cloud requests; contact, source and
approval boundaries remain enforced.

Deleting a memory scrubs its full revision chain and search data. Deleting a
conversation previews derived memories with deletion selected by default. Kept
items retain only minimal source-deleted provenance. Deleting a contact removes
its records, proposal history, memories, aliases, and deletion tombstones. Exported
JSON files are outside the application's later deletion control.

If migration or integrity verification fails, memory opens read-disabled and the
app does not replace the database with an empty one. A retained
`.migration-backup` file can be restored after closing the app. Capture and local
transcription may continue without writable memory.

Run the zero-cost local quality/performance gate and the explicitly paid fictional
extraction comparison with:

```powershell
.\.venv\Scripts\python -m conversation_copilot --install-memory-model
.\.venv\Scripts\python -m conversation_copilot --evaluate-f05-local
.\.venv\Scripts\python -m conversation_copilot --evaluate-f05-real
```

The explicit install downloads about 67 MB once. Call startup never downloads a
model. If it is absent, exact/date/FTS5 retrieval remains available and the UI says
that indirect recall is reduced.

The local gate uses a temporary 100,000-revision database and deletes it after the
run. The historical paid comparison has a $2.00 internal ceiling, but still needs
a newly applicable explicit budget; the old ceiling is not authorization. Normal tests use fake models and
make no cloud calls. Current evidence and remaining manual validation are recorded
in `docs/F05-VALIDATION.md`.

## Compare transcription accuracy

Compare the current model with the default model/settings profiles from
Faster-Whisper-Transcriber, Stage Whisper, and noScribe. Provision the production
model with `--install-transcription-model` first; then this command downloads missing
comparison-only models and runs the complete selected profile benchmark:

```powershell
.\.venv\Scripts\python -m conversation_copilot.transcription_benchmark --download-models
```

The built-in run defaults to English. Pass `--language he` for the retained Hebrew
fixture; profiles that do not support Hebrew are excluded rather than scored as failures,
and selecting only incompatible profiles is an error. By default each clean fixture also
gets a deterministic call-like degraded case; pass `--clean-only` to disable that or
`--json` for machine-readable results.

The benchmark corpus retains exact English and Hebrew reference text so future
models can be compared. To test a video or audio file with a human-verified transcript:

```powershell
.\.venv\Scripts\python -m conversation_copilot.transcription_benchmark `
  --media .\sample.mp4 --reference .\sample.txt --language en --download-models
```

The noScribe row intentionally uses the same pinned weights as production with
noScribe's decoding settings. The Stage Whisper profile is a faster-whisper execution
of Stage Whisper's default
`base` weights because the linked Stage Whisper application pins a 2022 PyTorch
Whisper build. These are end-to-end profile comparisons: each application's decoding
settings are part of the result, so the report does not isolate model weights. The
50-clip FLEURS Hebrew matrix was a separate external-corpus evaluation and is not
recreated by the built-in two-clip fixture. The committed runner can repeat an external
corpus from a JSON manifest containing `media`, `reference`, and `language` fields:

```powershell
.\.venv\Scripts\python -m conversation_copilot.transcription_benchmark `
  --manifest .\fleurs-hebrew.json --language he --profiles `
  ivrit-large-v3 ivrit-large-v3-turbo ivrit-bilingual-v2-d4 general-large-v3 `
  current-fair original-small stage-base-fair --download-models --json
```

## Tests

Current Review supports complete-summary editing, explicit approval/rejection and
retry of failed generation. A changed summary can regenerate pending memory
proposals; an unchanged save does not. Approved summaries and memories can support
Ask answers with exact source excerpts and conversation navigation. Ask uses a
4,700-token evidence allowance within a 6,300-token input ceiling.

Import text sends at most the first 20 shortened lines and contact names on explicit
Detect participants. Confirm which of the two speakers is the contact before
Import and generate. Undated imports remain undated; exported app JSON is not a
transcript import format.

Run the ordinary disposable/fake-provider tests:

```powershell
.\.venv\Scripts\python -m pytest
```
These checks do not establish native usability, physical capture, real API quality
or clean-machine installation. See [F08 validation](docs/F08-VALIDATION.md) for evidence and limits.

The permanent `conversation_copilot/assets/f04/basic-video-chat` bundle is a
fictional two-person call used for basic F02-F05 replay. It includes the preview
video, separate microphone/contact audio stems, exact turns, progressive 12-second
tone/memory checkpoints, expected cues, and future memory cases. It does not replace
the controlled model evaluation or a consenting live WhatsApp validation.

`heygen-video-chat.mp4` is the additional realistic-media stress fixture. Its
automated replay checks compressed 720p decoding, persistent remote-face
tracking, landmarks, and changing blendshapes. Keep the basic fixture for exact
speaker timing and indirect-memory tests: the HeyGen render uses one animated
voice, a static Alex tile, visible free-tier watermarks, and omits the opening
`the event` line.
