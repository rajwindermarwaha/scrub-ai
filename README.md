# 🧹 scrub-ai

> Sanitize sensitive content from any text before sharing with AI assistants.

[![PyPI version](https://badge.fury.io/py/scrub-ai.svg)](https://badge.fury.io/py/scrub-ai)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Windows](https://img.shields.io/badge/platform-Windows-blue.svg)](https://www.microsoft.com/windows)

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
- 👤 **PII detection** — email addresses, phone numbers *(v2)*
- ⌨️ **Windows hotkey** — press `Ctrl+Shift+S` to sanitize clipboard instantly
- 🖥️ **System tray** — runs quietly in the background
- 📋 **CLI** — pipe any text through it from the terminal
- 📦 **PyPI** — install with a single `pip install scrub-ai`

---

## Quick Start

### Install

```bash
pip install scrub-ai
```

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
```

### Hotkey Usage (Windows)

```bash
# Start scrub-ai in the background
scrub-ai --start

# Icon appears in system tray (bottom right)
# Copy any text with Ctrl+C as normal
# Press Ctrl+Shift+S to sanitize clipboard
# Paste clean text with Ctrl+V
```

---

## Example

**Input:**
```
ERROR 2024-01-15 14:32:01 - Connection failed
  host: db01.prod.internal
  user: john.doe@mycompany.com
  password: myS3cretP@ss123
  AWS Account: 123456789012
  API Key: AKIAIOSFODNN7EXAMPLE
  IP: 10.0.1.45
```

**Output:**
```
ERROR 2024-01-15 14:32:01 - Connection failed
  host: [INTERNAL_HOST]
  user: [EMAIL]
  password: [REDACTED]
  AWS Account: [AWS_ACCOUNT_ID]
  API Key: [AWS_ACCESS_KEY]
  IP: [IP_ADDRESS]
```

**Report:**
```
✅ Sanitized successfully
   Detected: 1 password, 1 email, 1 AWS account ID, 1 AWS access key, 1 IP address, 1 internal hostname
   Safe to share with AI.
```

---

## What Gets Detected

| Category | Examples |
|---|---|
| AWS credentials | Access keys, secret keys, session tokens |
| AWS infrastructure | Account IDs, ARNs, S3 URLs |
| GCP credentials | Service account keys, project IDs |
| Azure credentials | Subscription IDs, connection strings |
| Generic secrets | API keys, bearer tokens, JWTs, private keys |
| Database | Connection strings, passwords |
| Network | IPv4, IPv6, internal hostnames, internal URLs |
| PII | Email addresses, phone numbers *(v2)* |
| Filesystem | Absolute paths, usernames in paths |

---

## Roadmap

- [x] Project setup
- [ ] **v1.0** — CLI + secrets + cloud + network detection + Windows hotkey
- [ ] **v1.1** — PII detection (emails, phones) via Presidio
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

# Run tests
pytest
```

---

## License

MIT — see [LICENSE](LICENSE)

---

## Author

Built by [@rajwindermarwaha](https://github.com/rajwindermarwaha)

> *Built this because I kept accidentally pasting AWS credentials and internal hostnames into AI tools. Figured others do the same.*
