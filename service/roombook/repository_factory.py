# RQ-BKG-007, DEC-BKG-003, DEC-BKG-004 (ADR-BKG-002, ADR-BKG-003)
"""Chooses the reservation repository adapter from configuration (DEC-BKG-004)."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from roombook.file_repository import FileReservationRepository
from roombook.memory_repository import InMemoryReservationRepository
from roombook.ports import ReservationRepository

DATA_FILE_ENV = "ROOMBOOK_DATA_FILE"
UNSET_VALUE = ""


def create_repository(environ: Mapping[str, str]) -> ReservationRepository:
    """Return a file repository when the data-file setting is non-empty, else an in-memory one (RQ-BKG-007)."""
    data_file = environ.get(DATA_FILE_ENV, UNSET_VALUE)
    if data_file:
        return FileReservationRepository(Path(data_file))
    return InMemoryReservationRepository()
