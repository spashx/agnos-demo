# RQ-BKG-002, RQ-BKG-005, RQ-BKG-007, DEC-BKG-004 (ADR-BKG-003)
"""Unit tests of the JSON file repository adapter."""

from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

from roombook.domain import Reservation, ReservationStatus
from roombook.errors import RESERVATION_NOT_FOUND, ReservationNotFound
from roombook.file_repository import STORAGE_CORRUPTED, FileReservationRepository, StorageCorrupted

UTC = timezone.utc
BASE_TIME = datetime(2026, 1, 1, tzinfo=UTC)
ONE_HOUR = timedelta(hours=1)
ROOM_ID = "room-alpha"
ORGANIZER = "alice@example.test"
ATTENDEES = 3
DATA_FILE_NAME = "reservations.json"
CORRUPTED_TEXT = "{ this is not json"
WRONG_SHAPE_TEXT = '{"rooms": []}'
CONFIRMED_IDS = ("reservation-1", "reservation-2", "reservation-3")
CANCELLED_ID = "reservation-4"
NEW_ID = "reservation-5"
INTERRUPTED_MESSAGE = "simulated interruption"


class InterruptedSave(Exception):
    """Simulates a save interrupted before the final rename (RQ-BKG-007)."""


def make_reservation(reservation_id: str, status: ReservationStatus = ReservationStatus.CONFIRMED) -> Reservation:
    """Build a reservation of the test room (RQ-BKG-002)."""
    return Reservation(
        id=reservation_id,
        room_id=ROOM_ID,
        organizer=ORGANIZER,
        start=BASE_TIME,
        end=BASE_TIME + ONE_HOUR,
        attendees=ATTENDEES,
        status=status,
    )


class FileReservationRepositoryTest(unittest.TestCase):
    """Tests of FileReservationRepository (RQ-BKG-007, DEC-BKG-004)."""

    # RQ-BKG-002
    def setUp(self) -> None:
        self._directory = tempfile.TemporaryDirectory()
        self.path = Path(self._directory.name) / DATA_FILE_NAME

    # RQ-BKG-002
    def tearDown(self) -> None:
        self._directory.cleanup()

    # RQ-BKG-002
    def test_given_three_confirmed_and_one_cancelled_when_reopened_then_the_same_four_are_returned(self) -> None:
        # Given
        repository = FileReservationRepository(self.path)
        for reservation_id in CONFIRMED_IDS:
            repository.add(make_reservation(reservation_id))
        repository.add(make_reservation(CANCELLED_ID, status=ReservationStatus.CANCELLED))
        # When
        reopened = FileReservationRepository(self.path)
        # Then
        self.assertCountEqual(reopened.list_all(), repository.list_all())
        self.assertEqual(len(reopened.list_all()), len(CONFIRMED_IDS) + 1)

    # RQ-BKG-005
    def test_given_reservation_cancelled_when_reopened_then_cancelled_status_is_kept(self) -> None:
        # Given
        repository = FileReservationRepository(self.path)
        repository.add(make_reservation(CANCELLED_ID))
        repository.update(make_reservation(CANCELLED_ID, status=ReservationStatus.CANCELLED))
        # When
        reopened = FileReservationRepository(self.path)
        # Then
        self.assertEqual(reopened.get(CANCELLED_ID).status, ReservationStatus.CANCELLED)

    # RQ-BKG-002
    def test_given_save_interrupted_when_reservation_added_then_reopened_file_keeps_previous_reservations(self) -> None:
        # Given
        repository = FileReservationRepository(self.path)
        repository.add(make_reservation(CONFIRMED_IDS[0]))
        # When
        with mock.patch("roombook.file_repository.write_atomically", side_effect=InterruptedSave(INTERRUPTED_MESSAGE)):
            with self.assertRaises(InterruptedSave):
                repository.add(make_reservation(NEW_ID))
        # Then
        reopened = FileReservationRepository(self.path)
        self.assertEqual([item.id for item in reopened.list_all()], [CONFIRMED_IDS[0]])

    # RQ-BKG-002
    def test_given_no_data_file_when_opened_then_no_reservation_is_returned(self) -> None:
        # Given
        # no data file exists
        # When
        repository = FileReservationRepository(self.path)
        # Then
        self.assertEqual(repository.list_all(), [])

    # RQ-BKG-002
    def test_given_corrupted_json_when_opened_then_storage_corrupted_is_raised(self) -> None:
        # Given
        self.path.write_text(CORRUPTED_TEXT, encoding="utf-8")
        # When
        with self.assertRaises(StorageCorrupted) as context:
            FileReservationRepository(self.path)
        # Then
        self.assertEqual(context.exception.code, STORAGE_CORRUPTED)

    # RQ-BKG-002
    def test_given_file_of_wrong_shape_when_opened_then_storage_corrupted_is_raised(self) -> None:
        # Given
        self.path.write_text(WRONG_SHAPE_TEXT, encoding="utf-8")
        # When
        with self.assertRaises(StorageCorrupted) as context:
            FileReservationRepository(self.path)
        # Then
        self.assertEqual(context.exception.code, STORAGE_CORRUPTED)

    # RQ-BKG-002
    def test_given_unknown_identifier_when_get_then_reservation_not_found_is_raised(self) -> None:
        # Given
        repository = FileReservationRepository(self.path)
        # When
        with self.assertRaises(ReservationNotFound) as context:
            repository.get(NEW_ID)
        # Then
        self.assertEqual(context.exception.code, RESERVATION_NOT_FOUND)


if __name__ == "__main__":
    unittest.main()
