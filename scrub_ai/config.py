"""
config.py — Persistent user configuration for scrub-ai.

Settings are stored in a JSON file:
  - Windows: %APPDATA%\\scrub-ai\\config.json
  - Linux/macOS: ~/.config/scrub-ai/config.json

Only a small set of knobs exist in v1:
  - enabled (bool)  — whether the hotkey listener is active
  - hotkey (str)    — the keyboard shortcut string (default "ctrl+alt+s")
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


_DEFAULTS: dict[str, object] = {
    "enabled": True,
    "hotkey": "ctrl+alt+s",
}


def _config_dir() -> Path:
    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming"
        return Path(appdata) / "scrub-ai"
    return Path.home() / ".config" / "scrub-ai"


def _config_path() -> Path:
    return _config_dir() / "config.json"


def load() -> dict[str, object]:
    """Return the current config, falling back to defaults for any missing key."""
    path = _config_path()
    if not path.exists():
        return dict(_DEFAULTS)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return {**_DEFAULTS, **data}
    except (json.JSONDecodeError, OSError):
        return dict(_DEFAULTS)


def save(config: dict[str, object]) -> None:
    """Persist config to disk, creating directories as needed."""
    path = _config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config, indent=2), encoding="utf-8")


def set_enabled(value: bool) -> None:
    cfg = load()
    cfg["enabled"] = value
    save(cfg)


def is_enabled() -> bool:
    return bool(load().get("enabled", True))


def get_hotkey() -> str:
    return str(load().get("hotkey", _DEFAULTS["hotkey"]))
