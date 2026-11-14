"""Shared helpers for Security-Scripts command-line tools.

This is the one intentional cross-folder abstraction in the repo (see
CONTRIBUTING.md): a small, stdlib-only package that gives every tool the same
CLI contract, output formats, logging, hashing, and progress display, so the
tools stay consistent without each re-implementing boilerplate.

Install in editable mode from the repo root:

    pip install -e .

then import the pieces you need, e.g.::

    from secscripts.cli import build_parser, add_common_args
    from secscripts.output import emit
"""

__version__ = "1.0.0"
