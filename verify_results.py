"""Independent checks of saved outcomes, metrics, time separation and feature causality."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from run_analysis import features
P=Path(__file__).resolve().parent;R=P/'results'
d=pd.read_csv(R/'cleaned_hourly.csv',index_col=0,parse_dates=True)
splits=pd.read_csv(R/'splits.csv');scores=pd.read_csv(R/'metrics.csv')
checks=[]
for h in [6,12,24]:
    p=pd.read_csv(R/f'predictions_{h}h.csv',index_col=0,parse_dates=True)
    assert p.index.is_unique and p.index.is_monotonic_increasing
    # Guard against treating every hour as a gap when datetime units change.
    assert (np.diff(p.index.as_unit('ns').asi8)==3600*10**9).mean()>.9
    assert p.notna().all().all()
    expected=np.array([d.loc[t+pd.Timedelta(hours=1):t+pd.Timedelta(hours=h),'flow'].sum(min_count=h) for t in p.index])
    np.testing.assert_allclose(p.observed,expected,rtol=1e-12)
    s=splits[splits.horizon==h].set_index('split')
    assert pd.Timestamp(s.loc['train','end'])+pd.Timedelta(hours=h)<pd.Timestamp(s.loc['calibration','start'])
    assert pd.Timestamp(s.loc['calibration','end'])+pd.Timedelta(hours=h)<pd.Timestamp(s.loc['test','start'])
    for name in ['persistence','mean24','seasonal24','ridge_history','hgb_flow','hgb_history','hgb_oracle']:
        m=scores[(scores.horizon==h)&(scores.model==name)&(scores.group=='all')].iloc[0]
        np.testing.assert_allclose(np.mean(np.abs(p.observed-p[name])),m.MAE_m3)
        np.testing.assert_allclose(np.sqrt(np.mean((p.observed-p[name])**2)),m.RMSE_m3)
        assert (p[name+'_lower']<=p[name+'_upper']).all()
    # Perturb every future observation: historical features at t must remain unchanged.
    t=p.index[len(p)//2];changed=d.copy();changed.loc[changed.index>t,:]*=7
    x,_,_,_,_,hc=features(d,h);xx,_,_,_,_,_=features(changed,h)
    np.testing.assert_allclose(x.loc[t,hc],xx.loc[t,hc],equal_nan=True)
    checks.append({'horizon':h,'n_forecasts':len(p),'target_sums':'pass','chronology':'pass','saved_metrics':'pass','future_perturbation_causality':'pass'})
(R/'verification.json').write_text(json.dumps(checks,indent=2))
print(json.dumps(checks,indent=2))
