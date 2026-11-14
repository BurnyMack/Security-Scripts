"""Tests for HashCrack: hash-type coverage, auto-detect, attack modes, resume."""

import hashlib
import importlib.util
from pathlib import Path

import pytest

_MODULE_PATH = Path(__file__).resolve().parents[1] / "hashcrack.py"
_spec = importlib.util.spec_from_file_location("hashcrack", _MODULE_PATH)
hashcrack = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hashcrack)


def _wordlist(tmp_path, words):
    wl = tmp_path / "words.txt"
    wl.write_text("\n".join(words) + "\n")
    return str(wl)


def test_detect_type():
    assert hashcrack.detect_type(hashlib.md5(b"x").hexdigest()) == "md5"
    assert hashcrack.detect_type(hashlib.sha256(b"x").hexdigest()) == "sha256"
    assert hashcrack.detect_type("$6$abc$def") == "sha512crypt"
    assert hashcrack.detect_type("$5$abc$def") == "sha256crypt"
    assert hashcrack.detect_type("$1$abc$def") == "md5crypt"
    assert hashcrack.detect_type("$2b$12$" + "a" * 53) == "bcrypt"
    with pytest.raises(ValueError):
        hashcrack.detect_type("not-a-hash")


def test_raw_md5_autodetect(tmp_path, capsys):
    target = hashlib.md5(b"secret").hexdigest()
    wl = _wordlist(tmp_path, ["wrong", "secret", "other"])
    rc = hashcrack.main([target, "-w", wl, "--workers", "1"])
    assert rc == 0
    assert "Password found: secret" in capsys.readouterr().out


def test_sha256_family(tmp_path, capsys):
    target = hashlib.sha256(b"hunter2").hexdigest()
    wl = _wordlist(tmp_path, ["a", "hunter2", "b"])
    assert hashcrack.main([target, "-w", wl, "--workers", "1"]) == 0
    assert "hunter2" in capsys.readouterr().out


def test_crypt_scheme(tmp_path, capsys):
    from passlib.hash import md5_crypt

    target = md5_crypt.hash("letmein")
    wl = _wordlist(tmp_path, ["no", "letmein"])
    assert hashcrack.main([target, "-w", wl, "--workers", "1"]) == 0
    assert "letmein" in capsys.readouterr().out


def test_ntlm_needs_explicit_type(tmp_path, capsys):
    from passlib.hash import nthash

    target = nthash.hash("Welcome1")
    wl = _wordlist(tmp_path, ["x", "Welcome1"])
    assert hashcrack.main([target, "--type", "ntlm", "-w", wl, "--workers", "1"]) == 0
    assert "Welcome1" in capsys.readouterr().out


def test_mask_mode(tmp_path, capsys):
    target = hashlib.md5(b"42").hexdigest()
    assert hashcrack.main([target, "--mask", "?d?d", "--workers", "1"]) == 0
    assert "42" in capsys.readouterr().out


def test_rules_mode(tmp_path, capsys):
    # "pass" + rule "$1" -> "pass1"
    target = hashlib.md5(b"pass1").hexdigest()
    wl = _wordlist(tmp_path, ["pass"])
    rules = tmp_path / "r.rule"
    rules.write_text(":\n$1\n")
    rc = hashcrack.main([target, "-w", wl, "--rules", str(rules), "--workers", "1"])
    assert rc == 0
    assert "pass1" in capsys.readouterr().out


def test_not_found_returns_error(tmp_path):
    target = hashlib.md5(b"absent").hexdigest()
    wl = _wordlist(tmp_path, ["a", "b", "c"])
    assert hashcrack.main([target, "-w", wl, "--workers", "1"]) == 1


def test_resume_file_round_trip(tmp_path):
    # First run against a wordlist that does NOT contain the target leaves a
    # cleared resume file (clean exhaustion); a pre-seeded resume skips ahead.
    target = hashlib.md5(b"zzz").hexdigest()
    resume = tmp_path / "state.json"
    resume.write_text('{"tried": 2}')
    wl = _wordlist(tmp_path, ["zzz", "a", "b"])  # target at index 0, skipped
    rc = hashcrack.main([target, "-w", wl, "--workers", "1", "--resume", str(resume)])
    assert rc == 1  # skipped past the only match
