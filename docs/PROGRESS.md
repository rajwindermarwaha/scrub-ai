# scrub-ai — Progress Log

This file is updated after every working session.
When starting a new session with AI, share this file so it knows exactly where to pick up.

---

## ⏩ NEXT SESSION — START HERE

### What to do first
```bash
cd ~/scrub-ai
git checkout feature/v2.0-vscode-extension
source .venv/bin/activate
export NVM_DIR="$HOME/.nvm" && source "$NVM_DIR/nvm.sh" && nvm use 20
```

### Next step
VS Code extension is feature-complete and publish-ready. Next step is **publishing to the VS Code Marketplace**:
1. Create a publisher account at https://marketplace.visualstudio.com/manage
2. Generate a Personal Access Token (PAT) in Azure DevOps
3. Install `vsce`: `npm install -g @vscode/vsce`
4. Run `vsce package` inside `vscode-extension/scrub-ai/` — verify the `.vsix` installs cleanly
5. Run `vsce publish` to push to the Marketplace

---

### Session 17 — 2026-07-06

**What we did:**
- Added `--json` flag to `scrub_ai/cli.py`:
  - Outputs all matches as a JSON array to stderr with `start`, `end`, `original`, `replacement`, `label`, `confidence` fields
  - Used by the VS Code extension to get exact character positions for diagnostics
- Added auto-scan diagnostics to VS Code extension:
  - `scanDocument()` runs `--dry-run --json`, parses match positions, creates `DiagnosticCollection` entries
  - Triggered on `onDidOpenTextDocument` and `onDidSaveTextDocument`
  - Skips files >500 KB and ignored dirs (`node_modules`, `.git`, `dist`, `build`, `.venv`, `__pycache__`)
  - Scans 22 text-like file extensions
  - Yellow squiggly underlines + Problems panel entries
- Added inline quick-fix code actions:
  - `ScrubAiCodeActionProvider` — 💡 lightbulb on every flagged line
  - `Mask [label] → [replacement]` applies the fix in-place with a single click
  - `Mask all sensitive values in file` appears when multiple detections are on the same line
- Added status bar indicator:
  - `$(shield) scrub-ai` shown in bottom-right when CLI is found
  - `$(warning) scrub-ai` with warning background when CLI is not found
  - Tooltip shows which Python binary is being used
- Fixed `findCli()` for all three platforms:
  - Windows (extension host on Windows): probes `wsl.exe` with venv paths, then `wsl python3`
  - Linux/WSL (extension host inside WSL): probes venv paths directly, then `python3`, then `python`
  - macOS: same as Linux
- Replaced auto-install prompt with a clear error message (pip install must run in the correct environment)
- Changed all `spawn()` calls to `shell: false` for reliability
- Bumped extension version to `1.0.0` in `package.json`
- Added `keywords`, `repository`, `homepage`, `bugs` to `package.json` for Marketplace listing
- Updated extension `README.md` with full feature docs: auto-scan, inline quick-fix, clipboard watch, supported file types, platform support
- Compiled successfully, committed and pushed to `feature/v2.0-vscode-extension`

**Result:** Extension fully working — diagnostics, inline quick-fix, status bar, clipboard watch all confirmed working.

**What was NOT done:**
- Not yet published to VS Code Marketplace

**Blockers:**
- None

**Status:** 🟢 Extension publish-ready. Ready to package and publish to Marketplace.

---

### Session 16 — 2026-07-05

**What we did:**
- Added clipboard watch mode to VS Code extension:
  - `startWatcher()` spawns `python -m scrub_ai.cli --watch` as a background subprocess on extension activation
  - Watcher process is killed cleanly on extension deactivation via `context.subscriptions.push({ dispose })`
  - Automatically sanitizes clipboard whenever content is copied — no manual action needed
- Tested end-to-end — clipboard watch mode working inside VS Code
- Committed and pushed to `feature/v2.0-vscode-extension`

**Result:** Extension sanitizes clipboard automatically on copy + supports manual sanitize via Ctrl+Alt+S.

**Status:** 🟡 Extension fully feature-complete. Ready to publish to Marketplace.

---

### Session 15 — 2026-07-05

**What we did:**
- Scaffolded VS Code extension using `yo code` inside `vscode-extension/` (TypeScript, no bundler)
- Wired `package.json`: publisher, two commands, `Ctrl+Alt+S` keybinding, `activationEvents`, engine `^1.113.0`, icon
- Implemented `src/extension.ts`: `findCli()`, `ensureCli()`, `runScrubAi()`, `sanitizeText()` with diff view
- Tested end-to-end in Extension Development Host

**Status:** 🟡 Extension working locally. Ready for watch mode.

---

### Session 14 — 2026-07-05

**What we did:**
- Confirmed Node 18 too old, installed Node 20.20.2 via nvm
- Installed `yo` and `generator-code` globally

**Status:** 🟡 Node environment ready. Ready to scaffold.

---

### Session 13 — 2026-07-05

**What we did:**
- Created `feature/v2.0-vscode-extension` branch
- Updated `docs/ARCHITECTURE.md`, `docs/PLAN.md`, `docs/DECISIONS.md`, `README.md` for v2.0

**Status:** 🟡 Docs complete. Ready to scaffold the VS Code extension.

---

### Session 12 — 2026-07-04

**What we did:**
- Added `--watch` flag to `cli.py`
- Wrote `tests/test_cli_v12.py` — 3 tests
- Updated `README.md` for v1.2
- Created `.github/workflows/publish.yml` — manual publish workflow with TestPyPI gate
- Added `TEST_PYPI_API_TOKEN` and `PYPI_API_TOKEN` secrets to GitHub repo
- Created `release` environment with required reviewer approval gate

**Result:** `pytest -q` → `127 passed`

**Status:** 🟢 v1.2 feature-complete. Ready to merge to main and publish.

---

### Session 11 — 2026-07-03

**What we did:**
- Updated `config.py` for watch mode (`watch_mode` key, `is_watch_mode()`, `set_watch_mode()`)
- Created `watcher.py` — cross-platform clipboard polling loop
- Updated `tray.py` — Watch Mode ON/OFF toggle in menu
- Wrote `tests/test_config.py` additions and `tests/test_watcher.py`

**Result:** `pytest -q` → `124 passed`

**Status:** 🟢 Watch mode complete.

---

### Session 10 — 2026-07-03

**What we did:**
- New icon design: shield + lightning bolt
- Updated tagline to "Shield your prompts."
- Published LinkedIn post

**Status:** 🟢 Branding updated.

---

### Session 9 — 2026-07-02

**What we did:**
- Added confidence scoring to all detectors
- Created `detectors/custom.py`, `detectors/pii.py`, `profiles.py`
- Added `--profile` and `--min-confidence` CLI flags
- Bumped version to `1.1.0`, published to PyPI

**Result:** `pytest -q` → `94 passed`

**Status:** 🟢 v1.1 shipped.

---

### Session 8 final — 2026-06-29

**What we did:**
- Built and published to PyPI: https://pypi.org/project/scrub-ai/1.0.0/
- Merged `feature/v1-windows` → `main`

**Status:** 🟢 v1.0 shipped.

---

### Session 8 — 2026-06-29

**What we did:**
- Created `config.py`, `notifier.py`, `hotkey.py`, `tray.py`
- Added `--start` flag to `cli.py`
- Created `assets/icon.png`, polished README, set up GitHub Actions CI

**Status:** 🟢 v1 feature-complete. Ready to publish.

---

### Session 7 — 2026-06-26

**What we did:**
- Wrote `cli.py` with `--file`, `--dry-run`, `--copy` flags
- Wrote `tests/test_cli.py` — 4 tests

**Result:** `pytest -q` → `15 passed`

**Status:** 🟢 CLI complete.

---

### Session 6 — 2026-06-25

**What we did:**
- Added `tests/test_secrets_detector.py`, `tests/test_cloud_detector.py`, `tests/test_base_detector.py`
- Hardened test fixtures for GitHub secret scanning

**Result:** `pytest -q` → `11 passed`

**Status:** 🟢 Core detector/sanitizer/test foundation complete.

---

### Session 5 — 2026-06-25

**What we did:**
- Created `detectors/network.py`, `sanitizer.py`
- Added `tests/test_network_detector.py`, `tests/test_sanitizer.py`

**Result:** `pytest -q` → `4 passed`

**Status:** 🟢 Core detection + sanitizer foundation complete.

---

### Session 4 — 2026-06-24

**What we did:**
- Created `detectors/secrets.py` — 6 patterns
- Created `detectors/cloud.py` — 12 patterns (AWS, GCP, Azure)

**Status:** 🟡 Two of three detectors complete.

---

### Session 3 — 2026-06-22

**What we did:**
- Fixed `pyproject.toml` build backend
- Made CLI cross-platform
- Created venv, installed dependencies
- Created `scrub_ai/__init__.py`, `detectors/__init__.py`, `detectors/base.py`

**Status:** 🟡 Foundation complete. Ready to write detectors.

---

### Session 2 — 2026-06-22

**What we did:**
- Created `feature/v1-core` branch
- Created `docs/DEVLOG.md`, `pyproject.toml`

**Status:** 🟡 Project scaffold started.

---

### Session 1 — 2026-06-21

**What we did:**
- Defined problem, tech stack, v1 scope
- Created GitHub repo, pushed all planning docs

**Status:** 🟡 Planning complete. Ready to start coding.

---

## Completed Steps

| Step | Description | Session | Status |
|---|---|---|---|
| 1 | Project planning docs pushed to GitHub | Session 1 | ✅ Done |
| 2 | Confirm Python is installed | Session 2 | ✅ Done |
| 3 | Create `feature/v1-core` branch | Session 2 | ✅ Done |
| 4 | Create `docs/DEVLOG.md` | Session 2 | ✅ Done |
| 5 | Create `pyproject.toml` | Session 2 | ✅ Done |
| 6 | Create virtual environment | Session 3 | ✅ Done |
| 7 | Create `scrub_ai/__init__.py` and `detectors/__init__.py` | Session 3 | ✅ Done |
| 8 | Write `detectors/base.py` | Session 3 | ✅ Done |
| 9 | Write `detectors/secrets.py` | Session 4 | ✅ Done |
| 10 | Write `detectors/cloud.py` | Session 4 | ✅ Done |
| 11 | Write `detectors/network.py` | Session 5 | ✅ Done |
| 12 | Write `sanitizer.py` | Session 5 | ✅ Done |
| 13 | Write `cli.py` | Session 7 | ✅ Done |
| 14 | Write `notifier.py` | Session 8 | ✅ Done |
| 15 | Write `hotkey.py` | Session 8 | ✅ Done |
| 16 | Write `tray.py` | Session 8 | ✅ Done |
| 17 | Write tests + fixtures | Session 6 | ✅ Done |
| 18 | Publish to PyPI | Session 8 | ✅ Done |
| 19 | Add confidence scoring | Session 9 | ✅ Done |
| 20 | Write `detectors/custom.py` | Session 9 | ✅ Done |
| 21 | Write `detectors/pii.py` | Session 9 | ✅ Done |
| 22 | Write `profiles.py` | Session 9 | ✅ Done |
| 23 | Add `--profile` and `--min-confidence` CLI flags | Session 9 | ✅ Done |
| 24 | Publish v1.1.0 to PyPI | Session 9 | ✅ Done |
| 25 | New icon design (shield + bolt) + tagline + LinkedIn post | Session 10 | ✅ Done |
| 26 | Update `config.py` for watch mode | Session 11 | ✅ Done |
| 27 | Create `watcher.py` | Session 11 | ✅ Done |
| 28 | Update `tray.py` — watch mode toggle | Session 11 | ✅ Done |
| 29 | Add `--watch` flag to `cli.py` | Session 12 | ✅ Done |
| 30 | Update `README.md` for v1.2 | Session 12 | ✅ Done |
| 31 | Create `publish.yml` GitHub Actions workflow | Session 12 | ✅ Done |
| 32 | Add PyPI secrets to GitHub + release environment | Session 12 | ✅ Done |
| 33 | Create `feature/v2.0-vscode-extension` branch | Session 13 | ✅ Done |
| 34 | Update all docs for v2.0 (ARCHITECTURE, PLAN, DECISIONS, PROGRESS, README) | Session 13 | ✅ Done |
| 35 | Install Node 20 via nvm + yo + generator-code globally | Session 14 | ✅ Done |
| 36 | Scaffold VS Code extension (`yo code`) + implement extension.ts | Session 15 | ✅ Done |
| 37 | Test extension end-to-end in Extension Development Host | Session 15 | ✅ Done |
| 38 | Add clipboard watch mode to VS Code extension | Session 16 | ✅ Done |
| 39 | Add `--json` flag to CLI for editor integration | Session 17 | ✅ Done |
| 40 | Add diagnostics + inline quick-fix to VS Code extension | Session 17 | ✅ Done |
| 41 | Fix cross-platform CLI detection + status bar indicator | Session 17 | ✅ Done |
| 42 | Bump extension to v1.0.0 + add Marketplace metadata | Session 17 | ✅ Done |
| 43 | Update extension README for Marketplace | Session 17 | ✅ Done |
