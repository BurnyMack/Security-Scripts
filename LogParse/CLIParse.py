#!/usr/bin/env python3
"""
CLI entry point for LogParse: parse a log file to json, csv, text, or xlsx.

Usage:
    python LogParse/CLIParse.py -p access.log                     # auto-detect, json to stdout
    python LogParse/CLIParse.py -p access.log --format apache --output-format csv
    python LogParse/CLIParse.py -p rules.yar --output-format xlsx -o out/

Requirements:
    secscripts (pip install -e .); pandas + XlsxWriter for --output-format xlsx.

Supported formats: apache, iis, syslog, cef, yara (and pcap, via dpkt). When
--format is omitted the format is auto-detected; detection fails loudly on an
unrecognised or ambiguous file rather than guessing.
"""

import sys
from pathlib import Path

# Allow running directly as `python LogParse/CLIParse.py` (repo root not on the
# path) as well as `python -m LogParse.CLIParse`.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from LogParse.LogParse import LogParse  # noqa: E402
from secscripts.cli import EXIT_ERROR, EXIT_OK, build_parser  # noqa: E402
from secscripts.log import configure  # noqa: E402
from secscripts.output import emit, render  # noqa: E402

_FORMAT_CHOICES = ["apache", "iis", "syslog", "cef", "pcap", "yara"]
_EXTENSION = {"json": "json", "csv": "csv", "text": "txt"}


def _write_stdout_format(records, output_format, output_dir, log_format, logger):
    """Render json/csv/text either to stdout or, if -o was given, to a file."""
    if output_dir is None:
        emit(records, output_format)
        return
    output_dir.mkdir(parents=True, exist_ok=True)
    ext = _EXTENSION[output_format]
    out_path = output_dir / f"{log_format}_parsed_data.{ext}"
    out_path.write_text(render(records, output_format) + "\n", encoding="utf-8")
    logger.info("Wrote %d records to %s", len(records), out_path)


def _write_xlsx(records, output_dir, log_format, logger):
    try:
        import pandas as pd
    except ImportError:
        logger.error("xlsx output needs pandas + XlsxWriter (pip install -e . then pandas)")
        raise
    target_dir = output_dir if output_dir is not None else Path.cwd()
    target_dir.mkdir(parents=True, exist_ok=True)
    out_path = target_dir / f"{log_format}_parsed_data.xlsx"
    pd.DataFrame(records).to_excel(out_path, sheet_name="Parsed Data", index=False)
    logger.info("Wrote %d records to %s", len(records), out_path)


def main(argv=None):
    parser = build_parser(
        "Parse a log file to json, csv, text, or xlsx.",
        prog="CLIParse",
        output_formats=("json", "csv", "text", "xlsx"),
        default_format="json",
    )
    parser.add_argument("-p", "--path", required=True, help="path to the log file to parse")
    parser.add_argument(
        "--format",
        choices=_FORMAT_CHOICES,
        help="log format (default: auto-detect)",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="output directory; for json/csv/text, omit to print to stdout "
        "(xlsx always writes a file)",
    )
    args = parser.parse_args(argv)
    logger = configure(args, name="CLIParse")

    path = Path(args.path)
    if not path.is_file():
        logger.error("no such file: %s", path)
        return EXIT_ERROR

    output_dir = Path(args.output) if args.output else None
    parser_obj = LogParse(str(path))

    try:
        log_format = args.format or parser_obj.detect()
        if not args.format:
            logger.info("auto-detected format: %s", log_format)
        records = parser_obj.parse(log_format)
    except ValueError as exc:
        logger.error("%s", exc)
        return EXIT_ERROR
    except OSError as exc:
        logger.error("could not read %s: %s", path, exc)
        return EXIT_ERROR

    if not records:
        logger.warning("no %s records matched in %s", log_format, path)

    try:
        if args.output_format == "xlsx":
            _write_xlsx(records, output_dir, log_format, logger)
        else:
            _write_stdout_format(records, args.output_format, output_dir, log_format, logger)
    except ImportError:
        return EXIT_ERROR
    except OSError as exc:
        logger.error("could not write output: %s", exc)
        return EXIT_ERROR

    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
