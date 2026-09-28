# RQ-NTF-002, RQ-NTF-004, DEC-NTF-002 (ADR-NTF-001)
"""Reminder scheduler: sends one reminder per Confirmed reservation entering its lead time."""

from __future__ import annotations

from datetime import timedelta

from roombook.domain import ReservationStatus
from roombook.notifier import Notifier
from roombook.ports import Clock, ReservationRepository

REMINDER_LEAD_MINUTES = 10
REMINDER_MESSAGE_TEMPLATE = "reservation {reservation_id} starts at {start}"


class ReminderScheduler:
    """Sends one reminder to the organizer when the lead time of a reservation is reached (RQ-NTF-002)."""

    def __init__(self, repository: ReservationRepository, notifier: Notifier, clock: Clock) -> None:
        self._repository = repository
        self._notifier = notifier
        self._clock = clock
        self._reminded: set[str] = set()

    def dispatch_due(self) -> int:
        """Send the reminders that are due now and return how many were sent (RQ-NTF-002, RQ-NTF-004)."""
        now = self._clock.now()
        lead = timedelta(minutes=REMINDER_LEAD_MINUTES)
        sent = 0
        for reservation in self._repository.list_all():
            if reservation.status is not ReservationStatus.CONFIRMED or reservation.id in self._reminded:
                continue
            if not reservation.start - lead <= now < reservation.start:
                continue
            message = REMINDER_MESSAGE_TEMPLATE.format(
                reservation_id=reservation.id,
                start=reservation.start.isoformat(),
            )
            self._notifier.send(reservation.organizer, message)
            self._reminded.add(reservation.id)
            sent += 1
        return sent
