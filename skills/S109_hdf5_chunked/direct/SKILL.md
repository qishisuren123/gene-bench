# Large CSV to Chunked HDF5 Conversion

## Overview
This skill converts large CSV datasets into chunked, compressed HDF5 files using h5py, with proper metadata storage, automatic column type detection, and round-trip verification.

## Workflow
1. Parse command-line arguments for input CSV, output HDF5 path, chunk-rows (default 10000), compression (gzip), and compression-level (4)
2. Read CSV header to detect column names and types; classify as numeric (float64) or string (variable-length)
3. Create HDF5 file with one dataset per column: numeric columns as float64, string columns as h5py variable-length string dtype
4. Set chunk shape (chunk_rows, 1) and compression on each dataset for efficient partial reads
5. Stream CSV data in chunks: read chunk_rows at a time, write to corresponding HDF5 datasets to handle files larger than memory
6. Store metadata as HDF5 attributes: per-dataset (dtype, original_column_index, n_missing) and file-level (_metadata group with source_file, n_rows, n_cols, compression, creation_timestamp)
7. Verify round-trip: read back a sample (first 100 rows) and compare with original CSV data

## Common Pitfalls
- **Variable-length strings**: h5py requires `h5py.special_dtype(vlen=str)` for Python 2 or `h5py.string_dtype()` for Python 3 — using fixed-length strings truncates data
- **Chunk size tuning**: Chunks too small (< 1000 rows) cause excessive overhead; too large (> 100000 rows) waste memory — default 10000 is a good balance
- **Missing values**: NaN in numeric columns are preserved as float NaN; missing strings must be stored as empty string or a sentinel value
- **Memory management**: Don't load entire CSV into memory — stream in chunks matching HDF5 chunk size

## Error Handling
- Validate input CSV exists and is readable; check file size to warn if very large (> 1 GB)
- Handle mixed-type columns by defaulting to string dtype
- Verify HDF5 file was written correctly by reading back metadata and checking row counts match

## Quick Reference
- Create dataset: `f.create_dataset(name, shape=(n_rows,), dtype='float64', chunks=(chunk_rows,), compression='gzip', compression_opts=4)`
- String dtype: `h5py.string_dtype()`
- Write chunk: `ds[start:end] = data_chunk`
- Metadata: `ds.attrs['dtype'] = 'float64'`
- File metadata group: `f.create_group('_metadata')`
- Compression ratio: `os.path.getsize(h5_path) / os.path.getsize(csv_path)`
