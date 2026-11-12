# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and versions follow [Semantic Versioning](https://semver.org/).

## [0.2.4] - 2026-11-12

### Changed
- Manuscript: repository link to this release on the title page; Code Availability gives the full URLs and the steps a reviewer runs to verify the results.

No code, data or result changed; the verification reports of the v0.2.3 rerun apply unchanged.

## [0.2.3] - 2026-11-11

### Added
- Interval coverage for high-volume windows defined by the forecast, which is known at issue time (`src/forecast_high_coverage.py`; two registered CSV files, now 48 in total).
- Independent re-implementation of the results from the raw files and saved forecasts (`src/independent_check.py`), run by `reproduce.py` on every rerun.
- Results of the same run with newer library versions (`results/version_sensitivity/`, `src/compare_versions.py`).

### Changed
- Manuscript: forecast-conditioned coverage in the Abstract, Methods 2.6, Results 3.4 and 3.6, Discussion 4.3 and Conclusions; matched-configuration explanation of the October origin (3.3); exact description of the endpoint screening rule and the 16 near-constant values it leaves (2.2, 3.5); software-version sensitivity (3.5, Limitations); references to a non-existent supplement replaced; description of reference [5] corrected; earlier benchmark identified as v0.1.0.
- `src/check_manuscript.py` also checks the new numbers (43 key numbers in total).

### Removed
- Office lock file `paper/~$nuscript.docx`, committed by mistake in v0.2.2; lock files are now ignored.

No registered numerical result changed.

## [0.2.2] - 2026-11-11

### Changed
- Repository reorganized into a standard research-compendium layout: `src/` (code), `tests/`, `data/denmark` and `data/germany`, `results/denmark` and `results/germany`, `docs/`, `paper/` and `verification/`, with `reproduce.py` as the single entry point.
- Input checksums moved to `data/checksums.sha256`; whole-repository checksums in `SHA256SUMS` (standard `sha256sum` format) replace `MANIFEST_SHA256.json`.
- Reproduction reports record paths relative to the repository and list package versions.
- Manuscript: code-availability statement points to v0.2.2; acknowledgements and declarations follow the standard journal format.

### Removed
- Internal working notes and review registers, the duplicate root `PROTOCOL.md` and a bulk Crossref metadata file (still available in v0.2.1).

No numerical result changed: all 46 reference CSV files are byte-identical to v0.2.1.

## [0.2.1] - 2026-11-11

### Added
- Word manuscript and PDF rendering built from `paper/manuscript.md`.
- One-command two-site reproduction with protection against overwriting or self-comparing the reference results; integrity tests; manuscript check covering every table cell.
- Bundled source observations with checksums; `.gitattributes` disabling line-ending conversion.

### Changed
- Manuscript tables regenerated from the reference results: labels match the figures, input sets stated, interval-score and bias columns added, three-line layout.
- Wording clarified in Section 3.4 and the Conclusions; acknowledgement of the German data providers added; BibTeX author name corrected.

### Fixed
- Continuous integration omitted the configuration and synthetic diagnostics and compared a rerun with itself.

## [0.2.0] - 2026-11-10

### Changed
- Scientific framing and conclusions rewritten after configuration sensitivity reversed the primary model ranking.
- Residual order statistic corrected; fixed-length circular block bootstrap replaces shortened blocks.

### Added
- Development-selected loss and annual-term choices, three additional temporal origins and matched configuration and information diagnostics.
- Causally available rolling calibration; episode, leave-one-episode-out, nonoverlapping-phase, input-delay and no-QC sensitivities.
- External-site evaluation at Köln-Weiden (2017-2019) with 12 additional reproduced CSV files.
- Full grids, folds, forecasts, interval bounds and reference results; related work; funding, competing-interest and tool-use declarations.

## [0.1.0]

Earlier restricted benchmark. Its numerical outputs reproduce, but its main model ranking did not survive the configuration analysis in v0.2.0 and should not be cited as the study's conclusion.
