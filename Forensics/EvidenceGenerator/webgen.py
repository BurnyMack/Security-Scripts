#!/usr/bin/env python3
"""
Generate a synthetic Apache-style access log with embedded fake IOCs, for
building test evidence sets. Needs user_agents.txt, referrers.txt, and
page_names.txt (one entry per line). See README.md in this directory for the
full generate -> filter -> rename workflow.

Usage:
    webgen.py
    webgen.py -o out.log --min-entries 1000 --max-entries 2000

Requirements:
    secscripts (pip install -e .).
"""

import random
import socket
import struct
import sys
from datetime import datetime, timedelta
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from secscripts.cli import EXIT_ERROR, EXIT_OK, build_parser  # noqa: E402
from secscripts.log import configure  # noqa: E402


def _parse_dt(value):
    return datetime.strptime(value, "%Y-%m-%d %H:%M")


def main(argv=None):
    parser = build_parser(
        "Generate a synthetic Apache access log with embedded fake IOCs.",
        prog="webgen",
    )
    parser.add_argument("-o", "--output", default="fake_access_log_updated.txt")
    parser.add_argument("--user-agents", default="user_agents.txt")
    parser.add_argument("--referrers", default="referrers.txt")
    parser.add_argument("--page-names", default="page_names.txt")
    parser.add_argument("--start", default="2023-12-01 18:48", help="start time 'YYYY-MM-DD HH:MM'")
    parser.add_argument("--end", default="2023-12-03 19:33", help="end time 'YYYY-MM-DD HH:MM'")
    parser.add_argument("--min-entries", type=int, default=3000000)
    parser.add_argument("--max-entries", type=int, default=6000000)
    args = parser.parse_args(argv)
    logger = configure(args, name="webgen")

    output_file = args.output
    user_agent_file = args.user_agents
    referrer_file = args.referrers
    page_names_file = args.page_names
    try:
        start_time = _parse_dt(args.start)
        end_time = _parse_dt(args.end)
    except ValueError as exc:
        logger.error("bad --start/--end (expected 'YYYY-MM-DD HH:MM'): %s", exc)
        return EXIT_ERROR
    num_entries = random.randint(args.min_entries, args.max_entries)

    # Calculate time interval
    time_interval = (end_time - start_time) / num_entries

    # Load data from files
    try:
        with open(user_agent_file) as ua_file:
            user_agents = [line.strip() for line in ua_file]
        with open(referrer_file) as ref_file:
            referrers = [line.strip() for line in ref_file]
        with open(page_names_file) as page_file:
            page_names = [line.strip() for line in page_file]
    except OSError as exc:
        logger.error("could not read an input list file: %s", exc)
        return EXIT_ERROR

    # Open the output log file
    with open(output_file, "w") as log_file:
        current_time = start_time
        ip153_entry_count = 0  # Track the number of entries with IP 86.184.120.153
        ip49_entry_count = 0  # Track the number of entries with IP 157.245.137.49
        ip82_entry_count = 0  # Track the number of entries with IP 54.27.144.82
        ip88_entry_count = 0  # Track the number of entries with IP 54.27.144.88
        ip12_entry_count = 0  # Track the number of entries with IP 54.27.145.12
        ip156_entry_count = 0  # Track the number of entries with IP 54.27.144.156
        ip101_entry_count = 0  # Track the number of entries with IP 54.27.144.101
        ip177_entry_count = 0  # Track the number of entries with IP 54.27.144.177
        ip35_entry_count = 0  # Track the number of entries with IP 54.27.144.35

        for i in range(num_entries):
            # Check if it's time for the additional entries with IP 86.184.120.153
            if (
                ip153_entry_count < 2348
                and i % (50 * 60 * 5) < (3 * 60 * 5)
                and random.random() < 0.4
            ):
                # Generate entries for the specified duration
                for _ in range(3 * 60 * 5):
                    timestamp = current_time.strftime("%d/%b/%Y:%H:%M:%S +0000")
                    for num in range(1678371625, 1678389626):
                        log_entry = f'86.184.120.153 - - [{timestamp}] "OPTIONS / HTTP/1.1" 302 - "-" "Mozilla/5.0 (compatible; Nmap Scripting Engine; https://nmap.org/book/nse.html)"\n'
                        log_file.write(log_entry.replace("NUMBERS", str(num)))
                        ip153_entry_count += 1
                        if ip153_entry_count >= 300:
                            break
                    if ip153_entry_count >= 300:
                        break
                    current_time += timedelta(seconds=1)
            elif i % (13 * 60 + 27) == 0 and random.random() < 0.5:
                log_entry = f'157.245.137.49 - - [{current_time.strftime("%d/%b/%Y:%H:%M:%S +0000")}] "GET /b734k.php HTTP/1.1" 200 8880 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"\n'
                log_file.write(log_entry)
                ip49_entry_count += 1
            elif i % (13 * 60 + 28) == 0:
                log_entry = f'157.245.137.49 - - [{current_time.strftime("%d/%b/%Y:%H:%M:%S +0000")}] "POST /b734k.php HTTP/1.1" 200 6757 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"\n'
                log_file.write(log_entry)
                ip49_entry_count += 1
            elif i % 100 == 0 and random.random() < 0.6:
                log_entry = f'54.27.144.82 - - [{current_time.strftime("%d/%b/%Y:%H:%M:%S +0000")}] "GET /data.html HTTP/1.1" 200 6757 "/" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"\n'
                log_file.write(log_entry)
                ip82_entry_count += 1
            elif i % 117 == 0 and random.random() < 0.3:
                log_entry = f'54.27.144.88 - - [{current_time.strftime("%d/%b/%Y:%H:%M:%S +0000")}] "GET /data.html HTTP/1.1" 200 6757 "/" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"\n'
                log_file.write(log_entry)
                ip88_entry_count += 1
            elif i % 122 == 0 and random.random() < 0.7:
                log_entry = f'54.27.145.12 - - [{current_time.strftime("%d/%b/%Y:%H:%M:%S +0000")}] "GET /data.html HTTP/1.1" 200 6757 "/" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"\n'
                log_file.write(log_entry)
                ip12_entry_count += 1
            elif i % 139 == 0 and random.random() < 0.45:
                log_entry = f'54.27.144.156 - - [{current_time.strftime("%d/%b/%Y:%H:%M:%S +0000")}] "GET /data.html HTTP/1.1" 200 6757 "/" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"\n'
                log_file.write(log_entry)
                ip156_entry_count += 1
            elif i % 168 == 0 and random.random() < 0.6:
                log_entry = f'54.27.144.101 - - [{current_time.strftime("%d/%b/%Y:%H:%M:%S +0000")}] "GET /data.html HTTP/1.1" 200 6757 "/" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"\n'
                log_file.write(log_entry)
                ip101_entry_count += 1
            elif i % 250 == 0 and random.random() < 0.2:
                log_entry = f'54.27.144.177 - - [{current_time.strftime("%d/%b/%Y:%H:%M:%S +0000")}] "GET /data.html HTTP/1.1" 200 6757 "/" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"\n'
                log_file.write(log_entry)
                ip177_entry_count += 1
            elif i % 489 == 0 and random.random() < 0.45:
                log_entry = f'54.27.144.35 - - [{current_time.strftime("%d/%b/%Y:%H:%M:%S +0000")}] "GET /data.html HTTP/1.1" 200 6757 "/" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"\n'
                log_file.write(log_entry)
                ip35_entry_count += 1
            else:
                # Generate source IP address (valid internet routable)
                source_ip = socket.inet_ntoa(struct.pack(">I", random.randint(1, 0xFFFFFFFF)))

                # Generate HTTP request method (80% GET, 20% POST)
                if random.random() < 0.8:
                    http_method = "GET"
                else:
                    http_method = "POST"

                # Add HEAD request at random intervals with a blank referrer
                if random.random() < 0.005:  # 0.5% chance
                    http_method = "HEAD"
                    referrer = "-"
                    page = "/"
                else:
                    referrer = random.choice(referrers)
                    page = random.choice(page_names)

                # Generate a random user agent
                user_agent = random.choice(user_agents)

                # Generate response codes (60% 200, 40% random)
                if random.random() < 0.6:
                    response_code = "200"
                else:
                    response_code = random.choice(["404", "302", "301", "500", "401"])

                # Generate file size (4782 if 'index' in page name, otherwise random between 1287 and 12652)
                if "index" in page:
                    file_size = "4782"
                else:
                    file_size = str(random.randint(1287, 12652))

                # Write the log entry with modified fields
                log_entry = f'{source_ip} - - [{current_time.strftime("%d/%b/%Y:%H:%M:%S +0000")}] "{http_method} {page} HTTP/1.1" {response_code} {file_size} "{referrer}" "{user_agent}"\n'

                # Introduce a 10% chance of writing the same log entry twice
                if random.random() < 0.1:
                    log_file.write(log_entry)  # Write the log entry once
                    log_file.write(log_entry)  # Write the log entry again
                else:
                    log_file.write(log_entry)  # Write the log entry once

            # Increment the timestamp
            current_time += time_interval

            # Check if the specified number of entries has been reached
            if i == num_entries - 1:
                break

    logger.info("generated %d log entries in '%s'", num_entries, output_file)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
