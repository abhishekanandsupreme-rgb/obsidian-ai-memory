#!/usr/bin/env bash
# setup-vault.sh — Creates the complete Obsidian vault structure for AI agent memory.
# Cross-platform: tested with Git Bash / MSYS2 on Windows and native bash on Linux/macOS.
# Uses the absolute vault path. Does not modify existing files.

set -euo pipefail

VAULT_ROOT="C:/Users/asus/Documents/Obsidian Vault"

# Resolve to an absolute path (handles mixed / and \ on Windows)
if command -v cygpath >/dev/null 2>&1; then
    VAULT_ROOT="$(cygpath -m "$VAULT_ROOT")"
fi

echo "Setting up Obsidian vault at: $VAULT_ROOT"

# Helper: create directory if it does not exist
ensure_dir() {
    if [ ! -d "$1" ]; then
        mkdir -p "$1"
        echo "  Created directory: $1"
    else
        echo "  Directory already exists: $1"
    fi
}

# Helper: create file if it does not exist
ensure_file() {
    if [ ! -f "$1" ]; then
        cat > "$1" <<'EOF'
EOF
        echo "  Created file: $1"
    else
        echo "  File already exists: $1"
    fi
}

# --- Directory structure ---
ensure_dir "$VAULT_ROOT/Templates"
ensure_dir "$VAULT_ROOT/Agents"
ensure_dir "$VAULT_ROOT/Projects"
ensure_dir "$VAULT_ROOT/Inbox"

# --- Template files ---
TEMPLATE_SESSION="$VAULT_ROOT/Templates/session-template.md"
if [ ! -f "$TEMPLATE_SESSION" ]; then
cat > "$TEMPLATE_SESSION" <<'EOF'
---
agent_id: 
session_id: 
started_at: 
ended_at: 
status: 
tags: [session, agent-log]
---

# Session: {{session_id}}

**Agent:** {{agent_id}}
**Started:** {{started_at}}
**Ended:** {{ended_at}}
**Status:** {{status}}

## Summary

<!-- Session summary goes here -->

## Key Events

- 

## Actions Taken

1. 

## Decisions Made

- 

## Next Steps

- 
EOF
echo "  Created file: $TEMPLATE_SESSION"
else
echo "  File already exists: $TEMPLATE_SESSION"
fi

TEMPLATE_MEMORY="$VAULT_ROOT/Templates/memory-template.md"
if [ ! -f "$TEMPLATE_MEMORY" ]; then
cat > "$TEMPLATE_MEMORY" <<'EOF'
---
agent_id: 
memory_type: episodic|semantic|procedural
created_at: 
importance: low|medium|high
tags: [memory, agent-log]
---

# Memory Entry

**Agent:** {{agent_id}}
**Type:** {{memory_type}}
**Created:** {{created_at}}
**Importance:** {{importance}}

## Content

<!-- Memory content goes here -->

## Context

- Related Sessions: 
- Related Projects: 
EOF
echo "  Created file: $TEMPLATE_MEMORY"
else
echo "  File already exists: $TEMPLATE_MEMORY"
fi

TEMPLATE_PROJECT="$VAULT_ROOT/Templates/project-template.md"
if [ ! -f "$TEMPLATE_PROJECT" ]; then
cat > "$TEMPLATE_PROJECT" <<'EOF'
---
project_id: 
name: 
status: active|archived|on-hold
created_at: 
updated_at: 
tags: [project, agent-context]
---

# Project: {{name}}

**ID:** {{project_id}}
**Status:** {{status}}
**Created:** {{created_at}}
**Updated:** {{updated_at}}

## Overview

<!-- Project overview goes here -->

## Goals

1. 

## Key Deliverables

- 

## Current State

<!-- Current progress and blockers -->

## Team / Agents Assigned

- 
EOF
echo "  Created file: $TEMPLATE_PROJECT"
else
echo "  File already exists: $TEMPLATE_PROJECT"
fi

# --- Placeholder files to keep empty directories in git ---
ensure_file "$VAULT_ROOT/Agents/.gitkeep"
ensure_file "$VAULT_ROOT/Projects/.gitkeep"
ensure_file "$VAULT_ROOT/Inbox/.gitkeep"

echo ""
echo "Vault setup complete."
echo "Structure created under: $VAULT_ROOT"
echo "Run sync-to-obsidian.py to start writing agent memory."
