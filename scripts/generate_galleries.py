#!/usr/bin/env python3
"""Generate gallery JSON files; optionally convert HEIC/HEIF for browser compatibility."""
import argparse
import json
from pathlib import Path

WEB_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"}
HEIC_EXTENSIONS = {".heic", ".heif"}


def compress_photos(root: Path, max_dimension: int = 2560, quality: int = 85) -> None:
    """Color-manage and optimize only the deployment copies in _site/photos."""
    import io
    import os
    import tempfile
    from PIL import Image, ImageCms, ImageOps
    from pillow_heif import register_heif_opener

    register_heif_opener()
    photo_root = root / "photos"
    if not photo_root.exists():
        return

    srgb = ImageCms.createProfile("sRGB")
    srgb_icc = ImageCms.ImageCmsProfile(srgb).tobytes()

    def to_srgb(image, icc_bytes):
        """Convert embedded profiles to sRGB rather than stripping their colors."""
        if not icc_bytes:
            # With no embedded profile, standard web behavior assumes sRGB.
            return image.convert("RGBA" if "A" in image.getbands() else "RGB")
        source_profile = ImageCms.ImageCmsProfile(io.BytesIO(icc_bytes))
        if "A" in image.getbands():
            alpha = image.getchannel("A")
            rgb = ImageCms.profileToProfile(image.convert("RGB"), source_profile, srgb,
                                            outputMode="RGB", renderingIntent=0)
            rgb.putalpha(alpha)
            return rgb
        return ImageCms.profileToProfile(image.convert("RGB"), source_profile, srgb,
                                         outputMode="RGB", renderingIntent=0)

    for source in sorted(photo_root.rglob("*")):
        if not source.is_file() or source.suffix.lower() not in {
            ".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"
        }:
            continue
        ext = source.suffix.lower()
        tmp = None
        try:
            with Image.open(source) as original:
                icc_bytes = original.info.get("icc_profile")
                image = ImageOps.exif_transpose(original)
                image = to_srgb(image, icc_bytes)
                image.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)

                if ext in {".heic", ".heif"}:
                    target = source.with_suffix(".jpg")
                    if target.exists():
                        target = source.with_name(source.stem + "__converted_heic.jpg")
                    output_format = "JPEG"
                elif ext in {".jpg", ".jpeg"}:
                    target, output_format = source, "JPEG"
                elif ext == ".webp":
                    target, output_format = source, "WEBP"
                else:
                    target, output_format = source, "PNG"

                with tempfile.NamedTemporaryFile(suffix=target.suffix, dir=source.parent,
                                                 delete=False) as temp:
                    tmp = Path(temp.name)
                if output_format == "JPEG":
                    image.convert("RGB").save(tmp, "JPEG", quality=quality,
                                              optimize=True, progressive=True,
                                              icc_profile=srgb_icc)
                elif output_format == "WEBP":
                    image.save(tmp, "WEBP", quality=quality, method=6,
                               icc_profile=srgb_icc)
                else:
                    image.save(tmp, "PNG", optimize=True, icc_profile=srgb_icc)

                # Avoid replacing PNGs when lossless optimization increases size,
                # unless resized or a color-profile conversion was needed.
                if (ext == ".png" and tmp.stat().st_size >= source.stat().st_size
                        and max(image.size) == max(original.size) and not icc_bytes):
                    tmp.unlink()
                    tmp = None
                    continue
                os.replace(tmp, target)
                tmp = None
                if ext in {".heic", ".heif"}:
                    source.unlink()
                print("Color-managed and optimized:", target.relative_to(root))
        except Exception as exc:
            # Leave the original deployment image intact on any color conversion error.
            print(f"WARNING: Skipped {source}: {exc}")
        finally:
            if tmp is not None:
                tmp.unlink(missing_ok=True)


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
                    # Only reached when color-managed conversion failed; do not silently strip profiles.
                    print(f"WARNING: HEIC not published because color-managed conversion failed: {source}")
                    continue
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
