# Example 1: Baseline correction and peak detection
import numpy as np
from scipy.signal import find_peaks, peak_widths

# Simulated Raman spectrum
wavenumbers = np.linspace(200, 3500, 1000)
baseline = 0.001 * (wavenumbers - 1500)**2 / 1e6 + 0.5
peak1 = 2.0 * np.exp(-((wavenumbers - 1000) / 15)**2)
peak2 = 3.5 * np.exp(-((wavenumbers - 1600) / 20)**2)
peak3 = 1.8 * np.exp(-((wavenumbers - 2950) / 25)**2)
noise = 0.05 * np.random.randn(len(wavenumbers))
spectrum = baseline + peak1 + peak2 + peak3 + noise

# Polynomial baseline correction
coeffs = np.polyfit(wavenumbers, spectrum, 5)
baseline_fit = np.polyval(coeffs, wavenumbers)
corrected = spectrum - baseline_fit

# Find peaks
peaks, props = find_peaks(corrected, height=0.3, distance=20, prominence=0.2)
print("Peak positions (cm^-1):", wavenumbers[peaks].astype(int))
print("Peak heights:", np.round(props['peak_heights'], 2))

# FWHM calculation
widths, _, _, _ = peak_widths(corrected, peaks, rel_height=0.5)
step = wavenumbers[1] - wavenumbers[0]
fwhm = widths * step
print("FWHM (cm^-1):", np.round(fwhm, 1))

# Example 2: Band assignment
KNOWN_BANDS = {
    'C-C stretch': (800, 1100),
    'C=C stretch': (1550, 1680),
    'C-H stretch': (2850, 3100),
}

def assign_bands(peak_positions, band_table, tolerance=20):
    assignments = {}
    for pos in peak_positions:
        for name, (lo, hi) in band_table.items():
            if lo - tolerance <= pos <= hi + tolerance:
                assignments[pos] = name
                break
        else:
            assignments[pos] = 'unknown'
    return assignments

peak_pos = wavenumbers[peaks]
result = assign_bands(peak_pos, KNOWN_BANDS)
for pos, name in result.items():
    print(f"  {pos:.0f} cm^-1 -> {name}")
