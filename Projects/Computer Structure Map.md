---
title: Computer Structure Map
type: map
tags: [migration, filesystem, windows, drives]
status: active
tech_stack: [windows, powershell]
path: C:/Users/asus/Documents/Obsidian Vault/Projects/Computer Structure Map.md
git_remote: vault-internal
last_updated: 2026-09-17
---

# Computer Structure Map

Old PC filesystem as of 2026-09-17. User `asus`, win32.

## Drives

| Letter | Used | Free | Total | What It Is |
|---|---|---|---|---|
| C:\ | ~448GB | ~27GB (Health=Warning, low space) | 475GB | System + `C:\Users\asus` profile |
| D:\ | 128KB | ~29.7GB | 31.9GB | Empty removable/USB (only autorun.inf, System Volume Info, 2026-09-12) |
| G:\ | ~449GB | ~25.9GB | ~476GB | Google DriveFS mount #1 — `My Drive/` 6 items (Dead Air docs, gsheet demo) |
| H:\ | 15GB | 0 (full/quota) | 15GB | Google DriveFS mount #2 — `My Drive/` 83 items (UPSC, GATE, 2025 PC backup, resumes, Colab Notebooks) |

GoogleDriveFS x2 running. No local `Google Drive/` or `Dropbox/` folder; `Google Drive.lnk` on Desktop (2026-09-04).

## User Profile Root (`C:\Users\asus\`, 253 entries)

- `Desktop/` (59 files, 13 dirs), `Documents/` (12 files, 19 dirs incl. Obsidian Vault), `Downloads/` (67 entries)
- `OneDrive/` (Apps, Attachments, Desktop, Documents, Pictures, Videos) — last write 2026-07-18
- `AppData/`, `Pictures/`, `Videos/`, `Music/`, `Contacts/`, `Searches/`, `Saved Games/`
- Dotfiles: `.ssh/`, `.aws/`, `.config/`, `.claude/`, `.codex/`, `.gemini/`, `.opencode/`, `.cursor/`, `.vscode/`
- 30+ project dirs at root: `career-ops/`, `OpenCut/`, `WorkBuddy/`, `money-mission/`, etc. (see [[Projects Inventory]])
- `NTUSER.DAT` + `.regtrans-ms` registry hives — do not hand-copy, use Windows migration

## Desktop Top (13 dirs)

`.tmp.driveupload/`, `abhishek_personal_data/` (main workspace), `APOCALYPSE_VIDEO_ASSETS/`, `chrome-profile/`, `chrome_debug_profile/`, `Desktop/` (nested), `Founder mode/` (churnradar, guardian-eye, ranklens…), `linkedin_and_job_hunting/`, `odoo_multi_channel_crm client latest/`, `omnichannel crm odoo ashish bhai latest/`, `OmniChannel CRM odoo orig/`, `ringdesk-ai-mvp-deploy/` (Next.js), `Tor Browser/`. Plus ~40 `.lnk` (Obsidian, VS Code, Antigravity, BrowserOS, Docker, Gemini, Drive/Docs/Sheets/Slides), `claude-*.bat/ps1`, `Kill_Dev_Tasks.bat`, `Fix-PowerShell.bat`, `odoo_multi_channel_crm client latest.zip`, `comprehensive_testing_playbook.md`.

## Documents Top

`Obsidian Vault/`, `Projects/` (10 subfolders, AstroAI active), `Codex/`, `Cline/`, `Qoder/`, `kimi/`, `OmniChannel CRM odoo/`, `OneNote Notebooks/`, `Oneiros_Blueprint/`, `PowerShell/`, `WindowsPowerShell/`, `Custom Office Templates/`, `INSTALLER/`, `assets/`, `container/`, junctions for Music/Pictures/Videos. Odd hidden `*.qhlogs.*` files + `adsfd.txt`, `.spotube_logs`.

## Downloads Recent (newest)

`AstroAI-android-.../` (2026-09-17 DIR), `Agra Marvels — TAJGANJ...md`, `images.jpg` x5, `spectral-analysis_20260917053432.zip`, `topoexport-*.zip` (0.85/1.07MB, 09-16), `State-of-the-Art App Feature Plan...md`, `Shashi Edu — Client-Ready...html`, `3D Scrollable...html`, `Orbit — SaaS...html` x3, `FreeLLMAPI.Setup.0.11.0.exe` (103MB), `colibri-v1.11.0-windows-x86_64/`.

## Cloud Sync Status

- OneDrive: local mirror exists, stale since July — re-link, allow full sync on new PC
- G: + H: DriveFS mounts — verify both Google accounts sign in on new PC, confirm `2025 PC backup/` on H: before wiping old PC
- `.tmp.driveupload/` in Desktop/Documents/Downloads — transient upload staging, ignore

## Related

- [[Device Migration Index]]
- [[Projects Inventory]]
- [[Apps And Dev Environment]]
- [[Active Work Handoff]]
- [[AI Memory Hub]]
