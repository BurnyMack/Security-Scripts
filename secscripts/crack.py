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
from collections import deque
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


def _search_serial(
    candidates: Iterator[str],
    matcher: Matcher,
    *,
    tried: int,
    bar: Progress,
    resume_path: str | None,
    checkpoint_every: int,
) -> CrackResult:
    for candidate in candidates:
        tried += 1
        bar.update(1)
        if matcher(candidate):
            bar.close()
            _clear_resume(resume_path)
            return CrackResult(found=True, password=candidate, tried=tried)
        if resume_path and tried % checkpoint_every == 0:
            _write_resume(resume_path, tried)
    bar.close()
    _clear_resume(resume_path)
    return CrackResult(found=False, password=None, tried=tried)


def search(
    candidates: Iterator[str],
    matcher: Matcher,
    *,
    total: int | None = None,
    workers: int | None = None,
    chunksize: int = 128,
    checkpoint_every: int = 5000,
    resume_path: str | None = None,
    progress: bool | None = None,
) -> CrackResult:
    """Search ``candidates`` for one that satisfies ``matcher``.

    ``workers`` defaults to ``os.cpu_count()``; pass ``1`` to run in-process
    (no pool). Parallel work is streamed through ``pool.imap`` with ``chunksize``
    candidates per task, which keeps every worker fed (far less IPC overhead
    than a barrier per batch) while preserving candidate order, so the first
    match is deterministic and resume is exact. ``resume_path`` enables
    check-pointing: the already-tried count is skipped on start and rewritten
    every ``checkpoint_every`` candidates; it is cleared on success or clean
    exhaustion.
    """
    if workers is None:
        workers = os.cpu_count() or 1

    already = _read_resume(resume_path)
    if already:
        # Skip candidates already tried in a previous run.
        for _ in islice(candidates, already):
            pass
    remaining_total = None if total is None else max(total - already, 0)
    tried = already
    bar = Progress(total=remaining_total, enabled=progress)

    if workers <= 1:
        return _search_serial(
            candidates,
            matcher,
            tried=tried,
            bar=bar,
            resume_path=resume_path,
            checkpoint_every=checkpoint_every,
        )

    import multiprocessing

    # Record each candidate as imap pulls it from the source, so a True result
    # at position i maps back to the i-th candidate. The deque holds only the
    # in-flight window, not the whole keyspace.
    pending: deque[str] = deque()

    def recording_iter() -> Iterator[str]:
        for candidate in candidates:
            pending.append(candidate)
            yield candidate

    pool = multiprocessing.Pool(processes=workers)
    try:
        for hit in pool.imap(matcher, recording_iter(), chunksize):
            candidate = pending.popleft()
            tried += 1
            bar.update(1)
            if hit:
                bar.close()
                pool.terminate()  # stop remaining work immediately
                _clear_resume(resume_path)
                return CrackResult(found=True, password=candidate, tried=tried)
            if resume_path and tried % checkpoint_every == 0:
                _write_resume(resume_path, tried)
        bar.close()
        pool.close()
        _clear_resume(resume_path)
        return CrackResult(found=False, password=None, tried=tried)
    finally:
        pool.join()  # safe after either terminate() or close()
