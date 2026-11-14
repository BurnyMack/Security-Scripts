# Benchmarks

Measures the performance work from the tooling-modernization spec (AC-5).

## What it measures

- **Crack engine** (`secscripts.crack.search`, shared by HashCrack and
  ZipCrack): wall-clock time to scan a fixed, CPU-bound keyspace serially
  (1 process) vs. across all CPUs, and the resulting speedup. The workload
  (`benchmarks/matchers.CostMatcher`) does fixed per-candidate hashing and
  never matches, so the full keyspace is scanned — a fair, deterministic
  measure of parallel scaling. Real crypt-scheme/NTLM cracking is CPU-bound in
  the same way.
- **LogParse** throughput (lines/second). LogParse is streamed (line by line),
  not parallelised, so it's reported for information, without a speedup target.

## Running

```
pip install -e .          # from the repo root
python benchmarks/run.py  # defaults: 20000 candidates, 400 iters, 100k log lines
python benchmarks/run.py --candidates 50000 --iterations 400 --log-lines 500000
```

On a machine with **>= 4 cores** the script asserts a **>= 3x speedup** and
exits non-zero if it isn't met (this is the AC-5 gate, and runs as its own CI
step). With fewer than 4 cores it reports the speedup without asserting.

The `pytest` tests under `benchmarks/tests/` only check that the harness runs
(both paths, a positive speedup) at tiny sizes — they do not assert a ratio,
since small-workload ratios are noisy. Use `run.py` for the real figure.

## Example

```
Crack engine (secscripts.crack.search; used by HashCrack + ZipCrack)
  cores            : 18
  serial  (1 proc) : 1.353 s
  parallel (N proc): 0.222 s
  speedup          : 6.09x
LogParse (streamed, single-threaded)
  parsed 200000/200000 lines in 0.153 s (1,303,185 lines/s)
PASS: >= 3.0x on 18 cores
```
