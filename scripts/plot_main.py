"""Reproduce comparison plots from the saved post-run summaries; no training."""
import os
os.environ.setdefault('MPLCONFIGDIR', str(__import__('tempfile').gettempdir()+'/color_paper_mpl'))

from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(os.environ.get('COLOR_BUNDLE',Path(__file__).resolve().parents[1]/'published_results'))
OUT = Path(os.environ.get('COLOR_FIGURES',Path(__file__).resolve().parents[1]/'generated/figures'))
OUT.mkdir(parents=True,exist_ok=True)
P = json.loads((ROOT / 'primary/primary_analysis.json').read_text())
R = json.loads((ROOT / 'robustness/audit.json').read_text())
groups = {(r['stage'], r['condition'], r['mode']): r['metrics'] for r in P['groups']}
robust = {(r['stage'], r['condition'], r['mode']): r['metrics'] for r in R['groups']}
colors = {'classify':'#126E82', 'regress':'#BD5531', 'untrained':'#777777', 'shuffled':'#9773AC'}
plt.rcParams.update({'font.size':12.5, 'axes.titlesize':13, 'axes.labelsize':12.5, 'xtick.labelsize':12.5, 'ytick.labelsize':12.5,
                     'pdf.fonttype':42, 'ps.fonttype':42, 'axes.spines.top':False,
                     'axes.spines.right':False, 'legend.frameon':True, 'legend.framealpha':1.0, 'legend.edgecolor':'#dddddd'})

def points(ax, xs, stats, color, label, marker='o', line=False):
    means=np.array([s['mean'] for s in stats]); ci=np.array([s['ci95'] for s in stats])
    ax.errorbar(xs,means,yerr=np.array([means-ci[:,0],ci[:,1]-means]),
                color=color,marker=marker,ls='-' if line else 'none',capsize=2,
                markersize=4.8,lw=1.1,label=label)

def g(cond,mode,metric,stage='E1'):
    return groups[(stage,cond,mode)][metric]

fig, axes=plt.subplots(3,2,figsize=(8.2,8.5))
fig.subplots_adjust(left=.115,right=.98,top=.94,bottom=.085,wspace=.52,hspace=.82)

ax=axes[0,0]
for i,(mode,label) in enumerate([('untrained','Untrained'),('shuffled','Shuffled'),('classify','Classifier')]):
    points(ax,np.array([0,1])+(.15*(i-1)),[g(c,mode,'legacy_chromatic_power') for c in ['p9_baseline','p27_fixed']],colors[mode],label)
ax.set(xticks=[0,1],xticklabels=['9×9','27×27'],ylabel='Chromatic amplitude',ylim=(0,1.24),title='A  Chromatic amplitude')
ax.legend(fontsize=12.5,loc='upper center',bbox_to_anchor=(.64,1.0))

ax=axes[0,1]
for offset,metric,label,color in [(-.16,'train_accuracy','Train','#9BA3A7'),(0,'validation_accuracy','Validation','#3D8B52'),(.16,'test_accuracy','Test','#126E82')]:
    stats=[g('p9_baseline','classify',metric),g('p27_fixed','classify',metric),g('p9','classify',metric,'E0_synthetic'),g('p27','classify',metric,'E0_synthetic')]
    points(ax,np.arange(4)+offset,stats,color,label)
ax.set(xticks=range(4),xticklabels=['Natural\n9','Natural\n27','Synth.\n9','Synth.\n27'],ylabel='Category accuracy',ylim=(0,1.04),title='B  Accuracy by split')
ax.legend(fontsize=12.5,loc='lower left',ncol=1)

conds=['p9_baseline','p27_fixed','p27_dilated','p27_coarse']
labels=['9\nbase','27\nfixed','27\ndilated','27\ncoarse']
ax=axes[1,0]
for offset,mode,label in [(-.09,'classify','Classifier'),(.09,'regress','Regressor')]:
    points(ax,np.arange(4)+offset,[g(c,mode,'legacy_count') for c in conds],colors[mode],label)
ax.set(xticks=range(4),xticklabels=labels,ylabel='Filters above null / 8',ylim=(-.1,6.3),title='C  Amplitude-based counts')
ax.legend(fontsize=12.5,loc='upper right')

ax=axes[1,1]
for offset,mode,label in [(-.12,'classify','Classifier'),(0,'regress','Regressor'),(.12,'untrained','Untrained')]:
    stats=[{**g(c,mode,'double_opponent_fraction'),'mean':100*g(c,mode,'double_opponent_fraction')['mean'],'ci95':[100*v for v in g(c,mode,'double_opponent_fraction')['ci95']]} for c in conds]
    points(ax,np.arange(4)+offset,stats,colors[mode],label)
ax.set(xticks=range(4),xticklabels=labels,ylabel='Above normalized null (%)',ylim=(-.5,19),title='D  Normalized counts')
ax.legend(fontsize=12.5,loc='upper right')

ax=axes[2,0]
for offset,mode,label in [(-.1,'classify','Classifier'),(.1,'regress','Regressor')]:
    points(ax,np.arange(4)+offset,[g(c,mode,'double_opponency_score') for c in conds],colors[mode],label)
ax.axhline(g('p9_baseline','untrained','double_opponency_score')['mean'],color=colors['untrained'],ls='--',label='Untrained mean')
ax.set(xticks=range(4),xticklabels=labels,ylabel='Normalized opponent score',ylim=(0,.38),title='E  Normalized score')
ax.legend(fontsize=12.5,loc='upper right')

ax=axes[2,1]
for offset,p,color in [(-.09,9,'#126E82'),(.09,27,'#BD5531')]:
    default=g('p9_baseline' if p==9 else 'p27_fixed','regress','test_r2')
    candidates=[v for (s,c,m),v in robust.items() if s=='E5b' and c.startswith(f'p{p}_') and 'neutral' in c and m=='regress']
    assert len(candidates)==1, len(candidates)
    points(ax,np.arange(2)+offset,[default,candidates[0]['test/r2']],color,f'{p}×{p}')
ax.axhline(0,color='#888888',lw=.7)
ax.set(xticks=[0,1],xticklabels=['Unknown','Neutral'],ylabel='Test illuminant R²',ylim=(-1.05,1.9),title='F  Neutral-reference effect')
ax.legend(fontsize=12.5,loc='upper left')
for ax in axes.flat:
    ax.grid(axis='y',alpha=.15)

fig.savefig(OUT/'main_results.pdf')
fig.savefig(OUT/'main_results.png',dpi=200)
plt.close(fig)
print(OUT/'main_results.pdf')
