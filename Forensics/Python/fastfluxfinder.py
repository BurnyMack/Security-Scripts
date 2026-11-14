#!/usr/bin/env python3
"""
Scan a pcap for DNS responses and flag domains resolving to unusually many
unique IPs, a common indicator of fast-flux DNS.

Usage:
    fastfluxfinder.py capture.pcap
    fastfluxfinder.py capture.pcap --threshold 5 --output-format json

Requirements:
    scapy (pip install scapy); secscripts (pip install -e .).
"""

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from secscripts.cli import EXIT_ERROR, EXIT_OK, build_parser  # noqa: E402
from secscripts.log import configure  # noqa: E402
from secscripts.output import emit  # noqa: E402


def collect_dns_records(packets):
    """Return {domain: [unique rdata, ...]} from DNS response records."""
    from scapy.all import DNSRR  # imported lazily so the module loads without scapy

    records = {}
    for packet in packets:
        if packet.haslayer(DNSRR):
            layer = packet.getlayer(DNSRR)
            rrname = layer.rrname
            rdata = layer.rdata
            if isinstance(rrname, bytes):
                rrname = rrname.decode("utf-8", "replace")
            records.setdefault(rrname, [])
            if rdata not in records[rrname]:
                records[rrname].append(rdata)
    return records


def main(argv=None):
    parser = build_parser(
        "Flag domains with many unique resolved IPs (possible fast-flux DNS).",
        prog="fastfluxfinder",
    )
    parser.add_argument("pcap", help="path to the pcap file to analyse")
    parser.add_argument(
        "--threshold",
        type=int,
        default=1,
        help="minimum unique IPs for a domain to be reported (default: 1)",
    )
    args = parser.parse_args(argv)
    logger = configure(args, name="fastfluxfinder")

    try:
        from scapy.all import rdpcap

        packets = rdpcap(args.pcap)
    except OSError as e:
        logger.error("error reading %s: %s", args.pcap, e)
        return EXIT_ERROR

    records = collect_dns_records(packets)
    results = [
        {"domain": domain, "unique_ips": len(ips)}
        for domain, ips in records.items()
        if len(ips) >= args.threshold
    ]
    results.sort(key=lambda r: r["unique_ips"], reverse=True)
    emit(results, args.output_format)
    logger.info("%d domain(s) at or above threshold %d", len(results), args.threshold)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
