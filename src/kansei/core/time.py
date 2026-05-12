from __future__ import annotations

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

DEFAULT_TIMEZONE = "Asia/Tokyo"


def now_iso(timezone: str = DEFAULT_TIMEZONE) -> str:
    return datetime.now(_zone(timezone)).isoformat(timespec="seconds")


def today(timezone: str = DEFAULT_TIMEZONE) -> str:
    return datetime.now(_zone(timezone)).date().isoformat()


def _zone(name: str) -> ZoneInfo | timezone:
    try:
        return ZoneInfo(name)
    except ZoneInfoNotFoundError:
        if name == DEFAULT_TIMEZONE:
            return timezone(timedelta(hours=9), DEFAULT_TIMEZONE)
        raise
