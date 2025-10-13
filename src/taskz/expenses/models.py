from __future__ import annotations

import sqlite3
from typing import Iterable

from taskz.db.connection import connect
from taskz.utils.currency import to_gross

def add_expense(
    date: str,
    merchant: str,
    amount: float,
    currency: str,
    category: str | None = None,
    description: str | None = None,
    tax: float | None = None,
    tags_csv: str | None = None,
) -> int:
    conn = connect()
    gross = to_gross(amount, tax)
    with conn:
        cur = conn.execute(
            """
            INSERT INTO expense(date, merchant, category, description, amount_net, tax, amount_gross, currency, tags_csv, source)
            VALUES (?,?,?,?,?,?,?,?,?,'manual')
            """,
            (date, merchant, category, description, amount, tax, gross, currency, tags_csv),
        )
        return int(cur.lastrowid)

def add_rule(target_field: str, pattern: str, value: str, priority: int = 100, enabled: bool = True):
    conn = connect()
    with conn:
        conn.execute(
            "INSERT INTO rule(target_field, pattern, action, value, priority, enabled) VALUES (?,?,?,?,?,?)",
            (target_field, pattern, "set", value, priority, 1 if enabled else 0),
        )

def list_rules() -> list[sqlite3.Row]:
    return connect().execute("SELECT * FROM rule ORDER BY enabled DESC, priority ASC").fetchall()

def apply_rules() -> int:
    conn = connect()
    rules = list_rules()
    updated = 0
    for r in rules:
        if not r["enabled"]:
            continue
        field = r["target_field"]
        pat = r["pattern"]
        value = r["value"]
        # apply to merchant or description; simple LIKE for MVP
        with conn:
            if field == "category":
                cur = conn.execute(
                    """
                    UPDATE expense SET category=?
                    WHERE (merchant LIKE '%'||?||'%' OR description LIKE '%'||?||'%')
                    """,
                    (value, pat, pat),
                )
                updated += cur.rowcount or 0
    return updated

def query_expenses(since: str | None = None, until: str | None = None, category: str | None = None):
    conn = connect()
    sql = "SELECT * FROM expense WHERE 1=1"
    args: list[str] = []
    if since:
        sql += " AND date>=?"
        args.append(since)
    if until:
        sql += " AND date<=?"
        args.append(until)
    if category:
        sql += " AND category=?"
        args.append(category)
    sql += " ORDER BY date ASC, id ASC"
    return conn.execute(sql, args).fetchall()
