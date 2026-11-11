# Wastewater inflow forecasting research compendium

**Version 0.2.1 — supervisor review, 11 November 2026**

Viet Nam Tran · Faculty of Environment, Van Lang University, Ho Chi Minh City, Vietnam

The submission document is **[paper/manuscript.docx](paper/manuscript.docx)**. A PDF rendering, [paper/manuscript.pdf](paper/manuscript.pdf), is included for quick reading; the DOCX remains the review document. Its editable content source is [paper/manuscript.md](paper/manuscript.md). This compendium audits forecasting configuration and conditional interval reliability at two independently sourced wastewater plants. It is retrospective research, not a prospective operating trial or an accepted journal article.

## Start here

Read [HUONG_DAN_THAM_DINH_VI.md](HUONG_DAN_THAM_DINH_VI.md), the paper, and [docs/FINAL_AUDIT_VI.md](docs/FINAL_AUDIT_VI.md). The complete folder is the submission unit. Original data used in the analysis are bundled, separately licensed and checksum-verified. No login or data-download step is needed to run the analysis offline after installing dependencies.

## Reproduce from a new copy

Use **Python 3.11.9** for the verified platform. The recorded reference environment is Windows; other operating systems have not been certified. Allow about 1 GB for an environment, source data and a new run. Run these commands from this folder, not from `paper/`.

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest test_integrity -v
.\.venv\Scripts\python.exe reproduce.py --output reproduced
```

Linux/macOS equivalent (not independently tested here):

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest test_integrity -v
.venv/bin/python reproduce.py --output reproduced
```

The runner executes both sites, all configuration and synthetic diagnostics, both verification suites, figures, and the paper/table audit. It saves progress logs and `reproduced/summary.json`. A complete successful run compares **34 Danish and 12 German CSV files**, including every expected filename. Registered references in `results/` and `external_results/` are never overwritten. The comparator rejects comparing a directory with itself. For another run, choose a fresh output name, such as `reproduced_second`.

Reference comparison uses **rtol=1e-10, atol=1e-8**, with matching shape, column order and nonnumeric values. Exact zero differences observed in a particular run are not a requirement that every supported CPU or library build be bitwise identical. CSV files are compared by parsed contents, not by a misleading byte-identical claim. Results from the actual final run are recorded under `verification/`.

### Individual commands

```bash
python run_analysis.py --output reproduced/danish
python configuration_sensitivity.py --results reproduced/danish
python bootstrap_diagnostic.py --output reproduced/danish/SYNTHETIC_bootstrap_diagnostic.csv
python verify_results.py --results reproduced/danish --reference results
python external_site.py --output reproduced/german
python verify_external.py --results reproduced/german --reference external_results
python make_figures.py --results reproduced/danish --figures reproduced/figures
python audit_project.py --results reproduced/danish --external reproduced/german --report reproduced/paper_code_audit.json
```

These reproduce the runner's stages; do not run them over a completed output directory. The optional `download_data.py` restores the pinned Danish observation files from the provider archive. `external_site.py --download --output NEW_DIRECTORY` restores the pinned German observations and then runs that site. Internet access is required only for package installation and optional source downloads.

## Build the Word manuscript

```bash
python -m pip install -r requirements-docs.txt
python build_docx.py          # Word only
python build_docx.py --pdf    # Word plus a LibreOffice PDF rendering
```

The builder reads only `paper/manuscript.md` and the five saved PNG figures. It preserves all four tables as three-line academic tables (right-aligned numbers, typographic minus signs, notes below each table, rows kept together), citations and references, and creates an editable native Word equation. Every table cell, including row labels and input codes, is regenerated from and checked against the reference CSVs by `audit_project.py`. It does not fit models or change results. Visual rendering needs Word or LibreOffice separately; authoring dependencies alone do not perform a PDF layout check. The delivered DOCX is the review document; Markdown is its source, not a competing manuscript version.

## Folder map

| Location | Purpose |
| --- | --- |
| `paper/` | Word manuscript, PDF rendering, editable Markdown and verified bibliography |
| root `*.py` | Full analysis, download, reproduction, integrity tests and document builder |
| `requirements*.txt` | Pinned analysis and separate document-authoring dependencies |
| `data/`, `external_data/` | Original observations actually used; no interpolated replacement targets |
| `results/`, `external_results/` | Registered numerical reference outputs and manifests |
| `figures/` | Five figures in PNG, SVG and PDF for editing and publication |
| `sources/` | Provider and bibliographic metadata, source hashes |
| `docs/` | Protocols, deviations, limitations, audit response and section-by-section audit |
| `verification/` | Actual final-run checks, reproduction summaries and cleanup register |
| `.github/workflows/` | CI repeats the same protected two-site workflow |
| `MANIFEST_SHA256.json` | Submission file inventory and hashes, excluding itself |
| `.gitattributes` | Disables line-ending conversion so data and manifest checksums match on every platform |

The same figure in PNG/SVG/PDF serves distinct purposes and is intentionally retained. Older manuscripts, obsolete supplements, virtual environments, cache files, scratch files and full duplicate rerun outputs are excluded from the submission. Historical versions remain in Git history and external backups.

## Interpretation and licenses

The 12-hour Danish historical HGB MAE is 2,280.1 m³ versus 3,406.6 m³ for the preceding-24-hour mean. German flow/rain HGB MAE is 1,661.9 m³ versus 3,293.1 m³ for that baseline. Historical rain and rolling calibration have site-dependent effects. Aggregate coverage is substantially better than high-volume subgroup coverage; no finite-sample conditional guarantee is claimed.

Danish observations: DHI, DOI [10.5281/zenodo.15301164](https://doi.org/10.5281/zenodo.15301164), CC BY-NC 4.0; German observations: Sonnenschein and Ziel, DOI [10.5281/zenodo.6992694](https://doi.org/10.5281/zenodo.6992694), CC BY 4.0. [DATA_LICENSE.md](DATA_LICENSE.md) governs attribution and reuse. The MIT license covers newly authored code, not third-party data. `SYNTHETIC_bootstrap_diagnostic.csv` is explicitly simulated diagnostic data and is never described as plant evidence.

Models were fitted locally at each site. Rate aggregation, actual sensor latency, operational forecast vintages and treatment/control benefits remain unverified. Computational reproduction is not independent human peer review. The author must approve the work and provide correspondence details before journal submission. See `CITATION.cff` for citation metadata; the source-data DOIs are not DOIs for this paper.
