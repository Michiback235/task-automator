from __future__ import annotations

from datetime import datetime
from pathlib import Path


def exif_datetime_original(path: Path) -> datetime | None:
    # Import lazily to keep Pillow optional and avoid import-order lint noise.
    try:
        from PIL import ExifTags, Image  # type: ignore
    except Exception:
        return None

    try:
        with Image.open(path) as img:
            exif = img.getexif()
            if not exif:
                return None
            # Find the tag for DateTimeOriginal
            key = None
            for k, v in ExifTags.TAGS.items():
                if v == "DateTimeOriginal":
                    key = k
                    break
            if key is None or key not in exif:
                return None
            value = exif.get(key)
            # format "YYYY:MM:DD HH:MM:SS"
            return datetime.strptime(str(value), "%Y:%m:%d %H:%M:%S")
    except Exception:
        return None
