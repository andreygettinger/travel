import json
from pathlib import Path

photos_dir = Path("photos")
output_dir = Path("galleries")
output_dir.mkdir(exist_ok=True)

extensions = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"}

for country in photos_dir.iterdir():
    if not country.is_dir():
        continue

    images = sorted(
        f"../photos/{country.name}/{file.name}"
        for file in country.iterdir()
        if file.is_file() and file.suffix.lower() in extensions
    )

    output = output_dir / f"{country.name}.json"
    output.write_text(
        json.dumps(images, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
