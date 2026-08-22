#!/usr/bin/env python3
"""
sync-to-obsidian.py — Write agent session data and project context into the Obsidian vault.

Usage:
    python sync-to-obsidian.py --agent-id <id> --session-data <json_or_path> --project-context <json_or_path>
    python sync-to-obsidian.py --agent-id <id> --session-data <json_or_path>
    python sync-to-obsidian.py --project-context <json_or_path> --agent-id <id>

All paths are absolute. Does not modify existing files.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── Absolute vault path ──────────────────────────────────────────────────────
VAULT_ROOT = Path("C:/Users/asus/Documents/Obsidian Vault")
TEMPLATES_DIR = VAULT_ROOT / "Templates"
AGENTS_DIR = VAULT_ROOT / "Agents"
PROJECTS_DIR = VAULT_ROOT / "Projects"
INBOX_DIR = VAULT_ROOT / "Inbox"


def parse_json_arg(value: str) -> dict:
    """Accept either a raw JSON string or a path to a JSON file."""
    value = value.strip()
    if not value:
        return {}
    # Try parsing as raw JSON first
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        pass
    # Fall back to file path
    p = Path(value)
    if p.is_file():
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    raise ValueError(f"Unable to parse JSON from argument: {value!r}")


def render_template(template_text: str, context: dict) -> str:
    """Simple {{key}} template renderer without external dependencies."""
    result = template_text
    for key, val in context.items():
        placeholder = "{{" + str(key) + "}}"
        result = result.replace(placeholder, str(val))
    return result


def ensure_dirs(*dirs: Path) -> None:
    """Create directories if they do not exist. Never touches existing content."""
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)


def load_template(name: str) -> str:
    path = TEMPLATES_DIR / name
    if not path.is_file():
        raise FileNotFoundError(f"Template not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_if_missing(path: Path, content: str) -> bool:
    """Write content only if the file does not already exist. Returns True if written."""
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return True


def write_session(agent_id: str, session_data: dict) -> Path:
    """Write a session markdown file using the session template."""
    session_id = session_data.get("session_id", datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S"))
    started_at = session_data.get("started_at", datetime.now(timezone.utc).isoformat())
    ended_at = session_data.get("ended_at", "")
    status = session_data.get("status", "active")
    summary = session_data.get("summary", "")
    key_events = session_data.get("key_events", "")
    actions = session_data.get("actions_taken", "")
    decisions = session_data.get("decisions_made", "")
    next_steps = session_data.get("next_steps", "")

    template = load_template("session-template.md")
    context = {
        "agent_id": agent_id,
        "session_id": session_id,
        "started_at": started_at,
        "ended_at": ended_at,
        "status": status,
        "summary": summary,
        "key_events": key_events,
        "actions_taken": actions,
        "decisions_made": decisions,
        "next_steps": next_steps,
    }
    rendered = render_template(template, context)

    # Derive a safe filename
    safe_session_id = re.sub(r'[^A-Za-z0-9_\-]', '_', str(session_id))
    filename = f"{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}_{safe_session_id}.md"
    agent_sessions_dir = AGENTS_DIR / agent_id / "sessions"
    ensure_dirs(agent_sessions_dir)
    dest = agent_sessions_dir / filename

    written = write_if_missing(dest, rendered)
    if not written:
        print(f"[WARN] Session file already exists, skipping: {dest}", file=sys.stderr)
    return dest


def write_memory(agent_id: str, memory_data: dict) -> Path:
    """Append or create a memory entry using the memory template."""
    memory_type = memory_data.get("memory_type", "episodic")
    created_at = memory_data.get("created_at", datetime.now(timezone.utc).isoformat())
    importance = memory_data.get("importance", "medium")
    content = memory_data.get("content", "")
    context_sessions = memory_data.get("related_sessions", "")
    context_projects = memory_data.get("related_projects", "")

    template = load_template("memory-template.md")
    ctx = {
        "agent_id": agent_id,
        "memory_type": memory_type,
        "created_at": created_at,
        "importance": importance,
        "content": content,
        "related_sessions": context_sessions,
        "related_projects": context_projects,
    }
    rendered = render_template(template, ctx)

    agent_memory_dir = AGENTS_DIR / agent_id / "memory"
    ensure_dirs(agent_memory_dir)
    safe_type = re.sub(r'[^A-Za-z0-9_\-]', '_', memory_type)
    filename = f"{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}_{safe_type}.md"
    dest = agent_memory_dir / filename
    written = write_if_missing(dest, rendered)
    if not written:
        print(f"[WARN] Memory file already exists, skipping: {dest}", file=sys.stderr)
    return dest


def write_project(project_context: dict) -> Path:
    """Write or update a project markdown file using the project template."""
    project_id = project_context.get("project_id", "default")
    name = project_context.get("name", "Unnamed Project")
    status = project_context.get("status", "active")
    created_at = project_context.get("created_at", datetime.now(timezone.utc).isoformat())
    updated_at = datetime.now(timezone.utc).isoformat()
    overview = project_context.get("overview", "")
    goals = project_context.get("goals", "")
    deliverables = project_context.get("deliverables", "")
    current_state = project_context.get("current_state", "")
    assigned = project_context.get("assigned_agents", "")

    template = load_template("project-template.md")
    ctx = {
        "project_id": project_id,
        "name": name,
        "status": status,
        "created_at": created_at,
        "updated_at": updated_at,
        "overview": overview,
        "goals": goals,
        "deliverables": deliverables,
        "current_state": current_state,
        "assigned_agents": assigned,
    }
    rendered = render_template(template, ctx)

    # Use project_id as filename (sanitized)
    safe_name = re.sub(r'[^A-Za-z0-9_\-]', '_', str(name))
    filename = f"{project_id}_{safe_name}.md"
    ensure_dirs(PROJECTS_DIR)
    dest = PROJECTS_DIR / filename

    # For projects we allow updating if it already exists (overwrite with latest context)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with open(dest, "w", encoding="utf-8") as f:
        f.write(rendered)
    return dest


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync agent data into the Obsidian vault.")
    parser.add_argument("--agent-id", required=True, help="Unique agent identifier")
    parser.add_argument("--session-data", required=False, help="Session data as JSON string or path to JSON file")
    parser.add_argument("--project-context", required=False, help="Project context as JSON string or path to JSON file")
    parser.add_argument("--vault-path", required=False, default=str(VAULT_ROOT), help="Override vault root path")
    args = parser.parse_args()

    global VAULT_ROOT, TEMPLATES_DIR, AGENTS_DIR, PROJECTS_DIR, INBOX_DIR
    VAULT_ROOT = Path(args.vault_path).resolve()
    TEMPLATES_DIR = VAULT_ROOT / "Templates"
    AGENTS_DIR = VAULT_ROOT / "Agents"
    PROJECTS_DIR = VAULT_ROOT / "Projects"
    INBOX_DIR = VAULT_ROOT / "Inbox"

    # Ensure base dirs exist (idempotent)
    ensure_dirs(TEMPLATES_DIR, AGENTS_DIR, PROJECTS_DIR, INBOX_DIR)

    session_data = {}
    project_context = {}

    if args.session_data:
        session_data = parse_json_arg(args.session_data)

    if args.project_context:
        project_context = parse_json_arg(args.project_context)

    if not session_data and not project_context:
        print("[ERROR] Must provide at least --session-data or --project-context", file=sys.stderr)
        return 1

    results = {}

    if session_data:
        try:
            dest = write_session(args.agent_id, session_data)
            results["session_written"] = str(dest)
        except Exception as e:
            print(f"[ERROR] Failed to write session: {e}", file=sys.stderr)
            return 1

    if project_context:
        try:
            dest = write_project(project_context)
            results["project_written"] = str(dest)
        except Exception as e:
            print(f"[ERROR] Failed to write project: {e}", file=sys.stderr)
            return 1

    # Output summary as JSON
    print(json.dumps({"status": "success", "agent_id": args.agent_id, **results}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
