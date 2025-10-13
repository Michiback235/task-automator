from __future__ import annotations

import sqlite3
from taskz.db.connection import connect

def monthly_summary(since: str, until: str) -> list[sqlite3.Row]:
    conn = connect()
    return conn.execute(
        """
        SELECT substr(date,1,7) AS month, category, SUM(amount_gross) AS total
        FROM expense
        WHERE date BETWEEN ? AND ?
        GROUP BY month, category
        ORDER BY month ASC, total DESC
        """,
        (since, until),
    ).fetchall()

def merchant_summary(since: str, until: str) -> list[sqlite3.Row]:
    conn = connect()
    return conn.execute(
        """
        SELECT merchant, SUM(amount_gross) AS total
        FROM expense
        WHERE date BETWEEN ? AND ?
        GROUP BY merchant
        ORDER BY total DESC
        """,
        (since, until),
    ).fetchall()
