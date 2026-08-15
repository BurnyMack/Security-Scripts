#!/bin/bash
set -euo pipefail

# Purpose:
#     Securely wipes a single file by overwriting it 10 times before
#     deleting it.
#
# Requirements:
#     GNU coreutils (shred).
#
# Usage:
#     ./fileshred.sh /path/to/file

if [[ -z "${1:-}" ]]; then
    echo "[!] Usage: $0 /path/to/file"
    exit 1
fi

FILE=$1

echo "Wiping $FILE."
for _ in {1..10}
do
    shred "$FILE"
done
echo "Shred complete."
rm "$FILE"
echo "$FILE has been removed."
