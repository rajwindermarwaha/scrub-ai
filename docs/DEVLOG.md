# scrub-ai — Developer Log

A running log of every step taken to build scrub-ai, what was done, and why.

---

## Step 1 — Project planning docs pushed to GitHub
**What:** Created README, PLAN, ARCHITECTURE, DECISIONS, CONTRIBUTING, and .gitignore. Pushed to GitHub.

**Why:** Before writing any code, document the problem, the solution, the tech stack, and the architecture. This prevents wasted effort building the wrong thing. It also makes the repo look credible from day one.

---

## Step 2 — Created `feature/v1-core` branch
**What:** Created a new Git branch called `feature/v1-core` and pushed it to GitHub.

**Why:** All v1 code goes on this branch, not on `main`. This keeps `main` stable and clean. The rule is: only merge into `main` when the feature is fully working and tested. This is standard Git workflow (called feature branching).

---

## Step 3 — Created `pyproject.toml`
**What:** Created the project configuration file at the root of the repo.

**Why:** This is the modern Python packaging standard. It does 3 things:
1. Lists all dependencies so `pip install scrub-ai` automatically installs them
2. Registers the `scrub-ai` terminal command, pointing it to `scrub_ai/cli.py → main()`
3. Contains metadata (name, version, author) that PyPI uses to display the package page

**Key decisions:**
- `requires-python = ">=3.10"` — we use modern type hints available from 3.10+
- `win10toast`, `keyboard`, `pystray` are runtime deps — needed on the user's machine
- `pytest` is a dev-only dep under `[project.optional-dependencies]` — not installed for end users

---

## Step 4 — Made CLI cross-platform
**What:** Removed Windows-only platform markers from `pystray` and `Pillow`. Kept markers only on `win10toast` and `keyboard`. Updated classifiers, README, ARCHITECTURE, and DECISIONS docs.

**Why:** During venv setup, `win10toast` pulled in `pypiwin32` which is Windows-only and failed to install on WSL/Linux. This forced us to reconsider the platform strategy.

**Decision:** The CLI and all detectors are pure Python — there is no reason to restrict them to Windows. Only the hotkey and toast notification features are genuinely Windows-only. Making the CLI cross-platform from day one widens the audience and unblocks development on Linux/macOS.

**What is Windows-only:** `scrub-ai --start` (hotkey + tray + notifications)

**What works everywhere:** All CLI flags, all detectors

---
