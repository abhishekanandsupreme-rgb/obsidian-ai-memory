@echo off
rem Obsidian AI Memory vault - scheduled sync wrapper (15 min)
cd /d "C:\Users\asus\Documents\Obsidian Vault"
set "PY=C:/Users/asus/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe"
set "LOG=scripts\task-sync.log"
echo ===== %DATE% %TIME% ===== > %LOG%
"%PY%" "scripts\vault-sync.py" sync >> %LOG% 2>&1
"%PY%" "scripts\vault-sync.py" brief >> %LOG% 2>&1
"%PY%" "scripts\vault-sync.py" digest >> %LOG% 2>&1
"%PY%" "scripts\vault-sync.py" heartbeat >> %LOG% 2>&1
"%PY%" "scripts\vault-sync.py" commit --push >> %LOG% 2>&1
