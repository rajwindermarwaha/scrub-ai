from __future__ import annotations

import sys
import types
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest


# ---------------------------------------------------------------------------
# Label helpers
# ---------------------------------------------------------------------------

class TestEnabledLabel:
    def test_returns_on_when_enabled(self, tmp_path, monkeypatch) -> None:
        import scrub_ai.config as cfg
        from scrub_ai.tray import _enabled_label
        monkeypatch.setattr(cfg, "_config_path", lambda: tmp_path / "config.json")
        cfg.set_enabled(True)
        assert _enabled_label(None) == "Enabled: ON"

    def test_returns_off_when_disabled(self, tmp_path, monkeypatch) -> None:
        import scrub_ai.config as cfg
        from scrub_ai.tray import _enabled_label
        monkeypatch.setattr(cfg, "_config_path", lambda: tmp_path / "config.json")
        cfg.set_enabled(False)
        assert _enabled_label(None) == "Enabled: OFF"


class TestWatchModeLabel:
    def test_returns_on_when_active(self, tmp_path, monkeypatch) -> None:
        import scrub_ai.config as cfg
        from scrub_ai.tray import _watch_mode_label
        monkeypatch.setattr(cfg, "_config_path", lambda: tmp_path / "config.json")
        cfg.set_watch_mode(True)
        assert _watch_mode_label(None) == "Watch Mode: ON"

    def test_returns_off_when_inactive(self, tmp_path, monkeypatch) -> None:
        import scrub_ai.config as cfg
        from scrub_ai.tray import _watch_mode_label
        monkeypatch.setattr(cfg, "_config_path", lambda: tmp_path / "config.json")
        cfg.set_watch_mode(False)
        assert _watch_mode_label(None) == "Watch Mode: OFF"


# ---------------------------------------------------------------------------
# Toggle actions
# ---------------------------------------------------------------------------

class TestToggleEnabled:
    def test_flips_true_to_false(self, tmp_path, monkeypatch) -> None:
        import scrub_ai.config as cfg
        from scrub_ai.tray import _toggle_enabled
        monkeypatch.setattr(cfg, "_config_path", lambda: tmp_path / "config.json")
        cfg.set_enabled(True)
        icon = MagicMock()
        _toggle_enabled(icon, None)
        assert cfg.is_enabled() is False
        icon.update_menu.assert_called_once()

    def test_flips_false_to_true(self, tmp_path, monkeypatch) -> None:
        import scrub_ai.config as cfg
        from scrub_ai.tray import _toggle_enabled
        monkeypatch.setattr(cfg, "_config_path", lambda: tmp_path / "config.json")
        cfg.set_enabled(False)
        icon = MagicMock()
        _toggle_enabled(icon, None)
        assert cfg.is_enabled() is True
        icon.update_menu.assert_called_once()


class TestToggleWatchMode:
    def test_flips_false_to_true(self, tmp_path, monkeypatch) -> None:
        import scrub_ai.config as cfg
        from scrub_ai.tray import _toggle_watch_mode
        monkeypatch.setattr(cfg, "_config_path", lambda: tmp_path / "config.json")
        cfg.set_watch_mode(False)
        icon = MagicMock()
        _toggle_watch_mode(icon, None)
        assert cfg.is_watch_mode() is True
        icon.update_menu.assert_called_once()

    def test_flips_true_to_false(self, tmp_path, monkeypatch) -> None:
        import scrub_ai.config as cfg
        from scrub_ai.tray import _toggle_watch_mode
        monkeypatch.setattr(cfg, "_config_path", lambda: tmp_path / "config.json")
        cfg.set_watch_mode(True)
        icon = MagicMock()
        _toggle_watch_mode(icon, None)
        assert cfg.is_watch_mode() is False
        icon.update_menu.assert_called_once()


# ---------------------------------------------------------------------------
# Quit action
# ---------------------------------------------------------------------------

class TestQuitApp:
    def test_stops_hotkey_watcher_and_icon(self) -> None:
        from scrub_ai.tray import _quit_app
        icon = MagicMock()
        with (
            patch("scrub_ai.tray.hotkey_mod") as mock_hotkey,
            patch("scrub_ai.tray.watcher_mod") as mock_watcher,
        ):
            _quit_app(icon, None)
            mock_hotkey.stop.assert_called_once()
            mock_watcher.stop.assert_called_once()
            icon.stop.assert_called_once()

    def test_stops_in_correct_order(self) -> None:
        """Hotkey and watcher stop before icon.stop."""
        from scrub_ai.tray import _quit_app
        call_order: list[str] = []
        icon = MagicMock()
        icon.stop.side_effect = lambda: call_order.append("icon")

        with (
            patch("scrub_ai.tray.hotkey_mod") as mock_hotkey,
            patch("scrub_ai.tray.watcher_mod") as mock_watcher,
        ):
            mock_hotkey.stop.side_effect = lambda: call_order.append("hotkey")
            mock_watcher.stop.side_effect = lambda: call_order.append("watcher")
            _quit_app(icon, None)

        assert call_order == ["hotkey", "watcher", "icon"]


# ---------------------------------------------------------------------------
# Icon generation
# ---------------------------------------------------------------------------

class TestMakeIcon:
    def test_returns_image_when_icon_file_missing(self, tmp_path) -> None:
        from scrub_ai.tray import _make_icon
        with patch("scrub_ai.tray._ICON_PATH", tmp_path / "nonexistent.png"):
            img = _make_icon()
            assert img is not None
            assert img.size == (64, 64)

    def test_loads_existing_icon_file(self, tmp_path) -> None:
        from PIL import Image
        from scrub_ai.tray import _make_icon

        # Write a minimal valid PNG to tmp_path
        icon_path = tmp_path / "icon.png"
        img_src = Image.new("RGBA", (32, 32), (255, 0, 0, 255))
        img_src.save(icon_path)

        with patch("scrub_ai.tray._ICON_PATH", icon_path):
            img = _make_icon()
            assert img.size == (32, 32)


# ---------------------------------------------------------------------------
# Platform guard
# ---------------------------------------------------------------------------

class TestStartPlatformGuard:
    def test_returns_immediately_on_linux(self) -> None:
        import scrub_ai.tray as tray_mod
        with patch.object(sys, "platform", "linux"):
            # Should return without calling pystray at all
            tray_mod.start()  # no exception = pass

    def test_returns_immediately_on_darwin(self) -> None:
        import scrub_ai.tray as tray_mod
        with patch.object(sys, "platform", "darwin"):
            tray_mod.start()

    def test_returns_when_pystray_not_importable(self) -> None:
        import scrub_ai.tray as tray_mod
        with (
            patch.object(sys, "platform", "win32"),
            patch.dict(sys.modules, {"pystray": None}),
        ):
            tray_mod.start()  # ImportError swallowed, no exception


# ---------------------------------------------------------------------------
# start() integration on "Windows"
# ---------------------------------------------------------------------------

class TestStartIntegration:
    def test_spawns_hotkey_and_watcher_threads_and_runs_icon(self) -> None:
        import scrub_ai.tray as tray_mod

        fake_icon_instance = MagicMock()

        fake_pystray = types.ModuleType("pystray")
        fake_pystray.Icon = MagicMock(return_value=fake_icon_instance)

        fake_menu_cls = MagicMock()
        fake_menu_cls.SEPARATOR = MagicMock()
        fake_pystray.Menu = fake_menu_cls
        fake_pystray.MenuItem = MagicMock()

        spawned_threads: list[str] = []

        original_thread = __builtins__  # noqa: F841 — just a reference

        class _FakeThread:
            def __init__(self, target=None, daemon=None, name=None, **_):
                self.name = name
                self._target = target

            def start(self):
                spawned_threads.append(self.name)

        with (
            patch.object(sys, "platform", "win32"),
            patch.dict(sys.modules, {"pystray": fake_pystray}),
            patch("scrub_ai.tray.threading.Thread", side_effect=_FakeThread),
            patch("scrub_ai.tray._make_icon", return_value=MagicMock()),
            patch("scrub_ai.tray.hotkey_mod"),
            patch("scrub_ai.tray.watcher_mod"),
        ):
            tray_mod.start()

        assert "scrub-ai-hotkey" in spawned_threads
        assert "scrub-ai-watcher" in spawned_threads
        fake_icon_instance.run.assert_called_once()
