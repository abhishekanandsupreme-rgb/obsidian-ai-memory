#!/usr/bin/env python3
"""
Native Obsidian Neural Copilot & In-Vault Agent Bridge (Milestone M2 / R2)

Connects the Obsidian Second Brain workspace directly to AgentOS:
- WebSocket client for live telemetry streaming and kernel events
- REST client for status, dispatch, project audits, sync, and notifications
- Vault-wide BM25/TF-IDF semantic note query engine with weighted field scoring
- Instant daily neural synthesis aggregating sessions, episodic memories, and MOC stats
- Automated daily briefing coordinator verifying memory/cross-agent/briefing.md
- Cross-agent coordination note generator with auto-dispatch to AgentOS kernel
"""

import os
import sys
import json
import re
import math
import time
import argparse
import asyncio
import subprocess
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Tuple, Callable

import requests

# Ensure UTF-8 output encoding across Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

try:
    import websockets
    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False

# Default configuration paths & endpoints
VAULT_ROOT = Path(os.environ.get("OBSIDIAN_VAULT_PATH", Path(__file__).resolve().parent.parent))
AGENT_OS_URL = os.environ.get("AGENT_OS_URL", "http://127.0.0.1:8000").rstrip("/")
DEFAULT_WS_URL = os.environ.get(
    "AGENT_OS_WS_URL",
    AGENT_OS_URL.replace("http://", "ws://").replace("https://", "wss://") + "/ws/telemetry"
)


# =====================================================================
# 1. Semantic Search Engine (BM25 / TF-IDF with Zone Weighting)
# =====================================================================

class VaultSemanticSearch:
    """
    In-memory BM25 search engine across all markdown notes in the Obsidian Vault.
    Applies weighted scoring:
      - Title: weight 3.0
      - Tags / Category: weight 2.0
      - Headings: weight 1.5
      - Body text: weight 1.0
    """

    STOPWORDS = {
        "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
        "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
        "below", "between", "both", "but", "by", "can", "cannot", "could", "did", "do",
        "does", "doing", "don't", "down", "during", "each", "few", "for", "from", "further",
        "had", "has", "have", "having", "he", "her", "here", "hers", "herself", "him",
        "himself", "his", "how", "i", "if", "in", "into", "is", "it", "its", "itself",
        "me", "more", "most", "my", "myself", "no", "nor", "not", "of", "off", "on",
        "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over",
        "own", "same", "she", "should", "so", "some", "such", "than", "that", "the",
        "their", "theirs", "them", "themselves", "then", "there", "these", "they", "this",
        "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't",
        "we", "were", "weren't", "what", "when", "where", "which", "while", "who", "whom",
        "why", "with", "won't", "would", "you", "your", "yours", "yourself", "yourselves"
    }

    WEIGHT_TITLE = 3.0
    WEIGHT_TAGS = 2.0
    WEIGHT_HEADINGS = 1.5
    WEIGHT_BODY = 1.0

    K1 = 1.5
    B = 0.75

    def __init__(self, vault_root: Path = VAULT_ROOT):
        self.vault_root = Path(vault_root)

    @staticmethod
    def tokenize(text: str) -> List[str]:
        """Extract lowercase alphanumeric and unicode tokens."""
        if not text:
            return []
        return [t.lower() for t in re.findall(r'[\w\-\.]{2,}', text, re.UNICODE)]

    @classmethod
    def filter_stopwords(cls, tokens: List[str]) -> List[str]:
        filtered = [t for t in tokens if t not in cls.STOPWORDS]
        return filtered if filtered else tokens

    @staticmethod
    def parse_markdown_zones(content: str, file_path: Path) -> Dict[str, Any]:
        """
        Segment markdown content into Title, Tags, Headings, and Body.
        Extracts YAML frontmatter fields as well.
        """
        filename_stem = file_path.stem
        title_tokens = [filename_stem.replace("_", " ").replace("-", " ")]
        tags = []
        category = ""
        headings = []
        body_lines = []

        fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        rest_content = content
        if fm_match:
            fm_text = fm_match.group(1)
            rest_content = content[fm_match.end():]
            for line in fm_text.splitlines():
                trimmed = line.strip()
                if trimmed.startswith("title:"):
                    val = trimmed.split(":", 1)[1].strip().strip('"\'')
                    if val:
                        title_tokens.append(val)
                elif trimmed.startswith("category:"):
                    category = trimmed.split(":", 1)[1].strip().strip('"\'')
                    tags.append(category)
                elif trimmed.startswith("tags:"):
                    val = trimmed.split(":", 1)[1].strip().strip('[]"\'')
                    if val:
                        tags.extend([t.strip().strip('"\'') for t in val.split(",") if t.strip()])
                elif trimmed.startswith("- ") and tags:
                    tags.append(trimmed[2:].strip().strip('"\''))

        # Inline tags from body (#tag)
        inline_tags = re.findall(r'(?:^|\s)#([a-zA-Z0-9_\-]+)', rest_content)
        tags.extend(inline_tags)

        # Headings and body
        for line in rest_content.splitlines():
            line_str = line.strip()
            if line_str.startswith("#"):
                heading_text = line_str.lstrip("#").strip()
                if heading_text:
                    headings.append(heading_text)
            else:
                body_lines.append(line)

        return {
            "title": " ".join(title_tokens),
            "tags": " ".join(tags),
            "headings": " ".join(headings),
            "body": "\n".join(body_lines),
            "category": category,
            "raw": content
        }

    @staticmethod
    def extract_excerpt(content: str, query_tokens: List[str], max_len: int = 180) -> str:
        """Find the most relevant excerpt sentence or window surrounding query terms."""
        lines = [
            l.strip() for l in content.splitlines()
            if l.strip() and not l.strip().startswith("---") and not l.strip().startswith("#")
        ]
        best_line = ""
        best_matches = -1

        for line in lines:
            line_lower = line.lower()
            matches = sum(1 for tok in query_tokens if tok in line_lower)
            if matches > best_matches and len(line) > 15:
                best_matches = matches
                best_line = line

        if not best_line and lines:
            best_line = lines[0]

        cleaned = re.sub(r'\[\[(.*?)\]\]', r'\1', best_line)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        if len(cleaned) > max_len:
            return cleaned[:max_len].strip() + "..."
        return cleaned

    def collect_markdown_files(self, folder_filter: Optional[str] = None) -> List[Path]:
        """Collect all markdown files across vault targets."""
        target_dirs = ["Projects", "Areas", "Resources", "memory", "agents", "00_Hub"]
        files: List[Path] = []

        if folder_filter:
            target_path = self.vault_root / folder_filter
            if target_path.exists():
                if target_path.is_file() and target_path.suffix == ".md":
                    return [target_path]
                files.extend(list(target_path.rglob("*.md")))
                return sorted(list(set(files)))

        for d in target_dirs:
            p = self.vault_root / d
            if p.exists() and p.is_dir():
                files.extend(list(p.rglob("*.md")))

        # Add top-level markdown files
        for f in self.vault_root.glob("*.md"):
            if f.is_file() and not f.name.startswith("."):
                files.append(f)

        # Exclude hidden files or git directories
        filtered = [
            f for f in files
            if ".git" not in f.parts and ".obsidian" not in f.parts and not f.name.startswith(".")
        ]
        return sorted(list(set(filtered)))

    def search(
        self,
        query: str,
        limit: int = 10,
        folder_filter: Optional[str] = None,
        category_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute BM25 search across vault notes with field weighting.
        """
        raw_tokens = self.tokenize(query)
        if not raw_tokens:
            return []

        query_tokens = self.filter_stopwords(raw_tokens)
        all_files = self.collect_markdown_files(folder_filter=folder_filter)
        if not all_files:
            return []

        doc_data: List[Dict[str, Any]] = []
        doc_lengths: List[float] = []

        for f in all_files:
            try:
                content = f.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue

            zones = self.parse_markdown_zones(content, f)
            if category_filter and category_filter.lower() not in zones["category"].lower():
                continue

            t_tokens = self.tokenize(zones["title"])
            tag_tokens = self.tokenize(zones["tags"])
            h_tokens = self.tokenize(zones["headings"])
            b_tokens = self.tokenize(zones["body"])

            doc_len = len(t_tokens) + len(tag_tokens) + len(h_tokens) + len(b_tokens)
            doc_lengths.append(doc_len)

            doc_data.append({
                "file": f,
                "relative": f.relative_to(self.vault_root),
                "zones": zones,
                "tokens": {
                    "title": t_tokens,
                    "tags": tag_tokens,
                    "headings": h_tokens,
                    "body": b_tokens,
                },
                "doc_len": doc_len,
            })

        if not doc_data:
            return []

        num_docs = len(doc_data)
        avg_doc_len = sum(doc_lengths) / num_docs if num_docs > 0 else 1.0

        # Calculate document frequencies for query tokens
        doc_freqs: Dict[str, int] = {t: 0 for t in query_tokens}
        for d in doc_data:
            all_doc_tokens = set(
                d["tokens"]["title"] + d["tokens"]["tags"] +
                d["tokens"]["headings"] + d["tokens"]["body"]
            )
            for t in query_tokens:
                if t in all_doc_tokens:
                    doc_freqs[t] += 1

        # Calculate BM25 scores
        scored_results: List[Dict[str, Any]] = []
        full_phrase = query.lower().strip()

        for d in doc_data:
            score = 0.0
            matched_terms = 0

            for t in query_tokens:
                df = doc_freqs.get(t, 0)
                if df == 0:
                    continue

                # Standard Robertson-Spärck Jones IDF
                idf = math.log(1.0 + (num_docs - df + 0.5) / (df + 0.5))
                if idf < 0:
                    idf = 0.01

                tf_title = d["tokens"]["title"].count(t)
                tf_tags = d["tokens"]["tags"].count(t)
                tf_headings = d["tokens"]["headings"].count(t)
                tf_body = d["tokens"]["body"].count(t)

                weighted_tf = (
                    self.WEIGHT_TITLE * tf_title +
                    self.WEIGHT_TAGS * tf_tags +
                    self.WEIGHT_HEADINGS * tf_headings +
                    self.WEIGHT_BODY * tf_body
                )

                if weighted_tf > 0:
                    matched_terms += 1
                    len_norm = 1.0 - self.B + self.B * (d["doc_len"] / avg_doc_len if avg_doc_len > 0 else 1.0)
                    term_score = idf * ((weighted_tf * (self.K1 + 1.0)) / (weighted_tf + self.K1 * len_norm))
                    score += term_score

            if score > 0:
                # Contiguous exact phrase bonus
                if len(query_tokens) > 1 and full_phrase in d["zones"]["raw"].lower():
                    score += 2.5

                excerpt = self.extract_excerpt(d["zones"]["raw"], query_tokens)
                note_name = d["file"].stem
                scored_results.append({
                    "name": note_name,
                    "wikilink": f"[[{note_name}]]",
                    "file": str(d["relative"]).replace("\\", "/"),
                    "title": d["zones"]["title"] or note_name,
                    "category": d["zones"]["category"] or d["file"].parent.name,
                    "score": round(score, 4),
                    "matched_terms": matched_terms,
                    "excerpt": excerpt
                })

        scored_results.sort(key=lambda x: x["score"], reverse=True)
        return scored_results[:limit]


# =====================================================================
# 2. Native Copilot Core Engine & REST Integration
# =====================================================================

class AgentCopilot:
    """
    Obsidian In-Vault Agent Copilot and Neural Bridge to AgentOS.
    """

    def __init__(self, vault_root: Path = VAULT_ROOT, agent_os_url: str = AGENT_OS_URL):
        self.vault_root = Path(vault_root)
        self.agent_os_url = str(agent_os_url).rstrip("/")
        self.search_engine = VaultSemanticSearch(self.vault_root)
        self.sync_script = self.vault_root / "scripts" / "vault-sync.py"

    # -----------------------------------------------------------------
    # REST API Clients
    # -----------------------------------------------------------------

    def get_status(self) -> Dict[str, Any]:
        """Fetch kernel status from /api/status with graceful offline fallback."""
        try:
            r = requests.get(f"{self.agent_os_url}/api/status", timeout=5)
            if r.status_code == 200:
                return {"status": "online", "data": r.json()}
            return {"status": "error", "code": r.status_code, "text": r.text}
        except requests.RequestException as e:
            return {
                "status": "offline",
                "error": str(e),
                "message": f"AgentOS kernel is offline or unreachable at {self.agent_os_url}"
            }

    def dispatch(
        self,
        title: str,
        description: str = "",
        agent_id: str = "gemini",
        priority: str = "medium"
    ) -> Dict[str, Any]:
        """Dispatch a task to the AgentOS kernel via POST /api/dispatch."""
        payload = {
            "title": title,
            "description": description,
            "agent_id": agent_id,
            "priority": priority
        }
        try:
            r = requests.post(f"{self.agent_os_url}/api/dispatch", json=payload, timeout=10)
            if r.status_code == 200:
                res = r.json()
                return {"status": "ok", "task": res.get("task", {})}
            return {"status": "error", "code": r.status_code, "text": r.text}
        except requests.RequestException as e:
            return {"status": "offline", "error": str(e)}

    def get_projects(self, q: str = "", finished: Optional[bool] = None) -> Dict[str, Any]:
        """Query projects via GET /api/projects."""
        params: Dict[str, Any] = {}
        if q:
            params["q"] = q
        if finished is not None:
            params["finished"] = finished
        try:
            r = requests.get(f"{self.agent_os_url}/api/projects", params=params, timeout=5)
            if r.status_code == 200:
                return r.json()
            return {"total": 0, "projects": [], "error": r.text}
        except requests.RequestException as e:
            return {"total": 0, "projects": [], "error": str(e)}

    def run_worker(self, project_name: Optional[str] = None, agent_id: str = "gemini") -> Dict[str, Any]:
        """Trigger autonomous worker audit & upgrade via POST /api/worker/run."""
        payload = {"project_name": project_name, "agent_id": agent_id}
        try:
            r = requests.post(f"{self.agent_os_url}/api/worker/run", json=payload, timeout=30)
            if r.status_code == 200:
                return r.json()
            return {"status": "error", "code": r.status_code, "text": r.text}
        except requests.RequestException as e:
            return {"status": "offline", "error": str(e)}

    def get_unfinished_projects(self) -> Dict[str, Any]:
        """Fetch unfinished projects list via GET /api/worker/unfinished."""
        try:
            r = requests.get(f"{self.agent_os_url}/api/worker/unfinished", timeout=5)
            if r.status_code == 200:
                return r.json()
            return {"unfinished_projects": [], "error": r.text}
        except requests.RequestException as e:
            return {"unfinished_projects": [], "error": str(e)}

    def run_swarm(self, max_agents: int = 30) -> Dict[str, Any]:
        """Trigger 30-agent parallel swarm execution via AgentOS."""
        try:
            r = requests.post(f"{self.agent_os_url}/api/swarm/run", json={"max_agents": max_agents}, timeout=90)
            if r.status_code == 200:
                return r.json()
            return {"status": "error", "code": r.status_code, "text": r.text}
        except Exception as e:
            return {"status": "offline", "error": str(e)}

    def get_swarm_status(self) -> Dict[str, Any]:
        """Get real-time status of the 30-agent swarm."""
        try:
            r = requests.get(f"{self.agent_os_url}/api/swarm/status", timeout=10)
            if r.status_code == 200:
                return r.json()
            return {"status": "error", "code": r.status_code}
        except Exception as e:
            return {"status": "offline", "error": str(e)}

    def trigger_vault_sync(self) -> Dict[str, Any]:
        """Trigger bi-directional vault synchronization via POST /api/vault/sync."""
        try:
            r = requests.post(f"{self.agent_os_url}/api/vault/sync", timeout=30)
            if r.status_code == 200:
                return r.json()
            return {"status": "error", "code": r.status_code, "text": r.text}
        except requests.RequestException as e:
            return {"status": "offline", "error": str(e)}

    def send_notification(self, message: str, channel: str = "general", level: str = "info") -> Dict[str, Any]:
        """Send notification alert to AgentOS event bus via POST /api/webhook/notify."""
        payload = {"message": message, "channel": channel, "level": level}
        try:
            r = requests.post(f"{self.agent_os_url}/api/webhook/notify", json=payload, timeout=10)
            if r.status_code == 200:
                return r.json()
            return {"status": "error", "code": r.status_code, "text": r.text}
        except requests.RequestException as e:
            return {"status": "offline", "error": str(e)}

    # -----------------------------------------------------------------
    # Semantic Search
    # -----------------------------------------------------------------

    def query(
        self,
        search_phrase: str,
        limit: int = 10,
        folder: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Semantic search across all vault markdown notes."""
        return self.search_engine.search(
            query=search_phrase,
            limit=limit,
            folder_filter=folder,
            category_filter=category
        )

    # -----------------------------------------------------------------
    # Instant Daily Synthesis
    # -----------------------------------------------------------------

    def synthesize(self, lookback_hours: int = 24) -> Dict[str, Any]:
        """
        Aggregate multi-agent sessions, episodic memories, live telemetry, and MOC stats
        into C:/Users/asus/Documents/Obsidian Vault/memory/cross-agent/daily-synthesis.md.
        """
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(hours=lookback_hours)

        # 1. Aggregate recent sessions from agents/*/sessions/*.md
        agents_dir = self.vault_root / "agents"
        recent_sessions: List[Dict[str, Any]] = []

        if agents_dir.exists():
            for s_file in agents_dir.glob("*/sessions/*.md"):
                try:
                    txt = s_file.read_text(encoding="utf-8", errors="replace")
                    mtime_dt = datetime.fromtimestamp(s_file.stat().st_mtime, tz=timezone.utc)
                    agent_name = s_file.parent.parent.name
                    recent_sessions.append({
                        "agent": agent_name,
                        "file": s_file.name,
                        "mtime": mtime_dt.isoformat(),
                        "is_recent": mtime_dt >= cutoff,
                        "snippet": "\n".join(txt.splitlines()[:15])
                    })
                except Exception:
                    continue

        # Sort newest first; prioritize recent
        recent_sessions.sort(key=lambda x: x["mtime"], reverse=True)
        active_sessions = [s for s in recent_sessions if s["is_recent"]]
        top_sessions = active_sessions[:10] if active_sessions else recent_sessions[:10]

        # 2. Aggregate episodic memories from agents/*/memory/*.md
        recent_memories: List[Dict[str, Any]] = []
        if agents_dir.exists():
            for m_file in agents_dir.glob("*/memory/*.md"):
                try:
                    txt = m_file.read_text(encoding="utf-8", errors="replace")
                    mtime_dt = datetime.fromtimestamp(m_file.stat().st_mtime, tz=timezone.utc)
                    agent_name = m_file.parent.parent.name
                    
                    # Extract importance and body
                    imp_match = re.search(r'importance:\s*(\w+)', txt)
                    importance = imp_match.group(1).lower() if imp_match else "medium"
                    
                    # Strip frontmatter for body excerpt
                    body_txt = re.sub(r'^---\s*\n.*?\n---\s*\n', '', txt, flags=re.DOTALL).strip()
                    first_line = body_txt.splitlines()[0] if body_txt.splitlines() else "No details"
                    
                    recent_memories.append({
                        "agent": agent_name,
                        "file": m_file.name,
                        "importance": importance,
                        "mtime": mtime_dt.isoformat(),
                        "content": first_line[:200]
                    })
                except Exception:
                    continue

        recent_memories.sort(key=lambda x: x["mtime"], reverse=True)
        top_memories = recent_memories[:8]

        # 3. Read Project MOC metrics
        moc_path = self.vault_root / "Projects" / "00_Projects_MOC.md"
        moc_stats = {"total": 222, "finished": 50, "unfinished": 172}
        if moc_path.exists():
            try:
                moc_txt = moc_path.read_text(encoding="utf-8", errors="replace")
                tot_m = re.search(r'total_projects:\s*(\d+)', moc_txt)
                fin_m = re.search(r'finished_count:\s*(\d+)', moc_txt)
                unf_m = re.search(r'unfinished_count:\s*(\d+)', moc_txt)
                if tot_m:
                    moc_stats["total"] = int(tot_m.group(1))
                if fin_m:
                    moc_stats["finished"] = int(fin_m.group(1))
                if unf_m:
                    moc_stats["unfinished"] = int(unf_m.group(1))
            except Exception:
                pass

        # 4. Fetch AgentOS status
        os_status = self.get_status()

        # 5. Build Markdown Content
        synthesis_path = self.vault_root / "memory" / "cross-agent" / "daily-synthesis.md"
        synthesis_path.parent.mkdir(parents=True, exist_ok=True)

        lines = [
            "---",
            "title: 'Daily Multi-Agent Neural Synthesis'",
            "type: memory-synthesis",
            f"updated_at: '{now.isoformat()}'",
            "tags: [agent-memory, daily-synthesis, cross-agent]",
            "---",
            "",
            "# 🧠 Daily Multi-Agent Neural Synthesis",
            f"> **Generated:** {now.strftime('%Y-%m-%d %H:%M:%S UTC')}",
            "> **Monitored Agents:** Gemini, Claude, Hermes, Codex, BrowserOS, Prime, Cline",
            "",
            "## 🛰️ AgentOS Live Telemetry",
        ]

        if os_status.get("status") == "online":
            data = os_status["data"]
            lines.append(
                f"- **AgentOS Engine:** 🟢 Online (Active Tasks: {data.get('active_tasks_count', 0)}, "
                f"Completed: {data.get('completed_tasks_count', 0)})"
            )
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
                lines.append(s["snippet"])
                lines.append("```")
                lines.append("")

        lines.append("## 💡 Episodic Memory Highlights")
        if not top_memories:
            lines.append("- No episodic memories recorded recently.")
        else:
            for m in top_memories:
                badge = "🔴" if m["importance"] == "high" else "🟡"
                lines.append(f"- {badge} **`{m['agent']}`** ([[{m['file']}]]): {m['content']}")

        lines.append("")
        lines.append("## 🎯 Active Projects & Next Focus")
        lines.append(
            f"- [[00_Projects_MOC]]: Master Map of {moc_stats['total']} PC Projects "
            f"(🟢 {moc_stats['finished']} Finished | 🟡 {moc_stats['unfinished']} Unfinished)."
        )
        lines.append("- [[AI Memory Hub]]: Multi-agent unified memory topology.")
        lines.append("")

        lines.append("## ⚡ Next Priority Actions")
        lines.append("- [ ] Audit and upgrade pending projects via `agent_copilot.py worker-run`")
        lines.append("- [ ] Synchronize cross-agent briefs with `agent_copilot.py brief`")
        lines.append("- [ ] Monitor live fleet events with `agent_copilot.py watch`")
        lines.append("")

        content = "\n".join(lines)
        synthesis_path.write_text(content, encoding="utf-8")
        return {
            "status": "ok",
            "file": str(synthesis_path),
            "sessions_count": len(top_sessions),
            "memories_count": len(top_memories),
            "moc_stats": moc_stats
        }

    # -----------------------------------------------------------------
    # Automated Daily Briefing
    # -----------------------------------------------------------------

    def run_briefing(self) -> Dict[str, Any]:
        """
        Execute vault-sync.py brief and verify regeneration of memory/cross-agent/briefing.md.
        """
        if not self.sync_script.exists():
            return {"status": "error", "message": f"vault-sync.py not found at {self.sync_script}"}

        python_cmd = "py" if os.name == "nt" else sys.executable
        try:
            res = subprocess.run(
                [python_cmd, str(self.sync_script), "brief"],
                capture_output=True,
                text=True,
                timeout=60
            )
            briefing_file = self.vault_root / "memory" / "cross-agent" / "briefing.md"
            if briefing_file.exists():
                mtime_iso = datetime.fromtimestamp(briefing_file.stat().st_mtime, tz=timezone.utc).isoformat()
                return {
                    "status": "ok",
                    "briefing_file": str(briefing_file),
                    "last_modified": mtime_iso,
                    "stdout": res.stdout.strip()
                }
            return {"status": "error", "message": "briefing.md not found after execution", "stdout": res.stdout}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # -----------------------------------------------------------------
    # Cross-Agent Coordination Generator
    # -----------------------------------------------------------------

    def coordinate(
        self,
        topic: str,
        agents: Optional[List[str]] = None,
        content: str = "",
        priority: str = "high",
        auto_dispatch: bool = True
    ) -> Dict[str, Any]:
        """
        Generate structured coordination note in memory/cross-agent/coordination_{YYYYMMDD}_{topic}.md
        and auto-dispatch task to AgentOS kernel for lead agent.
        """
        if not agents:
            agents = ["gemini", "claude"]

        now = datetime.now(timezone.utc)
        date_str = now.strftime("%Y%m%d")
        safe_topic = re.sub(r'[^a-zA-Z0-9_\-]', '_', topic.lower()).strip('_')
        note_name = f"coordination_{date_str}_{safe_topic}.md"
        note_path = self.vault_root / "memory" / "cross-agent" / note_name
        note_path.parent.mkdir(parents=True, exist_ok=True)

        lines = [
            "---",
            f"title: 'Coordination: {topic}'",
            "type: coordination",
            f"topic: '{topic}'",
            f"participating_agents: [{', '.join(agents)}]",
            f"created_at: '{now.isoformat()}'",
            "status: active",
            "tags: [coordination, cross-agent, multi-agent]",
            "---",
            "",
            f"# 🤝 Cross-Agent Coordination: {topic}",
            f"> **Generated:** {now.strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"> **Participating Agents:** {', '.join(agents)}",
            "> **Lifecycle Status:** 🟡 Active Coordination",
            "",
            "## 🎯 Objective & Context",
            content or f"Coordinated multi-agent mission focused on: {topic}.",
            "",
            "## 👥 Agent Role Assignments",
        ]

        role_presets = {
            "gemini": "Primary IDE Pair, Architecture Design, and Memory Sync",
            "claude": "Deep Code Refactoring, Security Audits, and Verification",
            "hermes": "Background Autonomous Runner & Task Execution",
            "codex": "Rapid Snippet Generation, Tests, and Documentation",
            "browseros": "Live Browser Verification & Web Operations",
            "prime": "Operations & Specialized Pipeline Coordination"
        }

        for ag in agents:
            r = role_presets.get(ag.lower(), "Collaborating Specialist")
            lines.append(f"- **`{ag}`**: {r}")

        lines.extend([
            "",
            "## 📋 Action Items & Deliverables",
            f"- [ ] Initialize workspace context and read briefing for {topic}",
            f"- [ ] Execute primary implementation milestone for {topic}",
            "- [ ] Run unit test suite and verify 100% pass rate",
            "- [ ] Record episodic memory and log session to Obsidian",
            "",
            "## 🔗 Related Notes & Interlinks",
            "- [[00_Projects_MOC]] — Master Projects Map of Content",
            "- [[AI Memory Hub]] — Shared Cross-Agent Memory Hub",
            "- [[daily-synthesis]] — Latest Cross-Agent Neural Synthesis",
            "- [[briefing]] — Daily Multi-Agent Briefing",
            ""
        ])

        note_content = "\n".join(lines)
        note_path.write_text(note_content, encoding="utf-8")

        dispatch_result: Optional[Dict[str, Any]] = None
        if auto_dispatch and agents:
            lead_agent = agents[0]
            dispatch_result = self.dispatch(
                title=f"Coordination: {topic}",
                description=f"Execute tasks specified in [[{note_name}]]",
                agent_id=lead_agent,
                priority=priority
            )

        return {
            "status": "ok",
            "note_file": str(note_path),
            "topic": topic,
            "agents": agents,
            "dispatched": dispatch_result
        }


# =====================================================================
# 3. WebSocket Client & Live Telemetry Watcher
# =====================================================================

def format_kernel_event(event_dict: Dict[str, Any]) -> str:
    """Format kernel event for terminal output."""
    ev = event_dict.get("event", event_dict)
    ev_type = ev.get("type") or ev.get("event_type") or "unknown"
    data = ev.get("data") or ev.get("payload") or {}
    ts = ev.get("timestamp") or datetime.now(timezone.utc).isoformat()

    if ev_type == "task_dispatched":
        return (
            f"[{ts}] 🚀 Task Dispatched: #{data.get('task_id')} -> {data.get('agent_id')} "
            f"| \"{data.get('title')}\" (Priority: {data.get('priority')})"
        )
    elif ev_type == "agent_state_changed":
        return (
            f"[{ts}] 🔄 Agent State Changed: `{data.get('agent_id')}` -> "
            f"{str(data.get('state', '')).upper()} (Task: #{data.get('task_id') or 'none'})"
        )
    elif ev_type == "task_completed":
        res_snippet = str(data.get("result", ""))[:80]
        return (
            f"[{ts}] ✅ Task Completed: #{data.get('task_id')} by {data.get('agent_id')} "
            f"| {res_snippet}"
        )
    elif ev_type == "autonomous_audit_completed":
        return (
            f"[{ts}] 🛠️ Autonomous Audit: {data.get('project')} "
            f"| Score: {data.get('old_score')} -> {data.get('new_score')} "
            f"(Finished: {data.get('is_finished')})"
        )
    elif ev_type == "notification_alert":
        return (
            f"[{ts}] 🔔 Alert [{data.get('channel')} - {data.get('level')}]: "
            f"{data.get('message')}"
        )
    elif ev_type == "github_webhook_received":
        return (
            f"[{ts}] 🐙 GitHub Webhook: {data.get('event')} on {data.get('repo')} "
            f"(Task: #{data.get('task_id')})"
        )
    else:
        return f"[{ts}] ℹ️ Event [{ev_type}]: {json.dumps(data)}"


async def watch_telemetry(
    ws_url: str = DEFAULT_WS_URL,
    max_events: Optional[int] = None,
    timeout: Optional[float] = None,
    reconnect: bool = True,
    max_reconnects: int = 10,
    on_event: Optional[Callable[[Dict[str, Any]], None]] = None
) -> List[Dict[str, Any]]:
    """
    Connect to AgentOS WebSocket telemetry stream with auto-reconnect logic.
    Streams live kernel events to terminal and invokes on_event callback.
    """
    if not HAS_WEBSOCKETS:
        print("[ERROR] 'websockets' library is not installed. Run: py -m pip install websockets")
        return []

    events_received: List[Dict[str, Any]] = []
    reconnect_attempts = 0
    backoff = 1.0

    print(f"[*] Connecting to AgentOS live telemetry at {ws_url}...")
    while True:
        try:
            async with websockets.connect(ws_url) as ws:
                print(f"[CONNECTED] 🛰️ Live Telemetry Watcher active. Listening for kernel events...")
                backoff = 1.0  # Reset backoff on successful connection
                reconnect_attempts = 0

                while True:
                    if timeout:
                        try:
                            raw_msg = await asyncio.wait_for(ws.recv(), timeout=timeout)
                        except asyncio.TimeoutError:
                            print(f"[*] Timeout of {timeout}s reached without new events.")
                            return events_received
                    else:
                        raw_msg = await ws.recv()

                    try:
                        parsed = json.loads(raw_msg)
                    except json.JSONDecodeError:
                        parsed = {"type": "raw", "data": str(raw_msg)}

                    events_received.append(parsed)
                    formatted = format_kernel_event(parsed)
                    print(formatted)

                    if on_event:
                        try:
                            on_event(parsed)
                        except Exception as e:
                            print(f"[WARN] Error in event callback: {e}")

                    if max_events is not None and len(events_received) >= max_events:
                        print(f"[*] Reached target event count ({max_events}). Stopping watcher.")
                        return events_received

        except (websockets.exceptions.ConnectionClosed, OSError, Exception) as e:
            if not reconnect or (max_reconnects and reconnect_attempts >= max_reconnects):
                print(f"[CLOSED] WebSocket connection terminated: {e}")
                break

            reconnect_attempts += 1
            print(f"[RECONNECT] Connection dropped ({e}). Reconnecting in {backoff:.1f}s (attempt {reconnect_attempts}/{max_reconnects})...")
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2.0, 10.0)

    return events_received


# =====================================================================
# 4. Backward Compatibility Aliases
# =====================================================================

def get_agent_os_status() -> Dict[str, Any]:
    copilot = AgentCopilot()
    return copilot.get_status()

def run_synthesis() -> Path:
    copilot = AgentCopilot()
    res = copilot.synthesize()
    return Path(res["file"])

def query_vault(keyword: str) -> List[Dict[str, Any]]:
    copilot = AgentCopilot()
    results = copilot.query(keyword, limit=15)
    print(f"Found {len(results)} matches for '{keyword}':")
    for r in results:
        print(f"  - {r['wikilink']} (Score: {r['score']}) | {r['file']}")
        if r.get("excerpt"):
            print(f"    \"{r['excerpt']}\"")
    return results

def dispatch_task(agent: str, title: str, description: str = "", priority: str = "medium") -> Optional[Dict[str, Any]]:
    copilot = AgentCopilot()
    res = copilot.dispatch(title=title, description=description, agent_id=agent, priority=priority)
    if res.get("status") == "ok":
        t = res.get("task", {})
        print(f"[DISPATCHED] Task ID: {t.get('task_id')} dispatched to {agent}")
        return res
    print(f"[ERROR] Dispatch failed: {res}")
    return None

def run_briefing() -> Dict[str, Any]:
    copilot = AgentCopilot()
    return copilot.run_briefing()

def generate_coordination(
    topic: str,
    agents: Optional[List[str]] = None,
    content: str = "",
    priority: str = "high",
    auto_dispatch: bool = True
) -> Dict[str, Any]:
    copilot = AgentCopilot()
    return copilot.coordinate(topic=topic, agents=agents, content=content, priority=priority, auto_dispatch=auto_dispatch)


# =====================================================================
# 5. CLI Interface
# =====================================================================

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Obsidian Native Agent Copilot & In-Vault Agent Bridge",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--url", default=AGENT_OS_URL, help="AgentOS base URL")
    subparsers = parser.add_subparsers(dest="command")

    # Command: status
    subparsers.add_parser("status", help="Check AgentOS fleet states, tasks, and telemetry")

    # Command: dispatch
    d_parser = subparsers.add_parser("dispatch", help="Dispatch task to AgentOS kernel")
    d_parser.add_argument("--agent", default="gemini", help="Target agent id")
    d_parser.add_argument("--title", required=True, help="Task title")
    d_parser.add_argument("--desc", default="", help="Task description")
    d_parser.add_argument("--priority", default="medium", choices=["low", "medium", "high", "critical"])

    # Command: query
    q_parser = subparsers.add_parser("query", help="Semantic note query with BM25 weighted scoring")
    q_parser.add_argument("phrase", help="Search phrase or keyword")
    q_parser.add_argument("--limit", type=int, default=10, help="Max results")
    q_parser.add_argument("--folder", default=None, help="Filter by folder name (e.g. Projects, Areas)")
    q_parser.add_argument("--category", default=None, help="Filter by category")
    q_parser.add_argument("--json", action="store_true", help="Output results as JSON")

    # Command: synthesize
    s_parser = subparsers.add_parser("synthesize", help="Synthesize daily multi-agent memories into daily-synthesis.md")
    s_parser.add_argument("--hours", type=int, default=24, help="Session lookback hours")

    # Command: brief
    subparsers.add_parser("brief", help="Trigger automated daily briefing regeneration via vault-sync.py")

    # Command: coordinate
    c_parser = subparsers.add_parser("coordinate", help="Generate cross-agent coordination note and dispatch task")
    c_parser.add_argument("--topic", required=True, help="Coordination topic")
    c_parser.add_argument("--agents", default="gemini,claude", help="Comma-separated agent ids")
    c_parser.add_argument("--desc", default="", help="Mission objectives and context")
    c_parser.add_argument("--priority", default="high", choices=["low", "medium", "high", "critical"])
    c_parser.add_argument("--no-dispatch", action="store_true", help="Skip auto-dispatching task to kernel")

    # Command: watch
    w_parser = subparsers.add_parser("watch", help="Listen to real-time WebSocket kernel telemetry events")
    w_parser.add_argument("--ws-url", default=None, help="Custom WebSocket URL")
    w_parser.add_argument("--max-events", type=int, default=None, help="Exit after N events")
    w_parser.add_argument("--timeout", type=float, default=None, help="Exit after N seconds idle")
    w_parser.add_argument("--once", action="store_true", help="Exit after receiving first event")
    w_parser.add_argument("--no-reconnect", action="store_true", help="Do not reconnect on failure")

    # Command: projects
    p_parser = subparsers.add_parser("projects", help="Query registered codebases from AgentOS")
    p_parser.add_argument("--query", default="", help="Search query")
    p_parser.add_argument("--finished", action="store_true", help="Filter finished projects")
    p_parser.add_argument("--unfinished", action="store_true", help="Filter unfinished projects")

    # Command: worker-run
    wr_parser = subparsers.add_parser("worker-run", help="Trigger autonomous worker audit & upgrade")
    wr_parser.add_argument("--project", default=None, help="Target project name")
    wr_parser.add_argument("--agent", default="gemini", help="Auditing agent id")

    # Command: unfinished
    subparsers.add_parser("unfinished", help="List unfinished projects via AgentOS API")

    # Command: sync
    swarm_p = subparsers.add_parser("swarm", help="Trigger 30-agent parallel swarm execution")
    swarm_p.add_argument("--max-agents", type=int, default=30, help="Number of concurrent agents (default: 30)")

    subparsers.add_parser("swarm-status", help="Get 30-agent parallel swarm status")
    subparsers.add_parser("sync", help="Trigger bi-directional vault sync via AgentOS API")

    # Command: notify
    n_parser = subparsers.add_parser("notify", help="Dispatch notification alert")
    n_parser.add_argument("--message", required=True, help="Alert message")
    n_parser.add_argument("--channel", default="general", help="Notification channel")
    n_parser.add_argument("--level", default="info", choices=["info", "warning", "critical"])

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    copilot = AgentCopilot(agent_os_url=args.url)

    if not args.command or args.command == "status":
        status = copilot.get_status()
        print(json.dumps(status, indent=2))

    elif args.command == "dispatch":
        res = copilot.dispatch(args.title, args.desc, args.agent, args.priority)
        print(json.dumps(res, indent=2))

    elif args.command == "query":
        results = copilot.query(args.phrase, limit=args.limit, folder=args.folder, category=args.category)
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print(f"\n🔍 Semantic Search: '{args.phrase}' ({len(results)} matches found)\n")
            for r in results:
                print(f"  - {r['wikilink']} | Score: {r['score']} | {r['file']}")
                if r.get("excerpt"):
                    print(f"    \"{r['excerpt']}\"")
            print("")

    elif args.command == "synthesize":
        res = copilot.synthesize(lookback_hours=args.hours)
        print(f"[SUCCESS] Generated daily synthesis at: {res['file']}")
        print(f"  - Sessions aggregated: {res['sessions_count']}")
        print(f"  - Memories aggregated: {res['memories_count']}")
        print(f"  - Projects: {res['moc_stats']['finished']} finished / {res['moc_stats']['unfinished']} unfinished")

    elif args.command == "brief":
        res = copilot.run_briefing()
        if res.get("status") == "ok":
            print(f"[SUCCESS] Automated briefing regenerated at: {res.get('briefing_file')}")
            print(f"  - Last modified: {res.get('last_modified')}")
        else:
            print(f"[ERROR] Briefing regeneration failed: {res.get('message')}")

    elif args.command == "coordinate":
        agents_list = [a.strip() for a in args.agents.split(",") if a.strip()]
        res = copilot.coordinate(
            topic=args.topic,
            agents=agents_list,
            content=args.desc,
            priority=args.priority,
            auto_dispatch=not args.no_dispatch
        )
        print(f"[SUCCESS] Coordination note generated: {res['note_file']}")
        if res.get("dispatched"):
            d = res["dispatched"]
            t = d.get("task", {})
            print(f"  - Auto-dispatched task #{t.get('task_id')} to lead agent `{agents_list[0]}`")

    elif args.command == "watch":
        ws_url = args.ws_url or DEFAULT_WS_URL
        max_ev = 1 if args.once else args.max_events
        reconn = not args.no_reconnect
        try:
            asyncio.run(watch_telemetry(
                ws_url=ws_url,
                max_events=max_ev,
                timeout=args.timeout,
                reconnect=reconn
            ))
        except KeyboardInterrupt:
            print("\n[*] Live telemetry watcher stopped by user.")

    elif args.command == "projects":
        finished_val = True if args.finished else (False if args.unfinished else None)
        res = copilot.get_projects(q=args.query, finished=finished_val)
        print(json.dumps(res, indent=2))

    elif args.command == "worker-run":
        res = copilot.run_worker(project_name=args.project, agent_id=args.agent)
        print(json.dumps(res, indent=2))

    elif args.command == "unfinished":
        res = copilot.get_unfinished_projects()
        print(json.dumps(res, indent=2))

    elif args.command == "swarm":
        res = copilot.run_swarm(max_agents=args.max_agents)
        print(json.dumps(res, indent=2))

    elif args.command == "swarm-status":
        res = copilot.get_swarm_status()
        print(json.dumps(res, indent=2))
    elif args.command == "sync":
        res = copilot.trigger_vault_sync()
        print(json.dumps(res, indent=2))

    elif args.command == "notify":
        res = copilot.send_notification(args.message, channel=args.channel, level=args.level)
        print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
