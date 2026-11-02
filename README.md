# Call Analyzer

Call Analyzer (previously Conversation Copilot) is a Windows desktop assistant for one-to-one video calls. It transcribes both sides
locally, offers possible tones and replies, and recalls approved information about
the selected contact. After a call, you can review its summary and memory suggestions.

Built with Python and PySide6/Qt. Supports eligible WhatsApp Desktop, Zoom meeting,
and dedicated Chrome/Google Meet windows. English transcription is supported;
macOS and CPU-only Windows operation are not yet validated.

For the submission video, see the [technology list and API flow](TECHNOLOGIES.md)
and [architecture diagram](TECHNOLOGY-FLOW.png).

## Semantic memory retrieval

Call Analyzer combines SQLite full-text search with local BGE-small-en-v1.5
embeddings (384 dimensions, FastEmbed / ONNX Runtime). This lets it retrieve
approved contact memories from related meanings even when the caller does not
repeat the original wording. Retrieved sources can be inspected, and generated
memories and summaries require user review and approval.

The Python package, launch command, and local data directory retain their original
`conversation_copilot` / `ConversationCopilot` names.

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

```powershell
.\.venv\Scripts\python -m conversation_copilot
```

1. First-run setup can prepare the models and save your API key. You can also
   open **Settings** and save your OpenAI API key, or set `OPENAI_API_KEY` in the
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
The source includes fictional replay fixtures and bundled vision models; their origins
are documented beside the [vision](conversation_copilot/assets/PROVENANCE.md),
[audio](conversation_copilot/assets/audio/PROVENANCE.md), and
[video-call](conversation_copilot/assets/f04/PROVENANCE.md) assets.

Historical experiment reports, agent session notes, and design mockups are retained
locally and in earlier Git history; they are not needed to install or run the app.
