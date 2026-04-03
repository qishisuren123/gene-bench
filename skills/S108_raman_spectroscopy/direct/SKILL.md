# Raman Spectroscopy Analysis

## Overview
This skill analyzes Raman spectroscopy data by subtracting fluorescence baseline, detecting spectral peaks, computing their properties (FWHM, area), and matching peaks to known vibrational bands for chemical compound identification.

## Workflow
1. Parse command-line arguments for input CSV, output JSON, baseline-method (polynomial/als), and peak-prominence threshold (default 0.1)
2. Load CSV with wavenumber_cm1 and intensity columns; sort by wavenumber if not already ordered
3. Subtract baseline: polynomial fitting (degree 5) or ALS (Asymmetric Least Squares, smoothness=1e6, asymmetry=0.01)
4. Detect peaks in baseline-corrected spectrum using scipy.signal.find_peaks with prominence threshold
5. For each peak: compute FWHM using scipy.signal.peak_widths (convert from data points to wavenumber units), compute area via trapezoidal integration around the peak
6. Match each peak position to known Raman bands: C-H stretch (~2900 cm⁻¹), C=O stretch (~1700 cm⁻¹), C-C backbone (~1000 cm⁻¹), O-H stretch (~3400 cm⁻¹)
7. Output JSON with n_peaks, and per-peak: wavenumber, intensity, fwhm_cm1, area, assignment (functional group)

## Common Pitfalls
- **Baseline overfitting**: Polynomial degree too high (>7) follows the peaks instead of the baseline — use degree 5 as default
- **FWHM unit conversion**: scipy peak_widths returns width in data point indices — multiply by spectral resolution (wavenumber spacing) to get cm⁻¹ units
- **Band assignment tolerance**: Raman bands shift ±20 cm⁻¹ from literature values depending on sample matrix, temperature, and instrument calibration
- **Fluorescence swamping**: Strong fluorescence baseline can be orders of magnitude larger than Raman signal — ALS method handles this better than polynomial

## Error Handling
- Validate that wavenumber column is numeric and spans a reasonable range (100-4000 cm⁻¹)
- Handle negative intensities after baseline subtraction by clipping to zero
- Check that at least 3 peaks are detected; if fewer, reduce prominence threshold

## Quick Reference
- Polynomial baseline: `np.polyfit(wavenumber, intensity, deg=5)` → subtract `np.polyval(coeffs, wavenumber)`
- Peak detection: `scipy.signal.find_peaks(corrected, prominence=0.1)`
- FWHM: `scipy.signal.peak_widths(corrected, peaks, rel_height=0.5)[0] * spectral_resolution`
- Peak area: `np.trapz(corrected[peak-w:peak+w], wavenumber[peak-w:peak+w])`
- Known bands: C-H ~2900, C=O ~1700, C-C ~1000, O-H ~3400 cm⁻¹
