#!/bin/sh
set -e

echo "Starting Obsidian sync worker..."

# Run sync script
while true; do
    echo "[$(date)] Running sync-all-agents.py..."
    python3 sync-all-agents.py || echo "[$(date)] Sync failed, will retry in 15 minutes."
    echo "[$(date)] Sleeping 900 seconds (15 minutes)..."
    sleep 900
done
