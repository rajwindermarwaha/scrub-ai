# scrub-ai — Decision Log

This file records key technical decisions made during development, with the reasoning behind each choice. This is useful for contributors and for explaining design choices in interviews.

---

## D001 — Python over Node.js or Go

**Decision:** Python

**Options considered:**
- Python
- Node.js
- Go

**Reasoning:**
- Python has the richest ecosystem for NLP and secrets detection (Presidio, detect-secrets, truffleHog all use Python)
- `keyboard`, `pystray`, `pyperclip` are mature Python libraries with no Node/Go equivalents
- Target audience (SREs, DevOps engineers) are comfortable with `pip install`
- Author's primary language is Python

**Tradeoff accepted:**
Python is slower than Go for a CLI tool, but performance is not a concern here — input text is small (< 1MB) and detection is regex-based.

---

## D002 — Regex over NLP for V1 detection

**Decision:** Regex-only for V1, NLP added in V1.1

**Options considered:**
- Pure regex
- Pure NLP (Presidio)
- Hybrid (regex + NLP)

**Reasoning:**
- NLP models (spaCy) take 2-5 seconds to load — unacceptable for a hotkey that should feel instant
- Secrets (API keys, ARNs, IPs) have well-defined formats — regex is accurate enough
- NLP is needed for unstructured PII (names, addresses) which is lower priority for DevOps use case
- Keeping V1 dependency-light makes installation simpler

**Tradeoff accepted:**
Regex will miss some PII (e.g. a person's name in a log line). This is acceptable for V1. NLP covers this in V1.1.

---

## D003 — Hotkey mode over Watch mode for V1

**Decision:** Hotkey (`Ctrl+Shift+S`) for V1, Watch mode in V1.2

**Options considered:**
- Watch mode: automatically sanitize clipboard on every copy
- Hotkey mode: user manually triggers sanitization
- CLI only: no clipboard integration

**Reasoning:**
- Watch mode modifies clipboard automatically, which is dangerous:
  - If user copies a password to paste into a login form, it gets redacted
  - If false positive fires, user's clipboard is corrupted
  - Users will uninstall immediately after one bad experience
- Hotkey mode puts the user in control
- Trust must be earned before automating clipboard modification
- Watch mode can be added in V1.2 once users trust the tool

**Tradeoff accepted:**
Hotkey requires an extra keypress. Watch mode is more seamless but too risky for V1.

---

## D004 — `keyboard` over `pynput` for hotkeys

**Decision:** `keyboard` library

**Options considered:**
- `keyboard` — simple API, cross-platform, global hotkeys
- `pynput` — more control, better for monitoring all input
- `pywin32` — native Windows, most reliable but complex

**Reasoning:**
- `keyboard` has the simplest API for registering global hotkeys
- One line: `keyboard.add_hotkey('ctrl+alt+s', callback)`
- Works cross-platform (useful for macOS/Linux support later)
- Well maintained, 3.5k+ GitHub stars

**Tradeoff accepted:**
`keyboard` requires admin privileges on some Windows configurations. This is documented in the README.

**Note for implementation (`hotkey.py`):**
Wrap hotkey registration in a try/except. If it fails due to permissions, show a helpful message and fall back gracefully:
```
⚠️  Could not register hotkey. Try running as administrator.
   The CLI still works: scrub-ai --file logs.txt
```
The CLI must always work regardless of whether the hotkey registration succeeds.

---

## D008 — Default hotkey changed from `Ctrl+Shift+S` to `Ctrl+Alt+S`

**Decision:** `Ctrl+Alt+S`

**Options considered:**
- `Ctrl+Shift+S` — original choice, S for Scrub
- `Ctrl+Shift+X` — low conflicts, X for scrub out
- `Ctrl+Alt+S` — S for Scrub, no major conflicts

**Reasoning:**
- scrub-ai is primarily a developer tool and developers use VS Code daily
- VS Code uses `Ctrl+Shift+S` for Save All — this creates muscle memory confusion
- `Ctrl+Alt+S` has no known conflicts with VS Code or common developer tools
- Still memorable — S for Scrub
- Feels like a deliberate tool shortcut rather than an editor shortcut

**Tradeoff accepted:**
`Ctrl+Alt+S` conflicts with some music apps (e.g. Spotify shortcuts) but that is not relevant to the target audience.

---

## D005 — Label replacement over Redact for default

**Decision:** Default replacement is `[LABEL]` not `[REDACTED]`

**Options considered:**
- `[REDACTED]` — hides everything with same label
- `[AWS_ACCESS_KEY]` — label tells you what was removed
- Fake data — replace with realistic-looking fake value

**Reasoning:**
- `[AWS_ACCESS_KEY]` gives the AI assistant context about what type of data was there
- The AI can still help debug the issue even without the real value
- `[REDACTED]` is less useful — AI doesn't know what type of data it is
- Fake data (v2) is the most seamless but hardest to implement correctly

**Example of why label is better:**
```
# With [REDACTED]:
AWS error: invalid credentials [REDACTED]
# AI doesn't know if that was a key, a token, or a password

# With [AWS_ACCESS_KEY]:
AWS error: invalid credentials [AWS_ACCESS_KEY]
# AI immediately knows it's an access key and can give relevant advice
```

---

## D006 — Windows first, macOS/Linux later

**Decision:** V1 CLI is cross-platform. Hotkey and tray are Windows-only.

**Original decision:** Windows only for V1.

**Why we changed it:**
- During setup we discovered that developing on WSL/Linux was blocked by Windows-only dependencies
- The CLI and detectors are pure Python + regex — there is no reason to restrict them to Windows
- Only `win10toast` and `keyboard` are genuinely Windows-only
- `pystray` and `Pillow` work cross-platform
- Making the CLI cross-platform from day one means Linux and macOS developers can use and contribute to scrub-ai

**What is Windows-only:**
- `scrub-ai --start` (hotkey + system tray + toast notifications)

**What works everywhere:**
- `scrub-ai --file logs.txt` and all CLI flags
- All detectors

**Tradeoff accepted:**
The Windows hotkey experience remains the flagship feature but the tool is now useful to a much wider audience.

---

## D007 — Single PyPI package over separate packages

**Decision:** One package `scrub-ai` on PyPI

**Options considered:**
- One package with all features
- Core package + optional extras (`scrub-ai[windows]`, `scrub-ai[nlp]`)

**Reasoning:**
- Simpler for users: `pip install scrub-ai` just works
- Extras syntax confuses non-technical users
- Can always split later if package gets too large
- Windows-specific deps (`win10toast`, `pystray`) are small

**Tradeoff accepted:**
Installs Windows-specific libraries on non-Windows systems. Mitigated by platform checks at runtime.
