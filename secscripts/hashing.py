"""SHA-256 hashing and evidence-manifest helpers for collectors.

Evidence collectors use these to prove integrity: hash every artefact they
gather (streaming, so large disk images don't load into memory), record it in
a manifest with size and timestamps, and never modify the source. Reads are
opened read-only and source mtimes are left untouched.
"""

from __future__ import annotations

import hashlib
import os
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_CHUNK_SIZE = 1024 * 1024  # 1 MiB streaming reads


def sha256_file(path: str | os.PathLike[str]) -> str:
    """Return the hex SHA-256 of a file, reading it in streamed chunks."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(_CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(data: bytes) -> str:
    """Return the hex SHA-256 of a bytes object."""
    return hashlib.sha256(data).hexdigest()


def _isoformat(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp, tz=UTC).isoformat()


def manifest_entry(path: str | os.PathLike[str]) -> dict[str, Any]:
    """Build a manifest record for one artefact without modifying it.

    Captures the relative-safe path string, size, SHA-256, and the source
    mtime/ctime (UTC ISO-8601). ``stat`` does not change the file.
    """
    p = Path(path)
    stat = p.stat()
    return {
        "path": str(p),
        "size": stat.st_size,
        "sha256": sha256_file(p),
        "modified": _isoformat(stat.st_mtime),
        "changed": _isoformat(stat.st_ctime),
    }


def build_manifest(paths: Iterable[str | os.PathLike[str]]) -> list[dict[str, Any]]:
    """Return manifest entries for every existing file in ``paths``.

    Directories and missing paths are skipped (collectors decide what to pass);
    this helper only hashes regular files.
    """
    entries: list[dict[str, Any]] = []
    for path in paths:
        p = Path(path)
        if p.is_file():
            entries.append(manifest_entry(p))
    return entries
