# Targeted prior-art and novelty matrix

Updated 10 November 2026. This is a targeted audit, not an exhaustive systematic review. Full bibliographic identities are in the manuscript and `paper/references.bib`. “Different” does not imply scientifically novel.

| Study / source | Verified relationship to this study | Overlap | What this analysis adds / does not claim |
|---|---|---|---|
| DHI Zenodo v1, 10.5281/zenodo.15301164; provider example | Same source dataset; provider example includes ideal future precipitation and trajectory prediction | Dataset and rainfall-aware boosted-model family | Integrated-rate target, distinct eligibility, temporal audit and released calibration bounds; no exact reproduction of the provider example or new measurement campaign |
| Sonnenschein & Ziel 2023, 10.1029/2022WR033826 | Probabilistic intraday WWTP forecasting with rain forecasts and sewer sensors | Inflow/rainfall/probabilistic prediction question | Different data and information inputs; no direct numerical ranking or claim that rainfall-aware forecasting is new |
| González Barberá et al. 2025, 10.3390/w17223225 | Rain-event wastewater inflow forecasting at Mediterranean coastal WWTPs; publisher methods/data statement inspected | ML/rain-event forecasting | Different site/target/evaluation; no cross-paper accuracy comparison |
| Pearson et al. 2025, arXiv:2506.08577v1 | Four-page sewer forecasting conference paper with diffusion and calibration; full text inspected | Wet/dry and probabilistic sewer reliability | Different target and model; prevents claiming wet/dry calibration novelty |
| Lee & Lee 2026, PMLR329:1043-1045 | Publisher abstract: wastewater pH under drift, static/weighted/adaptive and rolling approaches | Drift and empirical interval adaptation | Different pH target, not same DHI observations; prevents claiming adaptation itself is new |
| Xu & Xie 2023, PMLR202:38707-38727 | Time-series residual-quantile framework (SPCI) | Dependence-aware interval motivation | This release does NOT implement SPCI and inherits no SPCI theorem |
| Bøhn, Eidnes & Jonassen 2024, arXiv:2412.14030 | Three-author record and wastewater process transfer context verified | Distribution change and model transfer | Different process/data; supporting context only |
| Roberts et al. 2017, 10.1111/ecog.02881 | Structured temporal validation methodology | Validation motivation | Does not validate this custom bootstrap or guarantee its coverage |
| Alsumaiei 2026, 10.2166/wst.2026.205 | Crossref identity and monthly influent topic verified; full text inaccessible | Related inflow modelling | Catalogue only, not used to assert full-method equivalence or support a major manuscript claim |

The restricted contribution is an executable configuration-and-information audit of a cumulative hydraulic target on open observations, with explicit retrospective status. There is no verified evidence sufficient to call it the first such study. All headline numerical comparisons are internal comparisons on common eligible windows. The review adds rather than hides close prior work.

Primary verification links: https://arxiv.org/abs/2506.08577 ; https://proceedings.mlr.press/v329/lee26a.html ; https://proceedings.mlr.press/v202/xu23r.html ; https://zenodo.org/records/15301164 . Existing Crossref/provider inspection records are retained in sources/.

## Added external source and an additional close comparator

Sonnenschein and Ziel's German observations, DOI 10.5281/zenodo.6992694, are now used as an external-site methodological replication. This is the same dataset used in their prior intraday study; our integrated 12-hour target, temporal split, HGB configuration audit and residual-calibration comparison differ. Dataset reuse is explicit and is not called new data or exact reproduction of their published method. Their radar forecast record is 6992869; a malformed DOI in a publisher-rendered availability sentence was not copied as a verified identifier.

Mateos-Bravo et al. (2026), Data Quality over Model Complexity: A Leakage-Aware, Horizon-Aware Forecasting Pipeline for Degraded Sensor Streams in a Small-Population Wastewater Treatment Plant, Zenodo 10.5281/zenodo.20596898 v2, was also inspected. Its public record explicitly contains derived figures/metrics/prediction arrays, not raw measurements or source code. It is relevant to the non-novelty of leakage-aware wastewater forecasting but cannot supply raw inflow/rain data for this evaluation. It is catalogued here rather than treated as a full-text peer-reviewed methodological comparison.

The Mediterranean coastal WWTP paper (10.3390/w17223225) explicitly makes raw utility data available only on reasonable request subject to permission/data-use agreement. That prevents immediate open reproduction and is why it was not selected as the additional site. No request was sent to its authors.
