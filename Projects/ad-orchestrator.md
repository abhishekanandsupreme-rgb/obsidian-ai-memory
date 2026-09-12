---
title: "ad-orchestrator"
type: project
category: "Core User Repositories"
status: "Prototype / Early Draft"
completion_score: 30
is_finished: false
tech_stack: ["Next.js", "Node.js", "TypeScript"]
path: "C:/Users/asus/ad-orchestrator"
git_remote: ""
git_branch: ""
git_dirty: false
last_commit: ""
created_at: 2026-09-13
last_mapped: 2026-09-13 01:00:58
tags:
  - project
  - project-prototype
  - core-user-repositories
---

# ad-orchestrator

> **Category:** `Core User Repositories`
> **Lifecycle Status:** `Prototype / Early Draft` (Health Score: **30/100**)
> **Local Path:** `C:/Users/asus/ad-orchestrator`
> **Git Remote:** `Local Only / Unpushed`

---

## 📊 Lifecycle & Readiness Analysis
- No git tracking configured
- README documentation present
- Standard dependency manifest present

## 🧭 Overview & Mission
Internal ad server — API-first. Other apps (e.g. `healthfit-saas`) call it to fetch ad slots and track impressions/clicks. | Method | Path | Description | | ------ | ---- | ----------- | | GET | `/api/ads/slot?placement=banner&country=IN&uid=user1` | Serve a slot → `{ provider, creative, clickUrl, height, width, label, requestId }` | | POST | `/api/ads/impression` | Body `{ requestId }` → records an impression | | POST | `/api/ads/click` | Body `{ requestId }` → records a click, **302** to `clic

## 🛠️ Technology Stack
- **Languages & Frameworks:** Next.js, Node.js, TypeScript
- **Obsidian Graph:** [[AI Memory Hub]] | [[00_Projects_MOC]]

## 📂 Key Architecture
- **Sub-Modules:** `app/`, `lib/`, `node_modules/`, `scripts/`
- **Artifacts:** `next-env.d.ts`, `next.config.mjs`, `package-lock.json`, `package.json`, `README.md`, `tsconfig.json`

## 🚀 Developer Run & Next Steps
```bash
cd "C:/Users/asus/ad-orchestrator"
npm run dev
```
- **Next Action:** Complete core features, resolve git status, and push to remote.

## 🔗 Interlinks
- Master Index: [[00_Projects_MOC]]
- Category Hub: [[Core User Repositories]]
