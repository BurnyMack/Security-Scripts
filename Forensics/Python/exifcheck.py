#!/usr/bin/env python3
"""
Extract key document metadata (core properties) from a .docx file.
Not a replacement for exiftool, but it makes the metadata available to other
tools in json/csv/text form.

Usage:
    exifcheck.py -i report.docx
    exifcheck.py -i report.docx --output-format json

Requirements:
    python-docx (pip install python-docx); secscripts (pip install -e .).
"""

import sys
from pathlib import Path

import docx
from docx.opc.exceptions import PackageNotFoundError

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from secscripts.cli import EXIT_ERROR, EXIT_OK, build_parser  # noqa: E402
from secscripts.log import configure  # noqa: E402
from secscripts.output import emit  # noqa: E402


def meta(doc):
    metadata = {}
    prop = doc.core_properties
    metadata["author"] = prop.author
    metadata["category"] = prop.category
    metadata["comments"] = prop.comments
    metadata["content_status"] = prop.content_status
    metadata["created"] = prop.created
    metadata["identifier"] = prop.identifier
    metadata["keywords"] = prop.keywords
    metadata["language"] = prop.language
    metadata["modified"] = prop.modified
    metadata["subject"] = prop.subject
    metadata["title"] = prop.title
    metadata["version"] = prop.version
    return metadata


def main(argv=None):
    parser = build_parser(
        "Extract core-property metadata from a .docx file.",
        prog="exifcheck",
    )
    parser.add_argument("-i", "--input", required=True, help="path to the .docx file to inspect")
    args = parser.parse_args(argv)
    logger = configure(args, name="exifcheck")

    try:
        doc = docx.Document(args.input)
    except (OSError, PackageNotFoundError) as e:
        logger.error("error opening %s: %s", args.input, e)
        return EXIT_ERROR

    logger.info("inspecting %s", args.input)
    metadata = {k: (None if v is None else str(v)) for k, v in meta(doc).items()}
    emit([metadata], args.output_format)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
