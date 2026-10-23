# RQ-CLI-006, RQ-CLI-005, RQ-BKG-007, DEC-CLI-001, DEC-BKG-004 (ADR-CLI-001, ADR-BKG-003)
"""Start command of the booking service: `python -m roombook`, run in `service/`."""

from __future__ import annotations

import json
import os
from collections.abc import Mapping
from pathlib import Path

from roombook.api import ReservationApi, serve
from roombook.catalog import RoomCatalog
from roombook.clock import SystemClock
from roombook.domain import Room
from roombook.events import EventBus
from roombook.publishing_create import PublishingCreateReservation
from roombook.repository_factory import create_repository
from roombook.rules import load_rules
from roombook.use_cases.cancel_reservation import CancelReservation
from roombook.use_cases.create_reservation import CreateReservation

HOST = "127.0.0.1"
PORT = 8080
ROOMS_FILE = Path("rooms.json")
ROOMS_ENCODING = "utf-8"
STARTED_TEXT = "Roombook service on http://{host}:{port}"


def load_rooms(path: Path) -> list[Room]:
    """Read the rooms of a JSON file holding a list of room objects (RQ-CLI-006, RQ-BKG-001)."""
    return [Room(**entry) for entry in json.loads(path.read_text(encoding=ROOMS_ENCODING))]


def build_api(rooms: list[Room], environ: Mapping[str, str]) -> ReservationApi:
    """Wire the catalog, the configured storage and the use cases to the HTTP adapter (RQ-CLI-006, DEC-BKG-004)."""
    catalog = RoomCatalog()
    for room in rooms:
        catalog.add(room)
    repository = create_repository(environ)
    create = PublishingCreateReservation(CreateReservation(catalog, repository, load_rules()), EventBus())
    return ReservationApi(catalog, create, CancelReservation(repository, SystemClock()))


def main(rooms_file: Path, environ: Mapping[str, str]) -> None:
    """Serve the service built from the rooms file on the local host and port (RQ-CLI-006)."""
    api = build_api(load_rooms(rooms_file), environ)
    print(STARTED_TEXT.format(host=HOST, port=PORT), flush=True)
    serve(api, HOST, PORT)


if __name__ == "__main__":
    main(ROOMS_FILE, os.environ)
