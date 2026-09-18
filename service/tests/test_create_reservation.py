# RQ-BKG-002, DEC-BKG-001, DEC-BKG-002 (ADR-BKG-001)
"""Unit tests of the create-reservation use case."""

from __future__ import annotations

import unittest
import uuid
from collections.abc import Sequence
from datetime import datetime, timedelta, timezone

from roombook.catalog import RoomCatalog
from roombook.domain import Reservation, ReservationRequest, ReservationStatus, Room
from roombook.errors import CapacityExceeded, ROOM_NOT_FOUND, RoomNotFound
from roombook.memory_repository import InMemoryReservationRepository
from roombook.use_cases.create_reservation import CreateReservation, uuid_id_factory

UTC = timezone.utc
BASE_TIME = datetime(2026, 1, 1, tzinfo=UTC)
ONE_HOUR = timedelta(hours=1)
ROOM_ID = "room-alpha"
ROOM_NAME = "Alpha"
ROOM_CAPACITY = 6
UNKNOWN_ROOM_ID = "room-missing"
ORGANIZER = "alice@example.test"
ATTENDEES = 3
NEW_RESERVATION_ID = "reservation-new"
EXISTING_RESERVATION_ID = "reservation-existing"


class RecordingRule:
    """Rule double that records the calls it receives (DEC-BKG-002)."""

    def __init__(self, calls: list[str], name: str, error: Exception | None = None) -> None:
        self._calls = calls
        self._name = name
        self._error = error
        self.existing_seen: Sequence[Reservation] = ()

    def check(self, room: Room, request: ReservationRequest, existing: Sequence[Reservation]) -> None:
        """Record the call and optionally raise (DEC-BKG-002)."""
        self._calls.append(self._name)
        self.existing_seen = tuple(existing)
        if self._error is not None:
            raise self._error


class CreateReservationTest(unittest.TestCase):
    """Tests of CreateReservation (RQ-BKG-002)."""

    # RQ-BKG-002
    def setUp(self) -> None:
        self.catalog = RoomCatalog()
        self.catalog.add(Room(id=ROOM_ID, name=ROOM_NAME, capacity=ROOM_CAPACITY))
        self.repository = InMemoryReservationRepository()
        self.request = ReservationRequest(
            room_id=ROOM_ID,
            organizer=ORGANIZER,
            start=BASE_TIME,
            end=BASE_TIME + ONE_HOUR,
            attendees=ATTENDEES,
        )

    # RQ-BKG-002
    def test_given_open_room_without_reservation_when_valid_request_then_confirmed_reservation_is_stored(self) -> None:
        # Given
        use_case = CreateReservation(self.catalog, self.repository, [], id_factory=lambda: NEW_RESERVATION_ID)
        # When
        reservation = use_case.execute(self.request)
        # Then
        self.assertEqual(reservation.id, NEW_RESERVATION_ID)
        self.assertEqual(self.repository.get(NEW_RESERVATION_ID).status, ReservationStatus.CONFIRMED)

    # RQ-BKG-002
    def test_given_unknown_room_when_request_executed_then_room_not_found_is_raised(self) -> None:
        # Given
        use_case = CreateReservation(self.catalog, self.repository, [])
        unknown = ReservationRequest(
            room_id=UNKNOWN_ROOM_ID,
            organizer=ORGANIZER,
            start=BASE_TIME,
            end=BASE_TIME + ONE_HOUR,
            attendees=ATTENDEES,
        )
        # When
        with self.assertRaises(RoomNotFound) as context:
            use_case.execute(unknown)
        # Then
        self.assertEqual(context.exception.code, ROOM_NOT_FOUND)

    # RQ-BKG-002
    def test_given_rule_that_refuses_when_request_executed_then_nothing_is_stored(self) -> None:
        # Given
        calls: list[str] = []
        refusing = RecordingRule(calls, "refusing", error=CapacityExceeded())
        use_case = CreateReservation(self.catalog, self.repository, [refusing])
        # When
        with self.assertRaises(CapacityExceeded):
            use_case.execute(self.request)
        # Then
        self.assertEqual(self.repository.list_all(), [])

    # RQ-BKG-002
    def test_given_several_rules_when_request_executed_then_rules_run_in_given_order(self) -> None:
        # Given
        calls: list[str] = []
        rules = [RecordingRule(calls, "first"), RecordingRule(calls, "second")]
        use_case = CreateReservation(self.catalog, self.repository, rules)
        # When
        use_case.execute(self.request)
        # Then
        self.assertEqual(calls, ["first", "second"])

    # RQ-BKG-002
    def test_given_confirmed_reservation_of_room_when_request_executed_then_rules_receive_it_as_existing(self) -> None:
        # Given
        existing = Reservation(
            id=EXISTING_RESERVATION_ID,
            room_id=ROOM_ID,
            organizer=ORGANIZER,
            start=BASE_TIME,
            end=BASE_TIME + ONE_HOUR,
            attendees=ATTENDEES,
        )
        self.repository.add(existing)
        rule = RecordingRule([], "recording")
        use_case = CreateReservation(self.catalog, self.repository, [rule])
        # When
        use_case.execute(self.request)
        # Then
        self.assertEqual(rule.existing_seen, (existing,))


class UuidIdFactoryTest(unittest.TestCase):
    """Tests of uuid_id_factory (RQ-BKG-002)."""

    # RQ-BKG-002
    def test_given_default_factory_when_called_twice_then_two_distinct_uuids_are_returned(self) -> None:
        # Given
        # the default identifier factory
        # When
        first = uuid_id_factory()
        second = uuid_id_factory()
        # Then
        self.assertNotEqual(first, second)
        self.assertEqual(str(uuid.UUID(first)), first)


if __name__ == "__main__":
    unittest.main()
