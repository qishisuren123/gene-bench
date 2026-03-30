#!/usr/bin/env python3
"""
为 15 个新场景（S101-S115）手动创建 Gene JSON。
这些场景没有 SKILL.md，需要直接编写 Gene。
"""

import json
from pathlib import Path

GENES_DIR = Path(__file__).parent / "genes"

NEW_GENES = {
    "S101_climate_attribution": {
        "scenario_id": "S101_climate_attribution",
        "domain": "climate_science",
        "keywords": ["attribution", "forcing", "regression", "ridge", "bayesian", "temperature anomaly", "GHG", "r-squared"],
        "summary": "Perform climate change attribution by regressing observed temperature anomalies against individual forcing factors to determine each factor's contribution percentage.",
        "strategy": [
            "Set up the regression with forcing factors as predictors and observed temperature as response, choosing OLS/Ridge/Bayesian based on method parameter",
            "Compute attribution fractions by normalizing each coefficient's contribution to total explained warming",
            "Calculate R² for goodness-of-fit and residual fraction for unexplained variability"
        ],
        "pitfalls": [
            "Multicollinearity: forcing factors may be correlated, causing unstable OLS coefficients — Ridge regularization helps",
            "Attribution fractions should be computed from absolute coefficient contributions, not raw coefficients"
        ],
        "key_concepts": [
            "Two-stage attribution: first fit regression, then decompose predicted values by forcing factor",
            "Bayesian approach uses prior precision to regularize, producing posterior mean as estimate"
        ]
    },
    "S102_protein_secondary": {
        "scenario_id": "S102_protein_secondary",
        "domain": "bioinformatics",
        "keywords": ["Chou-Fasman", "GOR", "helix", "sheet", "coil", "propensity", "sliding window", "FASTA"],
        "summary": "Predict protein secondary structure (H/E/C) from amino acid sequence using residue propensity tables and sliding window nucleation.",
        "strategy": [
            "Build propensity lookup tables for helix and sheet from known values, then scan with sliding windows for nucleation sites",
            "Extend nucleation regions along the sequence while average propensity exceeds threshold",
            "Assign remaining unassigned residues as coil (C) and compute per-sequence composition statistics"
        ],
        "pitfalls": [
            "Window size matters: helix nucleation uses 6-residue windows, sheet uses 5-residue windows",
            "Handle sequence edges where window extends beyond bounds by padding or truncating"
        ],
        "key_concepts": [
            "Propensity values > 1.0 indicate preference for that structure type",
            "Nucleation-extension model: find seed regions first, then grow them"
        ]
    },
    "S103_instrumental_variable": {
        "scenario_id": "S103_instrumental_variable",
        "domain": "causal_inference",
        "keywords": ["2SLS", "instrumental variable", "endogeneity", "first stage", "F-statistic", "causal effect", "OLS bias"],
        "summary": "Estimate causal effects using two-stage least squares (2SLS) to overcome endogeneity bias in observational data.",
        "strategy": [
            "Stage 1: Regress treatment on instrument(s) and confounders to get predicted treatment values (X_hat)",
            "Stage 2: Regress outcome on X_hat (and confounders) to get the IV estimate of causal effect",
            "Compute first-stage F-statistic to test instrument relevance — F < 10 indicates weak instruments"
        ],
        "pitfalls": [
            "Standard errors in Stage 2 must use original X, not X_hat, for correct inference",
            "Weak instrument bias: when F < 10, IV estimate can be more biased than OLS"
        ],
        "key_concepts": [
            "IV solves endogeneity by using variation in X that comes only through Z (the instrument)",
            "Compare IV and OLS: if IV differs substantially, endogeneity was present"
        ]
    },
    "S104_multisensor_anomaly": {
        "scenario_id": "S104_multisensor_anomaly",
        "domain": "anomaly_detection",
        "keywords": ["z-score", "rolling window", "Mahalanobis", "cross-sensor", "point anomaly", "collective anomaly", "ensemble"],
        "summary": "Detect anomalies in multi-sensor time series using ensemble of rolling z-score, cross-sensor correlation, and Mahalanobis distance methods.",
        "strategy": [
            "Compute per-sensor rolling z-scores and flag individual sensor anomalies exceeding the threshold",
            "Cross-validate: timestamps where >50% sensors are anomalous simultaneously indicate system-level events",
            "Use Mahalanobis distance across all sensors for multivariate anomaly detection that accounts for sensor correlations"
        ],
        "pitfalls": [
            "Rolling window must be large enough to estimate stable statistics but small enough to detect regime changes",
            "Mahalanobis distance requires invertible covariance matrix — handle near-singular cases with regularization"
        ],
        "key_concepts": [
            "Classify anomaly types: point (single spike), collective (sustained), contextual (cross-sensor disagreement)",
            "Ensemble approach reduces false positives by requiring agreement across detection methods"
        ]
    },
    "S105_community_detection": {
        "scenario_id": "S105_community_detection",
        "domain": "graph_analysis",
        "keywords": ["label propagation", "modularity", "Louvain", "community", "overlapping", "adjacency", "density"],
        "summary": "Detect overlapping communities in networks using label propagation or greedy modularity optimization without external graph libraries.",
        "strategy": [
            "Build adjacency list representation from edge list, then initialize each node with a unique community label",
            "Iteratively update labels: each node adopts the most frequent label among its neighbors with random tie-breaking",
            "Compute modularity Q to evaluate partition quality: Q = (1/2m) * sum[(A_ij - k_i*k_j/2m) * delta(c_i, c_j)]"
        ],
        "pitfalls": [
            "Label propagation can oscillate — use asynchronous updates (random node order each iteration) and convergence check",
            "For overlapping communities, allow nodes to belong to multiple communities if >30% of neighbors share that label"
        ],
        "key_concepts": [
            "Modularity measures how much better the partition is compared to random graph with same degree sequence",
            "Per-community density = 2 * internal_edges / (size * (size-1)) for undirected graphs"
        ]
    },
    "S106_seismic_denoise": {
        "scenario_id": "S106_seismic_denoise",
        "domain": "seismology",
        "keywords": ["bandpass filter", "Butterworth", "STA/LTA", "P-wave", "SNR", "seismic", "trigger detection"],
        "summary": "Denoise seismic waveforms using Butterworth bandpass filtering and detect P-wave arrivals using STA/LTA ratio triggering.",
        "strategy": [
            "Design 4th-order Butterworth bandpass filter between lowcut and highcut frequencies, apply to each velocity component",
            "Compute STA/LTA ratio: short-term average amplitude / long-term average amplitude in sliding windows",
            "Trigger P-wave detection where STA/LTA exceeds 3.0, compute SNR improvement as ratio of signal power before/after filtering"
        ],
        "pitfalls": [
            "Sampling rate must be correctly determined from time column spacing for proper filter frequency normalization",
            "STA and LTA windows must not overlap with signal onset for accurate trigger timing"
        ],
        "key_concepts": [
            "Butterworth filter provides maximally flat frequency response in the passband",
            "STA/LTA is the standard seismic trigger: STA captures signal onset, LTA captures background noise level"
        ]
    },
    "S107_regime_switch": {
        "scenario_id": "S107_regime_switch",
        "domain": "finance",
        "keywords": ["regime", "structural break", "volatility", "log return", "rolling statistics", "transition matrix", "Sharpe ratio"],
        "summary": "Detect volatility regime switches in financial time series using rolling statistics and classify into low-vol, high-vol, and crisis regimes.",
        "strategy": [
            "Compute log returns from price series, then calculate rolling mean and volatility with specified window size",
            "Detect change points where rolling volatility changes by >2x between adjacent non-overlapping windows",
            "Classify each regime by comparing its volatility to the median: low_vol, high_vol, or crisis (>2x median)"
        ],
        "pitfalls": [
            "Log returns: use log(P_t/P_{t-1}), not simple returns, for better statistical properties",
            "Rolling window at series boundaries produces NaN — handle by starting regime detection after full window is available"
        ],
        "key_concepts": [
            "Annualized Sharpe ratio = (mean_daily_return * 252) / (daily_vol * sqrt(252))",
            "Transition matrix: P(regime_j | current_regime_i) estimated from observed transitions"
        ]
    },
    "S108_raman_spectroscopy": {
        "scenario_id": "S108_raman_spectroscopy",
        "domain": "spectroscopy",
        "keywords": ["Raman", "baseline correction", "peak detection", "FWHM", "Gaussian fit", "wavenumber", "functional group"],
        "summary": "Analyze Raman spectra by subtracting fluorescence baseline, detecting peaks, and matching to known vibrational bands for compound identification.",
        "strategy": [
            "Subtract baseline using polynomial fitting (degree 5) or ALS iterative method to remove fluorescence background",
            "Detect peaks in baseline-corrected spectrum using scipy.signal.find_peaks with prominence threshold",
            "For each peak, compute FWHM and area via Gaussian fitting, then match position to known Raman band database"
        ],
        "pitfalls": [
            "Polynomial baseline can overfit if degree is too high — use degree 5 and visually inspect",
            "Peak assignment tolerance: Raman bands can shift ±20 cm⁻¹ from literature values depending on sample conditions"
        ],
        "key_concepts": [
            "Key Raman bands: C-H stretch ~2900, C=O ~1700, C-C ~1000, O-H ~3400 cm⁻¹",
            "FWHM from scipy peak_widths is in data points — convert to wavenumber units using spectral resolution"
        ]
    },
    "S109_hdf5_chunked": {
        "scenario_id": "S109_hdf5_chunked",
        "domain": "data_storage",
        "keywords": ["HDF5", "chunking", "gzip", "compression", "h5py", "dataset", "metadata", "round-trip"],
        "summary": "Convert large CSV data to chunked, compressed HDF5 format with proper metadata and efficient access patterns using h5py.",
        "strategy": [
            "Auto-detect column types from CSV, create separate HDF5 datasets for numeric (float64) and string (variable-length) columns",
            "Set chunk size and compression (gzip/lzf) on each dataset for efficient partial reads and storage savings",
            "Store column metadata as HDF5 attributes and create a _metadata group with file provenance information"
        ],
        "pitfalls": [
            "h5py variable-length strings require special dtype: h5py.special_dtype(vlen=str)",
            "Chunk size should match typical read patterns — too small causes overhead, too large wastes memory"
        ],
        "key_concepts": [
            "HDF5 chunking enables partial I/O: only chunks overlapping the requested slice are read from disk",
            "Compression is applied per-chunk: gzip gives best ratio, lzf gives best speed"
        ]
    },
    "S110_log_regex": {
        "scenario_id": "S110_log_regex",
        "domain": "text_processing",
        "keywords": ["regex", "Apache log", "parsing", "status code", "anomaly", "IP", "request rate", "error rate"],
        "summary": "Parse server access logs using format-specific regex patterns to extract structured metrics, detect anomalies, and compute traffic statistics.",
        "strategy": [
            "Define regex patterns per format: Apache combined log captures IP, timestamp, method, URL, status, size in named groups",
            "Iterate lines with compiled regex, track parsed/failed counts, aggregate into status distribution and per-IP/URL counters",
            "Detect anomalies: IPs exceeding request threshold and URLs with abnormally high error rates"
        ],
        "pitfalls": [
            "Regex must handle edge cases: missing response size (shown as '-'), URLs with query strings, IPv6 addresses",
            "Timestamp parsing varies between formats — Apache uses [dd/Mon/yyyy:HH:MM:SS +ZZZZ]"
        ],
        "key_concepts": [
            "Compiled regex (re.compile) is much faster than per-line re.match for large log files",
            "Error rate = count(4xx + 5xx) / total_requests"
        ]
    },
    "S111_cuda_memory": {
        "scenario_id": "S111_cuda_memory",
        "domain": "gpu_computing",
        "keywords": ["CUDA", "memory allocation", "peak usage", "fragmentation", "dtype downcast", "timeline", "optimization"],
        "summary": "Analyze GPU memory allocation events to find peak usage, detect fragmentation, and suggest optimization opportunities like early frees and dtype downcasts.",
        "strategy": [
            "Replay allocation/free events chronologically to reconstruct the memory timeline and find peak usage point",
            "Compute fragmentation as ratio of largest contiguous free block to total free memory at peak",
            "Identify optimizations: tensors allocated long before last use (early-free candidates) and float64 tensors that could be float32"
        ],
        "pitfalls": [
            "Track allocations by tensor_name for free matching — mismatched alloc/free pairs corrupt the timeline",
            "Fragmentation calculation requires tracking individual allocation positions, not just total used/free"
        ],
        "key_concepts": [
            "Memory efficiency = peak_used / total_GPU_memory — lower is better",
            "dtype downcast float64→float32 saves 50% memory for tensors where precision isn't critical"
        ]
    },
    "S112_midi_chords": {
        "scenario_id": "S112_midi_chords",
        "domain": "music",
        "keywords": ["MIDI", "chord detection", "interval", "triad", "seventh chord", "root note", "key signature", "transition matrix"],
        "summary": "Detect and classify chords from MIDI note events by grouping simultaneous notes and analyzing pitch class intervals.",
        "strategy": [
            "Group notes by temporal proximity (within max_gap ms) to form chord candidates",
            "Extract pitch classes (note % 12), compute pairwise intervals, and match against known chord templates",
            "Build chord progression sequence and compute transition frequency matrix between chord types"
        ],
        "pitfalls": [
            "MIDI note numbers must be converted to pitch classes (mod 12) before interval analysis",
            "Chord inversion: same notes in different octaves form the same chord — normalize to root position first"
        ],
        "key_concepts": [
            "Major triad intervals: [4, 3] semitones; Minor: [3, 4]; Dim: [3, 3]; Aug: [4, 4]",
            "Key signature estimation: count frequency of each pitch class, match against major/minor scale templates"
        ]
    },
    "S113_inventory_reorder": {
        "scenario_id": "S113_inventory_reorder",
        "domain": "supply_chain",
        "keywords": ["EOQ", "reorder point", "safety stock", "lead time", "service level", "demand forecasting", "holding cost"],
        "summary": "Compute optimal inventory reorder points and Economic Order Quantities (EOQ) from historical demand data with safety stock for target service level.",
        "strategy": [
            "Compute demand statistics per product: mean, std, and coefficient of variation to choose demand distribution",
            "Calculate EOQ using the Wilson formula: Q* = sqrt(2*D*K/h) where D=annual demand, K=ordering cost, h=holding cost",
            "Determine reorder point: ROP = mean_demand_during_lead_time + z*std_demand_during_lead_time where z=norm.ppf(service_level)"
        ],
        "pitfalls": [
            "Demand during lead time variance combines both demand and lead time variability: Var = LT*Var(D) + D²*Var(LT)",
            "EOQ assumes constant demand rate — for highly variable demand, adjust with demand coefficient of variation"
        ],
        "key_concepts": [
            "Safety stock = z-score * std_demand_during_lead_time provides buffer against stockouts",
            "Total annual cost = (D/Q)*K + (Q/2)*h + stockout_cost for optimization"
        ]
    },
    "S114_obstacle_avoidance": {
        "scenario_id": "S114_obstacle_avoidance",
        "domain": "robotics",
        "keywords": ["RRT", "potential field", "path planning", "collision detection", "obstacle", "trajectory", "smoothing"],
        "summary": "Plan collision-free robot trajectories using RRT (tree-based random sampling) or potential field (gradient descent) methods in 2D environments.",
        "strategy": [
            "For RRT: grow tree by sampling random points, extending nearest node toward sample with collision check along the segment",
            "Collision check: test line segment against each circular obstacle using closest-point-to-line-segment distance",
            "Post-process path: attempt shortcutting between non-adjacent waypoints to smooth and shorten the trajectory"
        ],
        "pitfalls": [
            "RRT step_size too large skips narrow passages; too small makes tree grow slowly — balance with environment scale",
            "Potential field local minima: add random perturbation or switch to RRT when gradient descent stalls"
        ],
        "key_concepts": [
            "Line-circle collision: compute perpendicular distance from circle center to line segment, compare with radius",
            "Path smoothness measured by total curvature: sum of angle changes between consecutive segments"
        ]
    },
    "S115_quantum_circuit": {
        "scenario_id": "S115_quantum_circuit",
        "domain": "quantum_computing",
        "keywords": ["qubit", "state vector", "Hadamard", "CNOT", "unitary", "tensor product", "measurement", "entanglement"],
        "summary": "Simulate quantum circuits by applying gate unitary matrices to a state vector and computing measurement probabilities for each basis state.",
        "strategy": [
            "Initialize 2^n state vector to |0...0>, then for each gate build the full unitary using tensor products with identity",
            "For controlled gates (CNOT, CZ): construct the controlled unitary using projectors |0><0|⊗I + |1><1|⊗U on control/target",
            "Compute measurement probabilities P(outcome) = |amplitude|² and sample shots according to this distribution"
        ],
        "pitfalls": [
            "Qubit ordering convention matters: decide if qubit 0 is MSB or LSB and be consistent throughout",
            "For non-adjacent CNOT, either implement SWAP gates or directly construct the sparse controlled unitary"
        ],
        "key_concepts": [
            "Hadamard creates superposition: H|0> = (|0>+|1>)/√2; CNOT creates entanglement: CNOT(H|0>⊗|0>) = (|00>+|11>)/√2",
            "State vector has 2^n complex amplitudes; probabilities must sum to 1.0"
        ]
    },
}


def main():
    GENES_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Creating Gene JSON for {len(NEW_GENES)} new scenarios...")
    for scenario_id, gene in NEW_GENES.items():
        out_path = GENES_DIR / f"{scenario_id}.json"
        with open(out_path, "w") as f:
            json.dump(gene, f, indent=2, ensure_ascii=False)
        print(f"  ✓ {scenario_id}: {len(gene['keywords'])} keywords, {len(gene['strategy'])} strategy steps")
    print(f"\nDone! {len(NEW_GENES)} genes created.")


if __name__ == "__main__":
    main()
