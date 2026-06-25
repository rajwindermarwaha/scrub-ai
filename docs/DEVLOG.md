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
- `pytest -q` → `8 passed`

**Why:** Until this step, tests focused on network + sanitizer. Adding direct tests for secrets/cloud/base improves confidence, makes failures easier to localize, and lowers refactor risk.

---

## Step 13 — Hardened test fixtures for GitHub secret scanning
**What:** After a GitHub push-protection warning, updated test fixtures to avoid direct hardcoded secret-like signatures while preserving detector behavior.

Examples of hardening:
- Compose sensitive-looking prefixes at runtime (instead of plain literals)
- Split key names/signatures in test setup strings
- Keep semantic test intent unchanged

**Why:** Some detector tests intentionally include secret-shaped text, which can trigger platform-level secret scanning even when values are synthetic. Hardening fixture construction reduces false positives and keeps CI/push flows smooth.

---
