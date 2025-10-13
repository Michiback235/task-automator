from __future__ import annotations

import re
from datetime import UTC, datetime

from bs4 import BeautifulSoup

from taskz.receipts.normalize import NormalizedReceipt, clean_text


def parse(html: str) -> NormalizedReceipt:
    soup = BeautifulSoup(html, "lxml")
    txt = clean_text(soup.get_text(" "))
    cur = "KES"
    total = 0.0
    m = re.search(r"\b([A-Z]{3})\s?([0-9]+(?:\.[0-9]{1,2})?)", txt)
    if m:
        cur = m.group(1)
        total = float(m.group(2))
    dt = datetime.now(UTC)
    dm = re.search(r"([A-Z][a-z]{2,}\s+\d{1,2},\s+\d{4}\s+\d{2}:\d{2})", txt)
    if dm:
        try:
            dt = datetime.strptime(dm.group(1), "%B %d, %Y %H:%M").astimezone(UTC)
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
