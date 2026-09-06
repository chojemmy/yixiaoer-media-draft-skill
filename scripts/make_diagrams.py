#!/usr/bin/env python3
"""Draw the public, privacy-safe explanatory images for the README."""

from __future__ import annotations

import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
FONT_CANDIDATES = [
    r"C:\Windows\Fonts\msyhbd.ttc",
    r"C:\Windows\Fonts\simhei.ttf",
    r"C:\Windows\Fonts\NotoSansSC-VF.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]


def font(size: int):
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    raise FileNotFoundError("Install a Chinese-capable font or set a font in make_diagrams.py")


def paper(size=(1600, 900)):
    im = Image.new("RGB", size, (246, 242, 231))
    d = ImageDraw.Draw(im, "RGBA")
    for x in range(0, size[0], 48):
        d.line((x, 0, x, size[1]), fill=(97, 129, 140, 28), width=1)
    for y in range(0, size[1], 48):
        d.line((0, y, size[0], y), fill=(97, 129, 140, 28), width=1)
    random.seed(7)
    for _ in range(40):
        x = random.randrange(size[0])
        y = random.randrange(size[1])
        d.ellipse((x, y, x + random.randrange(3, 12), y + random.randrange(3, 12)), fill=(206, 180, 125, 20))
    return im


def rounded_box(d, box, fill, outline=(32, 66, 85, 220), width=3, radius=24):
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)
    # A second offset ink line gives a lightly hand-drawn feel.
    x1, y1, x2, y2 = box
    d.rounded_rectangle((x1 + 4, y1 + 2, x2 - 3, y2 + 3), radius=radius, outline=(32, 66, 85, 65), width=1)


def centered(d, box, text, f, fill, stroke=0, stroke_fill=(0, 0, 0, 0)):
    x1, y1, x2, y2 = box
    b = d.textbbox((0, 0), text, font=f, stroke_width=stroke)
    x = (x1 + x2 - (b[2] - b[0])) / 2
    y = (y1 + y2 - (b[3] - b[1])) / 2 - b[1]
    d.text((x, y), text, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)


def arrow(d, start, end):
    d.line((*start, *end), fill=(37, 91, 143, 230), width=8)
    ex, ey = end
    sx, sy = start
    if abs(ex - sx) >= abs(ey - sy):
        pts = [(ex, ey), (ex - 20, ey - 14), (ex - 20, ey + 14)]
    else:
        pts = [(ex, ey), (ex - 14, ey - 20), (ex + 14, ey - 20)]
    d.polygon(pts, fill=(37, 91, 143, 230))


def workflow(path: Path):
    im = paper()
    d = ImageDraw.Draw(im, "RGBA")
    d.text((68, 38), "从视频到可审核草稿", font=font(48), fill=(17, 47, 78, 255))
    d.text((72, 100), "Video → Reviewable draft", font=font(25), fill=(77, 104, 116, 255))
    labels = [
        ("选项确认", "Choose", (225, 237, 231, 245)),
        ("脚本校对", "Verify", (226, 235, 245, 245)),
        ("封面制作", "Cover", (249, 236, 201, 245)),
        ("字段填写", "Fields", (233, 226, 242, 245)),
        ("草稿审核", "Draft", (226, 239, 218, 245)),
    ]
    x0, y0, bw, bh, gap = 70, 275, 260, 275, 42
    for i, (cn, en, fill) in enumerate(labels):
        x = x0 + i * (bw + gap)
        rounded_box(d, (x, y0, x + bw, y0 + bh), fill)
        # Simple ink icon.
        cx, cy = x + bw // 2, y0 + 70
        d.ellipse((cx - 34, cy - 34, cx + 34, cy + 34), fill=(255, 255, 255, 160), outline=(37, 91, 143, 190), width=4)
        d.line((cx - 18, cy, cx + 18, cy), fill=(37, 91, 143, 210), width=5)
        d.line((cx, cy - 18, cx, cy + 18), fill=(37, 91, 143, 210), width=5)
        centered(d, (x + 10, y0 + 120, x + bw - 10, y0 + 192), cn, font(34), (17, 47, 78, 255))
        centered(d, (x + 10, y0 + 194, x + bw - 10, y0 + 238), en, font(23), (77, 104, 116, 255))
        if i < len(labels) - 1:
            arrow(d, (x + bw + 8, y0 + bh // 2), (x + bw + gap - 10, y0 + bh // 2))
    d.text((70, 655), "先选择，再上传；校验通过后停在草稿箱。", font=font(32), fill=(17, 47, 78, 255))
    d.text((72, 708), "Choose first, upload second; stop for human review.", font=font(24), fill=(77, 104, 116, 255))
    im.save(path, format="PNG", optimize=True)


def mock_screenshot(d, box, vertical: bool):
    x1, y1, x2, y2 = box
    d.rounded_rectangle(box, radius=18, fill=(54, 80, 82, 255), outline=(17, 47, 78, 230), width=5)
    # Abstract outdoor scene and a generic person silhouette; no real person is included.
    d.rectangle((x1 + 6, y1 + 6, x2 - 6, y1 + (y2 - y1) * 0.52), fill=(119, 157, 136, 255))
    d.rectangle((x1 + 6, y1 + (y2 - y1) * 0.52, x2 - 6, y2 - 6), fill=(192, 177, 135, 255))
    cx = x1 + (x2 - x1) * 0.65
    cy = y1 + (y2 - y1) * 0.39
    r = min(x2 - x1, y2 - y1) * 0.13
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(35, 42, 51, 255))
    d.rounded_rectangle((cx - r * 1.8, cy + r * 0.8, cx + r * 1.8, y1 + (y2 - y1) * 0.8), radius=20, fill=(35, 42, 51, 255))
    # Large thumbnail text blocks, deliberately short.
    tx = x1 + 28
    ty = y1 + (y2 - y1) * 0.68
    d.rounded_rectangle((tx - 10, ty - 12, x2 - 20, y2 - 22), radius=12, fill=(8, 25, 43, 205))
    d.text((tx, ty), "临界点", font=font(48 if vertical else 42), fill=(255, 255, 255, 255), stroke_width=4, stroke_fill=(7, 18, 28, 255))
    d.text((tx, ty + (58 if vertical else 52)), "一过就加速", font=font(29 if vertical else 25), fill=(247, 202, 77, 255), stroke_width=3, stroke_fill=(7, 18, 28, 255))


def cover_layout(path: Path):
    im = paper()
    d = ImageDraw.Draw(im, "RGBA")
    d.text((68, 38), "一帧画面 + 大字 = 可读封面", font=font(46), fill=(17, 47, 78, 255))
    d.text((72, 100), "One frame + large type", font=font(25), fill=(77, 104, 116, 255))
    mock_screenshot(d, (180, 190, 560, 730), vertical=True)
    mock_screenshot(d, (790, 300, 1430, 660), vertical=False)
    d.text((215, 755), "竖版 1080×1440", font=font(30), fill=(17, 47, 78, 255))
    d.text((842, 690), "横版 1920×1080", font=font(30), fill=(17, 47, 78, 255))
    d.text((875, 760), "白字 / 黄字 · 粗黑描边 · 少量文字", font=font(26), fill=(77, 104, 116, 255))
    d.text((875, 808), "White/yellow type · bold outline · one idea", font=font(22), fill=(77, 104, 116, 255))
    # Callout lines.
    arrow(d, (595, 360), (750, 420))
    d.text((620, 285), "同一套信息层级", font=font(28), fill=(37, 91, 143, 255))
    im.save(path, format="PNG", optimize=True)


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    workflow(ASSETS / "workflow-overview.png")
    cover_layout(ASSETS / "cover-layout.png")
    print("created workflow-overview.png and cover-layout.png")


if __name__ == "__main__":
    main()
