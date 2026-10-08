from __future__ import annotations

from datetime import date, datetime, timezone


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def utc_now_iso() -> str:
    return utc_now().isoformat()


def local_now() -> datetime:
    return utc_now().astimezone()


def local_day() -> date:
    return local_now().date()


def local_day_iso() -> str:
    return local_day().isoformat()


def local_day_from_iso(value: str) -> date:
    dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if dt.tzinfo is None:
        # Legacy SQLite datetime('now') values were UTC but had no offset.
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone().date()
