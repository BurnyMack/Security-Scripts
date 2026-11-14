"""Password-candidate generators shared by the crackers.

Three deterministic sources, so a run can be resumed by skipping the first N
candidates it already tried:

* :func:`from_wordlist` — stream a wordlist file line by line.
* :func:`from_mask` — expand a hashcat-style mask over its keyspace.
* :func:`apply_rules` — transform each word with a subset of hashcat rules.

Mask charsets (``?`` placeholders), hashcat-compatible:

===== ======================================
token  characters
===== ======================================
``?l`` ``abcdefghijklmnopqrstuvwxyz``
``?u`` ``ABCDEFGHIJKLMNOPQRSTUVWXYZ``
``?d`` ``0123456789``
``?s`` `` !"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~``
``?a`` ``?l?u?d?s``
``??`` a literal ``?``
===== ======================================

Rule ops (applied left to right within one rule string), a documented subset
of hashcat's rule language:

===== ======================================
op     effect
===== ======================================
``:``  no-op (try the word unchanged)
``l``  lowercase
``u``  uppercase
``c``  capitalize (first upper, rest lower)
``t``  toggle case of every character
``r``  reverse
``d``  duplicate (``word`` -> ``wordword``)
``$X`` append character ``X``
``^X`` prepend character ``X``
===== ======================================
"""

from __future__ import annotations

import itertools
import string
from collections.abc import Iterable, Iterator

MASK_CHARSETS = {
    "l": string.ascii_lowercase,
    "u": string.ascii_uppercase,
    "d": string.digits,
    "s": " !\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~",
}
MASK_CHARSETS["a"] = (
    MASK_CHARSETS["l"] + MASK_CHARSETS["u"] + MASK_CHARSETS["d"] + MASK_CHARSETS["s"]
)


def from_wordlist(path: str) -> Iterator[str]:
    """Yield each stripped, non-empty line of a wordlist file."""
    with open(path, encoding="utf-8", errors="replace") as handle:
        for line in handle:
            word = line.rstrip("\r\n")
            if word:
                yield word


def _mask_positions(mask: str) -> list[str]:
    """Split a mask into per-position charsets (each a string of choices)."""
    positions: list[str] = []
    i = 0
    while i < len(mask):
        char = mask[i]
        if char == "?":
            if i + 1 >= len(mask):
                raise ValueError(f"dangling '?' at end of mask: {mask!r}")
            token = mask[i + 1]
            if token == "?":
                positions.append("?")
            elif token in MASK_CHARSETS:
                positions.append(MASK_CHARSETS[token])
            else:
                raise ValueError(f"unknown mask token '?{token}' in {mask!r}")
            i += 2
        else:
            positions.append(char)  # literal character, single choice
            i += 1
    return positions


def mask_keyspace(mask: str) -> int:
    """Return how many candidates a mask expands to."""
    size = 1
    for choices in _mask_positions(mask):
        size *= len(choices)
    return size


def from_mask(mask: str) -> Iterator[str]:
    """Yield every candidate in a mask's keyspace, in odometer order."""
    positions = _mask_positions(mask)
    for combo in itertools.product(*positions):
        yield "".join(combo)


def _apply_one_rule(word: str, rule: str) -> str:
    result = word
    i = 0
    while i < len(rule):
        op = rule[i]
        if op == ":":
            pass
        elif op == "l":
            result = result.lower()
        elif op == "u":
            result = result.upper()
        elif op == "c":
            result = result.capitalize()
        elif op == "t":
            result = result.swapcase()
        elif op == "r":
            result = result[::-1]
        elif op == "d":
            result = result + result
        elif op == "$":
            if i + 1 >= len(rule):
                raise ValueError(f"'$' needs a character in rule {rule!r}")
            result = result + rule[i + 1]
            i += 1
        elif op == "^":
            if i + 1 >= len(rule):
                raise ValueError(f"'^' needs a character in rule {rule!r}")
            result = rule[i + 1] + result
            i += 1
        else:
            raise ValueError(f"unknown rule op {op!r} in rule {rule!r}")
        i += 1
    return result


def apply_rules(words: Iterable[str], rules: list[str]) -> Iterator[str]:
    """For each word, yield one candidate per rule (in word-then-rule order)."""
    for word in words:
        for rule in rules:
            yield _apply_one_rule(word, rule)


def load_rules(path: str) -> list[str]:
    """Read a rules file: one rule per line, ``#`` comments and blanks skipped."""
    rules: list[str] = []
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                rules.append(stripped)
    return rules
