"""Tests for the XLanalyser CLI."""

import importlib.util
import json
from pathlib import Path

import pytest

_MODULE_PATH = Path(__file__).resolve().parents[1] / "XLanalyser.py"
_spec = importlib.util.spec_from_file_location("xlanalyser", _MODULE_PATH)
xlanalyser = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(xlanalyser)


def _csv(tmp_path):
    path = tmp_path / "data.csv"
    path.write_text("a,b\n1,10\n2,\n3,30\n")
    return str(path)


def test_json_summary_to_stdout(tmp_path, capsys):
    rc = xlanalyser.main([_csv(tmp_path), "--output-format", "json"])
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    cols = {row["column"]: row for row in data}
    assert cols["a"]["count"] == 3
    assert cols["b"]["null_count"] == 1  # one missing value in column b


def test_text_output(tmp_path, capsys):
    rc = xlanalyser.main([_csv(tmp_path)])
    assert rc == 0
    assert "column:" in capsys.readouterr().out


def test_xlsx_output_writes_file(tmp_path):
    out = tmp_path / "summary.xlsx"
    rc = xlanalyser.main([_csv(tmp_path), "--output-format", "xlsx", "-o", str(out)])
    assert rc == 0
    assert out.is_file()


def test_unsupported_input_returns_error(tmp_path):
    bad = tmp_path / "data.txt"
    bad.write_text("nope")
    assert xlanalyser.main([str(bad)]) == 1


def test_missing_file_returns_error(tmp_path):
    assert xlanalyser.main([str(tmp_path / "nope.csv")]) == 1


def test_version(capsys):
    with pytest.raises(SystemExit) as exc:
        xlanalyser.main(["--version"])
    assert exc.value.code == 0
    assert "XLanalyser" in capsys.readouterr().out
