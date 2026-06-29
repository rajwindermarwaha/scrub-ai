"""
hotkey.py — Global hotkey listener for scrub-ai (Windows-only).

When the user presses Ctrl+Alt+S (or the configured hotkey):
  1. Read the current clipboard contents.
  2. Sanitize the text with the core sanitizer.
  3. Write the clean text back to the clipboard.
  4. Fire a toast notification with the sanitization report.

Design constraints:
  - The `keyboard` library is Windows-only (pyproject.toml marker).  This
    module uses a runtime platform guard and no-ops on non-Windows systems so
    tests can import it without error.
  - Clipboard access uses `pyperclip`, which works cross-platform and is
    already a dependency.
  - The listener runs in a blocking loop; callers should launch it in a
    dedicated thread (tray.py does this).
  - `stop()` sets a threading.Event that the loop checks; the keyboard library
    also supports `keyboard.unhook_all()` to cleanly release the hook.
"""

from __future__ import annotations

import sys
import threading

import pyperclip

from scrub_ai import config as cfg
from scrub_ai.sanitizer import sanitize_text
from scrub_ai.notifier import notify

_stop_event = threading.Event()


def _handle_hotkey() -> None:
    """Called by the keyboard hook each time the hotkey fires."""
    if not cfg.is_enabled():
        return

    try:
        text = pyperclip.paste()
    except Exception:  # noqa: BLE001
        return

    if not text:
        return

    clean_text, report = sanitize_text(text)

    try:
        pyperclip.copy(clean_text)
    except Exception:  # noqa: BLE001
        pass

    notify(report)


def start(hotkey: str | None = None) -> None:
    """Register the global hotkey and block until stop() is called.

    This function is intended to be run in a background thread.
    On non-Windows platforms it returns immediately.
    """
    if sys.platform != "win32":
        return

    try:
        import keyboard  # type: ignore[import]
    except ImportError:
        return

    _stop_event.clear()
    shortcut = hotkey or cfg.get_hotkey()
    keyboard.add_hotkey(shortcut, _handle_hotkey, suppress=False)

    _stop_event.wait()  # block until stop() signals

    keyboard.unhook_all()


def stop() -> None:
    """Signal the listener loop to exit."""
    _stop_event.set()
