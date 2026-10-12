#!/usr/bin/env python3
"""Build galleries/*.json from the images in photos/<country>/ folders."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PHOTOS = ROOT / "photos"
GALLERIES = ROOT / "galleries"
EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"}
GALLERIES.mkdir(exist_ok=True)

country_slugs = {p.stem for p in (ROOT / "countries").glob("*.html")}
for folder in PHOTOS.iterdir():
    if folder.is_dir():
        country_slugs.add(folder.name)

for slug in sorted(country_slugs):
    folder = PHOTOS / slug
    photos = sorted(
        file.relative_to(folder).as_posix()
        for file in folder.rglob("*")
        if file.is_file() and file.suffix.lower() in EXTENSIONS
    ) if folder.is_dir() else []
    (GALLERIES / f"{slug}.json").write_text(
        json.dumps(photos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"{slug}: {len(photos)} photo(s)")

for old in GALLERIES.glob("*.json"):
    if old.stem not in country_slugs:
        old.unlink()
