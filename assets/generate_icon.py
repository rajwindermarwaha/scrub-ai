"""
Generate assets/icon.png — run this script to regenerate the tray icon.

Usage:
    python assets/generate_icon.py

Requires Pillow (already a project dependency).
Output: assets/icon.png (64x64 RGBA PNG)
"""

from pathlib import Path
from PIL import Image, ImageDraw

SIZE = 64
OUT = Path(__file__).parent / "icon.png"

img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Background: rounded square, dark blue
bg_color = (25, 90, 170, 255)
draw.rounded_rectangle([0, 0, SIZE - 1, SIZE - 1], radius=12, fill=bg_color)

# White shield — classic pointed-bottom shape
cx, cy = SIZE // 2, SIZE // 2
shield_pts = [
    (cx,      8),       # top centre
    (cx + 20, 14),      # top right
    (cx + 20, 34),      # mid right
    (cx,      56),      # bottom point
    (cx - 20, 34),      # mid left
    (cx - 20, 14),      # top left
]
draw.polygon(shield_pts, fill=(255, 255, 255, 240))

# Lightning bolt cutout — fast + powerful
bolt_color = bg_color
bolt_pts = [
    (cx + 4,  16),      # top right
    (cx - 2,  32),      # middle left
    (cx + 4,  32),      # middle right
    (cx - 4,  50),      # bottom left
    (cx + 10, 30),      # lower right
    (cx + 3,  30),      # lower middle
    (cx + 10, 16),      # back to top
]
draw.polygon(bolt_pts, fill=bolt_color)

img.save(OUT)
print(f"Saved {OUT}  ({img.size[0]}x{img.size[1]} RGBA)")
