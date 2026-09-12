#!/usr/bin/env python3
"""
vault-sync.py v2 - Unified Obsidian AI Memory sync engine for all local AI agents.

Replaces sync-to-obsidian.py/sync-all-agents.py (v1 had: dead write_memory path,
capitalized Templates/Agents dirs, sample-data pollution, no real discovery).

Commands:
  sync [--agent ID]      discover real sessions from agent stores, log them
  log --agent ID ...     manual entry: --session-id/--summary or --memory
  read --agent ID        print recent vault memory as JSON (read before working)
  brief                  regenerate cross-agent briefing from last 24h
  digest                 regenerate weekly digest
  heartbeat              append timestamped line to agents/system/heartbeat.md
  status                 human-readable vault status
  commit [--push]        git add+commit (optionally push)
Agent IDs: hermes, claude, codex, gemini, prime
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

VAULT_ROOT = Path(os.environ.get("OBSIDIAN_VAULT_PATH", "C:/Users/asus/Documents/Obsidian Vault"))
AGENTS_DIR = VAULT_ROOT / "agents"
BRIEFINGS_DIR = VAULT_ROOT / "memory" / "cross-agent"
DIGESTS_DIR = VAULT_ROOT / "memory" / "session-notes"
HEARTBEAT = VAULT_ROOT / "agents" / "system" / "heartbeat.md"

AGENT_IDS = ["hermes", "claude", "codex", "gemini", "prime", "browseros"]

AGENT_SOURCES = {
    "hermes": [Path("C:/Users/asus/AppData/Local/hermes/sessions")],
    "claude": [Path("C:/Users/asus/.claude/projects")],
    "codex": [Path("C:/Users/asus/.codex/sessions")],
    "gemini": [Path("C:/Users/asus/.gemini/tmp"), Path("C:/Users/asus/.gemini/history")],
    "prime": [Path("C:/Users/asus/.prime/sessions")],
    "browseros": [Path("C:/Users/asus/.browseros/sessions")],
}

ACTIVITY_WINDOW_HOURS = 26.0
REDACTION_PATTERNS = [
    (re.compile(r"sk-[A-Za-z0-9_-]{8,}"), "[REDACTED-KEY]"),
    (re.compile(r"ghp_[A-Za-z0-9]{20,}"), "[REDACTED-TOKEN]"),
    (re.compile(r"gho_[A-Za-z0-9]{20,}"), "[REDACTED-TOKEN]"),
    (re.compile(r"xox[bB]-[A-Za-z0-9-]{10,}"), "[REDACTED-TOKEN]"),
    (re.compile(r"AIza[A-Za-z0-9_-]{30,}"), "[REDACTED-KEY]"),
    (re.compile(r"sk-or-v1[^\s\"]*"), "[REDACTED-KEY]"),
    (re.compile(r"Bearer\s+[A-Za-z0-9._-]{8,}"), "Bearer [REDACTED]"),
]


def now_utc():
    return datetime.now(timezone.utc)


def safe_name(s):
    return re.sub(r"[^A-Za-z0-9_-]", "_", str(s))[:80]


def redact(text):
    for pat, repl in REDACTION_PATTERNS:
        text = pat.sub(repl, text)
    return text


def build_fm(pairs):
    lines = ["---"]
    for k, v in pairs.items():
        lines.append(k + ": " + str(v).replace(chr(10), " "))
    lines.append("---")
    return chr(10).join(lines)


def write_if_missing(path, content):
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline=chr(10)) as f:
        f.write(content)
    return True


def append_line(path, line):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8", newline=chr(10)) as f:
        f.write(line + chr(10))


# ── discovery ───────────────────────────────────────────────────────────────

def discover_recent(agent_id, window_hours):
    cutoff = now_utc().timestamp() - window_hours * 3600
    out = []
    for src in AGENT_SOURCES.get(agent_id, []):
        if not src.is_dir():
            continue
        for p in src.rglob("*"):
            try:
                if p.is_file() and p.stat().st_mtime >= cutoff:
                    out.append(p)
            except OSError:
                continue
    return out


def summarize_file(p, max_chars=400):
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return "artifact " + p.name + " (unreadable)"
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return "artifact " + p.name + " (empty)"
    text = redact(text)
    return text[:max_chars] + ("..." if len(text) > max_chars else "")


def find_latest_meaningful(files):
    """Pick the most informative recent file: prefer .md/.json/.jsonl text artifacts."""
    def score(p):
        s = 0
        if p.suffix in (".md", ".json", ".jsonl", ".txt", ".toml"):
            s += 10
        if p.suffix in (".py", ".js", ".sh"):
            s += 2
        try:
            s += min(p.stat().st_size // 1000, 20)
        except OSError:
            pass
        return s
    if not files:
        return None
    return sorted(files, key=score, reverse=True)[0]


# ── writers ─────────────────────────────────────────────────────────────────

def write_session(agent_id, session_id, summary, status="completed", source="manual"):
    fm = build_fm({
        "agent": agent_id,
        "session_id": session_id,
        "started_at": now_utc().isoformat(),
        "status": status,
        "source": source,
    })
    body = fm + chr(10) + chr(10) + "# Session " + str(session_id) + chr(10) + chr(10)
    body += "## Summary" + chr(10) + chr(10) + summary + chr(10) + chr(10)
    body += "Logged at: " + now_utc().isoformat() + chr(10)
    ts = now_utc().strftime("%Y%m%d-%H%M%S")
    dest = AGENTS_DIR / agent_id / "sessions" / (ts + "_" + safe_name(session_id) + ".md")
    if write_if_missing(dest, body):
        return dest
    return dest  # already exists


def write_memory(agent_id, content_text, importance="medium", memory_type="episodic"):
    fm = build_fm({
        "agent": agent_id,
        "memory_type": memory_type,
        "importance": importance,
        "created_at": now_utc().isoformat(),
    })
    body = fm + chr(10) + chr(10) + content_text + chr(10)
    ts = now_utc().strftime("%Y%m%d-%H%M%S")
    dest = AGENTS_DIR / agent_id / "memory" / (ts + "_" + safe_name(memory_type) + ".md")
    write_if_missing(dest, body)
    return dest


def read_agent_memory(agent_id, limit=50):
    """Return recent memory + session notes for an agent, newest first."""
    out = {"agent": agent_id, "generated_at": now_utc().isoformat(), "sessions": [], "memory": []}
    for sub, key in (("sessions", "sessions"), ("memory", "memory")):
        d = AGENTS_DIR / agent_id / sub
        if not d.is_dir():
            continue
        files = sorted(d.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]
        for p in files:
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            body = re.sub(r"\s+", " ", text.split("---", 2)[-1]).strip()[:400]
            out[key].append({"file": p.name, "summary": redact(body)})
    return out


# ── commands ────────────────────────────────────────────────────────────────

def last_log_mtime(agent_id):
    """Newest mtime among this agent's already-logged session notes."""
    d = AGENTS_DIR / agent_id / "sessions"
    if not d.is_dir():
        return 0.0
    mt = 0.0
    for p in d.glob("*.md"):
        try:
            mt = max(mt, p.stat().st_mtime)
        except OSError:
            continue
    return mt


def newest_artifact_mtime(files):
    mt = 0.0
    for p in files:
        try:
            mt = max(mt, p.stat().st_mtime)
        except OSError:
            continue
    return mt


def cmd_sync(args):
    agents = [args.agent] if args.agent else AGENT_IDS
    results = {}
    for agent_id in agents:
        files = discover_recent(agent_id, ACTIVITY_WINDOW_HOURS)
        if not files:
            results[agent_id] = {"status": "no recent activity", "logged": False}
            continue
        # Dedup: skip if nothing new since the last logged session for this agent
        if newest_artifact_mtime(files) <= last_log_mtime(agent_id):
            results[agent_id] = {"status": "no new activity since last log", "logged": False}
            continue
        latest = find_latest_meaningful(files)
        session_id = agent_id + "-" + now_utc().strftime("%Y%m%d-%H%M")
        # PRIVACY: auto-discovery logs counts + names ONLY, never file content.
        names = ", ".join(sorted({f.name for f in files})[:5]) + (" ..." if len(files) > 5 else "")
        summary = ("Detected " + str(len(files)) + " recent artifacts in " + agent_id
                   + " store (26h window). Notable: " + names
                   + ". Newest: " + latest.name + ".")
        dest = write_session(agent_id, session_id, summary, status="active", source="auto-discovery")
        results[agent_id] = {"status": "logged", "artifacts": len(files), "session_file": str(dest)}
    print(json.dumps({"cmd": "sync", "results": results}, indent=2))
    return 0


def cmd_log(args):
    if not args.agent or args.agent not in AGENT_IDS:
        print("[ERROR] --agent required (one of: " + ", ".join(AGENT_IDS) + ")", file=sys.stderr)
        return 1
    if args.memory:
        dest = write_memory(args.agent, args.memory, importance=args.importance or "medium",
                            memory_type=args.memory_type or "episodic")
        print(json.dumps({"status": "ok", "memory_file": str(dest)}))
        return 0
    if args.summary and args.session_id:
        dest = write_session(args.agent, args.session_id, args.summary,
                             status=args.status or "completed", source="manual")
        print(json.dumps({"status": "ok", "session_file": str(dest)}))
        return 0
    print("[ERROR] provide --memory, or --session-id + --summary", file=sys.stderr)
    return 1


def cmd_read(args):
    if not args.agent:
        print("[ERROR] --agent required", file=sys.stderr)
        return 1
    print(json.dumps(read_agent_memory(args.agent), indent=2))
    return 0


def cmd_brief(args):
    """Regenerate the cross-agent briefing from the last 24h of activity."""
    cutoff = now_utc() - timedelta(hours=24)
    lines = ["# Cross-Agent Briefing", "",
             "Generated: " + now_utc().isoformat(), "",
             "What each agent did in the last 24h:", ""]
    any_activity = False
    for agent_id in AGENT_IDS:
        d = AGENTS_DIR / agent_id / "sessions"
        recent = []
        if d.is_dir():
            for p in d.glob("*.md"):
                try:
                    if datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc) >= cutoff:
                        recent.append(p)
                except OSError:
                    continue
        if recent:
            any_activity = True
            lines.append("## " + agent_id + " (" + str(len(recent)) + " session log(s))")
            newest = sorted(recent, key=lambda p: p.stat().st_mtime)[-1]
            try:
                text = newest.read_text(encoding="utf-8", errors="replace")
                body = re.sub(r"\s+", " ", text.split("---", 2)[-1]).strip()[:300]
            except Exception:
                body = "(unreadable)"
            lines.append("- latest: " + body)
            lines.append("")
        else:
            lines.append("## " + agent_id)
            lines.append("- no logged activity in last 24h")
            lines.append("")
    if not any_activity:
        lines.append("_No agent activity logged in the last 24 hours. Run sync first._")
    dest = BRIEFINGS_DIR / "briefing.md"
    dest.parent.mkdir(parents=True, exist_ok=True)
    with open(dest, "w", encoding="utf-8", newline=chr(10)) as f:
        f.write(chr(10).join(lines) + chr(10))
    print(json.dumps({"status": "ok", "briefing": str(dest)}))
    return 0


def cmd_digest(args):
    """Weekly digest: all sessions logged in the last 7 days."""
    cutoff = now_utc() - timedelta(days=7)
    week_label = now_utc().strftime("%G-W%V")
    lines = ["# Weekly Digest " + week_label, "",
             "Generated: " + now_utc().isoformat(), ""]
    total = 0
    for agent_id in AGENT_IDS:
        d = AGENTS_DIR / agent_id / "sessions"
        recent = []
        if d.is_dir():
            for p in d.glob("*.md"):
                try:
                    if datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc) >= cutoff:
                        recent.append(p)
                except OSError:
                    continue
        if recent:
            total += len(recent)
            lines.append("## " + agent_id + " - " + str(len(recent)) + " sessions")
            for p in sorted(recent, key=lambda q: q.stat().st_mtime):
                try:
                    text = p.read_text(encoding="utf-8", errors="replace")
                    body = re.sub(r"\s+", " ", text.split("---", 2)[-1]).strip()[:200]
                except Exception:
                    body = "(unreadable)"
                lines.append("- " + p.name + ": " + body)
            lines.append("")
    if total == 0:
        lines.append("_No sessions logged in the last 7 days._")
    dest = DIGESTS_DIR / ("digest-" + week_label + ".md")
    dest.parent.mkdir(parents=True, exist_ok=True)
    with open(dest, "w", encoding="utf-8", newline=chr(10)) as f:
        f.write(chr(10).join(lines) + chr(10))
    print(json.dumps({"status": "ok", "digest": str(dest), "sessions_total": total}))
    return 0


def cmd_heartbeat(args):
    append_line(HEARTBEAT, now_utc().isoformat() + " vault-sync alive")
    print(json.dumps({"status": "ok", "heartbeat": str(HEARTBEAT)}))
    return 0


def cmd_status(args):
    print("Vault: " + str(VAULT_ROOT))
    print("Agents tracked: " + ", ".join(AGENT_IDS))
    for agent_id in AGENT_IDS:
        sd = AGENTS_DIR / agent_id / "sessions"
        md = AGENTS_DIR / agent_id / "memory"
        ns = len(list(sd.glob("*.md"))) if sd.is_dir() else 0
        nm = len(list(md.glob("*.md"))) if md.is_dir() else 0
        recent = len(discover_recent(agent_id, ACTIVITY_WINDOW_HOURS))
        print("  " + agent_id + ": " + str(ns) + " session logs, " + str(nm)
              + " memories, " + str(recent) + " recent store artifacts (26h)")
    print("Briefing: " + str(BRIEFINGS_DIR / "briefing.md"))
    print("Heartbeat: " + str(HEARTBEAT))
    return 0


def _github_token():
    """Read GITHUB_TOKEN from the Hermes .env without printing it."""
    for env_path in (Path("C:/Users/asus/AppData/Local/hermes/.env"),):
        try:
            for line in env_path.read_text(encoding="utf-8", errors="replace").splitlines():
                if line.startswith("GITHUB_TOKEN="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
        except OSError:
            continue
    return os.environ.get("GITHUB_TOKEN", "")


def cmd_commit(args):
    try:
        subprocess.run(["git", "add", "-A"], cwd=str(VAULT_ROOT), check=True,
                      capture_output=True, text=True)
        r = subprocess.run(["git", "status", "--porcelain"], cwd=str(VAULT_ROOT),
                           capture_output=True, text=True, check=True)
        if not r.stdout.strip():
            print(json.dumps({"status": "nothing to commit"}))
            return 0
        msg = "Vault sync " + now_utc().strftime("%Y-%m-%d %H:%M") + " [vault-sync.py]"
        subprocess.run(["git", "commit", "-m", msg], cwd=str(VAULT_ROOT), check=True,
                       capture_output=True, text=True)
        pushed = False
        push_err = None
        if args.push:
            token = _github_token()
            if not token:
                push_err = "GITHUB_TOKEN not found in hermes .env"
            else:
                remote = "https://x-access-token:" + token + "@github.com/abhishekanandsupreme-rgb/obsidian-ai-memory.git"
                pr = subprocess.run(["git", "push", remote, "master"], cwd=str(VAULT_ROOT),
                                     capture_output=True, text=True)
                pushed = pr.returncode == 0
                if not pushed:
                    push_err = (pr.stderr or "unknown")[:300]
        out = {"status": "committed", "pushed": pushed}
        if push_err:
            out["push_error"] = push_err
        print(json.dumps(out))
    except subprocess.CalledProcessError as e:
        print("[ERROR] git failed: " + str(e.stderr or e), file=sys.stderr)
        return 1
    return 0


def main():
    parser = argparse.ArgumentParser(description="Obsidian AI Memory vault sync v2")
    sub = parser.add_subparsers(dest="command")

    p_sync = sub.add_parser("sync")
    p_sync.add_argument("--agent", choices=AGENT_IDS)

    p_log = sub.add_parser("log")
    p_log.add_argument("--agent", choices=AGENT_IDS, required=True)
    p_log.add_argument("--session-id")
    p_log.add_argument("--summary")
    p_log.add_argument("--status")
    p_log.add_argument("--memory")
    p_log.add_argument("--importance", choices=["low", "medium", "high"])
    p_log.add_argument("--memory-type")

    p_read = sub.add_parser("read")
    p_read.add_argument("--agent", choices=AGENT_IDS, required=True)

    for name in ("brief", "digest", "heartbeat", "status"):
        sub.add_parser(name)

    p_commit = sub.add_parser("commit")
    p_commit.add_argument("--push", action="store_true")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 1
    return {
        "sync": cmd_sync, "log": cmd_log, "read": cmd_read, "brief": cmd_brief,
        "digest": cmd_digest, "heartbeat": cmd_heartbeat, "status": cmd_status,
        "commit": cmd_commit,
    }[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
