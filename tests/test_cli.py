from click.testing import CliRunner

from scrub_ai.cli import main


def test_cli_reads_from_stdin_and_sanitizes() -> None:
    runner = CliRunner()

    result = runner.invoke(main, input="password=SuperSecret123\n")

    assert result.exit_code == 0
    assert "[REDACTED]" in result.output
    assert "SuperSecret123" not in result.output


def test_cli_reads_from_file(tmp_path) -> None:
    runner = CliRunner()
    sample = tmp_path / "sample.log"
    sample.write_text("token=0123456789abcdef0123456789abcdef\n", encoding="utf-8")

    result = runner.invoke(main, ["--file", str(sample)])

    assert result.exit_code == 0
    assert "[TOKEN]" in result.output


def test_cli_dry_run_keeps_original_text() -> None:
    runner = CliRunner()

    result = runner.invoke(main, ["--dry-run"], input="password=SuperSecret123\n")

    assert result.exit_code == 0
    assert "password=SuperSecret123" in result.output
    assert "[REDACTED]" not in result.output
    assert "Dry run:" in result.output


def test_cli_copy_uses_clipboard(monkeypatch) -> None:
    runner = CliRunner()
    copied = {"value": None}

    def fake_copy(value: str) -> None:
        copied["value"] = value

    monkeypatch.setattr("scrub_ai.cli.pyperclip.copy", fake_copy)

    result = runner.invoke(main, ["--copy"], input="password=SuperSecret123\n")

    assert result.exit_code == 0
    assert copied["value"] is not None
    assert "[REDACTED]" in copied["value"]