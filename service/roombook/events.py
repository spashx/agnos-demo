# RQ-NTF-001, DEC-NTF-001 (ADR-NTF-001)
"""In-process event bus and the reservation-created event."""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass

from roombook.domain import Reservation

LOGGER_NAME = "roombook.events"
LOG_HANDLER_FAILED = "event handler failed for %s"

_LOGGER = logging.getLogger(LOGGER_NAME)


@dataclass(frozen=True)
class ReservationCreated:
    """Event published after a reservation was created (RQ-NTF-001)."""

    reservation: Reservation


EventHandler = Callable[[object], None]


class EventBus:
    """Delivers each published event to every subscribed handler (RQ-NTF-001, DEC-NTF-001)."""

    def __init__(self) -> None:
        self._handlers: list[EventHandler] = []

    def subscribe(self, handler: EventHandler) -> None:
        """Register a handler that receives every published event (RQ-NTF-001)."""
        self._handlers.append(handler)

    def publish(self, event: object) -> None:
        """Deliver the event to all handlers; a failing handler is logged and does not stop the others (DEC-NTF-001)."""
        for handler in list(self._handlers):
            try:
                handler(event)
            except Exception:
                _LOGGER.exception(LOG_HANDLER_FAILED, type(event).__name__)
