# RQ-BKG-002, RQ-BKG-003, RQ-BKG-005, DEC-BKG-003 (ADR-BKG-002)
"""Unit tests of the in-memory repository adapter."""

from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from roombook.domain import Reservation, ReservationStatus
from roombook.errors import RESERVATION_NOT_FOUND, ReservationNotFound
from roombook.memory_repository import InMemoryReservationRepository

UTC = timezone.utc
BASE_TIME = datetime(2026, 1, 1, tzinfo=UTC)
ONE_HOUR = timedelta(hours=1)
ROOM_ID = "room-alpha"
OTHER_ROOM_ID = "room-beta"
ORGANIZER = "alice@example.test"
ATTENDEES = 3
CONFIRMED_ID = "reservation-confirmed"
CANCELLED_ID = "reservation-cancelled"
OTHER_ROOM_RESERVATION_ID = "reservation-other-room"
UNKNOWN_ID = "reservation-missing"


def make_reservation(reservation_id: str, room_id: str = ROOM_ID, status: ReservationStatus = ReservationStatus.CONFIRMED) -> Reservation:
    """Build a reservation with a fixed interval (RQ-BKG-002)."""
    return Reservation(
        id=reservation_id,
        room_id=room_id,
        organizer=ORGANIZER,
        start=BASE_TIME,
        end=BASE_TIME + ONE_HOUR,
        attendees=ATTENDEES,
        status=status,
    )


class InMemoryReservationRepositoryTest(unittest.TestCase):
    """Tests of InMemoryReservationRepository (DEC-BKG-003)."""

    # RQ-BKG-002
    def setUp(self) -> None:
        self.repository = InMemoryReservationRepository()

    # RQ-BKG-002
    def test_given_empty_repository_when_reservation_added_then_get_returns_it(self) -> None:
        # Given
        reservation = make_reservation(CONFIRMED_ID)
        # When
        self.repository.add(reservation)
        # Then
        self.assertEqual(self.repository.get(CONFIRMED_ID), reservation)

    # RQ-BKG-002
    def test_given_unknown_identifier_when_get_then_reservation_not_found_is_raised(self) -> None:
        # Given
        # an empty repository
        # When
        with self.assertRaises(ReservationNotFound) as context:
            self.repository.get(UNKNOWN_ID)
        # Then
        self.assertEqual(context.exception.code, RESERVATION_NOT_FOUND)

    # RQ-BKG-003
    def test_given_reservations_of_two_rooms_when_listing_confirmed_for_room_then_only_its_confirmed_are_returned(
        self,
    ) -> None:
        # Given
        confirmed = make_reservation(CONFIRMED_ID)
        self.repository.add(confirmed)
        self.repository.add(make_reservation(CANCELLED_ID, status=ReservationStatus.CANCELLED))
        self.repository.add(make_reservation(OTHER_ROOM_RESERVATION_ID, room_id=OTHER_ROOM_ID))
        # When
        result = self.repository.list_confirmed_for_room(ROOM_ID)
        # Then
        self.assertEqual(result, [confirmed])

    # RQ-BKG-005
    def test_given_stored_reservation_when_updated_then_get_returns_the_new_status(self) -> None:
        # Given
        reservation = make_reservation(CONFIRMED_ID)
        self.repository.add(reservation)
        # When
        self.repository.update(reservation.cancelled())
        # Then
        self.assertEqual(self.repository.get(CONFIRMED_ID).status, ReservationStatus.CANCELLED)

    # RQ-BKG-005
    def test_given_unknown_reservation_when_updated_then_reservation_not_found_is_raised(self) -> None:
        # Given
        reservation = make_reservation(UNKNOWN_ID)
        # When
        with self.assertRaises(ReservationNotFound) as context:
            self.repository.update(reservation)
        # Then
        self.assertEqual(context.exception.code, RESERVATION_NOT_FOUND)

    # RQ-BKG-002
    def test_given_two_reservations_when_listing_all_then_both_are_returned(self) -> None:
        # Given
        first = make_reservation(CONFIRMED_ID)
        second = make_reservation(OTHER_ROOM_RESERVATION_ID, room_id=OTHER_ROOM_ID)
        self.repository.add(first)
        self.repository.add(second)
        # When
        result = self.repository.list_all()
        # Then
        self.assertCountEqual(result, [first, second])


if __name__ == "__main__":
    unittest.main()
