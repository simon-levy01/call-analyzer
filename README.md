# Conversation Copilot

## Setup (Windows PowerShell)

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[test]"
```

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
detected face; after six seconds of loss, **Continue tracking** explicitly resumes.
Small gallery tiles may be below the detector threshold, so use a layout with a
sufficiently large remote portrait.

Once two-sided audio is running, a lost or closed visual-capture target stops facial
signals but does not stop transcription. The status says that transcription is
continuing; use **Stop** when the call ends. No replacement video window is selected
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
A clean **Stop** keeps the same explicit choices for the next **Start** while the
current device enumeration remains live. **Refresh** or an audio/device fault rebuilds
that enumeration, clears both choices, and requires reselection. An app restart never
restores prior choices or indices; its fresh enumeration may suggest the current
Windows defaults. Temporary indices are never persisted or matched by name.

Audio and final transcripts remain in memory for the current session. Raw audio is
not written to disk or sent to a cloud service. Start never downloads the model.
Validate the cached offline path with:

```powershell
.\.venv\Scripts\python -m conversation_copilot --check-audio
.\.venv\Scripts\python -m conversation_copilot --benchmark-audio --seconds 600
```

## Multimodal interpretation

The app sends only bounded English transcript excerpts and compact derived remote
vocal/visual observations to OpenAI. It never sends raw audio, video frames,
landmarks, or full blendshape history. Automatic Luna requests stop at the session
hard limit; Terra runs only after **Check with Terra** and a per-request cost
confirmation. Live Luna uses low reasoning with up to 16 complete turns from the
last three minutes; repeated speaker labels are omitted and old visual rows are
trimmed before conversation text when the request needs shortening. Automatic
request starts are separated by at least 17 seconds. The compact cloud payload uses
`u` and `c` for the user and confirmed contact; the visible transcript continues to
show `You` and the confirmed contact's name.

When an API key is approved, place it in `.env.local` at the project root:

```text
OPENAI_API_KEY=replace-with-the-approved-key
```

`.env.local` and `.env` are ignored by Git. Do not commit, paste into source code,
or include the key in logs. The fixed paid comparison is an explicit command and
has a shared $1.50 hard limit:

```powershell
.\.venv\Scripts\python -m conversation_copilot --evaluate-f04
```

## Contact memory and personalization

Contact memory is local and off until you explicitly confirm a contact. Use the
Selected Contact control to search, select, create, change, or clear a contact.
Names and aliases are suggestions only; ambiguous aliases show candidates and
never select automatically. Calls that stop without a confirmed contact remain
under **Unassigned** and cannot retrieve or extract memory.

Concrete one-off routine activity may still appear as a proposal, but it is grouped
first and labeled **Likely generic — easy to reject**. It never becomes memory unless
you approve it. For example, carrying heavy things may be flagged as generic while
still helping retrieve an approved apartment-move memory. Vague references use only
the confirmed contact's bounded words after the latest vague cue. Weak matches
abstain, close matches appear as possibilities, and unscored connected memories are
not added to this cautious path.

The app stores normalized attributed text in
`%LOCALAPPDATA%\ConversationCopilot\memory.sqlite3`. When the optional local model
is installed, the same database also stores regenerable memory vectors. It never
stores call audio, PCM, video, frames, landmarks, blendshapes, or face screenshots. After
an assigned call stops, bounded attributed-text chunks may be sent to OpenAI with
`store=false` to create proposals for review. Model output is never approved
automatically. **Manage memory** supports user-created
approved items with an optional `DD/MM/YYYY` event date, proposal approval/rejection/reopen, immutable correction,
sensitivity permission, search, merge/delete previews, and contact-scoped JSON
export. Approved sensitive memory is excluded from later cloud interpretation
unless cloud use is enabled for that exact current revision; changing or revoking
it clears affected guidance.

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
run. The paid comparison has a $2.00 hard cap; normal tests use fake models and
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

```powershell
.\.venv\Scripts\python -m pytest
```

The permanent `conversation_copilot/assets/f04/basic-video-chat` bundle is a
fictional two-person call used for basic F02-F05 replay. It includes the preview
video, separate microphone/contact audio stems, exact turns, progressive 17-second
tone/memory checkpoints, expected cues, and future memory cases. It does not replace
the controlled model evaluation or a consenting live WhatsApp validation.

`heygen-video-chat.mp4` is the additional realistic-media stress fixture. Its
automated replay checks compressed 720p decoding, persistent remote-face
tracking, landmarks, and changing blendshapes. Keep the basic fixture for exact
speaker timing and indirect-memory tests: the HeyGen render uses one animated
voice, a static Alex tile, visible free-tier watermarks, and omits the opening
`the event` line.
