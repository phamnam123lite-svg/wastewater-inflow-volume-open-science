"""External-site methodological replication on pinned Koeln-Weiden observations.
Archive clock is retained (time zone unspecified); no operational forecast claim.
"""
from pathlib import Path
import argparse,json,hashlib
import numpy as np
import pandas as pd
import requests
from sklearn.model_selection import GridSearchCV,TimeSeriesSplit
import run_analysis as a
ROOT=Path(__file__).resolve().parent

def download():
    p=ROOT/'external_data';p.mkdir(exist_ok=True)
    r=requests.get('https://zenodo.org/api/records/6992694',timeout=90);r.raise_for_status();m=r.json()
    if m['doi']!='10.5281/zenodo.6992694' or m['metadata']['license']['id']!='cc-by-4.0':raise ValueError('Unexpected source identity/license')
    (p/'zenodo_6992694.json').write_text(json.dumps(m,indent=2))
    f=next(f for f in m['files'] if f['key']=='wtp_network_rain.csv');target=p/f['key']
    if target.exists():blob=target.read_bytes()
    else:
        r=requests.get(f['links']['self'],timeout=120);r.raise_for_status();blob=r.content
    if hashlib.md5(blob).hexdigest()!='40089e2901bca458818726092c51a4db':raise ValueError('Pinned source checksum mismatch')
    target.write_bytes(blob)

def load():
    path=ROOT/'external_data/wtp_network_rain.csv'
    if hashlib.md5(path.read_bytes()).hexdigest()!='40089e2901bca458818726092c51a4db':raise ValueError('Raw file changed')
    raw=pd.read_csv(path,sep=';',index_col=0,parse_dates=True)
    if raw.index.duplicated().any() or not raw.index.is_monotonic_increasing:raise ValueError('Invalid timestamp order')
    if not (raw.index.to_series().diff().dropna()==pd.Timedelta(minutes=15)).all():raise ValueError('Unexpected sampling grid')
    flow=raw['wtp_inflow [l/s]'];rain=raw['rain_rate [mm/min]']
    flow=flow.where(np.isfinite(flow)&flow.ge(0));rain=rain.where(np.isfinite(rain)&rain.ge(0))
    # Right-closed windows guarantee no use of observations after the issue stamp.
    fg=flow.resample('h',closed='right',label='right');rg=rain.resample('h',closed='right',label='right')
    d=pd.DataFrame({'flow':(fg.mean()*3.6).where(fg.count()==4),
                    'acc_precip':(rg.sum(min_count=4)*15).where(rg.count()==4)})
    for c in ['mean_pressure','mean_radiation','mean_relative_hum','mean_temp']:d[c]=np.nan
    info={'source_doi':'10.5281/zenodo.6992694','license':'CC BY 4.0','raw_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
      'raw_rows':len(raw),'start':str(raw.index.min()),'end':str(raw.index.max()),'raw_missing_flow':int(flow.isna().sum()),
      'raw_missing_rain':int(rain.isna().sum()),'hourly_rows':len(d),'hourly_missing_flow':int(d.flow.isna().sum()),
      'hourly_missing_rain':int(d.acc_precip.isna().sum()),'clock':'Provider-naive uniform clock; time zone unverified',
      'aggregation':'Four samples in (t-1h,t]; mean flow L/s times 3.6; sum rain mm/min times 15 min. No interpolation.'}
    return raw,d,info

def masks(d,v):
    return a.split_masks(d.index,v,12,pd.Timestamp('2019-01-01'),pd.Timestamp('2019-04-01'),pd.Timestamp('2020-01-01'))

def run(out):
    if (out/'reference_manifest.json').exists():
        raise ValueError('Refusing to overwrite registered reference results; choose a new --output directory')
    out.mkdir(parents=True,exist_ok=True);raw,d,info=load();x,y,b,v,fc,_=a.features(d,12);hc=fc+[c for c in x if c.startswith('rain_')];oc=hc+['ORACLE_rain_sum','ORACLE_rain_max']
    m=masks(d,v);tr,ca,te=[m[s] for s in ['train','calibration','test']];threshold=float(y[tr].quantile(.9));info['high_threshold_m3']=threshold
    d[['flow','acc_precip']].to_csv(out/'external_hourly.csv',index_label='provider_hour_ending')
    split=[]
    for key,mask in m.items():split.append(dict(split=key,n=int(mask.sum()),start=str(d.index[mask].min()),end=str(d.index[mask].max()),mean_target=float(y[mask].mean())))
    pd.DataFrame(split).to_csv(out/'external_splits.csv',index=False)
    cal=pd.DataFrame({'observed':y[ca],'wet':x.loc[ca,'rain_sum6'].gt(0),'high':y[ca]>threshold})
    test=pd.DataFrame({'observed':y[te],'wet':x.loc[te,'rain_sum6'].gt(0),'high':y[te]>threshold})
    for n in b:cal[n]=b.loc[ca,n];test[n]=b.loc[te,n]
    cv=TimeSeriesSplit(n_splits=3,gap=12);cvrows=[];folds=[];selected={}
    for fold,(itr,iva) in enumerate(cv.split(x[tr])):
        idx=x.index[tr];folds.append(dict(fold=fold,last_training_issue=str(idx[itr[-1]]),last_training_target=str(idx[itr[-1]]+12*a.HOUR),first_validation_issue=str(idx[iva[0]])))
    for name,cols in [('hgb_flow',fc),('hgb_rain',hc),('hgb_oracle',oc)]:
        pipe=a.hgb_model();grid={'annual__include_annual':[True,False],'model__loss':['squared_error','absolute_error'],
          'model__max_leaf_nodes':[7,15],'model__l2_regularization':[1.,10.]}
        search=GridSearchCV(pipe,grid,cv=cv,scoring='neg_mean_absolute_error',n_jobs=1,error_score='raise').fit(x.loc[tr,cols],y[tr])
        selected[name]=search.best_params_;pipe=search.best_estimator_
        for j,params in enumerate(search.cv_results_['params']):
            for f in range(3):cvrows.append(dict(model=name,candidate=j,fold=f,params=json.dumps(params,sort_keys=True),MAE_m3=-search.cv_results_[f'split{f}_test_score'][j],selected=j==search.best_index_))
        cal[name]=np.maximum(0,pipe.predict(x.loc[ca,cols]));test[name]=np.maximum(0,pipe.predict(x.loc[te,cols]));print(name,search.best_params_,a.metrics(test.observed,test[name]),flush=True)
    fixed=[('fixed_sq_annual',hc,'squared_error',True),('fixed_sq_noannual',hc,'squared_error',False),
      ('fixed_abs_annual',hc,'absolute_error',True),('fixed_abs_noannual',hc,'absolute_error',False),
      ('fixed_flow_abs',fc,'absolute_error',False),('fixed_oracle_abs',oc,'absolute_error',False)]
    for name,cols,loss,annual in fixed:
        pipe=a.hgb_model().set_params(model__loss=loss,annual__include_annual=annual,model__max_leaf_nodes=7,model__l2_regularization=1.)
        pipe.fit(x.loc[tr,cols],y[tr]);cal[name]=np.maximum(0,pipe.predict(x.loc[ca,cols]));test[name]=np.maximum(0,pipe.predict(x.loc[te,cols]))
    mm=[];ii=[];bounds=[];boot=[];episodes=[];phases=[]
    names=[c for c in test if c not in ['observed','wet','high']]
    for name in names:
        for group,mask in [('all',np.ones(len(test),bool)),('wet',test.wet),('dry',~test.wet),('high',test.high)]:
            if mask.sum():
                row=dict(model=name,group=group,**a.metrics(test.observed[mask],test.loc[mask,name]));row['MAE_over_mean_target']=row['MAE_m3']/float(test.observed[mask].mean());mm.append(row)
        for method in ['pooled','wet_dry','rolling30d']:
            lo,hi=a.interval_bounds(cal,test,name,12,method);obs=test.observed.to_numpy();cov=(obs>=lo)&(obs<=hi);score=hi-lo+20*np.maximum(lo-obs,0)+20*np.maximum(obs-hi,0)
            bounds.append(pd.DataFrame(dict(provider_issue_time=test.index,model=name,method=method,lower=lo,upper=hi)))
            for group,mask in [('all',np.ones(len(test),bool)),('wet',test.wet),('dry',~test.wet),('high',test.high)]:
                if mask.sum():ii.append(dict(model=name,method=method,group=group,n=int(mask.sum()),coverage=float(cov[mask].mean()),width_m3=float((hi-lo)[mask].mean()),interval_score_m3=float(score[mask].mean()),upper_exceedance=float((obs[mask]>hi[mask]).mean())))
        if name in ['mean24','hgb_flow','hgb_rain','hgb_oracle']:
            lo,hi=a.interval_bounds(cal,test,name,12,'pooled');cov=pd.Series((test.observed>=lo)&(test.observed<=hi),index=test.index)
            high=test.index[test.high];cuts=np.r_[0,np.flatnonzero(np.diff(high.as_unit('ns').asi8)!=3600*10**9)+1,len(high)]
            for event,(s,e) in enumerate(zip(cuts[:-1],cuts[1:])):
                if s==e:continue
                ts=high[s:e];episodes.append(dict(model=name,episode=event+1,start=str(ts.min()),end=str(ts.max()),n=len(ts),coverage=float(cov[ts].mean())))
            phase=((test.index-d.index.min())/a.HOUR).astype(int)%12
            for ph in range(12):
                mask=phase==ph;hi_mask=mask&test.high;phases.append(dict(model=name,phase=ph,n=int(mask.sum()),n_high=int(hi_mask.sum()),coverage=float(cov[mask].mean()),high_coverage=float(cov[hi_mask].mean()) if hi_mask.sum() else np.nan))
    for aa,bb in [('hgb_rain','hgb_flow'),('hgb_oracle','hgb_rain'),('hgb_flow','mean24'),('hgb_rain','mean24'),
      ('fixed_abs_noannual','fixed_flow_abs'),('fixed_oracle_abs','fixed_abs_noannual')]:
        diff=np.abs(test[aa]-test.observed)-np.abs(test[bb]-test.observed)
        for B in [24,48,168]:boot.append(dict(comparison=aa+' minus '+bb,block_hours=B,**a.bootstrap(diff,test.index,B)))
    cal.to_csv(out/'external_calibration.csv',index_label='provider_issue_time');test.to_csv(out/'external_predictions.csv',index_label='provider_issue_time')
    pd.concat(bounds,ignore_index=True).to_csv(out/'external_bounds.csv',index=False)
    for n,rows in [('external_metrics',mm),('external_intervals',ii),('external_bootstrap',boot),('external_cv_scores',cvrows),('external_cv_folds',folds),('external_episodes',episodes),('external_nonoverlap',phases)]:pd.DataFrame(rows).to_csv(out/(n+'.csv'),index=False)
    (out/'external_source_audit.json').write_text(json.dumps(info,indent=2));(out/'external_selected_parameters.json').write_text(json.dumps(selected,indent=2))
    print('EXTERNAL COMPLETE',out,flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'reproduced/german');p.add_argument('--download',action='store_true');args=p.parse_args()
    if args.download:download()
    run(args.output)
