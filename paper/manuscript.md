# Information availability and conditional reliability in 12-hour wastewater inflow-volume forecasting: a reproducible single-plant audit

**Viet Nam Tran**

Faculty of Environment, Van Lang University, Ho Chi Minh City, Vietnam

## Highlights

- Raw observations support an auditable benchmark of cumulative wastewater inflow.
- A 24-hour mean baseline outperformed historical-input boosted models on test MAE.
- Perfect future rainfall substantially improved the 12-hour diagnostic comparator.
- Near-nominal overall interval coverage concealed poor high-volume coverage.
- Operational interpretation requires real forecast vintages and plant constraints.

## Abstract

Wastewater inflow forecasts may support hydraulic planning, but their usefulness depends on information availability and reliability during high-volume conditions. We conducted a reproducible secondary analysis of an openly archived Danish wastewater treatment plant dataset to evaluate forecasts of cumulative inflow over the next 12 hours. Raw hourly observations were aligned in time without interpolating target values. Chronological development, calibration, and test periods were separated by forecast-horizon purges. Persistence, seasonal and moving-average baselines, ridge regression, and histogram gradient boosting were compared using historical inputs and an explicitly non-operational perfect-future-rainfall comparator. The primary test contained 2,160 overlapping forecast windows. The preceding-24-hour mean baseline achieved a mean absolute error of 3,407 m³, compared with 7,607 m³ for historical-input boosting and 2,044 m³ for the perfect-rainfall comparator. Adding historical meteorology to flow and calendar predictors did not yield a stable improvement: the paired mean absolute error difference was 63 m³, with an approximate 95% block-bootstrap interval of −526 to 653 m³. For the moving-average baseline, nominal 90% residual intervals covered 87.5% of test outcomes overall but only 23.5% of high-volume outcomes. Those high-volume outcomes comprised 81 overlapping windows in five contiguous episodes, limiting inference. These findings demonstrate a dataset-specific separation between average accuracy, conditional reliability, and idealized meteorological information. They do not establish storage savings or treatment improvements. Multi-site observations, archived weather forecasts, and plant operating constraints are needed before operational deployment.

## Keywords

Wastewater treatment; cumulative inflow; hydraulic planning; temporal validation; prediction intervals; rainfall information; open data.

## 1. Introduction

Machine learning is increasingly investigated for wastewater monitoring and prediction, but predictive accuracy alone does not establish suitability for operational decisions [1]. Inflow forecasting is one relevant application because it characterizes an incoming hydraulic boundary condition. The DHI open benchmark explicitly motivates forecasts at a 12-hour horizon and provides paired inflow and meteorological observations [2]. A forecast of total incoming volume can be examined in physical units relevant to planning, while retaining the distinction between predicted inflow and actual storage requirements.

Probabilistic wastewater inflow forecasting is not a new research direction. Sonnenschein and Ziel developed an intraday probabilistic approach using rainfall and sewer-network information, with particular attention to rainfall events [3]. González Barberá et al. examined wastewater inflow forecasting in a Mediterranean setting [4]. The DHI example uses boosted trees and explicitly assumes perfect precipitation information over its forecast horizon [2]. These precedents preclude claiming novelty for forecasting inflow, using rainfall predictors, or reporting uncertainty.

Nevertheless, an open benchmark can support a useful independent audit when the prediction target, information boundary and validation estimand are specified differently. Here, the target is the cumulative volume entering a plant during the next 12 hours. The audit asks whether models using information available at issue time remain accurate and empirically calibrated on a later period, especially for high-volume outcomes. The perfect-rainfall model is retained as a diagnostic comparator and is not conflated with a model driven by real weather forecasts.

The distinction matters methodologically. Evaluation of structured data should reflect its temporal dependence [5]. In wastewater applications, Bøhn et al. observed different transfer behavior for linear and nonlinear models and emphasized the importance of distribution changes [6]. Standard residual calibration also does not automatically provide guaranteed coverage for dependent, non-exchangeable observations; time-series-specific methods address additional assumptions and adaptation requirements [7]. Consequently, we evaluate empirical reliability and explicitly avoid a distribution-free coverage claim.

The study has three primary questions. First, does adding historical meteorology improve cumulative-volume MAE relative to flow and calendar predictors? Second, how much does a perfect-future-rainfall comparator change the performance of the selected model family? Third, does aggregate interval coverage mask poor coverage for high-volume outcomes? The contribution is a reproducible, narrowly scoped evaluation of these questions on raw-derived open observations, rather than a new forecasting algorithm or a demonstrated improvement to treatment performance. The literature search supports this scope but does not establish that this exact application is unprecedented.

## 2. Materials and Methods

### 2.1. Data provenance and scope

We used version 1 of the DHI dataset, archived under DOI 10.5281/zenodo.15301164 [2]. The archive identifies the source as an anonymized Danish wastewater treatment plant receiving combined sewage, with meteorological observations from the Danish Meteorological Institute. The observations and processed-data archives were downloaded and their MD5 checksums matched the values recorded by Zenodo. SHA-256 hashes of local files are supplied with the analysis package. Zenodo metadata records a CC BY-NC 4.0 license.

The raw flow table contains 9,868 timestamped hourly records. The meteorological table includes precipitation, pressure, radiation, relative humidity, air temperature, grass temperature and two soil-temperature measurements. There are no paired effluent-quality, energy, tank-level, process-control or treatment-capacity measurements. The dataset therefore supports inflow prediction but cannot directly quantify treatment efficiency, hydraulic storage requirements or energy savings.

The original repository was also inspected to identify prior use. Its example predicts a 12-hour flow trajectory with XGBoost and includes future observed precipitation under an explicit perfect-forecast assumption. Its preprocessing notebook applies linear interpolation to short gaps. We did not execute that benchmark as an exact replication, and its reported metrics are not treated as directly comparable with the cumulative-volume scores below.

### 2.2. Time alignment and quality control

Local inflow timestamps were interpreted in the Europe/Copenhagen time zone and converted to UTC. One ambiguous daylight-saving timestamp was excluded. Meteorological timestamps were treated as UTC, following the provider's preprocessing documentation. The aligned grid contains 11,257 hourly positions between 7 November 2023 and 18 February 2025. There were no duplicate retained UTC timestamps.

Flow observations below 2 m³/h were flagged. A trailing six-hour window with a flow range below 5 m³/h flagged its endpoint as potentially flat. These rules are transparent screening heuristics inspired by the provider's quality-control concerns; they are not independently validated sensor-fault labels. They flagged six low observations and 18 flat-window endpoints. Large flows were retained because extreme hydraulic conditions are part of the research question. Relative humidity outside 0–100% was marked missing. Grass and soil temperatures were omitted from the forecasting feature sets because of extensive gaps.

No target values were interpolated. An issue time was eligible only if its current flow, preceding 24-hour flow history, future target window and required rainfall summaries were available. Additional missing predictor values were imputed using training-fold medians, with missingness indicators. This complete-outcome design is reproducible but conditions evaluation on monitored periods; it does not resolve potentially informative missingness.

### 2.3. Prediction target and information sets

For issue time t and horizon h, the target was

\[
V_{t,h}=\sum_{k=1}^{h}Q_{t+k}\Delta t,\qquad \Delta t=1\ \mathrm{hour}.
\]

Q is hourly mean inflow in m³/h, so V is in m³. The primary horizon was 12 hours; 6- and 24-hour analyses were prespecified sensitivity checks. Issue time t denotes the time when the observation stamped t is assumed available. Actual measurement latency and whether timestamps denote the start or end of an aggregation interval require operational verification.

Flow features included lags 0, 1, 2, 3, 6, 12, 24, 48 and 168 hours and rolling means and standard deviations over 6, 12 and 24 hours. Calendar features were sine and cosine representations of hour, weekday and day of year. Historical meteorological features were precipitation sums over 1, 6, 12, 24 and 72 hours, together with current and trailing-six-hour means of pressure, radiation, humidity and air temperature. The oracle added the total and maximum observed rainfall during t+1 through t+h. These two oracle predictors are deliberately unavailable in the historical-input experiment.

### 2.4. Models and chronological validation

Three transparent baselines were evaluated: persistence, hQ(t); a preceding-24-hour mean multiplied by h; and the sum of the corresponding hours from the previous day. For h=24, the latter two baselines are algebraically identical. Ridge regression used historical flow, calendar and meteorological features. Histogram gradient boosting (HGB) was fitted to three information sets: flow/calendar, historical flow/calendar/meteorology, and the latter plus oracle rainfall. Learned point predictions were truncated below zero.

The first 60% of the elapsed timeline formed the development period, the next 20% the calibration period, and the final 20% the test period. Boundaries were 14 August 2024 at 10:00 UTC and 16 November 2024 at 05:00 UTC. A forecast was excluded from an earlier partition if its target window reached the next partition. Eligible sample dates thus differ from the nominal boundaries because missing windows were excluded.

Hyperparameters were selected by mean absolute error in three expanding temporal folds inside development, with a gap of h eligible observations between training and validation. Since eligible times are at least one hour apart, this is at least a horizon-length temporal gap. Median imputation and ridge scaling were fitted separately inside each fold. Ridge alpha was searched over 1, 100 and 10,000. HGB used 150 iterations, learning rate 0.05, minimum leaf size 30, maximum leaf counts 7 or 15, and L2 penalties 1 or 10. Automatic early stopping was disabled to avoid an internal random validation split. The random seed was 20261109. Models were not refitted after calibration or selected using test scores.

### 2.5. Residual intervals and performance measures

For each fixed model, absolute calibration residuals defined a symmetric interval radius. The empirical quantile level was min{1, ceil[(n+1)0.9]/n}, with the higher sample quantile used; lower bounds were truncated at zero. A sensitivity analysis estimated separate radii for wet and dry states, requiring at least 30 calibration scores per state. Wet state meant positive observed rainfall over the preceding six hours. This is residual-based calibration with a conformal-style rank adjustment, not a claim of exact coverage for the dependent sequence and not an implementation of SPCI [7].

MAE was the primary point metric; RMSE, R², mean prediction bias and mean positive underprediction were secondary. Interval measures included empirical coverage, width, upper-bound exceedance and the 90% interval score, equal to interval width plus a factor of 20 times each lower or upper miss. A high-volume subgroup was defined using the training-target 90th percentile. This outcome-defined subgroup is a retrospective diagnostic, not a state assumed known at issue time.

H1 predicted lower MAE for historical HGB than flow/calendar HGB. H2 predicted lower MAE for oracle HGB than historical HGB. Paired differences in absolute errors were assessed with 2,000 moving-block bootstrap replicates. Blocks began at eligible issue times and were shortened at gaps or the ends of contiguous runs; the primary maximum length was 48 hours, with 24 and 168 hours as sensitivities. Percentile intervals are approximate conditional uncertainty summaries for this test period. H3 predicted lower high-volume coverage than overall coverage and was assessed descriptively because the subgroup contained few episodes. No independent-binomial inference was applied to overlapping windows.

Training Spearman correlations, monthly summaries, test residual autocorrelation and the association between absolute residuals and predictions were examined. Group-shift sensitivity circularly shifted flow, rainfall, calendar or other-weather predictors together, using 20 shifts of at least 48 retained positions. This preserves within-group structure approximately but may create unrealistic cross-group combinations and crosses gaps in the retained sequence. It is a sensitivity diagnostic, not causal attribution or a formal uncertainty interval for importance.

## 3. Results

### 3.1. Data availability and temporal partitions

After alignment, 1,390 grid positions lacked raw flow. The low/flat screening increased missing flow to 1,414 positions. The 12-hour analysis retained 4,398 development, 2,089 calibration and 2,160 test windows. The first eligible development window was 20 January 2024, illustrating how complete-window requirements excluded much of the early record. Test issue times ranged from 16 November 2024 at 05:00 UTC to 17 February 2025 at 11:00 UTC.

Mean 12-hour target volume was 19,942 m³ in development, 13,728 m³ in calibration and 16,447 m³ in test. Wet-state proportions were 31.0%, 20.6% and 32.7%, respectively. These differences document changing observed distributions but do not identify their causes. The training-derived high-volume threshold was 32,304.98 m³. In test, 81 windows exceeded it, representing 3.75% of windows in five contiguous high-volume episodes. There were 707 wet and 1,453 dry test windows.

### 3.2. Point forecasting performance

The preceding-24-hour mean produced the lowest test MAE among the historical-information configurations (Table 1). Ridge had a lower RMSE than the simple baselines but a higher MAE, illustrating that model ranking depended on the error criterion. HGB with historical information had negative test R² and substantial positive mean bias. The oracle achieved the lowest 12-hour errors, but uses unavailable future observations.

**Table 1. Primary 12-hour test performance.** All volume errors and biases are in m³; n=2,160. Oracle results are diagnostic and non-operational.

| Configuration | MAE | RMSE | R² | Mean bias |
|---|---:|---:|---:|---:|
| Persistence | 3,740.22 | 6,185.43 | 0.219 | 168.45 |
| Previous 24-hour mean | 3,406.61 | 6,128.24 | 0.233 | 229.60 |
| Previous-day profile | 4,056.77 | 7,787.93 | −0.239 | 217.73 |
| Ridge, historical inputs | 4,655.34 | 5,743.78 | 0.326 | 3,250.69 |
| HGB, flow/calendar | 7,543.69 | 8,452.50 | −0.459 | 6,525.91 |
| HGB, historical inputs | 7,607.10 | 8,633.01 | −0.522 | 6,811.40 |
| HGB, perfect future rainfall | 2,044.11 | 2,756.37 | 0.845 | 1,505.88 |

H1 was not supported. Historical HGB minus flow/calendar HGB had a paired MAE difference of +63.41 m³, with an approximate 95% bootstrap interval of −526.35 to +653.47 m³ at the 48-hour maximum block length. H2 was supported within the diagnostic comparison: oracle minus historical HGB differed by −5,563.00 m³, with an interval of −6,163.54 to −4,957.69 m³. The point estimate corresponds to a 73.1% MAE reduction relative to historical HGB, but not relative to the best baseline. The 24- and 168-hour maximum-block analyses did not change the directions of these conclusions.

### 3.3. Conditional interval reliability

The moving-average baseline's pooled residual interval covered 87.5% of test outcomes overall, close to the nominal 90%, but only 23.5% of high-volume outcomes (Table 2). The historical HGB interval covered 49.8% overall and 44.4% in the high-volume subgroup. Oracle coverage was 86.6% overall and 58.0% for high volumes. Thus, H3 was descriptively consistent with the observed coverage patterns, but uncertainty over independent high-volume events remains poorly characterized.

**Table 2. Empirical coverage of nominal 90% intervals at the 12-hour horizon.** The high-volume group comprises 81 windows in five contiguous episodes; wet comprises 707 windows. Values are percentages.

| Configuration | Calibration | Overall | Wet | Dry | High volume |
|---|---|---:|---:|---:|---:|
| Previous 24-hour mean | Pooled | 87.5 | 79.3 | 91.5 | 23.5 |
| Previous 24-hour mean | Wet/dry | 88.1 | 92.9 | 85.8 | 34.6 |
| HGB, historical inputs | Pooled | 49.8 | 35.5 | 56.8 | 44.4 |
| HGB, historical inputs | Wet/dry | 61.9 | 88.1 | 49.1 | 65.4 |
| HGB, perfect rainfall | Pooled | 86.6 | 73.3 | 93.0 | 58.0 |
| HGB, perfect rainfall | Wet/dry | 90.0 | 85.9 | 92.1 | 66.7 |

Wet/dry calibration improved wet-state coverage for the moving-average baseline from 79.3% to 92.9%, while dry-state coverage decreased from 91.5% to 85.8%. The corresponding overall mean interval width increased from 14,046 to 16,210 m³. For the oracle, overall coverage reached 90.0% with wet/dry calibration, yet high-volume coverage remained 66.7%. Stratifying on past rain did not remove all conditional unreliability.

For the moving-average baseline, 54.3% of high-volume outcomes exceeded the pooled upper bound. Its mean positive underprediction was 13,924 m³ in that subgroup. These are forecast errors in cumulative inflow, not measured overflow volumes or estimates of additional tank capacity.

### 3.4. Sensitivity and residual behavior

Horizon-specific performance did not support a universal ranking. Persistence achieved MAE 1,567.68 m³ at six hours, versus 937.85 m³ for the oracle. At 24 hours, the moving-average baseline achieved 6,588.94 m³, slightly below the oracle's 6,617.34 m³. Historical HGB MAE was 2,833.40 and 22,297.85 m³ at six and 24 hours, respectively. Absolute errors should not be compared across horizons as if they represented identical targets or samples.

Historical-HGB test residual autocorrelation was 0.890 at one hour, 0.410 at six hours and 0.153 at 24 hours. The Spearman association between absolute residual magnitude and predicted volume was 0.481. These diagnostics indicate that independent, constant-error assumptions should not be adopted without qualification. The circular group-shift analysis increased MAE by an average of 894 m³ for flow features and 168 m³ for rainfall features; corresponding averages were 41 m³ for calendar features and approximately 1 m³ for other meteorology. These values describe sensitivity of this fitted, poorly transferring model, rather than universal predictor relevance.

## 4. Discussion

### 4.1. Information availability changes the interpretation of model accuracy

The most striking 12-hour contrast was between historical-input HGB and the perfect-rainfall comparator. The difference shows that the specified pipelines behave very differently when future rainfall observations are available. It does not show that a real weather forecast would deliver the same gain. Forecast errors, issue-time alignment, spatial representativeness and data latency could materially alter the result. Moreover, separate hyperparameter selection means the comparison measures a pipeline-level difference, rather than a causal effect of adding one variable.

The DHI example labels its perfect-rainfall assumption explicitly [2]. Our finding is therefore not an allegation of undisclosed leakage in that example. It is an extension that evaluates cumulative volume under a stricter historical-information boundary and reports the resulting conditional reliability. The original XGBoost trajectory benchmark was not reproduced exactly, and no numerical superiority over that implementation is claimed.

The strong performance of simple baselines also changes the engineering interpretation. Historical HGB was not a competitive general replacement for the moving-average baseline on MAE in this holdout period. Nonetheless, ridge's better RMSE and the different high-volume rankings show that no single summary metric fully describes behavior. An operational objective would need a defensible loss function reflecting overprediction and underprediction consequences, which cannot be specified reliably without plant constraints.

### 4.2. Calibration can conceal consequential conditional failures

Overall coverage near 90% was not sufficient evidence of reliability during high-volume conditions. The mean24 baseline covered fewer than one quarter of high-volume outcomes despite covering 87.5% overall. This is a directly observed conditional failure in this dataset. It does not establish its population frequency, because only five contiguous high-volume episodes were available and the windows within each episode overlap.

Wet/dry stratification improved some subgroup results but transferred error elsewhere, as seen in the decline in dry-state coverage for the moving-average baseline. Past rainfall is only one state descriptor; it does not fully encode future rain, antecedent network storage or other unobserved conditions. The results motivate evaluation of adaptive time-series uncertainty approaches such as those developed for dependent data [7], but do not establish that any untested method would solve the observed failures.

### 4.3. Relationship to earlier research and the scope of novelty

Our study is consistent with the importance that prior probabilistic inflow work assigns to rainfall information [3]. It also reinforces the need to evaluate model transfer rather than inferring future performance from development scores, a concern directly examined in the Veas denitrification study [6]. These are shared concerns, not discoveries first made here. The Mediterranean inflow study [4] provides further evidence that the broader application is already well developed, although differences in climate, horizons, targets and data prevent numerical cross-paper ranking.

The narrower contribution is an auditable open-data experiment combining noninterpolated cumulative-volume targets, chronological calibration, a clearly separated oracle information set and high-volume reliability reporting. This combination may support a methodological case study or reproducibility paper after stronger validation. It is not an independent contribution merely because HGB replaces XGBoost. The added scientific content lies in the information-boundary and reliability questions, including negative findings.

## 5. Practical Implications

The reported quantities could inform the specification of a forecasting service: which measurements must exist at issue time, which baseline must be exceeded, what coverage must be checked in high-volume periods, and what assumptions are hidden by aggregate accuracy. For this dataset, choosing a sophisticated historical-input model without the moving-average baseline would have obscured substantial underperformance. Reporting only overall coverage would also have hidden poor performance on high-volume windows.

No recommendation for tank sizing, bypass activation, aeration or energy optimization follows directly. Cumulative inflow alone does not determine the maximum storage excursion because intra-window timing, initial storage, discharge and treatment capacity matter. Energy and treatment benefits require additional measurements and an explicitly validated control or process model. The next operational study should replay real forecast vintages and quantify consequences under recorded plant constraints before proposing automated decisions.

## 6. Limitations

The analysis covers one anonymized plant and approximately 15 months. It lacks an independent-site test and a second full annual cycle. Complete-window selection reduces coverage of missing-data periods and may bias evaluation if outages coincide with extreme conditions. Screening thresholds are heuristic, and upstream sensor processing is not independently audited. The raw archive already contains hourly summaries rather than full sensor-frequency traces.

The chronological holdout is genuinely later than training but is not an independent plant sample. Overlapping targets and residual autocorrelation reduce effective information relative to the nominal number of windows. The shortened-block bootstrap is an approximate resampling scheme and does not account for all seasonal nonstationarity, model-selection uncertainty or site variability. High-volume inference is especially limited by five contiguous episodes. Temporal distribution differences were measured, but their causal role in HGB performance was not established.

We evaluated a modest hyperparameter grid and a limited model family. No adaptive refitting, SPCI implementation or mechanistic inflow model was tested. Thus, poor historical HGB performance is not evidence that historical-only forecasting is inherently infeasible. The oracle is neither deployable nor a mathematical upper bound on forecast skill. Weather forecast vintages, timing latency, network configuration, effluent quality, energy and control outcomes are unavailable. Finally, the targeted literature search had rate-limited and inaccessible sources, and does not establish exhaustive novelty.

## 7. Conclusions

On a temporally held-out period of the DHI dataset, the preceding-24-hour mean was the strongest historical-information configuration by 12-hour cumulative-volume MAE. Adding past meteorology to the selected HGB pipeline did not produce a stable gain, while a perfect-future-rainfall comparator substantially improved 12-hour performance. However, even near-nominal overall interval coverage could coexist with severe high-volume undercoverage. These findings support explicit information-boundary audits, simple baselines and conditional reliability assessment before operational interpretation. Independent plants, more events and actual weather forecasts are required to test generality and practical value.

## Data Availability Statement

The source observations are available from DHI, *Inflow to a Waste Water Treatment Plant: observations and processed data*, version 1, Zenodo, DOI [10.5281/zenodo.15301164](https://doi.org/10.5281/zenodo.15301164), with CC BY-NC 4.0 recorded in the archive metadata. DHI and the Danish Meteorological Institute are credited for plant and meteorological data, respectively. The accompanying research package contains unchanged source archives, checksums, derived hourly data and forecasts. Derived files identify their transformations; no new measurement campaign was performed.

## Code Availability Statement

The accompanying reproducibility package includes `download_data.py`, `run_analysis.py`, `verify_results.py`, bibliography/table-generation scripts, a prespecified analysis protocol, exact dependency versions and all numerical outputs. Newly authored Python code is provided under MIT terms; data and third-party materials retain their own conditions. The code and reproducibility materials are provided at [https://github.com/phamnam123lite-svg/wastewater-inflow-volume-open-science](https://github.com/phamnam123lite-svg/wastewater-inflow-volume-open-science), version 0.1.0. The repository provides standalone analysis scripts and a complete supplementary archive containing the source data, results, figures, protocol and clean-environment verification. All 13 compared numerical CSV outputs were reproduced with zero maximum absolute difference. A GitHub version is not a DOI archive; no code DOI is claimed. The DHI DOI identifies the source data, not this analysis.

## References

1. Yang, W., and Li, H. (2025). Machine Learning in Wastewater Treatment: A Comprehensive Bibliometric Review. *ACS ES&T Water*, 5, 511–524. [https://doi.org/10.1021/acsestwater.4c01047](https://doi.org/10.1021/acsestwater.4c01047).

2. DHI (2025). *Inflow to a Waste Water Treatment Plant: observations and processed data*, version 1. Zenodo. [https://doi.org/10.5281/zenodo.15301164](https://doi.org/10.5281/zenodo.15301164). Original modelling example: [DHI repository](https://github.com/DHI/WaterBench-TimeSeries-WWTPINflow), inspected commit 68cc22b5de3bbbc09c0bf63c6d5a9ef376d5fd6c; source data remain pinned to Zenodo v1.

3. Sonnenschein, B., and Ziel, F. (2023). Probabilistic Intraday Wastewater Treatment Plant Inflow Forecast Utilizing Rain Forecast Data and Sewer Network Sensor Data. *Water Resources Research*, 59, e2022WR033826. [https://doi.org/10.1029/2022WR033826](https://doi.org/10.1029/2022WR033826).

4. González Barberá, A., et al. (2025). Machine Learning-Based Forecasting of Wastewater Inflow During Rain Events at a Spanish Mediterranean Coastal WWTPs. *Water*, 17, 3225. [https://doi.org/10.3390/w17223225](https://doi.org/10.3390/w17223225). Complete author metadata is included in the accompanying bibliography.

5. Roberts, D. R., et al. (2017). Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure. *Ecography*, 40, 913–929. [https://doi.org/10.1111/ecog.02881](https://doi.org/10.1111/ecog.02881). Complete author metadata is included in the accompanying bibliography.

6. Bøhn, E., Eidnes, S., and Jonassen, K. R. (2024). Machine learning in wastewater treatment: insights from modelling a pilot denitrification reactor. *arXiv preprint*, arXiv:2412.14030. [https://arxiv.org/abs/2412.14030](https://arxiv.org/abs/2412.14030).

7. Xu, C., and Xie, Y. (2023). Sequential Predictive Conformal Inference for Time Series. *Proceedings of the 40th International Conference on Machine Learning*, PMLR 202, 38707–38727. [https://proceedings.mlr.press/v202/xu23r.html](https://proceedings.mlr.press/v202/xu23r.html).

## Open Science and Reproducibility

The analysis protocol was recorded before the initial model fits, but was not preregistered in an independent registry. All observed outcomes, preprocessing rules, parameter grids, predictions and negative findings are retained. The reproducibility package includes a clean-environment rerun, numerical comparison against the original results, source-data hashes and automated chronology and feature-causality checks. This computational reproduction is not independent scientific replication or external-site validation. Data remain subject to CC BY-NC 4.0; newly authored analysis code is MIT licensed. AI assistance was used for literature discovery, programming, analysis and manuscript drafting. The named author must review the work, verify all claims and take responsibility for the final submission.

## Figure captions

**Figure 1.** Raw-derived hourly flow and rainfall with development/calibration/test boundaries. Gaps are retained; lines do not imply that every target window is eligible. File: `figures/01_data_timeline`.

**Figure 2.** Twelve-hour MAE overall and in high-volume windows. “hgb_oracle” uses future observed rain and is diagnostic only. High volume is defined from the training-target 90th percentile; n=81 test windows. File: `figures/02_model_errors`.

**Figure 3.** Pooled 90% residual-interval coverage overall, in wet states and in high-volume windows. The dashed line is nominal coverage, not an achieved guarantee. File: `figures/03_interval_coverage`.

**Figure 4.** The first 14 days of test issue times, selected by date rather than prediction error, showing observed cumulative volume, historical HGB predictions and pooled residual intervals. File: `figures/04_test_example`.

**Figure 5.** Historical-HGB group-shift sensitivity. Bars show mean MAE increase across 20 circular shifts; error bars show standard deviation across perturbations, not confidence intervals. File: `figures/05_feature_sensitivity`.
