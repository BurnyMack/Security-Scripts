#!/usr/bin/env python3
"""
This script extracts some key exif data from a docx file.
It is not a replacement for exiftool or similar, but it can be used to make exifdata available for other tools.

Usage:
    exifcheck.py -i report.docx

Requirements:
    python-docx (pip install python-docx)
"""

import argparse
import sys

import docx


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


def main():
    parser = argparse.ArgumentParser(description="Extract key exif data from a docx file.")
    parser.add_argument("-i", "--input", required=True, help="Path to the .docx file to inspect")
    args = parser.parse_args()

    try:
        doc = docx.Document(args.input)
    except Exception as e:
        print(f"Error opening {args.input}: {e}", file=sys.stderr)
        sys.exit(1)

    print("Opening : " + args.input)
    metadata_dict = meta(doc)
    print("Author: " + str(metadata_dict["author"]))
    print("Created: " + str(metadata_dict["created"]))
    print("Modified: " + str(metadata_dict["modified"]))
    print("Title: " + str(metadata_dict["title"]))
    print("Language: " + str(metadata_dict["language"]))


if __name__ == "__main__":
    main()
