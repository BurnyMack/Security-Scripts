#!/bin/bash
set -uo pipefail
# NOTE: set -e is intentionally omitted — this is a multi-source collector
# and one unreadable/missing cron source (permission denied, empty dir, etc.)
# should not abort collection of the remaining sources.

# Purpose:
#     Collects scheduled task (cron) data from a Linux system — system
#     crontab, /etc/cron.d, per-user crontabs, and the /etc/cron.{hourly,
#     daily,weekly,monthly} directories — into a single CSV.
#
# Requirements:
#     Must be run with root privileges to read all cron sources.
#
# Usage:
#     ./cron_collector.sh <storage_location>

# Check if a storage location was provided
if [[ -z "${1:-}" ]]; then
    echo "[!] Usage: $0 <storage_location>"
    exit 1
fi

# Check the script is running as root
if [[ $EUID != 0 ]]; then
    echo "[!] This script must be run with root privileges!"
    echo "[!] Exiting"
    exit 1;
else 
    echo "[+] Running as root."

fi

# Define the storage location and CSV file
STORAGE_LOCATION=$1
CSV_FILE="$STORAGE_LOCATION/Cron_data.csv"
touch "$CSV_FILE"
if [[ -f "$CSV_FILE" ]]; then
    echo "[+] Write to storage successful."
    rm "$CSV_FILE"
    echo "[+] Cron collection will begin."
else
    echo "[!] Unable to write to storage media."
    echo "[!] Exiting."
    exit 1;
fi

# Create the CSV file
echo "Source filename,M Time,Task interval,User Account,Command/Filename" > "$CSV_FILE"

# Function to collect cron jobs
collect_cron_jobs() {
    local path=$1
    local user=$2
    local mtime timing command
    # shellcheck disable=SC2086 # $path is a glob pattern (e.g. "/etc/cron.d/*") and must expand
    for file in $path; do
        if [[ -f "$file" ]]; then
            mtime=$(stat -c %y "$file")
            while IFS= read -r line; do
                if [[ "$line" =~ ^#.*$ || "$line" =~ ^$ || "$line" =~ ^.*[[:space:]]ls[[:space:]].*$ ]]; then
                    continue
                fi
                # Extract timing intervals and commands correctly
                # Assuming a standard cron line format: minute hour day month weekday command
                timing=$(echo "$line" | awk '{print $1,$2,$3,$4,$5}')
                command=$(echo "$line" | cut -d' ' -f6-)
                echo "$file,$mtime,$timing,${user:-$(echo "$line" | awk '{print $6}')},$command" >> "$CSV_FILE"
            done < "$file"

            while IFS= read -r line; do
                if [[ "$line" =~ ^#.*$ || "$line" =~ ^$ ]]; then
                    continue
                fi
                echo "$file,$mtime,$(echo "$line" | cut -d' ' -f1-5),${user:-$(echo "$line" | cut -d' ' -f6)},$(echo "$line" | cut -d' ' -f7-)" >> "$CSV_FILE"
            done < "$file"
        fi
    done
}

# Collect cron jobs from /etc/crontab and /etc/cron.d/*
collect_cron_jobs "/etc/crontab" "root"
collect_cron_jobs "/etc/cron.d/*" "root"

# Collect user-specific cron jobs
for user in /var/spool/cron/crontabs/*; do
    collect_cron_jobs "$user" "$(basename "$user")"
done

# Function to collect data from /etc/cron.{hourly,daily,weekly,monthly}
collect_cron_dirs() {
    local dir=$1
    local timing=$2
    local mtime
    for file in "$dir"/*; do
        if [[ -f "$file" ]]; then
            mtime=$(stat -c %y "$file")
            echo "$file,$mtime,$timing,root,$(basename "$file")" >> "$CSV_FILE"
        fi
    done
}

# Collect data from cron directories
collect_cron_dirs "/etc/cron.hourly" "hourly"
collect_cron_dirs "/etc/cron.daily" "daily"
collect_cron_dirs "/etc/cron.weekly" "weekly"
collect_cron_dirs "/etc/cron.monthly" "monthly"

echo "[+] Cron data collection completed. File located at: $CSV_FILE"
