# Example 1: Parse Apache Combined Log Format
import re
from collections import Counter
from datetime import datetime

LOG_PATTERN = re.compile(
    r'(?P<ip>\S+) \S+ (?P<user>\S+) '
    r'\[(?P<time>[^\]]+)\] '
    r'"(?P<method>\S+) (?P<path>\S+) (?P<proto>[^"]*)" '
    r'(?P<status>\d{3}) (?P<size>\S+) '
    r'"(?P<referer>[^"]*)" "(?P<agent>[^"]*)"'
)

sample_lines = [
    '192.168.1.10 - frank [10/Oct/2023:13:55:36 -0700] "GET /index.html HTTP/1.1" 200 2326 "-" "Mozilla/5.0"',
    '10.0.0.5 - - [10/Oct/2023:13:56:01 -0700] "POST /api/login HTTP/1.1" 401 512 "-" "curl/7.68"',
    '192.168.1.10 - frank [10/Oct/2023:13:56:15 -0700] "GET /favicon.ico HTTP/1.1" 404 209 "-" "Mozilla/5.0"',
]

def parse_log_line(line):
    m = LOG_PATTERN.match(line)
    if not m:
        return None
    d = m.groupdict()
    d['status'] = int(d['status'])
    d['size'] = int(d['size']) if d['size'] != '-' else 0
    d['time'] = datetime.strptime(d['time'], '%d/%b/%Y:%H:%M:%S %z')
    return d

records = [parse_log_line(l) for l in sample_lines]
records = [r for r in records if r is not None]

# Example 2: Aggregate statistics
status_counts = Counter(r['status'] for r in records)
ip_counts = Counter(r['ip'] for r in records)
total_bytes = sum(r['size'] for r in records)

print(f"Status distribution: {dict(status_counts)}")
print(f"Top IPs: {ip_counts.most_common(3)}")
print(f"Total bytes served: {total_bytes}")

# Example 3: Filter errors (4xx and 5xx)
errors = [r for r in records if r['status'] >= 400]
for e in errors:
    print(f"  {e['status']} {e['method']} {e['path']} from {e['ip']}")
