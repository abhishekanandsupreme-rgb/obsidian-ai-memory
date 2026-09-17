---
title: Projects Inventory
type: inventory
tags: [migration, projects, repos, git]
status: active
tech_stack: [python, node, nextjs, git]
path: C:/Users/asus/Documents/Obsidian Vault/Projects/Projects Inventory.md
git_remote: vault-internal
last_updated: 2026-09-17
---

# Projects Inventory

All code projects verified 2026-09-17. `apd/` = `C:\Users\asus\Desktop\abhishek_personal_data\` (66 entries). `README-master-index.md` = Ringdesk AI hub (Next.js+Supabase), not a code index.

## High Priority (own IP — copy fully)

| Project | Stack / Git | Size / Modified | Note |
|---|---|---|---|
| `apd/agent_os/` | py (agent-os, req+pyproject+Docker+.venv), git local-only no remote | 58.7MB / 31 files / 09-14 | AI Agent OS for local multi-agent |
| `apd/agents_factory/` | docs/configs, no git | 1.6MB / 30 / 09-16, README 09-17 07:04 | Distributed workstation master, newest/active |
| `apd/Agra Marvels/` | 3D/assets, no git | 293.9MB / 8 / 09-17 | Taj Mahal precinct 3D twin 1.03km |
| `apd/competitor_price_matcher/` | py+Docker, git → own remote | 0.3MB / 30 / 06-08 | MatchSentinel B2B price monitor |
| `apd/projects/` → `last-survivor-apocalypse/` | game, no git | 0.1MB / 4 / 09-14 | Own game + tests |
| `apd/resume/` | docs, no git | 0.2MB / 13 / 09-14 | Personal docs (also docx/html/md/pdf/txt set) |
| `apd/ringdesk-ai*` (11 md + 2 tsx) | Next.js+Supabase+Vapi, no git | ~0.3MB / 09-12→09-15 | Ringdesk AI business+MVP package |
| `Desktop/ringdesk-ai-mvp-deploy/` | Next.js+node_modules | mod 09-16 | Deploy build — high |
| `Desktop/odoo_multi_channel_crm client latest/` | git, 642MB | 08-10 | Odoo CRM client |
| `Documents/Projects/` | 10 subfolders incl. AstroAI | AstroAI mod 09-17 | Active today — cross-check [[Active Work Handoff]] |

## Medium Priority (forks — re-clone OK, copy only if dirty)

| Project | Remote | Size |
|---|---|---|
| `apd/crewai_new/` | `crewAIInc/crewAI`, py + .venv | 1203MB (venv bloat) |
| `apd/gods-eye-view/` | `bilawalsidhu/...`, node | 324MB |
| `apd/NemoClaw/` | `NVIDIA/NemoClaw`, node+Docker | 609MB |
| `apd/OpenMontage/` | `calesthio/OpenMontage`, py | 1838MB — audit bulk before move |
| `apd/colibri/` | `JustVugg/colibri`, py | 31.7MB |
| `apd/strix/` | `usestrix/strix`, py + .venv | 302MB |
| `apd/application_kit/` | job docs, no git | 11.8MB |

## Low Priority (stubs / re-clonable / temp)

`apd/CL4R1T4S/` (prompts, 3.1MB), `apd/system-prompts.../` (2.4MB), `apd/crewAI/`, `apd/posthog/`, `apd/posthog-repo/` (git local-only stubs), `apd/apply_team/` (2.9MB/77), `apd/records/` (~0), `apd/scratch/` (3.1MB/794 temp files — skip), `apd/LLM` (72-byte file).

## All `.git` Repo Paths (verified, no depth-2 nesting)

`apd/`: agent_os (local-only), CL4R1T4S, colibri, competitor_price_matcher (own), crewAI (local-only), crewai_new, gods-eye-view, NemoClaw, OpenMontage, posthog (local-only), posthog-repo (local-only), strix, system-prompts-and-models-of-ai-tools. Elsewhere: `Desktop/odoo_multi_channel_crm client latest`, `Documents/Obsidian Vault` (git, 09-16). Note: `apd/` itself is NOT a repo.

## Move Rules

- Copy: high-priority list + `.git` dirs for local-only repos (agent_os, crewAI, posthog, posthog-repo).
- Skip on copy: `.venv/`, `node_modules/`, `scratch/`, OpenMontage bulk data. Reinstall via pip/npm on new PC.
- Push first: competitor_price_matcher (own remote) — `git push` before move. Local-only repos: bundle (`git bundle`) or copy `.git` whole.
- D:\ empty — usable as sneakernet. G:\ = Drive mount, candidate staging target.

## Related

- [[Device Migration Index]]
- [[Computer Structure Map]]
- [[Apps And Dev Environment]]
- [[Active Work Handoff]]
- [[00_Projects_MOC]]
