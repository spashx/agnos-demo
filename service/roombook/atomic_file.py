# RQ-BKG-007, DEC-BKG-004 (ADR-BKG-003)
"""Atomic file replacement: write a temporary file, then rename it over the target (DEC-BKG-004)."""

from __future__ import annotations

import os
from collections.abc import Callable
from pathlib import Path

TEMP_SUFFIX = ".tmp"
TEXT_ENCODING = "utf-8"


def write_atomically(path: Path, content: str, before_replace: Callable[[], None] | None = None) -> None:
    """Write content so that an interrupted save leaves the previous file intact (RQ-BKG-007)."""
    temp_path = path.with_name(path.name + TEMP_SUFFIX)
    with temp_path.open("w", encoding=TEXT_ENCODING) as handle:
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())
    if before_replace is not None:
        before_replace()
    os.replace(temp_path, path)
