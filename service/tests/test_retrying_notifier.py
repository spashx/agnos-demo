# RQ-NTF-003, DEC-NTF-002 (ADR-NTF-001)
"""Tests of the retrying notifier decorator."""

from __future__ import annotations

import logging
import unittest
from datetime import datetime, timedelta, timezone

from roombook.domain import Reservation, ReservationStatus
from roombook.memory_repository import InMemoryReservationRepository
from roombook.reminder_scheduler import ReminderScheduler
from roombook.retrying_notifier import LOG_DELIVERY_FAILED, LOGGER_NAME, MAX_ATTEMPTS, RetryingNotifier

RECIPIENT = "alice"
MESSAGE = "your meeting starts soon"
ROOM_ID = "room-a"
ATTENDEES = 4
START = datetime(2030, 5, 1, 10, 0, tzinfo=timezone.utc)
DURATION = timedelta(hours=1)
RESERVATION_ID = "res-1"
LEAD_TIME_CLOCK = START - timedelta(minutes=15)


class _FailingNotifier:
    """Notifier whose every attempt fails, counting the attempts."""

    def __init__(self) -> None:
        self.attempts = 0

    # RQ-NTF-003
    def send(self, recipient: str, message: str) -> None:
        self.attempts += 1
        raise OSError(recipient)


class _FlakyNotifier:
    """Notifier that fails a fixed number of times, then succeeds."""

    def __init__(self, failures: int) -> None:
        self._failures = failures
        self.attempts = 0

    # RQ-NTF-003
    def send(self, recipient: str, message: str) -> None:
        self.attempts += 1
        if self.attempts <= self._failures:
            raise OSError(recipient)


class _FixedClock:
    def __init__(self, moment: datetime) -> None:
        self._moment = moment

    # RQ-NTF-003
    def now(self) -> datetime:
        return self._moment


class RetryingNotifierTest(unittest.TestCase):
    """Tests for RetryingNotifier.send (RQ-NTF-003)."""

    def test_given_notifier_failing_every_time_when_send_then_max_attempts_are_made(self) -> None:
        # Given
        inner = _FailingNotifier()
        notifier = RetryingNotifier(inner)
        # When
        with self.assertLogs(LOGGER_NAME, level=logging.ERROR):
            notifier.send(RECIPIENT, MESSAGE)
        # Then
        self.assertEqual(inner.attempts, MAX_ATTEMPTS)

    # RQ-NTF-003
    def test_given_notifier_failing_every_time_when_send_then_one_failure_is_logged(self) -> None:
        # Given
        notifier = RetryingNotifier(_FailingNotifier())
        # When
        with self.assertLogs(LOGGER_NAME, level=logging.ERROR) as logs:
            notifier.send(RECIPIENT, MESSAGE)
        # Then
        self.assertEqual(len(logs.records), 1)
        self.assertEqual(logs.records[0].msg, LOG_DELIVERY_FAILED)

    # RQ-NTF-003
    def test_given_notifier_failing_every_time_when_send_then_no_error_reaches_caller(self) -> None:
        # Given
        inner = _FailingNotifier()
        notifier = RetryingNotifier(inner)
        # When
        with self.assertLogs(LOGGER_NAME, level=logging.ERROR):
            notifier.send(RECIPIENT, MESSAGE)
        # Then
        self.assertEqual(inner.attempts, MAX_ATTEMPTS)

    # RQ-NTF-003
    def test_given_notifier_failing_once_when_send_then_retry_succeeds_without_logging(self) -> None:
        # Given
        inner = _FlakyNotifier(failures=1)
        notifier = RetryingNotifier(inner)
        # When
        with self.assertNoLogs(LOGGER_NAME, level=logging.ERROR):
            notifier.send(RECIPIENT, MESSAGE)
        # Then
        self.assertEqual(inner.attempts, 2)

    # RQ-NTF-003
    def test_given_failing_reminder_when_dispatched_then_reservation_stays_confirmed(self) -> None:
        # Given
        repository = InMemoryReservationRepository()
        repository.add(
            Reservation(
                id=RESERVATION_ID,
                room_id=ROOM_ID,
                organizer=RECIPIENT,
                start=START,
                end=START + DURATION,
                attendees=ATTENDEES,
            )
        )
        inner = _FailingNotifier()
        scheduler = ReminderScheduler(repository, RetryingNotifier(inner), _FixedClock(LEAD_TIME_CLOCK))
        # When
        with self.assertLogs(LOGGER_NAME, level=logging.ERROR):
            sent = scheduler.dispatch_due()
        # Then
        self.assertEqual(sent, 1)
        self.assertEqual(inner.attempts, MAX_ATTEMPTS)
        self.assertEqual(repository.get(RESERVATION_ID).status, ReservationStatus.CONFIRMED)


if __name__ == "__main__":
    unittest.main()
