# Baseline correction
- Polynomial fit: np.polyfit(wavenumbers, intensity, degree)
  typical degree 3-7 for Raman spectra
- Iterative: fit polynomial, remove points above fit, repeat
- Subtract baseline: corrected = intensity - np.polyval(coeffs, wavenumbers)

# scipy.signal.find_peaks
find_peaks(x, height=None, distance=None, prominence=None, width=None)
- x: 1-D signal array
- height: minimum peak height
- distance: minimum samples between peaks
- prominence: minimum prominence (peak standing out from baseline)
- width: minimum peak width at half-prominence
- Returns: (peak_indices, properties_dict)

# scipy.signal.peak_prominences
peak_prominences(x, peaks)
- Returns: (prominences, left_bases, right_bases)

# scipy.signal.peak_widths
peak_widths(x, peaks, rel_height=0.5)
- rel_height=0.5 gives FWHM (full width at half maximum)
- Returns: (widths, width_heights, left_ips, right_ips)

# Raman band assignment
- Map detected peak positions (cm^-1) to known vibrational modes
- Common bands: C-H stretch ~2900-3100, C=C ~1600, C-O ~1050
- Tolerance: typically +/- 10-20 cm^-1 for matching
