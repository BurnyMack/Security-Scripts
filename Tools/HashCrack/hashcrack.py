#!/usr/bin/env python3
"""
Brute-force a crypt() password hash against a wordlist.

Usage:
    python hashcrack.py wordlist.txt '$6$abc123...'

Requirements:
    Unix `crypt` module (stdlib on Linux/macOS; not available on Windows).
"""

import argparse
import crypt
import sys


def find_password(filename, hash_val):
    try:
        with open(filename) as password_file:
            for passwd in password_file:
                passwd = passwd.strip()
                if crypt.crypt(passwd, hash_val) == hash_val:
                    return passwd
    except OSError as e:
        print(f"Error reading wordlist: {e}", file=sys.stderr)
        sys.exit(1)
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Find a password given its hash in a password file."
    )
    parser.add_argument("filename", help="Path to the password file")
    parser.add_argument("hash_val", help="Hash value of the password to find")
    args = parser.parse_args()
    found_password = find_password(args.filename, args.hash_val)
    if found_password:
        print("Password found:", found_password)
    else:
        print("Password not found in the provided file.")


if __name__ == "__main__":
    main()
