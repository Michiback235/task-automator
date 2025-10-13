from __future__ import annotations

import logging
import os
import re
import shutil
import uuid
from collections.abc import Iterable
from pathlib import Path

from taskz.db.connection import connect
from taskz.files.hashing import file_hash
from taskz.files.preview import PreviewItem
from taskz.files.undo import record_rename
from taskz.utils.dates import localize
from taskz.utils.paths import iter_files, split_name_ext

log = logging.getLogger(__name__)

TOKEN_RE = re.compile(r"\{([a-zA-Z_:%.0-9-]+)\}")


def _format_token(path: Path, token: str, timezone: str, stat) -> str:
    if token == "name":
        return split_name_ext(path)[0]
    if token == "ext":
        return split_name_ext(path)[1]
    if token == "parent":
        return path.parent.name
    if token.startswith("created"):
        fmt = "%Y-%m-%d"
        if ":" in token:
            fmt = token.split(":", 1)[1]
        dt = localize(stat.st_ctime, timezone)
        return dt.strftime(fmt)
    if token.startswith("modified"):
        fmt = "%Y-%m-%d"
        if ":" in token:
            fmt = token.split(":", 1)[1]
        dt = localize(stat.st_mtime, timezone)
        return dt.strftime(fmt)
    if token == "counter":
        return "{__COUNTER__}"
    if token.startswith("exif:"):
        # EXIF optional; token evaluates empty when unavailable
        return ""
    if token == "hash8":
        try:
            return file_hash(path)[:8]
        except Exception:
            return "00000000"
    return ""


def render_pattern(path: Path, pattern: str, timezone: str) -> str:
    """Render a filename pattern by substituting {tokens} safely."""
    stat = path.stat()

    def repl(match: re.Match[str]) -> str:
        token = match.group(1)
        return _format_token(path, token, timezone, stat)

    out = TOKEN_RE.sub(repl, pattern)
    # Normalize accidental dots after substitution
    out = out.replace("..", ".").strip(".")
    return out


def preview(
    src: Path,
    dest: Path,
    pattern: str,
    recursive: bool,
    timezone: str,
    lowercase: bool,
    dedupe: bool,
) -> list[PreviewItem]:
    files = list(iter_files(src, recursive=recursive))
    results: list[PreviewItem] = []
    counters: dict[str, int] = {}
    seen: set[Path] = set()
    for p in files:
        rel = p.relative_to(src)
        target_name = render_pattern(p, pattern, timezone)
        if "{__COUNTER__}" in target_name:
            key = target_name
            counters[key] = counters.get(key, 0) + 1
            target_name = target_name.replace("{__COUNTER__}", str(counters[key]))
        if lowercase:
            target_name = target_name.lower()
        target = dest / rel.parent / target_name
        if dedupe:
            base, ext = os.path.splitext(target.name)
            t = target
            k = 1
            while t.exists() or t in seen:
                t = t.with_name(f"{base}-{k}{ext}")
                k += 1
            target = t
        conflict = target.exists()
        results.append(PreviewItem(src=p, dest=target, conflict=conflict))
        seen.add(target)
    return results


def execute(previews: Iterable[PreviewItem], yes: bool, batch_id: str | None = None) -> int:
    n = 0
    conn = connect()
    if batch_id is None:
        batch_id = uuid.uuid4().hex[:12]
    for item in previews:
        if not yes:
            log.info("DRY-RUN %s -> %s", item.src, item.dest)
            continue
        item.dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(item.src), str(item.dest))
        try:
            h = file_hash(item.dest)
        except Exception:
            h = None
        record_rename(conn, batch_id, str(item.src), str(item.dest), h)
        n += 1
    conn.commit()
    return n