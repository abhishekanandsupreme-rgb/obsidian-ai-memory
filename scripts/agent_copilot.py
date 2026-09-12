import os
import sys
import json
import argparse
import requests
from pathlib import Path
from datetime import datetime, timezone

VAULT_ROOT = Path(__file__).resolve().parent.parent
AGENT_OS_URL = os.environ.get("AGENT_OS_URL", "http://127.0.0.1:8000")

def get_agent_os_status():
    try:
        r = requests.get(f"{AGENT_OS_URL}/api/status", timeout=5)
        if r.status_code == 200:
            return {"status": "online", "data": r.json()}
    except Exception as e:
        return {"status": "offline", "error": str(e)}
    return {"status": "unknown"}

def run_synthesis():
    sessions_dir = VAULT_ROOT / "agents"
    recent_sessions = []
    
    if sessions_dir.exists():
        for s_file in sessions_dir.glob("*/sessions/*.md"):
            try:
                txt = s_file.read_text(encoding="utf-8", errors="replace")
                agent_name = s_file.parent.parent.name
                recent_sessions.append({
                    "agent": agent_name,
                    "file": s_file.name,
                    "mtime": datetime.fromtimestamp(s_file.stat().st_mtime, tz=timezone.utc).isoformat(),
                    "snippet": "\n".join(txt.splitlines()[:15])
                })
            except Exception:
                pass

    recent_sessions.sort(key=lambda x: x["mtime"], reverse=True)
    top_sessions = recent_sessions[:10]

    synthesis_path = VAULT_ROOT / "memory" / "cross-agent" / "daily-synthesis.md"
    synthesis_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "---",
        "title: 'Daily Multi-Agent Neural Synthesis'",
        "type: memory-synthesis",
        f"updated_at: '{datetime.now(timezone.utc).isoformat()}'",
        "tags: [agent-memory, daily-synthesis, cross-agent]",
        "---",
        "",
        "# 🧠 Daily Multi-Agent Neural Synthesis",
        f"> **Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
        "> **Monitored Agents:** Gemini, Claude, Hermes, Codex, BrowserOS, Prime, Cline",
        "",
        "## 🛰️ AgentOS Live Telemetry",
    ]

    os_status = get_agent_os_status()
    if os_status.get("status") == "online":
        data = os_status["data"]
        lines.append(f"- **AgentOS Engine:** 🟢 Online (Active Tasks: {data.get('active_tasks_count', 0)}, Completed: {data.get('completed_tasks_count', 0)})")
        for ag in data.get("agents", []):
            lines.append(f"  - `{ag.get('agent_id')}` ({ag.get('role')}): **{ag.get('state', 'idle').upper()}**")
    else:
        lines.append(f"- **AgentOS Engine:** ⚪ Standalone / Offline mode ({os_status.get('error', 'Unreachable')})")

    lines.append("")
    lines.append("## 📋 Recent Multi-Agent Session Intel")
    if not top_sessions:
        lines.append("- No recent agent sessions found.")
    else:
        for s in top_sessions:
            lines.append(f"### 🤖 Agent: `{s['agent']}` | File: [[{s['file']}]]")
            lines.append(f"- **Timestamp:** {s['mtime']}")
            lines.append("```markdown")
            lines.append(s['snippet'])
            lines.append("```")
            lines.append("")

    lines.append("## 🎯 Active Projects & Next Focus")
    moc_path = VAULT_ROOT / "Projects" / "00_Projects_MOC.md"
    if moc_path.exists():
        lines.append("- [[00_Projects_MOC]]: Master Map of 224 PC Projects.")
    lines.append("- [[AI Memory Hub]]: Multi-agent unified memory topology.")
    lines.append("")

    content = "\n".join(lines)
    synthesis_path.write_text(content, encoding="utf-8")
    print(f"[SUCCESS] Daily synthesis generated at: {synthesis_path}")
    return synthesis_path

def query_vault(keyword: str):
    results = []
    projects_dir = VAULT_ROOT / "Projects"
    if projects_dir.exists():
        for md in projects_dir.glob("*.md"):
            try:
                c = md.read_text(encoding="utf-8", errors="replace")
                if keyword.lower() in c.lower():
                    results.append({"type": "project", "name": md.stem, "file": md.name})
            except Exception:
                pass
    print(f"Found {len(results)} matches for '{keyword}':")
    for r in results[:15]:
        print(f"  - [[{r['file'][:-3]}]] ({r['type']})")
    return results

def dispatch_task(agent: str, title: str, description: str, priority: str = "medium"):
    try:
        payload = {
            "title": title,
            "description": description,
            "agent_id": agent,
            "priority": priority
        }
        r = requests.post(f"{AGENT_OS_URL}/api/dispatch", json=payload, timeout=10)
        if r.status_code == 200:
            res = r.json()
            print(f"[DISPATCHED] Task ID: {res.get('task', {}).get('task_id')} dispatched to {agent}")
            return res
        else:
            print(f"[ERROR] Dispatch failed: {r.status_code} {r.text}")
    except Exception as e:
        print(f"[ERROR] Could not connect to AgentOS at {AGENT_OS_URL}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Obsidian Native Agent Copilot")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("status", help="Check AgentOS and fleet status")
    subparsers.add_parser("synthesize", help="Synthesize daily multi-agent notes")
    
    q_parser = subparsers.add_parser("query", help="Query vault notes")
    q_parser.add_argument("keyword", type=str, help="Search term")

    d_parser = subparsers.add_parser("dispatch", help="Dispatch task to AgentOS")
    d_parser.add_argument("--agent", type=str, default="gemini", help="Target agent id")
    d_parser.add_argument("--title", type=str, required=True, help="Task title")
    d_parser.add_argument("--desc", type=str, default="", help="Task description")
    d_parser.add_argument("--priority", type=str, default="medium", help="Priority")

    args = parser.parse_args()

    if args.command == "status":
        st = get_agent_os_status()
        print(json.dumps(st, indent=2))
    elif args.command == "synthesize":
        run_synthesis()
    elif args.command == "query":
        query_vault(args.keyword)
    elif args.command == "dispatch":
        dispatch_task(args.agent, args.title, args.desc, args.priority)
    else:
        run_synthesis()

if __name__ == "__main__":
    main()
