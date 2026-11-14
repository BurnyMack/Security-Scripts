"""Tests for hashing and manifest helpers."""

import hashlib

from secscripts.hashing import build_manifest, manifest_entry, sha256_bytes, sha256_file


def test_sha256_file_matches_hashlib(tmp_path):
    payload = b"evidence bytes" * 1000
    target = tmp_path / "artefact.bin"
    target.write_bytes(payload)
    assert sha256_file(target) == hashlib.sha256(payload).hexdigest()


def test_sha256_bytes():
    assert sha256_bytes(b"abc") == hashlib.sha256(b"abc").hexdigest()


def test_manifest_entry_fields_and_no_mutation(tmp_path):
    target = tmp_path / "a.txt"
    target.write_text("hello")
    before = target.stat().st_mtime_ns

    entry = manifest_entry(target)

    assert entry["sha256"] == hashlib.sha256(b"hello").hexdigest()
    assert entry["size"] == 5
    assert "modified" in entry and "changed" in entry
    # Hashing must not modify the source file's mtime.
    assert target.stat().st_mtime_ns == before


def test_build_manifest_skips_dirs_and_missing(tmp_path):
    (tmp_path / "f1.txt").write_text("one")
    (tmp_path / "sub").mkdir()
    entries = build_manifest([tmp_path / "f1.txt", tmp_path / "sub", tmp_path / "missing.txt"])
    assert len(entries) == 1
    assert entries[0]["path"].endswith("f1.txt")
