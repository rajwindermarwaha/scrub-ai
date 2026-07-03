"""
tray.py — Windows system tray icon and menu for scrub-ai.

Provides a persistent tray icon that lets the user:
  - See whether scrub-ai is enabled
  - Toggle the hotkey listener on/off
  - Quit the background service

The tray icon runs on the main thread (pystray requirement).
The hotkey listener runs in a daemon thread spawned here.

Design constraints:
  - pystray + Pillow are cross-platform, but the full --start workflow is only
    meaningful on Windows (keyboard/toast).  This module guards start() with a
    platform check so callers can rely on it safely.
  - A small 64×64 icon is generated with Pillow if no icon.png is present in
    the assets/ directory, so the tool works out of the box without bundled
    assets.
  - The tray loop is blocking; cli.py runs it as the final step of `scrub-ai
    --start`.
"""

from __future__ import annotations

import sys
import threading
from pathlib import Path

from scrub_ai import config as cfg
import scrub_ai.hotkey as hotkey_mod


# ---------------------------------------------------------------------------
# Icon helpers
# ---------------------------------------------------------------------------

_ASSETS_DIR = Path(__file__).parent.parent / "assets"
_ICON_PATH = _ASSETS_DIR / "icon.png"


def _make_icon():
    """Return a PIL Image to use as the tray icon.

    Loads assets/icon.png when available; otherwise generates a simple
    64x64 coloured square so the tray is always usable.
    """
    from PIL import Image, ImageDraw  # type: ignore[import]

    if _ICON_PATH.exists():
        return Image.open(_ICON_PATH).convert("RGBA")

    # Generate a minimal fallback icon: dark blue rounded square with shield + bolt
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx = size // 2
    draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=12, fill=(25, 90, 170, 255))
    shield_pts = [(cx, 8), (cx + 20, 14), (cx + 20, 34), (cx, 56), (cx - 20, 34), (cx - 20, 14)]
    draw.polygon(shield_pts, fill=(255, 255, 255, 240))
    bolt_pts = [(cx + 4, 16), (cx - 2, 32), (cx + 4, 32), (cx - 4, 50), (cx + 10, 30), (cx + 3, 30), (cx + 10, 16)]
    draw.polygon(bolt_pts, fill=(25, 90, 170, 255))
    return img


# ---------------------------------------------------------------------------
# Menu actions
# ---------------------------------------------------------------------------

def _toggle_enabled(icon, item) -> None:  # noqa: ANN001
    current = cfg.is_enabled()
    cfg.set_enabled(not current)
    icon.update_menu()


def _quit_app(icon, item) -> None:  # noqa: ANN001
    hotkey_mod.stop()
    icon.stop()


def _enabled_label(item) -> str:  # noqa: ANN001
    return "Enabled: ON" if cfg.is_enabled() else "Enabled: OFF"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def start() -> None:
    """Start the hotkey listener thread and show the system tray icon.

    Blocks until the user selects Quit from the tray menu.
    On non-Windows platforms this function returns immediately.
    """
    if sys.platform != "win32":
        return

    try:
        import pystray  # type: ignore[import]
        from pystray import MenuItem as Item, Menu  # type: ignore[import]
    except ImportError:
        return

    # Launch hotkey listener in a background daemon thread
    hotkey_thread = threading.Thread(
        target=hotkey_mod.start,
        daemon=True,
        name="scrub-ai-hotkey",
    )
    hotkey_thread.start()

    hotkey_label = cfg.get_hotkey().upper()

    menu = Menu(
        Item(_enabled_label, _toggle_enabled),
        Item(f"Hotkey: {hotkey_label}", lambda *_: None, enabled=False),
        Menu.SEPARATOR,
        Item("Quit", _quit_app),
    )

    icon = pystray.Icon(
        name="scrub-ai",
        icon=_make_icon(),
        title="scrub-ai",
        menu=menu,
    )

    icon.run()  # blocks until icon.stop() is called
