"""German site: unit, chronology, metric and interval checks, and comparison with the reference results."""
from pathlib import Path
import argparse,json
import numpy as np
import pandas as pd
import external_site as e
import run_analysis as a
from verify_results import close,compare

def main(out,reference=None,make_reference=False):
    raw,d,info=e.load();x,y,b,v,fc,_=a.features(d,12);hc=fc+[c for c in x if c.startswith('rain_')];m=e.masks(d,v)
    test=pd.read_csv(out/'external_predictions.csv',index_col=0,parse_dates=True);cal=pd.read_csv(out/'external_calibration.csv',index_col=0,parse_dates=True)
    for data,split in [(test,'test'),(cal,'calibration')]:
        assert data.index.equals(d.index[m[split]]);close(data.observed,y[m[split]])
        # Directly integrate 48 documented quarter-hour L/s samples, using 900/1000.
        direct=[]
        for t in data.index:
            z=raw.loc[t+pd.Timedelta(minutes=15):t+12*a.HOUR,'wtp_inflow [l/s]']
            assert len(z)==48 and z.notna().all();direct.append(z.sum()*.9)
        close(data.observed,direct)
        for n in b:close(data[n],b.loc[data.index,n])
    assert (d.index[m['train']]+12*a.HOUR<pd.Timestamp('2019-01-01')).all()
    assert (cal.index+12*a.HOUR<pd.Timestamp('2019-04-01')).all()
    folds=pd.read_csv(out/'external_cv_folds.csv');assert (pd.to_datetime(folds.last_training_target)<pd.to_datetime(folds.first_validation_issue)).all()
    count=0;mm=pd.read_csv(out/'external_metrics.csv');ii=pd.read_csv(out/'external_intervals.csv');bounds=pd.read_csv(out/'external_bounds.csv',parse_dates=['provider_issue_time'])
    for _,row in mm.iterrows():
        mask=np.ones(len(test),bool) if row.group=='all' else (~test.wet if row.group=='dry' else test[row.group])
        for k,val in a.metrics(test.observed[mask],test.loc[mask,row.model]).items():close(val,row[k]);count+=1
        close(row.MAE_over_mean_target,row.MAE_m3/test.observed[mask].mean())
    icount=0
    for (model,method),group in bounds.groupby(['model','method'],sort=False):
        lo,hi=a.interval_bounds(cal,test,model,12,method);close(group.lower,lo);close(group.upper,hi)
        assert pd.DatetimeIndex(group.provider_issue_time).equals(test.index)
        obs=test.observed.to_numpy();covered=(obs>=lo)&(obs<=hi);score=hi-lo+20*np.maximum(lo-obs,0)+20*np.maximum(obs-hi,0)
        for _,row in ii[(ii.model==model)&(ii.method==method)].iterrows():
            mask=np.ones(len(test),bool) if row.group=='all' else (~test.wet if row.group=='dry' else test[row.group])
            for k,val in dict(n=int(mask.sum()),coverage=float(covered[mask].mean()),width_m3=float((hi-lo)[mask].mean()),interval_score_m3=float(score[mask].mean()),upper_exceedance=float((obs[mask]>hi[mask]).mean())).items():close(val,row[k]);icount+=1
    for t in [test.index[0],test.index[len(test)//2],test.index[-1]]:
        z=d.copy();z.loc[z.index>t,:]=z.loc[z.index>t,:]*11+100
        close(a.features(z,12)[0].loc[t,hc],x.loc[t,hc])
    t=test.index[len(test)//2];z=test.copy();z.loc[t:,'observed']+=1e6
    lo,hi=a.interval_bounds(cal,test,'hgb_rain',12,'rolling30d');lo2,hi2=a.interval_bounds(cal,z,'hgb_rain',12,'rolling30d');close(lo[test.index<=t],lo2[test.index<=t]);close(hi[test.index<=t],hi2[test.index<=t])
    report={'status':'PASS','raw_quarter_hour_integrations':len(test)+len(cal),'point_metric_values':count,'interval_metric_values':icount,
      'feature_causality_probes':3,'rolling_causality_checks':1,'purged_cv_folds':3,'clock':'Archive clock; not asserted UTC'}
    if make_reference:
        names=sorted(p.name for p in out.glob('*.csv'))
        if not names:raise ValueError('Empty reference')
        (out/'reference_manifest.json').write_text(json.dumps({'required_csv_files':names,'rtol':1e-10,'atol':1e-8},indent=2))
    if reference:
        report['reproduction']=compare(reference,out);(out/'reproduction.json').write_text(json.dumps(report['reproduction'],indent=2))
    (out/'external_verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--results',type=Path,default=e.ROOT/'results'/'germany');p.add_argument('--reference',type=Path);p.add_argument('--make-reference',action='store_true');args=p.parse_args();main(args.results,args.reference,args.make_reference)
