# Example 1: Butterworth bandpass filter on seismic trace
import numpy as np
from scipy.signal import butter, sosfiltfilt

# Synthetic seismic signal with noise
fs = 100.0  # sampling rate Hz
t = np.arange(0, 30, 1/fs)
signal_clean = np.sin(2 * np.pi * 5 * t) * np.exp(-0.1 * t)
noise = 0.5 * np.random.randn(len(t))
trace = signal_clean + noise

# Bandpass filter: 1-20 Hz
low, high = 1.0, 20.0
sos = butter(4, [low, high], btype='band', fs=fs, output='sos')
filtered = sosfiltfilt(sos, trace)
print(f"Raw RMS: {np.sqrt(np.mean(trace**2)):.3f}")
print(f"Filtered RMS: {np.sqrt(np.mean(filtered**2)):.3f}")

# Example 2: STA/LTA event detection
def sta_lta(signal, sta_len, lta_len):
    """Compute STA/LTA ratio using cumulative sum."""
    sq = np.cumsum(signal ** 2)
    # Pad for indexing
    sq = np.insert(sq, 0, 0)
    sta = (sq[sta_len:] - sq[:-sta_len]) / sta_len
    lta = (sq[lta_len:] - sq[:-lta_len]) / lta_len
    # Align: trim to common length
    n = min(len(sta), len(lta))
    sta = sta[-n:]
    lta = lta[-n:]
    ratio = np.where(lta > 0, sta / lta, 0)
    return ratio

nsta = int(1.0 * fs)   # 1 sec STA
nlta = int(10.0 * fs)  # 10 sec LTA
ratio = sta_lta(filtered, nsta, nlta)

trigger_threshold = 4.0
triggers = np.where(ratio > trigger_threshold)[0]
if len(triggers) > 0:
    print(f"First trigger at sample {triggers[0]}, time {triggers[0]/fs:.2f}s")
