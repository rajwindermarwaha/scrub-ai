from __future__ import annotations

import sys
from pathlib import Path

import click
import pyperclip

from scrub_ai.sanitizer import sanitize_text
from scrub_ai import config as cfg


def _load_input(file_path: str | None) -> str:
    if file_path is not None:
        return Path(file_path).read_text(encoding="utf-8")

    if not sys.stdin.isatty():
        return sys.stdin.read()

    raise click.ClickException("No input provided. Use --file or pipe text via stdin.")


def _format_report(report: dict[str, object]) -> str:
    total = int(report.get("total_matches", 0))
    if total == 0:
        return "No sensitive content detected."

    by_label = report.get("by_label", {})
    if isinstance(by_label, dict) and by_label:
        details = ", ".join(f"{label}={count}" for label, count in sorted(by_label.items()))
        return f"Detected {total} sensitive value(s): {details}"

    return f"Detected {total} sensitive value(s)."


@click.command()
@click.option("--file", "file_path", type=click.Path(exists=True, dir_okay=False, path_type=str), help="Read input from a file.")
@click.option("--dry-run", is_flag=True, help="Show detections but do not modify the output text.")
@click.option("--copy", "copy_output", is_flag=True, help="Copy output text to clipboard.")
@click.option("--start", is_flag=True, help="Start background hotkey listener and system tray (Windows only).")
def main(file_path: str | None, dry_run: bool, copy_output: bool, start: bool) -> None:
    """Sanitize sensitive content from text."""

    if start:
        if sys.platform != "win32":
            raise click.ClickException("--start is only supported on Windows.")
        from scrub_ai import tray
        click.echo("scrub-ai running. Press Ctrl+Alt+S to sanitize clipboard. Right-click the tray icon to quit.", err=True)
        tray.start()
        return

    input_text = _load_input(file_path)
    clean_text, report = sanitize_text(input_text)

    output_text = input_text if dry_run else clean_text
    sys.stdout.write(output_text)

    click.echo("", err=True)
    if dry_run:
        click.echo(f"Dry run: {_format_report(report)}", err=True)
    else:
        click.echo(_format_report(report), err=True)

    if copy_output:
        try:
            pyperclip.copy(output_text)
            click.echo("Copied output to clipboard.", err=True)
        except pyperclip.PyperclipException as exc:
            raise click.ClickException(f"Clipboard copy failed: {exc}") from exc


if __name__ == "__main__":
    main()