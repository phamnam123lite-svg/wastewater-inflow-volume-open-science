# Wastewater inflow forecast audit - final revision v0.2.0

**Current manuscript:** [PDF](manuscript.pdf) · [editable Markdown](manuscript.md) · [release v0.2.0](https://github.com/phamnam123lite-svg/wastewater-inflow-volume-open-science/releases/tag/v0.2.0)

Author: **Viet Nam Tran**, Faculty of Environment, Van Lang University, Ho Chi Minh City, Vietnam.

This is the final computational revision prepared for supervisor review on 10 November 2026. It is not a journal acceptance. It includes an independently sourced German-site evaluation with local refitting, not zero-shot model transfer or a prospective operational trial. All revised analyses are retrospective. The author must approve the scientific content and provide a correspondence email before submission.

## What changed

The original v0.1.0 conclusion that a simple baseline outperformed historical HGB was sensitive to the restricted loss/calendar configuration. Development-only temporal selection in v0.2.0 gives primary 12-hour MAE of **2,280.1 m³** for historical HGB, **2,221.7 m³** for flow/calendar HGB, **3,406.6 m³** for the 24-hour mean and **1,402.3 m³** for a non-operational future-rainfall oracle. The legacy configuration is retained, not erased.

Three additional temporal tests, matched loss/calendar comparisons, exact residual quantiles, maturity-aware rolling calibration, fixed-length circular bootstrap sensitivities, episode diagnostics and delayed-input/no-screening refits are included. High-volume interval reliability remains weak; the target is an approximation of integrated archived flow rates, pending confirmation of hourly aggregation semantics.

## Download the complete study

[supplementary_v0.2.0.zip](supplementary_v0.2.0.zip) contains the source observations, executable scripts, full results, five figures in PNG/SVG/PDF, editable manuscript, reference metadata, protocol, original audit and revision response. Extract it before running. The archive root is a self-contained working directory. Its `MANIFEST_SHA256.json` records every packaged file except itself.

Root-level `manuscript.pdf` and `manuscript.md` are exact copies of `manuscript_FINAL.pdf` and `manuscript_FINAL.md` inside the supplement. Root scripts match their supplementary counterparts. [release_manifest.json](release_manifest.json) records SHA-256 hashes of the published files. GitHub's automatically generated source archive contains the repository; `supplementary_v0.2.0.zip` is the complete computational study.

## Reproduce the numerical results

Use Python **3.11.9** for the closest match to the verified environment. From the extracted supplement directory:

```bash
python -m venv .venv
```

Activate it (`.venv\Scripts\activate` on Windows, or `source .venv/bin/activate` on macOS/Linux), then:

```bash
python -m pip install -r requirements.txt
python download_data.py
python run_analysis.py --output rerun_results
python configuration_sensitivity.py --results rerun_results
python bootstrap_diagnostic.py --output rerun_results/SYNTHETIC_bootstrap_diagnostic.csv
python verify_results.py --results rerun_results --reference results
python make_figures.py --results rerun_results --figures rerun_figures
```

`download_data.py` checks the pinned Zenodo metadata and MD5 values. It requires network access, but the verified source files are also included for an offline run; omit that command when using the bundled verified data. The analysis does not use `data/data.csv`, which is preserved solely as provider provenance.

The main analysis runs six scenarios, with 16 HGB candidates and three temporal folds for each learned information set. Runtime depends on hardware. All modelling is CPU-based; no GPU is needed. Outputs are deterministic in the tested Windows/Python environment. Other numerical libraries or platforms may differ slightly; the comparator uses relative tolerance 1e-10 and absolute tolerance 1e-8, and fails on missing, empty, changed-schema or mismatched files. Do not overwrite the reference results before comparison. Do not use `--make-reference` on your rerun.

## External-site extension

The final paper additionally evaluates **6,588 German test windows** and **700 high-volume windows in 41 threshold episodes**. Flow/rain HGB MAE was **1,661.9 m³** versus **3,293.1 m³** for the 24-hour mean. Historical rain improved accuracy in Germany, while rolling calibration deteriorated there. These findings prevent universal claims based on the Danish site alone. All **12 external CSV tables** reproduced exactly, so the two numerical comparisons cover **46 CSV tables in total**, each with maximum absolute difference 0.0.

From the complete extracted supplement:

```bash
python external_site.py --output external_rerun --download
python verify_external.py --results external_rerun --reference external_results
```

Omit `--download` for offline use of the bundled checksum-verified German source. The source uses L/s and mm/min at quarter-hour resolution; aggregation is right-closed and causal. Its uniform archive clock is not asserted to be UTC. See `EXTERNAL_SITE_PROTOCOL.md`, `external_results/external_source_audit.json`, and `LIMITATIONS_RESOLVED_VI.md`.

## Render the manuscript

The text, tables and claim-to-evidence map are generated from the published reference results. PDF/HTML authoring has a separate dependency:

```bash
python -m pip install -r requirements-docs.txt
python write_manuscript.py
python build_paper.py
```

These commands regenerate `manuscript_FINAL.md`, `manuscript_FINAL.pdf` and `manuscript_FINAL.html`. They do not silently substitute a rerun's results for the versioned reference dataset. Fonts come from matplotlib; no Windows font paths or Microsoft Office installation are required. `make_figures.py` generates PNG, SVG and PDF assets.

## Executed verification

A newly created Python 3.11.9 environment installed the locked dependencies and reran the complete analysis, the matched diagnostic and the explicitly synthetic bootstrap experiment. **34 registered CSV files reproduced; maximum absolute numerical difference = 0.0.** See [reproduction.json](reproduction.json) and `results/verification.json` inside the supplement. Automated checks reconstructed 19,618 targets and recomputed all reported main metrics and interval arrays. Six intentionally invalid reference comparisons were rejected. This is computational reproduction by the same workflow, not independent human peer review. The external extension is a separate-site methodological replication with locally refitted models.

The manuscript PDF was rendered and visually reviewed across all 16 pages; table captions remain attached to tables. `claim_evidence_map.csv` links each result group to its source tables.

## Data, licenses and limitations

Source: DHI (2025), *Inflow to a Waste Water Treatment Plant: observations and processed data*, v1, [DOI 10.5281/zenodo.15301164](https://doi.org/10.5281/zenodo.15301164). Plant data are attributed to DHI and meteorological data to DMI. Zenodo metadata records **CC BY-NC 4.0**. Danish derived data retain source attribution and applicable non-commercial conditions. German observations are separately licensed CC BY 4.0 by Sonnenschein and Ziel, DOI [10.5281/zenodo.6992694](https://doi.org/10.5281/zenodo.6992694). Newly authored Python code is **MIT** licensed; this does not relicense source data or third-party articles. See `DATA_LICENSE.md`.

The Danish source covers one anonymized plant; a second source covers Köln-Weiden, Germany, in 2017-2019. There are five Danish and 41 German high-volume threshold episodes. The study still lacks independently confirmed sensor aggregation/actual latency and operational control/effluent/energy endpoints. Both sites use overlapping issue windows; models are refitted locally. We make no Q1/Q2 acceptance claim, guaranteed coverage claim, causal treatment-benefit claim or code DOI claim. The source-data DOI is not a DOI for this study.

## Review and provenance

- [Response to all 19 audit findings](RESPONSE_TO_AUDIT_VI.md)
- [Note for the supervisor](SUPERVISOR_NOTE_VI.md)
- [Changes and remaining limitations](CHANGELOG.md)
- [Revision protocol](PROTOCOL_v0.2.0.md) and [deviations](PROTOCOL_DEVIATIONS.md)
- [Literature and novelty matrix](LITERATURE_MATRIX.md)
- [CITATION.cff](CITATION.cff)

The [v0.1.0 release](https://github.com/phamnam123lite-svg/wastewater-inflow-volume-open-science/releases/tag/v0.1.0) is retained as historical provenance. Its numerical claims and access-status notes describe the earlier version and should not be used as the current manuscript. This repository was made public by its owner before the final revision. AI assisted literature discovery, computation, verification and drafting; human author approval remains necessary.
