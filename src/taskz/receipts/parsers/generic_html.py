from __future__ import annotations

import re
from datetime import datetime, timezone

from taskz.receipts.normalize import NormalizedReceipt, clean_text

CURRENCY_RE = re.compile(r"\b([A-Z]{3})\b")
AMOUNT_RE = re.compile(r"([0-9]+(?:\.[0-9]{1,2})?)")

def parse(html: str) -> NormalizedReceipt:
    text = clean_text(html)
    currency = CURRENCY_RE.search(text)
    amount = AMOUNT_RE.search(text)
    cur = currency.group(1) if currency else "KES"
    tot = float(amount.group(1)) if amount else 0.0
    now = datetime.now(timezone.utc).isoformat()
    return NormalizedReceipt(
        merchant="Unknown Merchant",
        datetime_utc=now,
        currency=cur,
        total_gross=tot,
        tax=None,
        reference=None,
        items=[],
    )