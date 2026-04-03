# Example 1: Streaming CSV to chunked, compressed HDF5
import numpy as np
import pandas as pd
import h5py

# Create a sample CSV for demonstration
csv_path = 'data.csv'
np.random.seed(42)
big_df = pd.DataFrame(np.random.randn(10000, 5), columns=[f'col_{i}' for i in range(5)])
big_df.to_csv(csv_path, index=False)

# Stream CSV into HDF5
hdf5_path = 'output.h5'
chunk_size = 2000

with h5py.File(hdf5_path, 'w') as f:
    dset = None
    col_names = None
    for i, chunk in enumerate(pd.read_csv(csv_path, chunksize=chunk_size)):
        arr = chunk.values.astype(np.float64)
        if dset is None:
            col_names = list(chunk.columns)
            dset = f.create_dataset(
                'data',
                data=arr,
                maxshape=(None, arr.shape[1]),
                chunks=(min(chunk_size, 1000), arr.shape[1]),
                compression='gzip',
                compression_opts=4,
            )
            dset.attrs['columns'] = col_names
        else:
            old_len = dset.shape[0]
            dset.resize(old_len + arr.shape[0], axis=0)
            dset[old_len:] = arr
        print(f"Chunk {i}: wrote {arr.shape[0]} rows, total {dset.shape[0]}")

# Example 2: Read back and verify
with h5py.File(hdf5_path, 'r') as f:
    dset = f['data']
    print(f"Shape: {dset.shape}, Chunks: {dset.chunks}")
    print(f"Columns: {list(dset.attrs['columns'])}")
    print(f"Compression: {dset.compression}, level: {dset.compression_opts}")
    sample = dset[:5]
    print(f"First 5 rows:\n{sample}")
