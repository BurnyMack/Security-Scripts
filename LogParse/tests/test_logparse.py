"""Tests for the LogParse parsers, auto-detection, and CLI."""

import csv
import io
import json
from pathlib import Path

import pytest

from LogParse import CLIParse
from LogParse.LogParse import TEXT_FORMATS, LogParse

SAMPLES = Path(__file__).resolve().parents[1] / "TestFiles"
SAMPLE_FILE = {
    "apache": SAMPLES / "apache.log",
    "iis": SAMPLES / "iis.log",
    "syslog": SAMPLES / "syslog.log",
    "cef": SAMPLES / "cef.log",
    "yara": SAMPLES / "rules.yar",
}


@pytest.mark.parametrize("fmt", TEXT_FORMATS)
def test_each_format_parses_its_sample(fmt):
    records = LogParse(str(SAMPLE_FILE[fmt])).parse(fmt)
    assert len(records) == 2, f"{fmt} should parse 2 records from its sample"
    assert all(isinstance(r, dict) and r for r in records)


@pytest.mark.parametrize("fmt", TEXT_FORMATS)
def test_auto_detect_identifies_each_sample(fmt):
    assert LogParse(str(SAMPLE_FILE[fmt])).detect() == fmt


def test_parse_unknown_format_raises():
    with pytest.raises(ValueError):
        LogParse(str(SAMPLE_FILE["apache"])).parse("nope")


def test_detect_undetectable_raises(tmp_path):
    junk = tmp_path / "junk.txt"
    junk.write_text("this is not any known log format\njust words\n")
    with pytest.raises(ValueError, match="could not auto-detect"):
        LogParse(str(junk)).detect()


def test_iis_schema_fields():
    record = LogParse(str(SAMPLE_FILE["iis"])).parse("iis")[0]
    assert record["HTTP Method"] == "GET"
    assert record["Status Code"] == "200"
    assert record["User Agent"].startswith("Mozilla")


# --- CLI tests ---


def test_cli_json_to_stdout(capsys):
    rc = CLIParse.main(["-p", str(SAMPLE_FILE["apache"]), "--output-format", "json"])
    assert rc == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert len(data) == 2
    assert data[0]["IP"] == "192.168.1.1"


def test_cli_autodetect_csv(capsys):
    rc = CLIParse.main(["-p", str(SAMPLE_FILE["cef"]), "--output-format", "csv"])
    assert rc == 0
    rows = list(csv.DictReader(io.StringIO(capsys.readouterr().out)))
    assert rows[0]["Vendor"] == "MyVendor"


def test_cli_missing_file_returns_error():
    rc = CLIParse.main(["-p", "/no/such/file.log"])
    assert rc == 1


def test_cli_writes_file_with_output_dir(tmp_path):
    rc = CLIParse.main(
        ["-p", str(SAMPLE_FILE["syslog"]), "--format", "syslog", "-o", str(tmp_path)]
    )
    assert rc == 0
    out_file = tmp_path / "syslog_parsed_data.json"
    assert out_file.is_file()
    assert len(json.loads(out_file.read_text())) == 2


def test_cli_xlsx_output(tmp_path):
    pytest.importorskip("pandas")
    rc = CLIParse.main(
        [
            "-p",
            str(SAMPLE_FILE["apache"]),
            "--output-format",
            "xlsx",
            "-o",
            str(tmp_path),
        ]
    )
    assert rc == 0
    assert (tmp_path / "apache_parsed_data.xlsx").is_file()
