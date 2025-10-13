from __future__ import annotations

from datetime import datetime, timezone
from dateutil import tz

def to_utc_iso(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat()

def now_iso() -> str:
    return to_utc_iso(datetime.now(timezone.utc))

def localize(ts: float, zone_name: str) -> datetime:
    zone = tz.gettz(zone_name)
    return datetime.fromtimestamp(ts, tz=zone)
