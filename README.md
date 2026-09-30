# Conversation Copilot

The app that helps you talk to your friends and manage their information.

## Setup

Use **64-bit Python 3.12** and a compatible **NVIDIA GPU and driver** for the current
CUDA transcription backend. Minimum GPU memory has not been established. Installation
needs internet and several gigabytes for dependencies and models.

Open PowerShell in the source directory containing `pyproject.toml`:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[test]"
.\.venv\Scripts\python -m pip check
.\.venv\Scripts\python -m conversation_copilot --check
.\.venv\Scripts\python -m conversation_copilot --install-transcription-model
.\.venv\Scripts\python -m conversation_copilot --install-memory-model
```

No environment activation or execution-policy change is needed. The foundation
`--check` uses a fictional transcript and requires no API key or downloaded model.
The transcription model is required for calls. The optional memory model enables
indirect recall; without it, exact/date/full-text retrieval remains available.
Call startup never downloads models. Qt is pinned to 6.8.3 in `pyproject.toml`.

## Run

### Windows executable

The standalone build is about **1.63 GB**, mostly bundled NVIDIA libraries.
It is currently kept locally; a GitHub executable release is deferred because of
that size. Run `ConversationCopilot.exe` by double-clicking it. No Python installation
or terminal commands are needed to run the executable.
On first run, enter your own OpenAI API key and click **Prepare models and save key**.
The app checks the NVIDIA runtime, downloads its local models, and verifies them.
Internet and several GB of free space are needed for this one-time setup.
If a download fails, use **Retry setup**. Setup is also available in
**Settings → Local model setup**.

Requires 64-bit Windows and a compatible NVIDIA GPU and driver for calls.
The executable unpacks its libraries into a temporary directory on launch;
opening it can take a little time. Contacts, call history, approved memories, models
and the API key are saved under `%LOCALAPPDATA%\ConversationCopilot`, in your own
Windows account. The download contains no developer contacts, call records or API key.
Replacing the executable preserves your saved data.

To rebuild from this checkout:

```powershell
.\.venv\Scripts\python -m pip install -e ".[build]"
powershell -NoProfile -ExecutionPolicy Bypass -File packaging\build.ps1
```

The output is `dist\ConversationCopilot.exe`. See [download instructions](packaging/README.txt).
Packaging uses [PyInstaller](https://www.pyinstaller.org/en/stable/usage.html).

### From source

```powershell
.\.venv\Scripts\python -m conversation_copilot
```

1. Open **Settings** and save your OpenAI API key, or set `OPENAI_API_KEY` in the
   environment. The environment takes precedence. Settings writes `.env.local`
   beside the source; a blank save preserves the existing key.
2. Select or create the contact, select the call window, and explicitly choose
   your microphone and playback device.
3. Start the call. Live shows **Possible tones**, **Cues & context**,
   **Possible responses**, and **Related memories**. These are suggestions and can
   be wrong; retained items may stay visible for up to 180 seconds.
4. End the call, then review the generated summary and memory proposals. Approve
   only the information you want to keep. **Contact information** provides history,
   approved memories, source-based questions, corrections, deletion, and export.

Playback capture includes **all sound on the selected output device**. Silence
other apps and tabs. Device choices must be made again after restarting the app.
If microphone access is blocked, enable desktop-app microphone access in Windows
privacy settings. A lost visual target stops facial signals while transcription
continues; use **End call** to finish the session.

## Data and API usage

- Audio and video processing runs locally. Raw audio, frames, landmarks, and full
  blendshape histories are not saved by the app or sent to OpenAI.
- Live analysis sends bounded transcript excerpts, compact derived observations,
  and eligible retrieved contact information. Ask, participant detection, and
  post-call generation also send relevant text. Import participant detection sends
  at most the first 20 shortened lines and contact names on explicit selection.
- Live/Ask offers Luna low or Sol 6.1 low; summary and memory generation uses Sol 6.1 low.
  **API usage costs money. Normal app operation has no dollar cap.** Displayed
  usage and estimates are accounting, not spending limits. Starting/ending calls,
  Ask, participant detection, changed summary saves, and retries can send requests.
- Text and contact memory live in
  `%LOCALAPPDATA%\ConversationCopilot\memory.sqlite3`. Model suggestions require
  review before becoming approved memories or searchable summaries. Calls without
  a confirmed contact remain unassigned and do not retrieve or extract memories.
- Deletion removes the relevant local records and search data. Exported files and
  retained migration backups are separate copies; deleting in the app does not
  remove those copies. Failed migrations do not replace the database with an empty one.
- Never put API keys in source, screenshots, logs, or submission ZIPs. Git ignores
  environment files, databases, private evaluation output, and local personal PDFs.

## Tests and validation

```powershell
.\.venv\Scripts\python -m pytest
```

Ordinary tests use disposable data and fake providers. See the [testing guide](docs/TESTING.md)
and [current validation status](docs/F08-VALIDATION.md) for coverage and remaining limits.
The [Eden demo](DEMO.md) includes the original script and an extra opening for faster speech.
The source includes fictional replay fixtures and bundled vision models; their origins
are documented beside the [vision](conversation_copilot/assets/PROVENANCE.md),
[audio](conversation_copilot/assets/audio/PROVENANCE.md), and
[video-call](conversation_copilot/assets/f04/PROVENANCE.md) assets.

Historical experiment reports, agent session notes, and design mockups are retained
locally and in earlier Git history; they are not needed to install or run the app.
