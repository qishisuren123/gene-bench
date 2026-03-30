Write a Python CLI script that converts a large CSV dataset into a chunked, compressed HDF5 file with efficient read access patterns.

Input: A CSV file with many rows and columns of mixed numeric/string data.

Requirements:
1. Use argparse: --input CSV, --output HDF5, --chunk-rows (default 10000), --compression (choices: "gzip", "lzf", "none", default "gzip"), --compression-level (default 4)
2. Read the CSV and auto-detect column types (numeric vs string)
3. Create HDF5 file with:
   - Numeric columns stored as float64 datasets with chunking=(chunk_rows,)
   - String columns stored as variable-length string datasets
   - Apply specified compression to all datasets
4. Store column metadata as HDF5 attributes: dtype, original_csv_column_index, n_missing
5. Create an index dataset for fast row-range queries
6. Write a _metadata group with: source_file, n_rows, n_cols, compression, chunk_size, creation_timestamp
7. Verify round-trip: read back a sample and compare with original
8. Output summary: file size, compression ratio, read speed for random 1000-row slice
