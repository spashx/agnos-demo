# RQ-NTF-003, DEC-NTF-002 (ADR-NTF-001)
"""Retrying decorator for notifiers: retries a failing delivery and never raises to the caller."""

from __future__ import annotations

import logging

from roombook.notifier import Notifier

MAX_ATTEMPTS = 3
LOGGER_NAME = "roombook.notifier"
LOG_DELIVERY_FAILED = "notification failed after %d attempts"

_LOGGER = logging.getLogger(LOGGER_NAME)


class RetryingNotifier:
    """Calls the inner notifier up to MAX_ATTEMPTS times and logs the final failure (RQ-NTF-003)."""

    def __init__(self, inner: Notifier, logger: logging.Logger | None = None) -> None:
        self._inner = inner
        self._logger = logger or _LOGGER

    def send(self, recipient: str, message: str) -> None:
        """Deliver with retries; on total failure log once and return normally (RQ-NTF-003)."""
        last_error: Exception | None = None
        for _ in range(MAX_ATTEMPTS):
            try:
                self._inner.send(recipient, message)
                return
            except Exception as error:
                last_error = error
        self._logger.error(LOG_DELIVERY_FAILED, MAX_ATTEMPTS, exc_info=last_error)
