from __future__ import annotations

import sqlite3

def record_rename(conn: sqlite3.Connection, batch_id: str, src: str, dest: str, file_hash: str | None):
    conn.execute(
        "INSERT INTO rename_op(batch_id, src_path, dest_path, file_hash) VALUES (?,?,?,?)",
        (batch_id, src, dest, file_hash),
    )

def undo_batch(conn: sqlite3.Connection, batch_id: str) -> int:
    rows = conn.execute(
        "SELECT id, src_path, dest_path, reverted FROM rename_op WHERE batch_id=? ORDER BY id DESC",
        (batch_id,),
    ).fetchall()
    count = 0
    for r in rows:
        if r["reverted"]:
            continue
        conn.execute("UPDATE rename_op SET reverted=1 WHERE id=?", (r["id"],))
        count += 1
    conn.commit()
    return count