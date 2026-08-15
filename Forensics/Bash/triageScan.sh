#!/bin/bash
#
# Purpose:
#   Example of running a scaled triage collection (CyLR) over every host in
#   a /24 subnet via SSH. NOT designed to be used "as is" — it needs
#   modification to match your local circumstances before use.
#
# Requirements:
#   An account with SSH access to the target systems (shown as "responder"
#   below) and a triage collection tool — this example uses CyLR
#   (https://github.com/orlikoski/CyLR), but should be changed to whatever
#   tool you use.
#
# Usage:
#   ./triageScan.sh

# Not using `set -e`: each host in the subnet is collected independently —
# one unreachable/failing host shouldn't abort the rest of the sweep.
set -uo pipefail

for i in {1..254} # Modify this to include the range of IP addresses you want to run it against.
do
  ssh "responder@10.10.10.$i" 'mkdir DFIR' # This is creating a folder to hold the tool and evidence
  scp CyLR "responder@10.10.10.$i:/home/responder/DFIR/" # Modify this to match your chosen tool or script
  ssh "responder@10.10.10.$i" 'cd DFIR && chmod +x CyLR && ./CyLR -od /home/responder/DFIR -of evidence_collection.zip' # Modify this to meet the command line arguments your tool needs and remember to make the tool executable.
  scp "responder@10.10.10.$i:/home/responder/DFIR/evidence_collection.zip" "./10.10.10.${i}_evidence_collection.zip" # Download the output evidence
  # Consider adding logic to validate the download and remove it from the endpoint to reduce disk use.
  # for example ssh responder@10.10.10.$i 'md5sum /home/responder/DFIR/evidence_collection.zip' then compare this with the local MD5 if they match run ssh responder@10.10.10.$i 'rm /home/responder/DFIR/evidence_collection.zip'
done
