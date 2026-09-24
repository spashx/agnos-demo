# RQ-NTF-001, DEC-NTF-001 (ADR-NTF-001)
"""Decorator that publishes the reservation-created event after a successful creation."""

from __future__ import annotations

from typing import Protocol

from roombook.domain import Reservation, ReservationRequest
from roombook.events import EventBus, ReservationCreated


class ReservationCreator(Protocol):
    """Anything that creates a reservation from a request (DEC-NTF-001)."""

    def execute(self, request: ReservationRequest) -> Reservation:
        """Create the reservation or raise (RQ-BKG-002)."""
        ...


class PublishingCreateReservation:
    """Wraps a creator and publishes ReservationCreated after it succeeds (RQ-NTF-001, DEC-NTF-001)."""

    def __init__(self, inner: ReservationCreator, bus: EventBus) -> None:
        self._inner = inner
        self._bus = bus

    def execute(self, request: ReservationRequest) -> Reservation:
        """Create through the inner use case; publish only when it returns (RQ-NTF-001)."""
        reservation = self._inner.execute(request)
        self._bus.publish(ReservationCreated(reservation))
        return reservation
