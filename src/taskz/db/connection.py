from __future__ import annotations

import sqlite3
from collections.abc import Iterable
from pathlib import Path

from taskz.config import load_config
from taskz.utils.paths import ensure_parent_dir


def db_path() -> Path:
    cfg = load_config()
    path = Path(cfg["database"]["path"]).expanduser()
    ensure_parent_dir(path)
    return path


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def apply_migrations(conn: sqlite3.Connection, sql_files: Iterable[Path]) -> None:
    with conn:
        conn.execute("CREATE TABLE IF NOT EXISTS _migrations (name TEXT PRIMARY KEY)")
        for path in sql_files:
            name = path.name
            row = conn.execute("SELECT 1 FROM _migrations WHERE name=?", (name,)).fetchone()
            if row:
                continue
            conn.executescript(path.read_text())
            conn.execute("INSERT INTO _migrations(name) VALUES (?)", (name,))