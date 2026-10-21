# RQ-CLI-006, RQ-CLI-005, DEC-CLI-001 (ADR-CLI-001)
"""Tests of the service's start command: rooms file, wiring and serving, without opening a socket."""

from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import roombook.__main__ as main_module
from roombook.__main__ import HOST, PORT, build_api, load_rooms, main
from roombook.api import (
    FIELD_ATTENDEES,
    FIELD_END,
    FIELD_ID,
    FIELD_ORGANIZER,
    FIELD_ROOM_ID,
    FIELD_START,
    METHOD_GET,
    METHOD_POST,
    STATUS_CREATED,
    STATUS_OK,
)
from roombook.domain import Room

ROOMS_NAME = "rooms.json"
OPEN_ROOM = {"id": "atlas", "name": "Atlas", "capacity": 8, "open": True}
CLOSED_ROOM = {"id": "boreal", "name": "Boreal", "capacity": 4, "open": False}
EXPECTED_HOST = "127.0.0.1"
EXPECTED_PORT = 8080
PATH_ROOMS = "/rooms"
PATH_RESERVATIONS = "/reservations"
ORGANIZER = "linda"
ATTENDEES = 2
START_OFFSET = timedelta(days=1)
DURATION = timedelta(hours=1)
NO_SETTINGS: dict[str, str] = {}


def _write_rooms(folder: Path) -> Path:
    path = folder / ROOMS_NAME
    path.write_text(json.dumps([OPEN_ROOM, CLOSED_ROOM]), encoding="utf-8")
    return path


class LoadRoomsTest(unittest.TestCase):
    """Tests for load_rooms (RQ-CLI-006)."""

    # RQ-CLI-006
    def test_given_rooms_file_with_two_rooms_when_loaded_then_both_rooms_are_returned(self) -> None:
        # Given
        with tempfile.TemporaryDirectory() as folder:
            path = _write_rooms(Path(folder))
            # When
            rooms = load_rooms(path)
        # Then
        self.assertEqual(rooms, [Room(**OPEN_ROOM), Room(**CLOSED_ROOM)])


class BuildApiTest(unittest.TestCase):
    """Tests for build_api (RQ-CLI-006, RQ-CLI-005)."""

    # RQ-CLI-006
    def test_given_two_rooms_when_api_built_then_get_rooms_answers_both(self) -> None:
        # Given
        rooms = [Room(**OPEN_ROOM), Room(**CLOSED_ROOM)]
        # When
        api = build_api(rooms, NO_SETTINGS)
        status, body = api.handle(METHOD_GET, PATH_ROOMS, None)
        # Then
        self.assertEqual(status, STATUS_OK)
        assert isinstance(body, list)
        self.assertEqual([room[FIELD_ID] for room in body], [OPEN_ROOM[FIELD_ID], CLOSED_ROOM[FIELD_ID]])

    # RQ-CLI-006
    def test_given_api_built_when_open_room_booked_then_answers_created(self) -> None:
        # Given
        api = build_api([Room(**OPEN_ROOM)], NO_SETTINGS)
        start = datetime.now(timezone.utc) + START_OFFSET
        booking = {FIELD_ROOM_ID: OPEN_ROOM[FIELD_ID], FIELD_ORGANIZER: ORGANIZER, FIELD_START: start.isoformat(),
                   FIELD_END: (start + DURATION).isoformat(), FIELD_ATTENDEES: ATTENDEES}
        # When
        status, _ = api.handle(METHOD_POST, PATH_RESERVATIONS, booking)
        # Then
        self.assertEqual(status, STATUS_CREATED)


class MainTest(unittest.TestCase):
    """Tests for main, with serve replaced by a mock (RQ-CLI-006)."""

    # RQ-CLI-006
    def test_given_rooms_file_when_main_runs_then_serves_on_local_host_and_port_8080(self) -> None:
        # Given
        with tempfile.TemporaryDirectory() as folder:
            path = _write_rooms(Path(folder))
            # When
            with patch.object(main_module, "serve") as serve:
                main(path, NO_SETTINGS)
        # Then
        serve.assert_called_once()
        self.assertEqual(serve.call_args.args[1:], (EXPECTED_HOST, EXPECTED_PORT))
        self.assertEqual((HOST, PORT), (EXPECTED_HOST, EXPECTED_PORT))


if __name__ == "__main__":
    unittest.main()
