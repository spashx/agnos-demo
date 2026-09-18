# RQ-BKG-001, RQ-BKG-002, RQ-BKG-003, RQ-BKG-005, DEC-BKG-001 (ADR-BKG-001)
"""Unit tests of the domain objects."""

from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from roombook.domain import (
    MIN_CAPACITY,
    OPEN_BY_DEFAULT,
    Reservation,
    ReservationRequest,
    ReservationStatus,
    Room,
)

UTC = timezone.utc
YEAR = 2026
MONTH = 1
DAY = 1
BASE_TIME = datetime(YEAR, MONTH, DAY, tzinfo=UTC)
ONE_HOUR = timedelta(hours=1)
HALF_HOUR = timedelta(minutes=30)
ROOM_ID = "room-alpha"
ROOM_NAME = "Alpha"
ROOM_CAPACITY = 6
ORGANIZER = "alice@example.test"
ATTENDEES = 3
RESERVATION_ID = "reservation-1"
BELOW_MINIMUM_CAPACITY = MIN_CAPACITY - 1
FIRST_START = BASE_TIME + ONE_HOUR
FIRST_END = FIRST_START + ONE_HOUR
EARLIER_START = FIRST_START - ONE_HOUR
LATER_END = FIRST_END + ONE_HOUR


def make_reservation() -> Reservation:
    """Build the reservation used by the overlap tests (RQ-BKG-003)."""
    return Reservation(
        id=RESERVATION_ID,
        room_id=ROOM_ID,
        organizer=ORGANIZER,
        start=FIRST_START,
        end=FIRST_END,
        attendees=ATTENDEES,
    )


class RoomTest(unittest.TestCase):
    """Tests of Room (RQ-BKG-001)."""

    # RQ-BKG-001
    def test_given_minimum_capacity_when_room_created_then_capacity_is_kept(self) -> None:
        # Given
        capacity = MIN_CAPACITY
        # When
        room = Room(id=ROOM_ID, name=ROOM_NAME, capacity=capacity)
        # Then
        self.assertEqual(room.capacity, MIN_CAPACITY)

    # RQ-BKG-001
    def test_given_capacity_below_minimum_when_room_created_then_value_error_is_raised(self) -> None:
        # Given
        capacity = BELOW_MINIMUM_CAPACITY
        # When
        with self.assertRaises(ValueError):
            Room(id=ROOM_ID, name=ROOM_NAME, capacity=capacity)
        # Then
        # the ValueError above is the expected outcome

    # RQ-BKG-001
    def test_given_room_created_without_flag_when_read_then_room_is_open(self) -> None:
        # Given
        room = Room(id=ROOM_ID, name=ROOM_NAME, capacity=ROOM_CAPACITY)
        # When
        is_open = room.open
        # Then
        self.assertEqual(is_open, OPEN_BY_DEFAULT)


class ReservationRequestTest(unittest.TestCase):
    """Tests of ReservationRequest (RQ-BKG-002)."""

    # RQ-BKG-002
    def test_given_end_before_start_when_request_created_then_value_error_is_raised(self) -> None:
        # Given
        start = FIRST_END
        end = FIRST_START
        # When
        with self.assertRaises(ValueError):
            ReservationRequest(room_id=ROOM_ID, organizer=ORGANIZER, start=start, end=end, attendees=ATTENDEES)
        # Then
        # the ValueError above is the expected outcome

    # RQ-BKG-002
    def test_given_end_equal_to_start_when_request_created_then_value_error_is_raised(self) -> None:
        # Given
        start = FIRST_START
        end = FIRST_START
        # When
        with self.assertRaises(ValueError):
            ReservationRequest(room_id=ROOM_ID, organizer=ORGANIZER, start=start, end=end, attendees=ATTENDEES)
        # Then
        # the ValueError above is the expected outcome


class ReservationTest(unittest.TestCase):
    """Tests of Reservation overlap and cancellation (RQ-BKG-003, RQ-BKG-005)."""

    # RQ-BKG-003
    def test_given_reservation_when_interval_overlaps_then_overlaps_is_true(self) -> None:
        # Given
        reservation = make_reservation()
        start = FIRST_START + HALF_HOUR
        end = FIRST_END + HALF_HOUR
        # When
        result = reservation.overlaps(start, end)
        # Then
        self.assertTrue(result)

    # RQ-BKG-003
    def test_given_reservation_when_interval_contains_it_then_overlaps_is_true(self) -> None:
        # Given
        reservation = make_reservation()
        # When
        result = reservation.overlaps(EARLIER_START, LATER_END)
        # Then
        self.assertTrue(result)

    # RQ-BKG-003
    def test_given_reservation_when_interval_starts_at_its_end_then_overlaps_is_false(self) -> None:
        # Given
        reservation = make_reservation()
        # When
        result = reservation.overlaps(FIRST_END, LATER_END)
        # Then
        self.assertFalse(result)

    # RQ-BKG-003
    def test_given_reservation_when_interval_ends_at_its_start_then_overlaps_is_false(self) -> None:
        # Given
        reservation = make_reservation()
        # When
        result = reservation.overlaps(EARLIER_START, FIRST_START)
        # Then
        self.assertFalse(result)

    # RQ-BKG-005
    def test_given_confirmed_reservation_when_cancelled_then_status_is_cancelled_and_original_is_unchanged(
        self,
    ) -> None:
        # Given
        reservation = make_reservation()
        # When
        cancelled = reservation.cancelled()
        # Then
        self.assertEqual(cancelled.status, ReservationStatus.CANCELLED)
        self.assertEqual(reservation.status, ReservationStatus.CONFIRMED)


if __name__ == "__main__":
    unittest.main()
