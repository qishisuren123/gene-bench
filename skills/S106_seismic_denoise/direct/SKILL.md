# Seismic Waveform Denoising

## Overview
This skill denoises seismic waveform data using Butterworth bandpass filtering and detects P-wave arrivals using STA/LTA ratio triggering, computing SNR improvement metrics.

## Workflow
1. Parse command-line arguments for input CSV, output prefix, lowcut (1.0 Hz), highcut (20.0 Hz), STA window (1.0 s), LTA window (10.0 s)
2. Load CSV with time_s, velocity_north, velocity_east, velocity_vertical columns; determine sampling rate from time spacing
3. Design 4th-order Butterworth bandpass filter using scipy.signal.butter with normalized frequency (Wn = [lowcut, highcut] / (fs/2))
4. Apply zero-phase filtering (filtfilt) to each velocity component independently
5. Compute STA/LTA ratio: short-term average amplitude / long-term average amplitude in sliding windows along each component
6. Trigger P-wave detection where STA/LTA exceeds threshold (3.0); record arrival time and triggering component
7. Compute SNR improvement: power ratio of signal before/after filtering (SNR_after / SNR_before in dB)
8. Output: filtered waveforms CSV + detection results JSON with arrivals, SNR improvements, filter parameters

## Common Pitfalls
- **Frequency normalization**: Butterworth filter requires frequencies normalized to Nyquist (fs/2); using raw Hz values produces wrong filter response
- **STA/LTA window overlap**: STA and LTA windows must not overlap with signal onset — LTA should represent pre-event background noise
- **Edge effects**: filtfilt pads data internally but short traces may still produce artifacts at boundaries; trim first/last 10% of filtered output
- **Sampling rate detection**: Determine fs from actual time column spacing (1/median(diff(time))), don't assume fixed rate

## Error Handling
- Validate that lowcut < highcut and both are below Nyquist frequency
- Handle non-uniform time sampling by interpolating to regular grid before filtering
- Check that STA window < LTA window (typically STA = 1s, LTA = 10s)

## Quick Reference
- Butterworth: `b, a = scipy.signal.butter(4, [lowcut/(fs/2), highcut/(fs/2)], btype='band')`
- Zero-phase filter: `scipy.signal.filtfilt(b, a, data)`
- STA/LTA: `sta = rolling_mean(abs(signal), sta_samples) / rolling_mean(abs(signal), lta_samples)`
- SNR (dB): `10 * log10(signal_power_after / noise_power_after)`
- P-wave trigger: first timestamp where STA/LTA > 3.0
