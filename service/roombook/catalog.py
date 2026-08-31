# RQ-BKG-001, DEC-BKG-001 (ADR-BKG-001)
"""Catalog of the rooms known to the booking service."""

from __future__ import annotations

from roombook.domain import Room
from roombook.errors import RoomNotFound

DUPLICATE_ROOM_MESSAGE = "room id is already in the catalog"


class RoomCatalog:
    """Holds the rooms by identifier (RQ-BKG-001)."""

    def __init__(self) -> None:
        self._rooms: dict[str, Room] = {}

    def add(self, room: Room) -> None:
        """Add a room to the catalog; a duplicate identifier is refused (RQ-BKG-001)."""
        if room.id in self._rooms:
            raise ValueError(DUPLICATE_ROOM_MESSAGE)
        self._rooms[room.id] = room

    def get(self, room_id: str) -> Room:
        """Return the room with this identifier (RQ-BKG-001)."""
        room = self._rooms.get(room_id)
        if room is None:
            raise RoomNotFound()
        return room

    def list(self) -> list[Room]:
        """Return every room sorted by identifier (RQ-BKG-001)."""
        return sorted(self._rooms.values(), key=lambda room: room.id)
