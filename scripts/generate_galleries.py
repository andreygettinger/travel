#!/usr/bin/env python3
"""Generate gallery JSON files; optionally convert HEIC/HEIF for browser compatibility."""
import argparse
import json
from pathlib import Path

WEB_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"}
HEIC_EXTENSIONS = {".heic", ".heif"}


def compress_photos(root: Path, max_dimension: int = 2560, quality: int = 85) -> None:
    """Optimize deployment copies in _site, never repository originals."""
    from PIL import Image, ImageOps
    from pillow_heif import register_heif_opener
    register_heif_opener()

    photo_root = root / "photos"
    if not photo_root.exists():
        return
    for source in sorted(photo_root.rglob("*")):
        if not source.is_file():
            continue
        ext = source.suffix.lower()
        if ext not in {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"}:
            continue
        try:
            with Image.open(source) as original:
                img = ImageOps.exif_transpose(original)
                img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
                if ext in {".heic", ".heif"}:
                    target = source.with_suffix(".jpg")
                    if target.exists():
                        target = source.with_name(source.stem + "__converted_heic.jpg")
                    img.convert("RGB").save(target, "JPEG", quality=quality, optimize=True, progressive=True)
                    source.unlink()  # HEIC source not needed in published site
                elif ext in {".jpg", ".jpeg"}:
                    import os
                    import tempfile
                    with tempfile.NamedTemporaryFile(suffix=".jpg", dir=source.parent, delete=False) as temp:
                        tmp = Path(temp.name)
                    try:
                        img.convert("RGB").save(tmp, "JPEG", quality=quality, optimize=True, progressive=True)
                        os.replace(tmp, source)
                    finally:
                        tmp.unlink(missing_ok=True)
                elif ext == ".png":
                    # Keep PNG filenames (and transparency) so existing HTML links still work.
                    import os
                    import tempfile
                    with tempfile.NamedTemporaryFile(suffix=".png", dir=source.parent, delete=False) as temp:
                        tmp = Path(temp.name)
                    try:
                        img.save(tmp, "PNG", optimize=True)
                        if tmp.stat().st_size < source.stat().st_size:
                            os.replace(tmp, source)
                    finally:
                        tmp.unlink(missing_ok=True)
                elif ext == ".webp":
                    import os
                    import tempfile
                    with tempfile.NamedTemporaryFile(suffix=".webp", dir=source.parent, delete=False) as temp:
                        tmp = Path(temp.name)
                    try:
                        img.save(tmp, "WEBP", quality=quality, method=6)
                        os.replace(tmp, source)
                    finally:
                        tmp.unlink(missing_ok=True)
                print("Optimized:", source.relative_to(root))
        except Exception as exc:
            print(f"WARNING: Could not optimize {source}: {exc}")


def build(root: Path, convert_heic: bool) -> None:
    photos_root = root / "photos"
    galleries = root / "galleries"
    galleries.mkdir(parents=True, exist_ok=True)
    if convert_heic:
        compress_photos(root)

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
                    # Fallback conversion for HEIC if not already optimized.
                    dest = source.with_suffix(".jpg")
                    if dest.exists():
                        # Do not overwrite an existing JPEG with the same basename.
                        dest = source.with_name(source.stem + "__converted_heic.jpg")
                    if not dest.exists():
                        from PIL import Image, ImageOps
                        with Image.open(source) as original:
                            image = ImageOps.exif_transpose(original)
                            if image.mode not in ("RGB", "L"):
                                image = image.convert("RGB")
                            image.thumbnail((3000, 3000))
                            image.save(dest, "JPEG", quality=85, optimize=True)
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
