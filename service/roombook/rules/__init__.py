# RQ-BKG-002, RQ-BKG-003, RQ-BKG-004, RQ-BKG-006, DEC-BKG-002 (ADR-BKG-001)
"""Reservation rules: each rule module defines RULE and RULE_ORDER; load_rules discovers them."""

from __future__ import annotations

import importlib
import pkgutil
from collections.abc import Sequence
from typing import Protocol

from roombook.domain import Reservation, ReservationRequest, Room

RULE_ATTRIBUTE = "RULE"
RULE_ORDER_ATTRIBUTE = "RULE_ORDER"


class ReservationRule(Protocol):
    """One validity rule of a reservation request (DEC-BKG-002)."""

    def check(self, room: Room, request: ReservationRequest, existing: Sequence[Reservation]) -> None:
        """Raise a RoombookError when the request breaks the rule (RQ-BKG-002)."""


def load_rules() -> list[ReservationRule]:
    """Discover the rule modules of this package and return their rules sorted by RULE_ORDER (DEC-BKG-002)."""
    loaded: list[tuple[int, ReservationRule]] = []
    for module_info in pkgutil.iter_modules(__path__):
        module = importlib.import_module(f"{__name__}.{module_info.name}")
        loaded.append((getattr(module, RULE_ORDER_ATTRIBUTE), getattr(module, RULE_ATTRIBUTE)))
    loaded.sort(key=lambda entry: entry[0])
    return [rule for _, rule in loaded]
