# Privacy Policy — scrub-ai

**Last updated: 2026-08-09**

## Overview

scrub-ai is a browser extension that sanitizes sensitive content before it is pasted into AI tools. This privacy policy explains how the extension handles data.

---

## Data Collection

**scrub-ai does not collect, store, transmit, or share any user data.**

- No data is sent to any server
- No analytics or telemetry is collected
- No account or sign-in is required
- No personal information is recorded anywhere

---

## How the Extension Works

When you paste text into a supported AI site, the extension:

1. Reads the pasted text **locally in your browser** using the DOM paste event
2. Runs the text through a set of regex patterns **entirely within the browser tab** — no network requests are made
3. Replaces any detected sensitive values (API keys, passwords, credentials, internal hostnames) with placeholders such as `[API_KEY]` or `[IP_ADDRESS]`
4. Injects the sanitized text into the input field

All processing happens **on-device**, in memory, within the browser tab. The original text and the sanitized result are never written to disk, never sent to a remote server, and are discarded after the paste event completes.

---

## Permissions

The extension requests the following permissions:

| Permission | Why it is needed |
|---|---|
| `clipboardRead` | To read the text being pasted so it can be checked for sensitive content |
| `clipboardWrite` | To inject the sanitized text back into the input field |
| Host access (specific AI sites only) | To run the content script on supported AI assistant websites |

The extension only activates on the following domains:
- `chatgpt.com`
- `chat.openai.com`
- `claude.ai`
- `copilot.microsoft.com`
- `gemini.google.com`
- `bing.com`

It does not run on any other websites.

---

## Third Parties

scrub-ai does not integrate with any third-party services, analytics platforms, or advertising networks. No data is shared with any third party under any circumstances.

---

## Changes to This Policy

If this policy changes, the updated version will be committed to this repository with a new **Last updated** date. The extension will not change its data handling practices without updating this document.

---

## Contact

If you have questions about this policy, open an issue at:
**https://github.com/rajwindermarwaha/scrub-ai/issues**
