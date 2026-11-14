"""Generate fixed-size fixtures for the benchmark (wordlist and apache log)."""

from __future__ import annotations

from pathlib import Path


def make_wordlist(path: str | Path, count: int) -> Path:
    """Write ``count`` deterministic candidate words to ``path``."""
    path = Path(path)
    with open(path, "w", encoding="utf-8") as handle:
        for i in range(count):
            handle.write(f"candidate{i:07d}\n")
    return path


def make_apache_log(path: str | Path, lines: int) -> Path:
    """Write ``lines`` deterministic apache access-log lines to ``path``."""
    path = Path(path)
    template = (
        "192.168.{a}.{b} - - [10/Oct/2023:12:34:{s:02d} +0000] "
        '"GET /page/{i} HTTP/1.1" 200 {size}\n'
    )
    with open(path, "w", encoding="utf-8") as handle:
        for i in range(lines):
            handle.write(
                template.format(a=i % 256, b=(i // 256) % 256, s=i % 60, i=i, size=1000 + i)
            )
    return path
