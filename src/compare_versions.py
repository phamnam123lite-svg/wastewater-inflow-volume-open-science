"""Summarize how the results change when the same code and data run with newer library versions.

Reads the reference results (pinned environment) and results/version_sensitivity (see its
environment.json) and writes results/version_sensitivity/summary.csv: MAE for every scenario and model
in both environments, plus the changed development selections.

    python src/compare_versions.py
"""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REF_DK, REF_DE, ALT = ROOT / 'results' / 'denmark', ROOT / 'results' / 'germany', ROOT / 'results' / 'version_sensitivity'

def main():
    rows = []
    for site, ref, alt, key in [('denmark', REF_DK / 'metrics.csv', ALT / 'metrics.csv', ['scenario', 'model']),
                                ('germany', REF_DE / 'external_metrics.csv', ALT / 'external_metrics.csv', ['model'])]:
        r, a = pd.read_csv(ref), pd.read_csv(alt)
        m = r[r.group == 'all'].merge(a[a.group == 'all'], on=key + ['group'], suffixes=('_pinned', '_newer'))
        for _, x in m.iterrows():
            rows.append(dict(site=site, scenario=x.get('scenario', 'external_12h'), model=x['model'], MAE_pinned_m3=x['MAE_m3_pinned'],
                             MAE_newer_m3=x['MAE_m3_newer'], difference_m3=x['MAE_m3_newer'] - x['MAE_m3_pinned']))
    out = pd.DataFrame(rows)
    sel_r = json.loads((REF_DK / 'selected_parameters.json').read_text()); sel_a = json.loads((ALT / 'selected_parameters.json').read_text())
    changed = [(s, m) for s in sel_r for m in sel_r[s] if sel_r[s][m] != sel_a[s][m]]
    out['selection_changed'] = [(r.scenario, r.model) in changed for r in out.itertuples()]
    out.to_csv(ALT / 'summary.csv', index=False)
    print(f'Danish development selections changed: {len(changed)} of {sum(len(v) for v in sel_r.values())}')
    print('Largest absolute MAE changes (m3):')
    print(out.reindex(out.difference_m3.abs().sort_values(ascending=False).index).head(8).round(1).to_string(index=False))

if __name__ == '__main__':
    main()
