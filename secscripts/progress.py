"""A tiny stdlib-only progress bar with ETA for long-running tools.

The crackers use this to show throughput over a wordlist/keyspace. It writes
to stderr so it never pollutes piped data output, and degrades to nothing when
stderr is not a TTY (e.g. under CI or when redirected), so logs stay clean.
"""

from __future__ import annotations

import sys
import time
from typing import TextIO


class Progress:
    """Render a single-line progress bar with rate and ETA.

    Parameters
    ----------
    total:
        Total number of items, or ``None`` when unknown (shows a spinner-style
        count without a bar/ETA).
    stream:
        Where to draw (default stderr).
    enabled:
        Force on/off. When ``None`` (default), auto-enables only if ``stream``
        is a TTY.
    min_interval:
        Minimum seconds between redraws, to avoid thrashing on fast loops.
    """

    def __init__(
        self,
        total: int | None = None,
        *,
        stream: TextIO | None = None,
        enabled: bool | None = None,
        min_interval: float = 0.1,
    ) -> None:
        self.total = total
        self.stream = stream if stream is not None else sys.stderr
        if enabled is None:
            enabled = bool(getattr(self.stream, "isatty", lambda: False)())
        self.enabled = enabled
        self.min_interval = min_interval
        self.count = 0
        self._start = time.monotonic()
        self._last_draw = 0.0

    def update(self, step: int = 1) -> None:
        """Advance the counter by ``step`` and redraw if due."""
        self.count += step
        if not self.enabled:
            return
        now = time.monotonic()
        is_last = self.total is not None and self.count >= self.total
        if not is_last and (now - self._last_draw) < self.min_interval:
            return
        self._last_draw = now
        self._draw(now)

    def _draw(self, now: float) -> None:
        elapsed = max(now - self._start, 1e-9)
        rate = self.count / elapsed
        if self.total:
            fraction = min(self.count / self.total, 1.0)
            filled = int(fraction * 30)
            bar = "#" * filled + "-" * (30 - filled)
            remaining = (self.total - self.count) / rate if rate > 0 else 0.0
            msg = (
                f"\r[{bar}] {self.count}/{self.total} "
                f"({fraction * 100:5.1f}%) {rate:,.0f}/s ETA {self._fmt(remaining)}"
            )
        else:
            msg = f"\r{self.count} done {rate:,.0f}/s elapsed {self._fmt(elapsed)}"
        self.stream.write(msg)
        self.stream.flush()

    def close(self) -> None:
        """Finish the line so later output starts fresh."""
        if self.enabled:
            self.stream.write("\n")
            self.stream.flush()

    def __enter__(self) -> Progress:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    @staticmethod
    def _fmt(seconds: float) -> str:
        seconds = int(seconds)
        hours, remainder = divmod(seconds, 3600)
        minutes, secs = divmod(remainder, 60)
        if hours:
            return f"{hours}h{minutes:02d}m{secs:02d}s"
        if minutes:
            return f"{minutes}m{secs:02d}s"
        return f"{secs}s"
