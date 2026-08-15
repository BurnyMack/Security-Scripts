#!/usr/bin/env python3
"""
Brute-force a password-protected zip file against a wordlist.

Usage:
    python zipcrack.py archive.zip wordlist.txt
"""

import argparse
import zipfile


def extract_zip(zipfile_path, password):
    try:
        with zipfile.ZipFile(zipfile_path) as zip_file:
            zip_file.extractall(pwd=password.encode())
            print("Password found:", password)
            return True
    except Exception:
        return False


def brute_force(zipfile_path, password_list):
    for password in password_list:
        if extract_zip(zipfile_path, password):
            break


def read_wordlist(wordlist_path):
    with open(wordlist_path) as f:
        for line in f:
            yield line.strip()


def main():
    parser = argparse.ArgumentParser(description="Brute force zip file password.")
    parser.add_argument("zipfile", metavar="zipfile", type=str, help="path to zip file")
    parser.add_argument("wordlist", metavar="wordlist", type=str, help="path to wordlist file")
    args = parser.parse_args()

    password_list = read_wordlist(args.wordlist)

    brute_force(args.zipfile, password_list)


if __name__ == "__main__":
    main()
