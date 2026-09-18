# RQ-BKG-001, RQ-BKG-002, DEC-BKG-001 (ADR-BKG-001)
"""Domain objects of Roombook: rooms, reservation requests and reservations."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from enum import Enum

MIN_CAPACITY = 1
OPEN_BY_DEFAULT = True
CAPACITY_BELOW_MINIMUM_MESSAGE = "room capacity is below the minimum"
INVALID_INTERVAL_MESSAGE = "reservation end must be after its start"


class ReservationStatus(str, Enum):
    """Lifecycle state of a reservation (RQ-BKG-002, RQ-BKG-005)."""

    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True)
class Room:
    """A meeting room of the catalog (RQ-BKG-001)."""

    id: str
    name: str
    capacity: int
    open: bool = OPEN_BY_DEFAULT

    def __post_init__(self) -> None:
        if self.capacity < MIN_CAPACITY:
            raise ValueError(CAPACITY_BELOW_MINIMUM_MESSAGE)


@dataclass(frozen=True)
class ReservationRequest:
    """A user's request to book a room over an interval (RQ-BKG-002)."""

    room_id: str
    organizer: str
    start: datetime
    end: datetime
    attendees: int

    def __post_init__(self) -> None:
        if self.end <= self.start:
            raise ValueError(INVALID_INTERVAL_MESSAGE)


@dataclass(frozen=True)
class Reservation:
    """A booking of a room over an interval (RQ-BKG-002, RQ-BKG-003, RQ-BKG-005)."""

    id: str
    room_id: str
    organizer: str
    start: datetime
    end: datetime
    attendees: int
    status: ReservationStatus = ReservationStatus.CONFIRMED

    def overlaps(self, start: datetime, end: datetime) -> bool:
        """Return True when the interval shares time with this reservation (RQ-BKG-003)."""
        return self.start < end and start < self.end

    def cancelled(self) -> Reservation:
        """Return a copy of this reservation with the Cancelled status (RQ-BKG-005)."""
        return replace(self, status=ReservationStatus.CANCELLED)
