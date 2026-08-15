#!/bin/bash
set -euo pipefail

# Purpose:
#     Example script showing how to check a live filesystem to see if LVM2
#     is in use.
#
# Requirements:
#     None beyond standard coreutils (grep, mount).
#
# Usage:
#     ./check_lvm2.sh

echo "> Checking for LVM2"
now=$(date +"%T")
echo "> Script running at $now" 
if  grep -Pq '/dev/(mapper/|disk/by-id/dm)' /etc/fstab  ||  mount | grep -q /dev/mapper/
then
    echo "> LVM *is* in use."
else
    echo "> LVM is NOT in use."
fi
echo "> Check complete."
