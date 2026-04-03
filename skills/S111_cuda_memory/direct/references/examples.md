# Example 1: Parse memory events and track allocations
import re
from collections import defaultdict

def parse_memory_log(lines):
    """Parse CUDA memory log lines into structured events."""
    events = []
    pattern = re.compile(
        r'(\d+\.?\d*)\s+(ALLOC|FREE|OOM)\s+(0x[0-9a-fA-F]+)\s+(\d+)'
    )
    for line in lines:
        m = pattern.match(line.strip())
        if m:
            ts, etype, addr, size = m.groups()
            events.append({
                'time': float(ts),
                'type': etype,
                'addr': int(addr, 16),
                'size': int(size),
            })
    return events

# Example 2: Compute memory timeline and peak usage
def memory_timeline(events):
    """Return (timestamps, usage_bytes) and peak usage."""
    active = {}  # addr -> size
    timeline = []
    current = 0
    peak = 0
    for e in events:
        if e['type'] == 'ALLOC':
            active[e['addr']] = e['size']
            current += e['size']
        elif e['type'] == 'FREE' and e['addr'] in active:
            current -= active.pop(e['addr'])
        peak = max(peak, current)
        timeline.append((e['time'], current))
    return timeline, peak

# Example 3: Detect leaks (allocations never freed)
def detect_leaks(events):
    """Find allocations that are never freed."""
    active = {}
    for e in events:
        if e['type'] == 'ALLOC':
            active[e['addr']] = e
        elif e['type'] == 'FREE':
            active.pop(e['addr'], None)
    leaks = sorted(active.values(), key=lambda x: -x['size'])
    total_leaked = sum(e['size'] for e in leaks)
    return leaks, total_leaked

# Example 4: Fragmentation metric
def fragmentation(free_blocks):
    """Compute external fragmentation ratio."""
    if not free_blocks:
        return 0.0
    total_free = sum(size for _, size in free_blocks)
    largest = max(size for _, size in free_blocks)
    return 1.0 - (largest / total_free) if total_free > 0 else 0.0
