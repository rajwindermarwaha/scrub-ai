from __future__ import annotations

from unittest.mock import patch, call

from click.testing import CliRunner

from scrub_ai.cli import main
from scrub_ai import config as cfg


class TestWatchFlag:
    def test_watch_starts_watcher(self, tmp_path, monkeypatch) -> None:
        monkeypatch.setattr(cfg, "_config_path", lambda: tmp_path / "config.json")
        runner = CliRunner()

        with patch("scrub_ai.watcher.start") as mock_start, \
             patch("scrub_ai.watcher.stop"):
            mock_start.side_effect = KeyboardInterrupt
            result = runner.invoke(main, ["--watch"])

        assert result.exit_code == 0
        mock_start.assert_called_once()

    def test_watch_sets_and_clears_watch_mode(self, tmp_path, monkeypatch) -> None:
        monkeypatch.setattr(cfg, "_config_path", lambda: tmp_path / "config.json")
        runner = CliRunner()

        states: list[bool] = []

        def fake_start() -> None:
            states.append(cfg.is_watch_mode())
            raise KeyboardInterrupt

        with patch("scrub_ai.watcher.start", side_effect=fake_start), \
             patch("scrub_ai.watcher.stop"):
            runner.invoke(main, ["--watch"])

        assert states == [True]
        assert cfg.is_watch_mode() is False

    def test_watch_prints_start_and_stop_messages(self, tmp_path, monkeypatch) -> None:
        monkeypatch.setattr(cfg, "_config_path", lambda: tmp_path / "config.json")
        runner = CliRunner()

        with patch("scrub_ai.watcher.start", side_effect=KeyboardInterrupt), \
             patch("scrub_ai.watcher.stop"):
            result = runner.invoke(main, ["--watch"], catch_exceptions=False)

        assert "Watch mode ON" in result.output
        assert "Watch mode OFF" in result.output
