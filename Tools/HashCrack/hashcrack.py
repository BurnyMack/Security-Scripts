#!/usr/bin/env python3
"""
Brute-force a password hash against a wordlist, mask, or rule-mutated wordlist.

Usage:
    python hashcrack.py '$6$abc...' --wordlist rockyou.txt
    python hashcrack.py 5f4dcc3b5aa765d61d8327deb882cf99 --mask '?l?l?l?l?l'
    python hashcrack.py <ntlm> --type ntlm --wordlist words.txt --rules best.rule

Requirements:
    secscripts (pip install -e .); passlib for crypt/NTLM/LM schemes.

Supported hash types (``--type`` optional; auto-detected from the hash when
omitted): md5, sha1, sha256, sha512 (raw hex), md5crypt, sha256crypt,
sha512crypt, bcrypt ("$...$" crypt strings), and ntlm / lm (must be given with
--type, since they look like a 32-char hex md5). Auto-detection maps a bare
32-char hex hash to md5.
"""

import sys
from dataclasses import dataclass
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import hashlib  # noqa: E402

from secscripts import candidates as cand  # noqa: E402
from secscripts.cli import EXIT_ERROR, EXIT_OK, build_parser  # noqa: E402
from secscripts.crack import search  # noqa: E402
from secscripts.log import configure  # noqa: E402

RAW_ALGOS = {"md5", "sha1", "sha256", "sha512"}
CRYPT_ALGOS = {"md5crypt", "sha256crypt", "sha512crypt", "bcrypt"}
WINDOWS_ALGOS = {"ntlm", "lm"}
ALL_TYPES = sorted(RAW_ALGOS | CRYPT_ALGOS | WINDOWS_ALGOS)

_RAW_LEN = {32: "md5", 40: "sha1", 64: "sha256", 128: "sha512"}


def detect_type(hash_value: str) -> str:
    """Infer the hash type from its prefix/length, or raise ValueError."""
    if hash_value.startswith(("$2a$", "$2b$", "$2y$")):
        return "bcrypt"
    if hash_value.startswith("$6$"):
        return "sha512crypt"
    if hash_value.startswith("$5$"):
        return "sha256crypt"
    if hash_value.startswith("$1$"):
        return "md5crypt"
    stripped = hash_value.strip()
    if all(c in "0123456789abcdefABCDEF" for c in stripped) and len(stripped) in _RAW_LEN:
        # A 32-char hex hash is ambiguous (md5 vs NTLM/LM); default to md5.
        return _RAW_LEN[len(stripped)]
    raise ValueError(f"could not auto-detect hash type for {hash_value!r}; pass --type")


@dataclass
class HashMatcher:
    """Picklable matcher: checks a candidate against a target hash.

    Holds only strings so it pickles cleanly to worker processes; the actual
    verification is recreated on each call.
    """

    hash_type: str
    target: str

    def __call__(self, candidate: str) -> bool:
        htype = self.hash_type
        if htype in RAW_ALGOS:
            digest = hashlib.new(htype, candidate.encode("utf-8", "surrogatepass"))
            return digest.hexdigest().lower() == self.target.strip().lower()
        if htype in CRYPT_ALGOS or htype in WINDOWS_ALGOS:
            scheme = _passlib_scheme(htype)
            try:
                return scheme.verify(candidate, self.target)
            except ValueError:
                return False
        raise ValueError(f"unknown hash type: {htype}")


def _passlib_scheme(htype: str):
    from passlib import hash as passlib_hash

    return {
        "md5crypt": passlib_hash.md5_crypt,
        "sha256crypt": passlib_hash.sha256_crypt,
        "sha512crypt": passlib_hash.sha512_crypt,
        "bcrypt": passlib_hash.bcrypt,
        "ntlm": passlib_hash.nthash,
        "lm": passlib_hash.lmhash,
    }[htype]


def _build_candidates(args, logger):
    """Return (iterator, total-or-None) for the chosen attack mode."""
    if args.mask:
        total = cand.mask_keyspace(args.mask)
        return cand.from_mask(args.mask), total
    words = cand.from_wordlist(args.wordlist)
    if args.rules:
        rules = cand.load_rules(args.rules)
        logger.info("loaded %d rules", len(rules))
        # Total is wordlist length * rule count; count lines cheaply up front.
        line_count = sum(1 for _ in cand.from_wordlist(args.wordlist))
        return cand.apply_rules(words, rules), line_count * len(rules)
    total = sum(1 for _ in cand.from_wordlist(args.wordlist))
    return cand.from_wordlist(args.wordlist), total


def main(argv=None):
    parser = build_parser(
        "Brute-force a password hash with a wordlist, mask, or rules.",
        prog="hashcrack",
    )
    parser.add_argument("hash", help="the hash to crack")
    parser.add_argument("--type", choices=ALL_TYPES, help="hash type (default: auto-detect)")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("-w", "--wordlist", help="path to a wordlist file")
    mode.add_argument("-m", "--mask", help="a hashcat-style mask, e.g. '?l?l?d?d'")
    parser.add_argument("--rules", help="path to a rules file (wordlist mode only)")
    parser.add_argument("--workers", type=int, help="worker processes (default: all CPUs)")
    parser.add_argument("--resume", help="path to a resume state file")
    args = parser.parse_args(argv)
    logger = configure(args, name="hashcrack")

    if args.rules and not args.wordlist:
        logger.error("--rules requires --wordlist")
        return EXIT_ERROR

    try:
        hash_type = args.type or detect_type(args.hash)
    except ValueError as exc:
        logger.error("%s", exc)
        return EXIT_ERROR
    logger.info("hash type: %s", hash_type)

    try:
        candidates, total = _build_candidates(args, logger)
    except OSError as exc:
        logger.error("could not read input: %s", exc)
        return EXIT_ERROR
    except ValueError as exc:
        logger.error("%s", exc)
        return EXIT_ERROR

    matcher = HashMatcher(hash_type, args.hash)
    result = search(
        candidates,
        matcher,
        total=total,
        workers=args.workers,
        resume_path=args.resume,
    )

    if result.found:
        print(f"Password found: {result.password}")
        return EXIT_OK
    logger.warning("password not found after %d candidates", result.tried)
    return EXIT_ERROR


if __name__ == "__main__":
    sys.exit(main())
