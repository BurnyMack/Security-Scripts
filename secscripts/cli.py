"""Common argparse scaffolding for Security-Scripts tools.

Every directly-run tool should build its parser via :func:`build_parser` (or
call :func:`add_common_args` on its own parser) so the whole repo shares one
CLI contract:

* ``--version``                 print ``<prog> <version>`` and exit 0
* ``--output-format {json,csv,text}``  how structured results are rendered
* ``-q/--quiet`` / ``-v/--verbose``    logging verbosity (see :mod:`secscripts.log`)

Exit-code convention (documented once here, used everywhere):

* ``0``  success
* ``1``  runtime/usage error the tool handled and reported to stderr
* ``2``  argparse usage error (argparse's own default)
"""

from __future__ import annotations

import argparse

from . import __version__

OUTPUT_FORMATS = ("json", "csv", "text")

EXIT_OK = 0
EXIT_ERROR = 1


def add_common_args(
    parser: argparse.ArgumentParser,
    *,
    version: str | None = None,
    prog: str | None = None,
    default_format: str = "text",
    output_formats: tuple[str, ...] = OUTPUT_FORMATS,
) -> argparse.ArgumentParser:
    """Add the shared ``--version``/``--output-format``/verbosity flags.

    ``version`` defaults to the package version; pass a per-tool version to
    override. ``output_formats`` lets a tool offer extra choices beyond the
    stdout-renderable ``json``/``csv``/``text`` (e.g. LogParse adds ``xlsx``);
    ``default_format`` must be one of them. Returns the same parser for
    chaining.
    """
    ver = version if version is not None else __version__
    prog_name = prog or parser.prog
    if default_format not in output_formats:
        raise ValueError(
            f"default_format {default_format!r} not in output_formats {output_formats!r}"
        )
    parser.add_argument(
        "--version",
        action="version",
        version=f"{prog_name} {ver}",
        help="show program version and exit",
    )
    parser.add_argument(
        "--output-format",
        choices=output_formats,
        default=default_format,
        help=f"how to render structured output (default: {default_format})",
    )
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="only log warnings and errors",
    )
    verbosity.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="log debug-level detail",
    )
    return parser


def build_parser(
    description: str,
    *,
    version: str | None = None,
    prog: str | None = None,
    default_format: str = "text",
    output_formats: tuple[str, ...] = OUTPUT_FORMATS,
) -> argparse.ArgumentParser:
    """Create an ``ArgumentParser`` pre-loaded with the common flags."""
    parser = argparse.ArgumentParser(prog=prog, description=description)
    add_common_args(
        parser,
        version=version,
        prog=prog,
        default_format=default_format,
        output_formats=output_formats,
    )
    return parser
