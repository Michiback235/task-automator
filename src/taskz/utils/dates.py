from __future__ import annotations

from datetime import UTC, datetime

from dateutil import tz


def to_utc_iso(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC).isoformat()


def now_iso() -> str:
    return to_utc_iso(datetime.now(UTC))


def localize(ts: float, zone_name: str) -> datetime:
    zone = tz.gettz(zone_name)
    return datetime.fromtimestamp(ts, tz=zone)
