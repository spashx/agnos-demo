# RQ-CLI-005, DEC-CLI-001 (ADR-CLI-001)
"""HTTP/JSON adapter: translates HTTP requests to use cases and domain errors to status and body."""

from __future__ import annotations

import json
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Protocol

from roombook.catalog import RoomCatalog
from roombook.domain import Reservation, ReservationRequest, Room
from roombook.errors import (
    ALREADY_STARTED,
    CAPACITY_EXCEEDED,
    CONFLICT,
    RESERVATION_NOT_FOUND,
    ROOM_CLOSED,
    ROOM_NOT_FOUND,
    RoombookError,
)
from roombook.publishing_create import ReservationCreator

JsonValue = dict[str, Any] | list[Any] | None

METHOD_GET = "GET"
METHOD_POST = "POST"
METHOD_DELETE = "DELETE"
PATH_SEPARATOR = "/"
QUERY_SEPARATOR = "?"
SEGMENT_ROOMS = "rooms"
SEGMENT_RESERVATIONS = "reservations"
RESERVATION_ID_INDEX = 1
RESERVATION_PATH_LENGTH = 2

FIELD_ID = "id"
FIELD_NAME = "name"
FIELD_CAPACITY = "capacity"
FIELD_OPEN = "open"
FIELD_ROOM_ID = "roomId"
FIELD_ORGANIZER = "organizer"
FIELD_START = "start"
FIELD_END = "end"
FIELD_ATTENDEES = "attendees"
FIELD_STATUS = "status"
FIELD_CODE = "code"
FIELD_MESSAGE = "message"

CODE_BAD_REQUEST = "BAD_REQUEST"
CODE_NOT_FOUND = "NOT_FOUND"
MESSAGE_BAD_REQUEST = "request body is invalid"
MESSAGE_UNKNOWN_ROUTE = "no route for this method and path"

STATUS_OK = 200
STATUS_CREATED = 201
STATUS_NO_CONTENT = 204
STATUS_BAD_REQUEST = 400
STATUS_NOT_FOUND = 404
STATUS_CONFLICT = 409
STATUS_UNPROCESSABLE = 422
STATUS_INTERNAL_ERROR = 500

ERROR_STATUS: dict[str, int] = {
    ROOM_NOT_FOUND: STATUS_NOT_FOUND,
    RESERVATION_NOT_FOUND: STATUS_NOT_FOUND,
    CONFLICT: STATUS_CONFLICT,
    ALREADY_STARTED: STATUS_CONFLICT,
    CAPACITY_EXCEEDED: STATUS_UNPROCESSABLE,
    ROOM_CLOSED: STATUS_UNPROCESSABLE,
    CODE_BAD_REQUEST: STATUS_BAD_REQUEST,
    CODE_NOT_FOUND: STATUS_NOT_FOUND,
}

HEADER_CONTENT_TYPE = "Content-Type"
HEADER_CONTENT_LENGTH = "Content-Length"
CONTENT_TYPE_JSON = "application/json"
ENCODING = "utf-8"
EMPTY_LENGTH = 0


class ReservationCanceller(Protocol):
    """Anything that cancels a reservation by identifier (RQ-CLI-005)."""

    def execute(self, reservation_id: str) -> Reservation:
        """Cancel the reservation or raise a domain error (RQ-BKG-005)."""
        ...


class BadRequest(RoombookError):
    """The request body is missing a field or has a wrong value (RQ-CLI-005)."""

    code = CODE_BAD_REQUEST


class UnknownRoute(RoombookError):
    """No route matches the method and path (RQ-CLI-005)."""

    code = CODE_NOT_FOUND


class ReservationApi:
    """Maps HTTP-like calls to use cases and back, without any transport (RQ-CLI-005, DEC-CLI-001)."""

    def __init__(self, catalog: RoomCatalog, create: ReservationCreator, cancel: ReservationCanceller) -> None:
        self._catalog = catalog
        self._create = create
        self._cancel = cancel

    def handle(self, method: str, path: str, body: object) -> tuple[int, JsonValue]:
        """Answer one request with a status and a JSON-compatible body (RQ-CLI-005, DEC-CLI-001)."""
        segments = _segments(path)
        try:
            return self._route(method, segments, body)
        except RoombookError as error:
            status = ERROR_STATUS.get(error.code, STATUS_INTERNAL_ERROR)
            return status, {FIELD_CODE: error.code, FIELD_MESSAGE: str(error)}

    # RQ-CLI-005
    def _route(self, method: str, segments: list[str], body: object) -> tuple[int, JsonValue]:
        if method == METHOD_GET and segments == [SEGMENT_ROOMS]:
            return STATUS_OK, [_room_json(room) for room in self._catalog.list()]
        if method == METHOD_POST and segments == [SEGMENT_RESERVATIONS]:
            reservation = self._create.execute(_parse_request(body))
            return STATUS_CREATED, _reservation_json(reservation)
        if method == METHOD_DELETE and _is_reservation_path(segments):
            self._cancel.execute(segments[RESERVATION_ID_INDEX])
            return STATUS_NO_CONTENT, None
        raise UnknownRoute(MESSAGE_UNKNOWN_ROUTE)


def _segments(path: str) -> list[str]:
    """Split a path into its non-empty segments, ignoring any query string (RQ-CLI-005)."""
    bare = path.partition(QUERY_SEPARATOR)[0]
    return [segment for segment in bare.split(PATH_SEPARATOR) if segment]


# RQ-CLI-005
def _is_reservation_path(segments: list[str]) -> bool:
    return len(segments) == RESERVATION_PATH_LENGTH and segments[0] == SEGMENT_RESERVATIONS


# RQ-CLI-005
def _room_json(room: Room) -> dict[str, Any]:
    return {FIELD_ID: room.id, FIELD_NAME: room.name, FIELD_CAPACITY: room.capacity, FIELD_OPEN: room.open}


# RQ-CLI-005
def _reservation_json(reservation: Reservation) -> dict[str, Any]:
    return {
        FIELD_ID: reservation.id,
        FIELD_ROOM_ID: reservation.room_id,
        FIELD_ORGANIZER: reservation.organizer,
        FIELD_START: reservation.start.isoformat(),
        FIELD_END: reservation.end.isoformat(),
        FIELD_ATTENDEES: reservation.attendees,
        FIELD_STATUS: reservation.status.value,
    }


def _parse_request(body: object) -> ReservationRequest:
    """Build a ReservationRequest from a JSON object; invalid input raises BadRequest (RQ-CLI-005)."""
    if not isinstance(body, dict):
        raise BadRequest(MESSAGE_BAD_REQUEST)
    try:
        return ReservationRequest(
            room_id=_text(body, FIELD_ROOM_ID),
            organizer=_text(body, FIELD_ORGANIZER),
            start=_moment(body, FIELD_START),
            end=_moment(body, FIELD_END),
            attendees=_count(body, FIELD_ATTENDEES),
        )
    except ValueError as error:
        raise BadRequest(MESSAGE_BAD_REQUEST) from error


# RQ-CLI-005
def _field(body: dict[str, Any], key: str) -> Any:
    if key not in body:
        raise BadRequest(MESSAGE_BAD_REQUEST)
    return body[key]


# RQ-CLI-005
def _text(body: dict[str, Any], key: str) -> str:
    value = _field(body, key)
    if not isinstance(value, str):
        raise BadRequest(MESSAGE_BAD_REQUEST)
    return value


# RQ-CLI-005
def _count(body: dict[str, Any], key: str) -> int:
    value = _field(body, key)
    if not isinstance(value, int) or isinstance(value, bool):
        raise BadRequest(MESSAGE_BAD_REQUEST)
    return value


def _moment(body: dict[str, Any], key: str) -> datetime:
    """Parse an ISO 8601 text that carries a UTC offset (RQ-CLI-005, DEC-CLI-001)."""
    value = _text(body, key)
    try:
        moment = datetime.fromisoformat(value)
    except ValueError as error:
        raise BadRequest(MESSAGE_BAD_REQUEST) from error
    if moment.utcoffset() is None:
        raise BadRequest(MESSAGE_BAD_REQUEST)
    return moment


def _make_handler(api: ReservationApi) -> type[BaseHTTPRequestHandler]:
    """Build the request handler class bound to one ReservationApi (RQ-CLI-005)."""

    class _RoombookHandler(BaseHTTPRequestHandler):
        """Translates HTTP to ReservationApi.handle and back, JSON in and JSON out (RQ-CLI-005)."""

        # RQ-CLI-005
        def do_GET(self) -> None:
            self._respond(METHOD_GET)

        # RQ-CLI-005
        def do_POST(self) -> None:
            self._respond(METHOD_POST)

        # RQ-CLI-005
        def do_DELETE(self) -> None:
            self._respond(METHOD_DELETE)

        # RQ-CLI-005
        def _respond(self, method: str) -> None:
            status, payload = api.handle(method, self.path, self._read_json())
            raw = b"" if payload is None else json.dumps(payload).encode(ENCODING)
            self.send_response(status)
            self.send_header(HEADER_CONTENT_TYPE, CONTENT_TYPE_JSON)
            self.send_header(HEADER_CONTENT_LENGTH, str(len(raw)))
            self.end_headers()
            if raw:
                self.wfile.write(raw)

        # RQ-CLI-005
        def _read_json(self) -> object:
            length = int(self.headers.get(HEADER_CONTENT_LENGTH, EMPTY_LENGTH))
            raw = self.rfile.read(length) if length else b""
            if not raw:
                return None
            try:
                return json.loads(raw)
            except ValueError:
                return None

    return _RoombookHandler


def serve(api: ReservationApi, host: str, port: int) -> None:
    """Run the HTTP server until interrupted; it only translates HTTP to ReservationApi.handle (RQ-CLI-005)."""
    server = ThreadingHTTPServer((host, port), _make_handler(api))
    try:
        server.serve_forever()
    finally:
        server.server_close()
