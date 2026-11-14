"""Tests for structured output rendering."""

import csv
import io
import json

import pytest

from secscripts.output import emit, render

RECORDS = [
    {"ip": "10.0.0.1", "status": "200"},
    {"ip": "10.0.0.2", "status": "404", "extra": "x"},
]


def test_render_json_roundtrips():
    out = render(RECORDS, "json")
    assert json.loads(out) == RECORDS


def test_render_csv_has_union_header_and_rows():
    out = render(RECORDS, "csv")
    rows = list(csv.DictReader(io.StringIO(out)))
    assert rows[0]["ip"] == "10.0.0.1"
    # Field missing from the first record is still a column, blank where absent.
    assert rows[0]["extra"] == ""
    assert rows[1]["extra"] == "x"


def test_render_text_groups_records():
    out = render(RECORDS, "text")
    assert "ip: 10.0.0.1" in out
    assert "status: 404" in out


def test_render_empty_is_empty_string():
    assert render([], "json") == "[]"
    assert render([], "csv") == ""
    assert render([], "text") == ""


def test_unknown_format_raises():
    with pytest.raises(ValueError):
        render(RECORDS, "xml")


def test_emit_writes_to_stream():
    buffer = io.StringIO()
    emit(RECORDS, "json", stream=buffer)
    assert json.loads(buffer.getvalue()) == RECORDS
