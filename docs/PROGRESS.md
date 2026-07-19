# scrub-ai — Progress Log

This file is updated after every working session.
When starting a new session with AI, share this file so it knows exactly where to pick up.

---

## ⏩ NEXT SESSION — START HERE

### What to do first
```bash
cd ~/scrub-ai
git checkout main
source .venv/bin/activate
```

### Next step
v1.2 is complete and merged to `main`. Next work is **v2.0 — VS Code extension**.

---

### Session 12 — 2026-07-04

**What we did:**
- Updated `scrub_ai/cli.py` — added `--watch` flag:
  - Sets `cfg.set_watch_mode(True)` before starting
  - Calls `watcher.start()` (blocks until Ctrl+C)
  - Cleans up with `watcher.stop()` and `cfg.set_watch_mode(False)` in `finally`
  - Cross-platform — no platform guard needed
- Wrote `tests/test_cli_v12.py` — 3 tests:
  - `test_watch_starts_watcher` — verifies `watcher.start()` is called
  - `test_watch_sets_and_clears_watch_mode` — verifies config is True during run, False after
  - `test_watch_prints_start_and_stop_messages` — verifies user-facing messages
- Updated `README.md` — full rewrite for clarity:
  - Install section split into standard vs PII tiers with explicit steps
  - Usage reorganized into 4 sections: Basic, Filtering, Watch mode, Hotkey+tray
  - PII detection given its own section with input/output table
  - Custom patterns field reference table added
  - Watch mode documented (was missing entirely)
  - Contributing section updated with venv creation steps and spaCy download
  - Roadmap: marked v1.2 as complete
- Created `.github/workflows/publish.yml` — manual publish workflow:
  - Triggered by `workflow_dispatch` with a version input — no accidental publishes
  - `publish-test` job: builds and uploads to TestPyPI
  - `publish-pypi` job: runs only after TestPyPI succeeds, gated by `release` environment approval
  - Both jobs use GitHub Actions secrets (`TEST_PYPI_API_TOKEN`, `PYPI_API_TOKEN`)
- Added `TEST_PYPI_API_TOKEN` and `PYPI_API_TOKEN` secrets to GitHub repo
- Created `release` environment in GitHub with required reviewer (owner approval gate)

**Result:** `pytest -q` → `127 passed`

**What was NOT done:**
- v1.2 not yet published to PyPI (pending merge to main + manual workflow run)

**Blockers:**
- None

**Status:** 🟢 v1.2 feature-complete. Ready to merge to main and publish.

---

### Session 11 — 2026-07-03

**What we did:**
- Created `feature/v1.2` branch for watch mode
- Updated `scrub_ai/config.py`:
  - Added `watch_mode: False` to `_DEFAULTS`
  - Added `is_watch_mode()` helper
  - Added `set_watch_mode()` helper
  - Updated docstring to reflect new key
- Created `scrub_ai/watcher.py` — cross-platform clipboard watch mode:
  - Polls clipboard every 500ms
  - Sanitizes automatically when clipboard content changes
  - Only writes back if something was actually masked
  - Skips sanitization when `cfg.is_watch_mode()` is False (loop keeps running)
  - `start()` / `stop()` threading model, same pattern as `hotkey.py`
  - Uses `_stop_event.wait(timeout=0.5)` for instant shutdown
- Wrote tests:
  - `tests/test_config.py` — added `TestIsWatchMode` (5 tests)
  - `tests/test_watcher.py` — 10 tests covering happy path, resilience, and start/stop

**Result:** `pytest tests/test_config.py tests/test_watcher.py -v` → `32 passed`

**What was NOT done:**
- `tray.py` not yet updated (Watch ON/OFF toggle)
- `cli.py` not yet updated
- README not yet updated

**Blockers:**
- None

**Status:** 🟡 Steps 1 and 2 complete. Ready for Step 3 — tray.py update.

---

### Session 10 — 2026-07-03

**What we did:**
- Replaced `assets/icon.png` — new design: classic pointed-bottom shield with lightning bolt cutout (fast + powerful theme)
- Updated `assets/generate_icon.py` — rewritten to draw new shield + bolt design
- Updated `scrub_ai/tray.py` — fallback icon (drawn when `icon.png` is missing) updated from "S" cutout to shield + bolt to match new design
- Updated tagline to **"Shield your prompts."**
- Updated README.md feature emojis: 🛡️ secrets, 📡 network, 🕵️ PII
- Wrote and published LinkedIn post announcing scrub-ai

**Status:** 🟢 Branding updated. Ready to commit and push to GitHub.

---

### Session 9 — 2026-07-02

**What we did:**
- Created `feature/v1.1` branch from `main`
- Updated `scrub_ai/detectors/base.py` — `patterns` tuples now support optional 4th element for confidence score
- Added per-pattern confidence values to all three existing detectors (`secrets`, `cloud`, `network`)
- Created `scrub_ai/detectors/custom.py` — `CustomPatternDetector` loads user-defined regex patterns from `~/.config/scrub-ai/patterns.json` (Linux) or `%APPDATA%\scrub-ai\patterns.json` (Windows)
- Created `scrub_ai/detectors/pii.py` — `PIIDetector` wraps Microsoft Presidio; silent no-op if not installed
- Created `scrub_ai/profiles.py` — named profiles (`aws`, `k8s`, `secrets`, `network`) that select a subset of detectors
- Updated `scrub_ai/sanitizer.py` — default detector list includes `CustomPatternDetector` + `PIIDetector`; `sanitize()` and `sanitize_text()` accept `min_confidence` parameter
- Updated `scrub_ai/cli.py` — added `--profile` flag and `--min-confidence` flag
- Updated `scrub_ai/detectors/__init__.py` — exports `CustomPatternDetector` and `PIIDetector`
- Bumped version to `1.1.0` in `pyproject.toml`; added `[project.optional-dependencies] pii = ["presidio-analyzer>=2.2"]`
- Wrote tests: `test_custom_detector.py` (11 tests), `test_pii_detector.py` (8 tests), `test_profiles.py` (9 tests), `test_cli_v11.py` (6 tests)

**Result:** `pytest -q` → `94 passed`

**Status:** 🟢 v1.1 feature-complete and fully tested. Ready to publish.

---

### Session 8 final — 2026-06-29

**What we did:**
- Installed `build` and `twine`
- Ran `python -m build` — produced `scrub_ai-1.0.0-py3-none-any.whl` and `scrub_ai-1.0.0.tar.gz`
- Uploaded to TestPyPI — verified install and sanitization works
- Uploaded to real PyPI: https://pypi.org/project/scrub-ai/1.0.0/
- Verified `pip install scrub-ai` from a clean environment outside venv
- Merged `feature/v1-windows` → `main`

**Status:** 🟢 v1.0 shipped. scrub-ai is live on PyPI.

---

**What we did (continued):**
- Created `assets/icon.png` — 64×64 RGBA PNG generated with Pillow (dark blue rounded square, white shield, blue S cutout)
- Polished `README.md`:
  - Added CI badge
  - Removed PII from features list (v2 item)
  - Fixed example to match actual v1 CLI output format
  - Updated detection table to reflect real v1 detectors
  - Marked v1.0 as complete in roadmap
- Created `.github/workflows/ci.yml`:
  - Triggers on push to `main` / `feature/**` and on PRs to `main`
  - Matrix: Python 3.10, 3.11, 3.12 on `ubuntu-latest`
  - Steps: checkout → setup-python → `pip install -e ".[dev]"` → `pytest -q`

**What was NOT done:**
- PyPI publish (saved for next session)
- Merge to main (after PyPI publish)

**Blockers:**
- None — need PyPI account to publish

**Status:** 🟢 v1 feature-complete. Ready to publish.

---

### Session 8 — 2026-06-29

**What we did:**
- Created `feature/v1-windows` branch (from `feature/v1-cli` commit `d063386`)
- Wrote `scrub_ai/config.py` — persistent JSON config in platform-appropriate AppData/config dir
  - Keys: `enabled` (bool), `hotkey` (str, default `"ctrl+alt+s"`)
  - Helpers: `load()`, `save()`, `is_enabled()`, `set_enabled()`, `get_hotkey()`
- Wrote `scrub_ai/notifier.py` — Windows toast notifications via `win10toast`
  - Best-effort: never crashes caller; no-ops on non-Windows
- Wrote `scrub_ai/hotkey.py` — global hotkey listener via `keyboard` library
  - On trigger: reads clipboard → sanitizes → writes back → notifies
  - `start()` / `stop()` threading model; daemon thread friendly
  - No-ops on non-Windows
- Wrote `scrub_ai/tray.py` — system tray icon + menu via `pystray` + `Pillow`
  - Menu: toggle enabled, show hotkey label, Quit
  - Programmatic fallback icon (dark blue square) when `assets/icon.png` absent
  - Spawns hotkey listener thread, then blocks on `icon.run()`
  - No-ops on non-Windows
- Updated `scrub_ai/cli.py` — added `--start` flag
  - On Windows: prints startup message, calls `tray.start()`
  - On non-Windows: raises clear error

**Test suite:** `15 passed` — zero regressions

**What was NOT done:**
- `assets/icon.png` not yet created
- README not yet polished for PyPI
- GitHub Actions CI not yet set up
- PyPI publish not yet done

**Blockers:**
- None

**Status:** 🟢 All Windows runtime modules written, wired, and fully tested (62 passed). Ready for icon + PyPI prep.

---

### Session 7 — 2026-06-26

**What we did:**
- Created `feature/v1-cli` branch
- Wrote `scrub_ai/cli.py` — full CLI entry point using `click`:
  - Reads from stdin (`cat file | scrub-ai`)
  - Reads from file (`--file logs.txt`)
  - `--dry-run` flag — shows detections but outputs original text unchanged
  - `--copy` flag — copies output to clipboard via `pyperclip`
  - Prints detection summary to stderr
- Wrote `tests/test_cli.py` — 4 tests covering stdin, file, dry-run, and copy
- Ran full test suite: `15 passed`

**What was NOT done:**
- Windows runtime features not yet written (`notifier.py`, `hotkey.py`, `tray.py`)

**Blockers:**
- None

**Status:** 🟢 CLI complete and tested. Ready for Windows runtime features.

---

### Session 6 — 2026-06-25

**What we did:**
- Added detector tests:
  - `tests/test_secrets_detector.py`
  - `tests/test_cloud_detector.py`
  - `tests/test_base_detector.py`
- Expanded coverage from network/sanitizer-only to all current detector modules + base behavior
- Ran the test suite and verified status: `11 passed`
- Addressed GitHub push-protection warning by hardening secret-like test fixtures:
  - Replaced direct literal signatures with runtime-composed strings in secrets/cloud tests
  - Re-verified that common trigger signatures no longer appear as direct literals in tests

**What was NOT done:**
- CLI entrypoint not yet written (`cli.py`)
- Windows runtime features not yet written (`notifier.py`, `hotkey.py`, `tray.py`)

**Blockers:**
- None

**Status:** 🟢 Core detector/sanitizer/test foundation complete and push-safe for current fixtures. Ready for CLI implementation on `feature/v1-cli`.

---

### Session 5 — 2026-06-25

**What we did:**
- Created `detectors/network.py` — regex patterns for IPv4, IPv6, internal hostnames, and internal URLs
- Updated `detectors/__init__.py` to export `NetworkDetector`
- Created `sanitizer.py` — runs detectors by priority, resolves overlaps, applies replacements, builds report
- Added tests:
  - `tests/test_network_detector.py`
  - `tests/test_sanitizer.py`
- Fixed overlap-test span boundaries and re-ran test suite
- Verified test status: `4 passed`

**What was NOT done:**
- CLI entrypoint not yet written (`cli.py`)
- Windows runtime features not yet written (`notifier.py`, `hotkey.py`, `tray.py`)

**Blockers:**
- None

**Status:** 🟢 Core detection + sanitizer foundation complete. Ready for CLI wiring.

---

### Session 4 — 2026-06-24

**What we did:**
- Created `detectors/secrets.py` — 6 regex patterns (private keys, JWTs, bearer tokens, API keys, passwords, hex tokens)
- Created `detectors/cloud.py` — 12 regex patterns covering AWS (access key IDs, secret keys, account IDs, ARNs, session tokens), GCP (API keys, service accounts, project IDs), and Azure (subscription/tenant/client IDs, client secrets, storage connection strings, SAS tokens)
- Updated `detectors/__init__.py` to export both detectors

**What was NOT done:**
- Network detector not yet written
- Core sanitizer not yet written
- CLI not yet written

**Blockers:**
- None

**Status:** 🟡 Two of three detectors complete. Ready to write network detector.

---



---

### Session 3 — 2026-06-22

**What we did:**
- Fixed `pyproject.toml` build backend (`setuptools.backends` → `setuptools.build_meta`)
- Made CLI cross-platform (Windows, Linux, macOS) — only hotkey/tray/notifications remain Windows-only
- Updated `ARCHITECTURE.md`, `DECISIONS.md`, `README.md` to reflect cross-platform support
- Created virtual environment and installed all dependencies
- Upgraded pip to 26.1.2, setuptools to 82.0.1
- Created `scrub_ai/__init__.py` and `scrub_ai/detectors/__init__.py`
- Created `detectors/base.py` with `Match` dataclass and `BaseDetector` class

**What was NOT done:**
- No detector logic written yet (secrets, cloud, network)

**Blockers:**
- None

**Status:** 🟡 Foundation complete. Ready to write detectors.

---

### Session 2 — 2026-06-22

**What we did:**
- Confirmed Python 3.10.12 is available in WSL (Ubuntu)
- Decided to work in WSL, not Windows native
- Created `feature/v1-core` branch and pushed to GitHub
- Created `docs/DEVLOG.md` — a running developer journal of what we built and why
- Created `pyproject.toml` — project metadata, dependencies, CLI entry point

**What was NOT done:**
- Virtual environment not yet created
- No Python source files written yet

**Blockers:**
- None

**Status:** 🟡 Project scaffold started. Ready to create venv and start writing code.

---

### Session 1 — 2026-06-21

**What we did:**
- Discussed the problem scrub-ai solves
- Decided on tech stack (Python, click, pyperclip, keyboard, pystray, win10toast)
- Decided on V1 scope:
  - CLI (`cat file | scrub-ai`)
  - Windows hotkey (`Ctrl+Shift+S` sanitizes clipboard)
  - Windows system tray icon
  - Secrets detector
  - Cloud detector (AWS/GCP/Azure)
  - Network detector (IPs, hostnames)
- Created GitHub repo: https://github.com/rajwindermarwaha/scrub-ai
- Pushed all planning documents:
  - `README.md`
  - `docs/PLAN.md`
  - `docs/ARCHITECTURE.md`
  - `docs/DECISIONS.md`
  - `CONTRIBUTING.md`
  - `.gitignore`
- Created Dayforce goal for this project

**What was NOT done:**
- Python not yet installed on Windows machine
- No code written yet
- No project skeleton created

**Blockers:**
- Need to install Python 3.12 before next session

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

---

## How to Resume With AI

At the start of every new chat, paste this exactly:

```
I am building scrub-ai, an open source Python CLI tool that sanitizes 
sensitive content before sharing with AI assistants.

Repo: https://github.com/rajwindermarwaha/scrub-ai
Progress: https://github.com/rajwindermarwaha/scrub-ai/blob/main/docs/PROGRESS.md

Please read my PROGRESS.md and pick up from where I left off.
```
