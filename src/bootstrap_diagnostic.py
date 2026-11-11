"""Synthetic AR(1) check of block-bootstrap coverage; simulated data, not plant observations."""
from pathlib import Path
import argparse
import numpy as np
import pandas as pd
from run_analysis import SEED

def main(out):
    rng=np.random.default_rng(SEED);n=1920;B=48;mc=200;nb=400;rows=[]
    idx=(np.arange(n)[:,None]+np.arange(B))%n
    for rho in [0.,.5,.9]:
        covers=[];widths=[];centering=[]
        for rep in range(mc):
            innovation=rng.normal(size=n+400)*np.sqrt(1-rho*rho);z=np.zeros(n+400)
            for i in range(1,len(z)):z[i]=rho*z[i-1]+innovation[i]
            z=z[-n:];sums=z[idx].sum(axis=1);boot=sums[rng.integers(n,size=(nb,n//B))].sum(axis=1)/n
            low,high=np.quantile(boot,[.025,.975]);covers.append(low<=0<=high);widths.append(high-low);centering.append(boot.mean()-z.mean())
        coverage=np.mean(covers);rows.append(dict(SYNTHETIC_rho=rho,n=n,block=B,monte_carlo=mc,bootstrap_replicates=nb,
            coverage=coverage,monte_carlo_standard_error=np.sqrt(coverage*(1-coverage)/mc),mean_width=np.mean(widths),mean_bootstrap_centering_error=np.mean(centering)))
    pd.DataFrame(rows).to_csv(out,index=False)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=Path(__file__).resolve().parents[1]/'results'/'denmark'/'SYNTHETIC_bootstrap_diagnostic.csv');args=p.parse_args();main(args.output)
