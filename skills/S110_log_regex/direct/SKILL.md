# Server Log Regex Parsing

## Overview
This skill parses server access logs (Apache/Nginx) using format-specific regex patterns to extract structured metrics including status distribution, top URLs/IPs, error rates, hourly traffic histograms, and anomalous IPs.

## Workflow
1. Parse command-line arguments for input log file, output JSON, log-format (apache/nginx/auto), and anomaly threshold (default 100 requests)
2. Define compiled regex patterns per format: Apache combined log captures IP, timestamp, method, URL, status, response_size in named groups
3. Iterate each line: apply regex match, track parsed/failed line counts; extract fields into structured records
4. Aggregate metrics: status code distribution (2xx/3xx/4xx/5xx), per-IP request counts, per-URL request counts, hourly request histogram
5. Compute error rate: count(4xx + 5xx) / total_parsed_lines
6. Detect anomalies: IPs exceeding request threshold, URLs with >50% error rate
7. Compute average response size (excluding '-' entries)
8. Output JSON with total_lines, parsed_lines, failed_lines, status_distribution, top_urls, top_ips, error_rate, hourly_distribution, anomalies, avg_response_size

## Common Pitfalls
- **Missing response size**: Apache logs show '-' for responses with no body (e.g., 304 Not Modified) — handle as 0 or skip in size calculations
- **Regex escaping**: Log timestamps use brackets `[dd/Mon/yyyy:HH:MM:SS +ZZZZ]` — escape brackets in regex or use character class `[^\]]+`
- **URL query strings**: URLs may contain query parameters with special characters — use `\S+` to match the full URL including query string
- **Timestamp parsing**: Apache format `[01/Jan/2024:12:00:00 +0000]` differs from Nginx; use format-specific strptime patterns
- **Malformed lines**: Real logs contain truncated or corrupted lines — always handle regex match failure gracefully

## Error Handling
- Count and report failed (unparseable) lines separately from valid entries
- Handle empty log files by outputting zero-count metrics
- Validate that at least some lines parse successfully; warn if failure rate > 50%

## Quick Reference
- Apache regex: `r'^(\S+) \S+ \S+ \[([^\]]+)\] "(\w+) (\S+) \S+" (\d{3}) (\d+|-)'`
- Compile for performance: `pattern = re.compile(regex_string)`
- Status grouping: `status_group = f"{int(status) // 100}xx"`
- Error rate: `(count_4xx + count_5xx) / total_parsed`
- Anomaly detection: `requests_per_ip > threshold` or `error_rate_per_url > 0.5`
- Hourly histogram: group by hour extracted from parsed timestamp
