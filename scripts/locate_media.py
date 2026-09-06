#!/usr/bin/env python3
"""Locate an Obsidian article's matching project folder and exp_final video.

This helper is read-only and prints JSON. It intentionally uses the stable
numeric project prefix because article and media dates often differ.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v"}
PROJECT_RE = re.compile(r"^(?P<id>\d{1,8})(?:[_ -]|$)")


def project_id(article: Path) -> str | None:
    match = PROJECT_RE.match(article.stem)
    return match.group("id").zfill(3) if match else None


def title_tokens(article: Path, number: str | None) -> set[str]:
    stem = article.stem
    if number:
        stem = stem[len(number):]
    tokens = {token.lower() for token in re.split(r"[_\-\s]+", stem) if len(token) > 1}
    return tokens


def score_folder(folder: Path, number: str | None, tokens: set[str]) -> int:
    score = 0
    if number and folder.name.startswith(number):
        score += 100
    lower = folder.name.lower()
    score += sum(5 for token in tokens if token in lower)
    return score


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--article", required=True, type=Path)
    parser.add_argument("--media-root", required=True, type=Path)
    args = parser.parse_args()
    article = args.article.expanduser().resolve()
    media_root = args.media_root.expanduser().resolve()
    number = project_id(article)
    tokens = title_tokens(article, number)
    folders = [p for p in media_root.rglob("*") if p.is_dir() and (not number or p.name.startswith(number))]
    folders.sort(key=lambda p: (-score_folder(p, number, tokens), str(p).lower()))
    candidates = []
    for folder in folders:
        videos = sorted(
            (p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in VIDEO_EXTENSIONS
             and "exp_final" in p.stem.lower()),
            key=lambda p: p.name.lower(),
        )
        for video in videos:
            candidates.append({
                "project_id": number,
                "folder": str(folder),
                "video": str(video),
                "score": score_folder(folder, number, tokens),
            })
    selected = candidates[0] if len(candidates) == 1 else None
    result = {
        "article": str(article),
        "media_root": str(media_root),
        "project_id": number,
        "candidates": candidates,
        "selected": selected,
        "needs_user_choice": len(candidates) > 1,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
