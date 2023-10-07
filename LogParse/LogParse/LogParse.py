import re , dpkt ,socket                

class LogParse: 
    
    def Apache(data):
        log_pattern = r'(?P<ip>\S+) - - \[(?P<timestamp>.*?)\] "(?P<request>.*?)" (?P<status>\d+) (?P<size>\d+)'
        log_regex = re.compile(log_pattern)
        with open(data, 'r') as log_file:
            for line in log_file:
                match = log_regex.search(line)
                if match:
                    ip = match.group('ip')
                    timestamp = match.group('timestamp')
                    request = match.group('request')
                    status = match.group('status')
                    size = match.group('size')
                    return {
                        "IP": ip,
                        "timestamp": timestamp,
                        "URL": request,
                        "Status Code": status,
                        "Bytes Sent": size,
                    }
                else:
                    return None

    def IIS(data):
        log_pattern = r'^(\S+) (\S+) (\S+) \[([\w:/]+\s[+\-]\d{4})\] "(\S+) (\S+) (\S+)" (\d+) (\d+) "([^"]*)" "([^"]*)"'
        match = re.match(log_pattern, data)
        with open(data, 'r') as log_file:
            for line in log_file:
                if match:
                    date = match.group(4)
                    http_method = match.group(5)
                    url = match.group(6)
                    status_code = match.group(8)
                    bytes_sent = match.group(9)
                    user_agent = match.group(11)
                    return {
                        "Date": date,
                        "HTTP Method": http_method,
                        "URL": url,
                        "Status Code": status_code,
                        "Bytes Sent": bytes_sent,
                        "User Agent": user_agent,
                    }
                else:
                    return None
    
    def Syslog(data):
        log_pattern = r'(\S+ \d+ \d+:\d+:\d+) (\S+) (\S+)\[([\d]+)\]: (.*)'
        match = re.match(log_pattern, data)
        with open(data, 'r') as log_file:
            for line in log_file:
                if match:
                    timestamp = match.group(1)
                    hostname = match.group(2)
                    process = match.group(3)
                    pid = match.group(4)
                    message = match.group(5)
                    return {
                        "Timestamp": timestamp,
                        "Hostname": hostname,
                        "Process": process,
                        "PID": pid,
                        "Message": message
                    }
                else:
                    return None
    
    def CEF(data):
        log_pattern = r'CEF:(\d+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|(\d+)\|(.+)'
        cef_regex = re.compile(cef_pattern)
        match = cef_regex.match(data)
        with open(data, 'r') as log_file:
            for line in log_file:
                if match:
                    cef_version = match.group(1)
                    vendor = match.group(2)
                    product = match.group(3)
                    version = match.group(4)
                    signature_id = match.group(5)
                    name = match.group(6)
                    severity = match.group(7)
                    extension = match.group(8)
                    return {
                        "CEF Version": cef_version,
                        "Vendor": vendor,
                        "Product": product,
                        "Version": version,
                        "Signature ID": signature_id,
                        "Name": name,
                        "Severity": severity,
                        "Extension": extension
                    }
                else:
                    return None

    def PCAP(pcap_file):
        with open(pcap_file, 'rb') as f:
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
                        
    def YARA(data):
        yara_pattern = r'rule\s+(\w+)\s+{([\s\S]*?)}'
        yara_regex = re.compile(yara_pattern)
        match = yara_regex.search(yara_rule)
        with open(data, 'r') as log_file:
            for line in log_file:
                if match:
                    rule_name = match.group(1)
                    rule_body = match.group(2).strip()

                    return {
                        "Rule Name": rule_name,
                        "Rule Body": rule_body
                    }
                else:
                    return None