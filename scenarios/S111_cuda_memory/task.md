Write a Python CLI script that analyzes and optimizes CUDA GPU memory usage patterns from profiling data.

Input: A JSON file containing GPU memory allocation events.

Requirements:
1. Use argparse: --input JSON, --output JSON, --gpu-memory-gb (default 16.0)
2. Load allocation events, each with: {timestamp_ms, operation ("alloc"/"free"), size_bytes, tensor_name, dtype}
3. Reconstruct memory timeline: track active allocations at each timestamp
4. Compute peak memory usage and when it occurs
5. Detect memory fragmentation: ratio of largest_free_block / total_free
6. Identify optimization opportunities:
   - Tensors that could be freed earlier (allocated long before last use)
   - Overlapping allocations that could be serialized to reduce peak
   - dtype downcast opportunities (float64 tensors > 1MB that could be float32)
7. Compute memory efficiency: peak_used / gpu_memory_total
8. Output JSON with: peak_memory_bytes, peak_timestamp, fragmentation_ratio, efficiency, n_allocations, optimization_suggestions (list), memory_timeline_summary
9. Print summary: peak usage, efficiency, top 3 optimization suggestions
