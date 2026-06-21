# scrub-ai — Progress Log

This file is updated after every working session.
When starting a new session with AI, share this file so it knows exactly where to pick up.

---

## ⏩ NEXT SESSION — START HERE

### What to do first
1. Verify Python is installed
```bash
python --version
# Expected: Python 3.12.x
```
2. If not installed → go to https://www.python.org/downloads/windows/
   - Tick **"Add python.exe to PATH"** before installing
   - Install to `C:\Python312\`
3. Once Python is confirmed → tell AI **"Python is ready, let's start Step 2"**

### Step 2 will be
- Create a virtual environment
- Create `pyproject.toml`
- Create the full folder structure
- Create `scrub_ai/__init__.py`

---

## Session Log

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
| 2 | Install Python 3.12 on Windows | - | ⏳ Pending |
| 3 | Create virtual environment | - | ⏳ Pending |
| 4 | Create `pyproject.toml` | - | ⏳ Pending |
| 5 | Create project folder structure | - | ⏳ Pending |
| 6 | Write `detectors/base.py` | - | ⏳ Pending |
| 7 | Write `detectors/secrets.py` | - | ⏳ Pending |
| 8 | Write `detectors/cloud.py` | - | ⏳ Pending |
| 9 | Write `detectors/network.py` | - | ⏳ Pending |
| 10 | Write `sanitizer.py` | - | ⏳ Pending |
| 11 | Write `cli.py` | - | ⏳ Pending |
| 12 | Write `notifier.py` | - | ⏳ Pending |
| 13 | Write `hotkey.py` | - | ⏳ Pending |
| 14 | Write `tray.py` | - | ⏳ Pending |
| 15 | Write tests + fixtures | - | ⏳ Pending |
| 16 | Publish to PyPI | - | ⏳ Pending |

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
