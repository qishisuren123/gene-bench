# CUDA GPU Memory Analysis

## Overview
This skill analyzes GPU memory allocation/free events to reconstruct the memory timeline, find peak usage, detect fragmentation, and suggest optimization opportunities like early frees and dtype downcasting.

## Workflow
1. Parse command-line arguments for input JSON (allocation events), output JSON, and gpu-memory-gb (default 16.0)
2. Load allocation events: each has timestamp_ms, operation (alloc/free), size_bytes, tensor_name, dtype
3. Replay events chronologically: maintain a dict of active allocations keyed by tensor_name; alloc adds, free removes
4. Track cumulative memory usage at each timestamp; record peak usage point (max total allocated bytes)
5. At peak: compute fragmentation as 1 - (largest_contiguous_free_block / total_free_memory)
6. Identify optimization opportunities: (a) early-free candidates: tensors allocated long before their last use, (b) dtype downcast: float64 tensors > 1MB that could be float32, (c) serializable: non-overlapping tensors that could share memory
7. Compute efficiency = peak_used_bytes / (gpu_memory_gb × 1024³)
8. Output JSON with peak_memory_bytes, peak_timestamp, fragmentation_ratio, efficiency, n_allocations, optimization_suggestions, memory_timeline_summary

## Common Pitfalls
- **Alloc/free matching**: Track allocations by tensor_name; mismatched or duplicate free events corrupt the timeline — skip unmatched frees with warning
- **Fragmentation tracking**: Simple total used/free is insufficient; must track individual allocation positions to compute largest contiguous free block
- **Peak detection timing**: Peak occurs at a specific timestamp between alloc events — don't confuse with total allocation count
- **dtype downcast savings**: float64→float32 saves exactly 50% memory; only suggest for tensors above size threshold (1 MB)

## Error Handling
- Handle out-of-order timestamps by sorting events before replay
- Skip free events for tensor_names not found in active allocations (unmatched frees)
- Validate that total freed memory never exceeds total allocated (negative usage indicates data error)

## Quick Reference
- Memory tracking: `active[tensor_name] = size_bytes` on alloc, `del active[tensor_name]` on free
- Peak detection: `peak = max(cumulative_usage)` across all timestamps
- Fragmentation: `1 - largest_free_block / total_free` (at peak)
- Efficiency: `peak_bytes / (gpu_gb * 1024**3)`
- Downcast savings: `sum(size for tensors where dtype=='float64' and size > 1MB) / 2`
- Early-free: tensors where `(last_use - alloc_time) > median_lifetime * 2`
