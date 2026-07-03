"""
watcher.py — Clipboard watch mode for scrub-ai.

When watch mode is active, the clipboard is checked every 500ms.
If the content has changed, it is sanitized automatically and written back.

Design:
  - Cross-platform (Windows, Linux, macOS) — uses only pyperclip.
  - Runs in a background daemon thread; start() blocks until stop() is called.
  - Only sanitizes when watch mode is enabled in config (cfg.is_watch_mode()).
  - Ignores clipboard content that scrub-ai itself just wrote (avoids re-sanitizing).
"""

from __future__ import annotations

import threading
import time

import pyperclip

from scrub_ai import config as cfg
from scrub_ai.sanitizer import sanitize_text
from scrub_ai.notifier import notify

_stop_event = threading.Event()
_POLL_INTERVAL = 0.5  # seconds between clipboard checks


def _watch_loop() -> None:
    """Poll the clipboard and sanitize on change."""
    last_text = ""
    while not _stop_event.is_set():
        if cfg.is_watch_mode():
            try:
                current = pyperclip.paste()
            except Exception:  # noqa: BLE001
                current = ""

            if current and current != last_text:
                clean_text, report = sanitize_text(current)
                if clean_text != current:
                    try:
                        pyperclip.copy(clean_text)
                    except Exception:  # noqa: BLE001
                        pass
                    notify(report)
                last_text = clean_text
            else:
                last_text = current

        _stop_event.wait(timeout=_POLL_INTERVAL)


def start() -> None:
    """Start the clipboard watcher loop. Blocks until stop() is called.

    Intended to be run in a background daemon thread.
    """
    _stop_event.clear()
    _watch_loop()


def stop() -> None:
    """Signal the watcher loop to exit."""
    _stop_event.set()
