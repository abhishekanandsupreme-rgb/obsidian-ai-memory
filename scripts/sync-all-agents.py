#!/usr/bin/env python3
"""
sync-all-agents.py — Master sync script for Obsidian AI Memory vault.

Discovers agent configs and session data from known locations, generates
sample/test data when no real data is available, and calls sync-to-obsidian.py
for each agent.

Usage:
    python sync-all-agents.py [--dry-run] [--agent-id <id>] [--vault-path <path>]

Agents discovered:
    system, claude-code, hermes-agent, browseros, gemini, codex
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── Defaults ────────────────────────────────────────────────────────────────
VAULT_ROOT = Path("C:/Users/asus/Documents/Obsidian Vault")
SYNC_SCRIPT = VAULT_ROOT / "scripts" / "sync-to-obsidian.py"

# Known agent IDs and their data source hints
KNOWN_AGENTS = [
    "system",
    "claude-code",
    "hermes-agent",
    "browseros",
    "gemini",
    "codex",
]

# ── Agent data discovery ────────────────────────────────────────────────────

def discover_hermes_sessions() -> list:
    """Discover recent Hermes Agent sessions from request dumps."""
    sessions = []
    sessions_dir = Path("C:/Users/asus/AppData/Local/hermes/sessions")
    if not sessions_dir.is_dir():
        return sessions

    # Find recent JSON request dumps (last 24 hours)
    cutoff = datetime.now(timezone.utc).timestamp() - 86400
    for p in sorted(sessions_dir.glob("*.json")):
        try:
            mtime = p.stat().st_mtime
            if mtime < cutoff:
                continue
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            sessions.append({
                "source": str(p),
                "session_id": data.get("session_id", p.stem),
                "timestamp": data.get("timestamp", datetime.now(timezone.utc).isoformat()),
                "model": data.get("request", {}).get("body", {}).get("model", "unknown"),
            })
        except Exception:
            continue
    return sessions


def discover_claude_sessions() -> list:
    """Discover Claude Code sessions."""
    sessions = []
    sessions_dir = Path("C:/Users/asus/AppData/Local/Claude-3p/claude-code-sessions")
    if not sessions_dir.is_dir():
        return sessions

    cutoff = datetime.now(timezone.utc).timestamp() - 86400
    for agent_dir in sessions_dir.iterdir():
        if not agent_dir.is_dir():
            continue
        for p in sorted(agent_dir.rglob("*.json")):
            try:
                mtime = p.stat().st_mtime
                if mtime < cutoff:
                    continue
                sessions.append({
                    "source": str(p),
                    "session_id": agent_dir.name,
                    "timestamp": datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat(),
                    "model": "claude-code",
                })
            except Exception:
                continue
    return sessions


def discover_codex_sessions() -> list:
    """Discover Codex CLI sessions."""
    sessions = []
    sessions_dir = Path("C:/Users/asus/.codex/sessions")
    if not sessions_dir.is_dir():
        return sessions

    cutoff = datetime.now(timezone.utc).timestamp() - 86400
    for p in sorted(sessions_dir.rglob("*")):
        if not p.is_file():
            continue
        try:
            mtime = p.stat().st_mtime
            if mtime < cutoff:
                continue
            sessions.append({
                "source": str(p),
                "session_id": p.stem,
                "timestamp": datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat(),
                "model": "codex",
            })
        except Exception:
            continue
    return sessions


def discover_browseros_sessions() -> list:
    """Discover BrowserOS sessions."""
    sessions = []
    sessions_dir = Path("C:/Users/asus/.browseros/sessions")
    if not sessions_dir.is_dir():
        return sessions

    cutoff = datetime.now(timezone.utc).timestamp() - 86400
    for p in sorted(sessions_dir.rglob("*")):
        if not p.is_file():
            continue
        try:
            mtime = p.stat().st_mtime
            if mtime < cutoff:
                continue
            sessions.append({
                "source": str(p),
                "session_id": p.stem,
                "timestamp": datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat(),
                "model": "browseros",
            })
        except Exception:
            continue
    return sessions


def discover_gemini_sessions() -> list:
    """Discover Gemini/antigravity sessions."""
    sessions = []
    base = Path("C:/Users/asus/.gemini/antigravity")
    if not base.is_dir():
        return sessions

    cutoff = datetime.now(timezone.utc).timestamp() - 86400
    # Look for conversation/annotation files
    for p in sorted(base.rglob("*")):
        if not p.is_file() or p.suffix not in (".json", ".pbtxt", ".md"):
            continue
        try:
            mtime = p.stat().st_mtime
            if mtime < cutoff:
                continue
            sessions.append({
                "source": str(p),
                "session_id": p.stem,
                "timestamp": datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat(),
                "model": "gemini",
            })
        except Exception:
            continue
    return sessions


# ── Data builders ───────────────────────────────────────────────────────────

def build_session_data(agent_id: str, real_sessions: list) -> dict:
    """Build session data dict for an agent. Uses real data if available, else sample."""
    if real_sessions:
        latest = real_sessions[-1]
        return {
            "session_id": latest.get("session_id", f"real-{agent_id}"),
            "started_at": latest.get("timestamp", datetime.now(timezone.utc).isoformat()),
            "ended_at": datetime.now(timezone.utc).isoformat(),
            "status": "active",
            "summary": f"Recent activity discovered from {latest.get('source', 'unknown')}",
            "key_events": f"Discovered {len(real_sessions)} recent session(s) for {agent_id}",
            "actions_taken": "Synced real session data from agent data store",
            "decisions_made": "None recorded in this sync",
            "next_steps": "Continue monitoring for new sessions",
        }
    else:
        now = datetime.now(timezone.utc)
        return {
            "session_id": f"sample-{now.strftime('%Y%m%d-%H%M%S')}",
            "started_at": now.isoformat(),
            "ended_at": now.isoformat(),
            "status": "active",
            "summary": f"Sample sync for {agent_id} — no real session data available",
            "key_events": "No recent activity found in agent data stores",
            "actions_taken": "Generated sample session entry for vault continuity",
            "decisions_made": "Use sample data until real sessions are available",
            "next_steps": "Check agent logs for recent activity on next sync",
        }


def build_memory_data(agent_id: str, real_sessions: list) -> dict:
    """Build memory data dict for an agent."""
    now = datetime.now(timezone.utc)
    if real_sessions:
        latest = real_sessions[-1]
        return {
            "memory_type": "episodic",
            "created_at": latest.get("timestamp", now.isoformat()),
            "importance": "medium",
            "content": f"Recent activity from {agent_id}: {latest.get('model', 'unknown')} session {latest.get('session_id', 'unknown')}",
            "related_sessions": latest.get("session_id", ""),
            "related_projects": "",
        }
    else:
        return {
            "memory_type": "episodic",
            "created_at": now.isoformat(),
            "importance": "low",
            "content": f"No recent memory events for {agent_id} during this sync window",
            "related_sessions": "",
            "related_projects": "",
        }


# ── Sync runner ─────────────────────────────────────────────────────────────

def run_sync(agent_id: str, session_data: dict, memory_data: dict, vault_path: Path, dry_run: bool = False) -> bool:
    """Run sync-to-obsidian.py for a single agent."""
    script = vault_path / "scripts" / "sync-to-obsidian.py"
    if not script.is_file():
        print(f"[ERROR] sync script not found: {script}", file=sys.stderr)
        return False

    cmd = [
        sys.executable,
        str(script),
        "--agent-id", agent_id,
        "--session-data", json.dumps(session_data),
        "--project-context", json.dumps({}),
        "--vault-path", str(vault_path),
    ]

    if dry_run:
        print(f"[DRY-RUN] Would run: {' '.join(cmd)}")
        return True

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            cwd=str(vault_path / "scripts"),
        )
        if result.returncode != 0:
            print(f"[WARN] sync-to-obsidian.py returned {result.returncode} for {agent_id}", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
            # Don't fail the whole run for one agent
        else:
            print(f"[OK] {agent_id}: {result.stdout.strip()}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to run sync for {agent_id}: {e}", file=sys.stderr)
        return False


# ── Main ────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="Master sync for Obsidian AI Memory vault")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without executing")
    parser.add_argument("--agent-id", help="Sync only this agent")
    parser.add_argument("--vault-path", default=str(VAULT_ROOT), help="Override vault root path")
    args = parser.parse_args()

    vault_path = Path(args.vault_path).resolve()
    agents_to_sync = [args.agent_id] if args.agent_id else KNOWN_AGENTS

    # Discover real session data
    discoverers = {
        "hermes-agent": discover_hermes_sessions,
        "claude-code": discover_claude_sessions,
        "codex": discover_codex_sessions,
        "browseros": discover_browseros_sessions,
        "gemini": discover_gemini_sessions,
        "system": lambda: [],  # System agent has no external session store
    }

    all_ok = True
    print(f"[INFO] Vault: {vault_path}")
    print(f"[INFO] Agents to sync: {', '.join(agents_to_sync)}")

    for agent_id in agents_to_sync:
        if agent_id not in KNOWN_AGENTS:
            print(f"[WARN] Unknown agent ID: {agent_id}, skipping", file=sys.stderr)
            continue

        discoverer = discoverers.get(agent_id, lambda: [])
        real_sessions = discoverer()

        session_data = build_session_data(agent_id, real_sessions)
        memory_data = build_memory_data(agent_id, real_sessions)

        if real_sessions:
            print(f"[INFO] {agent_id}: found {len(real_sessions)} real session(s)")
        else:
            print(f"[INFO] {agent_id}: no real data, using sample data")

        ok = run_sync(agent_id, session_data, memory_data, vault_path, args.dry_run)
        if not ok:
            all_ok = False

    if all_ok:
        print("[INFO] All agents synced successfully.")
        return 0
    else:
        print("[WARN] Some agents had sync issues.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
