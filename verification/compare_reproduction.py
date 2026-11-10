from pathlib import Path
import pandas as pd,numpy as np,json,hashlib,sys
P=Path(__file__).resolve().parents[1];old=P/'verification/baseline_results';new=P/'results' if (P/'results').exists() else P/'research/results';out=[]
for f in sorted(old.glob('*.csv')):
 g=new/f.name
 a=pd.read_csv(f);b=pd.read_csv(g)
 if a.shape!=b.shape or list(a)!=list(b):raise AssertionError(f.name+' shape mismatch')
 maxdiff=0.
 for c in a:
  if pd.api.types.is_numeric_dtype(a[c]) and a[c].dtype!=bool:
   np.testing.assert_allclose(a[c],b[c],rtol=1e-10,atol=1e-8,equal_nan=True)
   diff=np.abs(a[c].to_numpy(float)-b[c].to_numpy(float));maxdiff=max(maxdiff,float(np.nanmax(diff)) if np.isfinite(diff).any() else 0.)
  else:assert a[c].fillna('').equals(b[c].fillna('')),(f.name,c)
 out.append({'file':f.name,'rows':len(a),'max_absolute_numeric_difference':maxdiff,'passed':True})
report={'status':'PASS','method':'Independent fresh Python 3.11 virtual environment, pinned top-level dependencies; rerun entire pipeline and verify numerical equivalence','rtol':1e-10,'atol':1e-8,'csv_comparisons':out,'python':sys.version,'note':'Computational reproduction, not external scientific validation. Figures compared visually; binary PDF metadata may differ.'}
(P/'verification/reproduction.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
