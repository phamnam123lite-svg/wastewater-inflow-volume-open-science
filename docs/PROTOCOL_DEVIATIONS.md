# Revision chronology and deviations

The v0.2.0 protocol was written locally before the revised fits, after the original v0.1.0 results and audit stress tests were already known. It has no independent preregistration timestamp. All outcomes remain retrospective/exploratory.

The six temporal scenarios, development-only loss/annual search, three interval methods, circular block sensitivities, delay/no-QC refits and episode/phase analysis were executed. The protocol's optional mapping of episodes to rainfall storms was not implemented: a defensible hydraulic lag/event-independence interpretation is unavailable from the anonymized archive. We report threshold episodes without claiming independent storms.

The planned annual-removal sensitivity is identical to the selected primary model because development folds already excluded annual predictors. After inspecting that selection, an additional matched 2×2 loss/annual diagnostic was added, fixing seven leaves and L2=1. It is run by configuration_sensitivity.py and is explicitly post-selection, not confirmatory. The main grid, thresholds and test dates were not changed in response to its outcomes.

The explicitly synthetic AR(1) diagnostic used 200 Monte Carlo series per coefficient and 400 bootstrap replicates per series; real-data paired differences used 2,000 replicates. It tests behavior on known stationary artificial sequences only.

First-run outputs became the registered reference only after checks passed. The complete pipeline was independently re-executed computationally in a newly created environment; 34 registered CSV files matched with maximum absolute difference 0.0. It was the same code and dataset, not an independent implementation or site. Reproduction logs, environment metadata and both result sets are preserved.

## External extension after the author requested additional limit mitigation

EXTERNAL_SITE_PROTOCOL.md was recorded before loading the German measurement CSV and before computing its errors, after the Danish revision was complete. The observed source has a naive uniform clock; we retained it rather than asserting UTC. Right-closed hourly aggregation of four quarter-hour samples prevents future measurement use. The separately downloaded radar forecast was not modelled because the numbered columns and operational 12-hour availability could not be verified. Existing sewer-level columns were not added to the matched flow/rain comparison. All planned 12-hour external models and residual-calibration comparisons were executed and saved.

Twelve external CSVs were reproduced in the clean environment with zero maximum numeric difference. The supplementary package contains the reference CSVs and both reproduction reports; duplicate identical rerun CSVs are retained locally in D:\P2\v0.2.0 and omitted from the portable archive to avoid unnecessary duplication.
