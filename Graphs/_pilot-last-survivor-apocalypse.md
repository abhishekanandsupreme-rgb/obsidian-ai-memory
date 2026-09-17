# Pilot Codebase Map — last-survivor-apocalypse

Date: 2026-09-17 · Scope: `projects/last-survivor-apocalypse` · Method: bounded inventory + graphify detect + one archify architecture diagram

## Stack
- **Undetermined / pre-code asset scaffold.** No source files, no package manifest, no entry point found in scope.
- Only observed content is one audio asset (see below). Sibling `projects/tests/test_smoke.py` (unittest, stdlib only) and `projects/README.md` / `.gitignore` exist *outside* scope in the parent `projects/` scaffold.

## File counts (junk dirs excluded)
Target root top level: `assets/` only.

| Extension | Included files |
|---|---|
| .wav | 1 |
| **Total included** | **1** |

Excluded junk-dir counts inside scope (all zero): `node_modules=0`, `.git=0`, `dist=0`, `build=0`, `__pycache__=0`, `.next=0`, `.nuxt=0`, `.venv=0`, `venv=0`.
- The single file: `assets/audio/tts_sample_s3.wav` (114,732 bytes).

## Core components (honest: 1 observed, rest planned/scaffold)
Observed:
1. **Asset Store** — `assets/audio/` (observed, 1 wav)
2. **Audio Sample** — `tts_sample_s3.wav` (observed bytes)

Planned (diagram placeholders, NOT implemented — no code to confirm):
3. Players (external input), 4. Game Client (entry TBD), 5. Survival Loop, 6. World/Save State.
Scaffold context (observed outside scope, shown for orientation):
7. Project Scaffold (parent README/`.gitignore`), 8. Smoke Tests (`projects/tests/test_smoke.py`), 9. This pilot note.

No entry points. No language/runtime to report.

## graphify detect results (fast path, <60s — passed)
- Ran `py -c "from graphify.detect import detect"` via `py` (`python`/`python3` not on PATH; graphify import OK). Completed well under 60s.
- Result: `total_files=1`, `code=[]`, `document=[]`, `paper=[]`, `image=[]`, `video=["...assets/audio/tts_sample_s3.wav"]`, `total_words=0`, `needs_graph=false`, `warning="Corpus is ~0 words - fits in a single context window. You may not need a graph."`, `skipped_sensitive=[]`, `unclassified=[]`, `walk_errors=[]`.
- **Did NOT run full LLM extraction** per pilot instructions (and nothing to extract — corpus fits in one context window).

## archify artifact + validation receipt
- Candidate: `C:\Users\asus\Desktop\abhishek_personal_data\projects\last-survivor-apocalypse\archify-out\pilot-architecture.candidate.json` (9 nodes ≤ 12, showcase profile, honest planned-vs-observed labeling)
- Delivered: `C:\Users\asus\Desktop\abhishek_personal_data\projects\last-survivor-apocalypse\archify-out\pilot-architecture.html`
- Validation: **pass** — showcase, 9/9 artifact checks, 0 errors, 0 warnings (round 1 had 3 vertical-edge label overlaps; fixed with the 3 diagnosed `labelAt` positions, round 2 passed).
- Deliver receipt: spec sha256 `5759dd85…f706` (3,612 bytes) → artifact sha256 `a57ffa41…15b5` (811,843 bytes). `visual-check` NOT run (not requested; delivery is deterministic-evidence only, no browser claim).

## What to repeat for bigger projects
1. Read the graphify/archify SKILL contracts first; bounded inventory excluding `node_modules/.git/dist/build/__pycache__` (count by extension + excluded counts).
2. `graphify detect` with a 60s budget; if `total_files>500` or words>2M, narrow to top subfolders before extracting. Skip LLM extraction for code-only corpora (AST path) or tiny corpora.
3. Author ONE archify candidate (≤12 nodes, showcase, auto routes first), `validate … --quality showcase --json`, fix only diagnosed subjects (≤2 rounds improving), then `deliver` once and freeze the candidate.
4. Log one short vault note per pilot with counts, receipts (SHAs), and honest planned-vs-observed splits.
