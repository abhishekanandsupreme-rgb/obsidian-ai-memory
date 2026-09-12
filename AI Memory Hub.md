---
type: hub
created: 2026-09-12
---

# AI Memory Hub

One shared memory space for every local AI agent: **hermes, claude, codex, gemini, prime** (plus [[registry|agent registry]]).

## How it works
- Engine: `scripts/vault-sync.py` — syncs real session data from every agent's store every 15 minutes (scheduled task `ObsidianVaultSync`).
- Each agent writes to `agents/<id>/sessions/` and `agents/<id>/memory/`.
- Everyone reads [[briefing|the last-24h cross-agent briefing]] before starting work.
- Weekly rollup: `memory/session-notes/digest-<week>.md`.

## Read this first
- [[briefing|Cross-Agent Briefing (last 24h)]]
- [[registry|Agent Registry]]
- Agents' instruction blocks (CLAUDE.md / AGENTS.md / GEMINI.md) mandate: read before work, log after work, never duplicate another agent's in-flight task.

## Rules
1. Read `memory/cross-agent/briefing.md` before multi-step tasks.
2. Log sessions + durable facts with `vault-sync.py log`.
3. No secrets in notes.
4. Git-tracked: `https://github.com/abhishekanandsupreme-rgb/obsidian-ai-memory`
