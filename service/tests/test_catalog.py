# RQ-BKG-001, DEC-BKG-001 (ADR-BKG-001)
"""Unit tests of the room catalog."""

from __future__ import annotations

import unittest

from roombook.catalog import RoomCatalog
from roombook.domain import Room
from roombook.errors import ROOM_NOT_FOUND, RoomNotFound

FIRST_ROOM_ID = "room-b"
FIRST_ROOM_NAME = "Beta"
FIRST_ROOM_CAPACITY = 8
SECOND_ROOM_ID = "room-a"
SECOND_ROOM_NAME = "Alpha"
SECOND_ROOM_CAPACITY = 4
CLOSED_FLAG = False
UNKNOWN_ROOM_ID = "room-missing"


class RoomCatalogTest(unittest.TestCase):
    """Tests of RoomCatalog (RQ-BKG-001)."""

    # RQ-BKG-001
    def setUp(self) -> None:
        self.first_room = Room(id=FIRST_ROOM_ID, name=FIRST_ROOM_NAME, capacity=FIRST_ROOM_CAPACITY)
        self.second_room = Room(
            id=SECOND_ROOM_ID, name=SECOND_ROOM_NAME, capacity=SECOND_ROOM_CAPACITY, open=CLOSED_FLAG
        )
        self.catalog = RoomCatalog()

    # RQ-BKG-001
    def test_given_two_rooms_added_when_catalog_listed_then_each_room_is_returned_with_its_fields(self) -> None:
        # Given
        self.catalog.add(self.first_room)
        self.catalog.add(self.second_room)
        # When
        rooms = self.catalog.list()
        # Then
        self.assertEqual(rooms, [self.second_room, self.first_room])

    # RQ-BKG-001
    def test_given_room_in_catalog_when_get_then_room_is_returned(self) -> None:
        # Given
        self.catalog.add(self.first_room)
        # When
        room = self.catalog.get(FIRST_ROOM_ID)
        # Then
        self.assertEqual(room, self.first_room)

    # RQ-BKG-001
    def test_given_unknown_identifier_when_get_then_room_not_found_is_raised(self) -> None:
        # Given
        self.catalog.add(self.first_room)
        # When
        with self.assertRaises(RoomNotFound) as context:
            self.catalog.get(UNKNOWN_ROOM_ID)
        # Then
        self.assertEqual(context.exception.code, ROOM_NOT_FOUND)

    # RQ-BKG-001
    def test_given_room_already_in_catalog_when_added_again_then_value_error_is_raised(self) -> None:
        # Given
        self.catalog.add(self.first_room)
        # When
        with self.assertRaises(ValueError):
            self.catalog.add(self.first_room)
        # Then
        # the ValueError above is the expected outcome


if __name__ == "__main__":
    unittest.main()
