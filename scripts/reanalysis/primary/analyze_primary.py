import os
from pathlib import Path
if 'COLOR_RUN' not in os.environ or 'COLOR_ANALYSIS' not in os.environ:
    raise SystemExit('Run via scripts/reanalyze.py --run RUN --output ANALYSIS')
"""Post-run comparison; reads immutable records, performs no model training."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):
    os.environ[key]='2'
from pathlib import Path
import json, csv, hashlib
from collections import defaultdict
import numpy as np
from scipy.stats import binomtest

ROOT=Path(os.environ['COLOR_RUN']).resolve()
OUT=Path(os.environ['COLOR_ANALYSIS'])/'primary'
OUT.mkdir(parents=True,exist_ok=True)
RNG=np.random.default_rng(20261121)
BOOT=RNG.integers(0,30,(10000,30))


def summary(v):
    v=np.asarray(v,float);v=v[np.isfinite(v)]
    if not len(v):return dict(n=0,mean=None,ci95=None)
    ids=BOOT if len(v)==30 else np.random.default_rng(20261121).integers(0,len(v),(10000,len(v)))
    return dict(n=len(v),mean=float(v.mean()),ci95=np.quantile(v[ids].mean(axis=1),[.025,.975]).tolist(),min=float(v.min()),max=float(v.max()))


def vector(d):
    m=d['metrics'];old=m['legacy']
    row={k:m[k] for k in ('raw_chromatic_power','normalized_chromatic_power','double_opponency_score','double_opponent_fraction')}
    row.update(legacy_chromatic_power=float(np.mean(old['chromatic_power'])),legacy_score=float(np.mean(old['double_opponency_score'])),legacy_fraction=old['double_opponent_fraction'],legacy_count=old['double_opponent_fraction']*m['n_filters'],corrected_count=m['double_opponent_fraction']*m['n_filters'])
    for split,perf in d['performance'].items():
        for key,val in perf.items():
            if isinstance(val,(float,int)):row[f'{split}_{key}']=val
        if 'class_recall' in perf:
            for i,val in enumerate(perf['class_recall']):row[f'{split}_recall{i}']=val
    curve=d['learning_curve']
    if curve:
        row['first_loss']=curve[0]['loss'];row['last_loss']=curve[-1]['loss']
    row['validation_gate']=int(d['validation_gate'] is True)
    return row


groups=defaultdict(dict);flat=[]
for configpath in sorted((ROOT/'configs').glob('*.json')):
    c=json.loads(configpath.read_text())
    if c['stage'] not in ('E0_synthetic','E1'):continue
    for mode in c.get('models',['untrained','classify','regress','shuffled']):
        d=json.loads((ROOT/'jobs'/c['id']/f'{mode}.json').read_text())
        row=vector(d)
        groups[(c['stage'],c['condition'],mode)][c['seed']]=(row,d)
        flat.append(dict(stage=c['stage'],condition=c['condition'],mode=mode,seed=c['seed'],**row))

output=[]
for (stage,condition,mode),rows in groups.items():
    keys=sorted(set().union(*(v[0].keys() for v in rows.values())))
    output.append(dict(stage=stage,condition=condition,mode=mode,n=len(rows),metrics={k:summary([rows[s][0].get(k,np.nan) for s in sorted(rows)]) for k in keys}))

contrasts=[]
def contrast(label, a, b):
    A,B=groups[a],groups[b];seeds=sorted(A.keys()&B.keys())
    keys=sorted(set.intersection(*(set(A[s][0])&set(B[s][0]) for s in seeds)))
    metrics={k:summary([A[s][0][k]-B[s][0][k] for s in seeds]) for k in keys}
    contrasts.append(dict(label=label,A=a,B=b,paired_seeds=seeds,metrics=metrics))

for stage,condition in sorted({(x[0],x[1]) for x in groups}):
    for mode in ('untrained','shuffled','regress'):
        contrast(f'{stage}/{condition}: classify minus {mode}',(stage,condition,'classify'),(stage,condition,mode))
    contrast(f'{stage}/{condition}: shuffled minus untrained',(stage,condition,'shuffled'),(stage,condition,'untrained'))
for mode in ('classify','regress','shuffled','untrained'):
    for condition in ('p27_fixed','p27_dilated','p27_coarse'):
        contrast(f'E1/{mode}: {condition} minus p9_baseline',('E1',condition,mode),('E1','p9_baseline',mode))
    for condition in ('p27_dilated','p27_coarse'):
        contrast(f'E1/{mode}: {condition} minus p27_fixed',('E1',condition,mode),('E1','p27_fixed',mode))

decode=[]
for key,rows in groups.items():
    for noise in (0.,.02,.05):
        records=[]
        for seed,(_,d) in rows.items():
            points=[x for x in d.get('decodability',{}).get('rows',[]) if x['sensor_noise']==noise]
            if points:records.append(points[0])
        if records:
            decode.append(dict(stage=key[0],condition=key[1],mode=key[2],sensor_noise=noise,
                representation='learned or random network representation, not raw cone features',
                metrics={k:summary([r[k] for r in records]) for k in ('test_classification_accuracy','test_illuminant_r2','test_illuminant_rmse','constant_train_mean_test_rmse')}))

primary=json.loads((ROOT/'analysis/E1.json').read_text())['objective_comparisons']
artifact=dict(unit='network seed; conditional on fixed scene partitions',interval='10000 paired-seed bootstrap draws; descriptive exploratory intervals except frozen primary comparison',groups=output,contrasts=contrasts,learned_representation_decoding=decode,frozen_primary_comparisons=primary)
(OUT/'primary_analysis.json').write_text(json.dumps(artifact,indent=2)+'\n')
keys=sorted(set().union(*(r.keys() for r in flat)))
with (OUT/'per_seed.csv').open('w',newline='') as f:
    writer=csv.DictWriter(f,keys);writer.writeheader();writer.writerows(flat)
for row in output:
    m=row['metrics']
    def fmt(k):
        v=m.get(k,{})
        return None if v.get('mean') is None else round(v['mean'],5)
    print(row['stage'],row['condition'],row['mode'],{k:fmt(k) for k in ['legacy_chromatic_power','legacy_count','normalized_chromatic_power','double_opponency_score','double_opponent_fraction','train_accuracy','validation_accuracy','test_accuracy','illuminant_extrapolation_accuracy','test_r2','validation_gate']})
print('PRIMARY',primary)
