# RQ-BKG-003, RQ-BKG-004, DEC-BKG-002 (ADR-BKG-001)
"""Unit tests of the capacity rule and of the rule order given by the discovery."""

from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from roombook.domain import ReservationRequest, Room
from roombook.errors import CAPACITY_EXCEEDED, CapacityExceeded
from roombook.rules import capacity_rule, load_rules, overlap_rule, room_open_rule

UTC = timezone.utc
BASE_TIME = datetime(2026, 1, 1, tzinfo=UTC)
ONE_HOUR = timedelta(hours=1)
ROOM_ID = "room-alpha"
ROOM_NAME = "Alpha"
ROOM_CAPACITY = 6
OVER_CAPACITY = ROOM_CAPACITY + 1
ORGANIZER = "alice@example.test"


def make_room() -> Room:
    """Build the room of the capacity tests (RQ-BKG-004)."""
    return Room(id=ROOM_ID, name=ROOM_NAME, capacity=ROOM_CAPACITY)


def make_request(attendees: int) -> ReservationRequest:
    """Build a request with the given attendee count (RQ-BKG-004)."""
    return ReservationRequest(
        room_id=ROOM_ID,
        organizer=ORGANIZER,
        start=BASE_TIME,
        end=BASE_TIME + ONE_HOUR,
        attendees=attendees,
    )


class CapacityRuleTest(unittest.TestCase):
    """Tests of CapacityRule (RQ-BKG-004)."""

    # RQ-BKG-003
    def test_given_room_of_capacity_six_when_seven_attendees_requested_then_capacity_exceeded_is_raised(self) -> None:
        # Given
        request = make_request(OVER_CAPACITY)
        # When
        with self.assertRaises(CapacityExceeded) as context:
            capacity_rule.RULE.check(make_room(), request, [])
        # Then
        self.assertEqual(context.exception.code, CAPACITY_EXCEEDED)

    # RQ-BKG-003
    def test_given_room_of_capacity_six_when_six_attendees_requested_then_no_error(self) -> None:
        # Given
        request = make_request(ROOM_CAPACITY)
        # When
        capacity_rule.RULE.check(make_room(), request, [])
        # Then
        # no exception is raised: the attendees fit in the room

    # RQ-BKG-003
    def test_given_packaged_rules_when_loaded_then_they_are_sorted_by_rule_order(self) -> None:
        # Given
        # the rule modules of the rules package
        # When
        rules = load_rules()
        # Then
        self.assertEqual(rules, [room_open_rule.RULE, capacity_rule.RULE, overlap_rule.RULE])


if __name__ == "__main__":
    unittest.main()
