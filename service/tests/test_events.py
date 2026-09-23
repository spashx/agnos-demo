# RQ-NTF-001, DEC-NTF-001 (ADR-NTF-001)
"""Tests of the in-process event bus and the reservation-created event."""

from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from roombook.domain import Reservation
from roombook.events import LOGGER_NAME, EventBus, ReservationCreated

RESERVATION_ID = "res-1"
ROOM_ID = "room-a"
ORGANIZER = "alice"
ATTENDEES = 4
START = datetime(2030, 5, 1, 10, 0, tzinfo=timezone.utc)
DURATION = timedelta(hours=1)


def _reservation() -> Reservation:
    return Reservation(
        id=RESERVATION_ID,
        room_id=ROOM_ID,
        organizer=ORGANIZER,
        start=START,
        end=START + DURATION,
        attendees=ATTENDEES,
    )


class EventBusTest(unittest.TestCase):
    """Tests for EventBus (RQ-NTF-001, DEC-NTF-001)."""

    # RQ-NTF-001
    def test_given_subscriber_when_event_published_then_subscriber_receives_one_event_with_reservation(self) -> None:
        # Given
        bus = EventBus()
        received: list[object] = []
        bus.subscribe(received.append)
        reservation = _reservation()
        # When
        bus.publish(ReservationCreated(reservation))
        # Then
        self.assertEqual(len(received), 1)
        self.assertIsInstance(received[0], ReservationCreated)
        self.assertIs(received[0].reservation, reservation)

    # RQ-NTF-001
    def test_given_no_subscriber_when_event_published_then_nothing_fails(self) -> None:
        # Given
        bus = EventBus()
        # When
        bus.publish(ReservationCreated(_reservation()))
        # Then
        # no exception reaches the test: publishing without subscribers is a no-op

    # RQ-NTF-001
    def test_given_failing_subscriber_when_event_published_then_other_subscribers_still_receive_it(self) -> None:
        # Given
        bus = EventBus()
        received: list[object] = []

        # RQ-NTF-001
        def failing(event: object) -> None:
            raise RuntimeError(ORGANIZER)

        bus.subscribe(failing)
        bus.subscribe(received.append)
        # When
        with self.assertLogs(LOGGER_NAME, level="ERROR"):
            bus.publish(ReservationCreated(_reservation()))
        # Then
        self.assertEqual(len(received), 1)

    # RQ-NTF-001
    def test_given_failing_subscriber_when_event_published_then_failure_is_logged(self) -> None:
        # Given
        bus = EventBus()

        # RQ-NTF-001
        def failing(event: object) -> None:
            raise RuntimeError(ORGANIZER)

        bus.subscribe(failing)
        # When
        with self.assertLogs(LOGGER_NAME, level="ERROR") as logs:
            bus.publish(ReservationCreated(_reservation()))
        # Then
        self.assertEqual(len(logs.records), 1)


if __name__ == "__main__":
    unittest.main()
