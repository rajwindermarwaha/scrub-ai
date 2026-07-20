# scrub-ai — Architecture

## Overview

scrub-ai is a cross-platform Python CLI tool, Windows background service, and VS Code extension that detects and masks sensitive content from any text. The CLI works on Windows, Linux, and macOS. The hotkey and system tray features are Windows-only. The VS Code extension works on all platforms.

---

## Data Flow

```
┌─────────────────────────────────────────────┐
│           Input (any text)                   │
│  logs / code / traces / configs / output     │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│           Sanitizer (sanitizer.py)           │
│  Runs all detectors in priority order        │
│  Collects all matches with positions         │
│  Applies replacements (no overlaps)          │
│  Builds detection report                     │
└──────────────────┬──────────────────────────┘
                   │
        ┌──────────┼──────────┐
        ▼          ▼          ▼
  secrets.py   cloud.py   network.py
  detector     detector   detector
        │          │          │
        └──────────┼──────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│           Clean Output + Report              │
│  Modified text + summary of what was found   │
└─────────────────────────────────────────────┘
```

---

## Project Structure

```
scrub-ai/
│
├── scrub_ai/                      # main Python package
│   ├── __init__.py                # version, public API
│   ├── cli.py                     # click CLI entry point
│   ├── sanitizer.py               # core — wires all detectors together
│   ├── hotkey.py                  # Ctrl+Alt+S global hotkey listener (Windows)
│   ├── tray.py                    # Windows system tray icon + menu
│   ├── notifier.py                # Windows toast notifications
│   ├── config.py                  # loads/saves config from AppData
│   ├── watcher.py                 # clipboard watch mode (all platforms)
│   │
│   └── detectors/
│       ├── __init__.py
│       ├── base.py                # base class all detectors inherit from
│       ├── secrets.py             # API keys, tokens, passwords, JWTs
│       ├── cloud.py               # AWS / GCP / Azure specific patterns
│       ├── network.py             # IPs, hostnames, internal URLs
│       ├── pii.py                 # PII via Presidio (optional)
│       └── custom.py              # user-defined regex patterns
│
├── vscode-extension/              # VS Code extension (v2.0)
│   ├── src/
│   │   └── extension.ts           # extension entry point
│   ├── package.json               # extension manifest
│   └── tsconfig.json
│
├── tests/
│   ├── test_sanitizer.py
│   ├── test_secrets_detector.py
│   ├── test_cloud_detector.py
│   ├── test_network_detector.py
│   ├── test_pii_detector.py
│   ├── test_custom_detector.py
│   ├── test_profiles.py
│   ├── test_watcher.py
│   ├── test_config.py
│   ├── test_hotkey.py
│   ├── test_tray.py
│   └── test_notifier.py
│
├── assets/
│   └── icon.png                   # system tray icon
│
├── docs/
│   ├── PLAN.md
│   ├── ARCHITECTURE.md
│   ├── DECISIONS.md
│   └── DEVLOG.md
│
├── pyproject.toml
├── README.md
├── CONTRIBUTING.md
├── LICENSE
└── .github/
    └── workflows/
        ├── ci.yml
        └── publish.yml
```

---

## Core Components

### 1. `detectors/base.py` — Base Detector

All detectors inherit from `BaseDetector`. Each detector:
- Has a `name` and `priority`
- Has a list of `patterns` (compiled regex)
- Implements `detect(text) -> list[Match]`
- Returns a list of `Match` objects with: `start`, `end`, `original`, `replacement`, `category`

```python
@dataclass
class Match:
    start: int           # character position in original text
    end: int             # character position in original text
    original: str        # the actual matched text
    replacement: str     # what to replace it with e.g. [AWS_ACCESS_KEY]
    category: str        # e.g. "secrets", "cloud", "network"
    label: str           # e.g. "AWS Access Key"
    confidence: float    # 0.0 to 1.0
```

### 2. `sanitizer.py` — Core Sanitizer

The sanitizer:
1. Runs all detectors against input text
2. Collects all `Match` objects
3. Resolves overlapping matches (highest confidence wins)
4. Applies replacements from end to start (so positions don't shift)
5. Returns `(clean_text, report)`

### 3. `cli.py` — CLI Entry Point

Built with `click`. Handles:
- Reading from stdin (`cat file | scrub-ai`)
- Reading from file (`scrub-ai --file logs.txt`)
- `--dry-run` flag
- `--copy` flag (copy result to clipboard)
- `--start` flag (launch background hotkey daemon)
- `--watch` flag (clipboard watch mode, all platforms)


### 7. `vscode-extension/` — VS Code Extension

Built with TypeScript using the VS Code Extension API. Calls the Python CLI (`scrub-ai`) as a subprocess.

**Commands exposed:**
| Command | Action |
|---|---|
| `Scrub AI: Sanitize Selection` | Sanitizes the selected text and replaces it in-place via a diff view |
| `Scrub AI: Sanitize File` | Sanitizes the entire active file via a diff view |

**Keybinding:** `Ctrl+Alt+S` — consistent with the Windows hotkey.

**How it calls the CLI:**
```
scrub-ai --file <temp_file>
```
Output is shown in a diff view so the user can review and accept changes before anything is modified.

**Error handling:** If `scrub-ai` is not installed or not on PATH, the extension shows a clear install prompt linking to the README.

### 4. `hotkey.py` — Global Hotkey

Uses the `keyboard` library to register a global hotkey (`Ctrl+Shift+S`).
When triggered:
1. Reads current clipboard contents via `pyperclip`
2. Runs sanitizer on clipboard text
3. Writes clean text back to clipboard via `pyperclip`
4. Fires a Windows toast notification with the report

### 5. `tray.py` — System Tray

Uses `pystray` + `Pillow` to show a system tray icon.
Menu items:
- Enable / Disable (toggle hotkey on/off)
- Show last report
- Settings
- Quit

### 6. `notifier.py` — Toast Notifications

Uses `win10toast` to show Windows native toast notifications.
Shows:
- What was detected (e.g. "2 secrets, 1 IP address")
- Whether it was clean ("Nothing sensitive found")

---

## Detection Priority Order

Detectors run in this order. Higher priority detectors run first.

```
Priority 1 — Secrets     (highest damage if leaked)
Priority 2 — Cloud       (AWS/GCP/Azure specific)
Priority 3 — Network     (IPs, hostnames)
Priority 4 — PII         (emails, phones — v1.1)
```

---

## Tech Stack

| Component | Library | Version | Platform |
|---|---|---|---|
| Language | Python | 3.10+ | All |
| CLI | click | 8.x | All |
| Clipboard | pyperclip | 1.8.x | All |
| System tray | pystray | 0.19.x | All |
| Tray icon rendering | Pillow | 10.x | All |
| Global hotkey | keyboard | 0.13.x | Windows only |
| Toast notifications | win10toast | 0.9.x | Windows only |
| NLP PII (v1.1) | presidio-analyzer | 2.x | All |
| Tests | pytest | 7.x | All |
| Packaging | pyproject.toml + PyPI | — | All |
| CI | GitHub Actions | — | All |
| VS Code extension | TypeScript + VS Code API | — | All |

---

## Config File Location

```
Windows: C:\Users\{username}\AppData\Roaming\scrub-ai\config.json
Linux:   ~/.config/scrub-ai/config.json
macOS:   ~/Library/Application Support/scrub-ai/config.json
```

Default config:
```json
{
  "hotkey": "ctrl+alt+s",
  "enabled": true,
  "notify": true,
  "detectors": {
    "secrets": true,
    "cloud": true,
    "network": true,
    "pii": false
  },
  "replacement_style": "label"
}
```

---

## Replacement Styles

| Style | Example input | Example output |
|---|---|---|
| `label` | `AKIAIOSFODNN7EXAMPLE` | `[AWS_ACCESS_KEY]` |
| `redact` | `AKIAIOSFODNN7EXAMPLE` | `[REDACTED]` |
| `fake` *(v2)* | `AKIAIOSFODNN7EXAMPLE` | `AKIAXXXXXXXXXXXXXXXX` |
