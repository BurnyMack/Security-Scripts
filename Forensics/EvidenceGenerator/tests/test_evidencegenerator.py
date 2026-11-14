"""Tests for the EvidenceGenerator CLI tools at tiny sizes."""

import csv
import importlib.util
from pathlib import Path

import pytest

_DIR = Path(__file__).resolve().parents[1]


def _load(name):
    spec = importlib.util.spec_from_file_location(name, _DIR / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_generate_data_creates_csv(tmp_path):
    pytest.importorskip("faker")
    generate_data = _load("generate_data")
    out = tmp_path / "users.csv"
    rc = generate_data.main(["-o", str(out), "--min-users", "5", "--max-users", "5"])
    assert rc == 0
    rows = list(csv.reader(out.open()))
    assert rows[0][0] == "First Name"
    assert len(rows) == 6  # header + 5 records


def test_generate_data_version(capsys):
    pytest.importorskip("faker")
    generate_data = _load("generate_data")
    with pytest.raises(SystemExit) as exc:
        generate_data.main(["--version"])
    assert exc.value.code == 0
    assert "generate_data" in capsys.readouterr().out


def test_webgen_creates_log(tmp_path):
    webgen = _load("webgen")
    for name in ("ua.txt", "ref.txt", "pages.txt"):
        (tmp_path / name).write_text("Mozilla/5.0\n/index.html\n")
    out = tmp_path / "access.log"
    rc = webgen.main(
        [
            "-o",
            str(out),
            "--user-agents",
            str(tmp_path / "ua.txt"),
            "--referrers",
            str(tmp_path / "ref.txt"),
            "--page-names",
            str(tmp_path / "pages.txt"),
            "--min-entries",
            "200",
            "--max-entries",
            "200",
        ]
    )
    assert rc == 0
    assert out.is_file() and out.stat().st_size > 0


def test_webgen_missing_input_errors(tmp_path):
    webgen = _load("webgen")
    rc = webgen.main(
        [
            "-o",
            str(tmp_path / "o.log"),
            "--user-agents",
            str(tmp_path / "nope.txt"),
            "--min-entries",
            "10",
            "--max-entries",
            "10",
        ]
    )
    assert rc == 1


def test_webgen_version(capsys):
    webgen = _load("webgen")
    with pytest.raises(SystemExit) as exc:
        webgen.main(["--version"])
    assert exc.value.code == 0
    assert "webgen" in capsys.readouterr().out
