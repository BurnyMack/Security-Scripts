"""Tests for candidate generators (wordlist, mask, rules)."""

import pytest

from secscripts import candidates as cand


def test_from_wordlist_drops_newlines_keeps_spaces_skips_blanks(tmp_path):
    wl = tmp_path / "words.txt"
    wl.write_text("alpha\n\nbeta \n\ngamma\n")
    # Only the line terminator is removed; an embedded/trailing space is a
    # legitimate password character and is preserved. Blank lines are skipped.
    assert list(cand.from_wordlist(str(wl))) == ["alpha", "beta ", "gamma"]


def test_mask_keyspace_and_expansion():
    assert cand.mask_keyspace("?d?d") == 100
    out = list(cand.from_mask("?d"))
    assert out == [str(d) for d in range(10)]


def test_mask_literal_and_escaped_question():
    assert list(cand.from_mask("a?d")) == [f"a{d}" for d in range(10)]
    assert list(cand.from_mask("??")) == ["?"]


def test_mask_bad_token_raises():
    with pytest.raises(ValueError):
        list(cand.from_mask("?z"))
    with pytest.raises(ValueError):
        list(cand.from_mask("abc?"))


def test_rules_transforms():
    words = ["Pass"]
    assert list(cand.apply_rules(words, [":"])) == ["Pass"]
    assert list(cand.apply_rules(words, ["l"])) == ["pass"]
    assert list(cand.apply_rules(words, ["u"])) == ["PASS"]
    assert list(cand.apply_rules(words, ["c"])) == ["Pass"]
    assert list(cand.apply_rules(words, ["t"])) == ["pASS"]
    assert list(cand.apply_rules(words, ["r"])) == ["ssaP"]
    assert list(cand.apply_rules(words, ["d"])) == ["PassPass"]
    assert list(cand.apply_rules(words, ["$1"])) == ["Pass1"]
    assert list(cand.apply_rules(words, ["^x"])) == ["xPass"]
    # Ops combine left to right.
    assert list(cand.apply_rules(words, ["l$1"])) == ["pass1"]


def test_rules_bad_op_raises():
    with pytest.raises(ValueError):
        list(cand.apply_rules(["a"], ["z"]))
    with pytest.raises(ValueError):
        list(cand.apply_rules(["a"], ["$"]))


def test_load_rules_skips_comments(tmp_path):
    rf = tmp_path / "r.rule"
    rf.write_text("# comment\n:\n\nl\n$1\n")
    assert cand.load_rules(str(rf)) == [":", "l", "$1"]
