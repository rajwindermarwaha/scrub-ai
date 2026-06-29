"""Tests for scrub_ai/hotkey.py.

_handle_hotkey() is the core logic being tested:
  - reads clipboard → sanitizes → writes back → notifies
  - early-exits when disabled or clipboard is empty
  - swallows pyperclip errors without crashing

start() / stop() threading behaviour is tested with a lightweight fake
`keyboard` module injected via sys.modules.
"""

from __future__ import annotations

import sys
import threading
from unittest.mock import MagicMock, call, patch

import pytest

import scrub_ai.hotkey as hotkey_mod


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_fake_keyboard() -> MagicMock:
    """Return a mock that stands in for the `keyboard` library."""
    return MagicMock()


# ---------------------------------------------------------------------------
# _handle_hotkey — happy path
# ---------------------------------------------------------------------------

class TestHandleHotkeyHappyPath:
    def test_sanitizes_clipboard_and_writes_back(self, tmp_path, monkeypatch) -> None:
        monkeypatch.setattr("scrub_ai.config._config_path", lambda: tmp_path / "config.json")

        pasted = "password=SuperSecret123"
        with (
            patch("scrub_ai.hotkey.pyperclip.paste", return_value=pasted),
            patch("scrub_ai.hotkey.pyperclip.copy") as mock_copy,
            patch("scrub_ai.hotkey.notify") as mock_notify,
        ):
            hotkey_mod._handle_hotkey()

        # copy() must have been called with the sanitized text (secret removed)
        assert mock_copy.called
        written = mock_copy.call_args[0][0]
        assert "SuperSecret123" not in written

        # notify() must have been called with the report
        assert mock_notify.called
        report = mock_notify.call_args[0][0]
        assert report["total_matches"] >= 1

    def test_clean_clipboard_still_writes_back_and_notifies(self, tmp_path, monkeypatch) -> None:
        monkeypatch.setattr("scrub_ai.config._config_path", lambda: tmp_path / "config.json")

        clean_text = "hello world, nothing sensitive here"
        with (
            patch("scrub_ai.hotkey.pyperclip.paste", return_value=clean_text),
            patch("scrub_ai.hotkey.pyperclip.copy") as mock_copy,
            patch("scrub_ai.hotkey.notify") as mock_notify,
        ):
            hotkey_mod._handle_hotkey()

        mock_copy.assert_called_once_with(clean_text)
        report = mock_notify.call_args[0][0]
        assert report["total_matches"] == 0
        assert report["is_clean"] is True


# ---------------------------------------------------------------------------
# _handle_hotkey — early exit conditions
# ---------------------------------------------------------------------------

class TestHandleHotkeyEarlyExit:
    def test_does_nothing_when_disabled(self, tmp_path, monkeypatch) -> None:
        monkeypatch.setattr("scrub_ai.config._config_path", lambda: tmp_path / "config.json")
        import scrub_ai.config as cfg
        cfg.set_enabled(False)

        with (
            patch("scrub_ai.hotkey.pyperclip.paste") as mock_paste,
            patch("scrub_ai.hotkey.pyperclip.copy") as mock_copy,
            patch("scrub_ai.hotkey.notify") as mock_notify,
        ):
            hotkey_mod._handle_hotkey()

        mock_paste.assert_not_called()
        mock_copy.assert_not_called()
        mock_notify.assert_not_called()

    def test_does_nothing_when_clipboard_is_empty(self, tmp_path, monkeypatch) -> None:
        monkeypatch.setattr("scrub_ai.config._config_path", lambda: tmp_path / "config.json")

        with (
            patch("scrub_ai.hotkey.pyperclip.paste", return_value=""),
            patch("scrub_ai.hotkey.pyperclip.copy") as mock_copy,
            patch("scrub_ai.hotkey.notify") as mock_notify,
        ):
            hotkey_mod._handle_hotkey()

        mock_copy.assert_not_called()
        mock_notify.assert_not_called()


# ---------------------------------------------------------------------------
# _handle_hotkey — resilience
# ---------------------------------------------------------------------------

class TestHandleHotkeyResilience:
    def test_swallows_paste_exception(self, tmp_path, monkeypatch) -> None:
        monkeypatch.setattr("scrub_ai.config._config_path", lambda: tmp_path / "config.json")

        with (
            patch("scrub_ai.hotkey.pyperclip.paste", side_effect=Exception("no clipboard")),
            patch("scrub_ai.hotkey.pyperclip.copy") as mock_copy,
        ):
            hotkey_mod._handle_hotkey()  # must not raise

        mock_copy.assert_not_called()

    def test_swallows_copy_exception(self, tmp_path, monkeypatch) -> None:
        monkeypatch.setattr("scrub_ai.config._config_path", lambda: tmp_path / "config.json")

        with (
            patch("scrub_ai.hotkey.pyperclip.paste", return_value="some text"),
            patch("scrub_ai.hotkey.pyperclip.copy", side_effect=Exception("clipboard locked")),
            patch("scrub_ai.hotkey.notify"),
        ):
            hotkey_mod._handle_hotkey()  # must not raise

    def test_notify_still_called_even_if_copy_fails(self, tmp_path, monkeypatch) -> None:
        monkeypatch.setattr("scrub_ai.config._config_path", lambda: tmp_path / "config.json")

        with (
            patch("scrub_ai.hotkey.pyperclip.paste", return_value="password=abc123"),
            patch("scrub_ai.hotkey.pyperclip.copy", side_effect=Exception("fail")),
            patch("scrub_ai.hotkey.notify") as mock_notify,
        ):
            hotkey_mod._handle_hotkey()

        # notify should still be called even though copy failed
        assert mock_notify.called


# ---------------------------------------------------------------------------
# start() / stop() — platform guard and threading
# ---------------------------------------------------------------------------

class TestStart:
    def test_noop_on_linux(self, monkeypatch) -> None:
        monkeypatch.setattr(sys, "platform", "linux")
        # Should return immediately without touching keyboard
        hotkey_mod.start()  # must not raise or block

    def test_noop_on_darwin(self, monkeypatch) -> None:
        monkeypatch.setattr(sys, "platform", "darwin")
        hotkey_mod.start()  # must not raise or block

    def test_registers_hotkey_and_unregisters_on_stop(self, monkeypatch) -> None:
        monkeypatch.setattr(sys, "platform", "win32")
        fake_keyboard = _make_fake_keyboard()

        with patch.dict("sys.modules", {"keyboard": fake_keyboard}):
            # Run start() in a thread so stop() can unblock it
            t = threading.Thread(target=hotkey_mod.start, daemon=True)
            t.start()

            # Give the thread a moment to register the hotkey and reach wait()
            t.join(timeout=0.1)

            hotkey_mod.stop()
            t.join(timeout=1.0)

        assert not t.is_alive(), "start() should have returned after stop()"
        fake_keyboard.add_hotkey.assert_called_once()
        fake_keyboard.unhook_all.assert_called_once()

    def test_uses_configured_hotkey(self, monkeypatch, tmp_path) -> None:
        monkeypatch.setattr(sys, "platform", "win32")
        monkeypatch.setattr("scrub_ai.config._config_path", lambda: tmp_path / "config.json")
        import scrub_ai.config as cfg
        cfg.save({"enabled": True, "hotkey": "ctrl+shift+x"})

        fake_keyboard = _make_fake_keyboard()

        with patch.dict("sys.modules", {"keyboard": fake_keyboard}):
            t = threading.Thread(target=hotkey_mod.start, daemon=True)
            t.start()
            t.join(timeout=0.1)
            hotkey_mod.stop()
            t.join(timeout=1.0)

        registered_shortcut = fake_keyboard.add_hotkey.call_args[0][0]
        assert registered_shortcut == "ctrl+shift+x"

    def test_noop_when_keyboard_not_importable(self, monkeypatch) -> None:
        monkeypatch.setattr(sys, "platform", "win32")
        with patch.dict("sys.modules", {"keyboard": None}):
            hotkey_mod.start()  # must not raise


class TestStop:
    def test_stop_sets_event(self) -> None:
        hotkey_mod._stop_event.clear()
        assert not hotkey_mod._stop_event.is_set()
        hotkey_mod.stop()
        assert hotkey_mod._stop_event.is_set()
