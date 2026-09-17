---
title: Device Migration Index
type: moc
tags: [migration, device-move, moc, index]
status: active
tech_stack: [obsidian, windows, powershell]
path: C:/Users/asus/Documents/Obsidian Vault/Projects/Device Migration Index.md
git_remote: vault-internal
last_updated: 2026-09-17
---

# Device Migration Index

Master map for moving this whole computer to a new device. Surveyed 2026-09-17 with 5 parallel agents. Old machine: win32, user `asus`, C: 475GB (27GB free — low space warning).

## Map Notes

- [[Computer Structure Map]] — drives, Desktop, Documents, Downloads, cloud sync, critical paths
- [[Projects Inventory]] — all code repos in `abhishek_personal_data`, git remotes, sizes, priorities
- [[Apps And Dev Environment]] — installed apps, toolchain versions, VSCode extensions, reinstall checklist
- [[Active Work Handoff]] — recent files, in-flight tasks, VSCode folders, resume steps

## Migration-Critical Paths (copy first)

1. `C:\Users\asus\Documents\Obsidian Vault\` — this vault (git repo, last 2026-09-16)
2. `C:\Users\asus\Desktop\abhishek_personal_data\` — main workspace (see [[Projects Inventory]])
3. `C:\Users\asus\Desktop\Founder mode\` — churnradar, guardian-eye, ranklens + more
4. `C:\Users\asus\Desktop\ringdesk-ai-mvp-deploy\` — Next.js deploy (mod 2026-09-16)
5. `C:\Users\asus\Desktop\odoo_multi_channel_crm client latest\` — git repo 642MB
6. `C:\Users\asus\Documents\Projects\` — 10 subfolders incl. AstroAI (active 2026-09-17)
7. `C:\Users\asus\.ssh\`, `C:\Users\asus\.aws\`, `C:\Users\asus\.config\` — keys and CLI config
8. `G:\My Drive\` + `H:\My Drive\` — two Google DriveFS mounts (already cloud, verify on new device)
9. `C:\Users\asus\OneDrive\` — last sync 2026-07-18, re-link on new device

## Order Of Operations On New Device

1. Install runtimes + tools per [[Apps And Dev Environment]] reinstall checklist.
2. Sign in: Google Drive (2 accounts), OneDrive, GitHub (`gh auth login`), Obsidian.
3. Copy high-priority projects per [[Projects Inventory]] (skip `.venv`, `node_modules`, `scratch/`, OpenMontage bulk).
4. Re-link VSCode folders + restore extensions per [[Active Work Handoff]].
5. Verify `vault-sync.py status` + `brief` run clean, then resume in-flight tasks.

## Sources

Survey 2026-09-17: filesystem + projects + apps + recent-work + vault-state agents. Briefing showed hermes (47 logs) and copilot (68 artifacts) active — their stores live outside vault, do not hand-copy.

## Related

- [[AI Memory Hub]]
- [[00_Projects_MOC]]
- [[Computer Structure Map]]
- [[Projects Inventory]]
- [[Apps And Dev Environment]]
- [[Active Work Handoff]]
- [[briefing]]
