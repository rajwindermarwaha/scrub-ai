"""Tests for scrub_ai/config.py.

All tests redirect the config file to a temporary directory via monkeypatching
so they never touch the real user config on disk.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

import scrub_ai.config as config


# ---------------------------------------------------------------------------
# Fixture: redirect _config_path to a tmp dir for every test
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def isolated_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point config._config_dir() at a fresh temp directory for each test."""
    config_file = tmp_path / "config.json"
    monkeypatch.setattr(config, "_config_path", lambda: config_file)
    return config_file


# ---------------------------------------------------------------------------
# _config_dir — platform path selection
# ---------------------------------------------------------------------------

class TestConfigDir:
    def test_windows_uses_appdata(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setattr(sys, "platform", "win32")
        monkeypatch.setenv("APPDATA", str(tmp_path))
        # Re-import the function so it re-evaluates sys.platform
        from importlib import reload
        reloaded = reload(config)
        result = reloaded._config_dir()
        assert result == tmp_path / "scrub-ai"

    def test_linux_uses_xdg_config(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(sys, "platform", "linux")
        from importlib import reload
        reloaded = reload(config)
        result = reloaded._config_dir()
        assert result == Path.home() / ".config" / "scrub-ai"

    def test_windows_falls_back_when_appdata_missing(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(sys, "platform", "win32")
        monkeypatch.delenv("APPDATA", raising=False)
        from importlib import reload
        reloaded = reload(config)
        result = reloaded._config_dir()
        assert result == Path.home() / "AppData" / "Roaming" / "scrub-ai"


# ---------------------------------------------------------------------------
# load() — defaults when no file exists
# ---------------------------------------------------------------------------

class TestLoad:
    def test_returns_defaults_when_file_missing(self) -> None:
        result = config.load()
        assert result["enabled"] is True
        assert result["hotkey"] == "ctrl+alt+s"

    def test_returns_defaults_when_file_is_corrupt_json(
        self, isolated_config: Path
    ) -> None:
        isolated_config.write_text("{ not valid json }", encoding="utf-8")
        result = config.load()
        assert result["enabled"] is True
        assert result["hotkey"] == "ctrl+alt+s"

    def test_merges_stored_values_over_defaults(self, isolated_config: Path) -> None:
        isolated_config.write_text(
            json.dumps({"enabled": False}), encoding="utf-8"
        )
        result = config.load()
        assert result["enabled"] is False
        # hotkey still comes from defaults
        assert result["hotkey"] == "ctrl+alt+s"

    def test_returns_all_stored_keys(self, isolated_config: Path) -> None:
        isolated_config.write_text(
            json.dumps({"enabled": False, "hotkey": "ctrl+shift+x"}),
            encoding="utf-8",
        )
        result = config.load()
        assert result["enabled"] is False
        assert result["hotkey"] == "ctrl+shift+x"

    def test_unknown_extra_keys_are_preserved(self, isolated_config: Path) -> None:
        isolated_config.write_text(
            json.dumps({"enabled": True, "future_option": 42}), encoding="utf-8"
        )
        result = config.load()
        assert result.get("future_option") == 42


# ---------------------------------------------------------------------------
# save() — writes valid JSON, creates parent directories
# ---------------------------------------------------------------------------

class TestSave:
    def test_writes_json_to_disk(self, isolated_config: Path) -> None:
        config.save({"enabled": False, "hotkey": "ctrl+alt+s"})
        assert isolated_config.exists()
        data = json.loads(isolated_config.read_text(encoding="utf-8"))
        assert data["enabled"] is False

    def test_creates_parent_directory_if_missing(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        deep_path = tmp_path / "a" / "b" / "config.json"
        monkeypatch.setattr(config, "_config_path", lambda: deep_path)
        config.save({"enabled": True, "hotkey": "ctrl+alt+s"})
        assert deep_path.exists()

    def test_round_trip(self, isolated_config: Path) -> None:
        original = {"enabled": False, "hotkey": "ctrl+shift+s"}
        config.save(original)
        loaded = config.load()
        assert loaded["enabled"] is False
        assert loaded["hotkey"] == "ctrl+shift+s"

    def test_overwrites_existing_file(self, isolated_config: Path) -> None:
        config.save({"enabled": True, "hotkey": "ctrl+alt+s"})
        config.save({"enabled": False, "hotkey": "ctrl+alt+s"})
        data = json.loads(isolated_config.read_text(encoding="utf-8"))
        assert data["enabled"] is False


# ---------------------------------------------------------------------------
# is_enabled() / set_enabled()
# ---------------------------------------------------------------------------

class TestIsEnabled:
    def test_true_by_default(self) -> None:
        assert config.is_enabled() is True

    def test_false_after_set_enabled_false(self) -> None:
        config.set_enabled(False)
        assert config.is_enabled() is False

    def test_true_after_set_enabled_true(self) -> None:
        config.set_enabled(False)
        config.set_enabled(True)
        assert config.is_enabled() is True

    def test_persists_to_disk(self, isolated_config: Path) -> None:
        config.set_enabled(False)
        data = json.loads(isolated_config.read_text(encoding="utf-8"))
        assert data["enabled"] is False


# ---------------------------------------------------------------------------
# get_hotkey()
# ---------------------------------------------------------------------------

class TestGetHotkey:
    def test_returns_default_when_no_file(self) -> None:
        assert config.get_hotkey() == "ctrl+alt+s"

    def test_returns_stored_hotkey(self, isolated_config: Path) -> None:
        isolated_config.write_text(
            json.dumps({"enabled": True, "hotkey": "ctrl+shift+x"}),
            encoding="utf-8",
        )
        assert config.get_hotkey() == "ctrl+shift+x"


# ---------------------------------------------------------------------------
# is_watch_mode() / set_watch_mode()
# ---------------------------------------------------------------------------

class TestIsWatchMode:
    def test_false_by_default(self) -> None:
        assert config.is_watch_mode() is False

    def test_true_after_set_watch_mode_true(self) -> None:
        config.set_watch_mode(True)
        assert config.is_watch_mode() is True

    def test_false_after_set_watch_mode_false(self) -> None:
        config.set_watch_mode(True)
        config.set_watch_mode(False)
        assert config.is_watch_mode() is False

    def test_persists_to_disk(self, isolated_config: Path) -> None:
        config.set_watch_mode(True)
        data = json.loads(isolated_config.read_text(encoding="utf-8"))
        assert data["watch_mode"] is True

    def test_does_not_affect_other_keys(self) -> None:
        config.set_watch_mode(True)
        assert config.is_enabled() is True
        assert config.get_hotkey() == "ctrl+alt+s"
