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

# White shield shape (hexagonal polygon)
cx, cy = SIZE // 2, SIZE // 2
shield_pts = [
    (cx,      10),
    (cx + 18, 18),
    (cx + 18, 36),
    (cx,      54),
    (cx - 18, 36),
    (cx - 18, 18),
]
draw.polygon(shield_pts, fill=(255, 255, 255, 230))

# Blue "S" cutout inside the shield using two arcs + connecting strokes
s_color = bg_color
draw.arc([cx - 9, cy - 16, cx + 9, cy - 2],  start=180, end=360, fill=s_color, width=4)
draw.arc([cx - 9, cy - 2,  cx + 9, cy + 12], start=0,   end=180, fill=s_color, width=4)
draw.line([cx - 9, cy - 9, cx + 9, cy - 9], fill=s_color, width=3)
draw.line([cx - 9, cy + 5, cx + 9, cy + 5], fill=s_color, width=3)

img.save(OUT)
print(f"Saved {OUT}  ({img.size[0]}x{img.size[1]} RGBA)")
