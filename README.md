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
approved multilingual model plus the pinned CUDA wheel runtime once:

```powershell
.\.venv\Scripts\python -m conversation_copilot --install-transcription-model
```

Choose a microphone and playback device explicitly. Duplicate names show a temporary
`[WASAPI #index]` suffix; it is not a persistent identity. Playback capture is
endpoint-wide: every sound routed to the selected device can enter the contact
transcript. Close or silence Chrome and every other non-call audio app during
WhatsApp/Zoom. For Google Meet, use Chrome for the call and keep other Chrome tabs
and applications silent. The app shows this warning beside the playback selector.
Language choices are English, Hebrew, and Auto. Auto makes a fresh choice for each
finalized utterance but is intentionally limited to English or Hebrew; it cannot
select a third language and does not translate.
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

## Tests

```powershell
.\.venv\Scripts\python -m pytest
```
