#!/usr/bin/env python3
"""Generate gallery JSON files; optionally convert HEIC/HEIF for browser compatibility."""
import argparse
import json
from pathlib import Path

WEB_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"}
HEIC_EXTENSIONS = {".heic", ".heif"}


def build(root: Path, convert_heic: bool) -> None:
    photos_root = root / "photos"
    galleries = root / "galleries"
    galleries.mkdir(parents=True, exist_ok=True)
    if convert_heic:
        from PIL import Image, ImageOps
        from pillow_heif import register_heif_opener
        register_heif_opener()

    slugs = {p.stem for p in (root / "countries").glob("*.html")}
    if photos_root.is_dir():
        slugs.update(p.name for p in photos_root.iterdir() if p.is_dir())
    for slug in sorted(slugs):
        folder = photos_root / slug
        found = []
        if folder.is_dir():
            for source in sorted(folder.rglob("*")):
                if not source.is_file():
                    continue
                ext = source.suffix.lower()
                if ext in WEB_EXTENSIONS:
                    found.append(source.relative_to(folder).as_posix())
                elif ext in HEIC_EXTENSIONS and convert_heic:
                    # Keep the original HEIC; publish a browser-friendly JPEG beside it.
                    dest = source.with_suffix(".jpg")
                    if dest.exists():
                        # Do not overwrite an existing JPEG with the same basename.
                        dest = source.with_name(source.stem + "__converted_heic.jpg")
                    if not dest.exists():
                        with Image.open(source) as original:
                            image = ImageOps.exif_transpose(original)
                            if image.mode not in ("RGB", "L"):
                                image = image.convert("RGB")
                            image.thumbnail((3000, 3000))
                            image.save(dest, "JPEG", quality=87, optimize=True)
                    found.append(dest.relative_to(folder).as_posix())
        (galleries / (slug + ".json")).write_text(
            json.dumps(found, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"{slug}: {len(found)} web photos")
    for old in galleries.glob("*.json"):
        if old.stem not in slugs:
            old.unlink()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--convert-heic", action="store_true")
    args = parser.parse_args()
    build(args.root.resolve(), args.convert_heic)
