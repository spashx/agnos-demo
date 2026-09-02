# RQ-BKG-002, RQ-BKG-003, RQ-BKG-005, DEC-BKG-003 (ADR-BKG-002)
"""In-memory adapter of the reservation repository (DEC-BKG-003)."""

from __future__ import annotations

from roombook.domain import Reservation, ReservationStatus
from roombook.errors import ReservationNotFound
from roombook.ports import ReservationRepository


class InMemoryReservationRepository(ReservationRepository):
    """Keeps reservations in a dictionary keyed by identifier (DEC-BKG-003)."""

    def __init__(self) -> None:
        self._reservations: dict[str, Reservation] = {}

    def add(self, reservation: Reservation) -> None:
        """Store a new reservation (RQ-BKG-002)."""
        self._reservations[reservation.id] = reservation

    def get(self, reservation_id: str) -> Reservation:
        """Return the reservation, raising ReservationNotFound when absent (RQ-BKG-005)."""
        reservation = self._reservations.get(reservation_id)
        if reservation is None:
            raise ReservationNotFound()
        return reservation

    def update(self, reservation: Reservation) -> None:
        """Replace a stored reservation, raising ReservationNotFound when absent (RQ-BKG-005)."""
        self.get(reservation.id)
        self._reservations[reservation.id] = reservation

    def list_confirmed_for_room(self, room_id: str) -> list[Reservation]:
        """Return the Confirmed reservations of a room (RQ-BKG-003)."""
        return [
            reservation
            for reservation in self._reservations.values()
            if reservation.room_id == room_id and reservation.status is ReservationStatus.CONFIRMED
        ]

    def list_all(self) -> list[Reservation]:
        """Return every stored reservation (RQ-BKG-002)."""
        return list(self._reservations.values())
