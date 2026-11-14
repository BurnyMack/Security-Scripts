"""Tests for the progress bar."""

import io

from secscripts.progress import Progress


def test_disabled_when_not_a_tty():
    buffer = io.StringIO()  # not a TTY
    bar = Progress(total=10, stream=buffer)
    assert bar.enabled is False
    for _ in range(10):
        bar.update()
    bar.close()
    # Counting still works, but nothing is drawn.
    assert bar.count == 10
    assert buffer.getvalue() == ""


def test_draws_when_enabled():
    buffer = io.StringIO()
    bar = Progress(total=4, stream=buffer, enabled=True, min_interval=0.0)
    for _ in range(4):
        bar.update()
    bar.close()
    out = buffer.getvalue()
    assert "4/4" in out
    assert "100.0%" in out
    assert out.endswith("\n")


def test_unknown_total_shows_count():
    buffer = io.StringIO()
    bar = Progress(total=None, stream=buffer, enabled=True, min_interval=0.0)
    bar.update(5)
    bar.close()
    assert "5 done" in buffer.getvalue()


def test_fmt_durations():
    assert Progress._fmt(5) == "5s"
    assert Progress._fmt(65) == "1m05s"
    assert Progress._fmt(3725) == "1h02m05s"


def test_context_manager_closes():
    buffer = io.StringIO()
    with Progress(total=2, stream=buffer, enabled=True, min_interval=0.0) as bar:
        bar.update()
        bar.update()
    assert buffer.getvalue().endswith("\n")
