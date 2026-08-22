# Obsidian Docker Sync Worker

This container runs `sync-all-agents.py` every 15 minutes inside the Obsidian vault.

## Prerequisites

- Docker and Docker Compose installed
- An existing `sync-all-agents.py` script in your Obsidian vault root (or adjust the path in `entrypoint.sh`)

## Build and Run

```bash
cd "C:/Users/asus/Documents/Obsidian Vault/scripts/docker-sync"
docker compose up -d --build
```

## Logs

```bash
docker compose logs -f
```

## Stop

```bash
docker compose down
```

## Notes

- The container mounts `../..` (the Obsidian vault root) into `/vault`.
- `entrypoint.sh` runs `sync-all-agents.py`, sleeps 900 seconds, and repeats.
- The container restarts automatically unless stopped manually.
