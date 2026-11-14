#!/usr/bin/env python3
"""
Summarise a CSV/XLSX file: per-column describe() statistics and null counts.

Usage:
    python XLanalyser.py data.csv                       # text summary to stdout
    python XLanalyser.py data.xlsx --output-format json
    python XLanalyser.py data.csv --output-format xlsx -o summary.xlsx

Requirements:
    pandas; secscripts (pip install -e .); openpyxl for .xlsx input,
    XlsxWriter for .xlsx output.

Importable as a library (``XLanalyser`` class) or run as a CLI.
"""

import sys
from pathlib import Path

import pandas as pd

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from secscripts.cli import EXIT_ERROR, EXIT_OK, build_parser  # noqa: E402
from secscripts.log import configure  # noqa: E402
from secscripts.output import emit  # noqa: E402


class XLanalyser:
    def __init__(self, input_file):
        self.input_file = input_file
        self.data = None

    def load_data(self):
        if self.input_file.endswith(".csv"):
            self.data = pd.read_csv(self.input_file)
        elif self.input_file.endswith(".xlsx"):
            self.data = pd.read_excel(self.input_file)
        else:
            raise ValueError("Unsupported file format. Please provide a CSV or XLSX file.")

    def read(self):
        if self.data is None:
            raise ValueError("Data has not been loaded. Call load_data() first.")
        summary_stats = self.data.describe()
        null_counts = self.data.isnull().sum()
        return summary_stats, null_counts

    def records(self):
        """Return a list of per-column dicts (describe() stats + null count)."""
        summary_stats, null_counts = self.read()
        table = summary_stats.T
        table["null_count"] = null_counts
        table = table.reset_index().rename(columns={"index": "column"})
        return [
            {k: (None if pd.isna(v) else v) for k, v in row.items()}
            for row in table.to_dict(orient="records")
        ]

    def save(self, output_file):
        if output_file.endswith(".csv"):
            summary_stats, _null_counts = self.read()
            summary_stats.to_csv(output_file)
        elif output_file.endswith(".xlsx"):
            summary_stats, null_counts = self.read()
            with pd.ExcelWriter(output_file) as writer:
                summary_stats.to_excel(writer, sheet_name="Summary Stats")
                null_counts.to_excel(writer, sheet_name="Null Counts")
        else:
            raise ValueError("Unsupported output file format. Please use CSV or XLSX.")


def main(argv=None):
    parser = build_parser(
        "Summarise a CSV/XLSX file: describe() stats and null counts.",
        prog="XLanalyser",
        output_formats=("json", "csv", "text", "xlsx"),
        default_format="text",
    )
    parser.add_argument("input_file", help="path to a .csv or .xlsx file")
    parser.add_argument(
        "-o",
        "--output",
        help="output file for --output-format xlsx (default: summary.xlsx)",
    )
    args = parser.parse_args(argv)
    logger = configure(args, name="XLanalyser")

    analyser = XLanalyser(args.input_file)
    try:
        analyser.load_data()
    except (OSError, ValueError) as exc:
        logger.error("%s", exc)
        return EXIT_ERROR
    except ImportError as exc:  # missing xlsx engine
        logger.error("missing dependency: %s", exc)
        return EXIT_ERROR

    try:
        if args.output_format == "xlsx":
            out = args.output or "summary.xlsx"
            if not out.endswith(".xlsx"):
                out += ".xlsx"
            analyser.save(out)
            logger.info("wrote summary to %s", out)
        else:
            emit(analyser.records(), args.output_format)
    except (OSError, ValueError) as exc:
        logger.error("%s", exc)
        return EXIT_ERROR

    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
