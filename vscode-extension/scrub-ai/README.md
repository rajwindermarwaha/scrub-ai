# scrub-ai — VS Code Extension

> Shield your prompts. Sanitize sensitive content before sharing with AI assistants.

## What it does

Detects and masks sensitive content directly in your editor — automatically, as you work.

- 🛡️ **Secrets** — API keys, tokens, passwords, private keys
- ☁️ **Cloud** — AWS account IDs, ARNs, GCP project IDs, Azure subscriptions
- 📡 **Network** — IP addresses, internal hostnames, internal URLs
- 🕵️ **PII** *(optional)* — emails, phone numbers, person names

## Features

### Auto-scan on open and save
Every time you open or save a supported file, scrub-ai scans it automatically. Sensitive values are highlighted with yellow squiggly underlines and listed in the Problems panel (`Ctrl+Shift+M`).

### Inline quick-fix
Click the 💡 lightbulb on any flagged line (or press `Ctrl+.`) to instantly mask the value in-place — no commands needed.

### Clipboard watch mode
Runs silently in the background. Every time you copy something, scrub-ai checks it and replaces sensitive content before you paste.

### Manual sanitize
Use `Ctrl+Alt+S` or the Command Palette to sanitize a selection, the active file, or view a diff before applying.

## Requirements

Python must be installed with `scrub-ai` available. Install it inside your environment:

```bash
pip install scrub-ai
```

On Windows with WSL, install inside WSL:
```bash
# in WSL terminal
pip install scrub-ai
```

## Usage

| Action | How |
|---|---|
| Auto-scan | Opens automatically on file open / save |
| Inline fix | Click 💡 lightbulb on a flagged line → `Mask [label]` |
| Fix all in file | Click 💡 → `Mask all sensitive values in file` |
| Sanitize selection or file | `Ctrl+Alt+S` |
| Sanitize via palette | `Ctrl+Shift+P` → `Scrub AI: Sanitize Selection` |
| Sanitize entire file | `Ctrl+Shift+P` → `Scrub AI: Sanitize File` |
| View Problems | `Ctrl+Shift+M` |

## Supported file types

`.env` `.log` `.txt` `.yaml` `.yml` `.json` `.toml` `.ini` `.config` `.ts` `.tsx` `.js` `.jsx` `.py` `.sh` `.md` `.xml` `.properties` `.cfg` `.conf` `.tf` `.hcl` `.sql`

Files larger than 500 KB and paths inside `node_modules/`, `.git/`, `dist/`, `build/` are skipped.

## Platform support

Works on Windows, Linux, and macOS — anywhere Python is available.

## Links

- [PyPI package](https://pypi.org/project/scrub-ai/)
- [GitHub](https://github.com/rajwindermarwaha/scrub-ai)
- [Report an issue](https://github.com/rajwindermarwaha/scrub-ai/issues)
