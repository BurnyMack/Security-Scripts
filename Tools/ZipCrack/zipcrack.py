#!/usr/bin/env python3
"""
Brute-force a password-protected zip against a wordlist, mask, or rules.

Usage:
    python zipcrack.py archive.zip --wordlist rockyou.txt
    python zipcrack.py archive.zip --mask '?d?d?d?d'
    python zipcrack.py archive.zip --wordlist words.txt --rules best.rule

Requirements:
    secscripts (pip install -e .).
"""

import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from secscripts import candidates as cand  # noqa: E402
from secscripts.cli import EXIT_ERROR, EXIT_OK, build_parser  # noqa: E402
from secscripts.crack import search  # noqa: E402
from secscripts.log import configure  # noqa: E402


@dataclass
class ZipMatcher:
    """Picklable matcher: true when a password decrypts the zip's first entry.

    Holds only the archive path and the member name, so it pickles to worker
    processes; each worker opens its own handle.
    """

    zip_path: str
    member: str

    def __call__(self, candidate: str) -> bool:
        try:
            with zipfile.ZipFile(self.zip_path) as archive:
                # Reading one encrypted member verifies the password via its
                # CRC; a wrong password raises RuntimeError/BadZipFile.
                archive.read(self.member, pwd=candidate.encode("utf-8", "surrogatepass"))
            return True
        except (RuntimeError, zipfile.BadZipFile):
            return False


def _first_encrypted_member(archive: zipfile.ZipFile) -> str | None:
    for info in archive.infolist():
        if info.flag_bits & 0x1 and not info.is_dir():
            return info.filename
    return None


def _build_candidates(args, logger):
    if args.mask:
        return cand.from_mask(args.mask), cand.mask_keyspace(args.mask)
    if args.rules:
        rules = cand.load_rules(args.rules)
        logger.info("loaded %d rules", len(rules))
        line_count = sum(1 for _ in cand.from_wordlist(args.wordlist))
        return cand.apply_rules(cand.from_wordlist(args.wordlist), rules), line_count * len(rules)
    total = sum(1 for _ in cand.from_wordlist(args.wordlist))
    return cand.from_wordlist(args.wordlist), total


def main(argv=None):
    parser = build_parser(
        "Brute-force a zip password with a wordlist, mask, or rules.",
        prog="zipcrack",
    )
    parser.add_argument("zipfile", help="path to the password-protected zip")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("-w", "--wordlist", help="path to a wordlist file")
    mode.add_argument("-m", "--mask", help="a hashcat-style mask, e.g. '?d?d?d?d'")
    parser.add_argument("--rules", help="path to a rules file (wordlist mode only)")
    parser.add_argument("--workers", type=int, help="worker processes (default: all CPUs)")
    parser.add_argument("--resume", help="path to a resume state file")
    args = parser.parse_args(argv)
    logger = configure(args, name="zipcrack")

    if args.rules and not args.wordlist:
        logger.error("--rules requires --wordlist")
        return EXIT_ERROR

    try:
        with zipfile.ZipFile(args.zipfile) as archive:
            member = _first_encrypted_member(archive)
    except (OSError, zipfile.BadZipFile) as exc:
        logger.error("could not open zip %s: %s", args.zipfile, exc)
        return EXIT_ERROR

    if member is None:
        logger.error("no encrypted entries found in %s", args.zipfile)
        return EXIT_ERROR

    try:
        candidates, total = _build_candidates(args, logger)
    except (OSError, ValueError) as exc:
        logger.error("%s", exc)
        return EXIT_ERROR

    matcher = ZipMatcher(args.zipfile, member)
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
