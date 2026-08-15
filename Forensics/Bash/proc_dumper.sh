#!/bin/bash
#
# Purpose:
#   Dumps the memory of a running process, one file per writable mapping
#   listed in /proc/<pid>/maps.
#
# Requirements:
#   gdb. Must be able to read /proc/<pid>/maps and attach to the target PID
#   (usually root, or the same user as the target process).
#
# Usage:
#   ./proc_dumper.sh <PID>
#
# Example:
#   ./proc_dumper.sh 2337

# Not using `set -e`: a target process with no rw-p mappings is a valid,
# non-error outcome (the while loop simply does nothing) and shouldn't abort.
set -uo pipefail

grep rw-p "/proc/$1/maps" | sed -n 's/^\([0-9a-f]*\)-\([0-9a-f]*\).*$/\1 \2/p' | while read -r start stop; do
    gdb --batch --pid "$1" -ex \
        "dump memory $1-$start-$stop.dump 0x$start 0x$stop"
done
