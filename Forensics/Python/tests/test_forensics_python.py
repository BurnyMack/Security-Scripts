"""Tests for the Python forensics tools' CLI contract and output."""

import importlib.util
import json
from pathlib import Path

import pytest

_DIR = Path(__file__).resolve().parents[1]


def _load(name):
    spec = importlib.util.spec_from_file_location(name, _DIR / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# --- exifcheck (tested fully; python-docx can build a fixture) ---

exifcheck = _load("exifcheck")


def test_exifcheck_json(tmp_path, capsys):
    docx = pytest.importorskip("docx")
    doc = docx.Document()
    doc.core_properties.author = "Alice"
    doc.core_properties.title = "Case Notes"
    path = tmp_path / "report.docx"
    doc.save(str(path))

    rc = exifcheck.main(["-i", str(path), "--output-format", "json"])
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data[0]["author"] == "Alice"
    assert data[0]["title"] == "Case Notes"


def test_exifcheck_missing_file(tmp_path):
    assert exifcheck.main(["-i", str(tmp_path / "nope.docx")]) == 1


def test_exifcheck_version(capsys):
    with pytest.raises(SystemExit) as exc:
        exifcheck.main(["--version"])
    assert exc.value.code == 0
    assert "exifcheck" in capsys.readouterr().out


# --- fastfluxfinder / inode_reader: modules import without scapy/pytsk3, so
#     at least the CLI contract (version) is testable everywhere. ---

fastfluxfinder = _load("fastfluxfinder")
inode_reader = _load("inode_reader")


@pytest.mark.parametrize(
    "module,name", [(fastfluxfinder, "fastfluxfinder"), (inode_reader, "inode_reader")]
)
def test_version_flag(module, name, capsys):
    with pytest.raises(SystemExit) as exc:
        module.main(["--version"])
    assert exc.value.code == 0
    assert name in capsys.readouterr().out


def test_fastflux_collect_dns_records_without_scapy_import(monkeypatch):
    # collect_dns_records only needs DNSRR at call time; verify the grouping
    # logic with a stub packet so the test needs no real pcap/scapy capture.
    class StubLayer:
        def __init__(self, rrname, rdata):
            self.rrname = rrname
            self.rdata = rdata

    class StubPacket:
        def __init__(self, rrname, rdata):
            self._layer = StubLayer(rrname, rdata)

        def haslayer(self, _):
            return True

        def getlayer(self, _):
            return self._layer

    import sys
    import types

    fake_scapy = types.ModuleType("scapy")
    fake_all = types.ModuleType("scapy.all")
    fake_all.DNSRR = object
    fake_scapy.all = fake_all
    monkeypatch.setitem(sys.modules, "scapy", fake_scapy)
    monkeypatch.setitem(sys.modules, "scapy.all", fake_all)

    packets = [
        StubPacket(b"evil.example.", "1.1.1.1"),
        StubPacket(b"evil.example.", "2.2.2.2"),
        StubPacket(b"ok.example.", "3.3.3.3"),
    ]
    records = fastfluxfinder.collect_dns_records(packets)
    assert len(records["evil.example."]) == 2
    assert len(records["ok.example."]) == 1
