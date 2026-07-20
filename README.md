<p align="center">
  <img src="https://raw.githubusercontent.com/rajwindermarwaha/scrub-ai/main/assets/icon.png" width="80" alt="scrub-ai logo"/>
</p>

# scrub-ai

> Shield your prompts. Sanitize sensitive content before sharing with AI assistants.

[![PyPI version](https://badge.fury.io/py/scrub-ai.svg)](https://badge.fury.io/py/scrub-ai)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-blue.svg)]()
[![CI](https://github.com/rajwindermarwaha/scrub-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/rajwindermarwaha/scrub-ai/actions/workflows/ci.yml)

---

## The Problem

Every day, developers copy sensitive content into AI assistants without thinking:

```
❌ Stack trace with internal hostnames    → pasted into ChatGPT
❌ Application logs with session tokens   → pasted into Copilot
❌ Config files with database passwords   → pasted into Claude
❌ kubectl output with cluster names      → pasted into AI
❌ AWS CLI output with account IDs        → pasted into ChatGPT
```

Once that data leaves your machine, you have no control over it.

**scrub-ai fixes this** — it detects and masks sensitive content before you share it with any AI tool.

---

## Features

- 🛡️ **Secrets detection** — API keys, tokens, passwords, private keys
- ☁️ **Cloud detection** — AWS account IDs, ARNs, GCP project IDs, Azure subscriptions
- 📡 **Network detection** — IP addresses, internal hostnames, internal URLs
- 🕵️ **PII detection** — emails, phone numbers, names via Presidio (optional)
- 🎯 **Confidence scoring** — filter low-signal matches with `--min-confidence`
- 🗂️ **Named profiles** — focus on `aws`, `k8s`, `secrets`, or `network`
- 📝 **Custom patterns** — add your own regex rules via a local JSON file
- 👁️ **Watch mode** — automatically sanitize clipboard whenever it changes (all platforms)
- ⌨️ **Windows hotkey** — press `Ctrl+Alt+S` to sanitize clipboard on demand
- 🖥️ **System tray** — runs quietly in the background (Windows)
- 📋 **CLI** — pipe any text through it from the terminal
- 📦 **PyPI** — install with a single `pip install scrub-ai`

---

## Install

### What do you need?

| Feature | Run command | Extra step |
|---|---|---|
| CLI, file/pipe sanitization | `cat file.txt \| scrub-ai` or `scrub-ai --file file.txt` | None |
| Profiles | `scrub-ai --profile aws --file logs.txt` | None |
| Custom patterns | `scrub-ai --file logs.txt` | None |
| Watch mode | `scrub-ai --watch` (or `python -m scrub_ai.cli --watch` on Windows if PATH not set) | Linux: `sudo apt install xclip` |
| Copy to clipboard | `scrub-ai --file logs.txt --copy` | Linux: `sudo apt install xclip` |
| Hotkey + system tray | `scrub-ai --start` | Windows only |
| PII detection (names, emails, phones) | `scrub-ai --file logs.txt` (auto) | `python -m spacy download en_core_web_lg` |

### Standard install

Includes secrets, cloud, and network detection, profiles, custom patterns, watch mode, and the Windows hotkey + tray.

```bash
pip install scrub-ai
```

### With PII detection (optional, ~400 MB)

Adds detection of emails, phone numbers, and person names using Microsoft Presidio and spaCy.

```bash
# Step 1 — install the package with PII dependencies
pip install "scrub-ai[pii]"

# Step 2 — download the spaCy language model (required for PII to work)
python -m spacy download en_core_web_lg
```

> If you skip Step 2, scrub-ai will still run — PII detection will silently do nothing.

---

## Platform Setup

The CLI and all detection features work on Windows, Linux, and macOS. Some modes have platform-specific prerequisites.

### Linux

Clipboard access (`--watch`, `--copy`) requires `xclip` or `xsel`:

```bash
sudo apt install xclip
```

> WSL (Windows Subsystem for Linux) users: clipboard integration works when running inside a WSL terminal as long as `xclip` is installed.

### macOS

No extra setup needed. `pyperclip` uses the built-in `pbcopy`/`pbpaste` — clipboard access works out of the box.

### Windows

No extra setup needed for clipboard access.

If `scrub-ai` is not recognised as a command after installing, Python's `Scripts` folder is not in your PATH. Fix it once:

1. Search **"Environment Variables"** in the Start menu
2. Click **"Edit the system environment variables"** → **"Environment Variables"**
3. Under **User variables**, select **Path** → click **Edit** → click **New**
4. Add the path to Python's Scripts folder — typically:
   ```
   C:\Users\<your-username>\AppData\Local\Programs\Python\Python312\Scripts
   ```
5. Click OK, open a **new** terminal, and `scrub-ai` will work

For the background hotkey + tray service, see [Hotkey + system tray](#hotkey--system-tray-windows-only) below.

---

## Usage

### Basic — pipe or file

```bash
# Pipe any text through it
cat error.log | scrub-ai

# Sanitize a file
scrub-ai --file crash.log

# See what would be detected without changing the output
scrub-ai --dry-run --file logs.txt

# Sanitize and copy the result to clipboard
scrub-ai --file logs.txt --copy
```

### Filtering — profiles and confidence

Use profiles to focus on a specific category and ignore noise from others.

```bash
# Focus on AWS credentials only (ignores IPs, hostnames, etc.)
scrub-ai --profile aws --file logs.txt

# Focus on Kubernetes-related secrets
scrub-ai --profile k8s --file logs.txt

# Only mask high-confidence detections (0.0–1.0 scale)
scrub-ai --min-confidence 0.85 --file logs.txt

# Combine profile and confidence threshold
scrub-ai --profile secrets --min-confidence 0.90 --file logs.txt
```

Available profiles: `aws`, `k8s`, `secrets`, `network`

Each profile activates only the detectors relevant to that context. For example, `--profile aws` runs only AWS credential and ARN patterns — it will not mask IP addresses or internal hostnames.

### Watch mode — automatic clipboard sanitization

Watch mode monitors your clipboard continuously. Every time you copy something, scrub-ai checks it and masks any sensitive content automatically before you paste.

Works on Windows, Linux, and macOS.

```bash
scrub-ai --watch
```

- Starts polling the clipboard every 500ms
- If sensitive content is detected, the clipboard is silently replaced with the clean version
- If nothing sensitive is found, the clipboard is left unchanged
- Press `Ctrl+C` to stop

**Prerequisites by platform:**

| Platform | Run command | Requirement |
|---|---|---|
| Linux | `scrub-ai --watch` | `sudo apt install xclip` first |
| macOS | `scrub-ai --watch` | None — works out of the box |
| Windows | `scrub-ai --watch` or `python -m scrub_ai.cli --watch` | Fix PATH (see [Windows setup](#windows) above) or use the `python -m` form |

### Hotkey + system tray (Windows only)

For a manual, on-demand workflow on Windows. Runs as a background service with a system tray icon.

```bash
scrub-ai --start
```

- Icon appears in the system tray (bottom right)
- Copy any text with `Ctrl+C` as normal
- Press `Ctrl+Alt+S` to sanitize the clipboard
- Paste the clean text with `Ctrl+V`
- Right-click the tray icon to toggle the hotkey on/off, or to quit

> `--start` is Windows only. For automatic clipboard sanitization on all platforms, use `--watch` instead.

---

## PII Detection

When installed with `pip install "scrub-ai[pii]"` and the spaCy model is downloaded, scrub-ai automatically detects:

| Type | Example input | Masked as |
|---|---|---|
| Person names | `John Smith` | `[PERSON]` |
| Email addresses | `john@example.com` | `[EMAIL_ADDRESS]` |
| Phone numbers | `555-867-5309` | `[PHONE_NUMBER]` |

```bash
echo "Call John Smith at 555-867-5309 or john@example.com" | scrub-ai
# → Call [PERSON] at [PHONE_NUMBER] or [EMAIL_ADDRESS]
```

PII detection runs automatically alongside secrets, cloud, and network detection — no extra flags needed.

---

## Custom Patterns

You can add your own regex rules to catch internal identifiers that scrub-ai doesn't know about.

Create the patterns file at:
- Linux/macOS: `~/.config/scrub-ai/patterns.json`
- Windows: `%APPDATA%\scrub-ai\patterns.json`

```json
[
  {
    "pattern": "ticket-\\d+",
    "replacement": "[TICKET]",
    "label": "internal_ticket",
    "confidence": 0.95
  }
]
```

| Field | Required | Description |
|---|---|---|
| `pattern` | ✅ | Python regex string |
| `replacement` | ✅ | What to replace matches with |
| `label` | ✅ | Name shown in the detection summary |
| `confidence` | ❌ | Score from 0.0–1.0 (default: 1.0). Used with `--min-confidence` |

Custom patterns are loaded on every run — no restart needed.

---

## Example

**Input:**
```
ERROR 2024-01-15 14:32:01 - Connection failed
  host: db01.prod.internal
  password: myS3cretP@ss123
  aws_access_key_id: AKIAIOSFODNN7EXAMPLE
  aws_account_id: 123456789012
  ip: 10.0.1.45
```

**Output:**
```
ERROR 2024-01-15 14:32:01 - Connection failed
  host: [INTERNAL_HOST]
  password: [REDACTED]
  aws_access_key_id: [AWS_ACCESS_KEY]
  aws_account_id: [AWS_ACCOUNT_ID]
  ip: [IP_ADDRESS]
```

**Detection summary (stderr):**
```
Detected 5 sensitive value(s): aws_access_key=1, aws_account_id=1, internal_host=1, ipv4=1, password=1
```

---

## What Gets Detected

| Category | Examples |
|---|---|
| AWS credentials | Access keys, secret keys, session tokens |
| AWS infrastructure | Account IDs, ARNs, S3 URLs |
| GCP credentials | Service account keys, project IDs |
| Azure credentials | Subscription IDs, connection strings |
| Generic secrets | API keys, bearer tokens, JWTs, private keys, hex tokens |
| Passwords | `password=`, `passwd=`, `pwd=` key-value patterns |
| Network | IPv4, IPv6, internal hostnames, internal URLs |
| PII *(optional)* | Person names, email addresses, phone numbers |

---

## Roadmap

- [x] Project setup
- [x] **v1.0** — CLI + secrets + cloud + network detection + Windows hotkey + system tray
- [x] **v1.1** — PII detection (Presidio) + confidence scoring + profiles + custom patterns
- [x] **v1.2** — Watch mode (automatic clipboard monitoring, all platforms)
- [ ] **v2.0** — VS Code extension
- [ ] **v2.1** — Browser extension (warns before pasting into ChatGPT)
- [ ] **v3.0** — Team policies + audit log

---

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

```bash
# Clone
git clone https://github.com/rajwindermarwaha/scrub-ai
cd scrub-ai

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate        # Linux/macOS
.venv\Scripts\activate           # Windows

# Install with dev dependencies
pip install -e ".[dev]"

# Optional: also install PII dependencies
pip install -e ".[pii]"
python -m spacy download en_core_web_lg

# Run tests
pytest
```

---

## License

MIT — see [LICENSE](LICENSE)

---

## Author

Built by [@rajwindermarwaha](https://github.com/rajwindermarwaha)

> *Built this because I had to put in the extra effort of copying everything into Notepad first and manually scrubbing it before sharing with AI tools. Figured others do the same.*
