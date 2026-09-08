# RQ-BKG-004, DEC-BKG-002 (ADR-BKG-001)
"""Rule that refuses more attendees than the room capacity (RQ-BKG-004)."""

from __future__ import annotations

from collections.abc import Sequence

from roombook.domain import Reservation, ReservationRequest, Room
from roombook.errors import CapacityExceeded

RULE_ORDER = 20


class CapacityRule:
    """Rejects a request whose attendee count exceeds the room capacity (RQ-BKG-004)."""

    def check(self, room: Room, request: ReservationRequest, existing: Sequence[Reservation]) -> None:
        """Raise CapacityExceeded when the attendees do not fit (RQ-BKG-004)."""
        if request.attendees > room.capacity:
            raise CapacityExceeded()


RULE = CapacityRule()
