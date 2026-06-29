"""
notifier.py — Windows toast notifications for scrub-ai.

Shows a desktop notification after a sanitization event.

Design constraints:
  - win10toast is only available on Windows (pyproject.toml guards it with
    sys_platform == 'win32'), so this module must never be imported on other
    platforms.  The public API therefore does a runtime platform check and
    silently no-ops on non-Windows systems, which lets tests import this module
    without crashing.
  - Notification display is best-effort: if win10toast fails for any reason
    (e.g. notification service unavailable) we catch the exception and carry on.
"""

from __future__ import annotations

import sys


def _build_message(total: int, by_label: dict[str, int]) -> str:
    if total == 0:
        return "Clipboard is clean — nothing was masked."
    if by_label:
        detail = ", ".join(f"{label}={count}" for label, count in sorted(by_label.items()))
        return f"Masked {total} value(s): {detail}"
    return f"Masked {total} sensitive value(s)."


def notify(report: dict[str, object]) -> None:
    """Display a toast notification summarising a sanitization report.

    No-ops silently on non-Windows platforms or if win10toast is unavailable.
    """
    if sys.platform != "win32":
        return

    total = int(report.get("total_matches", 0))
    by_label = report.get("by_label", {})
    if not isinstance(by_label, dict):
        by_label = {}

    message = _build_message(total, by_label)

    try:
        from win10toast import ToastNotifier  # type: ignore[import]

        toaster = ToastNotifier()
        toaster.show_toast(
            "scrub-ai",
            message,
            duration=4,
            threaded=True,
        )
    except Exception:  # noqa: BLE001 — best-effort, never crash the caller
        pass
