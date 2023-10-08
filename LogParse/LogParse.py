import re, dpkt, socket

class LogParse:

    def __init__(self, data):
        self.data = data

    def Apache(self):
        log_pattern = r'(?P<ip>\S+) - - \[(?P<timestamp>.*?)\] "(?P<request>.*?)" (?P<status>\d+) (?P<size>\d+)'
        log_regex = re.compile(log_pattern)
        results = []
        with open(self.data, 'r') as log_file:
            for line in log_file:
                match = log_regex.search(line)
                if match:
                    ip = match.group('ip')
                    timestamp = match.group('timestamp')
                    request = match.group('request')
                    status = match.group('status')
                    size = match.group('size')
                    results.append({
                        "IP": ip,
                        "timestamp": timestamp,
                        "URL": request,
                        "Status Code": status,
                        "Bytes Sent": size,
                    })

        return results

    def IIS(self):
        log_pattern = r'^(\S+) (\S+) (\S+) \[([\w:/]+\s[+\-]\d{4})\] "(\S+) (\S+) (\S+)" (\d+) (\d+) "([^"]*)" "([^"]*)"'
        iis_regex = re.compile(log_pattern)
        results = []
        with open(self.data, 'r') as log_file:
            for line in log_file:
                match = iis_regex.match(line)
                if match:
                    date = match.group(4)
                    http_method = match.group(5)
                    url = match.group(6)
                    status_code = match.group(8)
                    bytes_sent = match.group(9)
                    user_agent = match.group(11)
                    results.append({
                        "Date": date,
                        "HTTP Method": http_method,
                        "URL": url,
                        "Status Code": status_code,
                        "Bytes Sent": bytes_sent,
                        "User Agent": user_agent,
                    })

        return results

    def Syslog(self):
        log_pattern = r'(\S+ \d+ \d+:\d+:\d+) (\S+) (\S+)\[([\d]+)\]: (.*)'
        syslog_regex = re.compile(log_pattern)
        results = []
        with open(self.data, 'r') as log_file:
            for line in log_file:
                match = syslog_regex.match(line)
                if match:
                    timestamp = match.group(1)
                    hostname = match.group(2)
                    process = match.group(3)
                    pid = match.group(4)
                    message = match.group(5)
                    results.append({
                        "Timestamp": timestamp,
                        "Hostname": hostname,
                        "Process": process,
                        "PID": pid,
                        "Message": message,
                    })

        return results

    def CEF(self):
        log_pattern = r'CEF:(\d+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|(\d+)\|(.+)'
        cef_regex = re.compile(log_pattern)
        results = []
        with open(self.data, 'r') as log_file:
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
                    results.append({
                        "CEF Version": cef_version,
                        "Vendor": vendor,
                        "Product": product,
                        "Version": version,
                        "Signature ID": signature_id,
                        "Name": name,
                        "Severity": severity,
                        "Extension": extension,
                    })

        return results

    def PCAP(self):
        results = []
        with open(self.data, 'rb') as f:
            pcap = dpkt.pcap.Reader(f)
            for ts, buf in pcap:
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
                        results.append({
                            "Source IP": src_ip,
                            "Destination IP": dst_ip,
                            "Source Port": src_port,
                            "Destination Port": dst_port,
                        })

        return results

    def YARA(self):
        yara_pattern = r'rule\s+(\w+)\s+{([\s\S]*?)}'
        yara_regex = re.compile(yara_pattern)
        results = []
        with open(self.data, 'r') as log_file:
            yara_rule = log_file.read()
            matches = yara_regex.findall(yara_rule)
            for match in matches:
                rule_name = match[0]
                rule_body = match[1].strip()
                results.append({
                    "Rule Name": rule_name,
                    "Rule Body": rule_body,
                })

        return results