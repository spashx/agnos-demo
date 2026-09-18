# RQ-BKG-005, DEC-BKG-001 (ADR-BKG-001)
"""Unit tests of the cancel-reservation use case and of the system clock."""

from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from roombook.clock import SystemClock
from roombook.domain import Reservation, ReservationStatus
from roombook.errors import ALREADY_STARTED, RESERVATION_NOT_FOUND, ReservationAlreadyStarted, ReservationNotFound
from roombook.memory_repository import InMemoryReservationRepository
from roombook.use_cases.cancel_reservation import CancelReservation

UTC = timezone.utc
BASE_TIME = datetime(2026, 1, 1, tzinfo=UTC)
ONE_HOUR = timedelta(hours=1)
ROOM_ID = "room-alpha"
ORGANIZER = "alice@example.test"
ATTENDEES = 3
RESERVATION_ID = "reservation-1"
UNKNOWN_ID = "reservation-missing"
BEFORE_START = BASE_TIME - ONE_HOUR
AFTER_START = BASE_TIME + ONE_HOUR


class FixedClock:
    """Clock double that always returns the same instant (RQ-BKG-005)."""

    def __init__(self, instant: datetime) -> None:
        self._instant = instant

    def now(self) -> datetime:
        """Return the fixed instant (RQ-BKG-005)."""
        return self._instant


def make_reservation(status: ReservationStatus = ReservationStatus.CONFIRMED) -> Reservation:
    """Build the reservation starting at BASE_TIME (RQ-BKG-005)."""
    return Reservation(
        id=RESERVATION_ID,
        room_id=ROOM_ID,
        organizer=ORGANIZER,
        start=BASE_TIME,
        end=BASE_TIME + ONE_HOUR,
        attendees=ATTENDEES,
        status=status,
    )


class CancelReservationTest(unittest.TestCase):
    """Tests of CancelReservation (RQ-BKG-005)."""

    # RQ-BKG-005
    def setUp(self) -> None:
        self.repository = InMemoryReservationRepository()

    # RQ-BKG-005
    def test_given_confirmed_reservation_not_started_when_cancelled_then_status_is_cancelled(self) -> None:
        # Given
        self.repository.add(make_reservation())
        use_case = CancelReservation(self.repository, FixedClock(BEFORE_START))
        # When
        result = use_case.execute(RESERVATION_ID)
        # Then
        self.assertEqual(result.status, ReservationStatus.CANCELLED)
        self.assertEqual(self.repository.get(RESERVATION_ID).status, ReservationStatus.CANCELLED)

    # RQ-BKG-005
    def test_given_confirmed_reservation_already_started_when_cancelled_then_already_started_is_raised(self) -> None:
        # Given
        self.repository.add(make_reservation())
        use_case = CancelReservation(self.repository, FixedClock(AFTER_START))
        # When
        with self.assertRaises(ReservationAlreadyStarted) as context:
            use_case.execute(RESERVATION_ID)
        # Then
        self.assertEqual(context.exception.code, ALREADY_STARTED)
        self.assertEqual(self.repository.get(RESERVATION_ID).status, ReservationStatus.CONFIRMED)

    # RQ-BKG-005
    def test_given_already_cancelled_reservation_when_cancelled_again_then_it_is_returned_unchanged(self) -> None:
        # Given
        self.repository.add(make_reservation(status=ReservationStatus.CANCELLED))
        use_case = CancelReservation(self.repository, FixedClock(AFTER_START))
        # When
        result = use_case.execute(RESERVATION_ID)
        # Then
        self.assertEqual(result.status, ReservationStatus.CANCELLED)

    # RQ-BKG-005
    def test_given_unknown_identifier_when_cancelled_then_reservation_not_found_is_raised(self) -> None:
        # Given
        use_case = CancelReservation(self.repository, FixedClock(BEFORE_START))
        # When
        with self.assertRaises(ReservationNotFound) as context:
            use_case.execute(UNKNOWN_ID)
        # Then
        self.assertEqual(context.exception.code, RESERVATION_NOT_FOUND)


class SystemClockTest(unittest.TestCase):
    """Tests of SystemClock (RQ-BKG-005)."""

    # RQ-BKG-005
    def test_given_system_clock_when_now_then_a_timezone_aware_utc_time_is_returned(self) -> None:
        # Given
        clock = SystemClock()
        # When
        now = clock.now()
        # Then
        self.assertIsNotNone(now.tzinfo)
        self.assertEqual(now.utcoffset(), timedelta(0))


if __name__ == "__main__":
    unittest.main()
