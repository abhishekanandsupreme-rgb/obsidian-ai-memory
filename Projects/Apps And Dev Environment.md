---
title: Apps And Dev Environment
type: inventory
tags: [migration, apps, dev-environment, setup]
status: active
tech_stack: [node, python, git, docker, vscode]
path: C:/Users/asus/Documents/Obsidian Vault/Projects/Apps And Dev Environment.md
git_remote: vault-internal
last_updated: 2026-09-17
---

# Apps And Dev Environment

Verified 2026-09-17 via registry (HKLM/HKCU), Appx, and CLI probes.

## Major Desktop Apps

| App | Version |
|---|---|
| 7-Zip x64 | 26.02 |
| Android Studio | 2026.1 |
| Docker Desktop | 4.90.0 |
| Temurin JDK 21 x64 | 21.0.11.10 |
| Git / GitHub CLI | 2.54.0 / 2.95.0 |
| Node.js | 24.16.0 |
| Google Drive | 130.0.2.0 |
| Office Pro Plus 2019 en-us | 16.0.19127 |
| .NET Host/Runtime 8 x64 | 8.0.21 |
| NVIDIA Graphics/App | 610.47 / 11.0.7.247 |
| PowerToys Preview | 0.101.2362 |
| Proton VPN | 5.1.7 |
| Python 3.11.9 | 3.11.9150 (9 MSI parts) |
| Quick Heal Total Security | 24.00 |
| WSL | 2.7.3.0 |
| VS Code (User) | 1.137.0 |
| Antigravity / Zed / Qoder / Orca | 2.13.0 / 1.19.2 / 0.1.4 / 1.4.200 |
| BrowserOS / BrowserOS neo | 151.0.8162.137 |
| OpenCode / MiniMax Code / Cline / GH Copilot | 1.18.31 / 3.0.70 / 0.0.28 / 1.1.21 |
| Obsidian / Telegram / Ollama / ngrok | 1.13.7 / 7.2.8 / 0.32.5 / 3.3.1 |
| FFmpeg / Firebase CLI / Rustup / RipGrep | 9.0.1 / 20.18.2 / 1.29.1 / 15.1.0 |
| Comfy Desktop / AgentOS / OpenMausBot / WorkBuddy | 1.0.46 / 1.0 / 0.1.78 / 5.5.2 |
| Browsers | Chrome, Edge, IE (StartMenu) + Brave + BrowserOS/neo |
| Store (Appx) | Claude, DevToys, CommandPalette, Intel Graphics Exp. |

## Toolchain (probed)

| Tool | Result |
|---|---|
| node v24.16.0 | OK |
| py → Python 3.11.9 | OK (`python` shim NOT recognized — fix on new PC by adding Python to PATH) |
| git 2.54.0 | OK |
| gh 2.95.0 | OK |
| docker 29.7.2 | OK |
| uv 0.12.12 | OK |
| npm 12.0.1 | OK |
| code CLI | fails in pipeline (`CantActivateDocumentInPipeline`); registry says 1.137.0 |

PATH includes: Temurin JDK bin, Git/cmd, dotnet, nodejs, cloudflared, GH CLI, Docker, Roaming/npm, Codex bins, hermes/bin+node, .cargo/bin, VS Code bin, Obsidian, Zed/bin, orca bin, Python311/Scripts, WinGet/Links, unsloth/kimi/grok/minimax bins.

## VSCode Extensions (~55, via `~/.vscode/extensions`)

Python: ms-python.python/pylance/debugpy/python-envs, jupyter+renderers+keymap. Containers/K8s: containers, kubernetes-tools, remote-containers, azure-mcp-server, azureresourcegroups, windows-ai-studio. AI: kilo-code, roo-cline, claude-dev, anthropic.claude-code, opencode, gitlens, blackbox, codeium, huggingface-chat, ollama, qwen companion, glm/kimi/minimax/qwen/deepseek/zai/unify/litellm providers. Misc: rainbow-csv, markdownlint, yaml.

## Global Packages

- pip (`py -m pip list`): aiohttp 3.14.3, boto3/botocore 1.43.72, FastAPI 0.141.1, faster-whisper 1.2.1, Flask 3.1.3, ctranslate2 4.8, editable `colibri-engine` → personal_data/colibri
- uv tools: aider-chat 0.86.2, browser-use 0.13.10
- npm -g (~40): @openai/codex 0.153.4, opencode-ai 1.18.30, cline 3.0.55, vercel 59.4, wrangler 4.104, kilocode/cli, qwen-code, auggie, crush, codebuff, remotion, vite 5.4.11, pnpm 11.25, bun 1.4, openclaw, composio-core
- Program Files: 7-Zip, Android, Docker, dotnet, Eclipse Adoptium, Epic, Git, GH CLI, Google, nodejs, NVIDIA, obs-studio, Proton, Quick Heal, WSL. x86: cloudflared, No-IP, Perplexity, MyPublicWiFi.

## Reinstall Checklist (new device)

1. Runtimes: Node 24.16 + npm 12, Python 3.11.9 (tick Add-to-PATH, verify `python --version`), Temurin JDK 21, .NET 8, Rustup.
2. Dev: Git 2.54, GH CLI 2.95 (`gh auth login`), Docker Desktop 4.90 + WSL 2.7.3, VS Code 1.137 + extensions (copy `~/.vscode/extensions` or reinstall list above), uv 0.12.12, cloudflared, ngrok, Firebase CLI, wrangler/vercel CLIs.
3. Apps: Chrome+Edge+Brave, Obsidian 1.13.7, Google Drive (2 accounts), Office 2019, 7-Zip, PowerToys, ProtonVPN, Quick Heal, Ollama 0.32.5, FFmpeg, RipGrep.
4. AI/IDE layer: Antigravity, Zed, OpenCode 1.18.31, Cline, Orca, Qoder, Comfy Desktop, BrowserOS neo.
5. Restore: `npm i -g` list above, `uv tool install aider-chat browser-use`, pip (FastAPI/boto3/faster-whisper), Docker images/volumes, `%APPDATA%/npm`, Obsidian vault.

## Related

- [[Device Migration Index]]
- [[Computer Structure Map]]
- [[Projects Inventory]]
- [[Active Work Handoff]]
- [[AI Memory Hub]]
