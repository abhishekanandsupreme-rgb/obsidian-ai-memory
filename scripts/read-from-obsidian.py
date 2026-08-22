#!/usr/bin/env python3
"""
read-from-obsidian.py — Read agent memory from the Obsidian vault and output JSON for agents.

Usage:
    python read-from-obsidian.py --agent-id <id> [--type sessions|memory|all]
    python read-from-obsidian.py --project-id <id>
    python read-from-obsidian.py --inbox

Outputs JSON to stdout describing what was found.
Cross-platform: uses pathlib and absolute paths.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from datetime import datetime, timezone

# ── Absolute vault path ──────────────────────────────────────────────────────
VAULT_ROOT = Path("C:/Users/asus/Documents/Obsidian Vault")
TEMPLATES_DIR = VAULT_ROOT / "Templates"
AGENTS_DIR = VAULT_ROOT / "Agents"
PROJECTS_DIR = VAULT_ROOT / "Projects"
INBOX_DIR = VAULT_ROOT / "Inbox"


def parse_frontmatter(text: str) -> dict:
    """Parse YAML-like frontmatter from markdown. Returns a dict."""
    frontmatter = {}
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            block = text[3:end].strip()
            for line in block.splitlines():
                if ":" in line:
                    key, _, val = line.partition(":")
                    frontmatter[key.strip()] = val.strip()
    return frontmatter


def strip_frontmatter(text: str) -> str:
    """Remove frontmatter and return body text."""
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            return text[end + 3 :].strip()
    return text.strip()


def read_markdown_file(path: Path) -> dict:
    """Read a markdown file and return frontmatter + body."""
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    fm = parse_frontmatter(text)
    body = strip_frontmatter(text)
    return {"frontmatter": fm, "body": body, "path": str(path)}


def collect_sessions(agent_id: str) -> list:
    agent_sessions_dir = AGENTS_DIR / agent_id / "sessions"
    if not agent_sessions_dir.is_dir():
        return []
    sessions = []
    for p in sorted(agent_sessions_dir.glob("*.md")):
        try:
            data = read_markdown_file(p)
            sessions.append(data)
        except Exception as e:
            print(f"[WARN] Could not read session {p}: {e}", file=sys.stderr)
    return sessions


def collect_memory(agent_id: str) -> list:
    agent_memory_dir = AGENTS_DIR / agent_id / "memory"
    if not agent_memory_dir.is_dir():
        return []
    memories = []
    for p in sorted(agent_memory_dir.glob("*.md")):
        try:
            data = read_markdown_file(p)
            memories.append(data)
        except Exception as e:
            print(f"[WARN] Could not read memory {p}: {e}", file=sys.stderr)
    return memories


def collect_projects() -> list:
    if not PROJECTS_DIR.is_dir():
        return []
    projects = []
    for p in sorted(PROJECTS_DIR.glob("*.md")):
        try:
            data = read_markdown_file(p)
            projects.append(data)
        except Exception as e:
            print(f"[WARN] Could not read project {p}: {e}", file=sys.stderr)
    return projects


def collect_inbox() -> list:
    if not INBOX_DIR.is_dir():
        return []
    items = []
    for p in sorted(INBOX_DIR.glob("*.md")):
        try:
            data = read_markdown_file(p)
            items.append(data)
        except Exception as e:
            print(f"[WARN] Could not read inbox item {p}: {e}", file=sys.stderr)
    return items


def summarize_body(body: str, max_chars: int = 500) -> str:
    """Return a truncated, whitespace-collapsed body summary."""
    text = re.sub(r'\s+', ' ', body).strip()
    if len(text) > max_chars:
        text = text[:max_chars] + "..."
    return text


def build_output(agent_id: str, mode: str) -> dict:
    result = {
        "agent_id": agent_id,
        "vault_path": str(VAULT_ROOT),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    if mode in ("sessions", "all"):
        sessions = collect_sessions(agent_id)
        result["sessions"] = [
            {
                "path": s["path"],
                "frontmatter": s["frontmatter"],
                "summary": summarize_body(s["body"]),
            }
            for s in sessions
        ]

    if mode in ("memory", "all"):
        memories = collect_memory(agent_id)
        result["memory"] = [
            {
                "path": m["path"],
                "frontmatter": m["frontmatter"],
                "summary": summarize_body(m["body"]),
            }
            for m in memories
        ]

    if mode == "all":
        result["projects"] = [
            {
                "path": p["path"],
                "frontmatter": p["frontmatter"],
                "summary": summarize_body(p["body"]),
            }
            for p in collect_projects()
        ]
        result["inbox"] = [
            {
                "path": i["path"],
                "frontmatter": i["frontmatter"],
                "summary": summarize_body(i["body"]),
            }
            for i in collect_inbox()
        ]

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Read agent memory from the Obsidian vault.")
    parser.add_argument("--agent-id", required=False, help="Agent identifier")
    parser.add_argument("--project-id", required=False, help="Project identifier (filters projects)")
    parser.add_argument("--inbox", action="store_true", help="Read inbox items")
    parser.add_argument("--type", choices=["sessions", "memory", "all"], default="all", help="What to read")
    parser.add_argument("--vault-path", required=False, default=str(VAULT_ROOT), help="Override vault root path")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    args = parser.parse_args()

    global VAULT_ROOT, TEMPLATES_DIR, AGENTS_DIR, PROJECTS_DIR, INBOX_DIR
    VAULT_ROOT = Path(args.vault_path).resolve()
    TEMPLATES_DIR = VAULT_ROOT / "Templates"
    AGENTS_DIR = VAULT_ROOT / "Agents"
    PROJECTS_DIR = VAULT_ROOT / "Projects"
    INBOX_DIR = VAULT_ROOT / "Inbox"

    if not args.agent_id and not args.project_id and not args.inbox:
        print("[ERROR] Must provide --agent-id, --project-id, or --inbox", file=sys.stderr)
        return 1

    output = {}

    if args.agent_id:
        output = build_output(args.agent_id, args.type)

    if args.project_id:
        projects = collect_projects()
        filtered = []
        for p in projects:
            fm = p["frontmatter"]
            if fm.get("project_id", "") == args.project_id or args.project_id in p["path"]:
                filtered.append(p)
        output = {
            "project_id": args.project_id,
            "vault_path": str(VAULT_ROOT),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "projects": [
                {
                    "path": p["path"],
                    "frontmatter": p["frontmatter"],
                    "summary": summarize_body(p["body"]),
                }
                for p in filtered
            ],
        }

    if args.inbox:
        inbox_items = collect_inbox()
        output = {
            "vault_path": str(VAULT_ROOT),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "inbox": [
                {
                    "path": i["path"],
                    "frontmatter": i["frontmatter"],
                    "summary": summarize_body(i["body"]),
                }
                for i in inbox_items
            ],
        }

    indent = 2 if args.pretty else None
    print(json.dumps(output, indent=indent, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
