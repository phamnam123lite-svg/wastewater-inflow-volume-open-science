# Wastewater inflow volume forecasting: configuration sensitivity and conditional reliability

[![Reproduce both sites](https://github.com/phamnam123lite-svg/wastewater-inflow-volume-open-science/actions/workflows/reproduce.yml/badge.svg)](https://github.com/phamnam123lite-svg/wastewater-inflow-volume-open-science/actions/workflows/reproduce.yml)

Research compendium for the manuscript **"Configuration sensitivity and conditional reliability in wastewater inflow volume forecasting: a two-site open-data audit"** by Viet Nam Tran (Faculty of Environment, Van Lang University, Ho Chi Minh City, Vietnam; nampham123ntt@gmail.com). It contains the manuscript, the source observations, all analysis code, the reference results and the reports of a complete rerun.

## Overview

The study forecasts the 12-hour integrated inflow volume at two wastewater treatment plants using open data: an anonymized Danish plant (DHI, Zenodo 15301164) and Köln-Weiden, Germany (Sonnenschein and Ziel, Zenodo 6992694). It evaluates how loss function and calendar terms change model rankings, whether historical and (idealized) future rainfall add value, and how residual-based 90% prediction intervals behave overall, in wet periods and in high-volume windows.

Main results on the held-out test periods:

| Site | Model | MAE (m³) | 24-h mean baseline MAE (m³) |
| --- | --- | ---: | ---: |
| Denmark (n = 2,160) | Gradient boosting, flow + calendar + weather | 2,280.1 | 3,406.6 |
| Germany (n = 6,588) | Gradient boosting, flow + calendar + rain | 1,661.9 | 3,293.1 |

Aggregate interval coverage was much higher than coverage in high-volume windows at both sites (Denmark 83.7% vs 21.0%; Germany 92.6% vs 39.3%), also when high volume is defined by the forecast (37.1% and 74.0%). The study is retrospective; it does not evaluate operational weather forecasts or treatment and control benefits.

## Repository structure

```
.
├── paper/                  manuscript (DOCX, PDF, Markdown source) and references.bib
├── data/
│   ├── denmark/            wwtp.csv, dmi.csv and Zenodo metadata (CC BY-NC 4.0)
│   ├── germany/            wtp_network_rain.csv and Zenodo metadata (CC BY 4.0)
│   └── checksums.sha256    SHA-256 of the three observation files
├── src/                    analysis, verification, figure and manuscript-build scripts
├── tests/                  integrity tests
├── results/
│   ├── denmark/            reference results, Danish site (35 CSV files + metadata)
│   ├── germany/            reference results, German site (13 CSV files + metadata)
│   └── version_sensitivity/  the same run with newer library versions (see below)
├── figures/                Figures 1-5 (PNG, SVG, PDF)
├── docs/                   protocols, deviations, literature matrix, claim-to-evidence map
├── verification/           reports of the complete rerun and of the manuscript check
├── reproduce.py            one command to rerun and verify everything
├── requirements.txt        pinned analysis dependencies
├── requirements-docs.txt   dependencies for building the Word manuscript
├── SHA256SUMS              checksums of every file in the repository
├── CITATION.cff, CHANGELOG.md, LICENSE (code, MIT), DATA_LICENSE.md (data)
└── .github/workflows/      continuous integration: the same complete rerun
```

| Script | Purpose |
| --- | --- |
| `src/run_analysis.py` | Danish site: data alignment, screening, model selection, forecasts, intervals, sensitivities |
| `src/configuration_sensitivity.py` | Matched 2×2 loss/annual-term diagnostic |
| `src/bootstrap_diagnostic.py` | Synthetic AR(1) check of the block bootstrap |
| `src/forecast_high_coverage.py` | Interval coverage when high volume is defined by the forecast (known at issue time) |
| `src/external_site.py` | German site: the same design refitted locally |
| `src/verify_results.py`, `src/verify_external.py` | Independent recomputation checks and comparison with the reference results |
| `src/make_figures.py` | Figures 1-5 from saved results |
| `src/check_manuscript.py` | Checks every table cell and key reported numbers against the results |
| `src/independent_check.py` | Separate re-implementation (no shared code) that rebuilds targets, baselines, splits, metrics, intervals and episodes from the raw files and saved forecasts |
| `src/compare_versions.py` | Summarizes the differences between the pinned and newer-library runs |
| `src/build_manuscript.py` | Builds `paper/manuscript.docx` (and optionally the PDF) from the Markdown source |
| `src/download_data.py` | Optional: restores the Danish observations from Zenodo (MD5 verified) |

## Reproducing the results

Requirements: Python 3.11 (the reference run used 3.11.9 on Windows), about 1 GB of free disk space and 5 minutes. No internet access is needed after installing the dependencies; the observations are included.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate      Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python reproduce.py --output reproduced
```

`reproduce.py` checks the input checksums, reruns both sites, compares all 48 registered CSV files with `results/` (relative tolerance 1e-10, absolute 1e-8), regenerates the figures and checks them pixel by pixel against `figures/`, checks every manuscript table cell and key number, and runs the independent re-implementation on the rerun outputs. It writes logs and `summary.json` to the new output directory and never modifies `results/`. The output directory must not already exist.

Exact agreement requires the pinned versions in `requirements.txt` with Python 3.11. With newer libraries the run completes but the comparison fails: 10 of 24 Danish hyperparameter selections and some model errors change (`results/version_sensitivity/`, summarized by `python src/compare_versions.py`; see manuscript Section 3.5).

The steps can also be run individually from the repository root:

```bash
python src/run_analysis.py --output reproduced/denmark
python src/configuration_sensitivity.py --results reproduced/denmark
python src/bootstrap_diagnostic.py --output reproduced/denmark/SYNTHETIC_bootstrap_diagnostic.csv
python src/forecast_high_coverage.py --results reproduced/denmark --site denmark
python src/verify_results.py --results reproduced/denmark --reference results/denmark
python src/external_site.py --output reproduced/germany
python src/forecast_high_coverage.py --results reproduced/germany --site germany
python src/verify_external.py --results reproduced/germany --reference results/germany
python src/make_figures.py --results reproduced/denmark --figures reproduced/figures
python src/check_manuscript.py --results reproduced/denmark --external reproduced/germany --report reproduced/manuscript_check.json
python src/independent_check.py --denmark reproduced/denmark --germany reproduced/germany --report reproduced/independent_check.json
```

## Verifying file integrity

Every file is stored byte-for-byte (`.gitattributes` disables line-ending conversion), so the checksums hold on any platform:

```bash
sha256sum -c SHA256SUMS                       # Linux/macOS, whole repository
sha256sum -c data/checksums.sha256            # observation files only
```

On Windows PowerShell: `Get-FileHash <file> -Algorithm SHA256`.

## Building the manuscript

```bash
python -m pip install -r requirements-docs.txt
python src/build_manuscript.py          # paper/manuscript.docx
python src/build_manuscript.py --pdf    # also paper/manuscript.pdf (requires LibreOffice)
```

The builder reads only `paper/manuscript.md` and the saved figures; it does not fit models or change results.

## Data and licenses

- Danish observations: DHI (2025), *Inflow to a Waste Water Treatment Plant: observations and processed data*, v1, [doi:10.5281/zenodo.15301164](https://doi.org/10.5281/zenodo.15301164), CC BY-NC 4.0. Plant and weather measurements are credited to DHI and the Danish Meteorological Institute.
- German observations: Sonnenschein, B. and Ziel, F. (2022), *Wastewater Treatment Plant Inflow Rate, Network Water Levels and Rain Rate for Koeln Weiden, Germany*, v1.0, [doi:10.5281/zenodo.6992694](https://doi.org/10.5281/zenodo.6992694), CC BY 4.0.
- Code: MIT License (`LICENSE`). Data keep their original licenses; see `DATA_LICENSE.md`.

## Citation

Please cite this repository using `CITATION.cff` and cite both source datasets.
