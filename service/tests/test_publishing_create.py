# RQ-NTF-001, DEC-NTF-001 (ADR-NTF-001)
"""Tests of the publishing decorator around the create-reservation use case."""

from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from roombook.domain import Reservation, ReservationRequest
from roombook.events import EventBus, ReservationCreated
from roombook.publishing_create import PublishingCreateReservation

RESERVATION_ID = "res-1"
ROOM_ID = "room-a"
ORGANIZER = "alice"
ATTENDEES = 4
START = datetime(2030, 5, 1, 10, 0, tzinfo=timezone.utc)
DURATION = timedelta(hours=1)
REJECTION = ValueError


class _FakeCreator:
    """Stands in for the create-reservation use case."""

    def __init__(self, fail: bool) -> None:
        self._fail = fail
        self.calls = 0

    # RQ-NTF-001
    def execute(self, request: ReservationRequest) -> Reservation:
        self.calls += 1
        if self._fail:
            raise REJECTION()
        return Reservation(
            id=RESERVATION_ID,
            room_id=request.room_id,
            organizer=request.organizer,
            start=request.start,
            end=request.end,
            attendees=request.attendees,
        )


def _request() -> ReservationRequest:
    return ReservationRequest(
        room_id=ROOM_ID,
        organizer=ORGANIZER,
        start=START,
        end=START + DURATION,
        attendees=ATTENDEES,
    )


class PublishingCreateReservationTest(unittest.TestCase):
    """Tests for PublishingCreateReservation (RQ-NTF-001, DEC-NTF-001)."""

    # RQ-NTF-001
    def test_given_subscriber_when_reservation_created_then_subscriber_receives_one_event_with_result(self) -> None:
        # Given
        received: list[object] = []
        bus = EventBus()
        bus.subscribe(received.append)
        creator = PublishingCreateReservation(_FakeCreator(fail=False), bus)
        # When
        result = creator.execute(_request())
        # Then
        self.assertEqual(len(received), 1)
        self.assertIsInstance(received[0], ReservationCreated)
        self.assertIs(received[0].reservation, result)

    # RQ-NTF-001
    def test_given_subscriber_when_reservation_created_then_result_is_returned_unchanged(self) -> None:
        # Given
        inner = _FakeCreator(fail=False)
        creator = PublishingCreateReservation(inner, EventBus())
        # When
        result = creator.execute(_request())
        # Then
        self.assertEqual(inner.calls, 1)
        self.assertEqual(result.id, RESERVATION_ID)

    # RQ-NTF-001
    def test_given_subscriber_when_request_rejected_then_nothing_is_published(self) -> None:
        # Given
        received: list[object] = []
        bus = EventBus()
        bus.subscribe(received.append)
        creator = PublishingCreateReservation(_FakeCreator(fail=True), bus)
        # When
        with self.assertRaises(REJECTION):
            creator.execute(_request())
        # Then
        self.assertEqual(received, [])


if __name__ == "__main__":
    unittest.main()
