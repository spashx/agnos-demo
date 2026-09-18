# RQ-BKG-005, DEC-BKG-001 (ADR-BKG-001)
"""Clock adapter reading the system time in UTC (RQ-BKG-005)."""

from __future__ import annotations

from datetime import datetime, timezone

from roombook.ports import Clock


class SystemClock(Clock):
    """Current time of the system, in UTC (RQ-BKG-005)."""

    def now(self) -> datetime:
        """Return the current UTC time (RQ-BKG-005)."""
        return datetime.now(timezone.utc)
