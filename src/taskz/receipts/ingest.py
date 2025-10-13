from __future__ import annotations

import glob
import logging
import sqlite3
from pathlib import Path

from taskz.db.connection import connect
from taskz.receipts.normalize import NormalizedReceipt, content_hash, to_json
from taskz.receipts.parsers import detector, generic_html, jumia, uber

log = logging.getLogger(__name__)


def _parser_for(vendor: str):
    if vendor == "uber":
        return uber.parse
    if vendor == "jumia":
        return jumia.parse
    return generic_html.parse


def _detect_vendor(raw: str, forced: str | None) -> str:
    if forced and forced != "auto":
        return forced
    v = detector.detect_vendor(raw) or "generic_html"
    return v


def _insert_receipt(
    conn: sqlite3.Connection,
    src_type: str,
    src_path: str,
    raw: str,
    vendor: str,
    normalized: NormalizedReceipt,
) -> int:
    h = content_hash(raw)
    ex = conn.execute("SELECT id FROM receipt WHERE content_hash=?", (h,)).fetchone()
    if ex:
        return int(ex["id"])
    with conn:
        cur = conn.execute(
            (
                "INSERT INTO receipt("
                "source_type, source_path_or_url, content_hash, raw_text, parsed_ok, "
                "parsed_at, vendor, meta_json"
                ") VALUES (?,?,?,?,1,datetime('now'),?,?)"
            ),
            (src_type, src_path, h, raw, vendor, to_json(normalized)),
        )
        rid = int(cur.lastrowid)
        conn.execute(
            (
                "INSERT INTO expense("
                "date, merchant, category, description, amount_net, tax, "
                "amount_gross, currency, payment_method, tags_csv, source, source_id, receipt_id"
                ") VALUES (date('now'), ?, NULL, ?, NULL, NULL, ?, ?, NULL, NULL, 'receipt', ?, ?)"
            ),
            (
                normalized.merchant,
                f"Imported from receipt {vendor}",
                normalized.total_gross,
                normalized.currency,
                h[:12],
                rid,
            ),
        )
    return rid


def scrape_from_path(base: Path, globs: list[str], vendor: str = "auto") -> int:
    conn = connect()
    count = 0
    matches: list[Path] = []
    for pattern in globs:
        matches.extend(Path(p) for p in glob.glob(str(base / pattern), recursive=True))
    for p in matches:
        raw = p.read_text(encoding="utf-8", errors="ignore")
        vd = _detect_vendor(raw, vendor)
        parser = _parser_for(vd)
        norm = parser(raw)
        _insert_receipt(conn, "file", str(p), raw, vd, norm)
        count += 1
    return count