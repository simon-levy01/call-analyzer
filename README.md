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

## Tests

```powershell
.\.venv\Scripts\python -m pytest
```
