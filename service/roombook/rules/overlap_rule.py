# RQ-BKG-003, DEC-BKG-002 (ADR-BKG-001)
"""Rule that refuses a request overlapping a Confirmed reservation of the same room (RQ-BKG-003)."""

from __future__ import annotations

from collections.abc import Sequence

from roombook.domain import Reservation, ReservationRequest, Room
from roombook.errors import ReservationConflict

RULE_ORDER = 30


class OverlapRule:
    """Rejects an interval that overlaps an existing reservation (RQ-BKG-003)."""

    def check(self, room: Room, request: ReservationRequest, existing: Sequence[Reservation]) -> None:
        """Raise ReservationConflict naming the first overlapping reservation (RQ-BKG-003)."""
        for reservation in existing:
            if reservation.overlaps(request.start, request.end):
                raise ReservationConflict(reservation.id)


RULE = OverlapRule()
