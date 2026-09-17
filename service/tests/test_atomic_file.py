# RQ-BKG-007, DEC-BKG-004 (ADR-BKG-003)
"""Unit tests of the atomic file writer."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from roombook.atomic_file import TEMP_SUFFIX, write_atomically

DATA_FILE_NAME = "reservations.json"
PREVIOUS_CONTENT = "previous content"
NEW_CONTENT = "new content"


class InterruptedSave(Exception):
    """Raised by a test double to simulate an interruption before the rename (RQ-BKG-007)."""


def _interrupt() -> None:
    """Simulate an interruption right before the final rename (RQ-BKG-007)."""
    raise InterruptedSave()


class WriteAtomicallyTest(unittest.TestCase):
    """Tests of write_atomically (RQ-BKG-007)."""

    # RQ-BKG-007
    def setUp(self) -> None:
        self._directory = tempfile.TemporaryDirectory()
        self.path = Path(self._directory.name) / DATA_FILE_NAME

    # RQ-BKG-007
    def tearDown(self) -> None:
        self._directory.cleanup()

    # RQ-BKG-007
    def test_given_existing_file_when_written_then_file_has_the_new_content_and_no_temp_file_remains(self) -> None:
        # Given
        self.path.write_text(PREVIOUS_CONTENT, encoding="utf-8")
        # When
        write_atomically(self.path, NEW_CONTENT)
        # Then
        self.assertEqual(self.path.read_text(encoding="utf-8"), NEW_CONTENT)
        self.assertFalse(self.path.with_name(self.path.name + TEMP_SUFFIX).exists())

    # RQ-BKG-007
    def test_given_no_file_when_written_then_file_is_created(self) -> None:
        # Given
        # no data file exists yet
        # When
        write_atomically(self.path, NEW_CONTENT)
        # Then
        self.assertEqual(self.path.read_text(encoding="utf-8"), NEW_CONTENT)

    # RQ-BKG-007
    def test_given_save_interrupted_before_rename_when_written_then_previous_file_stays_intact(self) -> None:
        # Given
        self.path.write_text(PREVIOUS_CONTENT, encoding="utf-8")
        # When
        with self.assertRaises(InterruptedSave):
            write_atomically(self.path, NEW_CONTENT, before_replace=_interrupt)
        # Then
        self.assertEqual(self.path.read_text(encoding="utf-8"), PREVIOUS_CONTENT)


if __name__ == "__main__":
    unittest.main()
