# Wastewater inflow volume forecasting

**Viet Nam Tran** — Faculty of Environment, Van Lang University, Ho Chi Minh City, Vietnam.

[Read the paper](paper/manuscript.pdf) · [Editable manuscript](paper/manuscript.md) · [Complete reproducibility package](supplementary_v0.1.0.zip)

Version 0.1.0. A secondary study on real DHI data. The historical-input boosting model did not beat the moving-average baseline; near-nominal overall interval coverage hid poor high-volume coverage. Future-rainfall results are diagnostic only.

## Reproduce directly from this repository

Python 3.11. Create and activate a virtual environment, then run:

```sh
python -m pip install -r requirements-clean-lock.txt
python download_data.py
python run_analysis.py
python verify_results.py
```

Downloads are checksum verified. Outputs are written to `results/` and `figures/`. The full supplementary ZIP also contains original and derived data, executed predictions, all five figures in PNG/SVG/PDF, literature review, proposal, protocol, source metadata, references and verification logs. Extract it to inspect the complete research directory offline. The ZIP contains no virtual environment or credentials.

## Reproducibility evidence

An independent fresh Python virtual environment reran the full pipeline. All **13 numeric CSV tables** matched the original outputs exactly (maximum absolute numeric difference **0.0**); see [reproduction.json](reproduction.json). Chronology, target sums, metrics and historical-feature causality checks passed. This is computational reproduction, not independent-site validation. No GitHub Actions execution is claimed.

## Attribution and conditions

Original data: DHI (2025), DOI https://doi.org/10.5281/zenodo.15301164; meteorology from DMI. Data and derivatives retain **CC BY-NC 4.0**. Newly written Python scripts: **MIT**. See LICENSE_DATA.md. Third-party source notebooks are not republished. The manuscript is publicly readable; no separate manuscript reuse license is asserted. Scientific claims require author review before journal submission. AI assisted coding, analysis and drafting is disclosed in the paper.

## Citation and limits

Use CITATION.cff and cite the original DHI dataset. Repository: https://github.com/phamnam123lite-svg/wastewater-inflow-volume-open-science. No software DOI has been minted. One plant, a short record and five high-volume episodes limit generalization; no storage, energy or treatment benefit has been established.
