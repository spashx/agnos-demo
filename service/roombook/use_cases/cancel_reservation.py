# RQ-BKG-005, DEC-BKG-001 (ADR-BKG-001)
"""Use case that cancels a reservation which has not started yet (RQ-BKG-005)."""

from __future__ import annotations

from roombook.domain import Reservation, ReservationStatus
from roombook.errors import ReservationAlreadyStarted
from roombook.ports import Clock, ReservationRepository


class CancelReservation:
    """Marks a reservation Cancelled before its start (RQ-BKG-005)."""

    def __init__(self, repository: ReservationRepository, clock: Clock) -> None:
        self._repository = repository
        self._clock = clock

    def execute(self, reservation_id: str) -> Reservation:
        """Cancel the reservation, or return it unchanged when already Cancelled (RQ-BKG-005)."""
        reservation = self._repository.get(reservation_id)
        if reservation.status is ReservationStatus.CANCELLED:
            return reservation
        if self._clock.now() >= reservation.start:
            raise ReservationAlreadyStarted()
        cancelled = reservation.cancelled()
        self._repository.update(cancelled)
        return cancelled
