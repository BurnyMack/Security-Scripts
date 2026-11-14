"""Tests for the config-driven collector (evidence integrity + JSON report)."""

import hashlib
import importlib.util
import json
from pathlib import Path

_DIR = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("collect", _DIR / "collect.py")
collect = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(collect)


def _profile(tmp_path, files):
    import yaml

    cfg = {
        "name": "test",
        "files": [str(f) for f in files],
        "commands": [{"name": "echo", "argv": ["echo", "hello"]}],
    }
    path = tmp_path / "profile.yaml"
    path.write_text(yaml.safe_dump(cfg))
    return str(path)


def test_every_artefact_is_hashed_and_report_is_valid_json(tmp_path):
    src = tmp_path / "evidence.txt"
    src.write_text("classified data")
    out = tmp_path / "out"
    rc = collect.main(["-c", _profile(tmp_path, [src]), "-o", str(out)])
    assert rc == 0

    manifest = json.loads((out / "manifest.json").read_text())
    # Every manifest entry has a non-empty sha256.
    assert manifest and all(e.get("sha256") for e in manifest)
    file_entry = next(e for e in manifest if e.get("kind") == "file")
    assert file_entry["sha256"] == hashlib.sha256(b"classified data").hexdigest()

    report = json.loads((out / "report.json").read_text())  # must be valid JSON
    assert report["profile"] == "test"
    assert report["artefact_count"] == len(manifest)
    assert (out / "audit.log").read_text().strip()  # timestamped audit log written


def test_source_is_not_modified(tmp_path):
    src = tmp_path / "evidence.txt"
    src.write_text("do not touch")
    before_mtime = src.stat().st_mtime_ns
    before_bytes = src.read_bytes()
    out = tmp_path / "out"
    collect.main(["-c", _profile(tmp_path, [src]), "-o", str(out)])
    assert src.stat().st_mtime_ns == before_mtime
    assert src.read_bytes() == before_bytes


def test_missing_file_is_logged_as_error_not_fatal(tmp_path):
    out = tmp_path / "out"
    profile = _profile(tmp_path, [tmp_path / "nonexistent.txt"])
    rc = collect.main(["-c", profile, "-o", str(out)])
    assert rc == 0  # keeps going
    report = json.loads((out / "report.json").read_text())
    assert report["error_count"] >= 1


def test_command_output_captured_and_hashed(tmp_path):
    out = tmp_path / "out"
    collect.main(["-c", _profile(tmp_path, []), "-o", str(out)])
    manifest = json.loads((out / "manifest.json").read_text())
    cmd = next(e for e in manifest if e.get("kind") == "command")
    assert cmd["name"] == "echo"
    assert cmd["sha256"]
    assert (out / cmd["collected_copy"]).read_text().strip() == "hello"


def test_print_default_config(capsys):
    assert collect.main(["--print-default-config"]) == 0
    import yaml

    parsed = yaml.safe_load(capsys.readouterr().out)
    assert parsed["name"] == "default"


def test_output_required_without_print():
    assert collect.main([]) == 1
