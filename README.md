# Configuration Sensitivity and Conditional Reliability in Wastewater Inflow Volume Forecasting: A Two-Site Open-Data Audit

**Viet Nam Tran**
Faculty of Environment, Van Lang University, Ho Chi Minh City, Vietnam

| Item | Detail |
|:-----|:-------|
| Version | v0.2.0 (10 November 2026) |
| Code license | [MIT](LICENSE) |
| Data licenses | [CC BY-NC 4.0 (Danish) / CC BY 4.0 (German)](DATA_LICENSE.md) |
| Python | 3.11+ |
| Reproduction | Deterministic, CI-verified |

---

## Overview

This repository is the complete research compendium for an open-science study of 12-hour cumulative wastewater inflow forecasting. The work audits configuration sensitivity and prediction interval reliability across two independently sourced treatment plants: a Danish WWTP (anonymized, combined sewage) and the Koeln-Weiden plant in Germany.

All analysis code, data download scripts, verification suites, manuscript sources and publication figures are included. Every numerical result in the manuscript can be reproduced from archived public data with a single sequence of commands, and the CI workflow verifies this on every push.

### Key findings

- **Configuration sensitivity.** Loss function and annual predictor choices reversed the primary benchmark ranking among gradient boosting models, demonstrating that model comparisons on open data require configuration audits.
- **Site-dependent meteorological value.** Historical rainfall improved forecast accuracy at the German site but not consistently across Danish temporal origins, indicating that meteorological predictor value cannot be assumed to transfer.
- **Conditional reliability gap.** Nominal 90% prediction intervals achieved near-nominal aggregate coverage (83.7--92.6%) but covered only 21.0--39.3% of high-volume windows, revealing that aggregate coverage statistics mask hydraulic-tail risk.
- **Rolling calibration trade-off.** Maturity-aware rolling residual calibration improved Danish aggregate coverage but reduced German coverage, suggesting that adaptive interval methods require site-specific evaluation.
- **Exact computational reproduction.** 46 CSV tables (34 Danish + 12 German) are reproduced with maximum absolute numeric difference of 0.0 across two independent clean-environment runs.

---

## Reproduction

### Prerequisites

- Python 3.11 or later
- Internet access (for initial data download from Zenodo)
- Approximately 200 MB disk space for source data and results

### Step-by-step instructions

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux / macOS:
source .venv/bin/activate

# 2. Install pinned dependencies
pip install -r requirements.txt

# 3. Download and verify Danish source data from Zenodo
python download_data.py

# 4. Run the main Danish analysis (produces 34 CSVs in results/)
python run_analysis.py

# 5. Verify Danish results against reference outputs
python verify_results.py --reference results/

# 6. Download German data and run external-site analysis (12 CSVs in external_results/)
python external_site.py --download

# 7. Verify German results
python verify_external.py --results external_results/

# 8. Render publication figures
python make_figures.py --results results/ --figures figures/

# 9. (Optional) Build the manuscript PDF and HTML
pip install -r requirements-docs.txt
python paper/build_paper.py paper/manuscript.md paper/manuscript.pdf
```

### Continuous integration

The GitHub Actions workflow ([`.github/workflows/reproduce.yml`](.github/workflows/reproduce.yml)) executes the Danish analysis pipeline on every push, pull request and manual dispatch. It installs dependencies from the clean-environment lock file, downloads data, runs the analysis, verifies outputs and uploads the reproduced results as a build artifact.

### Verification

The verification suite performs the following checks:

- Byte-level comparison of all CSV outputs against reference tables
- SHA-256 checksum validation of downloaded source archives
- Structural integrity checks (row counts, column names, data types)
- Numeric difference tolerance of exactly 0.0 (no floating-point drift)
- Fail-closed design: missing files, empty baselines or any numeric discrepancy cause hard failure

See [`reproduction.json`](reproduction.json) for the full machine-readable audit log.

---

## Repository Structure

```
.
├── README.md                        # This file
├── LICENSE                          # MIT (code only)
├── DATA_LICENSE.md                  # Data licensing terms
├── CITATION.cff                     # Machine-readable citation
├── CHANGELOG.md                     # Version history
├── PROTOCOL.md                      # Pre-analysis protocol
├── requirements.txt                 # Pinned dependencies
├── requirements-clean-lock.txt      # Clean-environment lock
├── SHA256SUMS.txt                   # File integrity checksums
├── reproduction.json                # Reproduction audit log
├── supplementary_v0.2.0.zip         # Complete release archive
│
├── paper/                           # Manuscript
│   ├── manuscript.md                #   Markdown source (v0.2.0)
│   ├── manuscript.pdf               #   Rendered PDF
│   ├── manuscript.html              #   Rendered HTML
│   ├── references.bib               #   BibTeX references
│   └── build_paper.py               #   PDF/HTML renderer
│
├── figures/                         # Publication figures
│   ├── Figure_1_timeline.*          #   Data timeline and partitions
│   ├── Figure_2_primary_accuracy.*  #   Primary accuracy comparison
│   ├── Figure_3_temporal_origins.*  #   Temporal origin sensitivity
│   ├── Figure_4_interval_reliability.* # Interval coverage analysis
│   └── Figure_5_episodes.*          #   High-volume episode diagnostics
│
├── data/                            # Danish source data (downloaded via script)
├── external_data/                   # German source data (downloaded via script)
│
├── results/                         # Main Danish analysis outputs (34 CSVs)
├── external_results/                # German site outputs (12 CSVs)
│
├── sources/                         # Data provenance metadata
├── verification/                    # Reproduction verification
│
├── docs/                            # Extended documentation
│   ├── PROTOCOL_v0.2.0.md           #   Version-stamped protocol
│   ├── PROTOCOL_DEVIATIONS.md       #   Protocol deviations register
│   ├── EXTERNAL_SITE_PROTOCOL.md    #   German site protocol
│   ├── RESPONSE_TO_AUDIT_VI.md      #   Response to audit findings
│   ├── LIMITATIONS_RESOLVED_VI.md   #   Resolved limitations
│   ├── LITERATURE_MATRIX.md         #   Literature comparison matrix
│   ├── SUPERVISOR_NOTE_VI.md        #   Supervisor note
│   ├── audit_resolution_register.csv#   Audit resolution register
│   └── claim_evidence_map.csv       #   Claim-to-evidence map
│
├── run_analysis.py                  # Main Danish analysis
├── external_site.py                 # German site analysis
├── download_data.py                 # Data downloader with checksum verification
├── make_figures.py                  # Figure renderer
├── verify_results.py                # Main verification suite
├── verify_external.py               # German verification suite
├── compare_reproduction.py          # Cross-run comparator
├── bootstrap_diagnostic.py          # Synthetic bootstrap validation
├── configuration_sensitivity.py     # Loss/annual sensitivity analysis
│
└── .github/workflows/reproduce.yml  # CI reproduction workflow
```

---

## Data Provenance

This study uses two independently archived public datasets. Source data are not redistributed; they are downloaded at analysis time with checksum verification.

### Danish WWTP

| Field | Value |
|:------|:------|
| Source | DHI, *Inflow to a Waste Water Treatment Plant: observations and processed data* |
| DOI | [10.5281/zenodo.15301164](https://doi.org/10.5281/zenodo.15301164) |
| License | CC BY-NC 4.0 |
| Records | 9,868 hourly flow observations; meteorological variables from the Danish Meteorological Institute |
| Period | November 2023 -- February 2025 |
| Download | `python download_data.py` |

### Koeln-Weiden, Germany

| Field | Value |
|:------|:------|
| Source | Sonnenschein, B. and Ziel, F. (2022), *Wastewater Treatment Plant Inflow Rate, Network Water Levels and Rain Rate for Koeln Weiden, Germany* |
| DOI | [10.5281/zenodo.6992694](https://doi.org/10.5281/zenodo.6992694) |
| License | CC BY 4.0 |
| Period | 2017--2019 |
| Download | `python external_site.py --download` |

Both datasets are accessed via Zenodo and verified against provider checksums. The Danish CC BY-NC 4.0 restriction does not relicense the independent German source. Users must respect both datasets' distinct license conditions. See [`DATA_LICENSE.md`](DATA_LICENSE.md) for full terms.

---

## Figures

All figures are generated deterministically from the analysis outputs and are available in PDF, PNG and SVG formats in the [`figures/`](figures/) directory.

| Figure | Description |
|:-------|:------------|
| Figure 1 | Data timeline, partitions and temporal origins |
| Figure 2 | Primary 12-hour accuracy: model comparison with bootstrap intervals |
| Figure 3 | Temporal origin sensitivity across three non-overlapping test periods |
| Figure 4 | Prediction interval reliability: aggregate versus high-volume coverage |
| Figure 5 | High-volume episode diagnostics and leave-one-episode-out analysis |

---

## Methods Summary

- **Target variable.** 12-hour cumulative inflow volume approximated by trapezoidal integration of hourly flow-rate observations.
- **Models.** Persistence, 24-hour mean, previous-day profile; ridge regression; histogram-based gradient boosting (HGB) with flow/calendar, flow/calendar/weather and oracle-rain information sets.
- **Validation.** Development-only temporal cross-validation with three expanding folds. Primary elapsed-time 60/20/20 partitions; three non-overlapping 60-day test periods for temporal robustness.
- **Hyperparameter grid.** Loss (squared error, absolute error), annual sine/cosine (included, removed), max leaf nodes (7, 15), L2 regularization (1, 10). Selection by development MAE only.
- **Prediction intervals.** Finite-sample residual order statistic at nominal 90%. Pooled static, wet/dry stratified and 30-calendar-day rolling calibration with maturity-aware residual eligibility.
- **Uncertainty.** Circular fixed-length block bootstrap (B = 24/48/168 hours, 2,000 resamples). Results are labeled as approximate bootstrap sensitivity intervals, not confirmatory confidence guarantees.
- **Episode analysis.** Training 90th-percentile outcome-tail threshold; contiguous high-volume episodes; leave-one-episode-out and non-overlapping phase diagnostics.

The full pre-analysis protocol is documented in [`PROTOCOL.md`](PROTOCOL.md). Protocol deviations are registered in [`docs/PROTOCOL_DEVIATIONS.md`](docs/PROTOCOL_DEVIATIONS.md).

---

## Citation

If you use this code or findings, please cite the versioned research compendium and the relevant source-data DOIs.

### BibTeX

```bibtex
@software{tran2026wastewater,
  author       = {Tran, Viet Nam},
  title        = {Configuration sensitivity and conditional reliability
                  in wastewater inflow volume forecasting:
                  a two-site open-data audit},
  version      = {0.2.0},
  date         = {2026-11-10},
  url          = {https://github.com/phamnam123lite-svg/wastewater-inflow-volume-open-science},
  license      = {MIT}
}
```

### CITATION.cff

A machine-readable citation file is provided at [`CITATION.cff`](CITATION.cff) for automated citation tools (GitHub "Cite this repository", Zenodo, CFF converters).

### Data citations

- DHI (2025). *Inflow to a Waste Water Treatment Plant.* Zenodo. [https://doi.org/10.5281/zenodo.15301164](https://doi.org/10.5281/zenodo.15301164)
- Sonnenschein, B. and Ziel, F. (2022). *Wastewater Treatment Plant Inflow Rate, Network Water Levels and Rain Rate for Koeln Weiden, Germany.* Zenodo. [https://doi.org/10.5281/zenodo.6992694](https://doi.org/10.5281/zenodo.6992694)

---

## Licensing

This repository uses a dual licensing model.

| Component | License | File |
|:----------|:--------|:-----|
| Analysis code (Python scripts) | MIT | [`LICENSE`](LICENSE) |
| Danish source data | CC BY-NC 4.0 | [Zenodo record](https://doi.org/10.5281/zenodo.15301164) |
| German source data | CC BY 4.0 | [Zenodo record](https://doi.org/10.5281/zenodo.6992694) |

The MIT license applies exclusively to newly authored Python scripts. Source datasets, third-party publications and provider metadata retain their original rights. See [`DATA_LICENSE.md`](DATA_LICENSE.md) for complete data licensing terms and attribution requirements.

---

## Known Limitations and Future Work

The following limitations are documented in the manuscript and the [CHANGELOG](CHANGELOG.md):

- **Scale.** Two treatment plants. Generalization to other catchments, climates and sewer configurations is not established.
- **Retrospective design.** All analyses are retrospective. Neither site was independently preregistered. The Danish revision was formulated after original results had been examined.
- **No operational trial.** No prospective deployment, real-time weather forecasts, treatment-outcome measurements or plant-control integration was conducted.
- **Temporal overlap.** High-volume episodes in the Danish data are few and partially overlapping; statistical independence cannot be claimed.
- **Aggregation semantics.** Hourly flow-rate integration approximates cumulative volume. Actual sensor latency, aggregation method and measurement uncertainty are not documented by the data providers.
- **Transfer.** German models were refitted locally. Zero-shot cross-site transfer was not evaluated.

Future work should include prospective operational trials with real-time weather forecasts, additional sites spanning diverse climates and sewer types, integration with treatment process models and storage optimization, and formal evaluation of sensor latency and aggregation effects.

---

## Extended Documentation

| Document | Description |
|:---------|:------------|
| [`PROTOCOL.md`](PROTOCOL.md) | Pre-analysis protocol (current version) |
| [`docs/PROTOCOL_v0.2.0.md`](docs/PROTOCOL_v0.2.0.md) | Version-stamped protocol snapshot |
| [`docs/PROTOCOL_DEVIATIONS.md`](docs/PROTOCOL_DEVIATIONS.md) | Registered deviations from the protocol |
| [`docs/EXTERNAL_SITE_PROTOCOL.md`](docs/EXTERNAL_SITE_PROTOCOL.md) | German site analysis protocol |
| [`docs/RESPONSE_TO_AUDIT_VI.md`](docs/RESPONSE_TO_AUDIT_VI.md) | Response to audit findings |
| [`docs/LIMITATIONS_RESOLVED_VI.md`](docs/LIMITATIONS_RESOLVED_VI.md) | Resolved limitations register |
| [`docs/LITERATURE_MATRIX.md`](docs/LITERATURE_MATRIX.md) | Literature comparison matrix |
| [`docs/SUPERVISOR_NOTE_VI.md`](docs/SUPERVISOR_NOTE_VI.md) | Supervisor note |
| [`docs/claim_evidence_map.csv`](docs/claim_evidence_map.csv) | Claim-to-evidence traceability |
| [`docs/audit_resolution_register.csv`](docs/audit_resolution_register.csv) | Audit resolution register |

---

## Acknowledgements

The author acknowledges DHI and the Danish Meteorological Institute for the Danish WWTP and meteorological observations, and Sonnenschein and Ziel for the Koeln-Weiden wastewater and rainfall data. Both datasets were made publicly available under open licenses via Zenodo.

This work was conducted at the Faculty of Environment, Van Lang University, Ho Chi Minh City, Vietnam. No external funding was received. The author declares no conflicts of interest.

AI-assisted tools were used during code development and manuscript preparation. All scientific decisions, analysis design, interpretation and responsibility for correctness remain with the human author. Full AI disclosure is provided in the manuscript.

---

*This repository follows open-science principles including FAIR data practices, computational reproducibility and transparent reporting. Version history is maintained in [`CHANGELOG.md`](CHANGELOG.md).*
