# RQ-BKG-002, DEC-BKG-001, DEC-BKG-002 (ADR-BKG-001)
"""Use case that creates a Confirmed reservation after running every validity rule."""

from __future__ import annotations

import uuid
from collections.abc import Callable, Sequence

from roombook.catalog import RoomCatalog
from roombook.domain import Reservation, ReservationRequest, ReservationStatus
from roombook.ports import ReservationRepository
from roombook.rules import ReservationRule


def uuid_id_factory() -> str:
    """Return a new UUID string to identify a reservation (RQ-BKG-002)."""
    return str(uuid.uuid4())


class CreateReservation:
    """Creates a Confirmed reservation of a room (RQ-BKG-002)."""

    def __init__(
        self,
        catalog: RoomCatalog,
        repository: ReservationRepository,
        rules: Sequence[ReservationRule],
        id_factory: Callable[[], str] = uuid_id_factory,
    ) -> None:
        self._catalog = catalog
        self._repository = repository
        self._rules = tuple(rules)
        self._id_factory = id_factory

    def execute(self, request: ReservationRequest) -> Reservation:
        """Run the rules in order, store the reservation and return it (RQ-BKG-002, DEC-BKG-002)."""
        room = self._catalog.get(request.room_id)
        existing = self._repository.list_confirmed_for_room(room.id)
        for rule in self._rules:
            rule.check(room, request, existing)
        reservation = Reservation(
            id=self._id_factory(),
            room_id=request.room_id,
            organizer=request.organizer,
            start=request.start,
            end=request.end,
            attendees=request.attendees,
            status=ReservationStatus.CONFIRMED,
        )
        self._repository.add(reservation)
        return reservation
