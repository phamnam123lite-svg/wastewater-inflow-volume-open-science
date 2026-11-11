"""Coverage of the 90% intervals in high-volume windows defined by the FORECAST (observable at issue time).

The manuscript's high-volume subgroup is defined by the observed outcome (target above the development
90th percentile). Conditioning on the outcome selects windows with large errors, so this script adds the
issue-time counterpart: windows whose forecast from the same model exceeds the same threshold.
Computed from saved forecasts and interval bounds only (no refitting).

    python src/forecast_high_coverage.py --results reproduced/denmark --site denmark
    python src/forecast_high_coverage.py --results reproduced/germany --site germany
"""
from pathlib import Path
import argparse, json
import pandas as pd

SITES = {'denmark': dict(pred='predictions_primary_12h.csv', bounds='bounds_primary_12h.csv', key='issue_time_utc',
                         models=['mean24', 'hgb_history', 'hgb_oracle'], out='forecast_high_coverage.csv'),
         'germany': dict(pred='external_predictions.csv', bounds='external_bounds.csv', key='provider_issue_time',
                         models=['mean24', 'hgb_rain', 'hgb_oracle'], out='external_forecast_high_coverage.csv')}

def threshold(results, site):
    if site == 'denmark':
        s = pd.read_csv(results / 'splits.csv')
        return float(s[(s.scenario == 'primary_12h') & (s.split == 'test')].high_threshold_m3.iloc[0])
    return float(json.loads((results / 'external_source_audit.json').read_text())['high_threshold_m3'])

def main(results, site):
    cfg = SITES[site]; thr = threshold(results, site)
    test = pd.read_csv(results / cfg['pred'], index_col=0, parse_dates=True)
    bounds = pd.read_csv(results / cfg['bounds'], parse_dates=[cfg['key']]).set_index(cfg['key'])
    y = test['observed'].to_numpy(); observed_high = test['high'].to_numpy(); rows = []
    for model in cfg['models']:
        forecast_high = test[model].to_numpy() > thr
        for method in ['pooled', 'wet_dry', 'rolling30d']:
            b = bounds[(bounds.model == model) & (bounds.method == method)].loc[test.index]
            covered = (y >= b['lower'].to_numpy()) & (y <= b['upper'].to_numpy())
            rows.append(dict(model=model, method=method, threshold_m3=thr,
                             n_forecast_high=int(forecast_high.sum()), coverage_forecast_high=float(covered[forecast_high].mean()),
                             n_observed_high=int(observed_high.sum()), coverage_observed_high=float(covered[observed_high].mean()),
                             n_both=int((forecast_high & observed_high).sum())))
    pd.DataFrame(rows).to_csv(results / cfg['out'], index=False)

if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--results', type=Path, required=True); p.add_argument('--site', choices=SITES, required=True)
    a = p.parse_args(); main(a.results, a.site)
