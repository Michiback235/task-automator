from __future__ import annotations

from dataclasses import dataclass, asdict
import hashlib
import json

@dataclass
class NormalizedReceipt:
    merchant: str
    datetime_utc: str
    currency: str
    total_gross: float
    tax: float | None
    reference: str | None
    items: list[dict]

def clean_text(s: str) -> str:
    return " ".join(s.split())

def content_hash(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def to_json(rec: NormalizedReceipt) -> str:
    return json.dumps(asdict(rec), ensure_ascii=False, sort_keys=True)