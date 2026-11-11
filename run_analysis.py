"""Retrospective, deterministic wastewater forecast audit. Python 3.11; see protocol.
Run: python run_analysis.py --output results
Only archived observations are used. Oracle columns are deliberately non-operational.
"""
import os
os.environ.setdefault('OMP_NUM_THREADS', '2')
os.environ.setdefault('OPENBLAS_NUM_THREADS', '2')
from pathlib import Path
import argparse, hashlib, importlib.metadata, json, platform, sys
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

ROOT = Path(__file__).resolve().parent
SEED = 20261110
HOUR = pd.Timedelta(hours=1)

def read_data(path=ROOT/'data', qc=True):
    raw = pd.read_csv(Path(path)/'wwtp.csv', sep=';')
    ix = pd.DatetimeIndex(pd.to_datetime(raw.iloc[:, 0])).tz_localize(
        'Europe/Copenhagen', ambiguous='NaT', nonexistent='NaT').tz_convert('UTC').tz_localize(None)
    flow = pd.Series(raw.flow.to_numpy(), index=ix, name='flow_raw')
    audit = {'raw_flow_rows':len(raw), 'ambiguous_timestamps_removed':int(ix.isna().sum()),
             'duplicate_valid_utc_timestamps':int(ix[~ix.isna()].duplicated().sum())}
    flow = flow[~flow.index.isna()].groupby(level=0).mean()
    met = pd.read_csv(Path(path)/'dmi.csv', index_col=0, parse_dates=True)
    d = met.join(flow, how='outer').sort_index().asfreq('h')
    low = d.flow_raw.lt(2)
    flat = (d.flow_raw.rolling(6,min_periods=6).max()-d.flow_raw.rolling(6,min_periods=6).min()).lt(5)
    d['flow'] = d.flow_raw.mask(low|flat) if qc else d.flow_raw
    d['mean_relative_hum'] = d.mean_relative_hum.mask(~d.mean_relative_hum.between(0,100))
    audit.update(grid_rows=len(d),start=str(d.index.min()),end=str(d.index.max()),
                 low_flags=int(low.sum()),flat_flags=int(flat.sum()),
                 missing=d.isna().sum().to_dict())
    return d, audit

def features(d,h,delay=0):
    # Shift all measured history together; calendar refers to the actual issue time.
    z=d.shift(delay);x=pd.DataFrame(index=d.index)
    for lag in [0,1,2,3,6,12,24,48,168]:x[f'flow_lag{lag}']=z.flow.shift(lag)
    for w in [6,12,24]:
        x[f'flow_mean{w}']=z.flow.rolling(w).mean();x[f'flow_std{w}']=z.flow.rolling(w).std()
    for name,v,period in [('hour',d.index.hour,24),('weekday',d.index.dayofweek,7),('annual',d.index.dayofyear,365.25)]:
        x[name+'_sin']=np.sin(2*np.pi*v/period);x[name+'_cos']=np.cos(2*np.pi*v/period)
    fc=list(x)
    for w in [1,6,12,24,72]:x[f'rain_sum{w}']=z.acc_precip.rolling(w).sum()
    for c in ['mean_pressure','mean_radiation','mean_relative_hum','mean_temp']:
        x[c]=z[c];x[c+'_mean6']=z[c].rolling(6).mean()
    hc=list(x)
    rain=pd.concat([d.acc_precip.shift(-k) for k in range(1,h+1)],axis=1)
    x['ORACLE_rain_sum']=rain.sum(axis=1,min_count=h);x['ORACLE_rain_max']=rain.max(axis=1)
    y=pd.concat([d.flow.shift(-k) for k in range(1,h+1)],axis=1).sum(axis=1,min_count=h)
    b=pd.DataFrame({'persistence':h*z.flow,'mean24':h*z.flow.rolling(24).mean(),
      'seasonal24':pd.concat([d.flow.shift(24-k+delay) for k in range(1,h+1)],axis=1).sum(axis=1,min_count=h)},index=d.index)
    valid=y.notna()&b.notna().all(axis=1)&x.rain_sum6.notna()&x.ORACLE_rain_sum.notna()
    return x,y,b,valid,fc,hc

class AnnualSelector(TransformerMixin,BaseEstimator):
    def __init__(self,include_annual=True):self.include_annual=include_annual
    def fit(self,X,y=None):return self
    def transform(self,X):
        return X if self.include_annual else X.drop(columns=['annual_sin','annual_cos'])

def hgb_model():
    return Pipeline([('annual',AnnualSelector()),('impute',SimpleImputer(strategy='median',add_indicator=True)),
      ('model',HistGradientBoostingRegressor(max_iter=150,learning_rate=.05,min_samples_leaf=30,
       early_stopping=False,random_state=SEED))])

def exact_quantile(scores,p=.9):
    a=np.asarray(scores,dtype=float)
    if a.ndim!=1 or len(a)==0 or not np.isfinite(a).all():raise ValueError('nonempty finite vector required')
    if not 0<p<1:raise ValueError('probability must be in (0,1)')
    k=int(np.ceil((len(a)+1)*p))
    return float('inf') if k>len(a) else float(np.partition(a,k-1)[k-1])

def metrics(y,p):
    y=np.asarray(y);p=np.asarray(p)
    return dict(n=len(y),MAE_m3=float(mean_absolute_error(y,p)),RMSE_m3=float(np.sqrt(mean_squared_error(y,p))),
      R2=float(r2_score(y,p)) if len(y)>1 else np.nan,bias_m3=float(np.mean(p-y)),
      mean_underprediction_m3=float(np.maximum(y-p,0).mean()))

def circular_blocks(index,B):
    ix=pd.DatetimeIndex(index).as_unit('ns').asi8
    cuts=np.r_[0,np.flatnonzero(np.diff(ix)!=3600*10**9)+1,len(ix)]
    out=np.empty((len(ix),B),dtype=int)
    for s,e in zip(cuts[:-1],cuts[1:]):out[s:e]=s+(np.arange(e-s)[:,None]+np.arange(B))%(e-s)
    return out

def bootstrap(values,index,B,nboot=2000):
    a=np.asarray(values);blocks=circular_blocks(index,B);n=len(a)
    rng=np.random.default_rng(SEED+B);full,rem=divmod(n,B)
    sums=a[blocks].sum(axis=1)
    out=sums[rng.integers(n,size=(nboot,full))].sum(axis=1)
    if rem:out+=a[blocks[:,:rem]].sum(axis=1)[rng.integers(n,size=nboot)]
    out/=n
    return dict(MAE_difference=float(a.mean()),bootstrap_mean=float(out.mean()),
      sensitivity_low=float(np.quantile(out,.025)),sensitivity_high=float(np.quantile(out,.975)))

def interval_bounds(cal,test,model,h,method):
    scores=np.abs(cal.observed-cal[model]);q=exact_quantile(scores)
    radii=np.full(len(test),q)
    if method=='wet_dry':
        for state in [False,True]:
            s=scores[cal.wet==state]
            if len(s)>=30:radii[test.wet.to_numpy()==state]=exact_quantile(s)
    elif method=='rolling30d':
        allp=pd.concat([cal,test]);mature=allp.index+pd.Timedelta(hours=h)
        residuals=np.abs(allp.observed-allp[model]).to_numpy()
        for j,t in enumerate(test.index):
            eligible=(mature<=t)&(mature>t-pd.Timedelta(days=30))
            if eligible.sum()>=30:radii[j]=exact_quantile(residuals[eligible])
    elif method!='pooled':raise ValueError(method)
    p=test[model].to_numpy()
    return np.maximum(0,p-radii),p+radii

def split_masks(index,valid,h,train_end,test_start,test_end):
    end=index+pd.Timedelta(hours=h)
    return {'train':valid&(end<train_end),'calibration':valid&(index>=train_end)&(end<test_start),
      'test':valid&(index>=test_start)&(end<test_end)}

def scenarios(d):
    c1=d.index[int(.6*len(d))];c2=d.index[int(.8*len(d))];end=d.index.max()+HOUR
    out=[(f'primary_{h}h',h,c1,c2,end) for h in [12,6,24]]
    for date in ['2024-08-15','2024-10-15','2024-12-15']:
        start=pd.Timestamp(date);out.append(('origin_'+date,12,start-pd.Timedelta(days=45),start,start+pd.Timedelta(days=60)))
    return out

def run(out):
    if (out/'reference_manifest.json').exists():
        raise ValueError('Refusing to overwrite registered reference results; choose a new --output directory')
    out.mkdir(parents=True,exist_ok=True);d,audit=read_data()
    (out/'data_audit.json').write_text(json.dumps(audit,indent=2))
    d.to_csv(out/'cleaned_hourly.csv',index_label='time_utc')
    rows={k:[] for k in ['metrics','intervals','bootstrap','splits','cv_scores','cv_folds','episodes','leave_one_episode_out','nonoverlap','sensitivity']}
    selected={};primary=None
    for name,h,c1,c2,c3 in scenarios(d):
        print('SCENARIO',name,flush=True)
        x,y,b,v,fc,hc=features(d,h);m=split_masks(d.index,v,h,c1,c2,c3)
        tr,ca,te=[m[k] for k in ['train','calibration','test']]
        threshold=float(y[tr].quantile(.9))
        for split,mask in m.items():
            times=d.index[mask];rows['splits'].append(dict(scenario=name,horizon=h,split=split,n=len(times),
              start=str(times.min()),end=str(times.max()),train_boundary=str(c1),test_boundary=str(c2),test_end=str(c3),
              high_threshold_m3=threshold,target_mean=float(y[mask].mean())))
        cal=pd.DataFrame({'observed':y[ca],'wet':x.loc[ca,'rain_sum6'].gt(0),'high':y[ca]>threshold})
        test=pd.DataFrame({'observed':y[te],'wet':x.loc[te,'rain_sum6'].gt(0),'high':y[te]>threshold})
        for model in b:cal[model]=b.loc[ca,model];test[model]=b.loc[te,model]
        fitted={};selected[name]={};cv=TimeSeriesSplit(n_splits=3,gap=h)
        for fold,(itr,iva) in enumerate(cv.split(x[tr])):
            times=x.index[tr];rows['cv_folds'].append(dict(scenario=name,fold=fold,n_train=len(itr),n_validation=len(iva),
              last_training_issue=str(times[itr[-1]]),last_training_target=str(times[itr[-1]]+h*HOUR),
              first_validation_issue=str(times[iva[0]])))
        for model,cols in [('ridge_history',hc),('hgb_flow',fc),('hgb_history',hc),('hgb_oracle',list(x))]:
            if model.startswith('ridge'):
                pipe=Pipeline([('impute',SimpleImputer(strategy='median',add_indicator=True)),('scale',StandardScaler()),('model',Ridge())])
                grid={'model__alpha':[1.,100.,10000.]}
            else:
                pipe=hgb_model();grid={'annual__include_annual':[True,False],'model__loss':['squared_error','absolute_error'],
                  'model__max_leaf_nodes':[7,15],'model__l2_regularization':[1.,10.]}
            search=GridSearchCV(pipe,grid,cv=cv,scoring='neg_mean_absolute_error',n_jobs=1,refit=True,error_score='raise')
            search.fit(x.loc[tr,cols],y[tr]);pipe=search.best_estimator_;fitted[model]=(pipe,cols)
            selected[name][model]=search.best_params_
            for i,params in enumerate(search.cv_results_['params']):
                for fold in range(3):rows['cv_scores'].append(dict(scenario=name,model=model,candidate=i,fold=fold,
                  params=json.dumps(params,sort_keys=True),MAE_m3=-search.cv_results_[f'split{fold}_test_score'][i],selected=i==search.best_index_))
            cal[model]=np.maximum(0,pipe.predict(x.loc[ca,cols]));test[model]=np.maximum(0,pipe.predict(x.loc[te,cols]))
            print(name,model,search.best_params_,'MAE',metrics(test.observed,test[model])['MAE_m3'],flush=True)
        for model,cols,loss in [('legacy_squared',hc,'squared_error'),('fixed_flow',fc,'absolute_error'),
                              ('fixed_history',hc,'absolute_error'),('fixed_oracle',list(x),'absolute_error')]:
            pipe=hgb_model().set_params(model__loss=loss,model__max_leaf_nodes=7,model__l2_regularization=10.)
            pipe.fit(x.loc[tr,cols],y[tr]);fitted[model]=(pipe,cols)
            cal[model]=np.maximum(0,pipe.predict(x.loc[ca,cols]));test[model]=np.maximum(0,pipe.predict(x.loc[te,cols]))
        names=[c for c in test if c not in ['observed','wet','high']]
        bounds=[]
        for model in names:
            for group,mask in [('all',np.ones(len(test),bool)),('wet',test.wet),('dry',~test.wet),('high',test.high)]:
                if mask.sum():rows['metrics'].append(dict(scenario=name,horizon=h,model=model,group=group,**metrics(test.observed[mask],test.loc[mask,model])))
            for method in ['pooled','wet_dry','rolling30d']:
                lo,hi=interval_bounds(cal,test,model,h,method);obs=test.observed.to_numpy();covered=(obs>=lo)&(obs<=hi)
                bounds.append(pd.DataFrame({'issue_time_utc':test.index,'model':model,'method':method,'lower':lo,'upper':hi}))
                score=hi-lo+20*np.maximum(lo-obs,0)+20*np.maximum(obs-hi,0)
                for group,mask in [('all',np.ones(len(test),bool)),('wet',test.wet),('dry',~test.wet),('high',test.high)]:
                    if mask.sum():rows['intervals'].append(dict(scenario=name,horizon=h,model=model,method=method,group=group,n=int(mask.sum()),
                      coverage=float(covered[mask].mean()),width_m3=float((hi-lo)[mask].mean()),interval_score_m3=float(score[mask].mean()),
                      upper_exceedance=float((obs[mask]>hi[mask]).mean())))
        comparisons=[('mean24','persistence'),('hgb_history','hgb_flow'),('hgb_oracle','hgb_history'),('hgb_history','mean24'),
          ('hgb_oracle','mean24'),('fixed_history','fixed_flow'),('fixed_oracle','fixed_history'),('fixed_history','legacy_squared')]
        for a,bb in comparisons:
            delta=np.abs(test[a]-test.observed)-np.abs(test[bb]-test.observed)
            for B in [24,48,168]:rows['bootstrap'].append(dict(scenario=name,comparison=a+' minus '+bb,block_hours=B,**bootstrap(delta,test.index,B)))
        cal.to_csv(out/f'calibration_{name}.csv',index_label='issue_time_utc');test.to_csv(out/f'predictions_{name}.csv',index_label='issue_time_utc')
        pd.concat(bounds,ignore_index=True).to_csv(out/f'bounds_{name}.csv',index=False)
        if name=='primary_12h':primary=(x,y,b,v,m,test,cal,fitted,hc,threshold)
        # Episodes are contiguous high-target issue windows, not independent rainstorms.
        highs=test.index[test.high];cuts=np.r_[0,np.flatnonzero(np.diff(highs.as_unit('ns').asi8)!=3600*10**9)+1,len(highs)]
        for model in ['mean24','hgb_history','fixed_history']:
            lo,hi=interval_bounds(cal,test,model,h,'pooled');cov=pd.Series((test.observed>=lo)&(test.observed<=hi),index=test.index)
            for event,(s,e) in enumerate(zip(cuts[:-1],cuts[1:])):
                if s==e:continue
                t=highs[s:e];rows['episodes'].append(dict(scenario=name,model=model,episode=event+1,start=str(t.min()),end=str(t.max()),
                  n=len(t),coverage=float(cov.loc[t].mean()),MAE_m3=float(np.abs(test.loc[t,'observed']-test.loc[t,model]).mean())))
                other=highs.difference(t)
                if len(other):rows['leave_one_episode_out'].append(dict(scenario=name,model=model,omitted_episode=event+1,n=len(other),coverage=float(cov.loc[other].mean())))
            phase=((test.index-d.index.min())/HOUR).astype(int)%h
            for ph in range(h):
                mask=(phase==ph);high=mask&test.high
                rows['nonoverlap'].append(dict(scenario=name,model=model,phase=ph,n=int(mask.sum()),n_high=int(high.sum()),
                  MAE_m3=float(np.abs(test.loc[mask,'observed']-test.loc[mask,model]).mean()),coverage=float(cov[mask].mean()),
                  high_coverage=float(cov[high].mean()) if high.sum() else np.nan))
    # Post-selection sensitivities reuse development-selected parameters; no retuning on final test.
    x,y,b,v,m,test,cal,fitted,hc,threshold=primary
    primary_scenario=scenarios(d)[0];_,h,c1,c2,c3=primary_scenario
    senspred=[]
    for setting in ['annual_removed','delay_1h','delay_2h','no_qc']:
        dd=read_data(qc=False)[0] if setting=='no_qc' else d
        delay={'delay_1h':1,'delay_2h':2}.get(setting,0)
        xx,yy,bb,vv,fc2,hc2=features(dd,h,delay);mm=split_masks(dd.index,vv,h,c1,c2,c3)
        common=test.index.intersection(xx.index[mm['test']]);tr=mm['train'];ca=mm['calibration']
        for model in ['mean24','persistence','hgb_history']:
            if model in bb:p=bb.loc[common,model].to_numpy();cp=bb.loc[ca,model].to_numpy()
            else:
                pipe=hgb_model().set_params(**selected['primary_12h']['hgb_history'])
                if setting=='annual_removed':pipe.set_params(annual__include_annual=False)
                pipe.fit(xx.loc[tr,hc2],yy[tr]);p=np.maximum(0,pipe.predict(xx.loc[common,hc2]));cp=np.maximum(0,pipe.predict(xx.loc[ca,hc2]))
            q=exact_quantile(np.abs(yy[ca].to_numpy()-cp));obs=yy.loc[common].to_numpy();lo=np.maximum(0,p-q);hi=p+q
            # No-QC changed labels can only be compared on equal observed targets.
            if not np.allclose(obs,test.loc[common,'observed']):raise ValueError('Sensitivity common targets changed')
            rows['sensitivity'].append(dict(setting=setting,model=model,n_train=int(tr.sum()),n_calibration=int(ca.sum()),
              coverage=float(((obs>=lo)&(obs<=hi)).mean()),reference_MAE_m3=float(np.abs(test.loc[common,model]-obs).mean()),**metrics(obs,p)))
            senspred.append(pd.DataFrame(dict(setting=setting,model=model,issue_time_utc=common,observed=obs,predicted=p,lower=lo,upper=hi)))
    pd.concat(senspred,ignore_index=True).to_csv(out/'sensitivity_predictions.csv',index=False)
    for key,data in rows.items():pd.DataFrame(data).to_csv(out/(key+'.csv'),index=False)
    (out/'selected_parameters.json').write_text(json.dumps(selected,indent=2,sort_keys=True))
    versions={p:importlib.metadata.version(p) for p in ['numpy','pandas','scipy','scikit-learn','matplotlib','tzdata']}
    versions.update(python=sys.version,platform=platform.platform(),seed=SEED)
    (out/'environment.json').write_text(json.dumps(versions,indent=2))
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'data').glob('*')) if p.is_file()}
    (out/'data_sha256.json').write_text(json.dumps(hashes,indent=2))
    print('COMPLETE',out,flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=ROOT/'reproduced/danish');args=ap.parse_args();run(args.output.resolve())
