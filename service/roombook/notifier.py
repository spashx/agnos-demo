# RQ-NTF-002, DEC-NTF-002 (ADR-NTF-001)
"""Notifier port and the console adapter that delivers messages on a text stream."""

from __future__ import annotations

import sys
from typing import Protocol, TextIO

RECIPIENT_SEPARATOR = ": "
LINE_END = "\n"


class Notifier(Protocol):
    """Delivers a message to a recipient (RQ-NTF-002, DEC-NTF-002)."""

    def send(self, recipient: str, message: str) -> None:
        """Deliver the message or raise if delivery fails (RQ-NTF-003)."""
        ...


class ConsoleNotifier:
    """Writes each message as one line on a stream (RQ-NTF-002, DEC-NTF-002)."""

    def __init__(self, stream: TextIO = sys.stdout) -> None:
        self._stream = stream

    def send(self, recipient: str, message: str) -> None:
        """Write the recipient and message on one line (RQ-NTF-002)."""
        self._stream.write(f"{recipient}{RECIPIENT_SEPARATOR}{message}{LINE_END}")
