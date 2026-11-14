"""Parallel candidate search with progress and resume, shared by the crackers.

:func:`search` pulls candidates from a deterministic iterator and tests each
with a *picklable* matcher across a multiprocessing pool, in sequential chunks.
Because the candidate stream is deterministic, progress can be check-pointed as
"candidates consumed so far"; a resumed run skips that many from the start and
carries on.

A *matcher* is any picklable callable ``matcher(candidate: str) -> bool``. The
crackers pass small dataclass matchers that hold only strings (the target hash
and its type) and recreate the verification each call, so they pickle cleanly
to worker processes.
"""

from __future__ import annotations

import json
import os
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from itertools import islice

from .progress import Progress

Matcher = Callable[[str], bool]


@dataclass
class CrackResult:
    found: bool
    password: str | None
    tried: int


def _chunks(iterator: Iterator[str], size: int) -> Iterator[list[str]]:
    while True:
        batch = list(islice(iterator, size))
        if not batch:
            return
        yield batch


def _read_resume(path: str | None) -> int:
    if not path or not os.path.exists(path):
        return 0
    try:
        with open(path, encoding="utf-8") as handle:
            return int(json.load(handle).get("tried", 0))
    except (OSError, ValueError, json.JSONDecodeError):
        return 0


def _write_resume(path: str | None, tried: int) -> None:
    if not path:
        return
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as handle:
        json.dump({"tried": tried}, handle)
    os.replace(tmp, path)  # atomic, so an interrupted write can't corrupt it


def _clear_resume(path: str | None) -> None:
    if path and os.path.exists(path):
        os.remove(path)


def _run_chunk(matcher: Matcher, chunk: list[str], pool) -> str | None:
    """Return the first matching candidate in a chunk, or None."""
    if pool is None:
        for candidate in chunk:
            if matcher(candidate):
                return candidate
        return None
    # Map preserves order, so the first True corresponds to the first match in
    # candidate order within the chunk.
    for candidate, hit in zip(chunk, pool.map(matcher, chunk), strict=True):
        if hit:
            return candidate
    return None


def search(
    candidates: Iterator[str],
    matcher: Matcher,
    *,
    total: int | None = None,
    workers: int | None = None,
    chunk_size: int = 2000,
    resume_path: str | None = None,
    progress: bool | None = None,
) -> CrackResult:
    """Search ``candidates`` for one that satisfies ``matcher``.

    ``workers`` defaults to ``os.cpu_count()``; pass ``1`` to run in-process
    (no pool). ``resume_path`` enables check-pointing: the already-tried count
    is skipped on start and updated after each exhausted chunk; it is cleared
    on success or clean exhaustion.
    """
    if workers is None:
        workers = os.cpu_count() or 1

    already = _read_resume(resume_path)
    if already:
        # Skip candidates already tried in a previous run.
        for _ in islice(candidates, already):
            pass
    remaining_total = None if total is None else max(total - already, 0)

    pool = None
    created_pool = False
    try:
        if workers > 1:
            import multiprocessing

            pool = multiprocessing.Pool(processes=workers)
            created_pool = True

        tried = already
        bar = Progress(total=remaining_total, enabled=progress)
        for chunk in _chunks(candidates, chunk_size):
            match = _run_chunk(matcher, chunk, pool)
            if match is not None:
                # Count candidates up to and including the match.
                index = chunk.index(match)
                tried += index + 1
                bar.update(index + 1)
                bar.close()
                _clear_resume(resume_path)
                return CrackResult(found=True, password=match, tried=tried)
            tried += len(chunk)
            bar.update(len(chunk))
            _write_resume(resume_path, tried)
        bar.close()
        _clear_resume(resume_path)
        return CrackResult(found=False, password=None, tried=tried)
    finally:
        if created_pool and pool is not None:
            pool.close()
            pool.join()
