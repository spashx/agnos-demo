# RQ-NTF-002, DEC-NTF-002 (ADR-NTF-001)
"""Tests of the console notifier."""

from __future__ import annotations

import io
import unittest

from roombook.notifier import LINE_END, RECIPIENT_SEPARATOR, ConsoleNotifier

RECIPIENT = "alice"
MESSAGE = "your meeting starts soon"


class ConsoleNotifierTest(unittest.TestCase):
    """Tests for ConsoleNotifier (RQ-NTF-002, DEC-NTF-002)."""

    # RQ-NTF-002
    def test_given_console_notifier_when_send_then_writes_recipient_and_message_on_one_line(self) -> None:
        # Given
        stream = io.StringIO()
        notifier = ConsoleNotifier(stream)
        # When
        notifier.send(RECIPIENT, MESSAGE)
        # Then
        self.assertEqual(stream.getvalue(), f"{RECIPIENT}{RECIPIENT_SEPARATOR}{MESSAGE}{LINE_END}")

    # RQ-NTF-002
    def test_given_console_notifier_when_send_twice_then_each_message_has_its_own_line(self) -> None:
        # Given
        stream = io.StringIO()
        notifier = ConsoleNotifier(stream)
        # When
        notifier.send(RECIPIENT, MESSAGE)
        notifier.send(RECIPIENT, MESSAGE)
        # Then
        self.assertEqual(stream.getvalue().count(LINE_END), 2)


if __name__ == "__main__":
    unittest.main()
