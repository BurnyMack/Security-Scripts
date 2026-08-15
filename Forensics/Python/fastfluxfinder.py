#!/usr/bin/env python3
"""
Scans a pcap for DNS responses and flags domains resolving to unusually
many unique IPs, a common indicator of fast-flux DNS.

Usage:
    fastfluxfinder.py capture.pcap

Requirements:
    scapy (pip install scapy)
"""

import argparse
import sys

from scapy.all import DNSRR, rdpcap

dnsRecords = {}


def checkPacket(packet):
    if packet.haslayer(DNSRR):
        rrname = packet.getlayer(DNSRR).rrname
        rdata = packet.getlayer(DNSRR).rdata
        if rrname in dnsRecords:
            if rdata not in dnsRecords[rrname]:
                dnsRecords[rrname].append(rdata)
        else:
            dnsRecords[rrname] = [rdata]


def main():
    parser = argparse.ArgumentParser(
        description="Find domains with many unique resolved IPs (possible fast-flux DNS) in a pcap."
    )
    parser.add_argument("pcap", help="Path to the pcap file to analyze")
    args = parser.parse_args()

    try:
        packets = rdpcap(args.pcap)
    except OSError as e:
        print(f"Error reading {args.pcap}: {e}", file=sys.stderr)
        sys.exit(1)

    for pkt in packets:
        checkPacket(pkt)
    for item in dnsRecords:
        print("[+] " + item + " has " + str(len(dnsRecords[item])) + " unique IPs")


if __name__ == "__main__":
    main()
