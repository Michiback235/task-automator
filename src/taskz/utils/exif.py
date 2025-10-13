from __future__ import annotations

from datetime import datetime
from pathlib import Path

try:
    from PIL import Image, ExifTags  # type: ignore
except Exception:  # pragma: no cover
    Image = None
    ExifTags = None

def exif_datetime_original(path: Path) -> datetime | None:
    if Image is None:
        return None
    try:
        with Image.open(path) as img:
            exif = img.getexif()
            if not exif:
                return None
            key = None
            for k, v in ExifTags.TAGS.items():
                if v == "DateTimeOriginal":
                    key = k
                    break
            if key is None or key not in exif:
                return None
            value = exif.get(key)
            return datetime.strptime(str(value), "%Y:%m:%d %H:%M:%S")
    except Exception:
        return None