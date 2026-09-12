---
title: "agent_os"
type: project
category: "Core Repositories and Tools"
status: "Finished / Production-Ready"
completion_score: 98
is_finished: true
tech_stack: ["Python", "FastAPI", "Uvicorn", "WebSockets", "Tailwind CSS", "Mermaid.js"]
path: "C:/Users/asus/Desktop/abhishek_personal_data/agent_os"
git_remote: ""
git_branch: "main"
git_dirty: false
last_commit: "2026-09-13"
created_at: 2026-09-13
last_mapped: "2026-09-13 01:30:00"
tags:
  - project
  - project-finished
  - core-repositories-and-tools
  - agent-os
  - operating-system
---

# AgentOS — AI Agent Operating System & Second Brain Telemetry

> **Category:** `Core Repositories and Tools`
> **Lifecycle Status:** `Finished / Production-Ready` (Health Score: **98/100**)
> **Local Path:** `C:/Users/asus/Desktop/abhishek_personal_data/agent_os`
> **Web Dashboard:** `http://127.0.0.1:8000`

---

## 🧭 Overview & Mission
AgentOS is a state-of-the-art, heavily customizable AI Agent Operating System designed specifically for your local multi-agent environment. It unifies **Gemini / Antigravity**, **Claude Code (40+ profiles)**, **Hermes**, **Codex**, and **BrowserOS neo** on top of your **Obsidian Second Brain**, providing real-time visual telemetry, task dispatching, process state machines, and bidirectional vault memory synchronization.

```mermaid
graph TD
    UI["🖥️ Visual Operating Dashboard"] --> App["⚡ FastAPI + WebSockets"]
    App --> Kernel["🧠 AgentOS Kernel & Scheduler"]
    Kernel --> Agents["🤖 Fleet: Gemini | Claude | Hermes | Codex | BrowserOS"]
    Kernel --> Plugins["🔌 Plugin Bus: Vault | Local Agents | 224 Projects | Webhooks"]
    Plugins --> Vault[("📁 Obsidian Second Brain")]
```

## 🛠️ Technology Stack
- **Core Kernel:** Python 3.11, Pydantic, Event Bus, Priority Task Queues
- **Web Telemetry:** FastAPI, WebSockets, Jinja2, Tailwind CSS, Mermaid.js
- **Obsidian Bridge:** `vault-sync.py` bi-directional IPC, cross-agent briefing streaming

## 🚀 Developer Run Command
```bash
cd "C:/Users/asus/Desktop/abhishek_personal_data/agent_os"
python main.py
```