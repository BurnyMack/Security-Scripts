#!/usr/bin/env python3
"""
Benchmark the shared crack engine's parallel speedup and LogParse throughput.

Usage:
    python benchmarks/run.py [--candidates N] [--log-lines N] [--iterations K]

Measures :func:`secscripts.crack.search` (the engine HashCrack and ZipCrack
share) running serially vs across all CPUs on a fixed, CPU-bound workload, and
reports the speedup. On a machine with >= 4 cores it asserts a >= 3x speedup
(AC-5); with fewer cores it reports the number without asserting. Also reports
LogParse parse throughput (LogParse is streamed, not parallelised).
"""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
import time
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from benchmarks.fixtures import make_apache_log, make_wordlist  # noqa: E402
from benchmarks.matchers import CostMatcher  # noqa: E402
from secscripts import candidates as cand  # noqa: E402
from secscripts.crack import search  # noqa: E402

TARGET_SPEEDUP = 3.0
MIN_CORES_FOR_ASSERT = 4


def _time_search(wordlist: str, total: int, workers: int, iterations: int) -> float:
    matcher = CostMatcher(iterations)
    start = time.perf_counter()
    result = search(
        cand.from_wordlist(wordlist),
        matcher,
        total=total,
        workers=workers,
        progress=False,
    )
    assert not result.found  # CostMatcher never matches
    return time.perf_counter() - start


def benchmark_engine(candidates: int, iterations: int, tmpdir: str) -> dict:
    wordlist = str(make_wordlist(Path(tmpdir) / "words.txt", candidates))
    cores = os.cpu_count() or 1
    serial = _time_search(wordlist, candidates, 1, iterations)
    parallel = _time_search(wordlist, candidates, cores, iterations)
    speedup = serial / parallel if parallel > 0 else float("inf")
    return {"cores": cores, "serial_s": serial, "parallel_s": parallel, "speedup": speedup}


def benchmark_logparse(lines: int, tmpdir: str) -> dict:
    from LogParse.LogParse import LogParse

    log = str(make_apache_log(Path(tmpdir) / "access.log", lines))
    start = time.perf_counter()
    records = LogParse(log).parse("apache")
    elapsed = time.perf_counter() - start
    return {
        "lines": lines,
        "parsed": len(records),
        "seconds": elapsed,
        "lines_per_s": lines / elapsed if elapsed > 0 else float("inf"),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates", type=int, default=20000)
    parser.add_argument("--log-lines", type=int, default=200000)
    parser.add_argument("--iterations", type=int, default=400)
    args = parser.parse_args(argv)

    with tempfile.TemporaryDirectory() as tmpdir:
        engine = benchmark_engine(args.candidates, args.iterations, tmpdir)
        logp = benchmark_logparse(args.log_lines, tmpdir)

    print("Crack engine (secscripts.crack.search; used by HashCrack + ZipCrack)")
    print(f"  cores            : {engine['cores']}")
    print(f"  serial  (1 proc) : {engine['serial_s']:.3f} s")
    print(f"  parallel (N proc): {engine['parallel_s']:.3f} s")
    print(f"  speedup          : {engine['speedup']:.2f}x")
    print("LogParse (streamed, single-threaded)")
    print(
        f"  parsed {logp['parsed']}/{logp['lines']} lines in {logp['seconds']:.3f} s "
        f"({logp['lines_per_s']:,.0f} lines/s)"
    )

    if engine["cores"] >= MIN_CORES_FOR_ASSERT:
        if engine["speedup"] < TARGET_SPEEDUP:
            print(
                f"FAIL: speedup {engine['speedup']:.2f}x < target {TARGET_SPEEDUP}x "
                f"on {engine['cores']} cores",
                file=sys.stderr,
            )
            return 1
        print(f"PASS: >= {TARGET_SPEEDUP}x on {engine['cores']} cores")
    else:
        print(
            f"SKIP assert: only {engine['cores']} cores (< {MIN_CORES_FOR_ASSERT}); "
            "speedup reported, not asserted"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
