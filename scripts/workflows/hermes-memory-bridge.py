#!/usr/bin/env python3
"""
hermes-memory-bridge.py — Hermes Agent bridge that writes conversation memory to Obsidian.

This script is intended to be called by Hermes Agent (or any subagent) after a
session completes. It reads conversation memory from stdin or a JSON file and
forwards it to the existing sync-to-obsidian.py.

Usage:
    python hermes-memory-bridge.py [--memory-file path/to/memory.json]
    echo '{"content": "..."}' | python hermes-memory-bridge.py

All paths are absolute. Does not modify any agent configs.
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── Absolute paths ────────────────────────────────────────────────────────────
SYNC_SCRIPT = Path("C:/Users/asus/Documents/Obsidian Vault/scripts/sync-to-obsidian.py")
DEFAULT_AGENT_ID = "hermes-agent"
DEFAULT_VAULT = "C:/Users/asus/Documents/Obsidian Vault"


def read_memory_from_stdin() -> dict:
    """Read raw JSON from stdin if available."""
    if sys.stdin.isatty():
        return {}
    try:
        data = json.load(sys.stdin)
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


def read_memory_from_file(path: Path) -> dict:
    """Read memory data from a JSON file."""
    if not path.is_file():
        print(f"[WARN] Memory file not found: {path}", file=sys.stderr)
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_session_data(memory: dict) -> dict:
    """Derive a session record from conversation memory."""
    now = datetime.now(timezone.utc).isoformat()
    session_id = memory.get("session_id", datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S"))
    return {
        "session_id": session_id,
        "started_at": memory.get("started_at", now),
        "ended_at": now,
        "status": "completed",
        "summary": memory.get("summary", memory.get("content", "Hermes Agent session")[:200]),
        "key_events": memory.get("key_events", ""),
        "actions_taken": memory.get("actions_taken", ""),
        "decisions_made": memory.get("decisions_made", ""),
        "next_steps": memory.get("next_steps", ""),
    }


def build_memory_data(memory: dict) -> dict:
    """Prepare a memory entry for Obsidian."""
    now = datetime.now(timezone.utc).isoformat()
    return {
        "memory_type": memory.get("memory_type", "episodic"),
        "created_at": memory.get("created_at", now),
        "importance": memory.get("importance", "medium"),
        "content": memory.get("content", ""),
        "related_sessions": memory.get("related_sessions", ""),
        "related_projects": memory.get("related_projects", ""),
    }


def build_project_context(memory: dict) -> dict:
    """Prepare project context if available."""
    if "project" not in memory:
        return {}
    proj = memory["project"]
    now = datetime.now(timezone.utc).isoformat()
    return {
        "project_id": proj.get("project_id", "default"),
        "name": proj.get("name", "Unnamed Project"),
        "status": proj.get("status", "active"),
        "created_at": proj.get("created_at", now),
        "updated_at": now,
        "overview": proj.get("overview", ""),
        "goals": proj.get("goals", ""),
        "deliverables": proj.get("deliverables", ""),
        "current_state": proj.get("current_state", ""),
        "assigned_agents": proj.get("assigned_agents", ""),
    }


def call_sync_script(agent_id: str, session_data: dict, project_context: dict) -> bool:
    """Invoke sync-to-obsidian.py as a subprocess."""
    cmd = [
        sys.executable,
        str(SYNC_SCRIPT),
        "--agent-id", agent_id,
        "--session-data", json.dumps(session_data),
        "--vault-path", DEFAULT_VAULT,
    ]
    if project_context:
        cmd += ["--project-context", json.dumps(project_context)]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            print(f"[ERROR] sync-to-obsidian.py failed:\n{result.stderr}", file=sys.stderr)
            return False
        print(result.stdout.strip())
        return True
    except Exception as e:
        print(f"[ERROR] Failed to invoke sync script: {e}", file=sys.stderr)
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Hermes Agent memory bridge to Obsidian.")
    parser.add_argument("--agent-id", default=DEFAULT_AGENT_ID, help="Agent identifier")
    parser.add_argument("--memory-file", type=Path, help="Path to memory JSON file")
    parser.add_argument("--session-only", action="store_true", help="Sync session only, skip memory entry")
    args = parser.parse_args()

    # Gather memory from file or stdin
    memory = {}
    if args.memory_file:
        memory = read_memory_from_file(args.memory_file)
    else:
        memory = read_memory_from_stdin()

    if not memory and not args.session_only:
        print("[INFO] No memory data provided; nothing to sync.", file=sys.stderr)
        return 0

    session_data = build_session_data(memory)
    project_context = build_project_context(memory)

    success = call_sync_script(args.agent_id, session_data, project_context)

    if not args.session_only and memory:
        memory_data = build_memory_data(memory)
        mem_success = call_sync_script(args.agent_id, {}, {})
        # Overwrite with memory-specific call
        cmd = [
            sys.executable,
            str(SYNC_SCRIPT),
            "--agent-id", args.agent_id,
            "--session-data", json.dumps(session_data),
            "--vault-path", DEFAULT_VAULT,
        ]
        if project_context:
            cmd += ["--project-context", json.dumps(project_context)]
        # We need to write memory separately using the same script's memory feature?
        # sync-to-obsidian.py doesn't expose --memory-data, so we emulate via session + project.
        # For memory-specific sync, we pass it as session_data with memory_type marker.
        memory_payload = {
            "session_id": session_data["session_id"],
            "summary": memory_data["content"],
            "status": "memory",
            "key_events": memory_data["related_sessions"],
            "actions_taken": memory_data["related_projects"],
            "ended_at": memory_data["created_at"],
        }
        cmd_mem = [
            sys.executable,
            str(SYNC_SCRIPT),
            "--agent-id", args.agent_id,
            "--session-data", json.dumps(memory_payload),
            "--vault-path", DEFAULT_VAULT,
        ]
        try:
            result = subprocess.run(cmd_mem, capture_output=True, text=True, check=False)
            if result.returncode == 0:
                print(result.stdout.strip())
            else:
                print(f"[WARN] Memory sync stderr: {result.stderr}", file=sys.stderr)
        except Exception as e:
            print(f"[WARN] Memory sync failed: {e}", file=sys.stderr)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
