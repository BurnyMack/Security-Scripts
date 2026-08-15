#!/usr/bin/env python3
"""
Reads a specific inode's data block from an ext4 disk image.

Usage:
    inode_reader.py disk.img 12345

Requirements:
    pytsk3 (pip install pytsk3)
"""

import argparse
import sys

import pytsk3


def extract_block(image, inode):
    # Open the disk image
    try:
        img = pytsk3.Img_Info(image)
    except OSError as e:
        print(f"Error opening image: {e}", file=sys.stderr)
        sys.exit(1)

    # Open the filesystem on the image
    try:
        fs = pytsk3.FS_Info(img)
    except OSError as e:
        print(f"Error opening filesystem: {e}", file=sys.stderr)
        sys.exit(1)

    # Get the inode structure
    try:
        inode_obj = fs.open_meta(inode)
    except OSError as e:
        print(f"Error opening inode: {e}", file=sys.stderr)
        sys.exit(1)

    # Extract the data block
    block = inode_obj.read_random(0, inode_obj.info.meta.size)

    # Return the data block
    return block


def main():
    parser = argparse.ArgumentParser(
        description="Read a specific inode's data block from a disk image."
    )
    parser.add_argument("image", help="Path to the disk image")
    parser.add_argument("inode", type=int, help="Inode number to read")
    args = parser.parse_args()

    block = extract_block(args.image, args.inode)
    print(block)


if __name__ == "__main__":
    main()
