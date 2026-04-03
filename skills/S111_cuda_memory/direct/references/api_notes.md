# Memory event types
- ALLOC: memory allocation request (address, size, stream)
- FREE: memory deallocation (address, stream)
- OOM: out-of-memory error (requested size, total allocated)

# Timeline construction
- Parse events chronologically: list of (timestamp, event_type, address, size)
- Track active allocations: dict mapping address -> (size, timestamp)
- Current usage = sum of all active allocation sizes
- Peak usage = max(current_usage) over time

# Fragmentation analysis
- External fragmentation: free memory exists but not contiguous
- Metric: 1 - (largest_free_block / total_free_memory)
- Values close to 1.0 indicate severe fragmentation
- Track free blocks as sorted list of (start, size)

# Memory leak detection
- Allocation without matching free = potential leak
- Group by allocation call site / stack trace
- Report: allocations alive at end, sorted by total size
- Growth pattern: if active_memory trend is monotonically increasing

# Useful data structures
- SortedList (from sortedcontainers) for free block management
- defaultdict(list) for grouping allocations by category
- heapq for tracking top-N largest allocations

# Parsing log lines
- Typical format: "timestamp event_type address size [optional_fields]"
- Address: hex string, parse with int(addr, 16)
- Size: in bytes, may use K/M/G suffixes
