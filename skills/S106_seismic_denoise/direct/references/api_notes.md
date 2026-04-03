# scipy.signal.butter
butter(N, Wn, btype='band', fs=None, output='ba')
- N: filter order (typically 2-4 for seismic)
- Wn: critical frequencies [low, high] in Hz (when fs is given)
- btype: 'band' for bandpass, 'low', 'high'
- output: 'ba' returns (b, a), 'sos' returns second-order sections
- Prefer sos output for numerical stability

# scipy.signal.filtfilt
filtfilt(b, a, x, axis=-1)
- Zero-phase forward-backward filtering (no phase shift)
- For sos: sosfiltfilt(sos, x)
- Doubles the effective filter order

# scipy.signal.sosfiltfilt
sosfiltfilt(sos, x)
- Preferred over filtfilt for numerical stability
- sos from butter(..., output='sos')

# STA/LTA (Short-Term Average / Long-Term Average)
- STA: average absolute amplitude over short window (0.5-2 sec)
- LTA: average absolute amplitude over long window (10-50 sec)
- Ratio: sta/lta, trigger when ratio > threshold (typically 3-5)
- Detrigger when ratio < lower threshold (typically 1-2)
- Use cumulative sum for efficient computation:
  cumsum = np.cumsum(np.abs(signal)**2)

# Typical seismic bandpass
- Microseismic: 1-100 Hz
- Teleseismic: 0.01-1 Hz
- Local earthquakes: 1-20 Hz
