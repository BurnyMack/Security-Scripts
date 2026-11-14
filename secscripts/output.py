"""Render structured results (a list of dict records) as json, csv, or text.

Tools collect their results as ``list[dict]`` and call :func:`emit` (or
:func:`render`) with the chosen ``--output-format``. Keeping this in one place
means every tool's json/csv/text output looks the same and pipes cleanly.
"""

from __future__ import annotations

import csv
import io
import json
import sys
from collections.abc import Iterable, Sequence
from typing import Any, TextIO

Record = dict[str, Any]


def _ordered_fieldnames(records: Sequence[Record]) -> list[str]:
    """Union of keys across records, preserving first-seen order."""
    fieldnames: list[str] = []
    seen: set[str] = set()
    for record in records:
        for key in record:
            if key not in seen:
                seen.add(key)
                fieldnames.append(key)
    return fieldnames


def render(records: Iterable[Record], output_format: str = "text") -> str:
    """Return ``records`` rendered in ``output_format`` as a string."""
    records = list(records)

    if output_format == "json":
        return json.dumps(records, indent=2, default=str)

    if output_format == "csv":
        if not records:
            return ""
        buffer = io.StringIO()
        fieldnames = _ordered_fieldnames(records)
        writer = csv.DictWriter(buffer, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow({key: record.get(key, "") for key in fieldnames})
        return buffer.getvalue().rstrip("\r\n")

    if output_format == "text":
        if not records:
            return ""
        lines: list[str] = []
        for index, record in enumerate(records):
            if index:
                lines.append("")
            for key, value in record.items():
                lines.append(f"{key}: {value}")
        return "\n".join(lines)

    raise ValueError(f"unknown output format: {output_format!r}")


def emit(
    records: Iterable[Record],
    output_format: str = "text",
    *,
    stream: TextIO | None = None,
) -> None:
    """Render ``records`` and write them to ``stream`` (default stdout)."""
    target = stream if stream is not None else sys.stdout
    text = render(records, output_format)
    if text:
        print(text, file=target)
