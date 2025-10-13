from __future__ import annotations

import re
from datetime import datetime, timezone
from bs4 import BeautifulSoup

from taskz.receipts.normalize import NormalizedReceipt, clean_text

def parse(html: str) -> NormalizedReceipt:
    soup = BeautifulSoup(html, "lxml")
    txt = clean_text(soup.get_text(" "))
    # crude patterns for MVP
    # currency & total like "KES 450.00" or "Total: KES450"
    cur = "KES"
    m = re.search(r"\b([A-Z]{3})\s?([0-9]+(?:\.[0-9]{1,2})?)", txt)
    total = 0.0
    if m:
        cur = m.group(1)
        total = float(m.group(2))
    # date like "Oct 12, 2025 21:33"
    dt = datetime.now(timezone.utc)
    dm = re.search(r"([A-Z][a-z]{2,}\s+\d{1,2},\s+\d{4}\s+\d{2}:\d{2})", txt)
    if dm:
        try:
            dt = datetime.strptime(dm.group(1), "%B %d, %Y %H:%M").astimezone(timezone.utc)
        except Exception:
            pass
    return NormalizedReceipt(
        merchant="Uber",
        datetime_utc=dt.isoformat(),
        currency=cur,
        total_gross=total,
        tax=None,
        reference=None,
        items=[],
    )
