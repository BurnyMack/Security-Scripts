"""Tests for the shared CLI scaffolding."""

import argparse

import pytest

from secscripts import __version__
from secscripts.cli import OUTPUT_FORMATS, add_common_args, build_parser


def test_build_parser_has_common_flags():
    parser = build_parser("demo tool", prog="demo")
    args = parser.parse_args(["--output-format", "json", "--verbose"])
    assert args.output_format == "json"
    assert args.verbose is True
    assert args.quiet is False


def test_default_output_format_is_text():
    parser = build_parser("demo tool")
    args = parser.parse_args([])
    assert args.output_format == "text"


def test_quiet_and_verbose_are_mutually_exclusive():
    parser = build_parser("demo tool")
    with pytest.raises(SystemExit):
        parser.parse_args(["--quiet", "--verbose"])


def test_version_action_exits(capsys):
    parser = build_parser("demo tool", prog="demo", version="9.9.9")
    with pytest.raises(SystemExit) as excinfo:
        parser.parse_args(["--version"])
    assert excinfo.value.code == 0
    assert "demo 9.9.9" in capsys.readouterr().out


def test_version_defaults_to_package_version(capsys):
    parser = build_parser("demo tool", prog="demo")
    with pytest.raises(SystemExit):
        parser.parse_args(["--version"])
    assert __version__ in capsys.readouterr().out


def test_add_common_args_on_existing_parser():
    parser = argparse.ArgumentParser(prog="own")
    parser.add_argument("target")
    add_common_args(parser)
    args = parser.parse_args(["x", "--output-format", "csv"])
    assert args.target == "x"
    assert args.output_format == "csv"


def test_bad_output_format_rejected():
    parser = build_parser("demo tool")
    with pytest.raises(SystemExit):
        parser.parse_args(["--output-format", "yaml"])
    assert "yaml" not in OUTPUT_FORMATS


def test_custom_output_formats():
    parser = build_parser(
        "demo tool",
        output_formats=("json", "csv", "text", "xlsx"),
        default_format="xlsx",
    )
    args = parser.parse_args([])
    assert args.output_format == "xlsx"
    args = parser.parse_args(["--output-format", "xlsx"])
    assert args.output_format == "xlsx"


def test_default_format_must_be_a_choice():
    with pytest.raises(ValueError):
        build_parser("demo tool", default_format="xlsx")  # not in default formats
