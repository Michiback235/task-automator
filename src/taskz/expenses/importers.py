from __future__ import annotations

import csv
from pathlib import Path
from taskz.expenses.models import add_expense

def import_csv(path: Path, currency_default: str = "KES") -> int:
    n = 0
    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            add_expense(
                date=row.get("date", ""),
                merchant=row.get("merchant", "Unknown"),
                amount=float(row.get("amount", "0") or 0),
                currency=row.get("currency", currency_default),
                category=row.get("category") or None,
                description=row.get("description") or None,
                tax=float(row.get("tax", "0") or 0),
                tags_csv=row.get("tags") or None,
            )
            n += 1
    return n
