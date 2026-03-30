Write a Python CLI script that analyzes Raman spectroscopy data to identify chemical compounds.

Input: A CSV file with columns: wavenumber_cm1, intensity (Raman spectrum data).

Requirements:
1. Use argparse: --input CSV, --output JSON, --baseline-method (choices: "als", "polynomial", default "polynomial"), --peak-prominence (default 0.1)
2. Load spectrum data and validate wavenumber range (typically 200-3500 cm⁻¹)
3. Baseline correction: subtract fluorescence background
   - Polynomial: fit and subtract polynomial of degree 5
   - ALS (Asymmetric Least Squares): iterative baseline estimation with smoothness=1e6, asymmetry=0.01
4. Peak detection using scipy.signal.find_peaks with prominence threshold
5. For each peak: compute wavenumber position, intensity, FWHM, area (Gaussian fit)
6. Match peaks to known Raman bands: C-H stretch (~2900 cm⁻¹), C=O (~1700 cm⁻¹), C-C (~1000 cm⁻¹), O-H (~3400 cm⁻¹)
7. Output JSON: n_peaks, peaks (list with position, intensity, fwhm, area, assignment), baseline_method, spectral_range
8. Print summary: number of peaks, identified functional groups
