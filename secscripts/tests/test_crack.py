"""Tests for the parallel search engine with resume."""

from secscripts import candidates as cand
from secscripts.crack import search


class EqualsMatcher:
    """Module-level (picklable) matcher: true when candidate == target.

    Defined at module scope so it survives pickling to spawned workers on the
    multiprocessing path.
    """

    def __init__(self, target):
        self.target = target

    def __call__(self, candidate):
        return candidate == self.target


def test_search_finds_in_process():
    result = search(cand.from_mask("?d?d"), EqualsMatcher("42"), total=100, workers=1)
    assert result.found
    assert result.password == "42"


def test_search_not_found():
    result = search(cand.from_mask("?d"), EqualsMatcher("zz"), total=10, workers=1)
    assert not result.found
    assert result.password is None
    assert result.tried == 10


def test_search_parallel_path():
    # Exercises the real multiprocessing pool (workers>1).
    result = search(
        cand.from_mask("?d?d?d"),
        EqualsMatcher("077"),
        total=1000,
        workers=2,
        chunk_size=50,
    )
    assert result.found
    assert result.password == "077"


def test_resume_skips_tried_candidates(tmp_path):
    resume = tmp_path / "state.json"
    # Pre-seed a resume file as if 50 candidates were already tried.
    resume.write_text('{"tried": 50}')
    # Target "07" is at index 7 — already skipped — so a resumed run misses it.
    result = search(
        cand.from_mask("?d?d"),
        EqualsMatcher("07"),
        total=100,
        workers=1,
        chunk_size=10,
        resume_path=str(resume),
    )
    assert not result.found
    # A target beyond the skip point is still found.
    resume.write_text('{"tried": 50}')
    result = search(
        cand.from_mask("?d?d"),
        EqualsMatcher("77"),
        total=100,
        workers=1,
        chunk_size=10,
        resume_path=str(resume),
    )
    assert result.found and result.password == "77"


def test_resume_cleared_on_success(tmp_path):
    resume = tmp_path / "state.json"
    result = search(
        cand.from_mask("?d?d"),
        EqualsMatcher("05"),
        total=100,
        workers=1,
        resume_path=str(resume),
    )
    assert result.found
    assert not resume.exists()  # cleared on success


def test_resume_written_on_exhaustion_then_cleared(tmp_path):
    resume = tmp_path / "state.json"
    result = search(
        cand.from_mask("?d"),
        EqualsMatcher("nope"),
        total=10,
        workers=1,
        resume_path=str(resume),
    )
    assert not result.found
    assert not resume.exists()  # cleared on clean exhaustion
