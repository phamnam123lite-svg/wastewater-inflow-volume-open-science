"""Matched 2x2 loss/annual diagnostic at primary development-selected tree size/L2.
Added after seeing the revision selection; exploratory, no new independent validation.
"""
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
import run_analysis as a

def main(r):
    d,_=a.read_data();x,y,b,v,fc,hc=a.features(d,12);_,h,c1,c2,c3=a.scenarios(d)[0]
    masks=a.split_masks(d.index,v,h,c1,c2,c3);tr,ca,te=[masks[s] for s in ['train','calibration','test']]
    selected=json.loads((r/'selected_parameters.json').read_text())['primary_12h']['hgb_history'];rows=[];preds=[];calpreds=[]
    for loss in ['squared_error','absolute_error']:
        for annual in [True,False]:
            pipe=a.hgb_model().set_params(**selected).set_params(model__loss=loss,annual__include_annual=annual)
            pipe.fit(x.loc[tr,hc],y[tr]);p=np.maximum(0,pipe.predict(x.loc[te,hc]));cp=np.maximum(0,pipe.predict(x.loc[ca,hc]))
            q=a.exact_quantile(np.abs(y[ca].to_numpy()-cp));lo=np.maximum(0,p-q);hi=p+q;obs=y[te].to_numpy()
            rows.append(dict(loss=loss,annual=annual,leaves=selected['model__max_leaf_nodes'],l2=selected['model__l2_regularization'],
              coverage=float(((obs>=lo)&(obs<=hi)).mean()),**a.metrics(obs,p)))
            preds.append(pd.DataFrame({'loss':loss,'annual':annual,'issue_time_utc':y.index[te],'observed':obs,'predicted':p,'lower':lo,'upper':hi}))
            calpreds.append(pd.DataFrame({'loss':loss,'annual':annual,'issue_time_utc':y.index[ca],'observed':y[ca].to_numpy(),'predicted':cp}))
    pd.DataFrame(rows).to_csv(r/'configuration_sensitivity.csv',index=False)
    pd.concat(preds,ignore_index=True).to_csv(r/'configuration_predictions.csv',index=False)
    pd.concat(calpreds,ignore_index=True).to_csv(r/'configuration_calibration.csv',index=False)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--results',type=Path,default=a.ROOT/'results');args=p.parse_args();main(args.results)
