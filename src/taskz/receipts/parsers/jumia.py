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
    m = re.search(r"\bTotal\b.*?([A-Z]{3})\s?([0-9]+(?:\.[0-9]{1,2})?)", txt, re.IGNORECASE)
    if m:
        cur = m.group(1)
        total = float(m.group(2))
    ref = None
    om = re.search(r"Order\s*#\s*([A-Z0-9-]+)", txt, re.IGNORECASE)
    if om:
        ref = om.group(1)
    dt = datetime.now(UTC).isoformat()
    return NormalizedReceipt(
        merchant="Jumia",
        datetime_utc=dt,
        currency=cur,
        total_gross=total,
        tax=None,
        reference=ref,
        items=[],
    )
