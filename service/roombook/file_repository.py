# RQ-BKG-002, RQ-BKG-005, RQ-BKG-007, DEC-BKG-004 (ADR-BKG-003)
"""JSON file adapter of the reservation repository, rewritten atomically on every change (DEC-BKG-004)."""

from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import datetime
from pathlib import Path
from typing import Any

from roombook.atomic_file import write_atomically
from roombook.domain import Reservation, ReservationStatus
from roombook.errors import ReservationNotFound, RoombookError
from roombook.ports import ReservationRepository

STORAGE_CORRUPTED = "STORAGE_CORRUPTED"
STORAGE_CORRUPTED_MESSAGE = "reservation data file is corrupted"
JSON_INDENT = 2
JSON_ENCODING = "utf-8"
KEY_RESERVATIONS = "reservations"
KEY_ID = "id"
KEY_ROOM_ID = "roomId"
KEY_ORGANIZER = "organizer"
KEY_START = "start"
KEY_END = "end"
KEY_ATTENDEES = "attendees"
KEY_STATUS = "status"


class StorageCorrupted(RoombookError):
    """The data file cannot be read as reservations (DEC-BKG-004)."""

    code = STORAGE_CORRUPTED
    default_message = STORAGE_CORRUPTED_MESSAGE


def _reservation_to_json(reservation: Reservation) -> dict[str, Any]:
    """Serialize a reservation to its JSON record (RQ-BKG-007)."""
    return {
        KEY_ID: reservation.id,
        KEY_ROOM_ID: reservation.room_id,
        KEY_ORGANIZER: reservation.organizer,
        KEY_START: reservation.start.isoformat(),
        KEY_END: reservation.end.isoformat(),
        KEY_ATTENDEES: reservation.attendees,
        KEY_STATUS: reservation.status.value,
    }


def _reservation_from_json(record: Mapping[str, Any]) -> Reservation:
    """Deserialize a JSON record to a reservation (RQ-BKG-007)."""
    return Reservation(
        id=record[KEY_ID],
        room_id=record[KEY_ROOM_ID],
        organizer=record[KEY_ORGANIZER],
        start=datetime.fromisoformat(record[KEY_START]),
        end=datetime.fromisoformat(record[KEY_END]),
        attendees=int(record[KEY_ATTENDEES]),
        status=ReservationStatus(record[KEY_STATUS]),
    )


def _load(path: Path) -> dict[str, Reservation]:
    """Read every reservation of the data file; a missing file means none (RQ-BKG-007)."""
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding=JSON_ENCODING))
        records = payload[KEY_RESERVATIONS]
        reservations = [_reservation_from_json(record) for record in records]
    except (KeyError, TypeError, ValueError):
        raise StorageCorrupted() from None
    return {reservation.id: reservation for reservation in reservations}


class FileReservationRepository(ReservationRepository):
    """Reservations stored in one JSON file, rewritten atomically on every change (DEC-BKG-004)."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._reservations = _load(path)

    def add(self, reservation: Reservation) -> None:
        """Store a new reservation and save the file (RQ-BKG-002, RQ-BKG-007)."""
        self._commit({**self._reservations, reservation.id: reservation})

    def get(self, reservation_id: str) -> Reservation:
        """Return the reservation, raising ReservationNotFound when absent (RQ-BKG-005)."""
        reservation = self._reservations.get(reservation_id)
        if reservation is None:
            raise ReservationNotFound()
        return reservation

    def update(self, reservation: Reservation) -> None:
        """Replace a stored reservation and save the file (RQ-BKG-005, RQ-BKG-007)."""
        self.get(reservation.id)
        self._commit({**self._reservations, reservation.id: reservation})

    def list_confirmed_for_room(self, room_id: str) -> list[Reservation]:
        """Return the Confirmed reservations of a room (RQ-BKG-003)."""
        return [
            reservation
            for reservation in self._reservations.values()
            if reservation.room_id == room_id and reservation.status is ReservationStatus.CONFIRMED
        ]

    def list_all(self) -> list[Reservation]:
        """Return every stored reservation (RQ-BKG-007)."""
        return list(self._reservations.values())

    def _commit(self, reservations: dict[str, Reservation]) -> None:
        """Save the new state to the file, then keep it in memory (DEC-BKG-004)."""
        payload = {KEY_RESERVATIONS: [_reservation_to_json(item) for item in reservations.values()]}
        write_atomically(self._path, json.dumps(payload, indent=JSON_INDENT))
        self._reservations = reservations
