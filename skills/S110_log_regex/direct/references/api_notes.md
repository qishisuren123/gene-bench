# re.compile
pattern = re.compile(r'regex_string')
- Compile once, reuse for performance on large log files
- match = pattern.match(line) for start-of-string match
- match = pattern.search(line) for anywhere in string

# Named groups
(?P<name>pattern) — capture group accessible by name
- match.group('name') or match.groupdict()
- Example: r'(?P<ip>\d+\.\d+\.\d+\.\d+)'

# Common Apache/Nginx Combined Log Format
format: '%h %l %u %t "%r" %>s %b "%{Referer}i" "%{User-Agent}i"'
- %h: remote host (IP)
- %t: time in [day/month/year:hour:min:sec zone]
- %r: request line "METHOD /path HTTP/version"
- %>s: status code
- %b: response size in bytes (or '-')

# Regex pattern for Combined Log Format
r'(?P<ip>\S+) \S+ (?P<user>\S+) \[(?P<time>[^\]]+)\] '
r'"(?P<method>\S+) (?P<path>\S+) (?P<proto>[^"]*)" '
r'(?P<status>\d{3}) (?P<size>\S+) '
r'"(?P<referer>[^"]*)" "(?P<agent>[^"]*)"'

# datetime parsing for log timestamps
from datetime import datetime
datetime.strptime(time_str, '%d/%b/%Y:%H:%M:%S %z')

# collections.Counter
Counter(iterable) — count occurrences
- most_common(n) returns top n (value, count) pairs
