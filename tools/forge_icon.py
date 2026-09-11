#!/usr/bin/env python3
"""Blackshield Clock — icon forge. Steel tile + bone clock glyph + blood dash.

Renders: mipmap-xxxhdpi webps, adaptive icon xml, store icon-512.
Run with the icon-pack venv: ../blackshield-icon-pack/tools/.venv/bin/python tools/forge_icon.py
"""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "app" / "src" / "main" / "res"
BUILD = ROOT / "build" / "svg"

TILE_HI, TILE_LO, TILE_STROKE = "#1E1E26", "#101014", "#2A2A31"
BONE_HI, BONE_LO = "#F5F1E8", "#D9D2C5"
BLOOD = "#C1121F"

# Material "schedule" (filled clock), Apache-2.0, 24x24 grid
CLOCK = ("M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12"
         "S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8"
         "-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z")

LEGACY_SCALE = 4.6
LEGACY_OFF = (192 - 24 * LEGACY_SCALE) / 2
FG_SCALE = 4.2
FG_OFF = (192 - 24 * FG_SCALE) / 2

DEFS = f"""<defs>
  <linearGradient id="tile" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{TILE_HI}"/><stop offset="1" stop-color="{TILE_LO}"/>
  </linearGradient>
  <linearGradient id="glyphgrad" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{BONE_HI}"/><stop offset="1" stop-color="{BONE_LO}"/>
  </linearGradient>
</defs>"""


def legacy() -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="192" height="192" viewBox="0 0 192 192">
{DEFS}
<rect x="10.4" y="9.5" width="171.2" height="171.2" rx="34" fill="url(#tile)" stroke="{TILE_STROKE}" stroke-width="1.5"/>
<g fill="url(#glyphgrad)" transform="translate({LEGACY_OFF:.1f} {LEGACY_OFF - 4:.1f}) scale({LEGACY_SCALE})"><path d="{CLOCK}"/></g>
<rect x="76" y="156" width="40" height="6" rx="3" fill="{BLOOD}"/>
</svg>"""


def fg() -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="192" height="192" viewBox="0 0 192 192">
{DEFS}
<g fill="url(#glyphgrad)" transform="translate({FG_OFF:.1f} {FG_OFF:.1f}) scale({FG_SCALE})"><path d="{CLOCK}"/></g>
</svg>"""


def render(svg: str, px: int, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    BUILD.mkdir(parents=True, exist_ok=True)
    tmp_svg = BUILD / (out.stem + ".svg")
    tmp_svg.write_text(svg)
    if out.suffix == ".png":
        subprocess.run(["rsvg-convert", "-w", str(px), "-h", str(px),
                        str(tmp_svg), "-o", str(out)], check=True)
        return
    tmp_png = out.with_suffix(".png")
    subprocess.run(["rsvg-convert", "-w", str(px), "-h", str(px),
                    str(tmp_svg), "-o", str(tmp_png)], check=True)
    subprocess.run(["magick", str(tmp_png), "-quality", "92", str(out)], check=True)
    tmp_png.unlink()


def main() -> None:
    render(legacy(), 192, RES / "mipmap-xxxhdpi" / "ic_launcher.webp")
    render(fg(), 432, RES / "mipmap-xxxhdpi" / "ic_launcher_fg.webp")
    render(legacy(), 512, ROOT / "store-assets" / "icon-512.png")

    anydpi = RES / "mipmap-anydpi-v26"
    anydpi.mkdir(parents=True, exist_ok=True)
    (anydpi / "ic_launcher.xml").write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">\n'
        '    <background android:drawable="@color/tile_bg" />\n'
        '    <foreground android:drawable="@mipmap/ic_launcher_fg" />\n'
        '    <monochrome android:drawable="@mipmap/ic_launcher_fg" />\n'
        '</adaptive-icon>\n')

    colors = RES / "values" / "colors.xml"
    existing = colors.read_text() if colors.exists() else \
        '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n</resources>\n'
    if "tile_bg" not in existing:
        colors.write_text(existing.replace(
            "</resources>", f'    <color name="tile_bg">{TILE_LO}</color>\n</resources>\n'))
    print("forged: legacy webp, adaptive fg, store 512, anydpi xml, tile_bg color")


if __name__ == "__main__":
    main()
