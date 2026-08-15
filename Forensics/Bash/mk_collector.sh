#!/bin/bash
#
# Purpose:
#   Creates an evidence collection device: sets up folders and copies a
#   standard set of trusted static binaries onto external media, plus
#   installs AVML, ready to be used for live-response collection.
#
# Requirements:
#   Ideally run from a trusted device that already contains the binaries
#   listed below (this works well from SANS Linux SIFT). Other systems may
#   need validation or tool installation first.
#
# Usage:
#   ./mk_collector.sh <mount_point>

# Not using `set -e`: install_tools copies dozens of independent tools —
# a source system missing one of them shouldn't abort copying the rest.
set -uo pipefail

function create_folders {
    mkdir -p "$mount_point/evidence"
    mkdir -p "$mount_point/collectiontools"
}

function check_space {
    available_space=$(df -BG "$mount_point" | awk 'NR==2 {print $4}' | sed 's/G//')
    if [[ "$available_space" -lt 8 ]]; then
        echo "[!] The storage device has less than 8Gb of storage space remaining. This is not suitable for evidence collection"
        exit 1
    elif [[ "$available_space" -gt 60 ]]; then
        echo "[ ] The storage device has more than 60gb of storage space remaining."
        echo "[ ] This will be effective at collecting triage data and memory in most situations."
        echo "[!] If this is insufficient, exit the script now."
    else
        echo "[ ] The mounted device has $available_space Gb free. Please ensure this is sufficient for your needs."
    fi
}
function install_tools {
    destination="$mount_point/collectiontools"
    echo "[ ] Installing the core tools."
    # This next section should only be used if source code is required and the tools will be built on the device
    # -----------------------------------------------------------------------------------------------------------
    #url="https://ftp.gnu.org/gnu/coreutils/coreutils-9.3.tar.gz"
    #wget -q "$url" -P "$destination"
    #if [ "$?" -ne 0 ]; then
    #    echo "[ ] Download failed. Exiting."
    #    exit 1
    #fi
    #tar --no-same-owner -xzf "$destination/coreutils-9.3.tar.gz" -C "$destination"
    #if [ "$?" -ne 0 ]; then
    #    echo "Extraction failed. Exiting."
    #    exit 1
    #fi
    # -----------------------------------------------------------------------------------------------------------
    
    # This will assume the script is being run from a trusted machine.
    local tools=(
        ls cat pwd grep zcat zgrep diff xxd gunzip tar zip df ping wget curl
        md5sum sha1sum sha256sum base64 json_pp rm scp nano chattr chown chgrp
        dd dcfldd dc3dd ewfacquire ss lsof ps netstat stat strace nslookup
        ngrep tcpdump du dumpcap echo env date time tee top exiftool file find
        uniq sort unzip gdb lsattr xargs hostname zless zmore head tail less
        more objdump readelf strings size
    )
    for tool in "${tools[@]}"; do
        cp "$(which "$tool")" "$destination"
    done
    
    echo "[ ] The core tools have been copied to the device."
    echo "[ ] Ensuring AVML is installed."
    url="https://github.com/microsoft/avml/releases/download/v0.13.0/avml"
    wget -q "$url" -P "$destination"
    
    echo "[ ] Tools installed. Making executable now."
    chmod +x "$destination"/*
    
    remaining_space=$(df -BG "$mount_point" | awk 'NR==2 {print $4}' | sed 's/G//')
    echo "[ ] Privileges set. There is $remaining_space Gb remaining on the device."
}

# Check if the number of arguments provided is exactly 1
if [[ "$#" -ne 1 ]]; then
    echo "Usage: $0 <device_path_or_mount_point>"
    exit 1
fi

# Get the device path or mount point from the command line argument
input="$1"

# Check if the input is a valid device path
if [[ -b "$input" ]]; then
    # Input is a device path, find the associated mount point
    mount_point=$(findmnt -n -o TARGET --source "$input")
elif [[ -d "$input" ]]; then
    # Input is a directory, consider it as a mount point
    mount_point="$input"
else
    # Invalid input, exit the script
    echo "Invalid device path or mount point. Exiting."
    exit 1
fi

# Check if the device is mounted
if [[ -n "$mount_point" ]]; then
    clear
    echo "Evidence Collector - Creation Script."
    echo "-------------------------------------"
    echo "This script will validate the mount"
    echo "point you have provided. If a device"
    echo "is mounted correctly, it will create"
    echo "two folders on the device and begin "
    echo "to install the tools required."
    echo "-------------------------------------"
    echo ""
    echo "[ ] Device or mount point $input is mounted at $mount_point."
    read -r -p "[?] Do you want to continue? (press N to abort, anything else will continue): " response
    response=$(echo "$response" | tr '[:upper:]' '[:lower:]')
    if [[ "$response" == "n" ]]; then
        echo "[!] Exiting as requested."
        exit 0
    fi
    check_space
    create_folders
    install_tools
else
    echo "[!] Device or mount point $input is not mounted. Exiting."
    exit 1
fi
