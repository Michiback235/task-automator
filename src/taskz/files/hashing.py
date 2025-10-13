from __future__ import annotations

import hashlib
from pathlib import Path


def file_hash(path: Path, algo: str = "sha256", chunk_size: int = 1 << 20) -> str:
    h = hashlib.new(algo)
    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()
