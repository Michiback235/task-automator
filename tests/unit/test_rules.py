from __future__ import annotations

from taskz.db.connection import connect
from taskz.expenses.models import add_expense, add_rule, apply_rules


def test_rules_apply_to_merchant():
    add_expense("2025-10-12", "Uber", 450, "KES")
    add_rule("category", "uber", "Transport")
    updated = apply_rules()
    assert updated >= 1
    row = connect().execute("SELECT category FROM expense WHERE merchant='Uber'").fetchone()
    assert row["category"] == "Transport"
