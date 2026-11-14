"""Logging setup shared by Security-Scripts tools.

Data goes to stdout (so ``--output-format json`` can be piped cleanly); all
log messages go to stderr. ``configure`` maps the common ``--quiet``/
``--verbose`` flags onto log levels.
"""

from __future__ import annotations

import argparse
import logging
import sys

_DEFAULT_FORMAT = "%(levelname)s: %(message)s"


def configure(
    args: argparse.Namespace | None = None,
    *,
    name: str | None = None,
    quiet: bool | None = None,
    verbose: bool | None = None,
) -> logging.Logger:
    """Configure and return a logger writing to stderr.

    Verbosity is taken from ``args.quiet``/``args.verbose`` when ``args`` is
    given, or from the explicit ``quiet``/``verbose`` keywords. Default level
    is INFO; ``--quiet`` raises it to WARNING, ``--verbose`` lowers it to
    DEBUG.
    """
    if args is not None:
        quiet = getattr(args, "quiet", False) if quiet is None else quiet
        verbose = getattr(args, "verbose", False) if verbose is None else verbose

    if verbose:
        level = logging.DEBUG
    elif quiet:
        level = logging.WARNING
    else:
        level = logging.INFO

    logger = logging.getLogger(name)
    logger.setLevel(level)
    # Replace any existing handlers so repeated calls (e.g. in tests) don't
    # stack duplicate stderr handlers.
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
    handler = logging.StreamHandler(stream=sys.stderr)
    handler.setFormatter(logging.Formatter(_DEFAULT_FORMAT))
    handler.setLevel(level)
    logger.addHandler(handler)
    logger.propagate = False
    return logger
