# RQ-BKG-006, DEC-BKG-002 (ADR-BKG-001)
"""Rule that refuses reservations of a room flagged closed (RQ-BKG-006)."""

from __future__ import annotations

from collections.abc import Sequence

from roombook.domain import Reservation, ReservationRequest, Room
from roombook.errors import RoomClosed

RULE_ORDER = 10


class RoomOpenRule:
    """Rejects a request for a closed room (RQ-BKG-006)."""

    def check(self, room: Room, request: ReservationRequest, existing: Sequence[Reservation]) -> None:
        """Raise RoomClosed when the room is not open (RQ-BKG-006)."""
        if not room.open:
            raise RoomClosed()


RULE = RoomOpenRule()
