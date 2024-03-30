import pandas as pd
import argparse, os, re, dpkt, socket


class LogParser:

    def __init__(self, data):
        self.data = data
        self.log_patterns = {
            "apache": r'(?P<ip>\S+) - - \[(?P<timestamp>.*?)\] "(?P<request>.*?)" (?P<status>\d+) (?P<size>\d+)',
            "iis": r'^(\S+) (\S+) (\S+) \[([\w:/]+\s[+\-]\d{4})\] "(\S+) (\S+) (\S+)" (\d+) (\d+) "([^"]*)" "([^"]*)"',
            "syslog": r"(\S+ \d+ \d+:\d+:\d+) (\S+) (\S+)\[([\d]+)\]: (.*)",
            "cef": r"CEF:(\d+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|(\d+)\|(.+)",
            "yara": r"rule\s+(\w+)\s+{([\s\S]*?)}",
        }

    def detect_log_format(self):
        for log_format, log_pattern in self.log_patterns.items():
            log_regex = re.compile(log_pattern)
            with open(self.data, "r") as log_file:
                for line in log_file:
                    if log_regex.search(line):
                        return log_format
        return None

    def Apache(self):
        log_pattern = self.log_patterns["apache"]
        log_regex = re.compile(log_pattern)
        results = []
        with open(self.data, "r") as log_file:
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

    def parse(self):
        log_format = self.detect_log_format()
        if log_format is None:
            print("Unsupported log format.")
            return

        parse_method = getattr(self, log_format.capitalize())
        parsed_data = parse_method()

        if parsed_data:
            self.save_to_excel(parsed_data, log_format)
            print(f"Data parsed and saved to {log_format}_parsed_data.xlsx")

    # Parsing methods for different log formats here...

    def save_to_excel(self, data, log_format):
        df = pd.DataFrame(data)
        output_file = f"{log_format}_parsed_data.xlsx"
        writer = pd.ExcelWriter(output_file, engine="xlsxwriter")
        df.to_excel(output_file, sheet_name="Parsed Data", index=False)


def main():
    parser = argparse.ArgumentParser(description="Log Parser CLI Tool")
    parser.add_argument(
        "log_format",
        choices=["apache", "iis", "syslog", "cef", "pcap", "yara"],
        help="Log format to parse (e.g., 'apache', 'iis', 'syslog', 'cef', 'pcap', 'yara')",
    )
    parser.add_argument(
        "-p", "--path", required=True, help="Path to the log file to parse"
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Path to the output directory (default: current working directory)",
    )
    args = parser.parse_args()
    # Use the specified output directory or default to the current working directory
    output_directory = args.output or os.getcwd()
    output_path = os.path.join(output_directory, f"{args.log_format}_parsed_data.xlsx")
    log_parser = LogParser(args.path)
    log_parser.parse()


if __name__ == "__main__":
    main()
