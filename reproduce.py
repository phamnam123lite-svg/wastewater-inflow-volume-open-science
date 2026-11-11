"""Run the complete analysis without modifying registered numerical references.

python reproduce.py --output reproduced
The output must not exist. Bundled source observations support offline analysis.
"""
from pathlib import Path
import argparse, hashlib, json, os, subprocess, sys, time
ROOT=Path(__file__).resolve().parent

def input_check():
    hashes=json.loads((ROOT/'sources/input_hashes.json').read_text())
    for name,expected in hashes.items():
        p=ROOT/name
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=expected:
            raise ValueError('Missing or altered source observation: '+name)
    return hashes

def main(output):
    input_check()
    output=output.resolve()
    if output.exists():raise ValueError('Choose a new output directory; existing results are never overwritten')
    output.mkdir(parents=True)
    started=time.time();steps=[]
    dk=output/'danish';de=output/'german'
    commands=[['run_analysis.py','--output',str(dk)],
      ['configuration_sensitivity.py','--results',str(dk)],
      ['bootstrap_diagnostic.py','--output',str(dk/'SYNTHETIC_bootstrap_diagnostic.csv')],
      ['verify_results.py','--results',str(dk),'--reference',str(ROOT/'results')],
      ['external_site.py','--output',str(de)],
      ['verify_external.py','--results',str(de),'--reference',str(ROOT/'external_results')],
      ['make_figures.py','--results',str(dk),'--figures',str(output/'figures')],
      ['audit_project.py','--results',str(dk),'--external',str(de),'--report',str(output/'paper_code_audit.json')]]
    for i,cmd in enumerate(commands,1):
        print(f'[{i}/{len(commands)}] '+cmd[0],flush=True);begin=time.time()
        with (output/f'{i:02d}_{Path(cmd[0]).stem}.log').open('w',encoding='utf8') as log:
            result=subprocess.run([sys.executable,'-B',*cmd],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,
                                  env={**os.environ,'PYTHONUTF8':'1','MPLBACKEND':'Agg'})
        steps.append({'command':cmd,'returncode':result.returncode,'seconds':time.time()-begin})
        (output/'execution.json').write_text(json.dumps({'steps':steps,'seconds':time.time()-started},indent=2))
        if result.returncode:raise RuntimeError('Failed: '+cmd[0]+'; inspect '+str(output))
    reports=[json.loads((d/'reproduction.json').read_text()) for d in [dk,de]]
    tables=[row for report in reports for row in report['tables']]
    report={'status':'PASS','csv_files':len(tables),'maximum_absolute_numeric_difference':max(t['maximum_absolute_numeric_difference'] for t in tables),
            'seconds':time.time()-started,'python':sys.version,'source_hashes':input_check(),
            'interpretation':'Computational reproduction by the same workflow; not independent human peer review.'}
    (output/'summary.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'reproduced');main(p.parse_args().output)
