"""Rerun the complete two-site analysis and compare it with the reference results.

    python reproduce.py --output reproduced

The output directory must not exist yet. The reference results in results/ are never modified.
Steps: Danish analysis, configuration and synthetic diagnostics, forecast-conditioned coverage, Danish
checks, German analysis and checks, figures, the manuscript check (tables, key numbers and pixel-identical
figures) and an independent re-computation from the raw data that shares no code with src/run_analysis.py.
"""
from pathlib import Path
import argparse, hashlib, importlib.metadata, json, os, platform, subprocess, sys, time
ROOT=Path(__file__).resolve().parent
PACKAGES=['numpy','pandas','scipy','scikit-learn','matplotlib','pillow']

def input_check():
    """Verify the bundled source observations against data/checksums.sha256."""
    hashes={}
    for line in (ROOT/'data'/'checksums.sha256').read_text(encoding='utf8').splitlines():
        if not line.strip():continue
        expected,name=line.split(None,1);name=name.strip().lstrip('*');p=ROOT/name
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=expected:
            raise ValueError('Missing or altered source observation: '+name)
        hashes[name]=expected
    return hashes

def main(output):
    input_check()
    output=output.resolve()
    if output.exists():raise ValueError('Choose a new output directory; existing results are never overwritten')
    output.mkdir(parents=True)
    def show(p):
        for base,label in [(output,'<output>/'),(ROOT,'')]:
            try:return label+Path(p).relative_to(base).as_posix()
            except ValueError:pass
        return str(p)
    started=time.time();steps=[]
    dk=output/'denmark';de=output/'germany';src=ROOT/'src'
    commands=[[src/'run_analysis.py','--output',dk],
      [src/'configuration_sensitivity.py','--results',dk],
      [src/'bootstrap_diagnostic.py','--output',dk/'SYNTHETIC_bootstrap_diagnostic.csv'],
      [src/'forecast_high_coverage.py','--results',dk,'--site','denmark'],
      [src/'verify_results.py','--results',dk,'--reference',ROOT/'results'/'denmark'],
      [src/'external_site.py','--output',de],
      [src/'forecast_high_coverage.py','--results',de,'--site','germany'],
      [src/'verify_external.py','--results',de,'--reference',ROOT/'results'/'germany'],
      [src/'make_figures.py','--results',dk,'--figures',output/'figures'],
      [src/'check_manuscript.py','--results',dk,'--external',de,'--report',output/'manuscript_check.json'],
      [src/'independent_check.py','--denmark',dk,'--germany',de,'--report',output/'independent_check.json']]
    for i,cmd in enumerate(commands,1):
        name=Path(cmd[0]).stem+('_'+cmd[-1] if Path(cmd[0]).stem=='forecast_high_coverage' else '')
        print(f'[{i}/{len(commands)}] '+name,flush=True);begin=time.time()
        with (output/f'{i:02d}_{name}.log').open('w',encoding='utf8') as log:
            result=subprocess.run([sys.executable,'-B',*map(str,cmd)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,
                                  env={**os.environ,'PYTHONUTF8':'1','MPLBACKEND':'Agg'})
        steps.append({'command':[show(c) if isinstance(c,Path) else c for c in cmd],'returncode':result.returncode,'seconds':round(time.time()-begin,1)})
        (output/'execution.json').write_text(json.dumps({'steps':steps,'seconds':round(time.time()-started,1)},indent=2))
        if result.returncode:raise RuntimeError('Failed: '+name+'; see the log in '+str(output))
    reports=[json.loads((d/'reproduction.json').read_text()) for d in [dk,de]]
    tables=[row for report in reports for row in report['tables']]
    figures=json.loads((output/'manuscript_check.json').read_text())['pixel_identical_rerun_figures']
    independent=json.loads((output/'independent_check.json').read_text())['summary']
    report={'status':'PASS','csv_files_compared':len(tables),'denmark_csv_files':len(reports[0]['tables']),'germany_csv_files':len(reports[1]['tables']),
            'maximum_absolute_numeric_difference':max(t['maximum_absolute_numeric_difference'] for t in tables),
            'tolerance':{'rtol':1e-10,'atol':1e-8},'pixel_identical_figures':figures,
            'independent_checks_passed':f"{independent['passed']}/{independent['checks']}",'seconds':round(time.time()-started,1),
            'python':platform.python_version(),'platform':platform.platform(),
            'packages':{p:importlib.metadata.version(p) for p in PACKAGES},'source_checksums':input_check()}
    (output/'summary.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'reproduced');main(p.parse_args().output)
