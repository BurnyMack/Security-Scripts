#!/bin/bash
set -euo pipefail

# Purpose:
#     Stub tool to search a directory for documents modified during an
#     incident window and flag ones whose "last modified by" field looks odd
#     (differs from the creator).
#
# Requirements:
#     exiftool
#
# Usage:
#     ./exifevidence.sh path [start-date] [end-date]
#
# Example:
#     ./exifevidence.sh /mnt/ntfs/c/user/administrator/documents

if [[ -z "${1:-}" ]]; then
    echo "[!] Usage: $0 path [start-date] [end-date]"
    exit 1
fi

FOLDER="$1"
SDATE="${2:-}"
EDATE="${3:-}"

# Check dates exist
if [[ -z "$SDATE" ]]
then
    SDATE=$(date -d '1 day ago' +%F)
fi
if [[ -z "$EDATE" ]]
then
    EDATE=$(date +%F)
fi

# Build date string

DATES="-newermt $SDATE ! -newermt $EDATE"
DSTRING="events between $SDATE and $EDATE"


# Check for exiftool

if ! command -v exiftool &>/dev/null
then
    echo "[!] Unable to find exiftool. Exiting"
    exit
fi

# Scan folder
echo -e "\n[ ] Checking EXIFdata to look for suspicious modifications.\n    This search will look for $DSTRING.\n    If this is incorrect please run it again with the correct dates."
echo -e "    -------------------------------------------------------------------\n"

# shellcheck disable=SC2086 # $DATES must expand into separate `find` predicate tokens
find "$FOLDER" -name "*.*" -type f $DATES -exec sh -c '
    for FILE do
        lastmod=$(exiftool "$FILE" | grep "Last Modified By" | cut -d':' -f2 | xargs)
        if [ -z "$lastmod" ]
        then
            lastmod="+No account name recorded+"
        fi
        author=$(exiftool "$FILE" | grep "Creator" | cut -d':' -f2 | xargs)
        if [ -z "$author" ]
        then
            author="+No account name recorded+"
        fi
        modtime=$(exiftool "$FILE" | grep "File Modif" | cut -d':' -f2- | xargs)
        language=$(exiftool "$FILE" | grep "Language Code" | cut -d':' -f2 | xargs)
        if [ -z "$language" ]
        then
            language="empty"
        fi
        if [ "$lastmod" != "$author" ]
        then
            echo -e "\n[!] $FILE, was last modified by a different account than its creator."
            echo "    This file was created by $author but modified by $lastmod."
            echo -e "    The modification time is $modtime, and the language pack in use is $language.\n"
        else
            echo "The document $FILE appears unchanged."
        fi
    done
' exec-sh {} +
echo -e "\n    -------------------------------------------------------------------"
echo -e "[ ] Search complete. Any results will be shown above. If there are no entries, then no files were found at the path or within the timeframe specified."


# TODO

# 1. Add logic to search for modification timestamps in a date range *DONE*
# 2. Add logic to search directories not specific files *DONE*
# 3. Add test to check inputted dates are valid format.
