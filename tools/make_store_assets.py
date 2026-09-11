#!/usr/bin/env python3
"""Blackshield Clock — store assets from the app's own render constants.

drawFace() in BlackshieldWidget.java: 900x420 bitmap, Pirata One,
bone time (size 190, centered at 0.44H), blood line at 0.60H (0.34W, 5px),
steel letterspaced date at 0.82H (size 58). Reproduced here 1:1 with the
bundled TTF so previewImage/store art match the real widget exactly.

Outputs:
  app/src/main/res/drawable-nodpi/widget_preview.png  (1800x840, 2x)
  store-assets/shot-1.png                             (1080x2400)
  store-assets/feature-1024x500.png
Run: python3 tools/make_store_assets.py
"""
import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONT = str(ROOT / "app" / "src" / "main" / "assets" / "pirata_one.ttf")
DEJAVU_BOLD = "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf"

BONE = "#E8E6E3"
BLOOD = "#C1121F"
STEEL = "#9BA0A6"
TILE_LO = "#101014"

BMP_W, BMP_H = 900, 420
SCALE = 2  # preview at 2x for crispness


def draw_face(scale: float = 1.0, bg: str | None = None,
              time_str: str = "9:41", date_str: str | None = None) -> Image.Image:
    W, H = round(BMP_W * scale), round(BMP_H * scale)
    im = Image.new("RGBA", (W, H), bg or (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if date_str is None:
        date_str = datetime.date.today().strftime("%A, %B %-d").upper()

    cx = W / 2

    # time — Pirata One, bone, soft shadow
    # Android: baseline = 0.44H - (ascent+descent)/2 (FontMetrics); PIL
    # anchor "ms" = middle-baseline, same reference frame.
    f_time = ImageFont.truetype(FONT, round(190 * scale))
    # Android: baseline = 0.44H - (fm.ascent + fm.descent)/2 with fm.ascent
    # negative-up == 0.44H + (ascent - descent)/2 with PIL's positive-up metrics.
    ascent, descent = f_time.getmetrics()
    baseline = H * 0.44 + (ascent - descent) / 2
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.text((cx + 3 * scale, baseline + 3 * scale), time_str, font=f_time,
            fill=(0, 0, 0, 180), anchor="ms")
    layer = layer.filter(ImageFilter.GaussianBlur(4 * scale))
    im.alpha_composite(layer)
    d.text((cx, baseline), time_str, font=f_time, fill=BONE, anchor="ms")

    # blood line
    line_w = W * 0.34
    line_y = H * 0.60
    d.rectangle([cx - line_w / 2, line_y, cx + line_w / 2, line_y + 5 * scale],
                fill=BLOOD)

    # date — Pirata One, steel, letterspaced caps
    f_date = ImageFont.truetype(FONT, round(58 * scale))
    tracking = round(58 * scale * 0.10)
    total = sum(d.textlength(ch, font=f_date) + tracking for ch in date_str) - tracking
    x = cx - total / 2
    y = H * 0.82
    for ch in date_str:
        d.text((x + 1.5 * scale, y + 1.5 * scale), ch, font=f_date,
               fill=(0, 0, 0, 150), anchor="ls")
        d.text((x, y), ch, font=f_date, fill=STEEL, anchor="ls")
        x += d.textlength(ch, font=f_date) + tracking
    return im


def main() -> None:
    # widget picker preview
    preview = draw_face(scale=SCALE, bg=TILE_LO)
    out = ROOT / "app" / "src" / "main" / "res" / "drawable-nodpi"
    out.mkdir(parents=True, exist_ok=True)
    preview.save(out / "widget_preview.png")

    # Play screenshot: face centered on dark wallpaper
    W, H = 1080, 2400
    shot = Image.new("RGB", (W, H), TILE_LO)
    px = shot.load()
    for y in range(H):  # subtle vertical lift
        f = 1 - y / H * 0.35
        row = tuple(round(c * f) for c in (16, 16, 20))
        for x in range(W):
            px[x, y] = row
    face = draw_face(scale=1.0)
    shot_rgba = shot.convert("RGBA")
    shot_rgba.alpha_composite(face, ((W - BMP_W) // 2, 700))
    d = ImageDraw.Draw(shot_rgba)
    f_word = ImageFont.truetype(DEJAVU_BOLD, 56)
    f_sub = ImageFont.truetype(DEJAVU_BOLD, 30)
    d.text((70, 150), "BLACKSHIELD CLOCK", font=f_word, fill=BONE)
    d.rectangle([70, 226, 190, 234], fill=BLOOD)
    d.text((70, 250), "gothic time · the blood line · zero permissions that matter",
           font=ImageFont.truetype(DEJAVU_BOLD, 24), fill=STEEL)
    shot_rgba.convert("RGB").save(ROOT / "store-assets" / "shot-1.png")

    # feature graphic 1024x500: face left, wordmark right
    feat = Image.new("RGB", (1024, 500), TILE_LO)
    fr = feat.convert("RGBA")
    face_small = draw_face(scale=0.62)
    fr.alpha_composite(face_small, (30, (500 - face_small.height) // 2))
    d = ImageDraw.Draw(fr)
    f_big = ImageFont.truetype(DEJAVU_BOLD, 64)
    d.text((640, 170), "BLACKSHIELD", font=f_big, fill=BONE)
    d.text((642, 250), "CLOCK", font=ImageFont.truetype(DEJAVU_BOLD, 40), fill=BLOOD)
    d.text((642, 310), "a gothic clock for the grid", font=f_sub, fill=STEEL)
    d.rectangle([0, 488, 1024, 500], fill=BLOOD)
    fr.convert("RGB").save(ROOT / "store-assets" / "feature-1024x500.png")
    print("wrote widget_preview.png, shot-1.png, feature-1024x500.png")


if __name__ == "__main__":
    main()
