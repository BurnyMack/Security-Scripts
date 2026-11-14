"""Fast correctness tests for the benchmark harness.

These run at tiny sizes so they're CI-friendly and deterministic. They verify
the harness works (both the serial and parallel paths run and produce a
speedup number); they deliberately do NOT assert a specific speedup ratio,
because small-workload ratios are dominated by pool-startup/IPC overhead and
vary with runner load. The real >= 3x speedup gate (AC-5) is `benchmarks/run.py`
at a representative size, run as its own CI step.
"""

import tempfile

from benchmarks import run
from benchmarks.fixtures import make_apache_log, make_wordlist


def test_make_wordlist(tmp_path):
    path = make_wordlist(tmp_path / "w.txt", 100)
    assert sum(1 for _ in open(path)) == 100


def test_make_apache_log_parses(tmp_path):
    from LogParse.LogParse import LogParse

    path = make_apache_log(tmp_path / "a.log", 50)
    assert len(LogParse(str(path)).parse("apache")) == 50


def test_benchmark_engine_runs_both_paths():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Tiny workload: just prove both paths run and a ratio is produced.
        result = run.benchmark_engine(candidates=2000, iterations=100, tmpdir=tmpdir)
    assert result["serial_s"] > 0
    assert result["parallel_s"] > 0
    assert result["speedup"] > 0


def test_benchmark_logparse_throughput():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = run.benchmark_logparse(lines=2000, tmpdir=tmpdir)
    assert result["parsed"] == 2000
    assert result["lines_per_s"] > 0
