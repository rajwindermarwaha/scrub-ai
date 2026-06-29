"""Tests for scrub_ai/notifier.py.

All Windows-path tests mock sys.platform to "win32" and inject a fake
win10toast module via patch.dict(sys.modules), so the suite runs cleanly on
Linux/macOS without win10toast installed.
"""

from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

import pytest

from scrub_ai.notifier import _build_message, notify


# ---------------------------------------------------------------------------
# _build_message — pure function, no mocking needed
# ---------------------------------------------------------------------------

class TestBuildMessage:
    def test_zero_matches_returns_clean_message(self) -> None:
        assert _build_message(0, {}) == "Clipboard is clean — nothing was masked."

    def test_zero_matches_ignores_non_empty_label_dict(self) -> None:
        # total=0 should always return the clean message regardless of by_label
        assert _build_message(0, {"api_key": 1}) == "Clipboard is clean — nothing was masked."

    def test_with_labels_includes_count_and_detail(self) -> None:
        msg = _build_message(3, {"api_key": 2, "password": 1})
        assert "3" in msg
        assert "api_key=2" in msg
        assert "password=1" in msg

    def test_with_labels_are_sorted_alphabetically(self) -> None:
        msg = _build_message(2, {"password": 1, "api_key": 1})
        assert msg.index("api_key") < msg.index("password")

    def test_without_labels_returns_generic_message(self) -> None:
        msg = _build_message(5, {})
        assert "5" in msg
        assert "sensitive" in msg

    def test_single_match_with_label(self) -> None:
        msg = _build_message(1, {"jwt": 1})
        assert "1" in msg
        assert "jwt=1" in msg


# ---------------------------------------------------------------------------
# Helpers for Windows-path tests
# ---------------------------------------------------------------------------

def _make_mock_win10toast() -> tuple[MagicMock, MagicMock, MagicMock]:
    """Return (mock_module, mock_class, mock_instance)."""
    mock_instance = MagicMock()
    mock_class = MagicMock(return_value=mock_instance)
    mock_module = MagicMock()
    mock_module.ToastNotifier = mock_class
    return mock_module, mock_class, mock_instance


# ---------------------------------------------------------------------------
# notify() — platform guard (non-Windows should be a no-op)
# ---------------------------------------------------------------------------

class TestNotifyPlatformGuard:
    def test_noop_on_linux(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(sys, "platform", "linux")
        # win10toast absent; if the guard fails this would ImportError
        with patch.dict("sys.modules", {"win10toast": None}):
            notify({"total_matches": 5, "by_label": {"api_key": 5}})  # must not raise

    def test_noop_on_darwin(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(sys, "platform", "darwin")
        with patch.dict("sys.modules", {"win10toast": None}):
            notify({"total_matches": 1, "by_label": {}})  # must not raise


# ---------------------------------------------------------------------------
# notify() — Windows path: correct calls to win10toast
# ---------------------------------------------------------------------------

class TestNotifyWindows:
    def test_calls_show_toast_with_correct_arguments(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(sys, "platform", "win32")
        mock_module, mock_class, mock_instance = _make_mock_win10toast()

        with patch.dict("sys.modules", {"win10toast": mock_module}):
            notify({"total_matches": 2, "by_label": {"jwt": 2}})

        mock_class.assert_called_once()
        mock_instance.show_toast.assert_called_once_with(
            "scrub-ai",
            "Masked 2 value(s): jwt=2",
            duration=4,
            threaded=True,
        )

    def test_clean_clipboard_shows_clean_message(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(sys, "platform", "win32")
        mock_module, _, mock_instance = _make_mock_win10toast()

        with patch.dict("sys.modules", {"win10toast": mock_module}):
            notify({"total_matches": 0, "by_label": {}})

        _, call_args, _ = mock_instance.show_toast.mock_calls[0]
        assert call_args[1] == "Clipboard is clean — nothing was masked."

    def test_multiple_labels_in_message(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(sys, "platform", "win32")
        mock_module, _, mock_instance = _make_mock_win10toast()

        with patch.dict("sys.modules", {"win10toast": mock_module}):
            notify({"total_matches": 4, "by_label": {"aws_key": 1, "password": 3}})

        _, call_args, _ = mock_instance.show_toast.mock_calls[0]
        assert "aws_key=1" in call_args[1]
        assert "password=3" in call_args[1]

    def test_app_title_is_scrub_ai(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(sys, "platform", "win32")
        mock_module, _, mock_instance = _make_mock_win10toast()

        with patch.dict("sys.modules", {"win10toast": mock_module}):
            notify({"total_matches": 1, "by_label": {}})

        _, call_args, _ = mock_instance.show_toast.mock_calls[0]
        assert call_args[0] == "scrub-ai"


# ---------------------------------------------------------------------------
# notify() — Windows path: resilience (must never crash the caller)
# ---------------------------------------------------------------------------

class TestNotifyResilience:
    def test_swallows_show_toast_exception(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(sys, "platform", "win32")
        mock_module, _, mock_instance = _make_mock_win10toast()
        mock_instance.show_toast.side_effect = RuntimeError("notification service unavailable")

        with patch.dict("sys.modules", {"win10toast": mock_module}):
            notify({"total_matches": 1, "by_label": {}})  # must not raise

    def test_swallows_win10toast_import_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(sys, "platform", "win32")
        # Setting to None causes ImportError when the module tries to import it
        with patch.dict("sys.modules", {"win10toast": None}):
            notify({"total_matches": 1, "by_label": {}})  # must not raise

    def test_handles_non_dict_by_label(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(sys, "platform", "win32")
        mock_module, _, mock_instance = _make_mock_win10toast()

        with patch.dict("sys.modules", {"win10toast": mock_module}):
            notify({"total_matches": 1, "by_label": None})  # must not raise

        _, call_args, _ = mock_instance.show_toast.mock_calls[0]
        # Falls back to generic message (no labels)
        assert "1 sensitive value(s)" in call_args[1]

    def test_handles_missing_keys_in_report(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(sys, "platform", "win32")
        mock_module, _, mock_instance = _make_mock_win10toast()

        with patch.dict("sys.modules", {"win10toast": mock_module}):
            notify({})  # empty report — must not raise

        # total defaults to 0 → clean message
        _, call_args, _ = mock_instance.show_toast.mock_calls[0]
        assert call_args[1] == "Clipboard is clean — nothing was masked."
