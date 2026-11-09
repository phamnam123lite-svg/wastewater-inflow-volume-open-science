# Analysis protocol fixed before model fitting

Date: 2026-11-09. Exploratory secondary analysis, not a registered study.

Question: how reliably can information available at issue time predict the next 12-hour cumulative inflow volume at the anonymized Danish WWTP, and how does performance differ from an explicitly idealized future-rainfall comparator?

Primary target: sum of hourly inflow rates over t+1,...,t+12 multiplied by one hour, in m3. Sensitivity horizons: 6 and 24 hours. This is incoming volume, not required tank capacity or pollution load.

Use Zenodo 15301164 raw observations, verified against archive checksums. Convert Copenhagen inflow timestamps to UTC, remove ambiguous timestamps, and align hourly. Do not interpolate outcomes. Flag flow below 2 m3/h and trailing six-hour ranges below 5 m3/h as suspect; preserve raw records. Features use t or earlier; calendar features are known. Impute predictors inside each training fold only. Exclude issue times lacking current flow, complete prior 24-hour flow, or complete future target windows. This creates a monitored-data subset; report retention and selection bias.

Chronological split by elapsed timeline: first 60% development, next 20% calibration, final 20% test. Purge horizon-length label overlap at boundaries. Expanding three-fold inner validation with horizon gap, choose parameters by MAE. No random train/test split. Calibration used only for residual-based 90% intervals; no test-set tuning. No refit after calibration.

Models: persistence, previous-day seasonal profile, prior 24-hour mean, ridge regression, histogram gradient boosting with flow/calendar only, same learner with past meteorology, and same learner plus perfect future rainfall (diagnostic, non-deployable). Small declared grid: ridge alpha 1/100/10000; boosting max_leaf_nodes 7/15 with l2_regularization 1/10, max_iter 150, learning_rate .05, min_samples_leaf 30, early_stopping false.

H1: historical meteorology improves MAE relative to flow/calendar alone. H2: perfect future rainfall improves MAE relative to historical-only features. H3: pooled 90% residual intervals have lower coverage on high-volume targets than overall. H1/H2 evaluated using paired moving-block bootstrap differences, 48-issue block primary and 24/168 sensitivity, 2000 resamples. Contiguous accepted issue sequences are retained within blocks; intervals are descriptive under nonstationarity, not guaranteed hypothesis tests. Multiple comparisons and secondary horizons are exploratory.

Report R2, RMSE, MAE, mean bias, 90% interval coverage/width/interval score, and underprediction in high-volume windows (threshold is training-target 90th percentile). Report wet state based on previous six-hour rain, not future outcomes. Compare pooled and wet/dry calibration. Use fixed test block without adaptation. Correlations, residual autocorrelation, monthly shift, and block permutation importance are descriptive; no causal interpretation.

Required limitations: one anonymized plant, 15 months, missingness, hourly aggregation and uncertain measurement latency, no real weather forecasts, no tank/control/effluent data, dependence of overlapping targets, seasonal drift, no external-site test. Do not claim control benefits or novel algorithms.
