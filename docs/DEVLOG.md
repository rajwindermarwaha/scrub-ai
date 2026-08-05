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

## Step 5 — Created `scrub_ai/__init__.py` and `scrub_ai/detectors/__init__.py`
**What:** Created `__init__.py` files in both `scrub_ai/` and `scrub_ai/detectors/`.

**Why:** In Python, a folder is just a folder unless it has an `__init__.py` inside it. That file is what makes it a package — meaning Python can import from it. `scrub_ai/__init__.py` also holds the version number as the single source of truth.

---

## Step 6 — Created `detectors/base.py`
**What:** Created the base detector class and the `Match` dataclass.

**Why:** All detectors (secrets, cloud, network) share the same loop logic — iterate patterns, find matches, return results. Writing this once in a base class avoids repetition. Each detector just defines its patterns and inherits the rest. The `Match` dataclass is a simple container representing one detected item — position, original text, replacement, category, and label.

---

## Step 4 — Made CLI cross-platform
**What:** Removed Windows-only platform markers from `pystray` and `Pillow`. Kept markers only on `win10toast` and `keyboard`. Updated classifiers, README, ARCHITECTURE, and DECISIONS docs.

**Why:** During venv setup, `win10toast` pulled in `pypiwin32` which is Windows-only and failed to install on WSL/Linux. This forced us to reconsider the platform strategy.

**Decision:** The CLI and all detectors are pure Python — there is no reason to restrict them to Windows. Only the hotkey and toast notification features are genuinely Windows-only. Making the CLI cross-platform from day one widens the audience and unblocks development on Linux/macOS.

**What is Windows-only:** `scrub-ai --start` (hotkey + tray + notifications)

**What works everywhere:** All CLI flags, all detectors

---

## Step 7 — Created `detectors/secrets.py`
**What:** Created the first concrete detector — `SecretsDetector` — with 6 compiled regex patterns.

**Patterns added:**
| Label | What it detects |
|---|---|
| `private_key` | PEM private key blocks (`-----BEGIN ... PRIVATE KEY-----`) |
| `jwt` | JSON Web Tokens (three base64url segments starting with `eyJ`) |
| `bearer_token` | HTTP `Authorization: Bearer <token>` headers |
| `api_key` | Key/value pairs like `api_key=...`, `access_token=...`, `secret_key=...` |
| `password` | Key/value pairs like `password=...`, `passwd=...`, `pwd=...` |
| `hex_token` | Raw 32–64 char lowercase hex strings used as tokens |

**Why these patterns:** These are the most common secrets that appear in logs, stack traces, and config files pasted into AI tools. PEM keys and JWTs have fixed structural signatures that make them easy to detect reliably. API keys and passwords are caught via named key=value context to reduce false positives. Hex tokens cover generic high-entropy values that don't match a named pattern.

**Design:** Follows the `BaseDetector` pattern — defines `patterns` as a class attribute, inherits `detect()`. `priority = 1` means it runs before cloud and network detectors.

---

## Step 8 — Created `detectors/cloud.py`
**What:** Created `CloudDetector` with 12 regex patterns covering the three major cloud providers.

**AWS patterns (5):**
- Access Key IDs — fixed prefixes (`AKIA`, `ASIA`, `AROA`, etc.) followed by 16 uppercase alphanumeric chars. Very low false-positive rate due to the distinctive prefix.
- Secret Access Keys — 40-char base64 string in `aws_secret_access_key=` context.
- Account IDs — 12-digit numbers in `account_id=` / `aws_account=` context.
- ARNs — full `arn:aws:service:region:accountid:resource` format. Structural match, very reliable.
- Session tokens — long base64 strings (100–300 chars) in `aws_session_token=` context.

**GCP patterns (3):**
- API keys — `AIza` prefix followed by 35 alphanumeric chars. Fixed structure, no false positives.
- Service account emails — `...@project.iam.gserviceaccount.com` domain is unique to GCP.
- Project IDs — lowercase alphanumeric+hyphen strings in `project_id=` / `gcp_project=` context.

**Azure patterns (4):**
- Subscription / Tenant / Client IDs — UUIDs detected only in named context to avoid flagging random UUIDs.
- Client secrets — 34+ char strings in `client_secret=` context.
- Storage connection strings — `DefaultEndpointsProtocol=https;AccountName=...;AccountKey=...` format.
- SAS tokens — multi-parameter query strings with `sv=`, `se=`, `sr=`, `sp=`, `sig=` components.

**Why cloud-specific patterns matter:** Cloud credentials (ARNs, access keys, GCP service accounts) are extremely common in SRE/DevOps workflows — `aws sts`, `kubectl`, Terraform output all contain them. They are high-severity leaks because they can grant direct access to production infrastructure.

---

## Step 9 — Created `detectors/network.py`
**What:** Created `NetworkDetector` with 4 regex pattern groups:
- IPv4 addresses
- IPv6 addresses (full and compressed forms)
- Internal hostnames (`*.internal`, `*.local`, `*.corp`, `*.lan`, `*.home.arpa`, and `localhost`)
- Internal URLs (localhost, RFC1918 private ranges, and internal host suffixes)

**Why:** Network identifiers are common in logs and stack traces shared with AI assistants. Even when they are not direct credentials, they leak internal topology (host naming conventions, private address ranges, service endpoints), which is sensitive operational metadata.

**Design:** `priority = 3`, so network masking runs after secrets and cloud patterns. This helps preserve higher-severity matches when patterns overlap.

---

## Step 10 — Created `sanitizer.py`
**What:** Implemented the core sanitizer engine with:
1. Detector execution in priority order
2. Match collection across all detectors
3. Overlap resolution (higher confidence wins; deterministic tie behavior)
4. Replacement application from end-to-start to avoid index drift
5. Report generation (`total_matches`, `by_category`, `by_label`, `is_clean`)

Also added a convenience helper:
- `sanitize_text(text) -> (clean_text, report)`

**Why:** This is the central orchestration layer of scrub-ai. Detectors only find sensitive spans; the sanitizer is what turns detections into safe output plus an auditable summary.

---

## Step 11 — Added tests for network + sanitizer
**What:** Added two test modules:
- `tests/test_network_detector.py` to verify IPv4/IPv6/internal hostname/internal URL detection
- `tests/test_sanitizer.py` to verify replacement/report behavior and overlap resolution

During testing, one overlap assertion initially failed due to incorrect character span boundaries in the test fixture. The spans were corrected, and the suite passed.

**Result:**
- `pytest -q` → `4 passed`

**Why:** These tests establish confidence in the first complete vertical slice of the core product: detection + sanitization + report generation.

---

## Step 12 — Added tests for `secrets.py`, `cloud.py`, and `base.py`
**What:** Added three new test modules:
- `tests/test_secrets_detector.py`
- `tests/test_cloud_detector.py`
- `tests/test_base_detector.py`

Coverage now includes:
- Shared base detector behavior
- All detector categories (secrets, cloud, network)
- Sanitizer orchestration and overlap logic

**Result:**
- `pytest -q` → `11 passed`

**Why:** Until this step, tests focused on network + sanitizer. Adding direct tests for secrets/cloud/base improves confidence, makes failures easier to localize, and lowers refactor risk.

---

## Step 14 — Wrote `cli.py` — CLI entry point

**What:** Implemented `scrub_ai/cli.py` using `click` with three flags:
- `--file` — read input from a file path
- `--dry-run` — show what would be detected without changing the output text
- `--copy` — copy the sanitized output to the system clipboard via `pyperclip`

Stdin pipe is auto-detected when no `--file` is given and a pipe is present.  
Detection summary is always written to stderr so it doesn't pollute piped output.

Also added `tests/test_cli.py` with 4 tests covering all CLI code paths.

**Result:**
- `pytest -q` → `15 passed`

**Why:** The CLI is the primary user-facing interface of scrub-ai. Without it, the detectors and sanitizer have no way to be invoked from the terminal. This step wires the whole core stack together end-to-end.

---

## Step 13 — Hardened test fixtures for GitHub secret scanning
**What:** After a GitHub push-protection warning, updated test fixtures to avoid direct hardcoded secret-like signatures while preserving detector behavior.

Examples of hardening:
- Compose sensitive-looking prefixes at runtime (instead of plain literals)
- Split key names/signatures in test setup strings
- Keep semantic test intent unchanged

**Why:** Some detector tests intentionally include secret-shaped text, which can trigger platform-level secret scanning even when values are synthetic. Hardening fixture construction reduces false positives and keeps CI/push flows smooth.

---

## Step 15 — Created `config.py` — persistent user settings

**What:** Implemented a small config layer that reads and writes a JSON file:
- Windows: `%APPDATA%\scrub-ai\config.json`
- Linux/macOS: `~/.config/scrub-ai/config.json`

**Keys stored in v1:**
| Key | Type | Default | Purpose |
|---|---|---|---|
| `enabled` | bool | `true` | whether the hotkey listener is active |
| `hotkey` | str | `"ctrl+alt+s"` | the keyboard shortcut |

**Public helpers:** `load()`, `save()`, `is_enabled()`, `set_enabled()`, `get_hotkey()`

**Why:** The tray and hotkey modules need to share state across threads without passing arguments. A tiny JSON config file is the simplest possible persistent store — no database, no registry, portable across reinstalls.

---

## Step 16 — Created `notifier.py` — Windows toast notifications

**What:** Implemented `notify(report)` which shows a win10toast desktop notification summarising a sanitization event.

**Behaviour:**
- If `total_matches == 0`: "Clipboard is clean — nothing was masked."
- Otherwise: "Masked N value(s): label1=count, label2=count"

**Platform guard:** The function is a no-op on non-Windows platforms and if win10toast is not installed. All failures are swallowed (best-effort — a failed notification must never crash the caller).

**Why:** The user needs immediate feedback that the hotkey fired and something was redacted. A toast is unobtrusive and native to Windows, which is the target platform for the background service.

---

## Step 17 — Created `hotkey.py` — Ctrl+Alt+S global hotkey listener

**What:** Implemented `start(hotkey)` and `stop()` using the `keyboard` library.

**Flow when hotkey fires:**
1. Check `config.is_enabled()` — bail out if disabled
2. Read clipboard via `pyperclip.paste()`
3. Sanitize with `sanitize_text()`
4. Write clean text back via `pyperclip.copy()`
5. Call `notify(report)` for the toast

**Threading:** `start()` blocks on a `threading.Event`; `stop()` sets the event and `keyboard.unhook_all()` releases the hook. Designed to run in a daemon thread started by `tray.py`.

**Platform guard:** Returns immediately on non-Windows.

**Why:** The hotkey is the core UX of the Windows background service — one keystroke sanitizes the clipboard invisibly, with no context switching needed.

---

## Step 18 — Created `tray.py` — system tray icon and menu

**What:** Implemented `start()` using `pystray` and `Pillow`.

**Menu items:**
| Item | Behaviour |
|---|---|
| Enabled: ON/OFF | Toggles `config.is_enabled()` and refreshes the menu label |
| Hotkey: CTRL+ALT+S | Static label showing the active shortcut (disabled/informational) |
| *(separator)* | |
| Quit | Calls `hotkey.stop()` then `icon.stop()` |

**Icon:** Loads `assets/icon.png` if present; otherwise generates a 64×64 programmatic fallback (dark blue square with white border) so the tray always has a visible icon even without bundled assets.

**Threading:** Spawns the hotkey listener in a daemon thread before entering the blocking `icon.run()` loop.

**Platform guard:** Returns immediately on non-Windows.

**Why:** A system tray icon is the standard Windows pattern for background services. It gives the user a visible reminder the tool is running and a reliable way to disable or quit without needing the terminal.

---

## Step 19 — Added `--start` flag to `cli.py`

**What:** Added a `--start` boolean flag to the `main()` click command.

**Behaviour:**
- On Windows: prints a startup message to stderr, then calls `tray.start()` (which blocks until Quit is selected)
- On non-Windows: raises a `ClickException` with a clear message

**Why:** The CLI is the single entry point for the tool. `--start` activates the full Windows background service from one command: `scrub-ai --start`. All other flags (--file, --dry-run, --copy) remain unaffected.

---

## Step 20 — Windows runtime verified, test suite clean

**What:** Ran full test suite after all Windows runtime modules were added.

**Result:** `pytest -q` → `15 passed`

**Why:** Confirming zero regressions after adding four new modules and modifying `cli.py`.

---

## Step 21 — Wrote `tests/test_notifier.py` — 18 tests

**What:** Full test coverage for `notifier.py`.

**Test groups:**
- `TestBuildMessage` — pure function tests: zero matches, label sorting, single match, generic fallback
- `TestNotifyPlatformGuard` — verifies no-op on Linux and macOS (mocking `sys.platform`)
- `TestNotifyWindows` — verifies correct `win10toast` call arguments (title, message, duration, threaded) using a fake injected module
- `TestNotifyResilience` — swallows `show_toast` exceptions, `ImportError`, non-dict `by_label`, and missing report keys

**Result:** `pytest tests/test_notifier.py -v` → `18 passed`

**Why:** The notifier is entirely untestable on Linux without mocking. These tests give confidence that the right message is built and the right calls are made, without needing a real Windows environment.

---

## Step 22 — Wrote `tests/test_config.py` — 18 tests

**What:** Full test coverage for `config.py`.

**Test groups:**
- `TestConfigDir` — platform-specific path selection (Windows APPDATA, Linux XDG, APPDATA fallback)
- `TestLoad` — defaults when file missing, corrupt JSON recovery, key merging, extra keys preserved
- `TestSave` — writes valid JSON, creates parent dirs, round-trip, overwrites existing file
- `TestIsEnabled` / `TestGetHotkey` — helper behaviour and persistence to disk

**Key technique:** An `autouse` fixture redirects `_config_path` to a `tmp_path` for every test, so no test ever touches the real config file on disk.

**Result:** `pytest tests/test_config.py -v` → `18 passed`

**Why:** Config correctness is critical — a bug here could silently disable the hotkey or use the wrong shortcut. Tests cover every code path including error recovery.

---

## Step 23 — Wrote `tests/test_hotkey.py` — 13 tests

**What:** Full test coverage for `hotkey.py`.

**Test groups:**
- `TestHandleHotkeyHappyPath` — sanitizes clipboard and writes back; clean text round-trips unchanged
- `TestHandleHotkeyEarlyExit` — does nothing when disabled; does nothing when clipboard is empty
- `TestHandleHotkeyResilience` — swallows paste exceptions; swallows copy exceptions; still calls notify even if copy fails
- `TestStart` — no-op on Linux/macOS; registers hotkey with fake `keyboard` module; uses configured shortcut; no-op when `keyboard` not importable
- `TestStop` — sets the threading event

**Key technique:** A fake `keyboard` module is injected via `patch.dict(sys.modules)`. `start()` is run in a daemon thread so `stop()` can unblock it, testing the full blocking-loop lifecycle.

**Result:** `pytest tests/test_hotkey.py -v` → `13 passed`

---

## Step 24 — Full suite green: 62 passed

**What:** Ran the complete test suite after all new test files were added.

**Result:** `pytest -q` → `62 passed in 0.44s`

**Why:** Confirming all 62 tests across 9 test files pass with zero failures or warnings.

---

## Step 25 — Created `assets/icon.png`

**What:** Generated a 64×64 RGBA PNG tray icon programmatically using Pillow.

**Design:**
- Dark blue rounded square background (RGB 25, 90, 170)
- White shield polygon centred in the square
- Blue "S" cutout inside the shield using two arcs and connecting strokes

**Why:** pystray requires a PIL Image for the tray icon. Without a real icon file the tool falls back to the plain blue square defined in `tray.py`. This gives the published tool a recognisable identity in the system tray.

---

## Step 26 — Polished `README.md` for PyPI

**What:** Updated the README with:
- Added CI badge linking to the GitHub Actions workflow
- Removed PII (email/phone) from the features list — that is a v1.1 item, not in v1
- Fixed the example to match the actual v1 CLI output format (real label names, stderr summary line)
- Updated the detection table to reflect real v1 detectors only
- Marked v1.0 as complete `[x]` in the roadmap

**Why:** The README is the PyPI project page. Everything on it should be accurate for what ships in v1 — listing features that don't exist yet damages credibility.

## Step 27 — Added confidence scoring to all detectors

**What:** Added a `confidence: float` field to the `Match` dataclass and assigned a score to every pattern across `secrets.py`, `cloud.py`, and `network.py`.

**Score rationale:**
- Structural patterns with fixed prefixes (AWS access keys `AKIA*`, GCP keys `AIza*`, JWTs `eyJ*`) → `0.99` — near-zero false-positive rate
- Named key=value context patterns (password=, api_key=, aws_secret_access_key=) → `0.95`
- Heuristic patterns (hex tokens, internal hostnames) → `0.75–0.85` — higher false-positive risk

**CLI flag added:** `--min-confidence FLOAT` — filters out any match below the threshold before replacement. Default `0.0` (all matches pass through).

**Why:** Not all detections are equally reliable. A hex token match on a log line is much noisier than an `AKIA`-prefixed AWS key. Confidence scoring lets users tune the signal-to-noise ratio without disabling entire detectors.

---

## Step 28 — Created `detectors/custom.py` — user-defined patterns

**What:** Implemented `CustomDetector` which loads patterns from a JSON file at runtime:
- Linux/macOS: `~/.config/scrub-ai/patterns.json`
- Windows: `%APPDATA%\scrub-ai\patterns.json`

**JSON schema per entry:** `pattern` (regex), `replacement`, `label`, `confidence` (optional, default 1.0)

**Behaviour:** File is read on every `detect()` call — no restart needed after editing. Invalid JSON or missing file is silently ignored.

**Why:** scrub-ai cannot know every internal identifier (ticket IDs, internal service names, employee IDs). Custom patterns let teams extend detection without forking the package or waiting for a release.

---

## Step 29 — Created `detectors/pii.py` — PII detection via Presidio

**What:** Implemented `PiiDetector` using Microsoft Presidio Analyzer with spaCy `en_core_web_lg`.

**Entities detected:** `PERSON`, `EMAIL_ADDRESS`, `PHONE_NUMBER`

**Behaviour:**
- If `presidio-analyzer` or `spacy` is not installed, `PiiDetector` is a no-op — no import error, no crash
- If the spaCy model is missing, Presidio raises on init — caught and suppressed
- Presidio results are converted to `Match` objects with character offsets

**Why optional:** The spaCy `en_core_web_lg` model is ~400 MB. Making it a hard dependency would make `pip install scrub-ai` unacceptably slow for users who only need secrets/cloud/network detection. The `[pii]` extras group keeps it opt-in.

**Why Presidio over regex for PII:** Names cannot be reliably detected with regex. Presidio uses NER (Named Entity Recognition) via spaCy, which understands linguistic context. "John Smith" is a name; "Smith & Wesson" is a brand. Regex cannot distinguish these.

---

## Step 30 — Created `profiles.py` — named detector profiles

**What:** Implemented a profile registry that maps profile names to detector subsets:

| Profile | Detectors active |
|---|---|
| `aws` | `CloudDetector` (AWS patterns only) |
| `k8s` | `SecretsDetector`, `NetworkDetector` |
| `secrets` | `SecretsDetector`, `CustomDetector`, `PiiDetector` |
| `network` | `NetworkDetector` |

**CLI flag added:** `--profile NAME` — activates only the detectors for that profile. Without `--profile`, all detectors run.

**Why:** A DevOps engineer debugging a Kubernetes issue doesn't want IP addresses masked in every log line — they want secrets masked. A developer reviewing AWS CLI output doesn't want phone numbers flagged. Profiles reduce noise by scoping detection to what's relevant for the task.

---

## Step 28 — Published to PyPI

**What:**
1. Installed `build` and `twine` into the venv
2. Ran `python -m build` — produced `scrub_ai-1.0.0-py3-none-any.whl` and `scrub_ai-1.0.0.tar.gz` in `dist/`
3. Uploaded to TestPyPI with `twine upload --repository testpypi dist/*` and verified install
4. Uploaded to real PyPI with `twine upload dist/*`
5. Verified `pip install scrub-ai` from outside the venv — downloaded from PyPI, sanitization worked correctly

**Live at:** https://pypi.org/project/scrub-ai/1.0.0/

**Why TestPyPI first:** TestPyPI is a sandbox that mirrors real PyPI. Uploading there first catches packaging mistakes (missing files, bad metadata) without wasting the real version number.

**Why `__token__` as username:** PyPI no longer accepts passwords for uploads. All uploads must use API tokens. The username is always the literal string `__token__` and the password is the token value.

---

## Step 31 — Updated `config.py` for watch mode

**What:**
- Added `watch_mode: False` to `_DEFAULTS`
- Added `is_watch_mode()` helper — returns current watch mode state from disk
- Added `set_watch_mode()` helper — persists watch mode state to disk
- Updated docstring

**Why:** `tray.py` needs to read and write watch mode state across threads without passing arguments. Same pattern used for `enabled` and `hotkey` keys already in config.

---

## Step 32 — Created `watcher.py` + tests

**What:** Implemented clipboard polling loop:
- Checks clipboard every 500ms via `pyperclip`
- Sanitizes automatically when content changes
- Only writes back and notifies if something was actually masked
- `cfg.is_watch_mode()` checked inside the loop — toggling watch mode from tray takes effect instantly without restarting the thread
- `_stop_event.wait(timeout=0.5)` instead of `time.sleep()` — shutdown is instant when `stop()` is called
- Stores `clean_text` (not `current`) as `last_text` to prevent re-sanitizing on the next poll

**Tests added:**
- `tests/test_config.py` — `TestIsWatchMode` (5 tests): default false, set true/false, persists to disk, does not affect other keys
- `tests/test_watcher.py` — 10 tests: sanitizes on change, skips clean text, skips same text twice, skips when watch mode off, skips empty clipboard, swallows paste/copy exceptions, start/stop threading

**Result:** `32 passed`

**Why cross-platform:** Watch mode only uses `pyperclip` which works on Windows, Linux, and macOS. Unlike `hotkey.py` which requires the `keyboard` library (Windows only), there is no platform restriction here.

**Why keep `hotkey.py`:** Hotkey and watch mode serve different use cases. Hotkey = manual control. Watch mode = fully automatic. They complement each other.

---

## Step 30 — Updated branding: new icon + tagline

**What:**
- Replaced `assets/icon.png` with a new design: classic pointed-bottom shield with a lightning bolt cutout inside
- Updated `assets/generate_icon.py` to draw the new design programmatically
- Updated fallback icon in `scrub_ai/tray.py` to match (shield + bolt instead of "S")
- New tagline: **"Shield your prompts."**
- Updated README.md feature emojis: 🛡️ secrets, 📡 network, 🕵️ PII
- Published LinkedIn post announcing scrub-ai

**Why:** The original icon had a blue "S" cutout which didn't communicate the tool's purpose visually. The new shield + lightning bolt design reads as "fast security" at a glance — more aligned with the tool's identity. The tagline "Shield your prompts." ties the icon, the name, and the purpose together in four words.

---


**What:** Merged `feature/v1-windows` into `main`. v1.0 is the stable, published release on `main`.

**Why:** `main` is kept clean and only receives merges of complete, tested, published features. Every commit on `main` represents a shippable state.

---

**What:** GitHub Actions workflow that runs on every push to `main`/`feature/**` and on PRs to `main`.

**Matrix:** Python 3.10, 3.11, 3.12 on `ubuntu-latest`  
**Steps:** checkout → setup-python → `pip install -e ".[dev]"` → `pytest -q`

**Why:** CI is a hard requirement before publishing. It:
1. Proves the package installs cleanly from `pyproject.toml` on a fresh machine
2. Protects `main` from broken merges
3. Shows the green badge on PyPI and GitHub, which signals to users that the tool is maintained

---

## Step 33 — Wired watch mode into `tray.py` + wrote `tests/test_tray.py`

**What:** Two changes in one step:

**`tray.py` updates:**
- Imported `scrub_ai.watcher` as `watcher_mod`
- Added `_toggle_watch_mode(icon, item)` — flips `cfg.is_watch_mode()` and calls `icon.update_menu()`
- Added `_watch_mode_label(item)` — returns `"Watch Mode: ON"` or `"Watch Mode: OFF"` based on config
- Added `watcher_mod.stop()` call inside `_quit_app()` — ensures watcher thread exits cleanly on Quit
- Spawned a second daemon thread (`scrub-ai-watcher`) that runs `watcher_mod.start()` alongside the existing hotkey thread
- Added `Watch Mode: ON/OFF` toggle as a menu item between the hotkey label and Quit

**`tests/test_tray.py` created — 16 tests:**
| Group | Tests |
|---|---|
| `TestEnabledLabel` | ON when enabled, OFF when disabled |
| `TestWatchModeLabel` | ON when active, OFF when inactive |
| `TestToggleEnabled` | flips true→false, false→true; calls `update_menu` |
| `TestToggleWatchMode` | flips false→true, true→false; calls `update_menu` |
| `TestQuitApp` | stops hotkey + watcher + icon; correct call order |
| `TestMakeIcon` | returns 64×64 image when icon.png missing; loads real file |
| `TestStartPlatformGuard` | no-op on Linux, macOS, and when pystray not importable |
| `TestStartIntegration` | both daemon threads spawned; `icon.run()` called |

**Key technique:** Config tests use `monkeypatch.setattr(cfg, "_config_path", lambda: tmp_path / "config.json")` — matching the pattern from `test_config.py`. Platform guard tests use `patch.object(sys, "platform", ...)`. The integration test injects a fake `pystray` module and a `_FakeThread` class to capture which thread names were started without running any real threads.

**Result:** `pytest -q` → `124 passed in 0.56s`

**Why:** `tray.py` is the central coordinator of the background service. Now that it manages three subsystems (hotkey, watcher, icon), it needed tests that verify each subsystem is started and stopped correctly and that menu labels reflect live config state.

## Step 34 — Added `--watch` flag to `cli.py`

**What:** Added `--watch` boolean flag to the `main()` click command.

**Behaviour:**
1. Sets `cfg.set_watch_mode(True)` — watcher loop reads this to activate sanitization
2. Prints "Watch mode ON" message to stderr
3. Calls `watcher.start()` — blocks until interrupted
4. `KeyboardInterrupt` (Ctrl+C) is caught silently
5. `finally` block calls `watcher.stop()` and `cfg.set_watch_mode(False)` — always cleans up
6. Prints "Watch mode OFF" to stderr

**Why cross-platform:** Unlike `--start`, watch mode only uses `pyperclip` — no platform guard needed. Works on Windows, Linux, and macOS.

**Tests:** `tests/test_cli_v12.py` — 3 tests covering watcher invocation, config state lifecycle, and user messages.

**Result:** `pytest -q` → `127 passed`

---

## Step 35 — Updated `README.md` for v1.2

**What:** Full README rewrite for clarity. Key changes:
- Install section split into standard vs PII tiers with numbered steps
- Usage reorganized into 4 logical sections: Basic, Filtering, Watch mode, Hotkey+tray
- PII detection given its own dedicated section with an input/output table
- Custom patterns field reference table added (was undocumented)
- Watch mode section added (was missing entirely)
- Contributing section updated with venv creation + spaCy download steps
- Roadmap: marked v1.2 as `[x]` complete

**Why:** The previous README had PII install steps mixed into the install section with no explanation of what PII actually detects. Watch mode had no documentation. The contributing section assumed you already had a venv. All of these are friction points for new users and contributors.

---

## Step 36 — Created `.github/workflows/publish.yml` — manual publish workflow

**What:** GitHub Actions workflow with two jobs:

| Job | Trigger | Target |
|---|---|---|
| `publish-test` | Manual (`workflow_dispatch`) | TestPyPI |
| `publish-pypi` | After `publish-test` succeeds | PyPI (gated by `release` environment approval) |

**`workflow_dispatch` input:** `version` (e.g. `1.2.0`) — for reference/traceability, does not auto-tag.

**Secrets used:**
- `TEST_PYPI_API_TOKEN` — stored in GitHub repo secrets
- `PYPI_API_TOKEN` — stored in GitHub repo secrets

**Approval gate:** `publish-pypi` job uses `environment: release`. The `release` environment has required reviewer set to the repo owner — GitHub pauses and sends an approval request before the PyPI job runs.

**Why `workflow_dispatch` instead of tag push:** Publish should be a deliberate action, not a side effect of pushing a tag. This gives full control over when a release goes out.

**Why TestPyPI first:** Catches packaging mistakes (missing files, bad metadata, import errors) before spending the real version number on PyPI.

## Step 37 — Created `feature/v2.0-vscode-extension` branch + updated all docs

**What:**
- Created and pushed `feature/v2.0-vscode-extension` branch
- Updated `docs/ARCHITECTURE.md` — added VS Code extension to overview, project structure, component descriptions, and tech stack table
- Updated `docs/PLAN.md` — expanded Phase 4 with v2.0 details, added Phase 5 (browser extension) and Phase 6 (team features), updated progress log
- Updated `docs/DECISIONS.md` — added D009 (subprocess over TypeScript rewrite), D010 (diff view before applying changes), D011 (same repo)
- Updated `README.md` — fixed watch mode section with correct Windows command (`python -m scrub_ai.cli --watch`) in both the prerequisites table and the install table

**Why document before coding:** Architecture and decision docs written before implementation prevent wasted effort and make the reasoning behind every choice traceable. Same principle applied here as in Session 1.

**Key decisions recorded:**
- Extension calls Python CLI as subprocess — no logic duplication, 127 tests already cover detection
- Diff view before applying changes — editor context demands more care than clipboard sanitization
- Same repo (`vscode-extension/` subfolder) — one place to maintain, version, and file issues

## Step 38 — Installed Node 20 + yo + generator-code

**What:**
- Node 18 (installed via apt) was rejected by `generator-code` — requires Node >=20
- Installed Node 20.20.2 via nvm: `nvm install 20 && nvm use 20`
- Installed scaffolding tools globally: `npm install -g yo generator-code`
- 638 packages installed, npm 10.8.2

**Why:** `yo` + `generator-code` is the official VS Code extension scaffolding tool. It generates the correct `package.json` structure, `tsconfig.json`, activation events, and `src/extension.ts` boilerplate that the VS Code Marketplace build pipeline expects. Doing this manually would risk missing required fields.

**Next:** Run `yo code` inside `vscode-extension/` to generate the extension skeleton.

## Step 39 — Scaffolded and implemented VS Code extension

**What:**
- Ran `yo code` inside `vscode-extension/` — generated TypeScript extension skeleton (no bundler)
- Wired `package.json`:
  - Publisher: `rajwindermarwaha`
  - Commands: `scrub-ai.sanitize` ("Scrub AI: Sanitize Selection") and `scrub-ai.sanitizeFile` ("Scrub AI: Sanitize File")
  - Keybinding: `Ctrl+Alt+S` → `scrub-ai.sanitize` (when `editorTextFocus`)
  - `activationEvents: ["onStartupFinished"]` — extension activates on startup
  - Engine: `^1.113.0` — lowered from scaffolded `^1.125.0` to match installed VS Code
  - Icon: `icon.png` (copied from `assets/icon.png`)
- Implemented `src/extension.ts`:
  - `findCli()` — tries `python -m scrub_ai.cli`, then `python3 -m scrub_ai.cli`, then `wsl python3 -m scrub_ai.cli`; returns null if none found
  - `ensureCli()` — calls `findCli()`; if null, prompts user to install; runs `pip install scrub-ai` with a progress notification; re-checks after install
  - `runScrubAi()` — spawns CLI as subprocess via `spawn()`, writes input to stdin, collects stdout
  - `sanitizeText()` — compares original vs sanitized; if different, offers "Show Diff / Apply / Cancel"; diff view uses `vscode.diff` with two in-memory documents; applies to selection or full document
- Updated `.vscodeignore` — added `node_modules/**`

**Why subprocess over TypeScript rewrite:** The Python CLI already has 127 passing tests covering all detection logic. Calling it as a subprocess means zero logic duplication and the extension automatically benefits from future CLI improvements (new detectors, profiles, custom patterns).

**Why `python -m scrub_ai.cli` over `scrub-ai`:** The `scrub-ai` entry point lives in Python's `Scripts/` folder which is often not on PATH on Windows. `python -m scrub_ai.cli` works as long as Python itself is on PATH, which is always true after a standard Python install.

**Why diff view:** Editors are higher-stakes than clipboard. Showing a diff before applying gives the user confidence that only sensitive content was changed and nothing else was altered.

**Result:** Extension tested end-to-end in Extension Development Host — sanitization, diff view, and apply all working correctly.

## Step 40 — Added clipboard watch mode to VS Code extension

**What:** Added automatic clipboard sanitization to the VS Code extension on activation.

- `startWatcher()` spawns `python -m scrub_ai.cli --watch` (or `python3`/WSL fallback) as a background subprocess when the extension activates
- The watcher process polls the clipboard every 500ms and sanitizes automatically when sensitive content is detected — same behaviour as `scrub-ai --watch` in the terminal
- Process is killed cleanly when the extension deactivates via `context.subscriptions.push({ dispose: () => watcherProcess.kill() })`
- If CLI is not found, `startWatcher()` fails silently — manual commands (`Ctrl+Alt+S`) still work

**Why:** The VS Code extension should provide the same zero-friction experience as the standalone watch mode. Users shouldn't need to remember to press a hotkey — sensitive content should be masked the moment it hits the clipboard.

**Why subprocess over VS Code clipboard API:** VS Code's clipboard API (`vscode.env.clipboard`) only reads/writes on demand — it has no change event. The Python watcher already implements reliable cross-platform polling. Reusing it via subprocess is consistent with D009 (no logic duplication in TypeScript).

---

## Step 41 — Added `--json` flag to `cli.py` for editor integration

**What:** Added a `--json` boolean flag to the `main()` click command.

**Behaviour:**
- Runs detection in dry-run mode (output text is unchanged)
- Writes all matches as a JSON array to stderr, one object per match:
  ```json
  [{"start": 12, "end": 47, "original": "...", "replacement": "[REDACTED]", "label": "password", "confidence": 0.95}]
  ```
- Fields: `start`, `end` (character offsets), `original`, `replacement`, `label`, `confidence`

**Why:** The VS Code extension needs exact character positions to create `DiagnosticCollection` entries (squiggly underlines in the editor). The existing stderr summary only gives label counts — not positions. `--json` exposes the raw `Match` objects so the extension can map them directly to `vscode.Range` values without any parsing heuristics.

**Why stderr:** stdout carries the sanitized text (used by pipe consumers). Mixing JSON into stdout would break all existing pipe usage. stderr is the correct channel for structured metadata.

---

## Step 42 — Added diagnostics + inline quick-fix to VS Code extension

**What:** Two major features added to `src/extension.ts`:

**Auto-scan diagnostics:**
- `scanDocument()` runs `scrub-ai --dry-run --json` on the active document's text
- Parses the JSON match array from stderr
- Creates a `vscode.DiagnosticCollection` entry for each match using the `start`/`end` character offsets
- Triggered on `onDidOpenTextDocument` and `onDidSaveTextDocument`
- Skips files >500 KB and ignored directories (`node_modules`, `.git`, `dist`, `build`, `.venv`, `__pycache__`)
- Scans 22 text-like file extensions (`.py`, `.ts`, `.js`, `.json`, `.yaml`, `.env`, `.log`, etc.)
- Result: yellow squiggly underlines + Problems panel entries for every detected sensitive value

**Inline quick-fix code actions:**
- `ScrubAiCodeActionProvider` registered for all file types
- 💡 lightbulb appears on every line that has a diagnostic
- "Mask [label] → [replacement]" applies the single fix in-place with one click
- "Mask all sensitive values in file" appears when multiple detections exist on the same line

**Why diagnostics:** Clipboard sanitization is reactive — it only fires after you copy. Diagnostics are proactive — they flag sensitive content the moment you open or save a file, before you ever copy anything. This is a fundamentally different (and more useful) UX for editor users.

**Why code actions over a command:** Code actions appear inline at the exact location of the problem. The user doesn't need to remember a command name or navigate to the Problems panel — the fix is one click away at the cursor.

---

## Step 43 — Fixed cross-platform CLI detection + added status bar indicator

**What:** Two changes to `src/extension.ts`:

**`findCli()` rewrite — platform-aware probing:**
- Windows (extension host on Windows): probes `wsl.exe python3 -m scrub_ai.cli` with venv paths, then `wsl python3 -m scrub_ai.cli`
- Linux/WSL (extension host inside WSL): probes venv paths directly (`~/.venv/bin/python3`, `~/scrub-ai/.venv/bin/python3`), then `python3`, then `python`
- macOS: same probe order as Linux
- All `spawn()` calls changed to `shell: false` for reliability across environments
- Replaced auto-install prompt with a clear error message — pip install must run in the correct environment and cannot be automated safely from the extension host

**Status bar indicator:**
- `$(shield) scrub-ai` shown in the bottom-right status bar when CLI is found
- `$(warning) scrub-ai` with warning background colour when CLI is not found
- Tooltip shows which Python binary is being used (e.g. `python3 -m scrub_ai.cli`)
- Updates on every `findCli()` call

**Why rewrite `findCli()`:** The original implementation used a single probe order that worked in WSL but failed when the extension host ran on Windows (common when VS Code is installed natively on Windows with WSL as the backend). The new implementation branches on `process.platform` and `os.arch()` to handle all three real-world configurations.

**Why status bar:** Users had no way to know whether the extension had found the CLI or was silently doing nothing. The status bar gives immediate, persistent feedback without being intrusive.

---

## Step 44 — Bumped extension to v1.0.0 + added Marketplace metadata

**What:** Updated `vscode-extension/scrub-ai/package.json`:
- Version bumped to `1.0.0`
- Added `keywords`: `["security", "secrets", "sanitize", "privacy", "AI", "clipboard"]`
- Added `repository`: points to the GitHub repo
- Added `homepage`: GitHub repo URL
- Added `bugs`: GitHub issues URL
- Compiled TypeScript successfully
- Committed and pushed to `feature/v2.0-vscode-extension`

**Why:** The VS Code Marketplace uses `keywords` for search ranking and `repository`/`homepage`/`bugs` for the sidebar links on the extension page. Without these, the extension is harder to discover and looks incomplete on the Marketplace listing.

---

## Step 46 — Published extension to VS Code Marketplace

**What:**
- Created VS Code Marketplace publisher account `rajwindermarwaha` at https://marketplace.visualstudio.com/manage
- Added `LICENSE` file to `vscode-extension/scrub-ai/`
- Optimized `icon.png` from 705 KB → 24 KB (resized to 128×128 via Pillow)
- Ran `vsce package` → `scrub-ai-1.0.0.vsix` (33.34 KB, 9 files)
- Uploaded `.vsix` via Marketplace web UI — passed automated verification
- Merged `feature/v2.0-vscode-extension` → `main`
- Updated `README.md` roadmap: marked v2.0 `[x]` complete

**Live at:** https://marketplace.visualstudio.com/items?itemName=rajwindermarwaha.scrub-ai

**Why upload via web UI instead of `vsce publish`:** `vsce publish` requires a PAT from Azure DevOps. The Azure AD tenant linked to the original Microsoft account was blocked due to inactivity. A new Microsoft account (Gmail-linked) was created, which only had access to the Marketplace web UI — sufficient for the initial upload. Future updates can use `vsce publish` once a PAT is generated from the new account's Azure DevOps org.
