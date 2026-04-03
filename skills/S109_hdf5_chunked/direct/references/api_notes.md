# h5py.File
h5py.File(name, mode)
- mode: 'w' create/overwrite, 'r' read-only, 'a' append
- Use as context manager: with h5py.File('out.h5', 'w') as f:

# h5py.File.create_dataset
f.create_dataset(name, shape=None, maxshape=None, dtype=None,
                 data=None, chunks=True, compression=None)
- maxshape: tuple, use None for unlimited dimension
  e.g., maxshape=(None, 5) allows unlimited rows, fixed 5 columns
- chunks: True for auto, or tuple for explicit chunk shape
  e.g., chunks=(1000, 5) for row-oriented access
- compression: 'gzip', 'lzf', or None
- compression_opts: 0-9 for gzip level (4 is good default)

# Dataset resizing
dset.resize(new_shape)
- Only works if maxshape was set with None dimensions
- Extend rows: dset.resize(dset.shape[0] + n, axis=0)

# Streaming CSV to HDF5 pattern
- Read CSV in chunks: pd.read_csv(path, chunksize=N)
- Create dataset with maxshape=(None, ncols) on first chunk
- Append subsequent chunks via resize + slice assignment
- dset[old_len:new_len] = chunk_array

# Attributes
dset.attrs['column_names'] = column_list
dset.attrs['description'] = 'some text'
- Store metadata as HDF5 attributes
