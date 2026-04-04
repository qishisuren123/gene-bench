#!/usr/bin/env python3
"""
EvoMap 双回路实验：测试记忆模式 vs 探索模式对代码生成的影响。

基于 evomap 2.0 架构：
  - 记忆模式（过去导向）: signals, failures, experience
  - 探索模式（未来导向）: persona, objective, direction, target_profile

三个核心实验：
  EX8: Memory vs Exploration — 记忆模式 vs 探索模式的引导效果
  EX9: Failure-Guided Learning — 失败案例是否比正确策略更有效
  EX10: Persona Spectrum — 角色定位的方向与精度如何影响生成

用法:
    python run_evomap_experiments.py --experiment ex8 \
        --gemini-key "$GEMINI_API_KEY"

    python run_evomap_experiments.py --experiment all \
        --gemini-key "$GEMINI_API_KEY"
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from dataclasses import dataclass, asdict
from collections import Counter

# 复用已有模块
sys.path.insert(0, str(Path(__file__).parent))
from run_gene_bench import (
    MODEL_REGISTRY, SCENARIOS_DIR, GENES_DIR, DATA_DIR, SKILLS_DIR,
    call_llm, extract_python_code, evaluate_code, load_gene_for_trial,
    TEMPERATURE, MAX_TOKENS, EVAL_TIMEOUT,
    GENE_SENSITIVE_SCENARIOS as _GENE_SENSITIVE_SCENARIOS,
)
from gene_builder import load_gene, serialize_gene

ROOT = Path(__file__).parent

# ── 场景选择 ──
# 使用统一的 15 个 Gene 敏感场景（从 run_gene_bench.py 导入）
GENE_SENSITIVE_SCENARIOS = _GENE_SENSITIVE_SCENARIOS


# ── 领域信息（persona/signals 生成用）──
DOMAIN_INFO = {
    "S012_uv_spectroscopy": {
        "domain": "spectroscopy",
        "expert": "analytical chemist specializing in UV-Vis spectroscopy",
        "adjacent": "infrared spectroscopy researcher",
        "wrong": "machine learning engineer working on NLP",
        "failure_patterns": [
            "Forgetting to convert min-distance from nm to data point indices — assumes 1nm spacing",
            "Using raw peak_widths output without converting back to wavelength units for FWHM",
            "Setting min_height too low and detecting noise as peaks",
            "Not handling the case where zero peaks are detected for a sample",
        ],
        "signals": ["absorbance", "wavelength", "peak detection", "FWHM", "Beer-Lambert", "baseline correction", "spectral resolution", "molar absorptivity"],
    },
    "S017_ctd_ocean": {
        "domain": "oceanography",
        "expert": "physical oceanographer specializing in CTD profiling",
        "adjacent": "marine biologist studying plankton distribution",
        "wrong": "financial analyst working on stock market prediction",
        "failure_patterns": [
            "Mishandling pressure-to-depth conversion without accounting for latitude",
            "Not applying the UNESCO equation of state for seawater density",
            "Ignoring the salinity effect on sound speed calculation",
            "Using linear interpolation where the thermocline requires higher-order methods",
        ],
        "signals": ["CTD", "pressure", "salinity", "temperature profile", "density", "mixed layer depth", "thermocline", "halocline"],
    },
    "S105_community_detection": {
        "domain": "graph analysis",
        "expert": "network scientist specializing in community structure analysis",
        "adjacent": "social scientist studying organizational networks",
        "wrong": "audio engineer working on sound processing",
        "failure_patterns": [
            "Label propagation oscillating without convergence — synchronous updates cause flip-flopping",
            "Computing modularity Q incorrectly — forgetting the 1/2m normalization factor",
            "Not handling disconnected components as separate communities",
            "Allowing label propagation to run indefinitely without a maximum iteration limit",
        ],
        "signals": ["modularity", "Louvain", "label propagation", "adjacency matrix", "community structure", "degree distribution", "clustering coefficient", "betweenness"],
    },
    "S113_inventory_reorder": {
        "domain": "supply chain optimization",
        "expert": "operations research specialist in inventory management",
        "adjacent": "logistics planner for warehouse operations",
        "wrong": "astrophysicist studying stellar evolution",
        "failure_patterns": [
            "Using the EOQ formula without accounting for lead time demand variability",
            "Setting safety stock based on average demand instead of demand standard deviation",
            "Not considering the service level z-score when computing reorder points",
            "Ignoring the relationship between order frequency and holding costs",
        ],
        "signals": ["EOQ", "reorder point", "safety stock", "lead time", "demand variability", "service level", "holding cost", "order cost"],
    },
    "S101_climate_attribution": {
        "domain": "climate science",
        "expert": "climate scientist specializing in detection and attribution studies",
        "adjacent": "atmospheric physicist studying radiative forcing",
        "wrong": "database administrator working on SQL optimization",
        "failure_patterns": [
            "Not normalizing forcing factors before regression, causing coefficient scale issues",
            "Computing attribution fractions from raw coefficients instead of absolute contributions",
            "Forgetting to add an intercept term in the regression model",
            "Using OLS when forcing factors are highly correlated — Ridge is more stable",
        ],
        "signals": ["attribution", "forcing", "regression", "GHG", "solar", "volcanic", "aerosol", "radiative balance"],
    },
    "S026_earthquake_catalog": {
        "domain": "seismology",
        "expert": "seismologist specializing in earthquake catalog analysis",
        "adjacent": "structural engineer studying building response to seismic waves",
        "wrong": "botanist studying plant growth patterns",
        "failure_patterns": [
            "Treating magnitude as a linear scale — it's logarithmic (each unit = 10x amplitude)",
            "Not handling catalog completeness — small events are under-reported",
            "Incorrect distance calculation — must use Haversine for lat/lon coordinates",
            "Forgetting to apply the Gutenberg-Richter law for frequency-magnitude distribution",
        ],
        "signals": ["magnitude", "epicenter", "depth", "Gutenberg-Richter", "b-value", "Haversine", "catalog completeness", "seismic moment"],
    },
    "S007_data_viz": {
        "domain": "data visualization",
        "expert": "data visualization specialist with expertise in scientific plotting",
        "adjacent": "UX designer working on dashboard interfaces",
        "wrong": "embedded systems programmer working on firmware",
        "failure_patterns": [
            "Choosing the wrong chart type for the data structure — scatter for categorical data",
            "Not setting proper figure DPI for publication-quality output",
            "Ignoring colorblind-safe palettes when designing multi-series plots",
            "Hard-coding axis limits instead of computing from data range with padding",
        ],
        "signals": ["matplotlib", "figure", "axes", "colormap", "legend", "annotation", "publication quality", "subplot"],
    },
    "S005_protein_parse": {
        "domain": "bioinformatics",
        "expert": "structural bioinformatician specializing in protein data analysis",
        "adjacent": "computational chemist studying molecular dynamics",
        "wrong": "civil engineer designing bridge structures",
        "failure_patterns": [
            "Assuming fixed-width columns in PDB format are always present — some optional",
            "Not handling alternate conformations (altLoc) correctly",
            "Treating B-factors as quality scores without understanding they're temperature factors",
            "Forgetting to convert PDB coordinates from Angstroms when computing distances",
        ],
        "signals": ["PDB", "ATOM", "residue", "chain", "B-factor", "coordinates", "secondary structure", "HETATM"],
    },
    "S030_fossil_morpho": {
        "domain": "paleontology",
        "expert": "paleontologist specializing in quantitative morphometric analysis",
        "adjacent": "evolutionary biologist studying phenotypic variation",
        "wrong": "telecommunications engineer working on signal routing",
        "failure_patterns": [
            "Using Euclidean distance on raw landmark coordinates without Procrustes alignment",
            "Not accounting for size in shape analysis — must separate size and shape components",
            "Applying PCA to raw coordinates instead of to Procrustes-aligned residuals",
            "Forgetting to check for landmark outliers before Procrustes superimposition",
        ],
        "signals": ["morphometrics", "landmark", "Procrustes", "PCA", "shape space", "centroid size", "allometry", "geometric morphometrics"],
    },
    "S011_particle_physics": {
        "domain": "particle physics",
        "expert": "experimental particle physicist specializing in data analysis at colliders",
        "adjacent": "nuclear physicist studying heavy-ion collisions",
        "wrong": "real estate analyst working on property valuations",
        "failure_patterns": [
            "Not accounting for detector acceptance and efficiency in cross-section calculations",
            "Using wrong kinematic variables — transverse momentum pT vs total momentum p",
            "Ignoring background subtraction when extracting signal peaks",
            "Computing invariant mass without proper four-vector algebra",
        ],
        "signals": ["invariant mass", "transverse momentum", "cross-section", "luminosity", "background subtraction", "histogram", "binning", "significance"],
    },
    "S033_exoplanet_transit": {
        "domain": "astrophysics",
        "expert": "astrophysicist specializing in exoplanet transit photometry",
        "adjacent": "stellar astronomer studying variable stars",
        "wrong": "marine biologist studying whale migration",
        "failure_patterns": [
            "Using a box-shaped transit model instead of proper limb-darkening curves",
            "Not detrending the light curve for systematic effects before fitting",
            "Computing transit depth without accounting for flux normalization",
            "Ignoring the ingress/egress shape which constrains planet-to-star radius ratio",
        ],
        "signals": ["transit", "light curve", "limb darkening", "epoch", "period", "depth", "flux", "phase folding"],
    },
    "S090_noise_reduction": {
        "domain": "signal processing",
        "expert": "signal processing engineer specializing in noise reduction algorithms",
        "adjacent": "acoustics researcher studying room impulse responses",
        "wrong": "graphic designer working on typography",
        "failure_patterns": [
            "Applying frequency-domain filtering without proper windowing, causing spectral leakage",
            "Using a fixed noise threshold instead of adaptive SNR-based estimation",
            "Forgetting overlap-add or overlap-save when processing signals in blocks",
            "Choosing filter order too high, introducing ringing artifacts in time domain",
        ],
        "signals": ["FFT", "spectral subtraction", "Wiener filter", "SNR", "window function", "overlap-add", "noise floor", "bandpass"],
    },
    "S096_network_influence": {
        "domain": "network science",
        "expert": "network scientist specializing in influence maximization",
        "adjacent": "sociologist studying information diffusion",
        "wrong": "pastry chef working on recipe optimization",
        "failure_patterns": [
            "Using degree centrality alone — high-degree nodes may be clustered together",
            "Not accounting for network structure in cascade simulation",
            "Ignoring the diminishing returns of adding nodes from the same community",
            "Computing influence spread without proper Monte Carlo averaging",
        ],
        "signals": ["centrality", "influence spread", "cascade", "seed set", "greedy algorithm", "IC model", "network topology", "k-core"],
    },
    "S112_midi_chords": {
        "domain": "music informatics",
        "expert": "music information retrieval researcher specializing in harmonic analysis",
        "adjacent": "audio engineer working on music production",
        "wrong": "geologist studying tectonic plate movements",
        "failure_patterns": [
            "Treating MIDI note numbers as frequencies — they're integer indices, not Hz",
            "Not grouping simultaneous note-on events within a timing tolerance window",
            "Classifying chords using only pitch class without considering inversions",
            "Ignoring note velocity when determining chord boundaries",
        ],
        "signals": ["MIDI", "note-on", "pitch class", "chord recognition", "interval", "velocity", "tick", "tempo"],
    },
    "S103_instrumental_variable": {
        "domain": "econometrics",
        "expert": "econometrician specializing in causal inference with instrumental variables",
        "adjacent": "biostatistician running clinical trials",
        "wrong": "animation artist working on character design",
        "failure_patterns": [
            "Using a weak instrument — the F-statistic on first stage should be >10",
            "Not checking the exclusion restriction — instrument may affect outcome directly",
            "Applying 2SLS without properly staging: first regress X on Z, then Y on X-hat",
            "Ignoring heteroscedasticity in standard errors after IV estimation",
        ],
        "signals": ["instrumental variable", "2SLS", "endogeneity", "first stage", "exclusion restriction", "Hausman test", "weak instrument", "LATE"],
    },
    # ── 以下为扩展的 30 个场景 DOMAIN_INFO ──
    "S002_spike_behavior": {
        "domain": "neuroscience",
        "expert": "computational neuroscientist specializing in electrophysiology data analysis",
        "adjacent": "biomedical engineer working on neural implant signals",
        "wrong": "web developer building e-commerce frontends",
        "failure_patterns": [
            "Not sorting spike timestamps before binning — produces incorrect firing rate histograms",
            "Assuming uniform sampling rate across all channels without verifying metadata",
            "Mixing units between milliseconds and seconds in time alignment",
            "Forgetting to validate HDF5 group structure before writing nested datasets",
        ],
        "signals": ["spike train", "firing rate", "HDF5", "binning", "timestamp", "neural recording", "sampling rate", "electrode"],
    },
    "S028_audio_features": {
        "domain": "audio signal processing",
        "expert": "audio researcher specializing in music information retrieval and acoustic feature extraction",
        "adjacent": "speech recognition engineer working on ASR systems",
        "wrong": "civil engineer designing road networks",
        "failure_patterns": [
            "Using wrong FFT window size — too short loses frequency resolution, too long loses time resolution",
            "Computing MFCCs without pre-emphasis filtering, underweighting high-frequency energy",
            "Not normalizing spectral features across different audio durations",
            "Forgetting to handle stereo audio by averaging channels or processing separately",
        ],
        "signals": ["MFCC", "spectral centroid", "zero crossing rate", "short-time energy", "chroma", "FFT", "mel filterbank", "onset detection"],
    },
    "S036_cmb_power_spectrum": {
        "domain": "cosmology",
        "expert": "cosmologist specializing in CMB data analysis and angular power spectrum estimation",
        "adjacent": "radio astronomer studying galactic foregrounds",
        "wrong": "veterinarian specializing in animal nutrition",
        "failure_patterns": [
            "Not converting from pixel space to angular multipole space correctly",
            "Ignoring beam smoothing effects that suppress power at high multipoles",
            "Using flat sky approximation for full-sky CMB analysis",
            "Not accounting for noise bias in the raw power spectrum estimate",
        ],
        "signals": ["angular power spectrum", "multipole", "Cl", "beam function", "pixel", "spherical harmonics", "noise bias", "cosmological parameters"],
    },
    "S037_asteroid_orbit": {
        "domain": "celestial mechanics",
        "expert": "planetary scientist specializing in asteroid orbital dynamics",
        "adjacent": "spacecraft trajectory engineer designing interplanetary missions",
        "wrong": "fashion designer working on textile patterns",
        "failure_patterns": [
            "Mixing degrees and radians in orbital element conversions",
            "Not handling the orbital eccentricity edge case where e ≈ 0 (circular orbit) causes division issues",
            "Forgetting to apply the correct gravitational parameter (GM_sun) in Kepler's equation",
            "Using Cartesian-to-Keplerian conversion without handling retrograde orbits (i > 90°)",
        ],
        "signals": ["semi-major axis", "eccentricity", "inclination", "orbital period", "Kepler equation", "true anomaly", "argument of perihelion", "ascending node"],
    },
    "S044_bfactor_analysis": {
        "domain": "structural biology",
        "expert": "structural biologist specializing in X-ray crystallography and B-factor analysis",
        "adjacent": "molecular dynamics researcher studying protein flexibility",
        "wrong": "marketing analyst working on customer segmentation",
        "failure_patterns": [
            "Treating B-factors as simple quality indicators — they represent atomic displacement parameters",
            "Not normalizing B-factors across different chains or structures for comparison",
            "Ignoring the relationship between B-factor and resolution — high-resolution structures have lower B-factors",
            "Computing average B-factor per residue without weighting by occupancy",
        ],
        "signals": ["B-factor", "temperature factor", "atomic displacement", "residue", "chain", "occupancy", "resolution", "flexibility"],
    },
    "S045_ramachandran": {
        "domain": "structural biology",
        "expert": "protein structure analyst specializing in backbone geometry and Ramachandran analysis",
        "adjacent": "computational biophysicist studying protein folding",
        "wrong": "automotive mechanic working on engine diagnostics",
        "failure_patterns": [
            "Computing phi/psi angles without handling chain breaks — peptide bond discontinuity",
            "Not wrapping angles to [-180, 180] range after calculation",
            "Ignoring glycine and proline special cases in Ramachandran classification",
            "Treating all outliers as errors — some are genuinely strained conformations",
        ],
        "signals": ["phi angle", "psi angle", "backbone", "Ramachandran plot", "allowed region", "glycine", "proline", "outlier"],
    },
    "S048_gene_ontology": {
        "domain": "genomics",
        "expert": "bioinformatician specializing in gene ontology enrichment analysis",
        "adjacent": "systems biologist studying pathway regulation",
        "wrong": "landscape architect designing urban parks",
        "failure_patterns": [
            "Not correcting for multiple testing — must apply Bonferroni or FDR correction to p-values",
            "Using the wrong background gene set for enrichment — should match the experimental platform",
            "Ignoring the hierarchical structure of GO terms — child terms inherit parent annotations",
            "Computing enrichment on too-specific GO terms with very few annotated genes",
        ],
        "signals": ["enrichment", "p-value", "FDR", "GO term", "hypergeometric test", "annotation", "biological process", "multiple testing"],
    },
    "S052_phylogenetic_distance": {
        "domain": "evolutionary biology",
        "expert": "phylogeneticist specializing in molecular evolution and tree construction",
        "adjacent": "population geneticist studying allele frequencies",
        "wrong": "interior designer working on office spaces",
        "failure_patterns": [
            "Using raw sequence differences without correcting for multiple substitutions (Jukes-Cantor/Kimura)",
            "Not handling gaps in multiple sequence alignments — should be excluded or treated as missing data",
            "Computing patristic distances on an unrooted tree without properly handling branch lengths",
            "Ignoring rate heterogeneity across sites when estimating evolutionary distances",
        ],
        "signals": ["distance matrix", "Jukes-Cantor", "Kimura", "substitution model", "tree topology", "branch length", "UPGMA", "neighbor joining"],
    },
    "S053_methylation_beta": {
        "domain": "epigenetics",
        "expert": "epigeneticist specializing in DNA methylation array data analysis",
        "adjacent": "cancer biologist studying epigenetic changes in tumors",
        "wrong": "electrician working on residential wiring",
        "failure_patterns": [
            "Not handling beta values at boundaries (0 and 1) — causes infinite M-values with logit transform",
            "Ignoring batch effects between methylation arrays without normalization",
            "Using mean beta instead of median for summary statistics — beta distributions are often skewed",
            "Not filtering probes on sex chromosomes or SNP-affected positions",
        ],
        "signals": ["beta value", "M-value", "CpG site", "methylation array", "differential methylation", "probe filtering", "normalization", "island/shore"],
    },
    "S054_species_accumulation": {
        "domain": "ecology",
        "expert": "community ecologist specializing in biodiversity estimation and species richness",
        "adjacent": "conservation biologist planning wildlife surveys",
        "wrong": "software QA tester working on mobile apps",
        "failure_patterns": [
            "Not randomizing sample order — accumulation curves depend on order of site addition",
            "Confusing species richness with Shannon diversity — they measure different aspects",
            "Not computing confidence intervals from multiple random permutations of sample order",
            "Using parametric extrapolation without verifying the accumulation curve has reached an asymptote",
        ],
        "signals": ["species richness", "accumulation curve", "rarefaction", "Chao estimator", "sample order", "asymptote", "confidence interval", "permutation"],
    },
    "S060_phenology_shifts": {
        "domain": "phenology",
        "expert": "phenologist specializing in climate-driven shifts in seasonal biological events",
        "adjacent": "agricultural scientist studying crop growth timing",
        "wrong": "mechanical engineer designing HVAC systems",
        "failure_patterns": [
            "Not accounting for latitude-dependent trends in phenological timing",
            "Using linear regression when the relationship is non-linear — consider breakpoints or polynomial fits",
            "Ignoring missing years in the time series — interpolation can introduce bias",
            "Confusing day-of-year with calendar date when comparing across years",
        ],
        "signals": ["first bloom", "leaf-out date", "growing degree days", "trend analysis", "day of year", "climate correlation", "spring onset", "phenophase"],
    },
    "S067_salinity_gradient": {
        "domain": "estuarine science",
        "expert": "estuarine oceanographer specializing in salinity dynamics and mixing processes",
        "adjacent": "environmental engineer studying water quality in river deltas",
        "wrong": "jewelry designer working on gemstone settings",
        "failure_patterns": [
            "Assuming linear salinity gradient — estuaries often show exponential or logistic mixing curves",
            "Not accounting for tidal effects on instantaneous salinity measurements",
            "Computing mixing zone width without proper definition of fresh/salt water end-members",
            "Ignoring vertical stratification — surface and bottom salinity can differ dramatically",
        ],
        "signals": ["salinity", "estuary", "mixing zone", "tidal influence", "stratification", "freshwater fraction", "conductivity", "gradient"],
    },
    "S068_weather_fronts": {
        "domain": "meteorology",
        "expert": "synoptic meteorologist specializing in frontal analysis and weather systems",
        "adjacent": "climate modeler studying atmospheric dynamics",
        "wrong": "event planner organizing corporate conferences",
        "failure_patterns": [
            "Using too small a spatial gradient threshold — detects noise as fronts",
            "Not considering both temperature gradient magnitude AND direction for front classification",
            "Confusing cold fronts and warm fronts — cold fronts have cold air advancing, warm fronts opposite",
            "Ignoring the time derivative of temperature when identifying moving fronts",
        ],
        "signals": ["temperature gradient", "cold front", "warm front", "isobar", "pressure change", "wind shift", "dew point", "frontal zone"],
    },
    "S069_rainfall_extreme": {
        "domain": "hydrology",
        "expert": "hydrologist specializing in extreme rainfall statistics and flood frequency analysis",
        "adjacent": "water resources engineer designing stormwater systems",
        "wrong": "music producer working on electronic tracks",
        "failure_patterns": [
            "Using normal distribution for extreme rainfall — must use GEV or Gumbel distributions",
            "Not using annual maxima series — including non-extreme events biases the fit",
            "Computing return periods without confidence intervals — single point estimates are insufficient",
            "Ignoring stationarity assumption — climate change may invalidate historical frequency analysis",
        ],
        "signals": ["return period", "GEV distribution", "Gumbel", "annual maximum", "exceedance probability", "IDF curve", "L-moments", "frequency analysis"],
    },
    "S072_ozone_profile": {
        "domain": "atmospheric chemistry",
        "expert": "atmospheric scientist specializing in stratospheric ozone profiling",
        "adjacent": "remote sensing specialist working on satellite-based atmospheric monitoring",
        "wrong": "bakery owner managing daily bread production",
        "failure_patterns": [
            "Not converting between mixing ratio (ppmv) and number density — requires pressure and temperature",
            "Ignoring the temperature dependence of ozone absorption cross-sections",
            "Using wrong altitude grid spacing — ozone profiles need finer resolution near tropopause",
            "Not identifying the ozone maximum correctly — it typically occurs at 20-25 km altitude",
        ],
        "signals": ["ozone mixing ratio", "Dobson units", "stratosphere", "tropopause", "altitude profile", "absorption cross-section", "column ozone", "ozonesonde"],
    },
    "S074_heat_index": {
        "domain": "applied meteorology",
        "expert": "biometeorolist specializing in thermal comfort and heat stress indices",
        "adjacent": "public health researcher studying heat-related mortality",
        "wrong": "florist arranging wedding bouquets",
        "failure_patterns": [
            "Using the simple heat index formula outside its valid range (T > 80°F and RH > 40%)",
            "Not applying the Rothfusz regression adjustment terms for extreme conditions",
            "Mixing Fahrenheit and Celsius inputs without proper conversion",
            "Defining heat waves with fixed thresholds instead of location-specific percentiles",
        ],
        "signals": ["heat index", "relative humidity", "temperature", "heat wave", "Rothfusz equation", "thermal comfort", "wet-bulb temperature", "threshold"],
    },
    "S077_grain_size": {
        "domain": "sedimentology",
        "expert": "sedimentologist specializing in grain size distribution analysis",
        "adjacent": "geomorphologist studying coastal sediment transport",
        "wrong": "HR recruiter reviewing job applications",
        "failure_patterns": [
            "Using arithmetic mean on phi-scale data instead of geometric (moment) statistics",
            "Not interpolating between sieve intervals for accurate percentile calculation",
            "Confusing phi units (logarithmic) with millimeter units (linear) in statistical measures",
            "Computing sorting coefficient without specifying which percentile method (Folk-Ward vs moment)",
        ],
        "signals": ["grain size distribution", "phi scale", "sorting", "skewness", "percentile", "cumulative curve", "Folk-Ward", "mean grain size"],
    },
    "S084_dose_response": {
        "domain": "pharmacology",
        "expert": "pharmacologist specializing in dose-response modeling and drug potency estimation",
        "adjacent": "toxicologist studying environmental chemical exposure thresholds",
        "wrong": "dance instructor teaching ballroom techniques",
        "failure_patterns": [
            "Using linear regression on sigmoidal dose-response data — must use logistic (4PL) model",
            "Not log-transforming dose values before fitting — EC50 operates on log-concentration scale",
            "Fixing Hill slope to 1.0 without verifying — steep dose-response curves need variable slope",
            "Ignoring data points at extremes (0% and 100%) which anchor the curve baselines",
        ],
        "signals": ["EC50", "IC50", "Hill equation", "four-parameter logistic", "dose", "response", "sigmoid", "potency"],
    },
    "S091_modulation_classify": {
        "domain": "digital communications",
        "expert": "communications engineer specializing in digital modulation and signal classification",
        "adjacent": "radar systems engineer working on signal detection",
        "wrong": "pastry chef working on cake decoration",
        "failure_patterns": [
            "Not normalizing IQ samples before feature extraction — amplitude variations dominate classification",
            "Confusing instantaneous frequency with carrier frequency offset",
            "Using time-domain features alone — constellation diagram features are essential for QAM vs PSK",
            "Not handling unknown SNR conditions — features degrade at low SNR",
        ],
        "signals": ["IQ samples", "constellation diagram", "modulation type", "SNR", "phase offset", "symbol rate", "spectral features", "classification accuracy"],
    },
    "S093_echo_removal": {
        "domain": "acoustic signal processing",
        "expert": "acoustics engineer specializing in echo cancellation and room impulse response estimation",
        "adjacent": "telecom engineer working on VoIP audio quality",
        "wrong": "geographer mapping urban land use patterns",
        "failure_patterns": [
            "Using fixed filter length regardless of room size — filter must span the room impulse response",
            "Not updating adaptive filter coefficients when the acoustic environment changes",
            "Applying spectral subtraction too aggressively, causing musical noise artifacts",
            "Ignoring the direct-path component when estimating echo delay",
        ],
        "signals": ["echo cancellation", "impulse response", "adaptive filter", "LMS", "NLMS", "delay estimation", "room acoustics", "speech enhancement"],
    },
    "S102_protein_secondary": {
        "domain": "structural biology",
        "expert": "structural biologist specializing in protein secondary structure prediction",
        "adjacent": "biophysicist studying protein folding kinetics",
        "wrong": "real estate photographer shooting property listings",
        "failure_patterns": [
            "Using wrong window sizes — helix nucleation needs 6 residues, sheet needs 5 residues",
            "Not handling sequence edges where sliding window extends beyond bounds",
            "Missing propensity values for all 20 standard amino acids in lookup tables",
            "Not resolving helix/sheet overlap — must compare average propensities to choose winner",
        ],
        "signals": ["Chou-Fasman", "helix propensity", "sheet propensity", "sliding window", "nucleation", "coil", "FASTA", "structure string"],
    },
    "S104_multisensor_anomaly": {
        "domain": "sensor fusion",
        "expert": "IoT data scientist specializing in multi-sensor anomaly detection systems",
        "adjacent": "industrial engineer monitoring manufacturing equipment health",
        "wrong": "children's book illustrator drawing animal stories",
        "failure_patterns": [
            "Computing rolling statistics on first window_size points where insufficient data exists",
            "Using raw Mahalanobis distance with singular covariance matrix — needs regularization",
            "Not distinguishing point anomalies from collective anomalies — need minimum duration check",
            "Flagging too many anomalies by setting threshold too low — use cross-sensor consensus",
        ],
        "signals": ["z-score", "Mahalanobis distance", "rolling statistics", "cross-sensor correlation", "point anomaly", "collective anomaly", "threshold", "ensemble"],
    },
    "S106_seismic_denoise": {
        "domain": "geophysics",
        "expert": "seismologist specializing in seismic waveform processing and event detection",
        "adjacent": "exploration geophysicist working on reflection seismology",
        "wrong": "fashion blogger reviewing seasonal trends",
        "failure_patterns": [
            "Not normalizing filter frequencies to Nyquist rate — scipy.signal.butter requires 0-1 range",
            "Using forward-only filtering (lfilter) instead of zero-phase (filtfilt) — introduces time delay",
            "STA/LTA window sizes not matching the expected signal duration — misses small events",
            "Not determining sampling rate from actual time column spacing — assuming fixed rate",
        ],
        "signals": ["Butterworth", "bandpass filter", "STA/LTA", "P-wave", "arrival time", "SNR", "filtfilt", "sampling rate"],
    },
    "S107_regime_switch": {
        "domain": "financial time series",
        "expert": "quantitative analyst specializing in volatility regime detection and structural breaks",
        "adjacent": "risk manager monitoring portfolio exposure during market transitions",
        "wrong": "yoga instructor teaching beginner classes",
        "failure_patterns": [
            "Using simple returns instead of log returns — log returns have better statistical properties",
            "Starting regime detection before rolling window is fully populated — produces NaN-based errors",
            "Not annualizing Sharpe ratio correctly — must multiply mean by 252 and std by sqrt(252)",
            "Creating too many short regimes — need minimum length threshold and merging logic",
        ],
        "signals": ["log returns", "rolling volatility", "regime", "change point", "Sharpe ratio", "crisis", "transition matrix", "structural break"],
    },
    "S108_raman_spectroscopy": {
        "domain": "spectroscopy",
        "expert": "analytical chemist specializing in Raman spectroscopy and vibrational band assignment",
        "adjacent": "materials scientist using Raman for thin film characterization",
        "wrong": "sports coach training youth basketball teams",
        "failure_patterns": [
            "Polynomial baseline degree too high — overfits and removes real Raman peaks along with fluorescence",
            "Not converting peak_widths from data point indices to wavenumber units for FWHM",
            "Using exact literature wavenumber values for band matching — need ±20 cm⁻¹ tolerance",
            "Not handling negative intensities after baseline subtraction — clip to zero",
        ],
        "signals": ["wavenumber", "baseline correction", "fluorescence", "peak detection", "FWHM", "Raman band", "functional group", "vibrational mode"],
    },
    "S109_hdf5_chunked": {
        "domain": "data engineering",
        "expert": "data engineer specializing in large-scale scientific data storage with HDF5",
        "adjacent": "database administrator working with columnar storage formats",
        "wrong": "fitness trainer designing workout programs",
        "failure_patterns": [
            "Using fixed-length strings for variable-length text data — truncates values silently",
            "Setting chunk size too small — causes excessive overhead in read/write operations",
            "Loading entire CSV into memory before writing HDF5 — must stream in chunks for large files",
            "Not storing column metadata as HDF5 attributes — makes the file unusable without original CSV",
        ],
        "signals": ["HDF5", "h5py", "chunking", "compression", "gzip", "dataset", "attributes", "metadata"],
    },
    "S110_log_regex": {
        "domain": "devops",
        "expert": "site reliability engineer specializing in log analysis and observability",
        "adjacent": "security analyst working on intrusion detection from access logs",
        "wrong": "pet groomer running a mobile grooming service",
        "failure_patterns": [
            "Regex not handling missing response size field (shown as '-' in Apache logs)",
            "Not compiling regex patterns — recompiling per line causes severe performance issues",
            "Ignoring lines that don't match the regex pattern — must count and report parse failures",
            "Using greedy matching for URLs — captures too much when query strings contain spaces",
        ],
        "signals": ["regex", "Apache log", "status code", "IP address", "error rate", "request count", "anomaly detection", "hourly distribution"],
    },
    "S111_cuda_memory": {
        "domain": "GPU computing",
        "expert": "GPU systems engineer specializing in CUDA memory management and optimization",
        "adjacent": "deep learning infrastructure engineer profiling training workloads",
        "wrong": "wedding planner coordinating venue logistics",
        "failure_patterns": [
            "Not matching free events to their corresponding alloc by tensor_name — corrupts timeline",
            "Computing fragmentation from total used/free ratio instead of tracking individual allocation positions",
            "Missing peak usage because events are processed out of timestamp order",
            "Suggesting dtype downcast for tensors that require float64 precision (e.g., loss computation)",
        ],
        "signals": ["allocation", "free", "peak memory", "fragmentation", "tensor", "dtype", "GPU memory", "optimization"],
    },
    "S114_obstacle_avoidance": {
        "domain": "robotics",
        "expert": "robotics engineer specializing in motion planning and path optimization",
        "adjacent": "autonomous vehicle researcher working on LIDAR-based navigation",
        "wrong": "librarian cataloging rare book collections",
        "failure_patterns": [
            "RRT step size too large — skips narrow passages between closely spaced obstacles",
            "Checking only waypoint collisions without testing the line segment between waypoints",
            "Not implementing goal bias in RRT sampling — pure random sampling converges very slowly",
            "Potential field getting stuck in local minima between symmetrically placed obstacles",
        ],
        "signals": ["RRT", "collision detection", "path planning", "waypoint", "obstacle clearance", "step size", "goal bias", "path smoothing"],
    },
    "S115_quantum_circuit": {
        "domain": "quantum computing",
        "expert": "quantum computing researcher specializing in circuit simulation and gate synthesis",
        "adjacent": "quantum algorithm developer designing variational circuits",
        "wrong": "archaeology student cataloging pottery shards",
        "failure_patterns": [
            "Inconsistent qubit ordering convention — MSB vs LSB indexing produces different tensor products",
            "Not handling non-adjacent CNOT gates — must use SWAP or direct sparse construction",
            "Accumulated floating-point errors cause probabilities to not sum to 1.0 — need normalization",
            "Using θ directly instead of θ/2 in rotation gate matrices (RX, RY, RZ)",
        ],
        "signals": ["state vector", "unitary matrix", "tensor product", "CNOT", "Hadamard", "measurement", "probability", "qubit"],
    },
}


# ── Prompt 模板 ──

# --- EX8: Memory vs Exploration ---

def make_memory_signals_prompt(scenario_id: str) -> str:
    """记忆模式 - 仅信号/关键词（过去导向）"""
    info = DOMAIN_INFO.get(scenario_id, {})
    signals = info.get("signals", [])
    if not signals:
        # 回退到 gene keywords
        gene_path = GENES_DIR / f"{scenario_id}.json"
        if gene_path.exists():
            gene = json.loads(gene_path.read_text())
            signals = gene.get("keywords", [])

    return (
        "Based on accumulated experience with similar tasks, these domain signals "
        "have been identified as critical indicators of solution quality:\n\n"
        f"<memory-signals>\n"
        f"Relevant signals: {', '.join(signals)}\n"
        f"</memory-signals>\n\n"
        "Use these signals to orient your approach. They reflect patterns "
        "that consistently appear in successful solutions."
    )


def make_memory_failures_prompt(scenario_id: str) -> str:
    """记忆模式 - 失败经验（过去导向的负面知识）"""
    info = DOMAIN_INFO.get(scenario_id, {})
    failures = info.get("failure_patterns", [])
    if not failures:
        return ""

    failure_text = "\n".join(f"  - {f}" for f in failures)
    return (
        "Based on analysis of past failed attempts at similar tasks, "
        "these failure patterns have been documented:\n\n"
        "<memory-failures>\n"
        f"Common failure patterns:\n{failure_text}\n\n"
        "Each of these has caused solution failures in >30% of past attempts.\n"
        "</memory-failures>\n\n"
        "Learn from these failures. Avoid these specific pitfalls in your implementation."
    )


def make_memory_experience_prompt(scenario_id: str) -> str:
    """记忆模式 - 完整经验叙述（过去导向的正+负知识）"""
    info = DOMAIN_INFO.get(scenario_id, {})
    signals = info.get("signals", [])
    failures = info.get("failure_patterns", [])
    domain = info.get("domain", "this domain")

    # 加载 gene 的 strategy
    gene_path = GENES_DIR / f"{scenario_id}.json"
    strategy = []
    if gene_path.exists():
        gene = json.loads(gene_path.read_text())
        strategy = gene.get("strategy", [])

    failure_text = "\n".join(f"  - {f}" for f in failures[:3])
    strategy_text = "\n".join(f"  - {s}" for s in strategy[:3])

    return (
        f"Drawing from accumulated experience in {domain} tasks:\n\n"
        "<memory-experience>\n"
        f"Domain signals that matter: {', '.join(signals[:5])}\n\n"
        f"What worked in past successful solutions:\n{strategy_text}\n\n"
        f"What caused past failures:\n{failure_text}\n\n"
        "This experience was compiled from multiple iterations of similar tasks.\n"
        "</memory-experience>\n\n"
        "Use this experience to guide your approach. Trust patterns that "
        "consistently appear across solutions."
    )


def make_exploration_persona_prompt(scenario_id: str) -> str:
    """探索模式 - 专家角色设定（未来导向）"""
    info = DOMAIN_INFO.get(scenario_id, {})
    expert = info.get("expert", "domain expert")

    return (
        f"You are a {expert} with over 15 years of experience. "
        f"You have published extensively in this field and regularly solve "
        f"computational problems in your domain.\n\n"
        f"Approach this task as you would approach a real research problem "
        f"in your field — with rigor, domain expertise, and attention to "
        f"methodology that reflects your deep understanding."
    )


def make_exploration_objective_prompt(scenario_id: str) -> str:
    """探索模式 - 明确目标（未来导向）"""
    # 从 task.md 提取核心目标
    task_path = SCENARIOS_DIR / scenario_id / "task.md"
    task_desc = task_path.read_text().strip() if task_path.exists() else ""

    # 取第一句作为核心目标
    first_line = task_desc.split("\n")[0] if task_desc else "Complete the task"

    return (
        "Your objective is clearly defined:\n\n"
        "<exploration-objective>\n"
        f"Primary goal: {first_line}\n\n"
        "Success criteria:\n"
        "  1. All test cases must pass\n"
        "  2. Code must be self-contained and production-quality\n"
        "  3. Edge cases must be handled gracefully\n"
        "  4. Output format must match specifications exactly\n"
        "</exploration-objective>\n\n"
        "Focus relentlessly on meeting these criteria. "
        "Every design decision should serve the objective."
    )


def make_exploration_direction_prompt(scenario_id: str) -> str:
    """探索模式 - 策略方向（未来导向）"""
    gene_path = GENES_DIR / f"{scenario_id}.json"
    if not gene_path.exists():
        return ""
    gene = json.loads(gene_path.read_text())
    summary = gene.get("summary", "")

    return (
        "Strategic direction for your exploration:\n\n"
        "<exploration-direction>\n"
        f"Recommended approach: {summary}\n\n"
        "This direction has been identified as the most promising path "
        "for tasks of this type. Explore solutions that align with this guidance, "
        "but adapt as needed based on the specific requirements.\n"
        "</exploration-direction>"
    )


def make_exploration_full_prompt(scenario_id: str) -> str:
    """探索模式 - 完整探索配置（persona + objective + direction + target_profile）"""
    info = DOMAIN_INFO.get(scenario_id, {})
    expert = info.get("expert", "domain expert")
    domain = info.get("domain", "this domain")
    signals = info.get("signals", [])

    gene_path = GENES_DIR / f"{scenario_id}.json"
    summary = ""
    if gene_path.exists():
        gene = json.loads(gene_path.read_text())
        summary = gene.get("summary", "")

    task_path = SCENARIOS_DIR / scenario_id / "task.md"
    task_desc = task_path.read_text().strip() if task_path.exists() else ""
    first_line = task_desc.split("\n")[0] if task_desc else "Complete the task"

    return (
        f"<exploration-profile>\n"
        f"Persona: You are a {expert}\n"
        f"Objective: {first_line}\n"
        f"Direction: {summary}\n"
        f"Target profile: A solution demonstrating expertise in {domain}, "
        f"utilizing established methodology around {', '.join(signals[:4])}\n"
        f"</exploration-profile>\n\n"
        f"Execute this exploration with full domain expertise. "
        f"Your solution should reflect the analytical rigor of a published researcher."
    )


# --- EX9: Failure-Guided Learning ---

def make_correct_strategy_prompt(scenario_id: str) -> str:
    """仅正确策略（从 gene 提取）"""
    gene_path = GENES_DIR / f"{scenario_id}.json"
    if not gene_path.exists():
        return ""
    gene = json.loads(gene_path.read_text())
    strategy = gene.get("strategy", [])

    steps = "\n".join(f"  {i+1}. {s}" for i, s in enumerate(strategy))
    return (
        "Here is the correct approach to solve this task:\n\n"
        "<correct-strategy>\n"
        f"{steps}\n"
        "</correct-strategy>\n\n"
        "Follow this strategy step-by-step."
    )


def make_failure_warnings_prompt(scenario_id: str) -> str:
    """仅失败警告（负面知识）"""
    info = DOMAIN_INFO.get(scenario_id, {})
    failures = info.get("failure_patterns", [])
    if not failures:
        return ""

    failure_text = "\n".join(f"  {i+1}. {f}" for i, f in enumerate(failures))
    return (
        "WARNING: These are the most common mistakes that cause solutions to fail:\n\n"
        "<failure-warnings>\n"
        f"{failure_text}\n"
        "</failure-warnings>\n\n"
        "Each of these mistakes has been observed in multiple failed attempts. "
        "Make sure your solution avoids ALL of these pitfalls."
    )


def make_failure_then_strategy_prompt(scenario_id: str) -> str:
    """先给失败案例，再给正确策略"""
    failures = make_failure_warnings_prompt(scenario_id)
    strategy = make_correct_strategy_prompt(scenario_id)
    if not failures or not strategy:
        return failures + strategy

    return (
        "First, understand what NOT to do:\n\n"
        f"{failures}\n\n"
        "Now, here is the recommended approach:\n\n"
        f"{strategy}"
    )


def make_strategy_then_failure_prompt(scenario_id: str) -> str:
    """先给正确策略，再给失败案例（顺序对调）"""
    failures = make_failure_warnings_prompt(scenario_id)
    strategy = make_correct_strategy_prompt(scenario_id)
    if not failures or not strategy:
        return strategy + failures

    return (
        "Here is the recommended approach:\n\n"
        f"{strategy}\n\n"
        "And here are critical mistakes to avoid:\n\n"
        f"{failures}"
    )


# --- EX10: Persona Spectrum ---

def make_expert_exact_prompt(scenario_id: str) -> str:
    """精确领域专家 persona"""
    info = DOMAIN_INFO.get(scenario_id, {})
    expert = info.get("expert", "domain expert")
    return f"You are a {expert}. Solve this task using your specialized expertise."


def make_expert_adjacent_prompt(scenario_id: str) -> str:
    """相邻领域专家 persona"""
    info = DOMAIN_INFO.get(scenario_id, {})
    adjacent = info.get("adjacent", "related domain expert")
    return f"You are a {adjacent}. Apply your transferable skills to solve this task."


def make_expert_wrong_prompt(scenario_id: str) -> str:
    """错误领域专家 persona"""
    info = DOMAIN_INFO.get(scenario_id, {})
    wrong = info.get("wrong", "unrelated domain expert")
    return f"You are a {wrong}. Apply your analytical skills to solve this task."


def make_generic_senior_prompt(scenario_id: str) -> str:
    """通用高级工程师 persona"""
    return (
        "You are a senior software engineer with 20 years of experience. "
        "You excel at understanding new domains quickly and writing clean, correct code."
    )


def make_novice_prompt(scenario_id: str) -> str:
    """新手 persona"""
    info = DOMAIN_INFO.get(scenario_id, {})
    domain = info.get("domain", "this domain")
    return (
        f"You are a programming student who is learning about {domain} for the first time. "
        f"Be very careful and methodical. Double-check every step of your solution."
    )


# --- EX11: 负面知识密度（Failure Density） ---

def make_n_failures_prompt(scenario_id: str, n: int) -> str:
    """给 n 条失败警告"""
    info = DOMAIN_INFO.get(scenario_id, {})
    failures = info.get("failure_patterns", [])
    selected = failures[:n] if n <= len(failures) else failures
    if not selected:
        return ""

    failure_text = "\n".join(f"  {i+1}. {f}" for i, f in enumerate(selected))
    return (
        f"CRITICAL: Avoid these {len(selected)} documented failure patterns:\n\n"
        f"<failure-patterns>\n{failure_text}\n</failure-patterns>"
    )


# ── Trial 配置 ──

@dataclass
class EvoTrialConfig:
    scenario_id: str
    model: str
    experiment: str  # ex8, ex9, ex10, ex11
    condition: str
    run_id: int = 0

    @property
    def trial_key(self) -> str:
        return f"{self.scenario_id}__{self.model}__{self.experiment}__{self.condition}__r{self.run_id}"


# ── EX8 条件映射 ──
EX8_CONDITIONS = {
    "none":                 lambda sid: "",
    "memory_signals":       make_memory_signals_prompt,
    "memory_failures":      make_memory_failures_prompt,
    "memory_experience":    make_memory_experience_prompt,
    "exploration_persona":  make_exploration_persona_prompt,
    "exploration_objective": make_exploration_objective_prompt,
    "exploration_direction": make_exploration_direction_prompt,
    "exploration_full":     make_exploration_full_prompt,
    "gene_g3":              lambda sid: _get_gene_g3_prompt(sid),
}

# EX9 条件映射
EX9_CONDITIONS = {
    "none":                lambda sid: "",
    "correct_strategy":    make_correct_strategy_prompt,
    "failure_warnings":    make_failure_warnings_prompt,
    "failure_first":       make_failure_then_strategy_prompt,
    "strategy_first":      make_strategy_then_failure_prompt,
}

# EX10 条件映射
EX10_CONDITIONS = {
    "none":            lambda sid: "",
    "expert_exact":    make_expert_exact_prompt,
    "expert_adjacent": make_expert_adjacent_prompt,
    "expert_wrong":    make_expert_wrong_prompt,
    "generic_senior":  make_generic_senior_prompt,
    "novice":          make_novice_prompt,
}

# EX11 条件映射
EX11_CONDITIONS = {
    "0_failures":  lambda sid: "",
    "1_failure":   lambda sid: make_n_failures_prompt(sid, 1),
    "2_failures":  lambda sid: make_n_failures_prompt(sid, 2),
    "3_failures":  lambda sid: make_n_failures_prompt(sid, 3),
    "4_failures":  lambda sid: make_n_failures_prompt(sid, 4),
}


def _get_gene_g3_prompt(scenario_id: str) -> str:
    """获取标准 G3 Gene prompt（作为对照组）"""
    gene_path = GENES_DIR / f"{scenario_id}.json"
    if not gene_path.exists():
        return ""
    gene = json.loads(gene_path.read_text())
    text = serialize_gene(gene, "G3")
    return (
        "You are given the following strategic gene to guide your approach.\n"
        "The gene describes a high-level strategy — use it as directional guidance,\n"
        "not as implementation instructions.\n\n"
        f"<strategy-gene>\n{text}\n</strategy-gene>"
    )


def _load_gene(scenario_id: str) -> dict:
    """加载场景的 Gene JSON"""
    gene_path = GENES_DIR / f"{scenario_id}.json"
    if gene_path.exists():
        return json.loads(gene_path.read_text())
    return {}


def _get_skill_dir(scenario_id: str) -> Path:
    """获取场景的 skill 目录"""
    return SKILLS_DIR / scenario_id / "direct"


# --- EX12: 自我预判 (Self-Anticipation) ---

def make_self_anticipation_prompt(scenario_id: str) -> str:
    """让模型先预测自己可能犯的错误"""
    return (
        "Before writing code, take a moment to anticipate what mistakes "
        "you are most likely to make on this task. List 3-5 specific, "
        "concrete pitfalls you might fall into, then write your solution "
        "while actively avoiding them.\n\n"
        "Structure your response as:\n"
        "1. SELF-PREDICTION: List anticipated mistakes\n"
        "2. SOLUTION: Write the code, explicitly avoiding those mistakes"
    )


def make_rubber_duck_prompt(scenario_id: str) -> str:
    """橡皮鸭调试：先解释再编码"""
    info = DOMAIN_INFO.get(scenario_id, {})
    domain = info.get("domain", "this domain")
    return (
        f"Imagine you're explaining your approach to a colleague who knows nothing about {domain}. "
        "First, write a plain-English explanation of your solution strategy "
        "in 3-5 bullet points, then implement the code.\n\n"
        "The explanation should cover: what algorithm to use, what edge cases to handle, "
        "and what output format to produce."
    )


def make_test_first_prompt(scenario_id: str) -> str:
    """测试先行：先写测试再写代码"""
    return (
        "Use a test-first approach:\n"
        "1. First, write 3-5 assertion-based test cases that your solution must pass\n"
        "2. Then implement the solution that passes all your tests\n"
        "3. Include both your tests and solution in the final code\n\n"
        "Think about edge cases: empty input, single element, boundary values."
    )


def make_curated_failures_prompt(scenario_id: str) -> str:
    """精选失败案例（来自 DOMAIN_INFO + gene pitfalls）"""
    info = DOMAIN_INFO.get(scenario_id, {})
    failures = info.get("failure_patterns", [])
    gene = _load_gene(scenario_id)
    pitfalls = gene.get("pitfalls", [])
    all_failures = failures[:2] + pitfalls[:2]
    if not all_failures:
        return ""
    text = "\n".join(f"  {i+1}. {f}" for i, f in enumerate(all_failures))
    return (
        "These specific mistakes have been documented from previous attempts:\n\n"
        f"<curated-failures>\n{text}\n</curated-failures>\n\n"
        "Each has caused at least 30% failure rate. Internalize these before coding."
    )


EX12_CONDITIONS = {
    "none":               lambda sid: "",
    "self_anticipation":  make_self_anticipation_prompt,
    "rubber_duck":        make_rubber_duck_prompt,
    "test_first":         make_test_first_prompt,
    "curated_failures":   make_curated_failures_prompt,
    "gene_g3":            lambda sid: _get_gene_g3_prompt(sid),
}


# --- EX13: 框架效应 (Framing Effect) ---

def make_imperative_prompt(scenario_id: str) -> str:
    """命令式框架"""
    gene = _load_gene(scenario_id)
    strategy = gene.get("strategy", [])
    if not strategy:
        return ""
    steps = "\n".join(f"  {i+1}. {s}" for i, s in enumerate(strategy))
    return f"DO the following steps exactly:\n\n{steps}"


def make_suggestive_prompt(scenario_id: str) -> str:
    """建议式框架"""
    gene = _load_gene(scenario_id)
    strategy = gene.get("strategy", [])
    if not strategy:
        return ""
    steps = "\n".join(f"  - Consider: {s}" for s in strategy)
    return f"You might find the following suggestions helpful:\n\n{steps}"


def make_warning_prompt(scenario_id: str) -> str:
    """警告式框架"""
    info = DOMAIN_INFO.get(scenario_id, {})
    failures = info.get("failure_patterns", [])
    if not failures:
        return ""
    text = "\n".join(f"  ⚠ {f}" for f in failures)
    return f"WARNING — Past solutions have failed due to:\n\n{text}\n\nDo NOT make these mistakes."


def make_teaching_prompt(scenario_id: str) -> str:
    """教学式框架"""
    gene = _load_gene(scenario_id)
    summary = gene.get("summary", "")
    strategy = gene.get("strategy", [])
    if not strategy:
        return ""
    steps = "\n".join(f"  Step {i+1}: {s}" for i, s in enumerate(strategy))
    return (
        f"Let me teach you the correct approach to this problem.\n\n"
        f"The key insight is: {summary}\n\n"
        f"Here's the step-by-step method:\n{steps}\n\n"
        f"Understanding WHY each step matters will help you implement correctly."
    )


def make_socratic_prompt(scenario_id: str) -> str:
    """苏格拉底式框架（用问题引导）"""
    gene = _load_gene(scenario_id)
    keywords = gene.get("signals_match", gene.get("keywords", []))
    summary = gene.get("summary", "")
    return (
        "Before coding, ask yourself:\n"
        f"  - What domain concepts ({', '.join(keywords[:4])}) are relevant here?\n"
        f"  - What is the core algorithmic challenge? (Hint: {summary})\n"
        "  - What edge cases could break my solution?\n"
        "  - What common mistakes do people make in this domain?\n\n"
        "Answer each question, then write your solution."
    )


EX13_CONDITIONS = {
    "none":       lambda sid: "",
    "imperative": make_imperative_prompt,
    "suggestive": make_suggestive_prompt,
    "warning":    make_warning_prompt,
    "teaching":   make_teaching_prompt,
    "socratic":   make_socratic_prompt,
}


# --- EX14: 失败真假 (Failure Authenticity) ---

def make_real_failures_prompt(scenario_id: str) -> str:
    """真实失败案例"""
    return make_failure_warnings_prompt(scenario_id)


def make_plausible_fake_prompt(scenario_id: str) -> str:
    """看起来合理但错误的失败警告"""
    info = DOMAIN_INFO.get(scenario_id, {})
    domain = info.get("domain", "this domain")
    # 生成看起来合理但实际误导的建议
    return (
        f"WARNING: Common mistakes in {domain} tasks:\n\n"
        f"<failure-warnings>\n"
        f"  1. Always normalize all input data to [0,1] range before any computation\n"
        f"  2. Use float32 instead of float64 to avoid numerical precision issues\n"
        f"  3. Sort all output arrays in descending order for consistency\n"
        f"  4. Always add a small epsilon (1e-10) to all denominators\n"
        f"</failure-warnings>\n\n"
        "Avoid these mistakes in your implementation."
    )


def make_generic_warnings_prompt(scenario_id: str) -> str:
    """通用编程警告（与领域无关）"""
    return (
        "WARNING: Common coding mistakes to avoid:\n\n"
        "<failure-warnings>\n"
        "  1. Not handling edge cases (empty input, single element)\n"
        "  2. Off-by-one errors in loop bounds\n"
        "  3. Not closing file handles properly\n"
        "  4. Integer overflow in intermediate calculations\n"
        "</failure-warnings>"
    )


def make_cross_domain_failures_prompt(scenario_id: str) -> str:
    """来自错误领域的失败案例"""
    info = DOMAIN_INFO.get(scenario_id, {})
    domain = info.get("domain", "")
    # 找一个不同领域的失败案例
    for sid, d_info in DOMAIN_INFO.items():
        if d_info.get("domain", "") != domain and d_info.get("failure_patterns"):
            failures = d_info["failure_patterns"]
            text = "\n".join(f"  {i+1}. {f}" for i, f in enumerate(failures))
            return (
                f"WARNING: These failure patterns have been documented:\n\n"
                f"<failure-warnings>\n{text}\n</failure-warnings>\n\n"
                "Avoid these mistakes."
            )
    return ""


def make_absurd_warnings_prompt(scenario_id: str) -> str:
    """荒谬警告（测试信号效应 vs 内容效应）"""
    return (
        "⚠ CRITICAL WARNING — FAILURE MODES DETECTED ⚠\n\n"
        "<failure-warnings severity=\"critical\">\n"
        "  1. CAUTION: The function may spontaneously reverse variable names\n"
        "  2. ALERT: Indentation errors have been known to cause memory leaks\n"
        "  3. WARNING: Using more than 3 list comprehensions will corrupt the output\n"
        "  4. DANGER: The letter 'x' in variable names triggers undefined behavior\n"
        "</failure-warnings>\n\n"
        "These warnings are based on extensive testing. Proceed with extreme caution."
    )


EX14_CONDITIONS = {
    "none":             lambda sid: "",
    "real_failures":    make_real_failures_prompt,
    "plausible_fake":   make_plausible_fake_prompt,
    "generic_warnings": make_generic_warnings_prompt,
    "cross_domain":     make_cross_domain_failures_prompt,
    "absurd_warnings":  make_absurd_warnings_prompt,
}


# --- EX15: 组合饱和 (Combination Saturation) ---

EX15_CONDITIONS = {
    "none":                     lambda sid: "",
    "novice_only":              make_novice_prompt,
    "warning_only":             make_failure_warnings_prompt,
    "failures_only":            make_memory_failures_prompt,
    "novice_warning":           lambda sid: make_novice_prompt(sid) + "\n\n" + make_failure_warnings_prompt(sid),
    "novice_failures":          lambda sid: make_novice_prompt(sid) + "\n\n" + make_memory_failures_prompt(sid),
    "warning_failures":         lambda sid: make_failure_warnings_prompt(sid) + "\n\n" + make_memory_failures_prompt(sid),
    "novice_warning_failures":  lambda sid: make_novice_prompt(sid) + "\n\n" + make_failure_warnings_prompt(sid) + "\n\n" + make_memory_failures_prompt(sid),
}


# --- EX16: 利害框架 (Stakes Framing) ---

def make_high_stakes_prompt(scenario_id: str) -> str:
    """高利害框架"""
    return (
        "IMPORTANT: This code will be deployed in a production system that processes "
        "real scientific data. Errors will cause incorrect research conclusions. "
        "Write with the rigor of code that will be peer-reviewed and published. "
        "Every edge case matters. Every numerical precision issue matters."
    )


def make_easy_explicit_prompt(scenario_id: str) -> str:
    """显式标记为简单任务"""
    return (
        "This is a straightforward task that most competent developers can solve quickly. "
        "The solution should be clean and direct — don't overthink it. "
        "Focus on getting the basics right and matching the expected output format."
    )


def make_hard_explicit_prompt(scenario_id: str) -> str:
    """显式标记为困难任务"""
    info = DOMAIN_INFO.get(scenario_id, {})
    domain = info.get("domain", "this domain")
    return (
        f"NOTE: This is a challenging task that requires deep expertise in {domain}. "
        "Most first attempts fail due to subtle domain-specific issues. "
        "Take your time, think carefully about the methodology, and double-check "
        "all computations before finalizing your solution."
    )


def make_competitive_prompt(scenario_id: str) -> str:
    """竞争框架"""
    return (
        "You are competing against other AI models to solve this task. "
        "Your solution will be benchmarked against GPT-5, Claude, and Gemini. "
        "Aim for the highest possible test pass rate. "
        "A perfect score means you outperform all competitors."
    )


def make_low_stakes_prompt(scenario_id: str) -> str:
    """低利害框架"""
    return (
        "This is just a quick prototype — it doesn't need to be perfect. "
        "Write a reasonable solution that handles the main cases. "
        "Don't worry about edge cases or performance optimization."
    )


EX16_CONDITIONS = {
    "none":          lambda sid: "",
    "high_stakes":   make_high_stakes_prompt,
    "easy_explicit": make_easy_explicit_prompt,
    "hard_explicit": make_hard_explicit_prompt,
    "competitive":   make_competitive_prompt,
    "low_stakes":    make_low_stakes_prompt,
}


# --- EX17: 格式对比 (Format Comparison) ---

def make_evomap_structured_prompt(scenario_id: str) -> str:
    """EvoMap 结构化 XML 格式"""
    gene = _load_gene(scenario_id)
    info = DOMAIN_INFO.get(scenario_id, {})
    keywords = gene.get("signals_match", gene.get("keywords", []))
    summary = gene.get("summary", "")
    strategy = gene.get("strategy", [])
    failures = info.get("failure_patterns", [])

    steps_xml = "\n".join(f"    <step>{s}</step>" for s in strategy)
    fail_xml = "\n".join(f"    <pattern>{f}</pattern>" for f in failures[:3])
    kw_text = ", ".join(keywords[:6])

    return (
        f'<evomap-gene format="structured" version="2.0">\n'
        f'  <domain-signals>{kw_text}</domain-signals>\n'
        f'  <summary>{summary}</summary>\n'
        f'  <strategy>\n{steps_xml}\n  </strategy>\n'
        f'  <failure-patterns>\n{fail_xml}\n  </failure-patterns>\n'
        f'</evomap-gene>'
    )


def make_raw_paragraph_prompt(scenario_id: str) -> str:
    """纯文本段落格式（无结构）"""
    gene = _load_gene(scenario_id)
    info = DOMAIN_INFO.get(scenario_id, {})
    keywords = gene.get("signals_match", gene.get("keywords", []))
    summary = gene.get("summary", "")
    strategy = gene.get("strategy", [])
    failures = info.get("failure_patterns", [])

    strategy_text = ". ".join(strategy)
    failures_text = ". ".join(failures[:3])
    return (
        f"Key concepts for this task include {', '.join(keywords[:6])}. "
        f"{summary} "
        f"The recommended approach is: {strategy_text}. "
        f"Common mistakes to avoid: {failures_text}."
    )


def make_bullet_list_prompt(scenario_id: str) -> str:
    """项目符号列表格式"""
    gene = _load_gene(scenario_id)
    info = DOMAIN_INFO.get(scenario_id, {})
    keywords = gene.get("signals_match", gene.get("keywords", []))
    summary = gene.get("summary", "")
    strategy = gene.get("strategy", [])
    failures = info.get("failure_patterns", [])

    parts = [f"Keywords: {', '.join(keywords[:6])}", f"Goal: {summary}"]
    parts.extend(f"• {s}" for s in strategy)
    parts.extend(f"⚠ {f}" for f in failures[:3])
    return "\n".join(parts)


def make_markdown_sections_prompt(scenario_id: str) -> str:
    """Markdown 章节格式"""
    gene = _load_gene(scenario_id)
    info = DOMAIN_INFO.get(scenario_id, {})
    keywords = gene.get("signals_match", gene.get("keywords", []))
    summary = gene.get("summary", "")
    strategy = gene.get("strategy", [])
    failures = info.get("failure_patterns", [])

    steps = "\n".join(f"{i+1}. {s}" for i, s in enumerate(strategy))
    warns = "\n".join(f"- {f}" for f in failures[:3])
    return (
        f"## Domain Keywords\n{', '.join(keywords[:6])}\n\n"
        f"## Summary\n{summary}\n\n"
        f"## Strategy\n{steps}\n\n"
        f"## Pitfalls\n{warns}"
    )


def make_keyword_dump_prompt(scenario_id: str) -> str:
    """仅关键词堆砌（最低信息量）"""
    gene = _load_gene(scenario_id)
    info = DOMAIN_INFO.get(scenario_id, {})
    keywords = gene.get("signals_match", gene.get("keywords", []))
    signals = info.get("signals", [])
    all_kw = list(dict.fromkeys(keywords + signals))[:12]
    return f"Relevant: {' | '.join(all_kw)}"


EX17_CONDITIONS = {
    "none":               lambda sid: "",
    "evomap_structured":  make_evomap_structured_prompt,
    "raw_paragraph":      make_raw_paragraph_prompt,
    "bullet_list":        make_bullet_list_prompt,
    "markdown_sections":  make_markdown_sections_prompt,
    "keyword_dump":       make_keyword_dump_prompt,
}


# --- EX18: 进化循环 (Evolution Loop) ---
# 注意: retry 条件需要二轮 API 调用，在 run_single_trial 中特殊处理

EX18_CONDITIONS = {
    "none":            lambda sid: "",
    "single_shot_evomap": lambda sid: _get_gene_g3_prompt(sid),
    "retry_blind":     lambda sid: "__RETRY_BLIND__",
    "retry_errors":    lambda sid: "__RETRY_ERRORS__",
    "retry_evomap":    lambda sid: "__RETRY_EVOMAP__",
}


# --- EX19: vs PE 方法 (vs Prompt Engineering) ---

def make_chatgpt_system_prompt(scenario_id: str) -> str:
    """ChatGPT 系统提示风格"""
    return (
        "You are a helpful assistant that writes Python code. "
        "When given a task, analyze it carefully and provide a complete, "
        "working solution. Focus on correctness and readability."
    )


def make_careful_prompt(scenario_id: str) -> str:
    """谨慎提示"""
    return (
        "Think step by step. Break down the problem into smaller parts. "
        "Consider edge cases. Write clean, well-structured code. "
        "Test your logic mentally before writing. "
        "Make sure all outputs match the required format exactly."
    )


def make_expert_cot_prompt(scenario_id: str) -> str:
    """专家思维链"""
    info = DOMAIN_INFO.get(scenario_id, {})
    expert = info.get("expert", "domain expert")
    domain = info.get("domain", "this domain")
    return (
        f"You are a {expert}. Think through this problem as an expert would:\n"
        f"1. First, identify the core {domain} challenge\n"
        "2. Then, plan your algorithmic approach\n"
        "3. Consider what could go wrong\n"
        "4. Implement with attention to domain-specific details\n"
        "5. Verify your solution handles edge cases\n\n"
        "Show your reasoning, then provide the complete solution."
    )


def make_stackoverflow_hints_prompt(scenario_id: str) -> str:
    """StackOverflow 风格提示（代码片段 + 注意事项）"""
    gene = _load_gene(scenario_id)
    keywords = gene.get("signals_match", gene.get("keywords", []))
    strategy = gene.get("strategy", [])
    return (
        f"Common SO answers for [{', '.join(keywords[:4])}] tasks suggest:\n\n"
        + "\n".join(f"  > {s}" for s in strategy[:3])
        + "\n\nNote: Check accepted answers for version compatibility."
    )


def make_skill_full_prompt(scenario_id: str) -> str:
    """完整 Skill 包"""
    from gene_injector import inject_skill_full
    skill_dir = _get_skill_dir(scenario_id)
    return inject_skill_full(skill_dir)


def make_evomap_optimized_prompt(scenario_id: str) -> str:
    """EvoMap 优化组合: Gene G3 + 失败经验 + 领域信号"""
    gene_prompt = _get_gene_g3_prompt(scenario_id)
    failures_prompt = make_memory_failures_prompt(scenario_id)
    return gene_prompt + "\n\n" + failures_prompt


EX19_CONDITIONS = {
    "none":               lambda sid: "",
    "chatgpt_system":     make_chatgpt_system_prompt,
    "careful_prompt":     make_careful_prompt,
    "expert_cot":         make_expert_cot_prompt,
    "stackoverflow_hints": make_stackoverflow_hints_prompt,
    "skill_full":         make_skill_full_prompt,
    "evomap_optimized":   make_evomap_optimized_prompt,
}


# --- EX20: Gene 复用 (Gene Reuse) ---

def make_exact_gene_prompt(scenario_id: str) -> str:
    """精确匹配 Gene"""
    return _get_gene_g3_prompt(scenario_id)


def make_sibling_gene_prompt(scenario_id: str) -> str:
    """同领域兄弟 Gene（不同场景但同领域）"""
    gene = _load_gene(scenario_id)
    domain = gene.get("domain", "")
    # 找同领域的其他场景
    for sid in GENE_SENSITIVE_SCENARIOS:
        if sid == scenario_id:
            continue
        other = _load_gene(sid)
        if other.get("domain", "") == domain:
            text = serialize_gene(other, "G3")
            return (
                "You are given a strategic gene from a related task in the same domain.\n"
                "Adapt the strategy to the specific requirements of your task.\n\n"
                f"<strategy-gene source=\"sibling\">\n{text}\n</strategy-gene>"
            )
    # 如果找不到同领域，用相邻场景
    return _get_gene_g3_prompt(scenario_id)


def make_cousin_gene_prompt(scenario_id: str) -> str:
    """远亲 Gene（不同领域但有结构类比）"""
    info = DOMAIN_INFO.get(scenario_id, {})
    domain = info.get("domain", "")
    # 找一个不同领域的场景
    for sid in GENE_SENSITIVE_SCENARIOS:
        if sid == scenario_id:
            other_info = DOMAIN_INFO.get(sid, {})
            if other_info.get("domain", "") != domain:
                other = _load_gene(sid)
                if other:
                    text = serialize_gene(other, "G3")
                    return (
                        "You are given a strategic gene from a different domain.\n"
                        "Extract any transferable patterns and adapt them to your task.\n\n"
                        f"<strategy-gene source=\"cousin\">\n{text}\n</strategy-gene>"
                    )
    # 遍历找不同领域
    for sid, d_info in DOMAIN_INFO.items():
        if d_info.get("domain", "") != domain and sid != scenario_id:
            other = _load_gene(sid)
            if other:
                text = serialize_gene(other, "G3")
                return (
                    "You are given a strategic gene from a different domain.\n"
                    "Extract any transferable patterns and adapt them to your task.\n\n"
                    f"<strategy-gene source=\"cousin\">\n{text}\n</strategy-gene>"
                )
    return ""


def make_generic_gene_prompt(scenario_id: str) -> str:
    """通用泛化 Gene（剥离领域细节）"""
    gene = _load_gene(scenario_id)
    strategy = gene.get("strategy", [])
    if not strategy:
        return ""
    # 泛化策略：移除领域术语
    generic_steps = []
    for s in strategy:
        generic_steps.append(
            s.replace("regression", "modeling")
            .replace("spectrum", "signal")
            .replace("MIDI", "data")
        )
    steps = "\n".join(f"  {i+1}. {s}" for i, s in enumerate(generic_steps))
    return (
        "Generic strategy guidance:\n\n"
        f"<strategy-gene source=\"generic\">\n{steps}\n</strategy-gene>"
    )


def make_skill_exact_prompt(scenario_id: str) -> str:
    """精确匹配 SKILL.md（L1 对照）"""
    from gene_injector import inject_gene
    skill_dir = _get_skill_dir(scenario_id)
    return inject_gene({}, "L1", skill_dir)


EX20_CONDITIONS = {
    "none":         lambda sid: "",
    "exact_gene":   make_exact_gene_prompt,
    "sibling_gene": make_sibling_gene_prompt,
    "cousin_gene":  make_cousin_gene_prompt,
    "generic_gene": make_generic_gene_prompt,
    "skill_exact":  make_skill_exact_prompt,
}


# --- EX21: 生态对比 (Ecology Comparison) ---

def make_skill_raw_prompt(scenario_id: str) -> str:
    """原始 SKILL.md（无增强）"""
    from gene_injector import _inject_skill_l1
    return _inject_skill_l1(_get_skill_dir(scenario_id))


def make_skill_plus_examples_prompt(scenario_id: str) -> str:
    """SKILL.md + 示例代码"""
    skill_dir = _get_skill_dir(scenario_id)
    skill_text = make_skill_raw_prompt(scenario_id)
    examples_path = skill_dir / "references" / "examples.md"
    if examples_path.exists():
        examples = examples_path.read_text()
        return skill_text + f"\n\n<examples>\n{examples}\n</examples>"
    return skill_text


def make_evomap_gene_only_prompt(scenario_id: str) -> str:
    """仅 Gene（不含记忆或失败）"""
    return _get_gene_g3_prompt(scenario_id)


def make_evomap_memory_only_prompt(scenario_id: str) -> str:
    """仅记忆信号（不含 Gene 策略）"""
    return make_memory_signals_prompt(scenario_id)


def make_evomap_curated_prompt(scenario_id: str) -> str:
    """完整 EvoMap 策划组合: Gene + 失败 + 记忆"""
    gene_p = _get_gene_g3_prompt(scenario_id)
    fail_p = make_memory_failures_prompt(scenario_id)
    sig_p = make_memory_signals_prompt(scenario_id)
    return gene_p + "\n\n" + fail_p + "\n\n" + sig_p


EX21_CONDITIONS = {
    "none":               lambda sid: "",
    "skill_raw":          make_skill_raw_prompt,
    "skill_plus_examples": make_skill_plus_examples_prompt,
    "evomap_gene_only":   make_evomap_gene_only_prompt,
    "evomap_memory_only": make_evomap_memory_only_prompt,
    "evomap_curated":     make_evomap_curated_prompt,
}


# --- EX22: Skill 归因 (Skill Attribution) ---

EX22_CONDITIONS = {
    "none":                lambda sid: "",
    "skill_overview":      lambda sid: _inject_skill_section_wrapped(sid, "overview"),
    "skill_workflow":      lambda sid: _inject_skill_section_wrapped(sid, "workflow"),
    "skill_pitfalls":      lambda sid: _inject_skill_section_wrapped(sid, "pitfalls"),
    "skill_error_handling": lambda sid: _inject_skill_section_wrapped(sid, "error_handling"),
    "skill_quick_ref":     lambda sid: _inject_skill_section_wrapped(sid, "quick_reference"),
    "gene_g3":             lambda sid: _get_gene_g3_prompt(sid),
}

def _inject_skill_section_wrapped(scenario_id: str, section: str) -> str:
    """注入单个 SKILL.md 章节"""
    from gene_injector import inject_skill_section
    return inject_skill_section(_get_skill_dir(scenario_id), section)


# --- EX23: 截断效应 (Truncation Effect) ---

EX23_CONDITIONS = {
    "none":            lambda sid: "",
    "pitfalls_short":  lambda sid: _inject_skill_truncated_wrapped(sid, "pitfalls", 3),
    "workflow_short":  lambda sid: _inject_skill_truncated_wrapped(sid, "workflow", 3),
    "mixed_short":     lambda sid: (
        _inject_skill_truncated_wrapped(sid, "pitfalls", 2) + "\n\n"
        + _inject_skill_truncated_wrapped(sid, "workflow", 2)
    ),
    "gene_g3":         lambda sid: _get_gene_g3_prompt(sid),
}

def _inject_skill_truncated_wrapped(scenario_id: str, section: str, max_lines: int) -> str:
    """注入截断版章节"""
    from gene_injector import inject_skill_truncated
    return inject_skill_truncated(_get_skill_dir(scenario_id), section, max_lines)


# --- EX24: 互补性 (Complementarity) ---

def make_gene_plus_examples_prompt(scenario_id: str) -> str:
    """Gene + 示例代码"""
    gene_p = _get_gene_g3_prompt(scenario_id)
    examples_path = _get_skill_dir(scenario_id) / "references" / "examples.md"
    if examples_path.exists():
        examples = examples_path.read_text()
        return gene_p + f"\n\n<reference-examples>\n{examples}\n</reference-examples>"
    return gene_p


def make_gene_plus_api_notes_prompt(scenario_id: str) -> str:
    """Gene + API 参考"""
    gene_p = _get_gene_g3_prompt(scenario_id)
    api_path = _get_skill_dir(scenario_id) / "references" / "api_notes.md"
    if api_path.exists():
        notes = api_path.read_text()
        return gene_p + f"\n\n<api-reference>\n{notes}\n</api-reference>"
    return gene_p


EX24_CONDITIONS = {
    "none":              lambda sid: "",
    "gene_alone":        lambda sid: _get_gene_g3_prompt(sid),
    "gene_plus_examples": make_gene_plus_examples_prompt,
    "gene_plus_api_notes": make_gene_plus_api_notes_prompt,
    "skill_full":        make_skill_full_prompt,
}


# --- EX25: 格式重包装 (Format Repackaging) ---

def make_pitfalls_raw_prompt(scenario_id: str) -> str:
    """原始 Markdown pitfalls"""
    from gene_injector import extract_skill_section
    text = extract_skill_section(_get_skill_dir(scenario_id), "pitfalls")
    if not text:
        return ""
    return f"Common pitfalls to avoid:\n\n{text}"


def make_pitfalls_xml_prompt(scenario_id: str) -> str:
    """Pitfalls 转 XML 格式"""
    from gene_injector import inject_pitfalls_as_xml
    return inject_pitfalls_as_xml(_get_skill_dir(scenario_id))


def make_pitfalls_warning_prompt(scenario_id: str) -> str:
    """Pitfalls 转警告框架"""
    from gene_injector import extract_skill_section
    text = extract_skill_section(_get_skill_dir(scenario_id), "pitfalls")
    if not text:
        return ""
    return (
        "⚠ CRITICAL WARNINGS — DO NOT IGNORE ⚠\n\n"
        f"{text}\n\n"
        "Each of these has caused >50% failure rate in past attempts."
    )


def make_memory_curated_prompt(scenario_id: str) -> str:
    """策划版记忆（人工精选，正+负）"""
    return make_memory_experience_prompt(scenario_id)


EX25_CONDITIONS = {
    "none":            lambda sid: "",
    "pitfalls_raw":    make_pitfalls_raw_prompt,
    "pitfalls_as_xml": make_pitfalls_xml_prompt,
    "pitfalls_warning": make_pitfalls_warning_prompt,
    "memory_curated":  make_memory_curated_prompt,
}


# --- EX26: 进化叙事 (Evolution Narrative) ---

def make_evolution_full_prompt(scenario_id: str) -> str:
    """完整进化事件叙事"""
    from gene_injector import inject_evolution_event
    gene = _load_gene(scenario_id)
    if not gene:
        return ""
    return inject_evolution_event(gene, scenario_id)


def make_gene_with_confidence_prompt(scenario_id: str) -> str:
    """Gene 附带置信度标注"""
    gene = _load_gene(scenario_id)
    text = serialize_gene(gene, "G3")
    return (
        "The following gene was evolved with high confidence (fitness: 0.85/1.0).\n"
        "Strategies marked as high-confidence have consistently produced passing solutions.\n\n"
        f"<strategy-gene confidence=\"high\">\n{text}\n</strategy-gene>"
    )


def make_capsule_style_prompt(scenario_id: str) -> str:
    """胶囊风格: 极简 one-liner"""
    gene = _load_gene(scenario_id)
    summary = gene.get("summary", "")
    keywords = gene.get("signals_match", gene.get("keywords", []))
    return f"[GENE] {summary} | Key: {', '.join(keywords[:4])}"


def make_failed_attempts_only_prompt(scenario_id: str) -> str:
    """仅失败尝试记录（不含成功策略）"""
    info = DOMAIN_INFO.get(scenario_id, {})
    failures = info.get("failure_patterns", [])
    gene = _load_gene(scenario_id)
    pitfalls = gene.get("pitfalls", [])
    all_fails = failures + pitfalls
    if not all_fails:
        return ""
    text = "\n".join(f"  Attempt failed: {f}" for f in all_fails)
    return (
        "Evolution log — failed attempts (no successful strategy found yet):\n\n"
        f"<evolution-failures>\n{text}\n</evolution-failures>\n\n"
        "Learn from these failures. Find your own path to success."
    )


EX26_CONDITIONS = {
    "none":                 lambda sid: "",
    "evolution_full":       make_evolution_full_prompt,
    "gene_with_confidence": make_gene_with_confidence_prompt,
    "capsule_style":        make_capsule_style_prompt,
    "failed_attempts_only": make_failed_attempts_only_prompt,
}


# --- EX27: 记忆来源 (Memory Source) ---

def make_pitfalls_auto_xml_prompt(scenario_id: str) -> str:
    """自动提取的 pitfalls（XML 格式）"""
    from gene_injector import inject_pitfalls_as_xml
    return inject_pitfalls_as_xml(_get_skill_dir(scenario_id))


def make_model_self_predict_prompt(scenario_id: str) -> str:
    """模型自预测的失败模式（模拟 — 用通用提示触发自预测）"""
    info = DOMAIN_INFO.get(scenario_id, {})
    domain = info.get("domain", "this domain")
    return (
        f"Before writing code for this {domain} task, predict the 3 most likely "
        "mistakes you would make. Then write your solution while actively "
        "avoiding those predicted mistakes.\n\n"
        "Format: First list predictions, then provide the full solution code."
    )


EX27_CONDITIONS = {
    "none":               lambda sid: "",
    "memory_curated":     make_memory_curated_prompt,
    "pitfalls_auto_xml":  make_pitfalls_auto_xml_prompt,
    "model_self_predict": make_model_self_predict_prompt,
}


# ── Trial 生成 ──

def _generate_trials(experiment: str, conditions: dict, models: list, scenarios: list) -> list:
    """通用 trial 生成器"""
    trials = []
    for m in models:
        for s in scenarios:
            for cond in conditions:
                trials.append(EvoTrialConfig(
                    scenario_id=s, model=m,
                    experiment=experiment, condition=cond,
                ))
    return trials


def generate_ex8_trials(models: list, scenarios: list) -> list:
    return _generate_trials("ex8", EX8_CONDITIONS, models, scenarios)

def generate_ex9_trials(models: list, scenarios: list) -> list:
    return _generate_trials("ex9", EX9_CONDITIONS, models, scenarios)

def generate_ex10_trials(models: list, scenarios: list) -> list:
    return _generate_trials("ex10", EX10_CONDITIONS, models, scenarios)

def generate_ex11_trials(models: list, scenarios: list) -> list:
    return _generate_trials("ex11", EX11_CONDITIONS, models, scenarios)

def generate_ex12_trials(models: list, scenarios: list) -> list:
    return _generate_trials("ex12", EX12_CONDITIONS, models, scenarios)

def generate_ex13_trials(models: list, scenarios: list) -> list:
    return _generate_trials("ex13", EX13_CONDITIONS, models, scenarios)

def generate_ex14_trials(models: list, scenarios: list) -> list:
    return _generate_trials("ex14", EX14_CONDITIONS, models, scenarios)

def generate_ex15_trials(models: list, scenarios: list) -> list:
    return _generate_trials("ex15", EX15_CONDITIONS, models, scenarios)

def generate_ex16_trials(models: list, scenarios: list) -> list:
    return _generate_trials("ex16", EX16_CONDITIONS, models, scenarios)

def generate_ex17_trials(models: list, scenarios: list) -> list:
    return _generate_trials("ex17", EX17_CONDITIONS, models, scenarios)

def generate_ex18_trials(models: list, scenarios: list) -> list:
    return _generate_trials("ex18", EX18_CONDITIONS, models, scenarios)

def generate_ex19_trials(models: list, scenarios: list) -> list:
    return _generate_trials("ex19", EX19_CONDITIONS, models, scenarios)

def generate_ex20_trials(models: list, scenarios: list) -> list:
    return _generate_trials("ex20", EX20_CONDITIONS, models, scenarios)

def generate_ex21_trials(models: list, scenarios: list) -> list:
    return _generate_trials("ex21", EX21_CONDITIONS, models, scenarios)

def generate_ex22_trials(models: list, scenarios: list) -> list:
    return _generate_trials("ex22", EX22_CONDITIONS, models, scenarios)

def generate_ex23_trials(models: list, scenarios: list) -> list:
    return _generate_trials("ex23", EX23_CONDITIONS, models, scenarios)

def generate_ex24_trials(models: list, scenarios: list) -> list:
    return _generate_trials("ex24", EX24_CONDITIONS, models, scenarios)

def generate_ex25_trials(models: list, scenarios: list) -> list:
    return _generate_trials("ex25", EX25_CONDITIONS, models, scenarios)

def generate_ex26_trials(models: list, scenarios: list) -> list:
    return _generate_trials("ex26", EX26_CONDITIONS, models, scenarios)

def generate_ex27_trials(models: list, scenarios: list) -> list:
    return _generate_trials("ex27", EX27_CONDITIONS, models, scenarios)


# ── 所有实验条件映射 ──

ALL_CONDITION_MAPS = {
    "ex8": EX8_CONDITIONS,
    "ex9": EX9_CONDITIONS,
    "ex10": EX10_CONDITIONS,
    "ex11": EX11_CONDITIONS,
    "ex12": EX12_CONDITIONS,
    "ex13": EX13_CONDITIONS,
    "ex14": EX14_CONDITIONS,
    "ex15": EX15_CONDITIONS,
    "ex16": EX16_CONDITIONS,
    "ex17": EX17_CONDITIONS,
    "ex18": EX18_CONDITIONS,
    "ex19": EX19_CONDITIONS,
    "ex20": EX20_CONDITIONS,
    "ex21": EX21_CONDITIONS,
    "ex22": EX22_CONDITIONS,
    "ex23": EX23_CONDITIONS,
    "ex24": EX24_CONDITIONS,
    "ex25": EX25_CONDITIONS,
    "ex26": EX26_CONDITIONS,
    "ex27": EX27_CONDITIONS,
}

# 实验分组
EXPERIMENT_GROUPS = {
    "phase2": ["ex8", "ex9", "ex10", "ex11", "ex12", "ex13"],
    "phase3": ["ex14", "ex15", "ex16"],
    "phase4": ["ex17", "ex18", "ex19", "ex20", "ex21"],
    "skillprobe": ["ex22", "ex23", "ex24", "ex25", "ex26", "ex27"],
}

# 实验描述
EXPERIMENT_NAMES = {
    "ex8": "Memory vs Exploration",
    "ex9": "Failure-Guided Learning",
    "ex10": "Persona Spectrum",
    "ex11": "Failure Density",
    "ex12": "Self-Anticipation",
    "ex13": "Framing Effect",
    "ex14": "Failure Authenticity",
    "ex15": "Combination Saturation",
    "ex16": "Stakes Framing",
    "ex17": "Format Comparison",
    "ex18": "Evolution Loop",
    "ex19": "vs PE Methods",
    "ex20": "Gene Reuse",
    "ex21": "Ecology Comparison",
    "ex22": "Skill Attribution",
    "ex23": "Truncation Effect",
    "ex24": "Complementarity",
    "ex25": "Format Repackaging",
    "ex26": "Evolution Narrative",
    "ex27": "Memory Source",
}

# 实验 trial 生成器
EXPERIMENT_GENERATORS = {
    "ex8": generate_ex8_trials,
    "ex9": generate_ex9_trials,
    "ex10": generate_ex10_trials,
    "ex11": generate_ex11_trials,
    "ex12": generate_ex12_trials,
    "ex13": generate_ex13_trials,
    "ex14": generate_ex14_trials,
    "ex15": generate_ex15_trials,
    "ex16": generate_ex16_trials,
    "ex17": generate_ex17_trials,
    "ex18": generate_ex18_trials,
    "ex19": generate_ex19_trials,
    "ex20": generate_ex20_trials,
    "ex21": generate_ex21_trials,
    "ex22": generate_ex22_trials,
    "ex23": generate_ex23_trials,
    "ex24": generate_ex24_trials,
    "ex25": generate_ex25_trials,
    "ex26": generate_ex26_trials,
    "ex27": generate_ex27_trials,
}


def get_system_prompt(trial: EvoTrialConfig) -> str:
    """根据实验条件生成系统提示"""
    cond_map = ALL_CONDITION_MAPS.get(trial.experiment, {})
    func = cond_map.get(trial.condition)
    if func:
        return func(trial.scenario_id)
    return ""


def run_evomap_experiment(trials: list, gemini_key: str, yunwu_key: str,
                          output_file: Path, dry_run: bool = False, n_threads: int = 1):
    """执行 evomap 实验（支持多线程并行）"""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import threading

    write_lock = threading.Lock()
    counter = {"done": 0, "errors": 0, "total": 0}

    print(f"\n{'DRY RUN — ' if dry_run else ''}Running {len(trials)} evomap trials ({n_threads} threads)")
    print(f"Output: {output_file}\n")

    # 加载已完成的 trials
    completed = set()
    if output_file.exists():
        for line in output_file.read_text().strip().split("\n"):
            if line:
                try:
                    completed.add(json.loads(line)["trial_key"])
                except (json.JSONDecodeError, KeyError):
                    pass
        print(f"  Resuming: {len(completed)} trials already completed\n")

    pending = [t for t in trials if t.trial_key not in completed]
    counter["total"] = len(pending)
    print(f"  Pending: {len(pending)} trials\n")

    if dry_run:
        for trial in pending:
            print(f"  {trial.model:16s} {trial.scenario_id:28s} {trial.condition:25s} (dry run)")
        return

    output_file.parent.mkdir(parents=True, exist_ok=True)

    def run_single_trial(trial: EvoTrialConfig) -> None:
        """执行单个 trial（线程安全）"""
        scenario_dir = SCENARIOS_DIR / trial.scenario_id
        task_path = scenario_dir / "task.md"
        if not task_path.exists():
            return

        task_desc = task_path.read_text().strip()
        task_desc += "\n\nWrite a complete, self-contained Python solution. Output ONLY the code inside a single ```python code block. Do not include explanations outside the code block."

        system_prompt = get_system_prompt(trial)

        # EX18 retry 条件：需要二轮 API 调用
        is_retry = system_prompt.startswith("__RETRY_")
        retry_mode = ""
        if is_retry:
            retry_mode = system_prompt  # __RETRY_BLIND__ / __RETRY_ERRORS__ / __RETRY_EVOMAP__
            system_prompt = _get_gene_g3_prompt(trial.scenario_id) if retry_mode == "__RETRY_EVOMAP__" else ""

        try:
            api_result = call_llm(trial.model, task_desc, system_prompt, yunwu_key, gemini_key)
        except Exception as e:
            _write_error_result(trial, system_prompt, str(e), output_file, write_lock, counter)
            return

        code = extract_python_code(api_result["response"])
        total_input = api_result.get("input_tokens", 0)
        total_output = api_result.get("output_tokens", 0)

        # EX18: 如果是 retry 条件，执行第二轮
        if is_retry and code:
            eval_r1 = evaluate_code(code, scenario_dir)
            if not eval_r1["passed"]:
                # 构建第二轮 prompt
                if retry_mode == "__RETRY_BLIND__":
                    retry_prompt = "Your previous attempt failed. Please try again with a different approach."
                elif retry_mode == "__RETRY_ERRORS__":
                    error_info = eval_r1.get("error_type", "test_failure")
                    retry_prompt = (
                        f"Your previous attempt failed with: {error_info}.\n"
                        "Here is your previous code:\n```python\n" + code + "\n```\n\n"
                        "Fix the issues and provide a corrected solution."
                    )
                else:  # __RETRY_EVOMAP__
                    retry_prompt = (
                        f"Your previous attempt failed. "
                        "Use the strategic gene provided earlier to guide your retry.\n\n"
                        "Here is your previous code:\n```python\n" + code + "\n```\n\n"
                        "Analyze what went wrong and provide a corrected solution."
                    )
                try:
                    r2 = call_llm(trial.model, task_desc + "\n\n" + retry_prompt,
                                  system_prompt, yunwu_key, gemini_key)
                    code2 = extract_python_code(r2["response"])
                    if code2:
                        code = code2
                    total_input += r2.get("input_tokens", 0)
                    total_output += r2.get("output_tokens", 0)
                except Exception:
                    pass  # 第二轮失败，使用第一轮结果

        if not code:
            result = {
                "trial_key": trial.trial_key,
                "trial_config": asdict(trial),
                "eval": {"passed": False, "n_pass": 0, "n_total": 0,
                         "pass_rate": 0, "error_type": "format_error"},
                "code_length": 0,
                "prompt_tokens": len(system_prompt) // 4,
                "input_tokens": total_input,
                "output_tokens": total_output,
            }
            status_str = "NO CODE"
        else:
            eval_result = evaluate_code(code, scenario_dir)
            result = {
                "trial_key": trial.trial_key,
                "trial_config": asdict(trial),
                "eval": eval_result,
                "code_length": len(code),
                "prompt_tokens": len(system_prompt) // 4,
                "input_tokens": total_input,
                "output_tokens": total_output,
            }
            if eval_result["passed"]:
                status_str = f"PASS ({eval_result['n_pass']}/{eval_result['n_total']})"
            else:
                status_str = f"FAIL ({eval_result.get('error_type', '?')})"

        with write_lock:
            with open(output_file, "a") as f:
                f.write(json.dumps(result, default=str) + "\n")
            counter["done"] += 1
            print(f"  [{counter['done']}/{counter['total']}] {trial.model:16s} {trial.scenario_id:28s} {trial.condition:25s} {status_str}")

    with ThreadPoolExecutor(max_workers=n_threads) as executor:
        futures = [executor.submit(run_single_trial, t) for t in pending]
        for f in as_completed(futures):
            try:
                f.result()
            except Exception as e:
                with write_lock:
                    counter["errors"] += 1
                    print(f"  Unexpected error: {e}")

    print(f"\n  Completed: {counter['done']}, Errors: {counter['errors']}")


def _write_error_result(trial, system_prompt, error_msg, output_file, write_lock, counter):
    """写入 API 错误结果（辅助函数）"""
    result = {
        "trial_key": trial.trial_key,
        "trial_config": asdict(trial),
        "eval": {"passed": False, "n_pass": 0, "n_total": 0,
                 "pass_rate": 0, "error_type": f"api_error: {error_msg}"},
        "code_length": 0,
        "prompt_tokens": len(system_prompt) // 4,
        "input_tokens": 0, "output_tokens": 0,
    }
    with write_lock:
        with open(output_file, "a") as f:
            f.write(json.dumps(result, default=str) + "\n")
        counter["errors"] += 1
        counter["done"] += 1
        print(f"  [{counter['done']}/{counter['total']}] {trial.model:16s} {trial.scenario_id:28s} {trial.condition:25s} API ERROR: {error_msg}")


# ── CLI ──

ALL_EXPERIMENT_IDS = list(EXPERIMENT_NAMES.keys())

def main():
    parser = argparse.ArgumentParser(
        description="EvoMap 实验：EX8-EX27 共 20 个实验",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
实验分组:
  phase2:    EX8-EX13 (记忆/探索/失败/角色/自我预判/框架)
  phase3:    EX14-EX16 (失败真假/组合饱和/利害框架)
  phase4:    EX17-EX21 (格式/进化/PE方法/复用/生态)
  skillprobe: EX22-EX27 (Skill归因/截断/互补/重包装/叙事/记忆来源)
""")
    parser.add_argument("--experiment",
                        choices=ALL_EXPERIMENT_IDS + ["all", "phase2", "phase3", "phase4", "skillprobe"],
                        default="all", help="Which experiment(s) to run")
    parser.add_argument("--models", type=str, default="gemini_pro,gemini_flash",
                        help="Comma-separated model list")
    parser.add_argument("--scenarios", type=str, default=None,
                        help="Override scenario list (comma-separated)")
    parser.add_argument("--gemini-key", type=str,
                        default=os.environ.get("GEMINI_API_KEY", ""),
                        help="Gemini API key")
    parser.add_argument("--yunwu-key", type=str,
                        default=os.environ.get("YUNWU_API_KEY", ""),
                        help="yunwu.ai API key")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print trial plan without executing")
    parser.add_argument("--output-dir", type=str, default=str(DATA_DIR),
                        help="Output directory")

    args = parser.parse_args()

    models = [m.strip() for m in args.models.split(",")]
    for m in models:
        if m not in MODEL_REGISTRY:
            parser.error(f"Unknown model: {m}")

    scenarios = (
        [s.strip() for s in args.scenarios.split(",")]
        if args.scenarios
        else GENE_SENSITIVE_SCENARIOS
    )

    output_dir = Path(args.output_dir)
    exp = args.experiment

    # 确定要运行的实验列表
    if exp == "all":
        experiments_to_run = ALL_EXPERIMENT_IDS
    elif exp in EXPERIMENT_GROUPS:
        experiments_to_run = EXPERIMENT_GROUPS[exp]
    else:
        experiments_to_run = [exp]

    all_trials = {}
    for ex_id in experiments_to_run:
        gen_func = EXPERIMENT_GENERATORS[ex_id]
        t = gen_func(models, scenarios)
        all_trials[ex_id] = t
        name = EXPERIMENT_NAMES.get(ex_id, ex_id)
        print(f"{ex_id.upper()} ({name}): {len(t)} trials")

    total = sum(len(t) for t in all_trials.values())
    print(f"\nTotal: {total} trials across {len(all_trials)} experiments")

    if args.dry_run:
        print("\n--- Dry Run Summary ---")
        for name, trials in all_trials.items():
            by_cond = Counter(t.condition for t in trials)
            print(f"\n{name}:")
            for cond, c in sorted(by_cond.items()):
                print(f"  {cond:25s}: {c}")
        return

    # 逐实验执行
    for name, trials in all_trials.items():
        out_file = output_dir / f"evomap_{name}_results.jsonl"
        print(f"\n{'='*60}")
        print(f"Running {name} ({EXPERIMENT_NAMES.get(name, '')})")
        print(f"{'='*60}")
        run_evomap_experiment(
            trials, args.gemini_key, args.yunwu_key, out_file, args.dry_run
        )

    print(f"\nAll experiments done! Results in {output_dir}/evomap_*.jsonl")


if __name__ == "__main__":
    main()
