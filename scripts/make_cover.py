#!/usr/bin/env python3
"""Create readable vertical and horizontal covers from a still frame.

The script is deliberately offline: it never calls a model or a network API.
Chinese typography is rendered locally so small platform thumbnails keep the
exact title supplied by the user.
"""

from __future__ import annotations

import argparse
import os
import sys
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


def wrap_lines(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont,
               max_width: int) -> list[str]:
    """Greedily wrap Chinese (or space-separated Latin) text to a pixel width."""
    if not text:
        return []
    latin_words = " " in text and not any("\u4e00" <= c <= "\u9fff" for c in text)
    chunks = text.split() if latin_words else list(text)
    lines: list[str] = []
    current = ""
    for chunk in chunks:
        candidate = (current + " " + chunk).strip() if latin_words else current + chunk
        box = draw.textbbox((0, 0), candidate, font=font)
        if current and box[2] - box[0] > max_width:
            lines.append(current)
            current = chunk
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def fit_block(draw: ImageDraw.ImageDraw, text: str, max_width: int, initial_size: int,
              min_size: int, max_lines: int, stroke: int) -> tuple[ImageFont.FreeTypeFont, list[str]]:
    """Find the largest font that keeps a text block within its line budget."""
    for size in range(initial_size, min_size - 1, -2):
        f = load_font(size)
        lines = wrap_lines(draw, text, f, max_width - stroke * 2)
        if len(lines) <= max_lines:
            return f, lines
    # At an extreme length, keep the first lines and mark the omission instead of
    # allowing text to run outside a thumbnail.
    f = load_font(min_size)
    lines = wrap_lines(draw, text, f, max_width - stroke * 2)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        last = lines[-1]
        while last and draw.textbbox((0, 0), last + "…", font=f)[2] > max_width - stroke * 2:
            last = last[:-1]
        lines[-1] = (last + "…") if last else "…"
    return f, lines


def draw_block(draw: ImageDraw.ImageDraw, xy: tuple[int, int], lines: list[str],
               f: ImageFont.FreeTypeFont, fill: tuple[int, ...], stroke: int,
               stroke_fill: tuple[int, ...], gap: int = 6) -> int:
    """Draw lines and return the block height."""
    x, y = xy
    line_height = f.size + gap
    for index, line in enumerate(lines):
        outlined_text(draw, (x, y + index * line_height), line, f, fill, stroke, stroke_fill)
    return max(0, len(lines) * line_height - gap)


def make_vertical(source: Image.Image, size: tuple[int, int], title: str,
                  subtitle: str, brand: str, subject_x: float, eyebrow: str = "") -> Image.Image:
    width, height = size
    panel_top = round(height * 0.62)
    image_height = round(height * 0.70)
    background = fit_crop(source, (width, height), subject_x).filter(ImageFilter.GaussianBlur(18))
    foreground = fit_crop(source, (width, image_height), subject_x)
    canvas = background.convert("RGB")
    canvas.paste(foreground, (0, 0))
    draw = ImageDraw.Draw(canvas, "RGBA")
    draw.rectangle((0, panel_top, width, height), fill=(8, 25, 43, 255))
    draw.rectangle((0, panel_top, width, panel_top + max(4, height // 180)), fill=(241, 193, 76, 255))

    margin = max(32, round(width * 0.065))
    eyebrow_font = load_font(max(24, round(width * 0.039)))
    brand_font = load_font(max(22, round(width * 0.032)))
    y = panel_top + round(height * 0.047)
    outlined_text(draw, (margin, y), eyebrow, eyebrow_font, (247, 207, 103, 255), 2, (7, 18, 28, 255))
    title_stroke = max(3, width // 155)
    subtitle_stroke = max(2, width // 215)
    title_font, title_lines = fit_block(draw, title, width - margin * 2, max(44, round(width * 0.090)),
                                         max(30, round(width * 0.050)), 2, title_stroke)
    title_y = y + eyebrow_font.size + round(height * 0.012)
    title_height = draw_block(draw, (margin, title_y), title_lines, title_font,
                              (255, 255, 255, 255), title_stroke, (7, 18, 28, 255), gap=3)
    subtitle_font, subtitle_lines = fit_block(draw, subtitle, width - margin * 2,
                                               max(30, round(width * 0.054)), max(24, round(width * 0.032)),
                                               2, subtitle_stroke)
    draw_block(draw, (margin, title_y + title_height + round(height * 0.035)), subtitle_lines,
               subtitle_font, (247, 202, 77, 255), subtitle_stroke, (7, 18, 28, 255), gap=3)
    outlined_text(draw, (margin, height - brand_font.size - round(height * 0.035)), brand,
                  brand_font, (231, 240, 241, 255), 2, (7, 18, 28, 255))
    return canvas


def make_horizontal(source: Image.Image, size: tuple[int, int], title: str,
                    subtitle: str, brand: str) -> Image.Image:
    width, height = size
    canvas = source.resize(size, Image.Resampling.LANCZOS).convert("RGB")
    draw = ImageDraw.Draw(canvas, "RGBA")
    panel_top = round(height * 0.61)
    draw.rectangle((0, panel_top, width, height), fill=(7, 24, 41, 255))
    draw.rectangle((round(width * 0.039), panel_top + round(height * 0.028),
                    round(width * 0.172), panel_top + round(height * 0.041)),
                   fill=(241, 193, 76, 255))
    margin = max(45, round(width * 0.039))
    brand_font = load_font(max(20, round(width * 0.019)))
    title_stroke = max(3, width // 270)
    subtitle_stroke = max(2, width // 380)
    title_font, title_lines = fit_block(draw, title, round(width * 0.78), max(52, round(width * 0.056)),
                                        max(32, round(width * 0.032)), 2, title_stroke)
    title_y = panel_top + round(height * 0.070)
    title_height = draw_block(draw, (margin, title_y), title_lines, title_font,
                              (255, 255, 255, 255), title_stroke, (7, 18, 28, 255), gap=3)
    subtitle_font, subtitle_lines = fit_block(draw, subtitle, round(width * 0.78),
                                               max(30, round(width * 0.030)), max(22, round(width * 0.022)),
                                               2, subtitle_stroke)
    draw_block(draw, (margin, title_y + title_height + round(height * 0.035)), subtitle_lines,
               subtitle_font, (247, 202, 77, 255), subtitle_stroke, (7, 18, 28, 255), gap=3)
    outlined_text(draw, (width - round(width * 0.19), height - brand_font.size - round(height * 0.032)), brand,
                  brand_font, (231, 240, 241, 255), 2, (7, 18, 28, 255))
    return canvas


def save_jpeg(image: Image.Image, output: Path, max_bytes: int, quality: int) -> int:
    output.parent.mkdir(parents=True, exist_ok=True)
    current_quality = max(45, min(95, quality))
    while True:
        image.save(output, format="JPEG", quality=current_quality, optimize=True, progressive=False)
        size = output.stat().st_size
        if size <= max_bytes:
            return size
        if current_quality <= 45:
            raise ValueError(f"Cover exceeds {max_bytes} bytes; reduce dimensions or simplify the image")
        current_quality -= 4


def main(argv: Iterable[str] | None = None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--vertical-output", required=True, type=Path)
    parser.add_argument("--horizontal-output", required=True, type=Path)
    parser.add_argument("--title", required=True)
    parser.add_argument("--subtitle", default="")
    parser.add_argument("--eyebrow", default="", help="Optional topic label above the portrait title.")
    parser.add_argument("--vertical-crop-bottom", type=int, default=0,
                        help="Pixels removed from the source bottom before portrait crop (e.g. subtitles).")
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
    if not 0 <= args.vertical_crop_bottom < source.height:
        parser.error("--vertical-crop-bottom must be nonnegative and smaller than source height")
    portrait_source = source.crop((0, 0, source.width, source.height - args.vertical_crop_bottom))
    vertical = make_vertical(portrait_source, args.vertical_size, args.title, args.subtitle, args.brand, args.subject_x, args.eyebrow)
    horizontal = make_horizontal(source, args.horizontal_size, args.title, args.subtitle, args.brand)
    vertical_size = save_jpeg(vertical, args.vertical_output, args.max_bytes, args.quality)
    horizontal_size = save_jpeg(horizontal, args.horizontal_output, args.max_bytes, args.quality)
    print(f"vertical={args.vertical_output} size={args.vertical_size[0]}x{args.vertical_size[1]} bytes={vertical_size}")
    print(f"horizontal={args.horizontal_output} size={args.horizontal_size[0]}x{args.horizontal_size[1]} bytes={horizontal_size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
