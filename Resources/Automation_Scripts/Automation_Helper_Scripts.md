---
title: "Automation Helper Scripts Directory"
type: reference
tags: [automation, powershell, python, scripts]
---

# ⚡ Automation Helper Scripts

Key utility scripts available in the workspace:

### 1. Headful Remote Chrome Launcher (`chrome_debug_launcher.ps1`)
```powershell
$UserDir = "$env:LOCALAPPDATA\Google\Chrome\User Data"
Start-Process -FilePath "C:\Program Files\Google\Chrome\Application\chrome.exe" -ArgumentList "--remote-debugging-port=9222 --user-data-dir='$UserDir' --no-first-run" -WindowStyle Normal
```

### 2. CDP Evaluation Script (`cdp_eval.ps1`)
Evaluates JavaScript directly on attached Chrome tabs via WebSocket CDP protocol without execution policy blocks.

### 3. Audio Transcription Engine (`transcribe_audio.py`)
Local Faster-Whisper script for transcribing microphone recordings or video audio files into text.
