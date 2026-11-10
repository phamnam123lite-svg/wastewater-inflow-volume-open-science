"""Fail-closed numerical, chronology and causality checks; no external replication claim."""
from pathlib import Path
import argparse, json, tempfile
import numpy as np
import pandas as pd
import run_analysis as a

def close(x,y):np.testing.assert_allclose(x,y,rtol=1e-10,atol=1e-8,equal_nan=True)

def compare(reference,actual):
    ref=Path(reference);act=Path(actual)
    manifest=json.loads((ref/'reference_manifest.json').read_text())
    names=manifest['required_csv_files']
    if not names or len(names)!=len(set(names)):raise ValueError('Empty or duplicated reference file list')
    diffs=[]
    for name in names:
        if Path(name).name!=name or not name.endswith('.csv'):raise ValueError('Unsafe reference filename')
        x=pd.read_csv(ref/name);y=pd.read_csv(act/name)
        if x.empty or y.empty:raise ValueError('Empty numerical table: '+name)
        if list(x)!=list(y) or x.shape!=y.shape:raise ValueError('Schema/shape mismatch: '+name)
        maximum=0.
        for c in x:
            if pd.api.types.is_numeric_dtype(x[c]) and pd.api.types.is_numeric_dtype(y[c]):
                close(x[c],y[c]);delta=np.abs(x[c].astype(float)-y[c].astype(float))
                if delta.notna().any():maximum=max(maximum,float(delta.max()))
            else:
                if not x[c].fillna('<NA>').astype(str).equals(y[c].fillna('<NA>').astype(str)):raise ValueError('Value mismatch '+name+':'+c)
        diffs.append({'file':name,'rows':len(x),'columns':len(x.columns),'maximum_absolute_numeric_difference':maximum})
    return {'status':'PASS','files_compared':len(diffs),'tables':diffs}

def negative_comparator_tests():
    with tempfile.TemporaryDirectory() as t:
        root=Path(t);r=root/'r';o=root/'o';r.mkdir();o.mkdir()
        (r/'reference_manifest.json').write_text(json.dumps({'required_csv_files':[]}))
        def rejects():
            try:compare(r,o)
            except (ValueError,FileNotFoundError,AssertionError):return True
            raise AssertionError('Comparator accepted invalid input')
        rejects();(r/'reference_manifest.json').write_text(json.dumps({'required_csv_files':['x.csv']}));rejects()
        pd.DataFrame({'x':[1.,2.]}).to_csv(r/'x.csv',index=False);rejects()
        pd.DataFrame({'x':[]}).to_csv(o/'x.csv',index=False);rejects()
        pd.DataFrame({'bad':[1.,2.]}).to_csv(o/'x.csv',index=False);rejects()
        pd.DataFrame({'x':[1.,3.]}).to_csv(o/'x.csv',index=False);rejects()
        pd.DataFrame({'x':[1.,2.]}).to_csv(o/'x.csv',index=False);assert compare(r,o)['files_compared']==1
    return 6

def verify(r):
    r=Path(r);d,audit=a.read_data();report={'status':'PASS','checks':{}}
    checks=report['checks'];metrics=pd.read_csv(r/'metrics.csv');intervals=pd.read_csv(r/'intervals.csv')
    checks['negative_comparator_tests']=negative_comparator_tests()
    for n in [9,10,29,30,100,2089]:
        scores=np.arange(1,n+1);k=int(np.ceil((n+1)*.9));assert a.exact_quantile(scores)==k
    assert np.isinf(a.exact_quantile([1.]))
    for bad in [[],[np.nan],[1,np.inf]]:
        try:a.exact_quantile(bad)
        except ValueError:pass
        else:raise AssertionError('Bad quantile input accepted')
    checks['quantile_rank_and_edge_cases']=10
    metric_count=interval_count=label_count=0
    for name,h,c1,c2,c3 in a.scenarios(d):
        x,y,b,v,fc,hc=a.features(d,h);m=a.split_masks(d.index,v,h,c1,c2,c3)
        cal=pd.read_csv(r/f'calibration_{name}.csv',index_col=0,parse_dates=True)
        test=pd.read_csv(r/f'predictions_{name}.csv',index_col=0,parse_dates=True)
        for frame,part in [(cal,'calibration'),(test,'test')]:
            assert frame.index.equals(d.index[m[part]])
            close(frame.observed,y[m[part]])
            for model in b:close(frame[model],b.loc[m[part],model])
            # Reconstruct every target from the individual hourly values without rolling sums.
            direct=np.array([d.flow.loc[t+a.HOUR:t+h*a.HOUR].to_numpy().sum() for t in frame.index])
            close(frame.observed,direct);label_count+=len(frame)
        assert (x.index[m['train']]+h*a.HOUR<c1).all()
        assert (cal.index+h*a.HOUR<c2).all() and (test.index+h*a.HOUR<c3).all()
        bounds=pd.read_csv(r/f'bounds_{name}.csv',parse_dates=['issue_time_utc'])
        for _,row in metrics[metrics.scenario==name].iterrows():
            mask=np.ones(len(test),bool) if row.group=='all' else (~test.wet if row.group=='dry' else test[row.group])
            got=a.metrics(test.observed[mask],test.loc[mask,row.model])
            for key,val in got.items():close(val,row[key]);metric_count+=1
        for (model,method),bs in bounds.groupby(['model','method'],sort=False):
            assert pd.DatetimeIndex(bs.issue_time_utc).equals(test.index)
            lo,hi=a.interval_bounds(cal,test,model,h,method);close(bs.lower,lo);close(bs.upper,hi)
            obs=test.observed.to_numpy();covered=(obs>=lo)&(obs<=hi)
            score=hi-lo+20*np.maximum(lo-obs,0)+20*np.maximum(obs-hi,0)
            for _,row in intervals[(intervals.scenario==name)&(intervals.model==model)&(intervals.method==method)].iterrows():
                mask=np.ones(len(test),bool) if row.group=='all' else (~test.wet if row.group=='dry' else test[row.group])
                for key,val in dict(n=int(mask.sum()),coverage=covered[mask].mean(),width_m3=(hi-lo)[mask].mean(),
                  interval_score_m3=score[mask].mean(),upper_exceedance=(obs[mask]>hi[mask]).mean()).items():
                    close(val,row[key]);interval_count+=1
        # Circular blocks have exactly uniform marginal inclusion, including short runs.
        for B in [24,48,168]:
            blocks=a.circular_blocks(test.index,B);close(np.bincount(blocks.ravel(),minlength=len(test)),np.full(len(test),B))
        # Perturb future outcomes: the radius at issue t cannot change before labels mature.
        t=test.index[len(test)//2];changed=test.copy();changed.loc[t:,'observed']+=1e6
        lo,hi=a.interval_bounds(cal,test,'mean24',h,'rolling30d')
        lo2,hi2=a.interval_bounds(cal,changed,'mean24',h,'rolling30d')
        close(lo[test.index<=t],lo2[test.index<=t]);close(hi[test.index<=t],hi2[test.index<=t])
        # Historical predictors do not read future measurement values.
        for t in [x.index[500],x.index[len(x)//2],test.index[0]]:
            pert=d.copy();pert.loc[pert.index>t,:]=pert.loc[pert.index>t,:]*7+123
            xp=a.features(pert,h)[0];close(x.loc[t,hc],xp.loc[t,hc])
    checks.update(raw_target_values=label_count,point_metric_values=metric_count,interval_metric_values=interval_count,
      complete_interval_arrays=6*11*3,circular_inclusion_checks=18,historical_feature_future_probes=18,rolling_causality_checks=6)
    folds=pd.read_csv(r/'cv_folds.csv')
    assert (pd.to_datetime(folds.last_training_target)<pd.to_datetime(folds.first_validation_issue)).all()
    checks['purged_cv_folds']=len(folds)
    extra_count=0
    for table,predfile,keys in [('sensitivity','sensitivity_predictions',['setting','model']),
                              ('configuration_sensitivity','configuration_predictions',['loss','annual'])]:
        summary=pd.read_csv(r/(table+'.csv'));pred=pd.read_csv(r/(predfile+'.csv'))
        for _,row in summary.iterrows():
            mask=np.ones(len(pred),bool)
            for key in keys:mask&=pred[key]==row[key]
            z=pred[mask]
            for key,val in a.metrics(z.observed,z.predicted).items():close(val,row[key]);extra_count+=1
            close(((z.observed>=z.lower)&(z.observed<=z.upper)).mean(),row.coverage)
    checks['additional_sensitivity_metric_values']=extra_count
    (r/'verification.json').write_text(json.dumps(report,indent=2));return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--results',type=Path,default=a.ROOT/'results');p.add_argument('--reference',type=Path)
    p.add_argument('--make-reference',action='store_true');args=p.parse_args()
    if args.make_reference:
        names=sorted(f.name for f in args.results.glob('*.csv'))
        if not names:raise ValueError('Cannot register empty reference directory')
        (args.results/'reference_manifest.json').write_text(json.dumps({'required_csv_files':names,'rtol':1e-10,'atol':1e-8},indent=2))
    result=verify(args.results)
    if args.reference:
        result['reproduction']=compare(args.reference,args.results)
        (args.results/'reproduction.json').write_text(json.dumps(result['reproduction'],indent=2))
    print(json.dumps(result,indent=2))
