Write a Python CLI script that parses complex server log files using regular expressions and extracts structured metrics.

Input: A log file with mixed formats (Apache access logs, application logs, error traces).

Requirements:
1. Use argparse: --input log file, --output JSON, --format (choices: "apache", "nginx", "custom", default "apache")
2. Define regex patterns for each format:
   - Apache: `^(\S+) \S+ \S+ \[([^\]]+)\] "(\w+) (\S+) \S+" (\d{3}) (\d+|-)`
   - Nginx: similar with upstream_response_time
   - Custom: `^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+) \[(\w+)\] (.+)$`
3. Parse each line, track: total lines, parsed lines, failed lines
4. Extract metrics:
   - Status code distribution (2xx, 3xx, 4xx, 5xx)
   - Top 10 URLs by request count
   - Top 10 IPs by request count
   - Requests per hour histogram
   - Average response size
   - Error rate (4xx + 5xx / total)
5. Detect anomalies: IPs with >100 requests, URLs with >50% error rate
6. Output JSON with all metrics, anomalies, and parse statistics
7. Print summary: total requests, error rate, top anomalies
