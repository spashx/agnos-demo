# RQ-BKG-006, DEC-BKG-002 (ADR-BKG-001)
"""Unit tests of the closed-room rule."""

from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from roombook.domain import ReservationRequest, Room
from roombook.errors import ROOM_CLOSED, RoomClosed
from roombook.rules import room_open_rule

UTC = timezone.utc
BASE_TIME = datetime(2026, 1, 1, tzinfo=UTC)
ONE_HOUR = timedelta(hours=1)
ROOM_ID = "room-alpha"
ROOM_NAME = "Alpha"
ROOM_CAPACITY = 6
ORGANIZER = "alice@example.test"
ATTENDEES = 3
CLOSED_FLAG = False


def make_request() -> ReservationRequest:
    """Build a valid request for the test room (RQ-BKG-006)."""
    return ReservationRequest(
        room_id=ROOM_ID,
        organizer=ORGANIZER,
        start=BASE_TIME,
        end=BASE_TIME + ONE_HOUR,
        attendees=ATTENDEES,
    )


class RoomOpenRuleTest(unittest.TestCase):
    """Tests of RoomOpenRule (RQ-BKG-006)."""

    # RQ-BKG-006
    def test_given_room_flagged_closed_when_reservation_requested_then_room_closed_is_raised(self) -> None:
        # Given
        closed_room = Room(id=ROOM_ID, name=ROOM_NAME, capacity=ROOM_CAPACITY, open=CLOSED_FLAG)
        # When
        with self.assertRaises(RoomClosed) as context:
            room_open_rule.RULE.check(closed_room, make_request(), [])
        # Then
        self.assertEqual(context.exception.code, ROOM_CLOSED)

    # RQ-BKG-006
    def test_given_open_room_when_reservation_requested_then_no_error(self) -> None:
        # Given
        open_room = Room(id=ROOM_ID, name=ROOM_NAME, capacity=ROOM_CAPACITY)
        # When
        room_open_rule.RULE.check(open_room, make_request(), [])
        # Then
        # no exception is raised: the room is open


if __name__ == "__main__":
    unittest.main()
