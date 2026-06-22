# scrub-ai — Progress Log

This file is updated after every working session.
When starting a new session with AI, share this file so it knows exactly where to pick up.

---

## ⏩ NEXT SESSION — START HERE

### What to do first
1. Check out the feature branch
```bash
git checkout feature/v1-core
```
2. Create a virtual environment and install dev dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```
3. Once done → tell AI **"venv is ready, let's continue"**

### Step 4 will be
- Create the full folder structure (`scrub_ai/`, `tests/`, etc.)
- Create `scrub_ai/__init__.py`
- Then start writing `detectors/base.py`

---

## Session Log

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
| 6 | Create virtual environment | - | ⏳ Pending |
| 7 | Create project folder structure | - | ⏳ Pending |
| 8 | Write `scrub_ai/__init__.py` | - | ⏳ Pending |
| 9 | Write `detectors/base.py` | - | ⏳ Pending |
| 10 | Write `detectors/secrets.py` | - | ⏳ Pending |
| 11 | Write `detectors/cloud.py` | - | ⏳ Pending |
| 12 | Write `detectors/network.py` | - | ⏳ Pending |
| 13 | Write `sanitizer.py` | - | ⏳ Pending |
| 14 | Write `cli.py` | - | ⏳ Pending |
| 15 | Write `notifier.py` | - | ⏳ Pending |
| 16 | Write `hotkey.py` | - | ⏳ Pending |
| 17 | Write `tray.py` | - | ⏳ Pending |
| 18 | Write tests + fixtures | - | ⏳ Pending |
| 19 | Publish to PyPI | - | ⏳ Pending |

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
