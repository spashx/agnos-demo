# RQ-BKG-007, DEC-BKG-003, DEC-BKG-004 (ADR-BKG-002, ADR-BKG-003)
"""Unit tests of the repository factory."""

from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from roombook.domain import Reservation
from roombook.file_repository import FileReservationRepository
from roombook.memory_repository import InMemoryReservationRepository
from roombook.repository_factory import DATA_FILE_ENV, create_repository

UTC = timezone.utc
BASE_TIME = datetime(2026, 1, 1, tzinfo=UTC)
ONE_HOUR = timedelta(hours=1)
ROOM_ID = "room-alpha"
ORGANIZER = "alice@example.test"
ATTENDEES = 3
RESERVATION_ID = "reservation-1"
DATA_FILE_NAME = "reservations.json"
EMPTY_SETTING = ""


def make_reservation() -> Reservation:
    """Build a reservation of the test room (RQ-BKG-007)."""
    return Reservation(
        id=RESERVATION_ID,
        room_id=ROOM_ID,
        organizer=ORGANIZER,
        start=BASE_TIME,
        end=BASE_TIME + ONE_HOUR,
        attendees=ATTENDEES,
    )


class CreateRepositoryTest(unittest.TestCase):
    """Tests of create_repository (RQ-BKG-007, DEC-BKG-004)."""

    # RQ-BKG-007
    def setUp(self) -> None:
        self._directory = tempfile.TemporaryDirectory()
        self.path = Path(self._directory.name) / DATA_FILE_NAME

    # RQ-BKG-007
    def tearDown(self) -> None:
        self._directory.cleanup()

    # RQ-BKG-007
    def test_given_data_file_setting_when_factory_called_then_file_repository_on_that_path_is_returned(self) -> None:
        # Given
        environ = {DATA_FILE_ENV: str(self.path)}
        # When
        repository = create_repository(environ)
        repository.add(make_reservation())
        # Then
        self.assertIsInstance(repository, FileReservationRepository)
        self.assertTrue(self.path.exists())

    # RQ-BKG-007
    def test_given_no_data_file_setting_when_factory_called_then_in_memory_repository_is_returned(self) -> None:
        # Given
        environ: dict[str, str] = {}
        # When
        repository = create_repository(environ)
        # Then
        self.assertIsInstance(repository, InMemoryReservationRepository)

    # RQ-BKG-007
    def test_given_empty_data_file_setting_when_factory_called_then_in_memory_repository_is_returned(self) -> None:
        # Given
        environ = {DATA_FILE_ENV: EMPTY_SETTING}
        # When
        repository = create_repository(environ)
        # Then
        self.assertIsInstance(repository, InMemoryReservationRepository)


if __name__ == "__main__":
    unittest.main()
