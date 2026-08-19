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
The largest visible face is selected initially. **Switch face** chooses another
detected face; after six seconds of loss, **Continue tracking** explicitly resumes.
Small gallery tiles may be below the detector threshold, so use a layout with a
sufficiently large remote portrait.

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

## Tests

```powershell
.\.venv\Scripts\python -m pytest
```
