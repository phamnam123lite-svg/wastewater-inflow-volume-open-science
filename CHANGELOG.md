# Version 0.2.1 — 11 November 2026

Submission packaging and integrity correction. Scientific reference CSV values remain those of the audited two-site v0.2.0 analysis. Added Word manuscript, full reproduction runner, guards against reference overwrite/self-comparison, source hashes, complete-table audit and regression tests. Corrected README and CI omissions, removed obsolete duplicate exports and v0.1 verification artifacts after backup. See docs/FINAL_AUDIT_VI.md. These changes do not create new experimental observations.

Final consistency pass (11 November 2026): all narrative values rechecked against the reference CSVs with no discrepancy; ten references rechecked against publisher records; two unclear sentences reworded (Section 3.4, Conclusions); acknowledgement of the German data providers and AI-tool disclosure completed; BibTeX author name corrected (Sølve Eidnes); Word manuscript rebuilt. No numerical result or conclusion changed.

Table revision (11 November 2026): all four manuscript tables regenerated directly from the reference CSVs. Row labels now match the figure labels; an Inputs column (F/C/W/P/R) states each model's information set; Table 3 adds the mean interval score; Table 4 adds bias; sample sizes use thousands separators; titles sit above and notes below each table with all abbreviations defined. Word tables use a three-line layout, right-aligned numbers and typographic minus signs, and are kept on one page. `audit_project.py` now checks every table cell, including labels and input codes. A PDF rendering of the Word manuscript and a `.gitattributes` file (no line-ending conversion) were added. No numerical value changed.

# Change log

## v0.2.0 - 10 November 2026

- Rewrote the scientific framing and conclusions after configuration sensitivity reversed the primary model ranking.
- Added development-selected loss/annual choices, three retrospective temporal origins and matched configuration/information diagnostics.
- Corrected the residual order statistic and added causally available rolling calibration.
- Replaced shortened unequal-weight blocks with fixed circular blocks and explicitly limited inferential interpretation.
- Added episode, leave-one-episode-out, nonoverlapping-phase, input-delay and no-QC sensitivities.
- Saved full grids, folds, calibration/test forecasts, interval bounds and reference results.
- Replaced the hardcoded empty-success comparator with a portable fail-closed comparator and negative tests.
- Added source-supported related work, complete author references, explicit AI disclosure, no-funding and no-conflict declarations.
- Generated portable figures, PDF/HTML manuscript, claim-to-evidence map and a 34-CSV clean-environment reproduction.
- Kept the original audit and v0.1.0 identifiable. Repository root and v0.2.0 are the current manuscript; v0.1.0 is historical.

Added external-site replication on Köln-Weiden (2017-2019), 12 additional exactly reproduced CSVs, 41 threshold episodes, and site-dependent rainfall/calibration findings.

Remaining scientific limits: two plants, no prospective operational trial, overlapping high-volume episodes; unknown hourly aggregation/actual latency; no operational weather forecasts or treatment outcomes. Remaining submission administration: correspondence email, human author/supervisor approval, author-contribution confirmation and selected journal formatting/requirements.

## v0.1.0 - original release

Earlier restricted benchmark. Reproduction of its numerical outputs was valid, but its main model ranking was not robust to loss/calendar configuration. Do not cite the historical ranking as the conclusion of v0.2.0.
