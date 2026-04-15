"""Small filesystem helpers used by experiments and tests."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def ensure_directory(path: Path) -> Path:
    """Create a directory if needed and return it."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write a JSON payload with stable formatting."""
    ensure_directory(path.parent)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    """Write a text file, creating parent directories if needed."""
    ensure_directory(path.parent)
    path.write_text(content, encoding="utf-8")


def write_csv_rows(
    path: Path,
    rows: list[dict[str, Any]],
    fieldnames: list[str] | None = None,
) -> None:
    """Write row dictionaries to CSV with a stable header order."""
    ensure_directory(path.parent)
    if not rows:
        if fieldnames is None:
            fieldnames = []
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
        return

    if fieldnames is None:
        ordered_keys = list(rows[0].keys())
        extras = sorted(
            {
                key
                for row in rows[1:]
                for key in row.keys()
                if key not in ordered_keys
            }
        )
        fieldnames = ordered_keys + extras

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
