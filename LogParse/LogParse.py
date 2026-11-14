"""
Regex/dpkt-based parsers for Apache, IIS, syslog, CEF, pcap, and YARA-rule
input, one method per format, each returning a list of dicts.

Library module — import ``LogParse`` and either call a format method directly
(``LogParse(path).Apache()``), dispatch by name (``.parse("apache")``), or let
``.detect()`` identify the format first. The ``CLIParse`` entry point drives
all three. ``dpkt`` is imported lazily so the text-format parsers work even
where it is not installed.
"""

import re
import socket

# Line-oriented regexes shared by the parsers and by format auto-detection, so
# both agree on exactly what each format looks like (single source of truth).
PATTERNS = {
    "apache": r'(?P<ip>\S+) - - \[(?P<timestamp>.*?)\] "(?P<request>.*?)" (?P<status>\d+) (?P<size>\d+)',
    "iis": r'^(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2}) (\S+) (\S+) (\S+) (\d+) (\d+) "([^"]*)"',
    "syslog": r"^(\S+ +\d+ \d+:\d+:\d+) (\S+) (\S+)\[(\d+)\]: (.*)",
    "cef": r"CEF:(\d+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|(\d+)\|(.+)",
}
# YARA rules span multiple lines, so detection scans the whole file rather than
# matching line by line.
YARA_PATTERN = r"rule\s+(\w+)\s+{([\s\S]*?)}"
# Order matters only for stable reporting; detection resolves ambiguity itself.
TEXT_FORMATS = ("apache", "iis", "syslog", "cef", "yara")


class LogParse:
    def __init__(self, data):
        self.data = data

    def Apache(self):
        log_regex = re.compile(PATTERNS["apache"])
        results = []
        with open(self.data) as log_file:
            for line in log_file:
                match = log_regex.search(line)
                if match:
                    ip = match.group("ip")
                    timestamp = match.group("timestamp")
                    request = match.group("request")
                    status = match.group("status")
                    size = match.group("size")
                    results.append(
                        {
                            "IP": ip,
                            "timestamp": timestamp,
                            "URL": request,
                            "Status Code": status,
                            "Bytes Sent": size,
                        }
                    )

        return results

    def IIS(self):
        log_regex = re.compile(PATTERNS["iis"])
        results = []
        with open(self.data) as log_file:
            for line in log_file:
                match = log_regex.match(line)
                if match:
                    results.append(
                        {
                            "Date": match.group(1),
                            "Time": match.group(2),
                            "Client IP": match.group(3),
                            "HTTP Method": match.group(4),
                            "URL": match.group(5),
                            "Status Code": match.group(6),
                            "Bytes Sent": match.group(7),
                            "User Agent": match.group(8),
                        }
                    )

        return results

    def Syslog(self):
        syslog_regex = re.compile(PATTERNS["syslog"])
        results = []
        with open(self.data) as log_file:
            for line in log_file:
                match = syslog_regex.match(line)
                if match:
                    timestamp = match.group(1)
                    hostname = match.group(2)
                    process = match.group(3)
                    pid = match.group(4)
                    message = match.group(5)
                    results.append(
                        {
                            "Timestamp": timestamp,
                            "Hostname": hostname,
                            "Process": process,
                            "PID": pid,
                            "Message": message,
                        }
                    )

        return results

    def CEF(self):
        cef_regex = re.compile(PATTERNS["cef"])
        results = []
        with open(self.data) as log_file:
            for line in log_file:
                match = cef_regex.match(line)
                if match:
                    cef_version = match.group(1)
                    vendor = match.group(2)
                    product = match.group(3)
                    version = match.group(4)
                    signature_id = match.group(5)
                    name = match.group(6)
                    severity = match.group(7)
                    extension = match.group(8)
                    results.append(
                        {
                            "CEF Version": cef_version,
                            "Vendor": vendor,
                            "Product": product,
                            "Version": version,
                            "Signature ID": signature_id,
                            "Name": name,
                            "Severity": severity,
                            "Extension": extension,
                        }
                    )

        return results

    def PCAP(self):
        import dpkt  # imported lazily; the text parsers don't need it

        results = []
        with open(self.data, "rb") as f:
            pcap = dpkt.pcap.Reader(f)
            for _ts, buf in pcap:
                eth = dpkt.ethernet.Ethernet(buf)
                # Check if it's an IP packet
                if isinstance(eth.data, dpkt.ip.IP):
                    ip = eth.data
                    src_ip = socket.inet_ntoa(ip.src)
                    dst_ip = socket.inet_ntoa(ip.dst)
                    # Check if it's a TCP packet
                    if isinstance(ip.data, dpkt.tcp.TCP):
                        tcp = ip.data
                        src_port = tcp.sport
                        dst_port = tcp.dport
                        results.append(
                            {
                                "Source IP": src_ip,
                                "Destination IP": dst_ip,
                                "Source Port": src_port,
                                "Destination Port": dst_port,
                            }
                        )

        return results

    def YARA(self):
        yara_regex = re.compile(YARA_PATTERN)
        results = []
        with open(self.data) as log_file:
            yara_rule = log_file.read()
            matches = yara_regex.findall(yara_rule)
            for match in matches:
                rule_name = match[0]
                rule_body = match[1].strip()
                results.append(
                    {
                        "Rule Name": rule_name,
                        "Rule Body": rule_body,
                    }
                )

        return results

    # Dispatch by format name, so callers don't rely on method-name casing
    # (the old getattr(self, fmt.capitalize()) was broken for iis/cef/yara).
    _DISPATCH = {
        "apache": "Apache",
        "iis": "IIS",
        "syslog": "Syslog",
        "cef": "CEF",
        "pcap": "PCAP",
        "yara": "YARA",
    }

    def parse(self, log_format):
        """Parse ``self.data`` as ``log_format`` and return a list of dicts."""
        try:
            method_name = self._DISPATCH[log_format]
        except KeyError:
            raise ValueError(f"unknown log format: {log_format!r}") from None
        return getattr(self, method_name)()

    def detect(self, max_lines=200):
        """Return the detected format name, or raise ``ValueError``.

        Counts how many of the first ``max_lines`` lines match each
        line-oriented format, plus a whole-file check for YARA. Raises if
        nothing matches (undetectable) or if two formats tie for the most
        matches (ambiguous).
        """
        line_regexes = {fmt: re.compile(PATTERNS[fmt]) for fmt in PATTERNS}
        counts = dict.fromkeys(line_regexes, 0)
        with open(self.data, encoding="utf-8", errors="replace") as handle:
            head = ""
            for index, line in enumerate(handle):
                if index < max_lines:
                    head += line
                    for fmt, regex in line_regexes.items():
                        if regex.search(line):
                            counts[fmt] += 1
                else:
                    break
        yara_hits = len(re.findall(YARA_PATTERN, head))
        if yara_hits:
            counts["yara"] = yara_hits

        best = max(counts.values())
        if best == 0:
            raise ValueError("could not auto-detect log format")
        winners = sorted(fmt for fmt, count in counts.items() if count == best)
        if len(winners) > 1:
            raise ValueError("ambiguous log format; candidates: " + ", ".join(winners))
        return winners[0]
