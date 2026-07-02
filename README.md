# 🧹 scrub-ai

> Sanitize sensitive content from any text before sharing with AI assistants.

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

- 🔑 **Secrets detection** — API keys, tokens, passwords, private keys
- ☁️ **Cloud detection** — AWS account IDs, ARNs, GCP project IDs, Azure subscriptions
- 🌐 **Network detection** — IP addresses, internal hostnames, internal URLs
- 🧑 **PII detection** — emails, phone numbers, names via Presidio (optional)
- 🎯 **Confidence scoring** — filter low-signal matches with `--min-confidence`
- 🗂️ **Named profiles** — focus on `aws`, `k8s`, `secrets`, or `network`
- 📝 **Custom patterns** — add your own regex rules via a local JSON file
- ⌨️ **Windows hotkey** — press `Ctrl+Alt+S` to sanitize clipboard instantly
- 🖥️ **System tray** — runs quietly in the background
- 📋 **CLI** — pipe any text through it from the terminal
- 📦 **PyPI** — install with a single `pip install scrub-ai`

---

## Quick Start

### Install

```bash
# Standard install — secrets, cloud, network detection, profiles, custom patterns
pip install scrub-ai

# With PII detection (emails, phone numbers, names) — adds ~400 MB spacy model
pip install "scrub-ai[pii]"
python -m spacy download en_core_web_lg
```

> **Note:** PII detection is completely optional. All other features work without it.

### CLI Usage

```bash
# Pipe any text through it
cat error.log | scrub-ai

# Sanitize a file
scrub-ai --file crash.log

# See what would be detected without changing anything
scrub-ai --dry-run --file logs.txt

# Sanitize and copy result to clipboard
scrub-ai --file logs.txt --copy

# Focus on AWS credentials only (ignore network noise)
scrub-ai --profile aws --file logs.txt

# Only mask high-confidence detections (0.0-1.0)
scrub-ai --min-confidence 0.85 --file logs.txt

# Available profiles: aws, k8s, secrets, network
```

### PII Detection (optional)

Install with `pip install "scrub-ai[pii]"` and download the spacy model (see Install section above), then emails, phone numbers, and names are automatically detected:

```bash
echo "Call John Smith at 555-867-5309" | scrub-ai
# → Call [PERSON] at [PHONE_NUMBER]
```

### Custom Patterns

Create `~/.config/scrub-ai/patterns.json` (Linux/macOS) or `%APPDATA%\scrub-ai\patterns.json` (Windows):

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

Custom patterns are picked up automatically on every run — no restart needed.

### Hotkey Usage (Windows only)

```bash
# Start scrub-ai in the background
scrub-ai --start

# Icon appears in system tray (bottom right)
# Copy any text with Ctrl+C as normal
# Press Ctrl+Alt+S to sanitize clipboard
# Paste clean text with Ctrl+V
```

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

---

## Roadmap

- [x] Project setup
- [x] **v1.0** — CLI + secrets + cloud + network detection + Windows hotkey + system tray
- [x] **v1.1** — PII detection (Presidio) + confidence scoring + profiles + custom patterns
- [ ] **v1.2** — Watch mode (automatic clipboard monitoring)
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

# Install dev dependencies
pip install -e ".[dev]"

# Install with PII support (optional)
pip install -e ".[pii]"

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
