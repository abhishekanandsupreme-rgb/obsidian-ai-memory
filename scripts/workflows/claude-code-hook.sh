#!/usr/bin/env bash
# claude-code-hook.sh — Claude Code hook that syncs session data to Obsidian after each session.
#
# This script is intended to be invoked by Claude Code's hook mechanism.
# It collects available session context and forwards it to sync-to-obsidian.py.
#
# Usage (standalone):
#   bash claude-code-hook.sh [session_json_path]
#
# Environment variables checked (in order):
#   CLAUDE_SESSION_JSON  — path or raw JSON string
#   CLAUDE_SESSION_ID    — used to build a default session record
#   CLAUDE_PROJECT_DIR   — used for project context
#
# All paths are absolute. Does not modify any agent configs.

set -euo pipefail

SYNC_SCRIPT="C:/Users/asus/Documents/Obsidian Vault/scripts/sync-to-obsidian.py"
AGENT_ID="claude-code"
DEFAULT_VAULT="C:/Users/asus/Documents/Obsidian Vault"

# Ensure Python is available
if ! command -v python >/dev/null 2>&1; then
    if ! command -v python3 >/dev/null 2>&1; then
        echo "[WARN] Python not found; skipping Obsidian sync." >&2
        exit 0
    else
        PYTHON=python3
    fi
else
    PYTHON=python
fi

# Collect session data
SESSION_DATA=""
if [[ $# -ge 1 && -n "${1:-}" ]]; then
    SESSION_DATA="$1"
elif [[ -n "${CLAUDE_SESSION_JSON:-}" ]]; then
    SESSION_DATA="${CLAUDE_SESSION_JSON}"
elif [[ -n "${CLAUDE_SESSION_ID:-}" ]]; then
    # Build a minimal session record from environment
    SESSION_DATA=$(cat <<EOF
{
  "session_id": "${CLAUDE_SESSION_ID}",
  "started_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "status": "completed",
  "summary": "Claude Code session ${CLAUDE_SESSION_ID}"
}
EOF
)
fi

if [[ -z "${SESSION_DATA}" ]]; then
    echo "[INFO] No Claude session data available; nothing to sync." >&2
    exit 0
fi

# Build project context if available
PROJECT_CONTEXT=""
if [[ -n "${CLAUDE_PROJECT_DIR:-}" ]]; then
    PROJECT_CONTEXT=$(cat <<EOF
{
  "project_id": "$(basename "${CLAUDE_PROJECT_DIR}")",
  "name": "$(basename "${CLAUDE_PROJECT_DIR}")",
  "current_state": "Active in ${CLAUDE_PROJECT_DIR}"
}
EOF
)
fi

# Invoke sync-to-obsidian.py with absolute paths
ARGS=()
ARGS+=("${SYNC_SCRIPT}")
ARGS+=("--agent-id" "${AGENT_ID}")
ARGS+=("--session-data" "${SESSION_DATA}")
ARGS+=("--vault-path" "${DEFAULT_VAULT}")

if [[ -n "${PROJECT_CONTEXT}" ]]; then
    ARGS+=("--project-context" "${PROJECT_CONTEXT}")
fi

echo "[INFO] Syncing Claude Code session to Obsidian..." >&2
if "${PYTHON}" "${ARGS[@]}"; then
    echo "[INFO] Claude Code session synced successfully." >&2
else
    echo "[WARN] Obsidian sync failed; continuing." >&2
    exit 0
fi
