#!/bin/bash
set -uo pipefail
# NOTE: set -e is intentionally omitted — this loops over every IP in
# ips.txt, and one failed/slow whois lookup should not abort the rest.

# Purpose:
#     Runs a whois lookup for every IP address in ips.txt and writes the
#     parsed results (owner, netname, country, etc.) to a timestamped CSV.
#
# Requirements:
#     whois.
#
# Usage:
#     Create a file called ips.txt containing the IP addresses (one per
#     line, no trailing blank line), then run:
#     ./iplookups.sh

filename=$(date -u --iso-8601="seconds" | cut -d '+' -f1 | tr : -)"_output.csv"

echo "Lookups commenced at $(date)"
echo "ip,dns,owner,netname,country,person,email,created,last_modified" > "$filename"
# NOTE: dns is never populated by a lookup below (pre-existing gap — the CSV
# header promises it but nothing computes it); initialized here only so the
# reference on the echo line below is safe under `set -u`, matching the
# original (always-empty) output for that field.
dns=""
while read -r ip
do
    echo "$ip"
    whois "$ip" > whoisip
    owner=$(grep -i -m 1 "owner:" whoisip | sed 's/owner:       //g')
    netname=$(grep -i -m 1 "netname:" whoisip | sed 's/netname:        //g')
    # shellcheck disable=SC2034 # parsed but not currently included in the CSV output (pre-existing gap, left as-is)
    descr=$(grep -i -m 1 "descr:" whoisip | sed 's/descr:          //g')
    country=$(grep -i -m 1 "country" whoisip | sed 's/country:     //g')
    person=$(grep -i -m 1 "person:" whoisip | sed 's/person:      //g')
    created=$(grep -i -m 1 "created" whoisip | sed 's/created:        //g')
    last_modified=$(grep -i -m 1 "last-modified:" whoisip | sed 's/last-modified:  //g')
    email=$(grep -m 1 "email:" whoisip | sed 's/email:      //g')
    if [[ -z "$created" ]] ; then
        created=$(grep -i -m 1 "RegDate" whoisip | sed 's/RegDate:        //g')
    fi
    if [[ -z "$last_modified" ]] ; then
        last_modified=$(grep -i -m 1 "updated" whoisip | sed 's/Updated:        //g')
    fi
    if [[ -z "$last_modified" ]]; then
        last_modified=$(grep -i -m 1 "changed" whoisip | sed 's/changed: //g')
    fi
    echo "$ip,$dns,$owner,$netname,$country,$person,$email,$created,$last_modified" >> "$filename"
done <ips.txt
