"""Tests for scrub_ai/watcher.py."""

from __future__ import annotations

import threading
from pathlib import Path
from unittest.mock import patch, call

import pytest

import scrub_ai.config as config
import scrub_ai.watcher as watcher


# ---------------------------------------------------------------------------
# Fixture: isolated config + reset stop event before each test
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def isolated_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(config, "_config_path", lambda: tmp_path / "config.json")
    watcher._stop_event.clear()


# ---------------------------------------------------------------------------
# _watch_loop — happy path
# ---------------------------------------------------------------------------

class TestWatchLoop:
    def test_sanitizes_when_clipboard_changes(self) -> None:
        config.set_watch_mode(True)

        def fake_paste():
            watcher._stop_event.set()  # stop after first iteration
            return "password=secret123"

        with patch("scrub_ai.watcher.pyperclip.paste", side_effect=fake_paste), \
             patch("scrub_ai.watcher.pyperclip.copy") as mock_copy, \
             patch("scrub_ai.watcher.notify") as mock_notify:

            watcher._watch_loop()

            mock_copy.assert_called_once()
            mock_notify.assert_called_once()
            assert "[REDACTED]" in mock_copy.call_args[0][0]

    def test_does_not_sanitize_clean_text(self) -> None:
        config.set_watch_mode(True)

        with patch("scrub_ai.watcher.pyperclip.paste", return_value="hello world"), \
             patch("scrub_ai.watcher.pyperclip.copy") as mock_copy, \
             patch("scrub_ai.watcher.notify") as mock_notify:

            watcher._stop_event.set()
            watcher._watch_loop()

            mock_copy.assert_not_called()
            mock_notify.assert_not_called()

    def test_does_not_sanitize_same_text_twice(self) -> None:
        config.set_watch_mode(True)
        clipboard = ["password=secret123"]
        calls = 0

        def fake_paste():
            return clipboard[0]

        def fake_copy(text):
            nonlocal calls
            clipboard[0] = text
            calls += 1
            if calls >= 1:
                watcher._stop_event.set()

        with patch("scrub_ai.watcher.pyperclip.paste", side_effect=fake_paste), \
             patch("scrub_ai.watcher.pyperclip.copy", side_effect=fake_copy), \
             patch("scrub_ai.watcher.notify"), \
             patch.object(watcher._stop_event, "wait", return_value=None):

            watcher._watch_loop()

            # copy should only be called once — second iteration sees clean text, no change
            assert calls == 1

    def test_skips_when_watch_mode_off(self) -> None:
        config.set_watch_mode(False)

        with patch("scrub_ai.watcher.pyperclip.paste", return_value="password=secret123"), \
             patch("scrub_ai.watcher.pyperclip.copy") as mock_copy:

            watcher._stop_event.set()
            watcher._watch_loop()

            mock_copy.assert_not_called()

    def test_skips_empty_clipboard(self) -> None:
        config.set_watch_mode(True)

        with patch("scrub_ai.watcher.pyperclip.paste", return_value=""), \
             patch("scrub_ai.watcher.pyperclip.copy") as mock_copy:

            watcher._stop_event.set()
            watcher._watch_loop()

            mock_copy.assert_not_called()


# ---------------------------------------------------------------------------
# Resilience
# ---------------------------------------------------------------------------

class TestWatchLoopResilience:
    def test_swallows_paste_exception(self) -> None:
        config.set_watch_mode(True)

        with patch("scrub_ai.watcher.pyperclip.paste", side_effect=Exception("clipboard error")), \
             patch("scrub_ai.watcher.pyperclip.copy") as mock_copy:

            watcher._stop_event.set()
            watcher._watch_loop()  # should not raise

            mock_copy.assert_not_called()

    def test_swallows_copy_exception(self) -> None:
        config.set_watch_mode(True)

        with patch("scrub_ai.watcher.pyperclip.paste", return_value="password=secret123"), \
             patch("scrub_ai.watcher.pyperclip.copy", side_effect=Exception("copy error")), \
             patch("scrub_ai.watcher.notify"):

            watcher._stop_event.set()
            watcher._watch_loop()  # should not raise


# ---------------------------------------------------------------------------
# start() / stop()
# ---------------------------------------------------------------------------

class TestStartStop:
    def test_stop_unblocks_start(self) -> None:
        config.set_watch_mode(False)

        with patch("scrub_ai.watcher.pyperclip.paste", return_value=""):
            t = threading.Thread(target=watcher.start, daemon=True)
            t.start()
            watcher.stop()
            t.join(timeout=2)
            assert not t.is_alive()

    def test_stop_sets_event(self) -> None:
        watcher.stop()
        assert watcher._stop_event.is_set()
