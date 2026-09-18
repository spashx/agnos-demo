# RQ-BKG-003, RQ-BKG-004, RQ-BKG-005, RQ-BKG-006, DEC-BKG-001 (ADR-BKG-001)
"""Domain errors of Roombook, each carrying a stable machine-readable code."""

from __future__ import annotations

BASE_ERROR_CODE = "ROOMBOOK_ERROR"
BASE_ERROR_MESSAGE = "booking service error"

ROOM_NOT_FOUND = "ROOM_NOT_FOUND"
RESERVATION_NOT_FOUND = "RESERVATION_NOT_FOUND"
CONFLICT = "CONFLICT"
CAPACITY_EXCEEDED = "CAPACITY_EXCEEDED"
ROOM_CLOSED = "ROOM_CLOSED"
ALREADY_STARTED = "ALREADY_STARTED"

ROOM_NOT_FOUND_MESSAGE = "room is not in the catalog"
RESERVATION_NOT_FOUND_MESSAGE = "reservation does not exist"
CAPACITY_EXCEEDED_MESSAGE = "more attendees than the room capacity"
ROOM_CLOSED_MESSAGE = "room is closed for reservations"
ALREADY_STARTED_MESSAGE = "reservation has already started"
CONFLICT_MESSAGE_TEMPLATE = "room already booked by reservation {conflicting_id}"


class RoombookError(Exception):
    """Base error of the booking service; `code` is stable for API clients."""

    code: str = BASE_ERROR_CODE
    default_message: str = BASE_ERROR_MESSAGE

    def __init__(self, message: str | None = None) -> None:
        super().__init__(self.default_message if message is None else message)


class RoomNotFound(RoombookError):
    """The requested room is not in the catalog (RQ-BKG-001)."""

    code = ROOM_NOT_FOUND
    default_message = ROOM_NOT_FOUND_MESSAGE


class ReservationNotFound(RoombookError):
    """The requested reservation does not exist (RQ-BKG-005)."""

    code = RESERVATION_NOT_FOUND
    default_message = RESERVATION_NOT_FOUND_MESSAGE


class ReservationConflict(RoombookError):
    """The interval overlaps a Confirmed reservation of the room (RQ-BKG-003)."""

    code = CONFLICT

    def __init__(self, conflicting_id: str) -> None:
        super().__init__(CONFLICT_MESSAGE_TEMPLATE.format(conflicting_id=conflicting_id))
        self.conflicting_id = conflicting_id


class CapacityExceeded(RoombookError):
    """More attendees than the room can hold (RQ-BKG-004)."""

    code = CAPACITY_EXCEEDED
    default_message = CAPACITY_EXCEEDED_MESSAGE


class RoomClosed(RoombookError):
    """The room is flagged closed (RQ-BKG-006)."""

    code = ROOM_CLOSED
    default_message = ROOM_CLOSED_MESSAGE


class ReservationAlreadyStarted(RoombookError):
    """The reservation started, so it can no longer be cancelled (RQ-BKG-005)."""

    code = ALREADY_STARTED
    default_message = ALREADY_STARTED_MESSAGE
