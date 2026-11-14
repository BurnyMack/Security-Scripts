#!/usr/bin/env python3
"""
Read a specific inode's data block from an ext4 disk image and report it with
a SHA-256 of the extracted bytes.

Usage:
    inode_reader.py disk.img 12345
    inode_reader.py disk.img 12345 --output-format json

Requirements:
    pytsk3 (pip install pytsk3); secscripts (pip install -e .).
"""

import hashlib
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from secscripts.cli import EXIT_ERROR, EXIT_OK, build_parser  # noqa: E402
from secscripts.log import configure  # noqa: E402
from secscripts.output import emit  # noqa: E402


def extract_block(image, inode):
    """Return the raw bytes of ``inode`` in the ext4 image, or raise OSError."""
    import pytsk3  # imported lazily so the module loads without pytsk3

    img = pytsk3.Img_Info(image)
    fs = pytsk3.FS_Info(img)
    inode_obj = fs.open_meta(inode)
    return inode_obj.read_random(0, inode_obj.info.meta.size)


def main(argv=None):
    parser = build_parser(
        "Read an inode's data block from an ext4 disk image.",
        prog="inode_reader",
    )
    parser.add_argument("image", help="path to the disk image")
    parser.add_argument("inode", type=int, help="inode number to read")
    parser.add_argument(
        "--hex", action="store_true", help="include the block bytes (hex) in the output"
    )
    args = parser.parse_args(argv)
    logger = configure(args, name="inode_reader")

    try:
        block = extract_block(args.image, args.inode)
    except OSError as e:
        logger.error("error reading inode %s from %s: %s", args.inode, args.image, e)
        return EXIT_ERROR

    record = {
        "image": args.image,
        "inode": args.inode,
        "size": len(block),
        "sha256": hashlib.sha256(block).hexdigest(),
    }
    if args.hex:
        record["data_hex"] = block.hex()
    emit([record], args.output_format)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
