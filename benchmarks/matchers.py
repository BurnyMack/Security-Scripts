"""Picklable, CPU-bound matchers for the performance benchmark.

Defined at module scope (``benchmarks.matchers``) so they survive pickling to
workers under the ``spawn`` start method used on macOS. ``CostMatcher`` does a
fixed amount of hashing per candidate and never matches, so a search scans the
whole keyspace — a fair, deterministic measure of how the shared crack engine
(:func:`secscripts.crack.search`, used by HashCrack and ZipCrack) scales across
processes. Real crypt-scheme/NTLM cracking is CPU-bound in the same way.
"""

import hashlib


class CostMatcher:
    def __init__(self, iterations: int = 400):
        self.iterations = iterations

    def __call__(self, candidate: str) -> bool:
        data = candidate.encode("utf-8", "surrogatepass")
        for _ in range(self.iterations):
            data = hashlib.sha256(data).digest()
        return False  # never matches, so the full keyspace is scanned
