#!/usr/bin/env python3
"""
Generate a CSV of synthetic fake user records for building test evidence sets.

Usage:
    generate_data.py
    generate_data.py --output fake_user_data.csv --min-users 50000 --max-users 99000

Requirements:
    Faker (pip install Faker); secscripts (pip install -e .).
"""

import csv
import random
import sys
from pathlib import Path

from faker import Faker

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from secscripts.cli import EXIT_OK, build_parser  # noqa: E402
from secscripts.log import configure  # noqa: E402

fake = Faker()


def generate_users(num_users):
    user_data = []
    for _ in range(num_users):
        first_name = fake.first_name()
        last_name = fake.last_name()
        age = random.randint(18, 65)
        street_address = fake.street_address()
        zip_code = fake.zipcode()
        account_number = "".join([str(random.randint(0, 9)) for _ in range(12)])

        user_data.append([first_name, last_name, age, street_address, zip_code, account_number])
    return user_data


def main(argv=None):
    parser = build_parser(
        "Generate synthetic fake user records as a CSV.",
        prog="generate_data",
    )
    parser.add_argument("-o", "--output", default="fake_user_data.csv", help="output CSV filename")
    parser.add_argument(
        "--min-users", type=int, default=50000, help="minimum number of records to generate"
    )
    parser.add_argument(
        "--max-users", type=int, default=99000, help="maximum number of records to generate"
    )
    args = parser.parse_args(argv)
    logger = configure(args, name="generate_data")

    num_users = random.randint(args.min_users, args.max_users)
    user_data = generate_users(num_users)

    with open(args.output, "w", newline="") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(
            ["First Name", "Last Name", "Age", "Street Address", "Zip Code", "Account Number"]
        )
        csv_writer.writerows(user_data)

    logger.info("generated %d fake user records in '%s'", num_users, args.output)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
