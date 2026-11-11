"""Check every manuscript table cell, key reported numbers, citations and figures against the reference results.
Run from the repository root: python src/check_manuscript.py
"""
from pathlib import Path
import argparse, ast, json, re
import numpy as np
import pandas as pd
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]

def audit(r,e):
    text=(ROOT/'paper/manuscript.md').read_text(encoding='utf8')
    tables=[];current=[]
    for line in text.splitlines()+['']:
        if line.startswith('|'):current.append([c.strip() for c in line.strip('|').split('|')])
        elif current:tables.append(current[2:]);current=[]
    assert len(tables)==4
    m=pd.read_csv(r/'metrics.csv');iv=pd.read_csv(r/'intervals.csv');em=pd.read_csv(e/'external_metrics.csv')
    p=m[(m.scenario=='primary_12h')&(m.group=='all')].set_index('model')
    primary=['persistence','mean24','seasonal24','ridge_history','legacy_squared','fixed_history','hgb_flow','hgb_history','hgb_oracle']
    label={'persistence':'Persistence','mean24':'24-h mean','seasonal24':'Previous day','ridge_history':'Ridge history','legacy_squared':'Legacy HGB',
           'fixed_history':'Fixed absolute-loss HGB','hgb_flow':'HGB flow','hgb_history':'HGB history','hgb_oracle':'HGB oracle'}
    inputs={'persistence':'F','mean24':'F','seasonal24':'F','ridge_history':'F+C+W','legacy_squared':'F+C+W','fixed_history':'F+C+W',
            'hgb_flow':'F+C','hgb_history':'F+C+W','hgb_oracle':'F+C+W+R'}
    # Each expected row is the complete rendered row, including labels, so row order and model identity are checked too.
    expected=[[[label[n],inputs[n],f'{p.loc[n,"MAE_m3"]:,.1f}',f'{p.loc[n,"RMSE_m3"]:,.1f}',f'{p.loc[n,"R2"]:.3f}',f'{p.loc[n,"bias_m3"]:,.1f}'] for n in primary]]
    rows=[]
    for date in ['2024-08-15','2024-10-15','2024-12-15']:
        z=m[(m.scenario=='origin_'+date)&(m.group=='all')].set_index('model')
        assert len({int(z.loc[n,'n']) for n in ['mean24','hgb_flow','hgb_history','hgb_oracle']})==1
        rows.append([date,f'{int(z.loc["mean24","n"]):,}']+[f'{z.loc[n,"MAE_m3"]:,.1f}' for n in ['mean24','hgb_flow','hgb_history','hgb_oracle']])
    expected.append(rows);rows=[]
    for n in ['mean24','hgb_history','hgb_oracle']:
        for i,(method,mlabel) in enumerate([('pooled','Pooled'),('wet_dry','Wet/dry'),('rolling30d','Rolling 30 d')]):
            z=iv[(iv.scenario=='primary_12h')&(iv.model==n)&(iv.method==method)].set_index('group')
            rows.append([label[n] if i==0 else '',mlabel]+[f'{100*z.loc[g,"coverage"]:.1f}' for g in ['all','wet','high']]+
                        [f'{z.loc["all","width_m3"]:,.0f}',f'{z.loc["all","interval_score_m3"]:,.0f}'])
    expected.append(rows);z=em[em.group=='all'].set_index('model')
    german=[('persistence','Persistence','F'),('mean24','24-h mean','F'),('seasonal24','Previous day','F'),('hgb_flow','HGB flow','F+C'),
            ('hgb_rain','HGB flow + rain','F+C+P'),('hgb_oracle','HGB oracle','F+C+P+R')]
    expected.append([[lab,inp,f'{z.loc[n,"MAE_m3"]:,.1f}',f'{z.loc[n,"RMSE_m3"]:,.1f}',f'{z.loc[n,"R2"]:.3f}',f'{z.loc[n,"bias_m3"]:,.1f}',
                      f'{100*z.loc[n,"MAE_over_mean_target"]:.1f}'] for n,lab,inp in german])
    cells=0
    for no,(actual,want) in enumerate(zip(tables,expected),1):
        assert len(actual)==len(want),f'Table {no} row count'
        for row,exp in zip(actual,want):
            assert row==exp,f'Table {no}: {row} != {exp}'
            cells+=sum(1 for c in exp if re.fullmatch(r'-?[\d,]+(?:\.\d+)?|\d{4}-\d{2}-\d{2}',c))
    claims=[]
    def claim(value,formatted,source):
        assert formatted in text,'Manuscript claim missing: '+formatted
        claims.append({'rendered':formatted,'value':float(value),'source':source})
    for model in primary:
        val=p.loc[model,'MAE_m3'];claim(val,f'{val:,.1f}','results/denmark/metrics.csv:primary_12h/all/'+model)
    for model in ['hgb_rain','hgb_flow','mean24','hgb_oracle']:
        val=z.loc[model,'MAE_m3'];claim(val,f'{val:,.1f}','results/germany/external_metrics.csv:all/'+model)
    splits=pd.read_csv(r/'splits.csv');s=splits[splits.scenario=='primary_12h'].set_index('split')
    for part in ['train','calibration','test']:
        val=s.loc[part,'n'];claim(val,f'{int(val):,}','results/denmark/splits.csv:primary_12h/'+part)
    es=pd.read_csv(e/'external_splits.csv').set_index('split')
    for part in ['train','calibration','test']:
        val=es.loc[part,'n'];claim(val,f'{int(val):,}','results/germany/external_splits.csv:'+part)
    # forecast-conditioned high-volume coverage (Sections 3.4, 3.6, 4.3 and the Abstract)
    fh=pd.read_csv(r/'forecast_high_coverage.csv').set_index(['model','method'])
    fe=pd.read_csv(e/'external_forecast_high_coverage.csv').set_index(['model','method'])
    for src,tab,model in [('results/denmark/forecast_high_coverage.csv',fh,'hgb_history'),('results/denmark/forecast_high_coverage.csv',fh,'mean24'),
                          ('results/germany/external_forecast_high_coverage.csv',fe,'hgb_rain')]:
        n=tab.loc[(model,'pooled'),'n_forecast_high'];claim(n,f'{int(n)} ',src+':'+model+'/n_forecast_high')
        for method in ['pooled','wet_dry','rolling30d']:
            val=100*tab.loc[(model,method),'coverage_forecast_high'];claim(val,f'{val:.1f}%',src+':'+model+'/'+method)
    # matched-configuration decomposition of the additional origins (Section 3.3)
    for origin in ['origin_2024-08-15','origin_2024-10-15','origin_2024-12-15']:
        z=m[(m.scenario==origin)&(m.group=='all')].set_index('model')
        for model in ['fixed_flow','fixed_history']:
            val=z.loc[model,'MAE_m3'];claim(val,f'{val:,.1f}',f'results/denmark/metrics.csv:{origin}/all/{model}')
    # near-constant values left by the endpoint screening rule (Sections 2.2 and 3.5)
    h=pd.read_csv(r/'cleaned_hourly.csv',index_col=0,parse_dates=True).flow_raw
    flat=(h.rolling(6,min_periods=6).max()-h.rolling(6,min_periods=6).min()).lt(5);covered=pd.Series(False,index=h.index)
    for t in h.index[flat]:covered.loc[t-pd.Timedelta(hours=5):t]=True
    val=int((covered&~flat).sum());claim(val,f'leave {val} near-constant','results/denmark/cleaned_hourly.csv:flat-window stretches')
    # software-version sensitivity (Section 3.5); compares the registered results with results/version_sensitivity
    vs=ROOT/'results'/'version_sensitivity'
    if vs.is_dir():
        sr=json.loads((ROOT/'results'/'denmark'/'selected_parameters.json').read_text());sa=json.loads((vs/'selected_parameters.json').read_text())
        changed=sum(sr[s][k]!=sa[s][k] for s in sr for k in sr[s]);claim(changed,f'changed {changed} of the {sum(len(v) for v in sr.values())} Danish','results/version_sensitivity/selected_parameters.json')
        a=pd.read_csv(vs/'metrics.csv');a=a[a.group=='all'].set_index(['scenario','model']).MAE_m3
        ea=pd.read_csv(vs/'external_metrics.csv');ea=ea[ea.group=='all'].set_index('model').MAE_m3
        for val,src in [(a[('primary_12h','hgb_history')],'primary_12h/hgb_history'),(ea['hgb_rain'],'external/hgb_rain'),(a[('primary_24h','hgb_flow')],'primary_24h/hgb_flow')]:
            claim(val,f'{val:,.1f}','results/version_sensitivity:'+src)
        val=a[('primary_12h','fixed_history')]-a[('primary_12h','fixed_flow')];claim(val,f'{val:,.1f}'.replace('-','-'),'results/version_sensitivity:fixed_history-fixed_flow')
    citations=set()
    for x in re.findall(r'\[(\d+(?:,\d+)*)\]',text):citations.update(map(int,x.split(',')))
    assert citations==set(range(1,11))
    assert len(re.findall(r'^\d+\. ',text,re.M))==10
    images=re.findall(r'!\[[^]]*\]\(([^)]+)\)',text);assert len(images)==5
    for name in images:assert (ROOT/'paper'/name).is_file(),name
    figures_checked=0
    if (r.parent/'figures').is_dir() and r.resolve()!=(ROOT/'results'/'denmark').resolve():
        for name in images:
            ref=Image.open(ROOT/'paper'/name);actual=Image.open(r.parent/'figures'/Path(name).name)
            assert ref.size==actual.size and np.array_equal(np.asarray(ref),np.asarray(actual)),name
            figures_checked+=1
    for f in [*ROOT.glob('*.py'),*(ROOT/'src').glob('*.py'),*(ROOT/'tests').glob('*.py')]:ast.parse(f.read_text(encoding='utf8'))
    a=(ROOT/'src'/'run_analysis.py').read_text(encoding='utf8')
    for token in ["gap=h","early_stopping=False","min_samples_leaf=30","max_iter=150","learning_rate=.05","(mature<=t)","min_count=h","scoring='neg_mean_absolute_error'"]:assert token in a,token
    return {'status':'PASS','table_count':4,'numeric_table_cells':cells,'table_rows_checked_with_labels':sum(len(x) for x in expected),'traceable_claims':claims,'referenced_figures':5,'pixel_identical_rerun_figures':figures_checked,'references':10,
            'scope':'All table cells, including row labels and input codes, and selected narrative numbers are checked automatically; figures are compared pixel by pixel when a rerun directory is given.'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--results',type=Path,default=ROOT/'results'/'denmark');p.add_argument('--external',type=Path,default=ROOT/'results'/'germany');p.add_argument('--report',type=Path,default=ROOT/'verification'/'manuscript_check.json');args=p.parse_args()
    report=audit(args.results,args.external);args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
