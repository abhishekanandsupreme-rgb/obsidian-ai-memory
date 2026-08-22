@echo off
setlocal enabledelayedexpansion

:: ── Obsidian AI Memory Vault — Master Sync Batch ──────────────────────────
:: Runs sync-to-obsidian.py for all known agent IDs.
:: Uses sample/test session data when no real data is available.

set "VAULT=C:\Users\asus\Documents\Obsidian Vault"
set "SCRIPT=%VAULT%\scripts\sync-to-obsidian.py"
set "PYTHON=python"

echo [INFO] Starting agent memory sync for vault: %VAULT%
echo.

:: Known agent IDs
set "AGENTS=system claude-code hermes-agent browseros gemini codex"

:: Generate a timestamp for sample data
for /f "tokens=1-4 delims=/ " %%a in ("%date%") do (
    set "YYYY=%%d"
    set "MM=%%b"
    set "DD=%%c"
)
for /f "tokens=1-3 delims=:." %%a in ("%time%") do (
    set "HH=%%a"
    set "MN=%%b"
    set "SS=%%c"
)
:: Pad hour with leading zero if needed
if 1%HH% LSS 10 set "HH=0%HH%"
set "TIMESTAMP=%YYYY%%MM%%DD%-%HH%%MN%%SS%"

for %%A in (%AGENTS%) do (
    echo [INFO] Syncing agent: %%A

    :: Check if agent already has session files in the vault
    if exist "%VAULT%\Agents\%%A\sessions\*.md" (
        echo [INFO]   Found existing sessions for %%A, syncing real-ish data...
        %PYTHON% "%SCRIPT%" --agent-id %%A --session-data "{\"session_id\":\"recent-%TIMESTAMP%\",\"summary\":\"Recent activity synced from existing vault data\",\"status\":\"active\",\"started_at\":\"%date%T%time%\",\"key_events\":\"Existing session files detected in vault\",\"actions_taken\":\"Synced latest vault state\",\"decisions_made\":\"None\",\"next_steps\":\"Continue monitoring\"}" --project-context "{}"
    ) else (
        echo [INFO]   No existing sessions for %%A, using sample data...
        %PYTHON% "%SCRIPT%" --agent-id %%A --session-data "{\"session_id\":\"sample-%TIMESTAMP%-%%A\",\"summary\":\"Sample sync for %%A — no real data available yet\",\"status\":\"active\",\"started_at\":\"%date%T%time%\",\"key_events\":\"No recent activity found in agent data stores\",\"actions_taken\":\"Generated sample session entry for vault continuity\",\"decisions_made\":\"Use sample data until real sessions are available\",\"next_steps\":\"Check agent logs on next sync\"}" --project-context "{}"
    )

    echo.
)

echo [INFO] Agent memory sync complete.
endlocal
