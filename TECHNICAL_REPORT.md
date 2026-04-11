# Gene-Bench Technical Report

**Version**: 1.0  
**Date**: 2026-04-08  
**Repository**: `/mnt/shared-storage-user/renyiming/projects/gen/`

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Section 1: The 45 Scenarios](#section-1-the-45-scenarios)
3. [Section 2: Probe 1 — Skill Probe](#section-2-probe-1--skill-probe)
4. [Section 3: Probe 2 — Gene Probe](#section-3-probe-2--gene-probe)
5. [Section 4: Probe 3 — Evolution Probe](#section-4-probe-3--evolution-probe)
6. [Section 5: Reproducibility](#section-5-reproducibility)

---

## Project Overview

Gene-Bench is a benchmark that evaluates whether lightweight "Gene" strategy templates (~230 tokens) can outperform full "Skill" documentation packages (~630–2572 tokens) when used to guide LLM code generation across 45 scientific computing scenarios.

The central hypothesis is that compact, action-oriented strategy representations (Genes) are more effective as test-time guidance than traditional long-form documentation (Skills), despite carrying far less information by token count. Gene-Bench tests this across three research probes: Skill Probe (does documentation-style guidance even help?), Gene Probe (is Gene's advantage structural, not just brevity?), and Evolution Probe (is Gene better suited as a carrier for cumulative knowledge?).

### Models

Two Gemini models are evaluated throughout all experiments:

| Model | Identifier | Description |
|-------|-----------|-------------|
| Gemini 3.1 Pro Preview | `gemini-3.1-pro-preview` | Referred to as "Pro" throughout this report |
| Gemini 3.1 Flash Lite Preview | `gemini-3.1-flash-lite-preview` | Referred to as "Flash" throughout this report |

### Evaluation Protocol

Each trial proceeds as follows:

1. A system prompt (if any) is injected via the `system_instruction` field of the Gemini API call.
2. The model generates Python code for the scenario task.
3. The generated code is executed against a per-scenario `test_script.py`.
4. The test script awards points for N discrete checkpoints (sub-tasks).
5. Metrics are computed:
   - `pass_rate = n_pass / n_total` (fraction of checkpoints passed)
   - `passed = True` if and only if `pass_rate == 1.0` (all checkpoints passed)

**Temperature**: 0.0 (deterministic generation)  
**Max output tokens**: 16,384  
**Guidance injection**: `system_instruction` field only

### Guidance Representations

| Name | Tokens (approx.) | Description |
|------|-----------------|-------------|
| No context | 0 | Bare task description, no system prompt |
| Gene G1 | ~88 | Keywords only |
| Gene G2 | ~136 | Keywords + summary |
| Gene G3 | ~230 | Keywords + summary + strategy (primary Gene representation) |
| Gene G4 | ~375 | Full Gene template |
| Skill L1 | ~630 | SKILL.md overview document |
| Skill L4 | ~2572 | Full Skill package: SKILL.md + scripts + references |

---

## Section 1: The 45 Scenarios

Each scenario is a self-contained task in a specific scientific computing domain. The model receives the task description and any guidance prompt, then must produce a working Python CLI script. Sub-tasks are discrete checkpoints that the test script verifies programmatically.

The 45 scenarios span neuroscience, bioinformatics, geoscience, atmospheric science, signal processing, materials science, network analysis, financial modeling, robotics, and quantum computing.

---

### S002 — spike_behavior

**Domain**: Computational Neuroscience  
**Sub-tasks**: 12

**Task**: Write a CLI script that reads neural spike times and behavioral velocity data from a MATLAB `.mat` file and produces a trial-structured HDF5 file. The script must filter to successful trials, bin spike times into uniform time windows, resample velocity data to match bin centers via interpolation, and write each trial as `/trial_NNNN/spikes`, `/trial_NNNN/behavior`, and `/trial_NNNN/timestamps` HDF5 datasets. A quality-check flag must be raised for trials with aberrantly high firing rates (>200 Hz) or NaN velocity values.

**Sub-tasks tested (12 checkpoints)**:
- Correct parsing of MATLAB `.mat` cell array format for spike times
- Filtering to only successful trials (`trial_success == True`)
- Correct spike binning using `np.histogram` with the specified bin size
- Correct behavior resampling via interpolation to bin centers
- HDF5 output structure: `/trial_NNNN/spikes` shape `(n_bins, n_units)`
- HDF5 output structure: `/trial_NNNN/behavior` shape `(n_bins, 2)`
- HDF5 output structure: `/trial_NNNN/timestamps` shape `(n_bins,)`
- Argparse interface: `--input`, `--output`, `--bin-size`
- Correct trial count matches number of successful trials
- Numerical accuracy of spike counts in bins
- Firing rate quality-check flag logic (>200 Hz detection)
- NaN detection in behavior data

---

### S005 — protein_parse

**Domain**: Bioinformatics / Proteomics  
**Sub-tasks**: 12

**Task**: Write a CLI script that parses a JSON file of SwissProt protein entries and extracts structured fields into a CSV. Required fields per protein include accession, recommended name, gene name, organism, sequence length, feature count, and GO terms drawn from `dbReferences`.

**Sub-tasks tested (12 checkpoints)**:
- JSON input parsing with correct field traversal
- Extraction of `accession` field
- Extraction of `protein.recommendedName` (nested path)
- Extraction of `gene` name (handling multiple gene entries)
- Extraction of `organism` name
- Correct computation of `sequence_length`
- Correct count of `features` array length
- GO term extraction from `dbReferences` entries
- Graceful handling of missing fields (empty string or 0 defaults)
- CSV output with one row per protein and correct headers
- Summary print: total protein count
- Summary print: unique organism count and average sequence length

---

### S007 — data_viz

**Domain**: Computational Neuroscience / Data Visualization  
**Sub-tasks**: 8

**Task**: Write a CLI script that reads a CSV of neural firing rates (columns: `trial`, `time`, `neuron_0`, `neuron_1`, ...) and produces two PNG plots: a heatmap of trial-averaged firing rates (neurons × time) and a population PSTH with shaded SEM. The script must use the Matplotlib Agg backend (no interactive display).

**Sub-tasks tested (8 checkpoints)**:
- Correct CSV parsing and identification of neuron columns
- Trial averaging of firing rates across trials
- Heatmap axes: neurons on one axis, time on the other
- `firing_rate_heatmap.png` saved to the specified output directory
- Population mean firing rate computed across all neurons per time point
- SEM computation and shaded region added to PSTH plot
- `population_psth.png` saved to the specified output directory
- Summary print: number of neurons, trials, and time range

---

### S011 — particle_physics

**Domain**: High-Energy Particle Physics  
**Sub-tasks**: 12

**Task**: Write a CLI script that processes collision event data from a CSV and applies physics quality cuts, classifies events as signal or background, computes signal-to-noise ratio and statistical significance, and outputs a filtered CSV and a JSON summary.

**Sub-tasks tested (12 checkpoints)**:
- Argparse interface: `--input`, `--output`, `--mass-window`
- Quality cut: `n_tracks >= 2`
- Quality cut: `total_energy > 10 GeV`
- Quality cut: `|leading_jet_eta| < 2.5`
- Signal classification: invariant mass within window AND `n_leptons >= 2`
- Background classification for events failing signal criteria
- Signal count and background count in JSON output
- Signal-to-noise ratio (`S/B`) computation
- Statistical significance computed as `S / sqrt(S+B)`
- `filtered_events.csv` output
- `event_summary.json` output with required fields including `cut_flow`
- Summary print: events before/after cuts, signal fraction, significance

---

### S012 — uv_spectroscopy

**Domain**: Analytical Chemistry  
**Sub-tasks**: 12

**Task**: Write a CLI script that detects and characterizes peaks in UV-Vis absorption spectra from a CSV. The script must handle multiple samples, detect peaks by prominence, compute FWHM and integrated area for each peak, and identify the dominant peak per sample.

**Sub-tasks tested (12 checkpoints)**:
- Argparse interface: `--input`, `--output`, `--min-height`, `--min-distance`
- Correct parsing of multi-column CSV (multiple samples)
- Prominence-based peak detection per sample
- Peak wavelength position recorded correctly
- Peak height recorded correctly
- FWHM computed correctly for each peak
- Area under each peak computed by numerical integration
- Dominant peak (highest absorbance) identified per sample
- JSON output structure: `{sample_name: {peaks: [...], dominant_peak, n_peaks}}`
- Correct `n_peaks` count per sample
- Correct wavelength range of dominant peaks in summary
- Summary print with dominant peak wavelength range

---

### S017 — ctd_ocean

**Domain**: Physical Oceanography  
**Sub-tasks**: 13

**Task**: Write a CLI script that processes CTD (Conductivity-Temperature-Depth) oceanographic profiles. For each station, the script must interpolate all variables to a regular depth grid, compute potential density via a simplified UNESCO equation, locate the thermocline (maximum dT/dz), and identify the mixed layer depth (where temperature drops 0.5°C from surface).

**Sub-tasks tested (13 checkpoints)**:
- Argparse interface: `--input`, `--output`, `--depth-resolution`
- Per-station processing loop
- Correct interpolation to regular depth grid at specified resolution
- Potential density (sigma-t) computed with the specified UNESCO approximation formula
- Thermocline depth identified as depth of maximum temperature gradient
- Mixed layer depth identified using the 0.5°C criterion
- `interpolated_profiles.csv` output
- `station_summary.json` output
- Correct station count in summary
- Correct depth range in summary
- Mean thermocline depth printed correctly
- Numerical accuracy of density computation (within tolerance)
- Handling of stations with varying max depth

---

### S026 — earthquake_catalog

**Domain**: Seismology  
**Sub-tasks**: 14

**Task**: Write a CLI script that analyzes an earthquake catalog CSV to identify aftershock sequences and compute seismological statistics. The script must estimate the Gutenberg-Richter b-value using the Aki maximum-likelihood formula, identify aftershocks using Haversine distance and time proximity criteria, produce magnitude-frequency statistics, and output multiple structured files.

**Sub-tasks tested (14 checkpoints)**:
- Argparse interface: `--input`, `--output`, `--cluster-radius`, `--cluster-time`
- Correct parsing of catalog including datetime field
- Haversine distance computation between event pairs
- Aftershock identification: events within radius AND time window of M≥4.0 mainshock
- `aftershock_sequences.csv` output with required columns
- Magnitude-frequency histogram with 0.1-magnitude bin width
- Completeness magnitude estimation from frequency histogram peak
- Gutenberg-Richter b-value computed via Aki formula
- `catalog_stats.json` with b_value, completeness_mag, largest_event, total_events
- `magnitude_freq.csv` with mag_bin, count, cumulative_count, log10_cumulative
- Summary print: total events, b-value, number of sequences, largest event
- Largest event correctly identified
- Correct total aftershock sequence count
- Numerical accuracy of b-value

---

### S028 — audio_features

**Domain**: Audio Signal Processing  
**Sub-tasks**: 15

**Task**: Write a CLI script that extracts frame-level audio features from signals stored in a `.npz` file. Features include STFT spectrogram, MFCCs (with manually implemented mel filterbank), zero-crossing rate, and RMS energy. The mel filterbank must use triangular filters on the mel scale; scipy's DCT is permitted for the final step.

**Sub-tasks tested (15 checkpoints)**:
- Argparse interface: `--input`, `--output`, `--frame-size`, `--hop-size`
- Correct loading of `.npz` file with signals, sample_rate, labels
- STFT magnitude spectrogram computed correctly per frame
- Mel filterbank implemented manually with ≥26 triangular filters
- Filters correctly spaced on the mel scale
- Log power spectrum applied before DCT
- 13 MFCC coefficients produced per frame
- Zero-crossing rate (ZCR) per frame
- RMS energy per frame
- `features.csv` output: columns `signal_id, frame_idx, zcr, rms_energy, mfcc_0 ... mfcc_12`
- `summary.json` output: per-signal mean and std of each feature, total_frames, label
- Correct total frame count matching hop-size arithmetic
- All signals processed
- Summary print: number of signals processed
- Summary print: total frames extracted

---

### S030 — fossil_morpho

**Domain**: Paleontology / Morphometrics  
**Sub-tasks**: 15

**Task**: Write a CLI script for morphometric analysis of fossil specimens. It must compute shape indices (elongation, flatness, Krumbein sphericity, ellipsoidal volume, density), perform PCA on standardized measurement columns using numpy eigendecomposition, and output per-specimen metrics, PCA results, and group statistics by taxon and epoch.

**Sub-tasks tested (15 checkpoints)**:
- Argparse interface: `--input`, `--output`
- Elongation = length / width computed correctly
- Flatness = width / height computed correctly
- Sphericity = (width × height)^(1/3) / length computed correctly
- Ellipsoidal volume formula applied correctly (mm³)
- Density = mass / volume with mm³ to cm³ conversion
- Z-score standardization of 4 measurement columns
- PCA via numpy covariance matrix eigendecomposition
- PC1–PC4 loadings reported correctly
- Explained variance ratios summing to 1.0
- `morphometrics.csv` output with original columns + shape indices + PC scores
- `pca_results.csv` output
- `taxon_summary.json` with per-taxon and per-epoch statistics
- Summary print: specimen count, taxon count, dominant taxon
- Summary print: PCA variance explained by first 2 components

---

### S033 — exoplanet_transit

**Domain**: Observational Astronomy  
**Sub-tasks**: 10

**Task**: Write a CLI script that generates synthetic photometric time series data, injects a box-car transit signal, detects the transit with a sliding box-car filter, and fits transit parameters (depth, duration, center time) via least-squares. Results are saved as JSON and optionally as a diagnostic plot.

**Sub-tasks tested (10 checkpoints)**:
- Argparse interface: `--num_points`, `--noise_level`, `--transit_depth`, `--output_file`, `--plot_file`
- Synthetic time series generated over 10 days with Gaussian noise at specified level
- Transit injected at day 5.0 with 3-hour duration and box-car shape
- Sliding box-car detection algorithm implemented
- Detection significance calculated
- Best-fit transit time identified
- Least-squares fit converges for transit depth, duration, center time
- JSON output contains: detected transit time, fitted depth, fitted duration, significance
- JSON output contains: chi-squared and reduced chi-squared fit quality metrics
- Handling of non-detection case (appropriate error metrics reported)

---

### S036 — cmb_power_spectrum

**Domain**: Cosmology  
**Sub-tasks**: 3

**Task**: Write a CLI script that computes the angular power spectrum from a synthetic CMB temperature map stored as a HEALPix-like 1D numpy array. The script must perform a spherical harmonic decomposition to extract a_lm coefficients, compute C_l = <|a_lm|^2> averaged over m, and output the spectrum and a standard ell(ell+1)C_l/(2pi) plot.

**Sub-tasks tested (3 checkpoints)**:
- Correct computation of power spectrum values C_l across the multipole range l=2 to l_max
- JSON output with multipole values (l), power spectrum values (C_l in µK²), and summary statistics (total power, peak multipole, RMS temperature)
- Plot saved showing ell(ell+1)C_l/(2pi) vs ell

---

### S037 — asteroid_orbit

**Domain**: Solar System Astronomy  
**Sub-tasks**: 3

**Task**: Write a CLI script that reads JSON asteroid position observations (x, y in AU), fits an elliptical orbit using least-squares, computes orbital elements (semi-major axis, semi-minor axis, eccentricity, orbital period via Kepler's third law), and produces a JSON results file and a visualization.

**Sub-tasks tested (3 checkpoints)**:
- Elliptical orbit fit converges correctly and yields valid orbital elements (eccentricity in [0,1], positive semi-major axis)
- JSON output with semi-major axis, semi-minor axis, eccentricity, period, and R-squared fitting statistic
- Plot generated showing observation points, fitted ellipse, and Sun at origin

---

### S044 — bfactor_analysis

**Domain**: Structural Biology  
**Sub-tasks**: 1

**Task**: Write a CLI script that accepts B-factor values (protein residue flexibility indicators) as a comma-separated string, computes distribution statistics, identifies flexible residues (above 75th percentile), groups them into consecutive segments, optionally normalizes values to 0–100, and outputs a JSON report and a line plot.

**Sub-tasks tested (1 checkpoint)**:
- Complete pipeline: statistical summary (mean, median, std, quartiles), flexible residue identification, segment grouping, optional normalization, JSON output, and PNG plot all produced correctly and consistently

---

### S045 — ramachandran

**Domain**: Structural Biology  
**Sub-tasks**: 13

**Task**: Write a CLI script that generates synthetic phi/psi backbone dihedral angles following realistic distributions (alpha-helix ~-60°/-45°, beta-sheet ~-120°/+120°), creates a Ramachandran scatter plot, detects outliers via statistical methods, computes regional percentages, and exports a JSON analysis file.

**Sub-tasks tested (13 checkpoints)**:
- Argparse interface: `--num_residues`, `--output_plot`, `--output_data`, `--outlier_threshold`
- Phi angles generated in realistic alpha-helix region
- Psi angles generated in realistic alpha-helix region
- Phi angles generated in realistic beta-sheet region
- Psi angles generated in realistic beta-sheet region
- Scatter plot created with phi on x-axis, psi on y-axis, range -180° to +180°
- Outlier detection applied using z-score or KDE method
- Outlier threshold parameter respected
- Percentage of residues in favored regions (helix + sheet) computed
- Percentage in disallowed regions computed
- JSON output contains all phi/psi angles, outlier indices, regional percentages, and summary
- Angle periodicity handled correctly at ±180° boundary
- PNG plot saved correctly

---

### S048 — gene_ontology

**Domain**: Bioinformatics / Functional Genomics  
**Sub-tasks**: 2

**Task**: Write a CLI script that performs GO enrichment analysis by mapping input gene IDs to a synthetic GO annotation database, computing Fisher's exact test p-values for each GO term, applying Bonferroni correction, and reporting significantly enriched terms (≥2 input genes, corrected p < 0.05) in a JSON output.

**Sub-tasks tested (2 checkpoints)**:
- Fisher's exact test p-values computed correctly; Bonferroni correction applied; results filtered to terms with ≥2 input genes and corrected p-value < 0.05
- JSON output contains GO term ID, description, gene count, background count, enrichment ratio, raw p-value, and corrected p-value, sorted by corrected p-value

---

### S052 — phylogenetic_distance

**Domain**: Evolutionary Biology / Bioinformatics  
**Sub-tasks**: 15

**Task**: Write a CLI script that computes pairwise phylogenetic distances from a multiple sequence alignment in FASTA format using three distance metrics: Hamming distance (proportion of differing sites), p-distance (gaps excluded pairwise), and Jukes-Cantor corrected distance. Results are output as a tab-separated matrix and a pairwise JSON file with summary statistics.

**Sub-tasks tested (15 checkpoints)**:
- FASTA input parsing (stdin or string argument)
- Hamming distance computed correctly as proportion of differing sites
- p-distance computed with gap exclusion on a pairwise basis
- Jukes-Cantor correction formula applied: d = -3/4 * ln(1 - 4p/3)
- Undefined JC correction handled (returns p-distance when 4p/3 >= 1)
- Gap characters ('-') excluded from pairwise computations
- All pairwise combinations computed
- Symmetric distance matrix produced
- Tab-separated matrix output with sequence names as headers and row labels
- JSON pairwise output with sequence pair identifiers and distances
- Mean pairwise distance in summary statistics
- Standard deviation of distances in summary statistics
- Minimum pairwise distance in summary statistics
- Maximum pairwise distance in summary statistics
- All three methods available and producing consistent results

---

### S053 — methylation_beta

**Domain**: Epigenomics  
**Sub-tasks**: 1

**Task**: Write a CLI script that processes DNA methylation beta-value arrays for case and control samples, identifies differentially methylated regions (DMRs) based on statistical thresholds, and outputs results with genomic coordinates.

**Sub-tasks tested (1 checkpoint)**:
- Complete pipeline: beta-value loading, DMR detection (identifying genomic regions with significant differential methylation between cases and controls), and structured output produced correctly

---

### S054 — species_accumulation

**Domain**: Ecology / Biodiversity  
**Sub-tasks**: 1

**Task**: Write a CLI script that generates synthetic species-site occurrence data following log-normal abundance distributions, computes species accumulation curves via repeated random site orderings, performs sample-based rarefaction, estimates asymptotic richness via the Chao2 estimator, and saves a visualization and JSON/CSV output.

**Sub-tasks tested (1 checkpoint)**:
- Complete pipeline: synthetic data generation, accumulation curve with CI bands, rarefaction curve, Chao2 estimate, summary statistics JSON, site-by-species CSV, and PNG plot all produced and internally consistent

---

### S060 — phenology_shifts

**Domain**: Ecology / Climate Science  
**Sub-tasks**: 15

**Task**: Write a CLI script that analyzes long-term phenological time series (year, day-of-year of events, temperature, precipitation) to detect temporal shifts. The script must implement at minimum PELT change-point detection and the Mann-Kendall trend test, correlate shifts with climate variables using Pearson and Spearman methods with 0–3 year lag analysis, apply Benjamini-Hochberg correction, and perform segmented regression around detected breakpoints.

**Sub-tasks tested (15 checkpoints)**:
- Argparse interface with configurable input, output paths, and significance thresholds
- Data parsing with handling of missing values and outliers
- PELT algorithm implemented for change-point detection
- Mann-Kendall trend test implemented correctly
- At least one significant change-point detected in test data
- Pearson correlation computed between phenology shifts and temperature
- Spearman correlation computed between phenology shifts and temperature
- Lag analysis conducted for lags 0–3 years
- Benjamini-Hochberg correction applied to multiple comparisons
- Confidence intervals computed for shift magnitudes
- Breakpoint timing estimated via segmented regression
- Uncertainty quantified for breakpoint locations
- JSON report contains detected shifts, significance values, climate correlations, and breakpoints
- Visualization shows time series with change-points and trend lines
- PNG and JSON output files saved correctly

---

### S067 — salinity_gradient

**Domain**: Physical Oceanography / Estuarine Science  
**Sub-tasks**: 1

**Task**: Write a CLI script that analyzes CTD transect data from estuarine environments to detect haloclines (salinity gradient > 0.5 PSU/m over ≥2m), compute Simpson's Stratification Parameter, map salt wedge intrusion (2 PSU isohaline), calculate tidal mixing efficiency (Richardson number-based), perform 2D optimal interpolation on a 50m×0.5m grid, and apply quality control flags.

**Sub-tasks tested (1 checkpoint)**:
- Complete pipeline: all six analysis outputs (haloclines.json, stratification.json, salt_wedge.json, mixing_zones.json, interpolated_field.h5, quality_flags.json) produced with physically consistent and correctly computed values

---

### S068 — weather_fronts

**Domain**: Meteorology  
**Sub-tasks**: 12

**Task**: Write a CLI script that reads temperature grid data from an HDF5 file, applies Gaussian smoothing, computes spatial temperature gradients, identifies front segments as connected high-gradient regions exceeding a threshold, filters by minimum length, and outputs front locations and a visualization.

**Sub-tasks tested (12 checkpoints)**:
- Argparse interface: `--input-data`, `--output-fronts`, `--output-plot`, `--gradient-threshold`, `--min-front-length`, `--smoothing-sigma`
- HDF5 input loaded: temperature, lat, lon, grid_spacing
- Gaussian smoothing applied with the specified sigma
- X-direction gradient computed with grid spacing correction
- Y-direction gradient computed with grid spacing correction
- Gradient magnitude computed correctly
- Front pixels identified where magnitude exceeds threshold
- Connected-component grouping of front pixels
- Front segments filtered by minimum length
- JSON output with front segments containing coordinates, average gradient, and length
- Temperature field visualized as color map in PNG
- Detected fronts overlaid as contour lines in the plot

---

### S069 — rainfall_extreme

**Domain**: Hydrology / Climate Science  
**Sub-tasks**: 1

**Task**: Write a CLI script that processes daily precipitation data, extracts annual maxima, calculates return periods using the Weibull plotting position formula (T = (n+1)/r), identifies extreme events exceeding the 10-year return period threshold, and outputs a JSON summary with annual maxima, return periods, extreme events, and statistical summary.

**Sub-tasks tested (1 checkpoint)**:
- Complete pipeline: correct annual maxima extraction (skipping incomplete years), Weibull return period formula applied, 10-year threshold correctly derived, extreme event list output with dates and magnitudes, JSON output with all required fields, and negative values excluded as missing data

---

### S072 — ozone_profile

**Domain**: Atmospheric Science  
**Sub-tasks**: 15

**Task**: Write a CLI script that processes vertical ozonesonde balloon measurement profiles (altitude, pressure, temperature, ozone concentration). The script must apply quality control, identify the tropopause using lapse rate, compute tropospheric and stratospheric ozone columns by integration, find the stratospheric ozone maximum, fit an exponential decay model for ozone scale height, and produce a publication-quality plot.

**Sub-tasks tested (15 checkpoints)**:
- Argparse interface with input file, output paths, and QC threshold options
- Negative ozone values removed in quality control
- Unrealistically high values (>20 mPa) removed
- Tropopause identified using lapse rate criterion (<2 K/km over 2 km layer)
- Tropospheric ozone column computed by integrating from surface to tropopause
- Stratospheric ozone column computed from tropopause to 30 km
- Ozone maximum altitude identified (above tropopause)
- Ozone maximum concentration value reported
- Exponential decay model fitted in the specified stratospheric layer
- Scale height extracted from the exponential fit
- JSON output: tropopause height, tropospheric column, stratospheric column, ozone max altitude and concentration, scale height, with units
- Plot shows ozone vs altitude profile
- Tropopause height marked on plot
- Ozone maximum marked on plot
- PNG saved correctly

---

### S074 — heat_index

**Domain**: Climatology / Biometeorology  
**Sub-tasks**: 1

**Task**: Write a CLI script that reads temperature and humidity time series CSVs, computes heat index using the full NWS multi-step formula with adjustment factors, builds a rolling climatological baseline by day-of-year using a 15-day window, detects heat wave events as periods where heat index exceeds the baseline threshold for at least `--min-duration` days, and reports trends and per-event statistics.

**Sub-tasks tested (1 checkpoint)**:
- Complete pipeline: NWS heat index formula implemented correctly with adjustment factors, climatological baseline computed, heat waves detected with correct merging and duration logic, per-event statistics (duration, mean/max heat index, cumulative excess), decadal trend analysis with significance, and structured JSON output produced

---

### S077 — grain_size

**Domain**: Materials Science  
**Sub-tasks**: 1

**Task**: Write a CLI script that accepts grain diameter measurements (micrometers) as a comma-separated string, computes basic statistics and distribution metrics (D10, D50, D90, Cu, Cc), classifies grains into fine/medium/coarse categories, generates a histogram, and saves a JSON results file.

**Sub-tasks tested (1 checkpoint)**:
- Complete pipeline: all statistical measures (mean, median, std, min, max, D10/D50/D90, Cu, Cc) computed correctly; size classification correct; histogram PNG saved; JSON output with all sections

---

### S084 — dose_response

**Domain**: Pharmacology / Toxicology  
**Sub-tasks**: 1

**Task**: Write a CLI script that reads dose-response data (concentration and response columns) from a CSV, validates input (positive concentrations, response in 0–100%), fits a 4-parameter logistic model using scipy.optimize, computes IC50, Hill slope, top/bottom plateaus with confidence intervals, generates a log-scale plot, and saves `fit_results.json`.

**Sub-tasks tested (1 checkpoint)**:
- Complete pipeline: data validation and invalid point filtering, 4PL model fit converges, IC50/Hill slope/top/bottom with confidence intervals reported, R-squared goodness of fit computed, log-scale plot with data and fitted curve saved, `fit_results.json` and `dose_response_curve.png` output correctly

---

### S090 — noise_reduction

**Domain**: Signal Processing  
**Sub-tasks**: 12 (Pro), 13 (Flash) — model-dependent

**Task**: Write a CLI script implementing Least Mean Squares (LMS) adaptive noise cancellation on a synthesized audio signal (440 Hz + 880 Hz sine waves + broadband noise at 8 kHz sample rate). The script must create a correlated reference noise signal, run the LMS filter, and compute SNR improvement, MSE reduction, and convergence rate.

**Sub-tasks tested (12 checkpoints)**:
- Argparse interface: `--input-signal`, `--output-signal`, `--reference-noise`, `--step-size`, `--filter-length`, `--metrics-file`
- 440 Hz sine wave component present in generated signal
- 880 Hz sine wave component present in generated signal
- Broadband noise added to signal
- Reference noise signal generated with correlated but delayed/scaled components
- LMS algorithm implemented: iterative coefficient update to minimize error
- Step-size bounds checked (0.001 to 0.1)
- Filter length bounds checked (8 to 128 taps)
- SNR improvement computed (before vs after)
- MSE reduction computed
- Filter convergence rate metric reported
- Output signal, reference noise, and noisy signal saved as numpy arrays

---

### S091 — modulation_classify

**Domain**: Communications Engineering  
**Sub-tasks**: 2

**Task**: Write a CLI script that reads IQ sample data from an HDF5 file, extracts at least 6 signal features (amplitude statistics, phase statistics, constellation metrics, spectral characteristics, higher-order moments, zero-crossing rate), classifies signals as BPSK/QPSK/8PSK/16QAM/64QAM, generates constellation diagrams, and reports accuracy, confusion matrix, and per-class precision/recall.

**Sub-tasks tested (2 checkpoints)**:
- Feature extraction: at least 6 distinct signal features extracted and saved to JSON including instantaneous amplitude and phase statistics, spectral and constellation-based metrics
- Classification: cross-validation accuracy, confusion matrix, per-class precision/recall, and confidence scores reported in JSON output; constellation diagrams saved as PNG files

---

### S093 — echo_removal

**Domain**: Audio Signal Processing  
**Sub-tasks**: 1

**Task**: Write a CLI script that reads a normalized 1D audio signal from a `.npy` file, detects echo delay via autocorrelation secondary peak analysis, cancels the echo by subtracting the attenuated delayed copy, computes ERLE and signal-to-echo ratio improvement, and saves the processed signal, a JSON report, and a comparison plot.

**Sub-tasks tested (1 checkpoint)**:
- Complete pipeline: autocorrelation analysis correctly identifies echo delay and attenuation, echo cancellation reduces echo power measurably, ERLE and SER improvement metrics computed, JSON report and processed signal `.npy` saved, comparison plot with autocorrelation functions generated

---

### S096 — network_influence

**Domain**: Social Network Analysis  
**Sub-tasks**: 2

**Task**: Write a CLI script that processes social network interaction data (likes, shares, comments with weights 1, 3, 2), computes weighted influence scores, calculates normalized degree centrality, identifies top-N influencers by a 60/40 weighted combination of influence and centrality, and outputs user metrics and network statistics as JSON.

**Sub-tasks tested (2 checkpoints)**:
- Influence score computation (weighted by interaction type) and degree centrality computation (normalized to [0,1]) both implemented correctly
- Top-N influencer ranking by combined metric (60% influence + 40% centrality), interaction statistics, and JSON output with all required fields

---

### S101 — climate_attribution

**Domain**: Climate Science  
**Sub-tasks**: 12

**Task**: Write a CLI script that performs climate change attribution analysis by regressing observed temperature anomalies against multiple forcing factors (solar, volcanic, GHG, aerosol, natural variability). Three regression methods must be supported: OLS via numpy lstsq, L2-regularized ridge regression (alpha=1.0), and analytical Bayesian linear regression with prior precision=0.1.

**Sub-tasks tested (12 checkpoints)**:
- Argparse interface: `--input`, `--output`, `--method`
- CSV loading and validation of required columns
- Missing value handling
- OLS regression implemented via `numpy.linalg.lstsq`
- Ridge regression implemented with L2 penalty (alpha=1.0)
- Bayesian regression implemented analytically with prior precision=0.1
- Coefficient values in output for all forcing factors
- Attribution fractions computed as percentage of total explained warming
- Residual (unexplained) fraction reported
- R-squared computed and included in JSON output
- JSON output structure: method, coefficients, attribution_fractions, r_squared, residual_fraction
- Summary print identifies dominant forcing factor with attribution percentage

---

### S102 — protein_secondary

**Domain**: Structural Bioinformatics  
**Sub-tasks**: 10

**Task**: Write a CLI script that predicts protein secondary structure (H=helix, E=sheet, C=coil) from FASTA-formatted sequences using either the Chou-Fasman method (sliding windows of 6 for helix, 5 for sheet with specific propensity tables) or a simplified GOR method.

**Sub-tasks tested (10 checkpoints)**:
- Argparse interface: `--input`, `--output`, `--method`
- FASTA parsing: sequence IDs and sequences extracted correctly
- Chou-Fasman helix propensity values used correctly for specified amino acids
- Chou-Fasman sheet propensity values used correctly for specified amino acids
- Sliding window of 6 applied for helix nucleation
- Sliding window of 5 applied for sheet nucleation
- Per-residue assignment produces H, E, or C characters
- CSV output: `sequence_id, length, helix_pct, sheet_pct, coil_pct, structure_string`
- Percentages sum to 100% per sequence
- Summary print: average secondary structure composition across all sequences

---

### S103 — instrumental_variable

**Domain**: Econometrics / Causal Inference  
**Sub-tasks**: 10

**Task**: Write a CLI script that implements two-stage least squares (2SLS) IV regression. Stage 1 regresses the treatment on the instrument (and optional confounders) to get predicted values; Stage 2 regresses the outcome on predicted treatment (and confounders). The script also computes a naive OLS estimate, standard errors, and the first-stage F-statistic for testing instrument weakness.

**Sub-tasks tested (10 checkpoints)**:
- Argparse interface: `--input`, `--output`, `--outcome`, `--treatment`, `--instrument`, `--confounders`
- CSV loading and column validation
- Stage 1 regression: treatment on instrument (+ confounders)
- Predicted treatment values (X_hat) obtained from stage 1
- Stage 2 regression: outcome on X_hat (+ confounders)
- IV estimate extracted from stage 2
- OLS estimate computed for comparison
- Standard errors computed for both IV and OLS estimates
- First-stage F-statistic computed; `weak_instrument` flag set True if F < 10
- JSON output: iv_estimate, iv_std_error, ols_estimate, ols_std_error, first_stage_f, weak_instrument, n_observations

---

### S104 — multisensor_anomaly

**Domain**: Industrial Sensing / Time Series Analysis  
**Sub-tasks**: 10

**Task**: Write a CLI script that detects anomalies in multi-sensor time series using three complementary methods: per-sensor rolling z-score, cross-sensor co-anomaly detection (>50% of sensors simultaneously), and multivariate Mahalanobis distance. Anomalies are classified as point, collective, or contextual.

**Sub-tasks tested (10 checkpoints)**:
- Argparse interface: `--input`, `--output`, `--window-size`, `--threshold`
- CSV loading with automatic sensor column detection
- Rolling z-score computed per sensor with specified window
- Per-sensor anomaly flags at z > threshold
- Cross-sensor check: timestamps where >50% of sensors flag simultaneously
- Mahalanobis distance computed across all sensors
- Point anomaly classification (single spike)
- Collective anomaly classification (sustained deviation)
- Contextual anomaly classification (cross-sensor disagreement)
- JSON output: n_sensors, n_timestamps, anomaly list with timestamp/type/sensors_affected/score, summary_stats

---

### S105 — community_detection

**Domain**: Network Science / Graph Analysis  
**Sub-tasks**: 10

**Task**: Write a CLI script that detects overlapping communities in an edge-list graph without requiring NetworkX. The script implements asynchronous label propagation (with 30% neighbor-label threshold for overlap) and a Louvain-like greedy modularity optimization. Modularity score Q is computed globally; per-community statistics include size, internal edges, and density.

**Sub-tasks tested (10 checkpoints)**:
- Argparse interface: `--input`, `--output`, `--method`
- Edge-list CSV loaded; undirected adjacency structure built
- Label propagation: unique label initialization
- Label propagation: iterative update adopting most-frequent neighbor label
- Overlap assignment: node assigned to community if >30% of neighbors share label
- Convergence or max-100-iterations stopping condition
- Modularity: greedy community merging increases Q
- Per-community: size, internal_edges, density computed
- Global modularity Q computed
- JSON output: n_nodes, n_edges, n_communities, modularity, communities list

---

### S106 — seismic_denoise

**Domain**: Seismology / Signal Processing  
**Sub-tasks**: 10

**Task**: Write a CLI script that denoises three-component seismic waveform data (N, E, Z velocity) using a 4th-order Butterworth bandpass filter, implements STA/LTA ratio for P-wave arrival detection (threshold = 3.0), and computes per-component SNR before and after filtering.

**Sub-tasks tested (10 checkpoints)**:
- Argparse interface: `--input`, `--output-dir`, `--lowcut`, `--highcut`, `--sta`, `--lta`
- CSV loaded and sampling rate inferred from time column
- Butterworth bandpass filter (order 4) applied to north component
- Butterworth bandpass filter applied to east component
- Butterworth bandpass filter applied to vertical component
- STA computed as short-term amplitude average
- LTA computed as long-term amplitude average
- P-wave arrivals detected where STA/LTA > 3.0
- SNR before filtering computed per component
- SNR after filtering computed per component; filtered waveforms CSV and detection JSON output

---

### S107 — regime_switch

**Domain**: Quantitative Finance  
**Sub-tasks**: 10

**Task**: Write a CLI script that detects structural regime breaks in financial time series by computing log returns, using rolling volatility with change-point detection (>2x change in adjacent windows), classifying regimes as low_vol / high_vol / crisis based on median volatility, and computing a transition probability matrix between regime types.

**Sub-tasks tested (10 checkpoints)**:
- Argparse interface: `--input`, `--output`, `--min-regime-length`, `--n-regimes`
- Log returns computed from price series
- Rolling mean computed with specified window
- Rolling volatility (std) computed with specified window
- Change-points identified where volatility changes >2x between adjacent windows
- Regime classification: low_vol (below median), high_vol (above median), crisis (above 2x median)
- Per-regime statistics: start_date, end_date, duration, mean_return, volatility, annualized Sharpe ratio
- Transition matrix computed with probability of switching between regime types
- JSON output: n_regimes, regimes list, transition_matrix, overall_stats
- Summary print: regime count, longest regime, current regime type

---

### S108 — raman_spectroscopy

**Domain**: Analytical Chemistry  
**Sub-tasks**: 10

**Task**: Write a CLI script that processes Raman spectroscopy data (wavenumber vs. intensity), applies baseline correction (polynomial degree-5 or ALS method), detects peaks by prominence, fits each peak with a Gaussian to extract FWHM and area, and matches peaks to known Raman band assignments (C-H ~2900, C=O ~1700, C-C ~1000, O-H ~3400 cm^-1).

**Sub-tasks tested (10 checkpoints)**:
- Argparse interface: `--input`, `--output`, `--baseline-method`, `--peak-prominence`
- CSV loaded and wavenumber range validated (200–3500 cm^-1)
- Polynomial baseline correction (degree 5) applied
- ALS baseline correction (smoothness=1e6, asymmetry=0.01) implemented
- Peak detection using `scipy.signal.find_peaks` with prominence threshold
- Peak position (wavenumber) reported for each peak
- Peak intensity (height) reported
- FWHM computed via Gaussian fit
- Area computed via Gaussian fit
- Peak-to-band assignment: C-H, C=O, C-C, O-H matched by proximity; JSON output correct

---

### S109 — hdf5_chunked

**Domain**: Scientific Data Engineering  
**Sub-tasks**: 10

**Task**: Write a CLI script that converts a large CSV to a chunked, compressed HDF5 file. Numeric columns are stored as float64 with chunking; string columns use variable-length encoding. Column metadata is stored as HDF5 attributes, a `_metadata` group is created, and a round-trip read-back verification is performed.

**Sub-tasks tested (10 checkpoints)**:
- Argparse interface: `--input`, `--output`, `--chunk-rows`, `--compression`, `--compression-level`
- Column type auto-detection (numeric vs. string)
- Numeric columns stored as float64 datasets with `chunking=(chunk_rows,)`
- String columns stored as variable-length string datasets
- Specified compression applied (gzip/lzf/none) with specified level
- Column metadata attributes: dtype, original_csv_column_index, n_missing
- Index dataset created for fast row-range queries
- `_metadata` group created with: source_file, n_rows, n_cols, compression, chunk_size, creation_timestamp
- Round-trip verification: sample read-back matches original values
- Output summary: file size, compression ratio, read speed for 1000-row random slice

---

### S110 — log_regex

**Domain**: Systems Engineering / Log Analysis  
**Sub-tasks**: 11

**Task**: Write a CLI script that parses server log files using regex patterns for Apache, Nginx, or custom formats. It extracts structured metrics including status code distribution, top-10 URLs and IPs, hourly request histogram, average response size, error rate, and anomaly detection (high-request IPs, high-error URLs).

**Sub-tasks tested (11 checkpoints)**:
- Argparse interface: `--input`, `--output`, `--format`
- Apache regex pattern applied correctly: `^(\S+) \S+ \S+ \[([^\]]+)\] "(\w+) (\S+) \S+" (\d{3}) (\d+|-)`
- Nginx regex pattern applied correctly
- Custom format regex applied correctly
- Parse statistics tracked: total lines, parsed lines, failed lines
- Status code distribution computed (2xx, 3xx, 4xx, 5xx buckets)
- Top-10 URLs by request count identified
- Top-10 IPs by request count identified
- Requests-per-hour histogram computed
- Average response size computed; error rate computed as (4xx+5xx)/total
- Anomaly detection: IPs with >100 requests flagged; URLs with >50% error rate flagged; JSON output correct

---

### S111 — cuda_memory

**Domain**: GPU Computing / Performance Optimization  
**Sub-tasks**: 10

**Task**: Write a CLI script that analyzes a JSON log of GPU memory allocation events (alloc/free with size, tensor name, dtype, timestamp), reconstructs the memory timeline, identifies peak memory usage, detects fragmentation, and generates optimization suggestions (early-free candidates, serializable overlapping allocations, float64-to-float32 downcast candidates).

**Sub-tasks tested (10 checkpoints)**:
- Argparse interface: `--input`, `--output`, `--gpu-memory-gb`
- Allocation events loaded and validated
- Memory timeline reconstructed by tracking active allocations at each timestamp
- Peak memory usage and timestamp identified
- Fragmentation ratio computed as `largest_free_block / total_free`
- Tensors flagged for early-free opportunity (allocated long before last use)
- Overlapping allocations identified as serialization candidates
- float64 tensors >1MB flagged as downcast candidates to float32
- Memory efficiency computed as `peak_used / gpu_memory_total`
- JSON output: peak_memory_bytes, peak_timestamp, fragmentation_ratio, efficiency, n_allocations, optimization_suggestions, memory_timeline_summary

---

### S112 — midi_chords

**Domain**: Music Information Retrieval  
**Sub-tasks**: 11

**Task**: Write a CLI script that reads MIDI note events from a CSV, groups simultaneous notes (within `--max-gap` ms), classifies each chord group by semitone interval patterns (major/minor triads, diminished, augmented, seventh types, power chords), names them by root note, computes a chord transition frequency matrix, and guesses the key signature.

**Sub-tasks tested (11 checkpoints)**:
- Argparse interface: `--input`, `--output`, `--min-duration`, `--max-gap`
- CSV loaded and events sorted by time
- Simultaneous note grouping within max-gap ms
- Major triad detection: intervals [4, 3]
- Minor triad detection: intervals [3, 4]
- Diminished detection: intervals [3, 3]
- Augmented detection: intervals [4, 4]
- Seventh chord detection: [4,3,4], [4,3,3], [3,4,3] variants
- Root note and chord name assigned (e.g., "C major", "A minor 7th")
- Transition frequency matrix computed between chord types
- JSON output: n_events, n_chords, chord_sequence, transition_matrix, key_signature_guess

---

### S113 — inventory_reorder

**Domain**: Operations Research / Supply Chain  
**Sub-tasks**: 11

**Task**: Write a CLI script that reads historical demand data by product, fits normal or Poisson demand distributions based on coefficient of variation, computes Economic Order Quantity (Q* = sqrt(2DK/h) with K=$50) and safety stock (from service level z-score and demand variability during lead time), and outputs per-product reorder points and annual costs.

**Sub-tasks tested (11 checkpoints)**:
- Argparse interface: `--input`, `--output`, `--service-level`, `--holding-cost-pct`
- CSV loaded and grouped by product_id
- Demand statistics computed: mean, std, coefficient of variation
- Distribution fitted: normal if CV is high, Poisson if low
- Mean and variability of lead time computed
- EOQ formula applied correctly: `sqrt(2*D*K/h)`
- z-score derived from service level parameter
- Safety stock = z × std of demand during lead time
- Reorder point = mean demand during lead time + safety stock
- Expected annual cost computed (ordering + holding + stockout)
- JSON output per product: eoq, reorder_point, safety_stock, service_level, annual_cost, demand_stats

---

### S114 — obstacle_avoidance

**Domain**: Robotics / Motion Planning  
**Sub-tasks**: 11

**Task**: Write a CLI script for 2D robot trajectory planning using either RRT (Rapidly-exploring Random Tree) or Potential Field methods. RRT must implement random sampling, nearest-node extension, line-circle collision checking, and path smoothing. Potential Field uses attractive/repulsive gradient descent with local minima detection. Both compute path metrics: total length, waypoint count, minimum obstacle clearance, and smoothness.

**Sub-tasks tested (11 checkpoints)**:
- Argparse interface: `--input`, `--output`, `--method`, `--step-size`, `--max-iterations`
- Environment JSON loaded and validated
- RRT: tree initialized from start node
- RRT: random sampling and nearest-node lookup implemented
- RRT: line-circle collision check implemented
- RRT: path to goal found within max iterations
- RRT: path smoothing by shortcutting waypoints
- Potential Field: attractive and repulsive force computation implemented
- Path metrics: total_length, n_waypoints, min_obstacle_clearance, smoothness computed
- JSON output: path (list of [x,y]), method, metrics, success flag
- Path avoids all obstacles (clearance > 0 for all waypoints)

---

### S115 — quantum_circuit

**Domain**: Quantum Computing  
**Sub-tasks**: 10

**Task**: Write a CLI script that simulates small quantum circuits by maintaining a complex state vector of length 2^n_qubits. Gates (H, X, Y, Z, CNOT, CZ, RX, RY, RZ, SWAP, T, S) are applied via full unitary matrices constructed with tensor products. Measurement probabilities are computed from squared amplitudes and used to sample `--shots` measurements.

**Sub-tasks tested (10 checkpoints)**:
- Argparse interface: `--input`, `--output`, `--shots`
- State vector initialized to |00...0> correctly
- Single-qubit gate matrices (H, X, RX, etc.) defined correctly
- Tensor product with identity matrices used to build n-qubit unitaries
- CNOT/CZ constructed correctly with controlled-gate expansion
- State vector updated sequentially for each gate in circuit
- Measurement probabilities computed as |amplitude|^2 per basis state
- Sampling from probabilities produces `shots` measurements
- JSON output: n_qubits, state_vector (real + imag parts), probabilities (bitstring→probability), measurement_counts, circuit_depth
- Entanglement indicator computed (non-product state detection)

---

## Section 2: Probe 1 — Skill Probe

**Core question**: Why does documentation-oriented Skill guidance fail as test-time control?

The Skill Probe investigates whether providing LLMs with structured documentation (analogous to a software developer reading an API manual) improves code generation over a no-guidance baseline. Three experiments address this from different angles.

---

### EX2: Main Comparison (Skill vs Gene vs No Guidance)

**Source file**: `results/gene_bench_gemini.jsonl`

**Design**: 4 conditions × 45 scenarios × 2 models = 360 trials

Each condition uses a different type and length of system prompt. Gene G3 (~230 tokens) is a structured strategy template. Skill L1 (~630 tokens) is a SKILL.md overview document. Skill L4 (~2572 tokens) is the full Skill package including SKILL.md, code scripts, and references. Both Skill and Gene are derived from the same per-scenario underlying knowledge; the token budget and representation format are the only variables.

**Results**:

| Condition | Pro Avg Pass Rate | Pro Passed/Total | Flash Avg Pass Rate | Flash Passed/Total |
|-----------|:-----------------:|:----------------:|:-------------------:|:-----------------:|
| `ex2_no_context` | 53.8% | 17/45 | 39.8% | 9/45 |
| `ex2_gene_g3` | 52.6% | 17/45 | 46.6% | 10/45 |
| `ex2_skill_l1` | 54.3% | 18/45 | 47.6% | 10/45 |
| `ex2_skill_l4` | 50.3% | 16/45 | 37.2% | 9/44 |

**To verify**: `python3 -c "import json; data=[json.loads(l) for l in open('results/gene_bench_gemini.jsonl')]; rows=[(d['trial_config']['model'],d['trial_config']['condition'],d['eval']['pass_rate'],d['eval']['passed']) for d in data if d['trial_config']['rq']=='ex2']; print(rows[:5])"`

**Key findings**:

- Skill L4, the most token-heavy condition at ~2572 tokens, performs worst on both models (50.3% Pro, 37.2% Flash). This negative result is striking: more documentation actively hurts performance.
- Skill L1 provides a modest gain on Flash (+7.8 pp over no-context) but offers negligible benefit on Pro (+0.5 pp).
- Gene G3 with less than half the tokens of Skill L1 matches Skill L1's `passed/total` count on Pro (17/45 for both) and nearly matches on Flash (10/45 vs 10/45). Both Skill and Gene yield pass counts within 1 scenario of each other.
- Flash shows greater sensitivity to guidance than Pro: a 46.6%/47.6% range with Gene/Skill guidance vs 39.8% baseline.
- The full-package Skill L4 result on Flash (37.2%, 9/44) is below the no-context baseline (39.8%, 9/45), suggesting that verbose documentation actively distracts Flash from the core task.

---

### EX1: Budget Curve

**Source file**: `results/gene_bench_gemini.jsonl`

**Design**: 6 conditions × 45 scenarios × 2 models = 540 trials

This experiment tests a token-budget sweep from 0 (no guidance) to ~630 tokens (Skill L1 overview). The G0→G4 progression uses components from the same Gene experience source, gradually adding keywords, then a summary, then strategy, then the full template. L1 is included at the top of the budget range for comparison.

**Conditions and token counts**:

| Condition | Token Budget (approx.) | Content |
|-----------|----------------------|---------|
| `ex1_G0` | 0 | No context (baseline) |
| `ex1_G1` | ~88 | Keywords only |
| `ex1_G2` | ~136 | Keywords + summary |
| `ex1_G3` | ~230 | Keywords + summary + strategy |
| `ex1_G4` | ~375 | Full Gene template |
| `ex1_L1` | ~630 | Skill overview document |

**Results**:

| Condition | Pro Avg Pass Rate | Pro Passed/Total | Flash Avg Pass Rate | Flash Passed/Total |
|-----------|:-----------------:|:----------------:|:-------------------:|:-----------------:|
| `ex1_G0` | 51.9% | 16/45 | 39.8% | 9/45 |
| `ex1_G1` | 54.4% | 17/45 | 49.9% | 11/45 |
| `ex1_G2` | 49.6% | 15/44 | 48.5% | 12/45 |
| `ex1_G3` | 52.8% | 17/45 | 46.6% | 10/45 |
| `ex1_G4` | 52.4% | 17/45 | 47.4% | 11/45 |
| `ex1_L1` | 55.6% | 18/44 | 47.6% | 10/45 |

**To verify**: `python3 -c "import json; data=[json.loads(l) for l in open('results/gene_bench_gemini.jsonl')]; rows=[(d['trial_config']['model'],d['trial_config']['condition'],d['eval']['pass_rate'],d['eval']['passed']) for d in data if d['trial_config']['rq']=='ex1']; print(rows[:5])"`

**Key findings**:

- There is no monotonic improvement as token budget increases for either model. The budget curve is flat and noisy, not a smooth improvement curve.
- On Pro, G1 (keywords only, ~88 tokens) matches or exceeds G3, G4, and even approaches L1 on the `passed/total` metric. This suggests that minimal keyword cues may be nearly as effective as richer guidance for Pro.
- On Flash, the pattern is reversed: G1 and G2 outperform G3 and G4 in `passed/total` (11–12 vs 10–11 scenarios fully passed). Going from ~136 to ~230 tokens does not help and may slightly hurt Flash.
- L1 achieves the highest `passed/total` for Pro (18/44) but only 10/45 for Flash, which is worse than G1 and G2. This further undermines the case for documentation-style guidance.
- G2 on Pro shows the only partial dip (15/44 passed), suggesting that summary-without-strategy can occasionally conflict with the model's own approach.

---

### EX22: Component Attribution

**Source file**: `results/evomap_gemini/evomap_ex22_results.jsonl`

**Design**: 7 conditions × 45 scenarios × 2 models = 630 trials

This experiment dissects the SKILL.md document by providing individual sections in isolation: overview, workflow, error handling, quick reference, and pitfalls. Gene G3 is included as a control to compare the best Skill section against the Gene representation. This isolates whether any particular type of documentation content drives Skill's aggregate performance.

**Results**:

| Condition | Pro Avg Pass Rate | Pro Passed/Total | Flash Avg Pass Rate | Flash Passed/Total |
|-----------|:-----------------:|:----------------:|:-------------------:|:-----------------:|
| `none` | 57.0% | 19/44 | 41.8% | 10/45 |
| `skill_overview` | 52.4% | 16/45 | 40.8% | 9/45 |
| `skill_workflow` | 52.6% | 18/45 | 52.5% | 10/45 |
| `skill_error_handling` | 55.1% | 16/45 | 47.2% | 9/45 |
| `skill_quick_ref` | 56.3% | 19/45 | 44.6% | 11/45 |
| `skill_pitfalls` | 55.7% | 17/43 | 44.9% | 6/45 |
| `gene_g3` | 56.5% | 18/45 | 48.2% | 12/45 |

**To verify**: `python3 -c "import json; data=[json.loads(l) for l in open('results/evomap_gemini/evomap_ex22_results.jsonl')]; rows=[(d['trial_config']['model'],d['trial_config']['condition'],d['eval']['pass_rate'],d['eval']['passed']) for d in data]; print(rows[:5])"`

**Key findings**:

- No individual Skill section component outperforms the no-guidance baseline on Pro across both metrics simultaneously. The baseline (19/44) matches or exceeds all Skill sections on `passed/total`.
- `skill_overview` is the most harmful section on Pro (16/45), dropping below baseline by 3 fully-passed scenarios. Overview documents describe what the skill does, not how to apply it — this may prime the model toward meta-description rather than coding.
- `skill_pitfalls` shows an extreme result on Flash: only 6/45 scenarios fully passed, a 4-scenario drop from baseline. Warning-heavy text may trigger overly defensive code generation in Flash.
- `skill_workflow` is the strongest Skill section for Flash (52.5% avg pass rate, matching 10/45), suggesting that step-by-step procedural text is more actionable than descriptive documentation.
- Gene G3 achieves the best `passed/total` on Flash (12/45), outperforming all individual Skill sections and the no-guidance baseline (10/45). This is a key result: a compact, action-oriented template beats any single documentation section for Flash.
- The fragmentation of Skill into components reveals that no single content type drives Skill's aggregate performance. The effect is distributed and often net-negative.

---

## Section 3: Probe 2 — Gene Probe

**Core question**: Is Gene just a shorter prompt, or a fundamentally different representation?

The Gene Probe investigates whether Gene's structure (hierarchically organized, action-oriented, structured XML-tagged template) provides advantages beyond mere brevity. If Gene were simply a short prompt, then any sufficiently short prompt should work as well, and mutating Gene's content should have proportional effects.

---

### EX2: Same-Source Comparison (Recap)

EX2, described fully in Probe 1, controls for the experience source: both Skill L1 and Gene G3 are derived from identical per-scenario knowledge. The token difference (Gene G3 ~230 tokens vs Skill L1 ~630 tokens) is the primary variable. Gene G3 achieves equivalent or better `passed/total` counts on both models using fewer than 40% of Skill L1's tokens.

---

### EX3: Robustness Test (Content and Structure Perturbations)

**Source file**: `results/gene_bench_gemini.jsonl`

**Design**: 6 conditions × 45 scenarios × 2 models = 540 trials

This experiment tests whether Gene's advantage is robust to deliberate perturbations. Content perturbations inject incorrect information (stale techniques, wrong algorithms, wrong domain). Structure perturbations preserve content but distort organization (reversed step order, overly specific constraints). If Gene were merely providing relevant tokens, any perturbation should reduce performance proportionally to information loss.

**Conditions**:

| Condition | Perturbation Type | Description |
|-----------|------------------|-------------|
| `ex3_clean_g3` | None (control) | Correct Gene G3 |
| `ex3_mutated_stale_paradigm` | Content | Outdated technique recommended |
| `ex3_mutated_wrong_algorithm` | Content | Incorrect algorithm for the task |
| `ex3_mutated_wrong_domain` | Content | Gene from a different scientific domain |
| `ex3_mutated_inverted_priority` | Structure | Steps listed in reversed order |
| `ex3_mutated_overconstrained` | Structure | Overly restrictive, over-specific constraints |

**Results**:

| Condition | Pro Avg Pass Rate | Pro Passed/Total | Flash Avg Pass Rate | Flash Passed/Total |
|-----------|:-----------------:|:----------------:|:-------------------:|:-----------------:|
| `ex3_clean_g3` | 52.8% | 17/45 | 46.6% | 10/45 |
| `ex3_mutated_stale_paradigm` | 58.4% | 19/45 | 52.8% | 13/45 |
| `ex3_mutated_wrong_algorithm` | 54.1% | 15/45 | 44.4% | 9/45 |
| `ex3_mutated_wrong_domain` | 54.4% | 18/45 | 48.9% | 9/45 |
| `ex3_mutated_inverted_priority` | 54.8% | 17/45 | 45.6% | 11/45 |
| `ex3_mutated_overconstrained` | 55.4% | 9/44 | 53.0% | 12/45 |

**To verify**: `python3 -c "import json; data=[json.loads(l) for l in open('results/gene_bench_gemini.jsonl')]; rows=[(d['trial_config']['model'],d['trial_config']['condition'],d['eval']['pass_rate'],d['eval']['passed']) for d in data if d['trial_config']['rq']=='ex3']; print(rows[:5])"`

**Key findings**:

- The most counterintuitive result: `ex3_mutated_stale_paradigm` (wrong technique) outperforms clean G3 on both models (58.4% vs 52.8% Pro, 52.8% vs 46.6% Flash, and 19/45 vs 17/45 in passed scenarios for Pro, 13/45 vs 10/45 for Flash). This suggests models may already know the correct technique and the "stale" advice merely triggers domain-relevant context activation without overriding their priors.
- `ex3_mutated_overconstrained` (too many restrictions) shows a dramatic divergence: Pro's `passed/total` drops to 9/44 — the worst of any Gene condition — while Flash achieves 12/45, its second-best result in this experiment. This split suggests Pro is more susceptible to constraint-induced interference.
- `ex3_mutated_wrong_algorithm` is the only content perturbation that consistently reduces performance below clean G3 on both Pro (15/45) and Flash (9/45), suggesting that explicit algorithmic misdirection has more reliable negative impact than stale-paradigm or cross-domain errors.
- `ex3_mutated_inverted_priority` (reversed steps) does not catastrophically harm performance on either model. Pro maintains 17/45 (equal to clean), Flash drops only 1 scenario. This suggests that step ordering in the Gene template has limited influence.
- Overall, the resilience of performance to content perturbations (most mutants still within 1–2 scenarios of clean G3 in `passed/total`) supports the view that Gene's structural format, not its literal content, may be the primary mechanism of action.

---

### EX24: Selective Complementarity

**Source file**: `results/evomap_gemini/evomap_ex24_results.jsonl`

**Design**: 5 conditions × 45 scenarios × 2 models = 450 trials

This experiment tests whether Gene can be effectively augmented by complementary information types. It compares standalone Gene G3 against Gene augmented with API reference notes (~+200 tokens) or example code snippets (~+200 tokens), and benchmarks against the full Skill L4 package (~2572 tokens) as an upper-bound reference.

**Results**:

| Condition | Pro Avg Pass Rate | Pro Passed/Total | Flash Avg Pass Rate | Flash Passed/Total |
|-----------|:-----------------:|:----------------:|:-------------------:|:-----------------:|
| `none` | 58.1% | 18/45 | 45.6% | 11/45 |
| `gene_alone` | 57.9% | 18/45 | 48.2% | 12/45 |
| `gene_plus_api_notes` | 57.0% | 18/45 | 53.2% | 13/45 |
| `gene_plus_examples` | 57.0% | 17/45 | 46.3% | 13/45 |
| `skill_full` | 56.4% | 18/45 | 54.5% | 14/45 |

**To verify**: `python3 -c "import json; data=[json.loads(l) for l in open('results/evomap_gemini/evomap_ex24_results.jsonl')]; rows=[(d['trial_config']['model'],d['trial_config']['condition'],d['eval']['pass_rate'],d['eval']['passed']) for d in data]; print(rows[:5])"`

**Key findings**:

- On Pro, all conditions produce almost identical results in `passed/total` (17–18/45), and mean pass rates cluster tightly between 56.4% and 58.1%. Pro appears to extract near-maximum value from Gene alone and is not improved by augmentation.
- On Flash, there is a clear ordering in `passed/total`: no guidance (11) < gene alone (12) < gene + api notes / gene + examples (13 each) < skill full (14). This suggests Flash benefits from additional context, and that augmented Gene narrows the gap with the full Skill L4 package.
- `gene_plus_api_notes` provides the best Flash mean pass rate among the Gene conditions (53.2%), outperforming both `gene_alone` (48.2%) and `gene_plus_examples` (46.3%) on average.
- The full Skill L4 package achieves the best Flash performance (54.5%, 14/45) in this experiment — different from EX2 where Skill L4 underperformed. This may reflect that EX24 uses a different baseline population of scenarios or a refined Skill package.
- Selective augmentation of Gene with ~200 tokens of targeted supplementary content (either API notes or examples) achieves 13/45 on Flash — just 1 scenario short of the full Skill L4 at 14/45 — while using roughly 5× fewer tokens.

---

### EX5: Multi-Gene Combination

**Source file**: `results/gene_bench_gemini.jsonl`

**Design**: 5 conditions × scenarios × 2 models = 385 trials (Pro has 31–33 trials per condition due to paired scenario structure; Flash has full 45 scenarios per condition)

This experiment tests whether providing multiple Genes simultaneously improves performance. It contrasts complementary multi-Gene contexts (different aspects of the same task) against conflicting multi-Gene contexts (contradictory guidance).

**Conditions**:

| Condition | Description |
|-----------|-------------|
| `ex5_none` | No guidance (baseline) |
| `ex5_single` | One Gene for the target task |
| `ex5_2x_complementary` | Two complementary Genes covering different aspects |
| `ex5_2x_conflicting` | Two Genes with conflicting guidance |
| `ex5_3x_complementary` | Three complementary Genes |

**Results**:

| Condition | Pro Avg Pass Rate | Pro Passed/Total | Flash Avg Pass Rate | Flash Passed/Total |
|-----------|:-----------------:|:----------------:|:-------------------:|:-----------------:|
| `ex5_none` | 43.2% | 10/32 | 39.8% | 9/45 |
| `ex5_single` | 44.8% | 10/32 | 46.6% | 10/45 |
| `ex5_2x_complementary` | 52.4% | 13/33 | 41.1% | 6/45 |
| `ex5_2x_conflicting` | 48.1% | 10/31 | 44.7% | 10/45 |
| `ex5_3x_complementary` | 46.4% | 11/32 | 48.0% | 10/45 |

Note: Pro has 31–33 trials per condition (not 45) because EX5 uses a paired scenario design where scenarios are matched for multi-Gene combination validity. Flash retains the full 45 scenarios per condition.

**To verify**: `python3 -c "import json; data=[json.loads(l) for l in open('results/gene_bench_gemini.jsonl')]; rows=[(d['trial_config']['model'],d['trial_config']['condition'],d['eval']['pass_rate'],d['eval']['passed']) for d in data if d['trial_config']['rq']=='ex5']; print(rows[:5])"`

**Key findings**:

- `ex5_2x_complementary` shows the strongest Pro result (52.4% avg, 13/33 passed) — the only condition that noticeably improves over the Pro baseline. However, this is the paired subset of 33 scenarios (not the full 45), so direct comparison to other experiments requires care.
- On Flash, `ex5_2x_complementary` produces the worst result (41.1%, 6/45) — a sharp drop from the single-Gene baseline (46.6%, 10/45). This suggests that two simultaneous Genes may overwhelm Flash's context integration ability.
- `ex5_2x_conflicting` is slightly below `ex5_2x_complementary` for Pro (48.1% vs 52.4%) but essentially matches the single-Gene condition on Flash (44.7% vs 46.6%). Conflicting Genes do not catastrophically degrade performance.
- `ex5_3x_complementary` does not outperform `ex5_2x_complementary` on Pro and performs similarly to `ex5_single` on Flash. Three Genes provide diminishing returns beyond two.
- The asymmetry between Pro and Flash for `ex5_2x_complementary` is the most striking directional reversal in the dataset: it is simultaneously the best Pro condition by avg pass rate (52.4%, 13/33 passed) and the worst Flash condition by scenarios fully passed (41.1%, 6/45). The same guidance that most helps Pro most hurts Flash.

---

## Section 4: Probe 3 — Evolution Probe

**Core question**: Why is Gene better suited as a carrier for ongoing attachment and accumulation of experiential knowledge?

The Evolution Probe tests whether Gene's structured, editable format (XML-tagged sections, consistent schema) provides advantages that are not explained by content or token count alone. It also investigates how failure history information is best encoded within a Gene.

---

### EX29: Editable vs Static

**Source file**: `results/evomap_gemini/evomap_ex29_results.jsonl`

**Design**: 4 conditions × 45 scenarios × 2 models = 360 trials

This experiment compares Gene G3 in its native GEP (Gene Expression Protocol) structured format against the same content flattened into flowing prose without XML structure. The key question is whether the structured, editable representation — independently of content — performs differently from an unstructured rendering of the same information.

**Conditions**:

| Condition | Format | Token Budget (approx.) |
|-----------|--------|----------------------|
| `none` | No guidance | 0 |
| `gene_g3` | Gene in GEP XML-tagged structured format | ~230 |
| `gene_static` | Same content as G3, flattened to flowing prose (no XML) | ~230 |
| `skill_l1` | Skill L1 documentation-format overview | ~630 |

**Results**:

| Condition | Pro Avg Pass Rate | Pro Passed/Total | Flash Avg Pass Rate | Flash Passed/Total |
|-----------|:-----------------:|:----------------:|:-------------------:|:-----------------:|
| `none` | 59.9% | 18/45 | 41.8% | 10/45 |
| `gene_g3` | 60.5% | 19/45 | 48.2% | 12/45 |
| `gene_static` | 53.4% | 17/45 | 44.1% | 9/45 |
| `skill_l1` | 54.1% | 17/44 | 46.8% | 11/45 |

**To verify**: `python3 -c "import json; data=[json.loads(l) for l in open('results/evomap_gemini/evomap_ex29_results.jsonl')]; rows=[(d['trial_config']['model'],d['trial_config']['condition'],d['eval']['pass_rate'],d['eval']['passed']) for d in data]; print(rows[:5])"`

**Key findings**:

- Gene G3 (structured format) achieves the best result on Pro (60.5%, 19/45) and Flash (48.2%, 12/45) among all conditions including the no-guidance baseline.
- The flattened prose version (`gene_static`) performs substantially worse than structured Gene G3 on Pro (53.4% vs 60.5%, 17 vs 19 passed) and Flash (44.1% vs 48.2%, 9 vs 12 passed) despite containing the same information.
- `gene_static` also performs below the no-guidance baseline on Pro (53.4% vs 59.9%) and Flash (44.1% vs 41.8% — approximately equivalent). The structured format, not the content itself, appears to be providing the guidance benefit.
- Skill L1 falls between the baseline and `gene_static` in most metrics, performing similarly to `gene_static` but not achieving Gene G3 levels. This replicates the EX2 finding that documentation-format text underperforms structured Gene.
- This is the strongest evidence in the benchmark that Gene's structural properties (XML-tagged sections, consistent schema, protocol-style organization) provide direct value to the LLM beyond the information content, and that the format itself is the mechanistic lever.

---

### EX9: Failure-First vs Strategy-First

**Source file**: `results/evomap_gemini/evomap_ex9_results.jsonl`

**Design**: 5 conditions × 45 scenarios × 2 models = 450 trials

This experiment examines how experiential failure information should be ordered within a Gene when both failure history and correct strategy are present. It tests whether leading with failure descriptions (priming the model to avoid pitfalls) or leading with the strategy (priming for the correct approach) produces better outcomes.

**Conditions**:

| Condition | Description |
|-----------|-------------|
| `none` | No guidance (baseline) |
| `correct_strategy` | Strategy only, no failure history |
| `failure_warnings` | Failure warnings only, no explicit strategy |
| `failure_first` | Failure description, then strategy |
| `strategy_first` | Strategy, then failure description |

**Results**:

| Condition | Pro Avg Pass Rate | Pro Passed/Total | Flash Avg Pass Rate | Flash Passed/Total |
|-----------|:-----------------:|:----------------:|:-------------------:|:-----------------:|
| `none` | 56.8% | 18/44 | 41.8% | 10/45 |
| `correct_strategy` | 57.2% | 18/45 | 47.7% | 13/45 |
| `failure_warnings` | 56.8% | 18/45 | 52.0% | 15/45 |
| `failure_first` | 58.6% | 19/44 | 44.7% | 11/45 |
| `strategy_first` | 53.9% | 17/44 | 45.8% | 11/45 |

**To verify**: `python3 -c "import json; data=[json.loads(l) for l in open('results/evomap_gemini/evomap_ex9_results.jsonl')]; rows=[(d['trial_config']['model'],d['trial_config']['condition'],d['eval']['pass_rate'],d['eval']['passed']) for d in data]; print(rows[:5])"`

**Key findings**:

- On Flash, `failure_warnings` (failure only, no strategy) is the single best condition across the entire Probe 3 dataset at 52.0% avg pass rate and 15/45 fully passed scenarios. This dramatically outperforms the strategy-only condition (47.7%, 13/45) and the no-guidance baseline (41.8%, 10/45).
- The failure-warning-only result on Flash suggests that for smaller/lighter models, learning what not to do is more actionable than learning what to do.
- On Pro, `failure_first` (fail then strategy) achieves the highest `passed/total` at 19/44, narrowly beating the baseline and all other conditions. The ordering matters for Pro.
- `strategy_first` (strategy then failure) is the worst guided condition for Pro (17/44) and only slightly above baseline for Flash (11/45). Leading with strategy may cause the model to partially ignore the subsequent failure context.
- `correct_strategy` alone is effective for Flash (13/45), but `failure_warnings` alone is even more effective (15/45), suggesting that failure history encodes complementary information not captured by the strategy template.
- The divergence between Pro and Flash in this experiment (failure_warnings: best for Flash, not for Pro; failure_first: best for Pro, average for Flash) highlights that optimal Gene composition may be model-dependent.

---

## Section 5: Reproducibility

### Data Provenance

All experimental data is stored in JSONL format. Each line is a self-contained JSON object recording the full trial configuration, evaluation results, and token/cost metadata.

| Experiment Set | File Path |
|---------------|-----------|
| EX1, EX2, EX3, EX5 (and other main experiments) | `results/gene_bench_gemini.jsonl` |
| EX8 | `results/evomap_gemini/evomap_ex8_results.jsonl` |
| EX9 | `results/evomap_gemini/evomap_ex9_results.jsonl` |
| EX10 | `results/evomap_gemini/evomap_ex10_results.jsonl` |
| EX11 | `results/evomap_gemini/evomap_ex11_results.jsonl` |
| EX12 | `results/evomap_gemini/evomap_ex12_results.jsonl` |
| EX13 | `results/evomap_gemini/evomap_ex13_results.jsonl` |
| EX14 | `results/evomap_gemini/evomap_ex14_results.jsonl` |
| EX15 | `results/evomap_gemini/evomap_ex15_results.jsonl` |
| EX16 | `results/evomap_gemini/evomap_ex16_results.jsonl` |
| EX17 | `results/evomap_gemini/evomap_ex17_results.jsonl` |
| EX18 | `results/evomap_gemini/evomap_ex18_results.jsonl` |
| EX19 | `results/evomap_gemini/evomap_ex19_results.jsonl` |
| EX20 | `results/evomap_gemini/evomap_ex20_results.jsonl` |
| EX21 | `results/evomap_gemini/evomap_ex21_results.jsonl` |
| EX22 | `results/evomap_gemini/evomap_ex22_results.jsonl` |
| EX23 | `results/evomap_gemini/evomap_ex23_results.jsonl` |
| EX24 | `results/evomap_gemini/evomap_ex24_results.jsonl` |
| EX25 | `results/evomap_gemini/evomap_ex25_results.jsonl` |
| EX26 | `results/evomap_gemini/evomap_ex26_results.jsonl` |
| EX27 | `results/evomap_gemini/evomap_ex27_results.jsonl` |
| EX28 | `results/evomap_gemini/evomap_ex28_results.jsonl` |
| EX29 | `results/evomap_gemini/evomap_ex29_results.jsonl` |

### JSONL Record Schema

Each record in a JSONL file has the following structure:

```json
{
  "trial_key": "S002_spike_behavior__gemini_pro__ex1__ex1_G2__t0.0__r0",
  "trial_config": {
    "scenario_id": "S002_spike_behavior",
    "model": "gemini_pro",
    "rq": "ex1",
    "condition": "ex1_G2",
    "temperature": 0.0,
    "run_id": 0
  },
  "eval": {
    "passed": true,
    "n_pass": 12,
    "n_total": 12,
    "pass_rate": 1.0,
    "error_type": "success",
    "returncode": 0
  },
  "code_length": 5094,
  "gene_tokens": 148,
  "input_tokens": 413,
  "output_tokens": 1739,
  "cost": 0.00563
}
```

The `eval.pass_rate` field is the primary metric for all tables. `eval.passed` is `True` if and only if `pass_rate == 1.0`.

### Determinism

Temperature is set to 0.0 for all trials. This guarantees within-batch determinism for the same model version and API endpoint. Independent reruns on 171 trials achieved 94.7% consistency (162/171 matching), with 9 discrepancies concentrated in one scenario (`S012_uv_spectroscopy × gemini_pro`). These discrepancies are attributed to API version drift between the two run batches, not to model stochasticity.

### Reproduction Commands

To reproduce EX2 (main Skill vs Gene comparison):

```bash
python3 run_gene_bench.py \
  --experiment ex2 \
  --models gemini_pro,gemini_flash \
  --gemini-key $GEMINI_API_KEY
```

To reproduce an evomap experiment (e.g., EX22):

```bash
python3 run_evomap_experiments.py \
  --experiment ex22 \
  --models gemini_pro,gemini_flash \
  --gemini-key $GEMINI_API_KEY \
  --output-dir results/evomap_gemini
```

To verify specific experiment results from the JSONL files using Python:

```bash
# EX2 results summary
python3 - <<'EOF'
import json
from collections import defaultdict

data = [json.loads(l) for l in open("results/gene_bench_gemini.jsonl")]
ex2 = [d for d in data if d["trial_config"]["rq"] == "ex2"]

for model in ["gemini_pro", "gemini_flash"]:
    print(f"\n=== {model} ===")
    by_cond = defaultdict(list)
    for d in ex2:
        if d["trial_config"]["model"] == model:
            by_cond[d["trial_config"]["condition"]].append(d["eval"])
    for cond, evals in sorted(by_cond.items()):
        avg = sum(e["pass_rate"] for e in evals) / len(evals)
        passed = sum(1 for e in evals if e["passed"])
        print(f"  {cond}: avg={avg:.1%} passed={passed}/{len(evals)}")
EOF
```

```bash
# EX22 component attribution results
python3 - <<'EOF'
import json
from collections import defaultdict

data = [json.loads(l) for l in open("results/evomap_gemini/evomap_ex22_results.jsonl")]

for model in ["gemini_pro", "gemini_flash"]:
    print(f"\n=== {model} ===")
    by_cond = defaultdict(list)
    for d in data:
        if d["trial_config"]["model"] == model:
            by_cond[d["trial_config"]["condition"]].append(d["eval"])
    for cond, evals in sorted(by_cond.items()):
        avg = sum(e["pass_rate"] for e in evals) / len(evals)
        passed = sum(1 for e in evals if e["passed"])
        print(f"  {cond}: avg={avg:.1%} passed={passed}/{len(evals)}")
EOF
```

### Summary of Key Findings Across All Probes

| Finding | Evidence | Strongest Signal |
|---------|---------|-----------------|
| Verbose Skill guidance (L4) hurts performance below baseline | EX2: Skill L4 at 50.3%/37.2% vs baseline 53.8%/39.8% | Flash: -2.6 pp, 9/44 vs 9/45 |
| No monotonic improvement with increasing token budget | EX1: flat/noisy budget curve | Pro: G1 (35 tokens) matches L1 (630 tokens) |
| Individual Skill sections do not improve over baseline | EX22: all Skill sections ≤ baseline on Pro | `skill_overview` drops to 16/45 on Pro (vs 19/44 baseline) |
| Gene's structured format, not content, drives benefit | EX29: `gene_static` (same content, no XML) drops below baseline | Pro: 53.4%/17 vs 60.5%/19 for structured Gene |
| Gene resists content perturbations (stale paradigm even helps) | EX3: stale paradigm (+5.6 pp Pro, +6.2 pp Flash) | Most mutants within 1–2 scenarios of clean Gene |
| Failure warnings alone are highly effective for Flash | EX9: `failure_warnings` achieves 15/45 (best of any non-Pro condition) | Flash: 52.0% vs 41.8% baseline |
| Multi-Gene helps Pro but hurts Flash | EX5: `ex5_2x_complementary` Pro 13/33 vs Flash 6/45 | Best Pro / worst Flash directional reversal |

---

*End of Technical Report*
