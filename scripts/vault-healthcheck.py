#!/usr/bin/env python3
"""
Obsidian Vault Validation and Sync Health Checker
Checks vault structure, registry, templates, session notes, and script executability.
Generates a JSON health report without modifying any vault files.
"""

import os
import re
import json
import yaml
from datetime import datetime
from pathlib import Path


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

VAULT_ROOT = Path("C:/Users/asus/Documents/Obsidian Vault")
REPORT_PATH = VAULT_ROOT / "scripts" / "vault-health-report.json"

REQUIRED_FOLDERS = [
    "agents",
    "Inbox",
    "memory",
    "Projects",
    "scripts",
    "templates",
]

SYNC_SCRIPT_EXTENSIONS = {".py", ".sh", ".bat", ".ps1", ".vbs"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def is_executable(path: Path) -> bool:
    """Return True if the file is executable by the current user."""
    return os.access(path, os.X_OK)


def parse_yaml_frontmatter(text: str) -> tuple[dict | None, int, int]:
    """
    Extract YAML frontmatter between the first pair of '---' markers.
    Returns (data_dict, start_line, end_line) or (None, -1, -1) on failure.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, -1, -1

    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        return None, -1, -1

    yaml_text = "\n".join(lines[1:end_idx])
    try:
        data = yaml.safe_load(yaml_text)
        if not isinstance(data, dict):
            return None, 1, end_idx + 1
        return data, 1, end_idx + 1
    except yaml.YAMLError:
        return None, 1, end_idx + 1


def extract_timestamp_from_filename(filename: str) -> datetime | None:
    """
    Extract timestamp from session note filenames like:
    20260822-074033_claude-test-001.md
    """
    match = re.match(r"(\d{8}-\d{6})_", filename)
    if match:
        try:
            return datetime.strptime(match.group(1), "%Y%m%d-%H%M%S")
        except ValueError:
            pass
    return None


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_required_folders() -> dict:
    results = {}
    for folder in REQUIRED_FOLDERS:
        path = VAULT_ROOT / folder
        exists = path.is_dir()
        results[folder] = {
            "path": str(path),
            "exists": exists,
            "status": "pass" if exists else "fail",
        }
    all_exist = all(r["exists"] for r in results.values())
    results["status"] = "pass" if all_exist else "fail"
    results["details"] = {
        folder: {"exists": r["exists"], "status": r["status"]}
        for folder, r in results.items()
        if folder not in ("status", "details")
    }
    return results


def check_registry() -> dict:
    registry_path = VAULT_ROOT / "agents" / "registry.md"
    result = {
        "path": str(registry_path),
        "exists": registry_path.is_file(),
        "status": "pass",
        "details": {},
    }

    if not result["exists"]:
        result["status"] = "fail"
        result["details"]["error"] = "registry.md not found"
        return result

    text = registry_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    # Check for markdown table structure
    table_rows = [line for line in lines if line.strip().startswith("|")]
    header_separator = any(
        re.match(r"^\|[\s\-:|]+\|$", line.strip())
        for line in lines
    )

    result["details"]["total_lines"] = len(lines)
    result["details"]["table_rows"] = len(table_rows)
    result["details"]["has_header_separator"] = header_separator
    result["details"]["is_valid_table"] = len(table_rows) >= 2 and header_separator

    if not result["details"]["is_valid_table"]:
        result["status"] = "fail"
        result["details"]["error"] = "Not a valid markdown table"

    return result


def check_templates() -> dict:
    templates_dir = VAULT_ROOT / "templates"
    result = {
        "path": str(templates_dir),
        "exists": templates_dir.is_dir(),
        "status": "pass",
        "files": {},
    }

    if not result["exists"]:
        result["status"] = "fail"
        result["details"] = {"error": "templates directory not found"}
        return result

    template_files = sorted(templates_dir.glob("*.md"))
    if not template_files:
        result["status"] = "warn"
        result["details"] = {"error": "No template files found"}
        return result

    all_valid = True
    for tmpl in template_files:
        text = tmpl.read_text(encoding="utf-8")
        data, start, end = parse_yaml_frontmatter(text)
        file_result = {
            "has_frontmatter": data is not None,
            "frontmatter_keys": list(data.keys()) if data else [],
            "status": "pass" if data is not None else "fail",
        }
        result["files"][tmpl.name] = file_result
        if not data:
            all_valid = False

    result["status"] = "pass" if all_valid else "fail"
    return result


def check_session_notes() -> dict:
    result = {
        "total_notes": 0,
        "status": "pass",
        "by_agent": {},
        "timestamps": [],
        "gaps": [],
    }

    session_files = list(VAULT_ROOT.glob("agents/*/sessions/*.md"))
    result["total_notes"] = len(session_files)

    if result["total_notes"] == 0:
        result["status"] = "warn"
        result["gaps"].append("No session notes found in any agent/sessions/ directory")
        return result

    timestamps = []
    agent_counts = {}

    for f in session_files:
        agent = f.parts[-3]  # agents/<agent>/sessions/<file>
        agent_counts[agent] = agent_counts.get(agent, 0) + 1
        ts = extract_timestamp_from_filename(f.name)
        if ts:
            timestamps.append((ts, f.name, agent))

    result["by_agent"] = dict(sorted(agent_counts.items()))

    # Check for temporal gaps (> 30 minutes between consecutive notes)
    if len(timestamps) >= 2:
        timestamps.sort(key=lambda x: x[0])
        result["timestamps"] = [
            {"time": t[0].isoformat(), "file": t[1], "agent": t[2]}
            for t in timestamps
        ]
        for i in range(1, len(timestamps)):
            delta = (timestamps[i][0] - timestamps[i - 1][0]).total_seconds()
            if delta > 1800:  # > 30 minutes
                result["gaps"].append({
                    "from": timestamps[i - 1][0].isoformat(),
                    "to": timestamps[i][0].isoformat(),
                    "gap_minutes": round(delta / 60, 1),
                })
    else:
        result["timestamps"] = [
            {"time": t[0].isoformat(), "file": t[1], "agent": t[2]}
            for t in timestamps
        ]

    if result["gaps"]:
        result["status"] = "warn"

    return result


def check_sync_scripts() -> dict:
    scripts_dir = VAULT_ROOT / "scripts"
    result = {
        "path": str(scripts_dir),
        "exists": scripts_dir.is_dir(),
        "status": "pass",
        "scripts": {},
    }

    if not result["exists"]:
        result["status"] = "fail"
        result["details"] = {"error": "scripts directory not found"}
        return result

    script_files = sorted(scripts_dir.rglob("*"))
    relevant = [f for f in script_files if f.is_file() and f.suffix in SYNC_SCRIPT_EXTENSIONS]

    if not relevant:
        result["status"] = "warn"
        result["details"] = {"error": "No sync scripts found"}
        return result

    all_executable = True
    for script in relevant:
        rel = script.relative_to(VAULT_ROOT)
        exec_status = is_executable(script)
        result["scripts"][str(rel)] = {
            "executable": exec_status,
            "status": "pass" if exec_status else "fail",
        }
        if not exec_status:
            all_executable = False

    result["status"] = "pass" if all_executable else "warn"
    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    report = {
        "vault_root": str(VAULT_ROOT),
        "generated_at": datetime.now().isoformat(),
        "overall_status": "pass",
        "checks": {},
    }

    checks = {
        "required_folders": check_required_folders(),
        "agents_registry": check_registry(),
        "templates": check_templates(),
        "session_notes": check_session_notes(),
        "sync_scripts": check_sync_scripts(),
    }

    report["checks"] = checks

    # Determine overall status
    statuses = [c.get("status", "pass") for c in checks.values()]
    if "fail" in statuses:
        report["overall_status"] = "fail"
    elif "warn" in statuses:
        report["overall_status"] = "warn"

    # Ensure scripts directory exists for report
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Health report generated: {REPORT_PATH}")
    print(f"Overall status: {report['overall_status']}")
    for name, check in checks.items():
        print(f"  {name}: {check.get('status', 'unknown')}")
    return report


if __name__ == "__main__":
    main()
