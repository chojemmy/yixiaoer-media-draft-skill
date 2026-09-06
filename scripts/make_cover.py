#!/usr/bin/env python3
"""Create readable vertical and horizontal covers from a still frame.

The script is deliberately offline: it never calls a model or a network API.
Chinese typography is rendered locally so small platform thumbnails keep the
exact title supplied by the user.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFilter, ImageFont


FONT_CANDIDATES = (
    os.environ.get("YIXIAOER_COVER_FONT", ""),
    r"C:\Windows\Fonts\msyhbd.ttc",
    r"C:\Windows\Fonts\simhei.ttf",
    r"C:\Windows\Fonts\NotoSansSC-VF.ttf",
    "/System/Library/Fonts/PingFang.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
)


def find_font() -> str:
    for candidate in FONT_CANDIDATES:
        if candidate and Path(candidate).exists():
            return candidate
    raise FileNotFoundError(
        "No usable font found. Set YIXIAOER_COVER_FONT to a Chinese-capable TTF/OTF/TTC."
    )


def load_font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(find_font(), size=size)


def parse_size(raw: str) -> tuple[int, int]:
    try:
        width, height = (int(v) for v in raw.lower().replace("×", "x").split("x", 1))
    except Exception as exc:  # pragma: no cover - argparse turns this into a friendly error
        raise argparse.ArgumentTypeError("size must look like 1080x1440") from exc
    if width < 64 or height < 64:
        raise argparse.ArgumentTypeError("width and height must be at least 64")
    return width, height


def fit_crop(image: Image.Image, target: tuple[int, int], center_x: float) -> Image.Image:
    target_w, target_h = target
    source_w, source_h = image.size
    target_ratio = target_w / target_h
    source_ratio = source_w / source_h
    if source_ratio > target_ratio:
        crop_w = round(source_h * target_ratio)
        left = round(source_w * center_x - crop_w / 2)
        left = max(0, min(left, source_w - crop_w))
        box = (left, 0, left + crop_w, source_h)
    else:
        crop_h = round(source_w / target_ratio)
        top = max(0, min(round(source_h / 2 - crop_h / 2), source_h - crop_h))
        box = (0, top, source_w, top + crop_h)
    return image.crop(box).resize(target, Image.Resampling.LANCZOS)


def outlined_text(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str,
                  font: ImageFont.FreeTypeFont, fill: tuple[int, ...],
                  stroke: int, stroke_fill: tuple[int, ...]) -> None:
    draw.text(xy, text, font=font, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)


def make_vertical(source: Image.Image, size: tuple[int, int], title: str,
                  subtitle: str, brand: str, subject_x: float) -> Image.Image:
    width, height = size
    panel_top = round(height * 0.62)
    image_height = round(height * 0.70)
    background = fit_crop(source, (width, height), subject_x).filter(ImageFilter.GaussianBlur(18))
    foreground = fit_crop(source, (width, image_height), subject_x)
    canvas = background.convert("RGB")
    canvas.paste(foreground, (0, 0))
    draw = ImageDraw.Draw(canvas, "RGBA")
    draw.rectangle((0, panel_top, width, height), fill=(8, 25, 43, 232))
    draw.rectangle((0, panel_top, width, panel_top + max(4, height // 180)), fill=(241, 193, 76, 255))

    margin = max(32, round(width * 0.065))
    eyebrow_font = load_font(max(24, round(width * 0.039)))
    title_font = load_font(max(44, round(width * 0.090)))
    subtitle_font = load_font(max(30, round(width * 0.054)))
    brand_font = load_font(max(22, round(width * 0.032)))
    y = panel_top + round(height * 0.047)
    outlined_text(draw, (margin, y), "技术替代的", eyebrow_font, (247, 207, 103, 255), 2, (7, 18, 28, 255))
    outlined_text(draw, (margin, y + eyebrow_font.size + round(height * 0.012)), title,
                  title_font, (255, 255, 255, 255), max(3, width // 155), (7, 18, 28, 255))
    outlined_text(draw, (margin, y + title_font.size + round(height * 0.105)), subtitle,
                  subtitle_font, (247, 202, 77, 255), max(2, width // 215), (7, 18, 28, 255))
    outlined_text(draw, (margin, height - brand_font.size - round(height * 0.035)), brand,
                  brand_font, (231, 240, 241, 255), 2, (7, 18, 28, 255))
    return canvas


def make_horizontal(source: Image.Image, size: tuple[int, int], title: str,
                    subtitle: str, brand: str) -> Image.Image:
    width, height = size
    canvas = source.resize(size, Image.Resampling.LANCZOS).convert("RGB")
    draw = ImageDraw.Draw(canvas, "RGBA")
    panel_top = round(height * 0.61)
    draw.rectangle((0, panel_top, width, height), fill=(7, 24, 41, 218))
    draw.rectangle((round(width * 0.039), panel_top + round(height * 0.028),
                    round(width * 0.172), panel_top + round(height * 0.041)),
                   fill=(241, 193, 76, 255))
    margin = max(45, round(width * 0.039))
    title_font = load_font(max(52, round(width * 0.056)))
    subtitle_font = load_font(max(30, round(width * 0.030)))
    brand_font = load_font(max(20, round(width * 0.019)))
    outlined_text(draw, (margin, panel_top + round(height * 0.070)), title,
                  title_font, (255, 255, 255, 255), max(3, width // 270), (7, 18, 28, 255))
    outlined_text(draw, (margin, panel_top + round(height * 0.215)), subtitle,
                  subtitle_font, (247, 202, 77, 255), max(2, width // 380), (7, 18, 28, 255))
    outlined_text(draw, (width - round(width * 0.19), height - brand_font.size - round(height * 0.032)), brand,
                  brand_font, (231, 240, 241, 255), 2, (7, 18, 28, 255))
    return canvas


def save_jpeg(image: Image.Image, output: Path, max_bytes: int, quality: int) -> int:
    output.parent.mkdir(parents=True, exist_ok=True)
    current_quality = max(45, min(95, quality))
    while True:
        image.save(output, format="JPEG", quality=current_quality, optimize=True, progressive=False)
        size = output.stat().st_size
        if size <= max_bytes or current_quality <= 45:
            return size
        current_quality -= 4


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--vertical-output", required=True, type=Path)
    parser.add_argument("--horizontal-output", required=True, type=Path)
    parser.add_argument("--title", default="技术替代的临界点")
    parser.add_argument("--subtitle", default="一过，替代突然加速")
    parser.add_argument("--brand", default="")
    parser.add_argument("--vertical-size", type=parse_size, default=(1080, 1440))
    parser.add_argument("--horizontal-size", type=parse_size, default=(1920, 1080))
    parser.add_argument("--subject-x", type=float, default=0.68,
                        help="Horizontal subject bias from 0 to 1 for portrait cropping.")
    parser.add_argument("--max-bytes", type=int, default=500_000)
    parser.add_argument("--quality", type=int, default=88)
    args = parser.parse_args(argv)
    if not 0 <= args.subject_x <= 1:
        parser.error("--subject-x must be between 0 and 1")
    if args.max_bytes < 10_000:
        parser.error("--max-bytes is too small")
    source = Image.open(args.input).convert("RGB")
    vertical = make_vertical(source, args.vertical_size, args.title, args.subtitle, args.brand, args.subject_x)
    horizontal = make_horizontal(source, args.horizontal_size, args.title, args.subtitle, args.brand)
    vertical_size = save_jpeg(vertical, args.vertical_output, args.max_bytes, args.quality)
    horizontal_size = save_jpeg(horizontal, args.horizontal_output, args.max_bytes, args.quality)
    print(f"vertical={args.vertical_output} size={args.vertical_size[0]}x{args.vertical_size[1]} bytes={vertical_size}")
    print(f"horizontal={args.horizontal_output} size={args.horizontal_size[0]}x{args.horizontal_size[1]} bytes={horizontal_size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
