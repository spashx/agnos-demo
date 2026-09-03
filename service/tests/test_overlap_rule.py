# RQ-BKG-003, DEC-BKG-002 (ADR-BKG-001)
"""Unit tests of the overlap rule and of the packaged rule discovery."""

from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from roombook.domain import Reservation, ReservationRequest, Room
from roombook.errors import CONFLICT, ReservationConflict
from roombook.rules import load_rules
from roombook.rules import overlap_rule

UTC = timezone.utc
BASE_TIME = datetime(2026, 1, 1, tzinfo=UTC)
ONE_HOUR = timedelta(hours=1)
HALF_HOUR = timedelta(minutes=30)
ROOM_ID = "room-alpha"
ROOM_CAPACITY = 6
ORGANIZER = "alice@example.test"
ATTENDEES = 3
EXISTING_ID = "reservation-existing"
FIRST_START = BASE_TIME + ONE_HOUR
FIRST_END = FIRST_START + ONE_HOUR


def make_room() -> Room:
    """Build the open room used by the rule tests (RQ-BKG-003)."""
    return Room(id=ROOM_ID, name="Alpha", capacity=ROOM_CAPACITY)


def make_existing() -> list[Reservation]:
    """Build the Confirmed reservation from FIRST_START to FIRST_END (RQ-BKG-003)."""
    return [
        Reservation(
            id=EXISTING_ID,
            room_id=ROOM_ID,
            organizer=ORGANIZER,
            start=FIRST_START,
            end=FIRST_END,
            attendees=ATTENDEES,
        )
    ]


def make_request(start: datetime, end: datetime) -> ReservationRequest:
    """Build a request for the test room over the given interval (RQ-BKG-003)."""
    return ReservationRequest(room_id=ROOM_ID, organizer=ORGANIZER, start=start, end=end, attendees=ATTENDEES)


class OverlapRuleTest(unittest.TestCase):
    """Tests of OverlapRule (RQ-BKG-003)."""

    def test_given_reservation_from_ten_to_eleven_when_request_overlaps_then_conflict_names_it(self) -> None:
        # Given
        request = make_request(FIRST_START + HALF_HOUR, FIRST_END + HALF_HOUR)
        # When
        with self.assertRaises(ReservationConflict) as context:
            overlap_rule.RULE.check(make_room(), request, make_existing())
        # Then
        self.assertEqual(context.exception.conflicting_id, EXISTING_ID)
        self.assertEqual(context.exception.code, CONFLICT)

    # RQ-BKG-003
    def test_given_reservation_from_ten_to_eleven_when_request_starts_at_its_end_then_no_error(self) -> None:
        # Given
        request = make_request(FIRST_END, FIRST_END + ONE_HOUR)
        # When
        overlap_rule.RULE.check(make_room(), request, make_existing())
        # Then
        # no exception is raised: back-to-back intervals do not conflict

    # RQ-BKG-003
    def test_given_reservation_from_ten_to_eleven_when_request_ends_at_its_start_then_no_error(self) -> None:
        # Given
        request = make_request(BASE_TIME, FIRST_START)
        # When
        overlap_rule.RULE.check(make_room(), request, make_existing())
        # Then
        # no exception is raised: the request ends when the reservation starts

    # RQ-BKG-003
    def test_given_no_existing_reservation_when_request_checked_then_no_error(self) -> None:
        # Given
        request = make_request(FIRST_START, FIRST_END)
        # When
        overlap_rule.RULE.check(make_room(), request, [])
        # Then
        # no exception is raised: the room is free

    # RQ-BKG-003
    def test_given_packaged_rules_when_loaded_then_overlap_rule_is_among_them(self) -> None:
        # Given
        # the rule modules of the rules package
        # When
        rules = load_rules()
        # Then
        self.assertIn(overlap_rule.RULE, rules)


if __name__ == "__main__":
    unittest.main()
