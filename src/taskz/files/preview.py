from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class PreviewItem:
    src: Path
    dest: Path
    conflict: bool