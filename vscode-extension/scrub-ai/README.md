# scrub-ai — VS Code Extension

> Shield your prompts. Sanitize sensitive content before sharing with AI assistants.

## What it does

Detects and masks sensitive content directly in your editor before you copy it into any AI tool.

- Secrets — API keys, tokens, passwords, private keys
- Cloud — AWS account IDs, ARNs, GCP project IDs, Azure subscriptions
- Network — IP addresses, internal hostnames, internal URLs
- PII *(optional)* — emails, phone numbers, person names

## Requirements

Python must be installed and on your PATH. The extension will offer to install the `scrub-ai` Python package automatically on first use.

To install manually:
```bash
pip install scrub-ai
```

## Usage

| Action | How |
|---|---|
| Sanitize selection or full file | `Ctrl+Alt+S` |
| Sanitize selection or full file | Command Palette → `Scrub AI: Sanitize Selection` |
| Sanitize entire file | Command Palette → `Scrub AI: Sanitize File` |

When sensitive content is found, you will be prompted to:
- **Show Diff** — view exactly what will change before applying
- **Apply** — apply immediately
- **Cancel** — do nothing

## Platform support

Works on Windows, Linux, and macOS — anywhere Python is available.
