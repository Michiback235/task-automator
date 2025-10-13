from __future__ import annotations

import csv
from pathlib import Path

from taskz.expenses.models import query_expenses


def export_csv(
    path: Path,
    since: str | None = None,
    until: str | None = None,
    category: str | None = None,
) -> int:
    rows = query_expenses(since=since, until=until, category=category)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "id",
                "date",
                "merchant",
                "category",
                "description",
                "amount_gross",
                "currency",
            ]
        )
        for r in rows:
            writer.writerow(
                [
                    r["id"],
                    r["date"],
                    r["merchant"],
                    r["category"],
                    r["description"],
                    r["amount_gross"],
                    r["currency"],
                ]
            )
    return len(rows)