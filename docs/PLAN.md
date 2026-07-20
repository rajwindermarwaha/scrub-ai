# scrub-ai — Project Plan

## Problem Statement

Developers and SREs regularly copy sensitive content — logs, stack traces, config files, terminal output, source code — and paste it directly into AI assistants like ChatGPT, GitHub Copilot, and Claude.

This content frequently contains:
- API keys and secrets
- Internal hostnames and IP addresses
- Cloud account IDs and ARNs
- Database passwords and connection strings
- Personal information (emails, usernames)

Once this data is sent to an AI provider, the developer has no control over how it is stored, processed, or used. This is a **real security and privacy risk** that currently has no simple, developer-friendly solution.

**scrub-ai solves this** by automatically detecting and masking sensitive content before it leaves the developer's machine.

---

## Target Users

### Primary
- **SREs and DevOps engineers** — copy logs, Terraform output, kubectl output, AWS CLI output into AI tools daily
- **Backend developers** — copy stack traces, config files, environment variables into AI tools
- **Developers on any platform** — Windows, macOS, and Linux users who want a simple, cross-platform sanitization tool

### Secondary
- Security engineers who want to enforce sanitization policies in their team
- Any developer who uses AI coding assistants regularly

---

## Success Metrics

| Metric | Target | Timeline |
|---|---|---|
| PyPI publish | v1.0 live on PyPI | End of Week 2 |
| GitHub stars | 100+ stars | 3 months |
| PyPI downloads | 500+/month | 3 months |
| On CV | Described as published open source tool | Immediately after PyPI publish |
| Used by others | 10+ people other than author | 1 month |

---

## V1 Scope

### In V1
- ✅ CLI — `cat file | scrub-ai` and `scrub-ai --file logs.txt`
- ✅ `--dry-run` flag — show what would be detected without changing anything
- ✅ `--copy` flag — copy sanitized output to clipboard
- ✅ Secrets detector — API keys, tokens, passwords, private keys, JWTs
- ✅ Cloud detector — AWS (account IDs, ARNs, access keys), GCP (project IDs), Azure (subscription IDs)
- ✅ Network detector — IPv4, IPv6, internal hostnames, internal URLs
- ✅ Windows hotkey — `Ctrl+Alt+S` sanitizes clipboard contents
- ✅ Windows system tray icon — start/stop, enable/disable
- ✅ Windows toast notifications — tells user what was found
- ✅ Sanitization report — summary of what was detected and masked
- ✅ Published on PyPI

---

## Phased Roadmap

### Phase 1 — V1.0 (Weeks 1-2)
**Goal:** Working tool published on PyPI

```
Week 1:
  Day 1-2: Project setup, pyproject.toml, base structure
  Day 3:   Secrets detector
  Day 4:   Cloud detector (AWS/GCP/Azure)
  Day 5:   Network detector
  Day 6:   Core sanitizer (wires all detectors)
  Day 7:   CLI (click)

Week 2:
  Day 1:   Windows notifier (toast notifications)
  Day 2:   Hotkey listener (Ctrl+Shift+S)
  Day 3:   System tray icon
  Day 4:   Tests + fixtures
  Day 5:   README polish + PyPI publish
```

### Phase 2 — V1.1 (Week 3-4)
**Goal:** PII detection + better accuracy

- Add Presidio for NLP-based PII detection (emails, names, phone numbers)
- Add confidence scoring to reduce false positives
- Add `--profile` flag (`--profile aws`, `--profile k8s`)
- Custom pattern config file (`~/.scrub-ai/patterns.json`)
- Fake data replacement (replace with realistic fake values instead of `[REDACTED]`)

### Phase 3 — V1.2 (Month 2)
**Goal:** Watch mode + community growth

- Watch mode (automatic clipboard monitoring without needing the hotkey)
- Community feedback incorporated
- Blog post published

### Phase 4 — V2.0 (Month 3+)
**Goal:** VS Code extension

- VS Code extension — sanitize selection or file via command palette / `Ctrl+Alt+S`
- Calls existing Python CLI as subprocess — no logic duplication
- Diff view so user reviews changes before accepting
- Works on Windows, Linux, and macOS
- Published to VS Code Marketplace

### Phase 5 — V2.1 (Month 4+)
**Goal:** Browser integration

- Browser extension (warns before pasting into ChatGPT/Claude)

### Phase 6 — V3.0 (Month 5+)
**Goal:** Team features

- Team policies / audit log

---

## Weekly Progress Log

| Week | Goal | Status |
|---|---|---|
| Week 1 | Project setup + all detectors + CLI | ✅ Complete |
| Week 2 | Hotkey + tray + tests + PyPI v1.0 publish | ✅ Complete |
| Week 3 | PII detection + confidence scoring + profiles + custom patterns (v1.1) | ✅ Complete |
| Week 4 | Watch mode (v1.2) | ✅ Complete |
| Month 3 | VS Code extension (v2.0) | 🔄 In progress |

---

## Risks & Mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| False positives annoy users | High | Confidence scoring, dry-run mode, user can review |
| `keyboard` lib needs admin rights | Medium | Document this clearly, provide alternative |
| Heavy NLP models slow down hotkey | High | Keep v1 regex-only, add NLP as optional in v1.1 |
| PyPI name `scrub-ai` is taken | Low | Check before publishing, have backup names ready |
