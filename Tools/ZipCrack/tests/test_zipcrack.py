"""Tests for ZipCrack against fixture encrypted archives."""

import importlib.util
import zipfile
from pathlib import Path

import pytest

_MODULE_PATH = Path(__file__).resolve().parents[1] / "zipcrack.py"
_spec = importlib.util.spec_from_file_location("zipcrack", _MODULE_PATH)
zipcrack = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(zipcrack)


def _encrypted_zip(tmp_path, password):
    """Create a ZipCrypto-encrypted zip. Uses the stdlib writestr + pwd.

    Python's zipfile can *read* with a password but cannot *write* encrypted
    entries, so we shell out to the system `zip` if present; otherwise skip.
    """
    import shutil
    import subprocess

    zip_bin = shutil.which("zip")
    if not zip_bin:
        pytest.skip("system 'zip' not available to build an encrypted fixture")
    payload = tmp_path / "secret.txt"
    payload.write_text("classified")
    archive = tmp_path / "enc.zip"
    subprocess.run(
        [zip_bin, "-j", "-P", password, str(archive), str(payload)],
        check=True,
        capture_output=True,
    )
    return str(archive)


def test_cracks_known_password(tmp_path, capsys):
    archive = _encrypted_zip(tmp_path, "s3cret")
    wl = tmp_path / "words.txt"
    wl.write_text("nope\ns3cret\nother\n")
    rc = zipcrack.main([archive, "-w", str(wl), "--workers", "1"])
    assert rc == 0
    assert "Password found: s3cret" in capsys.readouterr().out


def test_wrong_passwords_return_error(tmp_path):
    archive = _encrypted_zip(tmp_path, "s3cret")
    wl = tmp_path / "words.txt"
    wl.write_text("aaa\nbbb\nccc\n")
    assert zipcrack.main([archive, "-w", str(wl), "--workers", "1"]) == 1


def test_unencrypted_zip_errors(tmp_path):
    plain = tmp_path / "plain.zip"
    with zipfile.ZipFile(plain, "w") as zf:
        zf.writestr("a.txt", "hello")
    wl = tmp_path / "w.txt"
    wl.write_text("x\n")
    assert zipcrack.main([str(plain), "-w", str(wl), "--workers", "1"]) == 1


def test_mask_mode(tmp_path, capsys):
    archive = _encrypted_zip(tmp_path, "07")
    rc = zipcrack.main([archive, "--mask", "?d?d", "--workers", "1"])
    assert rc == 0
    assert "07" in capsys.readouterr().out
