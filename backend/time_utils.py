from __future__ import annotations
from datetime import date, datetime, timezone


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def utc_now_iso() -> str:
    return utc_now().isoformat()


def local_day() -> date:
    """Calendar day in the computer's configured local timezone."""
    return datetime.now().astimezone().date()


def local_day_iso() -> str:
    return local_day().isoformat()


def local_day_from_timestamp(value: str) -> str:
    """Convert a stored UTC/offset ISO timestamp into the local calendar day."""
    parsed=datetime.fromisoformat(str(value).replace("Z","+00:00"))
    if parsed.tzinfo is None:
        parsed=parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone().date().isoformat()
