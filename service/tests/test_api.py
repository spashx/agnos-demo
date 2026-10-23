# RQ-CLI-005, DEC-CLI-001 (ADR-CLI-001)
"""Tests of the HTTP/JSON adapter, calling ReservationApi.handle directly without sockets."""

from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone
from typing import Any
from unittest.mock import patch

import roombook.api as api_module
from roombook.api import (
    CODE_BAD_REQUEST,
    CODE_NOT_FOUND,
    FIELD_ATTENDEES,
    FIELD_CAPACITY,
    FIELD_CODE,
    FIELD_END,
    FIELD_ID,
    FIELD_NAME,
    FIELD_OPEN,
    FIELD_ORGANIZER,
    FIELD_ROOM_ID,
    FIELD_START,
    FIELD_STATUS,
    METHOD_DELETE,
    METHOD_GET,
    METHOD_POST,
    SEGMENT_RESERVATIONS,
    SEGMENT_ROOMS,
    STATUS_BAD_REQUEST,
    STATUS_CONFLICT,
    STATUS_CREATED,
    STATUS_NO_CONTENT,
    STATUS_NOT_FOUND,
    STATUS_OK,
    STATUS_UNPROCESSABLE,
    ReservationApi,
    serve,
)
from roombook.catalog import RoomCatalog
from roombook.domain import ReservationStatus, Room
from roombook.errors import (
    ALREADY_STARTED,
    CAPACITY_EXCEEDED,
    CONFLICT,
    RESERVATION_NOT_FOUND,
    ROOM_CLOSED,
    ROOM_NOT_FOUND,
)
from roombook.events import EventBus
from roombook.memory_repository import InMemoryReservationRepository
from roombook.publishing_create import PublishingCreateReservation
from roombook.rules import load_rules
from roombook.use_cases.cancel_reservation import CancelReservation
from roombook.use_cases.create_reservation import CreateReservation

ROOM_ID = "room-a"
ROOM_NAME = "Atlas"
CAPACITY = 6
CLOSED_ROOM_ID = "room-closed"
CLOSED_ROOM_NAME = "Boreal"
CLOSED_CAPACITY = 2
ORGANIZER = "alice"
NOW = datetime(2030, 5, 1, 8, 0, tzinfo=timezone.utc)
START = NOW + timedelta(hours=2)
DURATION = timedelta(hours=1)
HOST = "127.0.0.1"
PORT = 8080
PATH_ROOMS = f"/{SEGMENT_ROOMS}"
PATH_RESERVATIONS = f"/{SEGMENT_RESERVATIONS}"
UNKNOWN_PATH = "/unknown"
UNKNOWN_ID = "missing"
QUERY_SUFFIX = "?verbose=1"


class _FixedClock:
    """Clock whose time the test sets."""

    def __init__(self, moment: datetime) -> None:
        self.moment = moment

    # RQ-CLI-005
    def now(self) -> datetime:
        return self.moment


class _Wiring:
    """The API wired to real use cases, an in-memory repository and a controllable clock."""

    def __init__(self) -> None:
        self.clock = _FixedClock(NOW)
        self.repository = InMemoryReservationRepository()
        catalog = RoomCatalog()
        catalog.add(Room(id=ROOM_ID, name=ROOM_NAME, capacity=CAPACITY))
        catalog.add(Room(id=CLOSED_ROOM_ID, name=CLOSED_ROOM_NAME, capacity=CLOSED_CAPACITY, open=False))
        create = PublishingCreateReservation(
            CreateReservation(catalog, self.repository, load_rules()),
            EventBus(),
        )
        self.api = ReservationApi(catalog, create, CancelReservation(self.repository, self.clock))


def _booking(overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    body: dict[str, Any] = {
        FIELD_ROOM_ID: ROOM_ID,
        FIELD_ORGANIZER: ORGANIZER,
        FIELD_START: START.isoformat(),
        FIELD_END: (START + DURATION).isoformat(),
        FIELD_ATTENDEES: CAPACITY,
    }
    body.update(overrides or {})
    return body


def _book(wiring: _Wiring) -> dict[str, Any]:
    status, body = wiring.api.handle(METHOD_POST, PATH_RESERVATIONS, _booking())
    assert status == STATUS_CREATED
    assert isinstance(body, dict)
    return body


class ListRoomsTest(unittest.TestCase):
    """Tests for GET /rooms (RQ-CLI-005)."""

    # RQ-CLI-005
    def test_given_catalog_when_get_rooms_then_answers_ok_with_rooms_sorted_by_id(self) -> None:
        # Given
        wiring = _Wiring()
        # When
        status, body = wiring.api.handle(METHOD_GET, PATH_ROOMS, None)
        # Then
        self.assertEqual(status, STATUS_OK)
        assert isinstance(body, list)
        self.assertEqual([room[FIELD_ID] for room in body], sorted([ROOM_ID, CLOSED_ROOM_ID]))

    # RQ-CLI-005
    def test_given_closed_room_when_get_rooms_then_room_is_reported_as_not_open(self) -> None:
        # Given
        wiring = _Wiring()
        # When
        _, body = wiring.api.handle(METHOD_GET, PATH_ROOMS, None)
        # Then
        assert isinstance(body, list)
        closed = next(room for room in body if room[FIELD_ID] == CLOSED_ROOM_ID)
        self.assertEqual(closed[FIELD_NAME], CLOSED_ROOM_NAME)
        self.assertEqual(closed[FIELD_CAPACITY], CLOSED_CAPACITY)
        self.assertFalse(closed[FIELD_OPEN])

    # RQ-CLI-005
    def test_given_query_string_when_get_rooms_then_query_is_ignored(self) -> None:
        # Given
        wiring = _Wiring()
        # When
        status, _ = wiring.api.handle(METHOD_GET, f"{PATH_ROOMS}{QUERY_SUFFIX}", None)
        # Then
        self.assertEqual(status, STATUS_OK)


class CreateReservationRouteTest(unittest.TestCase):
    """Tests for POST /reservations (RQ-CLI-005)."""

    # RQ-CLI-005
    def test_given_valid_body_when_post_reservation_then_answers_created_with_confirmed_reservation(self) -> None:
        # Given
        wiring = _Wiring()
        # When
        status, body = wiring.api.handle(METHOD_POST, PATH_RESERVATIONS, _booking())
        # Then
        self.assertEqual(status, STATUS_CREATED)
        assert isinstance(body, dict)
        self.assertEqual(body[FIELD_ROOM_ID], ROOM_ID)
        self.assertEqual(body[FIELD_ORGANIZER], ORGANIZER)
        self.assertEqual(body[FIELD_STATUS], ReservationStatus.CONFIRMED.value)

    # RQ-CLI-005
    def test_given_valid_body_when_post_reservation_then_times_are_iso_text_with_offset(self) -> None:
        # Given
        wiring = _Wiring()
        # When
        body = _book(wiring)
        # Then
        self.assertEqual(datetime.fromisoformat(body[FIELD_START]), START)
        self.assertEqual(datetime.fromisoformat(body[FIELD_END]), START + DURATION)

    # RQ-CLI-005
    def test_given_existing_reservation_when_post_overlapping_then_answers_conflict(self) -> None:
        # Given
        wiring = _Wiring()
        _book(wiring)
        # When
        status, body = wiring.api.handle(METHOD_POST, PATH_RESERVATIONS, _booking())
        # Then
        self.assertEqual(status, STATUS_CONFLICT)
        assert isinstance(body, dict)
        self.assertEqual(body[FIELD_CODE], CONFLICT)

    # RQ-CLI-005
    def test_given_attendees_above_capacity_when_post_then_answers_unprocessable_capacity_exceeded(self) -> None:
        # Given
        wiring = _Wiring()
        # When
        status, body = wiring.api.handle(METHOD_POST, PATH_RESERVATIONS, _booking({FIELD_ATTENDEES: CAPACITY + 1}))
        # Then
        self.assertEqual(status, STATUS_UNPROCESSABLE)
        assert isinstance(body, dict)
        self.assertEqual(body[FIELD_CODE], CAPACITY_EXCEEDED)

    # RQ-CLI-005
    def test_given_closed_room_when_post_then_answers_unprocessable_room_closed(self) -> None:
        # Given
        wiring = _Wiring()
        # When
        status, body = wiring.api.handle(
            METHOD_POST,
            PATH_RESERVATIONS,
            _booking({FIELD_ROOM_ID: CLOSED_ROOM_ID, FIELD_ATTENDEES: CLOSED_CAPACITY}),
        )
        # Then
        self.assertEqual(status, STATUS_UNPROCESSABLE)
        assert isinstance(body, dict)
        self.assertEqual(body[FIELD_CODE], ROOM_CLOSED)

    # RQ-CLI-005
    def test_given_unknown_room_when_post_then_answers_not_found_room_not_found(self) -> None:
        # Given
        wiring = _Wiring()
        # When
        status, body = wiring.api.handle(METHOD_POST, PATH_RESERVATIONS, _booking({FIELD_ROOM_ID: UNKNOWN_ID}))
        # Then
        self.assertEqual(status, STATUS_NOT_FOUND)
        assert isinstance(body, dict)
        self.assertEqual(body[FIELD_CODE], ROOM_NOT_FOUND)

    # RQ-CLI-005
    def test_given_missing_field_when_post_then_answers_bad_request(self) -> None:
        # Given
        wiring = _Wiring()
        body_without_organizer = _booking()
        del body_without_organizer[FIELD_ORGANIZER]
        # When
        status, body = wiring.api.handle(METHOD_POST, PATH_RESERVATIONS, body_without_organizer)
        # Then
        self.assertEqual(status, STATUS_BAD_REQUEST)
        assert isinstance(body, dict)
        self.assertEqual(body[FIELD_CODE], CODE_BAD_REQUEST)

    # RQ-CLI-005
    def test_given_no_json_body_when_post_then_answers_bad_request(self) -> None:
        # Given
        wiring = _Wiring()
        # When
        status, body = wiring.api.handle(METHOD_POST, PATH_RESERVATIONS, None)
        # Then
        self.assertEqual(status, STATUS_BAD_REQUEST)
        assert isinstance(body, dict)
        self.assertEqual(body[FIELD_CODE], CODE_BAD_REQUEST)

    # RQ-CLI-005
    def test_given_naive_time_when_post_then_answers_bad_request(self) -> None:
        # Given
        wiring = _Wiring()
        # When
        status, body = wiring.api.handle(
            METHOD_POST,
            PATH_RESERVATIONS,
            _booking({FIELD_START: START.replace(tzinfo=None).isoformat()}),
        )
        # Then
        self.assertEqual(status, STATUS_BAD_REQUEST)
        assert isinstance(body, dict)
        self.assertEqual(body[FIELD_CODE], CODE_BAD_REQUEST)

    # RQ-CLI-005
    def test_given_boolean_attendees_when_post_then_answers_bad_request(self) -> None:
        # Given
        wiring = _Wiring()
        # When
        status, body = wiring.api.handle(METHOD_POST, PATH_RESERVATIONS, _booking({FIELD_ATTENDEES: True}))
        # Then
        self.assertEqual(status, STATUS_BAD_REQUEST)
        assert isinstance(body, dict)
        self.assertEqual(body[FIELD_CODE], CODE_BAD_REQUEST)


class CancelReservationRouteTest(unittest.TestCase):
    """Tests for DELETE /reservations/{id} (RQ-CLI-005)."""

    # RQ-CLI-005
    def test_given_confirmed_reservation_when_delete_then_answers_no_content(self) -> None:
        # Given
        wiring = _Wiring()
        reservation_id = _book(wiring)[FIELD_ID]
        # When
        status, body = wiring.api.handle(METHOD_DELETE, f"{PATH_RESERVATIONS}/{reservation_id}", None)
        # Then
        self.assertEqual(status, STATUS_NO_CONTENT)
        self.assertIsNone(body)

    # RQ-CLI-005
    def test_given_unknown_id_when_delete_then_answers_not_found_reservation_not_found(self) -> None:
        # Given
        wiring = _Wiring()
        # When
        status, body = wiring.api.handle(METHOD_DELETE, f"{PATH_RESERVATIONS}/{UNKNOWN_ID}", None)
        # Then
        self.assertEqual(status, STATUS_NOT_FOUND)
        assert isinstance(body, dict)
        self.assertEqual(body[FIELD_CODE], RESERVATION_NOT_FOUND)

    # RQ-CLI-005
    def test_given_started_reservation_when_delete_then_answers_conflict_already_started(self) -> None:
        # Given
        wiring = _Wiring()
        reservation_id = _book(wiring)[FIELD_ID]
        wiring.clock.moment = START
        # When
        status, body = wiring.api.handle(METHOD_DELETE, f"{PATH_RESERVATIONS}/{reservation_id}", None)
        # Then
        self.assertEqual(status, STATUS_CONFLICT)
        assert isinstance(body, dict)
        self.assertEqual(body[FIELD_CODE], ALREADY_STARTED)


class RoutingTest(unittest.TestCase):
    """Tests for unknown routes (RQ-CLI-005)."""

    # RQ-CLI-005
    def test_given_unknown_path_when_get_then_answers_not_found_not_found(self) -> None:
        # Given
        wiring = _Wiring()
        # When
        status, body = wiring.api.handle(METHOD_GET, UNKNOWN_PATH, None)
        # Then
        self.assertEqual(status, STATUS_NOT_FOUND)
        assert isinstance(body, dict)
        self.assertEqual(body[FIELD_CODE], CODE_NOT_FOUND)

    # RQ-CLI-005
    def test_given_wrong_method_when_called_then_answers_not_found(self) -> None:
        # Given
        wiring = _Wiring()
        # When
        status, body = wiring.api.handle(METHOD_DELETE, PATH_ROOMS, None)
        # Then
        self.assertEqual(status, STATUS_NOT_FOUND)
        assert isinstance(body, dict)
        self.assertEqual(body[FIELD_CODE], CODE_NOT_FOUND)


class ServeTest(unittest.TestCase):
    """Tests for serve, with the HTTP server replaced by a mock so that no socket is opened (RQ-CLI-005)."""

    # RQ-CLI-005
    def test_given_api_when_serve_then_server_listens_on_host_and_port_and_serves_forever(self) -> None:
        # Given
        api = _Wiring().api
        # When
        with patch.object(api_module, "ThreadingHTTPServer") as server_class:
            serve(api, HOST, PORT)
        # Then
        server_class.assert_called_once()
        self.assertEqual(server_class.call_args.args[0], (HOST, PORT))
        server_class.return_value.serve_forever.assert_called_once()
        server_class.return_value.server_close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
