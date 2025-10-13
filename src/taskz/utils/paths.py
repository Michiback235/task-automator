from __future__ import annotations

from pathlib import Path


def ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def iter_files(src: Path, recursive: bool = True):
    if recursive:
        yield from (p for p in src.rglob("*") if p.is_file())
    else:
        yield from (p for p in src.iterdir() if p.is_file())


def split_name_ext(path: Path) -> tuple[str, str]:
    name = path.name
    if "." in name:
        stem, ext = name.rsplit(".", 1)
        return stem, ext
    return name, ""


def safe_rel(root: Path, p: Path) -> str:
    try:
        return str(p.relative_to(root))
    except Exception:
        return str(p)
