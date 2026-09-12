---
title: "ad-orchestrator"
type: project
category: "Core Repositories & Tools"
status: active
tech_stack: ["Next.js", "Node.js", "TypeScript"]
path: "C:/Users/asus/ad-orchestrator"
git_remote: ""
created_at: 2026-09-13
last_mapped: 2026-09-13 00:29:15
tags:
  - project
  - core-repositories-and-tools
---

# ad-orchestrator

> **Category:** `Core Repositories & Tools` | **Status:** `Active`
> **Local Path:** `C:/Users/asus/ad-orchestrator`
> **Git Remote:** `Local Only / Unpushed`

---

## 🧭 Overview & Mission
Internal ad server — API-first. Other apps (e.g. `healthfit-saas`) call it to fetch ad slots and track impressions/clicks. | Method | Path | Description | | ------ | ---- | ----------- | | GET | `/api/ads/slot?placement=banner&country=IN&uid=user1` | Serve a slot → `{ provider, creative, clickUrl, height, width, label, requestId }` | | POST | `/api/ads/impression` | Body `{ requestId }` → records an impression | | POST | `/api/ads/click` | Body `{ requestId }` → records a click, **302** to `clickUrl` target | | GET | `/api/ads/click?rid=...` | Same as POST (click URL format) | | GET | `/api/ad

## 🛠️ Technology Stack
- **Core Tech:** Next.js, Node.js, TypeScript
- **Vault Integrations:** [[AI Memory Hub]] | [[00_Projects_MOC]]

## 📂 Key Architecture & Directories
- **Sub-Modules:** `app/`, `lib/`, `node_modules/`, `scripts/`
- **Key Artifacts:** `next-env.d.ts`, `next.config.mjs`, `package-lock.json`, `package.json`, `README.md`, `tsconfig.json`

## 🚀 Execution & Developer Quickstart
```bash
cd "C:/Users/asus/ad-orchestrator"
npm run dev
```

## 🔗 Interlinks & Knowledge Connections
- Master Index: [[00_Projects_MOC|Projects Map of Content]]
- Central Brain Hub: [[AI Memory Hub]]
- Category: [[Core Repositories & Tools]]
