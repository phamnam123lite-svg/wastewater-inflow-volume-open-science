"""Render the final figures from saved numerical results (no model fitting)."""
from pathlib import Path
import argparse
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

LABEL={'persistence':'Persistence','mean24':'24-h mean','seasonal24':'Previous day','ridge_history':'Ridge history',
 'hgb_flow':'HGB flow','hgb_history':'HGB history','hgb_oracle':'HGB oracle*','legacy_squared':'Legacy HGB',
 'fixed_history':'Fixed absolute-loss HGB'}
COLORS=['#186b8c','#bf762e','#4b8c65','#9b4f70']

def main(r,f):
    f.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,
      'svg.fonttype':'none','pdf.fonttype':42,'axes.titleweight':'bold'})
    def save(fig,name):
        fig.tight_layout()
        for ext in ['png','svg','pdf']:fig.savefig(f/(name+'.'+ext),dpi=300,bbox_inches='tight')
        plt.close(fig)
    m=pd.read_csv(r/'metrics.csv');it=pd.read_csv(r/'intervals.csv');spl=pd.read_csv(r/'splits.csv')
    d=pd.read_csv(r/'cleaned_hourly.csv',index_col=0,parse_dates=True)
    fig,axes=plt.subplots(2,1,figsize=(9,5),sharex=True)
    axes[0].plot(d.index,d.flow,lw=.5,color=COLORS[0]);axes[0].set_ylabel('Archived inflow rate (m³/h)')
    axes[1].plot(d.index,d.acc_precip,lw=.5,color=COLORS[1]);axes[1].set_ylabel('Hourly precipitation (mm)')
    cut=spl[spl.scenario=='primary_12h'].iloc[0]
    for ax in axes:
        ax.axvline(pd.Timestamp(cut.train_boundary),color='#333333',ls='--',lw=.8)
        ax.axvline(pd.Timestamp(cut.test_boundary),color='#333333',ls='--',lw=.8)
    for lab,start,end in [('Development',d.index.min(),pd.Timestamp(cut.train_boundary)),('Calibration',pd.Timestamp(cut.train_boundary),pd.Timestamp(cut.test_boundary)),('Test',pd.Timestamp(cut.test_boundary),d.index.max())]:
        axes[0].text(start+(end-start)/2,1.02,lab,transform=axes[0].get_xaxis_transform(),ha='center',fontsize=9)
    axes[1].xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'));save(fig,'Figure_1_timeline')
    z=m[(m.scenario=='primary_12h')&(m.group=='all')].set_index('model')
    names=['persistence','mean24','seasonal24','ridge_history','legacy_squared','fixed_history','hgb_flow','hgb_history','hgb_oracle']
    fig,ax=plt.subplots(figsize=(8,4.8));colors=[COLORS[0]]*len(names);colors[-1]=COLORS[1];colors[4]='#999999'
    ax.barh(np.arange(len(names)),z.loc[names,'MAE_m3'],color=colors)
    for i,n in enumerate(names):ax.text(z.loc[n,'MAE_m3']+80,i,f"{z.loc[n,'MAE_m3']:,.0f}",va='center',fontsize=8)
    ax.set_yticks(np.arange(len(names)),[LABEL[n] for n in names]);ax.invert_yaxis();ax.set_xlim(0,8800)
    ax.set_xlabel('12-hour integrated-rate target MAE (m³)');ax.set_title('Primary test: 2,160 overlapping issue windows')
    ax.text(0,-.18,'* Oracle uses future observed rainfall; diagnostic only.',transform=ax.transAxes,fontsize=8);save(fig,'Figure_2_primary_accuracy')
    origins=['origin_2024-08-15','origin_2024-10-15','origin_2024-12-15'];names=['mean24','hgb_flow','hgb_history','hgb_oracle']
    fig,ax=plt.subplots(figsize=(8,4));pos=np.arange(3)
    for j,n in enumerate(names):
        z=m[(m.group=='all')&(m.model==n)].set_index('scenario');ax.bar(pos+(j-1.5)*.19,z.loc[origins,'MAE_m3'],width=.18,color=COLORS[j],label=LABEL[n])
    ax.set_xticks(pos,['15 Aug 2024','15 Oct 2024','15 Dec 2024']);ax.set_xlabel('Start of 60-day test period (UTC)');ax.set_ylabel('12-hour target MAE (m³)')
    ax.legend(ncol=2,fontsize=8);save(fig,'Figure_3_temporal_origins')
    fig,axes=plt.subplots(1,3,figsize=(9,3.8),sharey=True);names=['mean24','hgb_history','hgb_oracle']
    for ax,model in zip(axes,names):
        for j,group in enumerate(['all','wet','high']):
            z=it[(it.scenario=='primary_12h')&(it.model==model)&(it.group==group)].set_index('method')
            vals=z.loc[['pooled','wet_dry','rolling30d'],'coverage'];ax.bar(np.arange(3)+(j-1)*.23,vals,width=.22,label=group,color=COLORS[j])
        ax.set_xticks(range(3),['Pooled','Wet/dry','Rolling'],rotation=25);ax.axhline(.9,color='gray',ls='--',lw=.8);ax.set_title(LABEL[model]);ax.set_ylim(0,1.04)
    axes[0].set_ylabel('Empirical coverage');axes[1].legend(ncol=3,loc='lower center',bbox_to_anchor=(.5,-.42),fontsize=8)
    save(fig,'Figure_4_interval_reliability')
    ep=pd.read_csv(r/'episodes.csv');ep=ep[ep.scenario=='primary_12h']
    fig,ax=plt.subplots(figsize=(8,3.7));names=['mean24','hgb_history','fixed_history']
    for j,n in enumerate(names):
        z=ep[ep.model==n].sort_values('episode');ax.scatter(z.episode+(j-1)*.12,z.coverage,s=45,color=COLORS[j],label=LABEL[n])
    z=ep[ep.model=='mean24'];ax.set_xticks(z.episode,[f"{pd.Timestamp(s):%d %b}\n(n={n})" for s,n in zip(z.start,z.n)])
    ax.axhline(.9,color='gray',ls='--',lw=.8);ax.set_ylim(-.04,1.04);ax.set_ylabel('Pooled-interval coverage');ax.set_xlabel('Contiguous high-volume episode (overlapping windows)');ax.legend(fontsize=8,ncol=3,loc='lower center',bbox_to_anchor=(.5,1.01));save(fig,'Figure_5_episodes')

if __name__=='__main__':
    p=argparse.ArgumentParser();root=Path(__file__).parent;p.add_argument('--results',type=Path,default=root/'results');p.add_argument('--figures',type=Path,default=root/'figures');a=p.parse_args();main(a.results,a.figures)
