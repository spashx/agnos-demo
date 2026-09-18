# RQ-BKG-002, RQ-BKG-005, DEC-BKG-001 (ADR-BKG-001)
"""Ports: the interfaces that use cases depend on, implemented by adapters (DEC-BKG-001)."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol

from roombook.domain import Reservation


class ReservationRepository(Protocol):
    """Storage of reservations (RQ-BKG-002, RQ-BKG-005, DEC-BKG-001)."""

    def add(self, reservation: Reservation) -> None:
        """Store a new reservation (RQ-BKG-002)."""

    def get(self, reservation_id: str) -> Reservation:
        """Return the reservation, raising ReservationNotFound when absent (RQ-BKG-005)."""

    def update(self, reservation: Reservation) -> None:
        """Replace a stored reservation, raising ReservationNotFound when absent (RQ-BKG-005)."""

    def list_confirmed_for_room(self, room_id: str) -> list[Reservation]:
        """Return the Confirmed reservations of a room (RQ-BKG-003)."""

    def list_all(self) -> list[Reservation]:
        """Return every stored reservation (RQ-BKG-002)."""


class Clock(Protocol):
    """Source of the current time (RQ-BKG-005, DEC-BKG-001)."""

    def now(self) -> datetime:
        """Return the current timezone-aware time (RQ-BKG-005)."""
