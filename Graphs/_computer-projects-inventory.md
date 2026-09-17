---
title: Computer Projects Inventory (bounded discovery)
type: inventory
tags: [inventory, archify, graphify, discovery-only]
status: active
last_updated: 2026-09-17
source_task: bounded-discovery-no-full-extraction
---

# Computer Projects Inventory (bounded, discovery-only)

> Method: top-level `-Directory` listings + marker-file checks only. No recursive file counts, no `node_modules/.git` traversal. Rough size = **top-level entries count only**.
> Prior deep work exists — do NOT redo it. See §0.

## 0. Prior pcmap-20260917 work (do not duplicate)

Session log: `C:/Users/asus/Documents/Obsidian Vault/agents/opencode/sessions/20260917-171937_pcmap-20260917.md`

5 notes found under the vault (all in `Projects/`):

| # | Note | Path |
|---|------|------|
| 1 | Device Migration Index | `C:/Users/asus/Documents/Obsidian Vault/Projects/Device Migration Index.md` |
| 2 | Computer Structure Map | `C:/Users/asus/Documents/Obsidian Vault/Projects/Computer Structure Map.md` |
| 3 | Projects Inventory (deep: sizes MB, 13 git repos, high/med/low priority, move rules) | `C:/Users/asus/Documents/Obsidian Vault/Projects/Projects Inventory.md` |
| 4 | Apps And Dev Environment | `C:/Users/asus/Documents/Obsidian Vault/Projects/Apps And Dev Environment.md` |
| 5 | Active Work Handoff | `C:/Users/asus/Documents/Obsidian Vault/Projects/Active Work Handoff.md` |

Summary from session file: 5 parallel agents (filesystem/drives, 13 git repos + priorities, apps/toolchain VSCode-55/npm-40, active work agents_factory+AstroAI+Odoo+Ringdesk, vault state). Key flags: C: low space, G/H are DriveFS mounts, skip `.venv/node_modules/scratch`.

This file is intentionally **shallower** than note #3: discovery + markers + mapping queue only.

## 1. Desktop (`C:\Users\asus\Desktop`, 72 top entries)

| Project dir | Markers | Likely stack | Top entries |
|---|---|---|---|
| `Founder mode/` | (none at root; subdirs: churnradar, guardian-eye, tokenguard, trustdesk… + `index.html`, `node_modules/`) | Vanilla HTML/JS micro-SaaS portfolio | 27 |
| `ringdesk-ai-mvp-deploy/` | `package.json`, `README.md` (+`app/`, `lib/`, `.next/`, `node_modules/`) | Next.js/TypeScript | 15 |
| `odoo_multi_channel_crm client latest/` | `.git`, `package.json`, `requirements.txt`, `Dockerfile`, `docker-compose.yml` | Python/Odoo + Node, Docker | 84 |
| `omnichannel crm odoo ashish bhai latest/` | `Dockerfile`, `docker-compose.yml`, `README.md` | Odoo/Docker copy | 7 |
| `OmniChannel CRM odoo orig/` | `README.md` | Odoo copy (orig) | 4 |
| `APOCALYPSE_VIDEO_ASSETS/` | (none; `hyperframes*/`, `*.json` props, `*.mp4`) | Video/assets, Hyperframes | 25 |
| `linkedin_and_job_hunting/` | `requirements.txt`, `Dockerfile`, `docker-compose.yml`, `README.md` | Python/Docker job toolkit | 16 |

## 2. abhishek_personal_data (`C:\Users\asus\Desktop\abhishek_personal_data`, 69 top entries)

| Project dir | Markers | Likely stack | Top entries |
|---|---|---|---|
| `agents_factory/` | `README.md` (+`PROJECT.md`, `*.py` orchestrators) | Python orchestration (active) | 30 |
| `agent_os/` | `.git`, `pyproject.toml`, `requirements.txt`, `Dockerfile`, `docker-compose.yml`, `README.md` | Python Agent OS | 31 |
| `crewAI/` | `.git`, `README.md` | Stub/fork | 5 |
| `crewai_new/` | `.git`, `pyproject.toml`, `README.md` | Python (CrewAI fork) | 24 |
| `colibri/` | `.git`, `pyproject.toml`, `README.md` | Python (fork) | 51 |
| `NemoClaw/` | `.git`, `package.json`, `Dockerfile`, `README.md` | Node (fork) | 58 |
| `OpenMontage/` | `.git`, `setup.py`, `requirements.txt`, `README.md` | Python (fork) | 54 |
| `spynel/` | `.git`, `README.md` | Stub | 7 |
| `strix/` | `.git`, `pyproject.toml`, `README.md` | Python (fork) | 23 |
| `posthog/` | `.git`, `README.md` | Stub | 5 |
| `posthog-repo/` | `.git`, `README.md` | Stub | 5 |
| `CL4R1T4S/` | `.git`, `README.md` | Prompts | 29 |
| `gods-eye-view/` | `.git`, `package.json`, `README.md` | Node (fork) | 32 |
| `competitor_price_matcher/` | `.git`, `requirements.txt`, `Dockerfile`, `docker-compose.yml`, `README.md` | Python + Docker (own IP) | 30 |
| `application_kit/` | `README.md` | Job docs | 7 |
| `apply_team/` | `README.md` | Data/docs (77 items, not all code) | 77 |
| `resume/` | `README.md` | Docs | 13 |
| `Agra Marvels/` | `README.md` | 3D/assets | 8 |
| `projects/last-survivor-apocalypse/` | (none; only `assets/` at top; sibling `tests/`, `README.md`, `.gitignore`) | Game (tiny) | 1 (+tests/README at parent) |

Excluded as non-projects: `records/`, `scratch/` (temp), `LLM` (72-byte file), loose `*.md/*.png/*.py` at root (e.g. ringdesk-ai-*.md/tsx business pack).

## 3. Documents/Projects (`C:\Users\asus\Documents\Projects`, 10 subdirs)

| Project dir | Markers | Likely stack | Top entries |
|---|---|---|---|
| `Affiliate marketing business plus other side gigs/` | `README.md` | Docs/business | 199 |
| `Ai hack agent/` | `README.md` | Docs/stub | 3 |
| `AstroAI-android-feature-desi-connect-app-9924190810085556398/` | `.git`, `README.md` (+`backend/`, `docs/`) | Mobile + backend (active 09-17) | 21 |
| `Personal and jobs/` | `README.md` | Docs | 3 |
| `Ragdoll Dodgeball/` | `README.md` | Docs/stub | 3 |
| `React Duels/` | `.git`, `README.md` | React/Node | 20 |
| `shashi-international-school/` | `package.json`, `README.md`, `Dockerfile` | Node/Docker (school site) | 21 |
| `shashi_school_app/` | `README.md` | Mobile app (README-only at top) | 23 |
| `Yotube automation +side gigs/` | `README.md` | Docs/scripts | 12 |
| `youtube ai song music/` | `README.md` | Docs/stub | 3 |

## 4. Documents root extras

| Project dir | Markers | Likely stack | Top entries |
|---|---|---|---|
| `C:\Users\asus\Documents\OmniChannel CRM odoo/` | `docker-compose.yml`, `README.md` | Odoo/Docker copy | 4 |
| `C:\Users\asus\Documents\Oneiros_Blueprint/` | `README.md` (+`*.dart` files) | Dart/Flutter blueprint | 5 |

## 5. Drives D:, G:, H: (honest status)

| Drive | Status | Top-level seen | Code projects |
|---|---|---|---|
| `D:\` | Accessible, ~empty | `System Volume Information/`, `autorun.inf`, `autorun.ico` only | 0 |
| `G:\` | Accessible, DriveFS mount | `G:\My Drive/` → 6 gdoc/gsheet stubs (Dead Air docs, gmass demo) | 0 |
| `H:\` | Accessible (reports 0 free), DriveFS mount | `H:\My Drive/` → study/personal: Pmnt, Dc, Upsc 2024, GATE, Youtube, Google AI Studio, Colab Notebooks, resumes, SSC PDFs | 0 |

Skipped honestly: no recursive walks on G:/H: (Drive-mount stubs + large personal backup `2025 PC backup/`), no byte-size or full file counts anywhere (timeouts), no `node_modules/.git/.venv` interiors.

## 6. Priority queue for archify/graphify mapping

Requested bias: smallest / most-active first — agents_factory, ringdesk-ai-mvp-deploy, odoo dirs, Founder mode, last-survivor-apocalypse.

| Order | Target | Why |
|---|---|---|
| 1 | `abhishek_personal_data/agents_factory/` (30) | Most active, newest (README 09-17), small |
| 2 | `Desktop/ringdesk-ai-mvp-deploy/` (15) | Active Next.js MVP, small, no .git check needed |
| 3 | `abhishek_personal_data/projects/last-survivor-apocalypse/` (tiny) | Smallest real project; fast first graph win |
| 4 | `Desktop/odoo_multi_channel_crm client latest/` (84) + 3 sibling odoo copies | Active client work but large (642MB per prior note); dedupe 4 copies BEFORE mapping — map `client latest` only, link others as copies |
| 5 | `Desktop/Founder mode/` (27) | Portfolio of ~12 micro-SaaS subdirs; map root once, then per-subdir only for churnradar/guardian-eye/tokenguard if active |
| 6 | `Documents/Projects/AstroAI-…/` (21) | Active today per prior handoff; mobile+backend |
| 7 | `abhishek_personal_data/agent_os/` (31) | Local-only git, mid-size; needs bundle before wipe |
| 8 | `abhishek_personal_data/competitor_price_matcher/` (30) | Own IP + own remote → `git push` first, then map |
| 9 | `Documents/Projects/shashi-international-school` + `shashi_school_app` | Paired school web+app |
| 10 | Forks batch (crewai_new, colibri, NemoClaw, OpenMontage, strix, gods-eye-view) | Re-clonable; map only if dirty; OpenMontage bulk data last (largest) |
| 11 | Stubs/docs batch (crewAI, posthog, posthog-repo, spynel, CL4R1T4S, application_kit, apply_team, resume, Agra Marvels, APOCALYPSE_VIDEO_ASSETS, linkedin_and_job_hunting, Oneiros_Blueprint, remaining Documents/Projects) | Docs/assets; cheap to map, low value |

Dedupe warning: 4 odoo copies (`client latest`, `ashish bhai latest`, `orig`, `Documents/OmniChannel CRM odoo`) — confirm canonical before graphing. Prior deep note (#3) already covers git-remotes/sizes; consult it at step 4+.

## Related

- [[Device Migration Index]]
- [[Computer Structure Map]]
- [[Projects Inventory]]
- [[Apps And Dev Environment]]
- [[Active Work Handoff]]
