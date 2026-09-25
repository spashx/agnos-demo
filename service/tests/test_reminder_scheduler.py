# RQ-NTF-002, RQ-NTF-004, DEC-NTF-002 (ADR-NTF-001)
"""Tests of the reminder scheduler."""

from __future__ import annotations

import time
import unittest
from datetime import datetime, timedelta, timezone

from roombook.domain import Reservation
from roombook.memory_repository import InMemoryReservationRepository
from roombook.reminder_scheduler import REMINDER_LEAD_MINUTES, ReminderScheduler

ROOM_ID = "room-a"
ORGANIZER = "alice"
ATTENDEES = 4
START = datetime(2030, 5, 1, 10, 0, tzinfo=timezone.utc)
DURATION = timedelta(hours=1)
LEAD = timedelta(minutes=REMINDER_LEAD_MINUTES)
BULK_COUNT = 1000
MAX_DISPATCH_SECONDS = 1.0
FIRST_ID = "res-1"
SECOND_ID = "res-2"


class _FixedClock:
    """Clock whose time the test sets."""

    def __init__(self, moment: datetime) -> None:
        self.moment = moment

    # RQ-NTF-002
    def now(self) -> datetime:
        return self.moment


class _RecordingNotifier:
    """Notifier that records every send."""

    def __init__(self) -> None:
        self.sent: list[tuple[str, str]] = []

    # RQ-NTF-002
    def send(self, recipient: str, message: str) -> None:
        self.sent.append((recipient, message))


def _reservation(reservation_id: str, start: datetime = START) -> Reservation:
    return Reservation(
        id=reservation_id,
        room_id=ROOM_ID,
        organizer=ORGANIZER,
        start=start,
        end=start + DURATION,
        attendees=ATTENDEES,
    )


class ReminderSchedulerTest(unittest.TestCase):
    """Tests for ReminderScheduler.dispatch_due (RQ-NTF-002, RQ-NTF-004)."""

    # RQ-NTF-002
    def test_given_confirmed_reservation_when_clock_reaches_lead_time_then_one_reminder_is_sent_to_organizer(
        self,
    ) -> None:
        # Given
        repository = InMemoryReservationRepository()
        repository.add(_reservation(FIRST_ID))
        notifier = _RecordingNotifier()
        scheduler = ReminderScheduler(repository, notifier, _FixedClock(START - LEAD))
        # When
        sent = scheduler.dispatch_due()
        # Then
        self.assertEqual(sent, 1)
        self.assertEqual(len(notifier.sent), 1)
        self.assertEqual(notifier.sent[0][0], ORGANIZER)

    # RQ-NTF-002
    def test_given_reminder_already_sent_when_dispatch_again_then_no_second_reminder_is_sent(self) -> None:
        # Given
        repository = InMemoryReservationRepository()
        repository.add(_reservation(FIRST_ID))
        notifier = _RecordingNotifier()
        scheduler = ReminderScheduler(repository, notifier, _FixedClock(START - LEAD))
        scheduler.dispatch_due()
        # When
        sent = scheduler.dispatch_due()
        # Then
        self.assertEqual(sent, 0)
        self.assertEqual(len(notifier.sent), 1)

    # RQ-NTF-002
    def test_given_clock_before_lead_time_when_dispatch_then_no_reminder_is_sent(self) -> None:
        # Given
        repository = InMemoryReservationRepository()
        repository.add(_reservation(FIRST_ID))
        notifier = _RecordingNotifier()
        scheduler = ReminderScheduler(repository, notifier, _FixedClock(START - LEAD - timedelta(seconds=1)))
        # When
        sent = scheduler.dispatch_due()
        # Then
        self.assertEqual(sent, 0)
        self.assertEqual(notifier.sent, [])

    # RQ-NTF-002
    def test_given_clock_at_start_when_dispatch_then_no_reminder_is_sent(self) -> None:
        # Given
        repository = InMemoryReservationRepository()
        repository.add(_reservation(FIRST_ID))
        notifier = _RecordingNotifier()
        scheduler = ReminderScheduler(repository, notifier, _FixedClock(START))
        # When
        sent = scheduler.dispatch_due()
        # Then
        self.assertEqual(sent, 0)

    # RQ-NTF-002
    def test_given_cancelled_reservation_when_lead_time_reached_then_no_reminder_is_sent(self) -> None:
        # Given
        repository = InMemoryReservationRepository()
        repository.add(_reservation(FIRST_ID).cancelled())
        notifier = _RecordingNotifier()
        scheduler = ReminderScheduler(repository, notifier, _FixedClock(START - LEAD))
        # When
        sent = scheduler.dispatch_due()
        # Then
        self.assertEqual(sent, 0)
        self.assertEqual(notifier.sent, [])

    # RQ-NTF-004
    def test_given_1000_due_reminders_when_dispatched_then_elapsed_time_is_below_limit(self) -> None:
        # Given
        repository = InMemoryReservationRepository()
        for index in range(BULK_COUNT):
            repository.add(_reservation(f"{FIRST_ID}-{index}"))
        notifier = _RecordingNotifier()
        scheduler = ReminderScheduler(repository, notifier, _FixedClock(START - LEAD))
        # When
        began = time.perf_counter()
        sent = scheduler.dispatch_due()
        elapsed = time.perf_counter() - began
        # Then
        self.assertEqual(sent, BULK_COUNT)
        self.assertLess(elapsed, MAX_DISPATCH_SECONDS)


if __name__ == "__main__":
    unittest.main()
