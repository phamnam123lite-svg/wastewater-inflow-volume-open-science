"""Reproducible secondary analysis. Run from any directory: python run_analysis.py."""
import os
os.environ.setdefault('OMP_NUM_THREADS','2')
os.environ.setdefault('OPENBLAS_NUM_THREADS','2')
from pathlib import Path
import json, hashlib, platform, sys, warnings, importlib.metadata
import numpy as np
import pandas as pd
import scipy
from scipy.stats import spearmanr
import sklearn
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent
for folder in ['results','figures']: (ROOT/folder).mkdir(exist_ok=True)
R=ROOT/'results'; F=ROOT/'figures'; SEED=20261109
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none','pdf.fonttype':42})

def savefig(fig,name):
    fig.tight_layout()
    for ext in ['png','svg','pdf']: fig.savefig(F/f'{name}.{ext}',dpi=300,bbox_inches='tight')
    plt.close(fig)

def load_data():
    raw=pd.read_csv(ROOT/'data/wwtp.csv',sep=';')
    ix=pd.DatetimeIndex(pd.to_datetime(raw.iloc[:,0])).tz_localize('Europe/Copenhagen',ambiguous='NaT',nonexistent='NaT').tz_convert('UTC').tz_localize(None)
    flow=pd.Series(raw.flow.to_numpy(),index=ix,name='flow_raw')
    ambiguous=int(flow.index.isna().sum());flow=flow[~flow.index.isna()]
    dup=int(flow.index.duplicated().sum());flow=flow.groupby(level=0).mean()
    met=pd.read_csv(ROOT/'data/dmi.csv',index_col=0,parse_dates=True)
    d=met.join(flow,how='outer').sort_index().asfreq('h')
    low=d.flow_raw.lt(2)
    flat=(d.flow_raw.rolling(6,min_periods=6).max()-d.flow_raw.rolling(6,min_periods=6).min()).lt(5)
    d['flow']=d.flow_raw.mask(low|flat)
    # Valid-range flags do not remove extremes without sensor evidence.
    d['mean_relative_hum']=d.mean_relative_hum.mask((d.mean_relative_hum<0)|(d.mean_relative_hum>100))
    audit={'raw_flow_rows':len(raw),'ambiguous_timestamps_removed':ambiguous,'duplicate_utc_timestamps':dup,'hourly_grid_rows':len(d),'start':str(d.index.min()),'end':str(d.index.max()),'flow_missing_raw':int(d.flow_raw.isna().sum()),'flow_below_2':int(low.sum()),'trailing_flat_flag':int(flat.sum()),'flow_missing_clean':int(d.flow.isna().sum()),'missing_by_column':d.isna().sum().to_dict(),'negative_rain':int(d.acc_precip.lt(0).sum())}
    (R/'data_audit.json').write_text(json.dumps(audit,indent=2))
    d.describe().T.to_csv(R/'descriptive_statistics.csv')
    d.resample('MS').agg({'flow':['count','mean','median','max'],'acc_precip':['sum','count']}).to_csv(R/'monthly_data_audit.csv')
    d.to_csv(R/'cleaned_hourly.csv',index_label='time_utc')
    return d,audit

def features(d,h):
    x=pd.DataFrame(index=d.index)
    for lag in [0,1,2,3,6,12,24,48,168]: x[f'flow_lag{lag}']=d.flow.shift(lag)
    for w in [6,12,24]:
        x[f'flow_mean{w}']=d.flow.rolling(w).mean()
        x[f'flow_std{w}']=d.flow.rolling(w).std()
    for name,v,period in [('hour',d.index.hour,24),('weekday',d.index.dayofweek,7),('annual',d.index.dayofyear,365.25)]:
        x[f'{name}_sin']=np.sin(2*np.pi*v/period);x[f'{name}_cos']=np.cos(2*np.pi*v/period)
    flowcols=list(x.columns)
    for w in [1,6,12,24,72]: x[f'rain_sum{w}']=d.acc_precip.rolling(w).sum()
    for c in ['mean_pressure','mean_radiation','mean_relative_hum','mean_temp']:
        x[c]=d[c];x[c+'_mean6']=d[c].rolling(6).mean()
    histcols=list(x.columns)
    # Diagnostic comparator: deliberately unavailable future observations.
    future_rain=pd.concat([d.acc_precip.shift(-k) for k in range(1,h+1)],axis=1)
    x['ORACLE_rain_sum']=future_rain.sum(axis=1,min_count=h)
    x['ORACLE_rain_max']=future_rain.max(axis=1)
    future_flow=pd.concat([d.flow.shift(-k) for k in range(1,h+1)],axis=1)
    y=future_flow.sum(axis=1,min_count=h)
    b=pd.DataFrame({'persistence':h*d.flow,'mean24':h*d.flow.rolling(24).mean(),
                    'seasonal24':pd.concat([d.flow.shift(24-k) for k in range(1,h+1)],axis=1).sum(axis=1,min_count=h)},index=d.index)
    valid=y.notna() & b.notna().all(axis=1) & x['ORACLE_rain_sum'].notna() & x.rain_sum6.notna()
    return x,y,b,valid,flowcols,histcols

def metrics(y,p):
    return {'n':len(y),'MAE_m3':mean_absolute_error(y,p),'RMSE_m3':np.sqrt(mean_squared_error(y,p)),'R2':r2_score(y,p),'bias_m3':float(np.mean(p-y)),'mean_underprediction_m3':float(np.mean(np.maximum(y-p,0)))}

def quantile(scores,p=.9):
    return float(np.quantile(scores,min(1,np.ceil((len(scores)+1)*p)/len(scores)),method='higher'))

def block_ci(values,index,block=48,nboot=2000):
    # Blocks never cross gaps in the accepted issue-time sequence.
    a=np.asarray(values); idx=pd.DatetimeIndex(index)
    # pandas 3 may store datetime in microseconds; normalize before comparing.
    cuts=np.r_[0,np.flatnonzero(np.diff(idx.as_unit('ns').asi8)!=3600*10**9)+1,len(a)]
    blocks=[np.arange(s,min(s+block,e)) for b,e in zip(cuts[:-1],cuts[1:]) for s in range(b,e)]
    rng=np.random.default_rng(SEED+block);out=[]
    for _ in range(nboot):
        parts=[];n=0
        while n<len(a):
            z=blocks[rng.integers(len(blocks))];parts.append(z);n+=len(z)
        out.append(np.mean(a[np.concatenate(parts)[:len(a)]]))
    return float(np.mean(a)),*map(float,np.quantile(out,[.025,.975]))

def main():
    d,audit=load_data();n=len(d);cut1=d.index[int(.6*n)];cut2=d.index[int(.8*n)]
    allmetrics=[];allintervals=[];allci=[];splits=[];cvrows=[];predframes=[];models={};sets={}
    for h in [12,6,24]:
        print('HORIZON',h,flush=True)
        x,y,b,valid,flowcols,histcols=features(d,h)
        masks={'train':valid & (d.index+pd.Timedelta(hours=h)<cut1),'calibration':valid & (d.index>=cut1)&(d.index+pd.Timedelta(hours=h)<cut2),'test':valid&(d.index>=cut2)}
        for s,m in masks.items():
            times=d.index[m];splits.append({'horizon':h,'split':s,'n':len(times),'start':str(times.min()),'end':str(times.max()),'target_mean':float(y[m].mean()),'wet_fraction':float(x.loc[m,'rain_sum6'].gt(0).mean())})
        tr,ca,te=[masks[s] for s in ['train','calibration','test']]
        threshold=float(y[tr].quantile(.9))
        pred=pd.DataFrame({'observed':y[te],'wet':x.loc[te,'rain_sum6'].gt(0),'high':y[te]>threshold})
        calpred={name:b.loc[ca,name].to_numpy() for name in b}
        for name in b: pred[name]=b.loc[te,name]
        configurations={'ridge_history':histcols,'hgb_flow':flowcols,'hgb_history':histcols,'hgb_oracle':list(x.columns)}
        for name,cols in configurations.items():
            if name.startswith('ridge'):
                model=make_pipeline(SimpleImputer(strategy='median',add_indicator=True),StandardScaler(),Ridge())
                grid={'ridge__alpha':[1.,100.,10000.]}
            else:
                model=make_pipeline(SimpleImputer(strategy='median',add_indicator=True),HistGradientBoostingRegressor(max_iter=150,learning_rate=.05,min_samples_leaf=30,early_stopping=False,random_state=SEED))
                grid={'histgradientboostingregressor__max_leaf_nodes':[7,15],'histgradientboostingregressor__l2_regularization':[1.,10.]}
            search=GridSearchCV(model,grid,cv=TimeSeriesSplit(n_splits=3,gap=h),scoring='neg_mean_absolute_error',n_jobs=1)
            search.fit(x.loc[tr,cols],y[tr]);model=search.best_estimator_
            print(h,name,search.best_params_,flush=True)
            for i,params in enumerate(search.cv_results_['params']):
                cvrows.append({'horizon':h,'model':name,'params':json.dumps(params),'CV_MAE':-search.cv_results_['mean_test_score'][i],'best':params==search.best_params_})
            calpred[name]=np.maximum(0,model.predict(x.loc[ca,cols]))
            pred[name]=np.maximum(0,model.predict(x.loc[te,cols]))
            if h==12: models[name]=(model,cols)
        names=list(calpred)
        for name in names:
            for group,m in [('all',np.ones(len(pred),bool)),('wet',pred.wet.to_numpy()),('dry',~pred.wet.to_numpy()),('high',pred.high.to_numpy())]:
                if m.sum()>1: allmetrics.append({'horizon':h,'model':name,'group':group,**metrics(pred.observed[m],pred[name][m])})
            scores=np.abs(y[ca].to_numpy()-calpred[name]);q=quantile(scores)
            wetcal=x.loc[ca,'rain_sum6'].gt(0).to_numpy()
            for method in ['pooled','wet_dry']:
                widths=np.full(len(pred),q)
                if method=='wet_dry':
                    for state in [False,True]:
                        if (wetcal==state).sum()>=30: widths[pred.wet.to_numpy()==state]=quantile(scores[wetcal==state])
                lo=np.maximum(0,pred[name].to_numpy()-widths);hi=pred[name].to_numpy()+widths
                if method=='pooled': pred[name+'_lower']=lo;pred[name+'_upper']=hi
                observed=pred.observed.to_numpy();covered=(observed>=lo)&(observed<=hi)
                score=hi-lo+20*np.maximum(lo-observed,0)+20*np.maximum(observed-hi,0)
                for group,m in [('all',np.ones(len(pred),bool)),('wet',pred.wet.to_numpy()),('dry',~pred.wet.to_numpy()),('high',pred.high.to_numpy())]:
                    if m.sum(): allintervals.append({'horizon':h,'model':name,'method':method,'group':group,'n':int(m.sum()),'coverage':float(covered[m].mean()),'width_m3':float((hi-lo)[m].mean()),'interval_score_m3':float(score[m].mean()),'upper_exceedance':float((observed[m]>hi[m]).mean())})
        for a,bb in [('hgb_history','hgb_flow'),('hgb_oracle','hgb_history'),('hgb_history','persistence'),('ridge_history','persistence')]:
            delta=np.abs(pred[a]-pred.observed)-np.abs(pred[bb]-pred.observed)
            for bl in [24,48,168]:
                est,low,high=block_ci(delta,pred.index,bl)
                allci.append({'horizon':h,'comparison':a+' minus '+bb,'block_hours':bl,'MAE_difference':est,'CI_low':low,'CI_high':high})
        pred.to_csv(R/f'predictions_{h}h.csv',index_label='issue_time_utc');predframes.append((h,pred))
        if h==12: sets={'x':x,'y':y,'tr':tr,'ca':ca,'te':te,'threshold':threshold,'pred':pred,'histcols':histcols}
    for name,rows in [('metrics',allmetrics),('intervals',allintervals),('bootstrap_comparisons',allci),('splits',splits),('hyperparameter_search',cvrows)]:pd.DataFrame(rows).to_csv(R/f'{name}.csv',index=False)
    # Descriptive tests use the training period only; test residual diagnostics are post-evaluation.
    x=sets['x'];y=sets['y'];tr=sets['tr'];te=sets['te'];p=sets['pred']
    corr=x.loc[tr,sets['histcols']].corrwith(y[tr],method='spearman').sort_values()
    corr.to_csv(R/'training_spearman.csv',header=['rho'])
    resid=p.observed-p.hgb_history
    resid_grid=resid.reindex(d.index)
    acf={str(k):float(resid_grid.autocorr(k)) for k in [1,6,12,24,48,168]}
    rho,pvalue=spearmanr(np.abs(resid),p.hgb_history)
    diag={'primary_high_volume_threshold_m3':sets['threshold'],'test_residual_acf':acf,'abs_residual_vs_prediction_spearman':float(rho),'spearman_naive_p_not_valid_under_dependence':float(pvalue),'split_cutoffs_utc':[str(cut1),str(cut2)]}
    (R/'diagnostics.json').write_text(json.dumps(diag,indent=2))
    # Group circular shifts preserve each feature group's internal temporal pattern, approximate sensitivity only.
    model,cols=models['hgb_history'];xt=x.loc[te,cols];rng=np.random.default_rng(SEED);base=mean_absolute_error(y[te],p.hgb_history)
    groups={'flow':[c for c in cols if c.startswith('flow_')],'rain':[c for c in cols if c.startswith('rain_')],'calendar':[c for c in cols if c.endswith(('_sin','_cos'))],'other_weather':[c for c in cols if c.startswith('mean_')]}
    imp=[]
    for group,cc in groups.items():
        for repeat in range(20):
            z=xt.copy();offset=int(rng.integers(48,len(z)-48));z[cc]=np.roll(z[cc].to_numpy(),offset,axis=0)
            imp.append({'group':group,'repeat':repeat,'MAE_increase':mean_absolute_error(y[te],np.maximum(0,model.predict(z)))-base})
    pd.DataFrame(imp).to_csv(R/'group_shift_sensitivity.csv',index=False)
    # Visuals.
    fig,axes=plt.subplots(2,1,figsize=(9,5),sharex=True)
    axes[0].plot(d.index,d.flow,lw=.45,color='#176b87');axes[0].set_ylabel('Inflow (m³/h)')
    axes[1].plot(d.index,d.acc_precip,lw=.5,color='#b96528');axes[1].set_ylabel('Rainfall (mm/h)')
    for ax in axes:
        ax.axvline(cut1,color='black',ls='--',lw=.8);ax.axvline(cut2,color='black',ls='--',lw=.8)
    axes[0].set_title('Raw-derived observations and chronological split boundaries');savefig(fig,'01_data_timeline')
    mm=pd.DataFrame(allmetrics);z=mm[(mm.horizon==12)&mm.group.isin(['all','high'])]
    names=['persistence','seasonal24','mean24','ridge_history','hgb_flow','hgb_history','hgb_oracle']
    fig,ax=plt.subplots(figsize=(8,4));pos=np.arange(len(names))
    for off,group,color in [(-.18,'all','#176b87'),(.18,'high','#c17430')]:
        vals=z[z.group==group].set_index('model').loc[names,'MAE_m3'];ax.bar(pos+off,vals,width=.35,label=group,color=color)
    ax.set_xticks(pos,names,rotation=25,ha='right');ax.set_ylabel('12-hour volume MAE (m³)');ax.legend();savefig(fig,'02_model_errors')
    zz=pd.DataFrame(allintervals);zz=zz[(zz.horizon==12)&(zz.method=='pooled')]
    fig,ax=plt.subplots(figsize=(7,4))
    for group,color in [('all','#176b87'),('wet','#66994d'),('high','#c17430')]:ax.plot(names,zz[zz.group==group].set_index('model').loc[names,'coverage'],marker='o',label=group,color=color)
    ax.axhline(.9,color='gray',ls='--',label='Nominal 90%');ax.set_ylim(0,1.03);ax.set_ylabel('Empirical interval coverage');ax.tick_params(axis='x',rotation=30);ax.legend(ncol=2);savefig(fig,'03_interval_coverage')
    # Fixed first 14 days of test, not cherry-picked by errors.
    window=p.loc[p.index.min():p.index.min()+pd.Timedelta(days=14)]
    fig,ax=plt.subplots(figsize=(9,4));ax.fill_between(window.index,window.hgb_history_lower,window.hgb_history_upper,color='#176b87',alpha=.2,label='90% calibrated interval');ax.plot(window.index,window.observed,color='black',lw=.9,label='Observed');ax.plot(window.index,window.hgb_history,lw=.8,color='#176b87',label='Historical model');ax.set_ylabel('Next 12-hour volume (m³)');ax.legend();savefig(fig,'04_test_example')
    zz=pd.DataFrame(imp).groupby('group').MAE_increase.agg(['mean','std']).sort_values('mean')
    fig,ax=plt.subplots(figsize=(6,3.5));ax.barh(zz.index,zz['mean'],xerr=zz['std'],color='#176b87');ax.set_xlabel('MAE increase after group shift (m³)');savefig(fig,'05_feature_sensitivity')
    versions={'python':sys.version,'platform':platform.platform(),'numpy':np.__version__,'pandas':pd.__version__,'scipy':scipy.__version__,'scikit-learn':sklearn.__version__,'matplotlib':matplotlib.__version__,'tzdata':importlib.metadata.version('tzdata'),'seed':SEED}
    (R/'environment.json').write_text(json.dumps(versions,indent=2))
    import requests
    (ROOT/'requirements.txt').write_text('\n'.join(f'{k}=={v}' for k,v in versions.items() if k in ['numpy','pandas','scipy','scikit-learn','matplotlib','tzdata'])+'\nrequests=='+requests.__version__+'\n')
    hashes={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in (ROOT/'data').iterdir() if f.is_file()}
    (R/'data_sha256.json').write_text(json.dumps(hashes,indent=2))
    print('COMPLETE',flush=True)

if __name__=='__main__':main()
