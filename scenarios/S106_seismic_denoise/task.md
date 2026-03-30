Write a Python CLI script that denoises seismic waveform data using bandpass filtering and STA/LTA detection.

Input: A CSV file with columns: time_s, velocity_north, velocity_east, velocity_vertical.

Requirements:
1. Use argparse: --input CSV, --output-dir for results, --lowcut (default 1.0 Hz), --highcut (default 20.0 Hz), --sta (default 1.0s), --lta (default 10.0s)
2. Load seismic data and determine sampling rate from time column
3. Apply Butterworth bandpass filter (order 4) to each velocity component
4. Implement STA/LTA trigger detection: compute ratio of short-term to long-term average amplitude
5. Detect P-wave arrivals where STA/LTA ratio exceeds 3.0
6. Compute signal-to-noise ratio (SNR) before and after filtering for each component
7. Output: filtered waveforms CSV, detection results JSON (arrivals, SNR improvements, filter parameters)
8. Print summary: number of detections, average SNR improvement
