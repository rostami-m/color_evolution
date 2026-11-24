import os
from pathlib import Path
if 'COLOR_RUN' not in os.environ or 'COLOR_ANALYSIS' not in os.environ:
    raise SystemExit('Run via scripts/reanalyze.py --run RUN --output ANALYSIS')
"""Read-only E5a/b/c post-run audit. Seed blocks are inferential units.
Exploratory two-sided sign-flip p-values, BH separately for each stage,
comparison type and metric across all included conditions; percentile bootstrap CIs.
Never pool reused E1/E0 or shared-initialization architecture seeds as independent replicates.
"""
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
from pathlib import Path
import json,csv,hashlib
from collections import defaultdict
import numpy as np
ROOT=Path(os.environ['COLOR_RUN']).resolve()
DEST=Path(os.environ['COLOR_ANALYSIS'])/'robustness'
DEST.mkdir(parents=True,exist_ok=True)
NBOOT=10000;NPERM=65535

def random_seed(key):return int(hashlib.sha256(key.encode()).hexdigest()[:8],16)
def summ(values,key):
 v=np.asarray([x for x in values if x is not None and np.isfinite(x)],dtype=float)
 if not len(v):return dict(n=0,mean=None,ci95=None)
 rng=np.random.default_rng(random_seed(key))
 ci=np.quantile(v[rng.integers(len(v),size=(NBOOT,len(v)))].mean(1),[.025,.975]).tolist()
 return dict(n=len(v),mean=float(v.mean()),ci95=ci,median=float(np.median(v)),min=float(v.min()),max=float(v.max()))
def signflip(v,key):
 v=np.asarray(v,float);v=v[v!=0]
 if not len(v):return 1.
 rng=np.random.default_rng(random_seed(key));obs=abs(v.mean());n=0
 for i in range(0,NPERM,2048):
  z=rng.choice([-1.,1.],size=(min(2048,NPERM-i),len(v)))
  n+=np.count_nonzero(abs(z@v/len(v))>=obs-1e-14)
 return (n+1)/(NPERM+1)
def scalar(row,name):
 m=row['metrics']
 if name.startswith('legacy_'):
  v=m['legacy'][name.removeprefix('legacy_')]
  return float(np.mean(v))
 if name in m:return float(m[name])
 if '/' in name:
  split,metric=name.split('/')
  return row['performance'][split].get(metric)
 raise KeyError(name)
metrics=['raw_chromatic_power','normalized_chromatic_power','double_opponency_score','double_opponent_fraction','legacy_chromatic_power','legacy_double_opponency_score','legacy_double_opponent_fraction']
perfs=['train/accuracy','validation/accuracy','test/accuracy','illuminant_extrapolation/accuracy','train/r2','validation/r2','test/r2','illuminant_extrapolation/r2','train/rmse_kelvin','validation/rmse_kelvin','test/rmse_kelvin']
rows={}; groups=defaultdict(dict);counts={}; allcomps=[];summaries=[]
for stage in ['E5a','E5b','E5c']:
 for cp in sorted((ROOT/'configs').glob('*.json')):
  c=json.loads(cp.read_text()); s=c.get('stage');co=c.get('condition'); exbase=stage in ('E5a','E5b') and s=='E1' and co in ('p9_baseline','p27_fixed');exsynth=stage=='E5b' and s=='E0_synthetic'
  if s!=stage and not(exbase or exsynth):continue
  co=co+('_synthetic' if exsynth else '')
  for mode in c['models'] if 'models' in c else ['untrained','classify','regress','shuffled']:
   p=ROOT/'jobs'/c['id']/f'{mode}.json';r=json.loads(p.read_text());r['_source']=str(p);r['_origin_stage']=s
   groups[(stage,co,mode)][c['seed']]=r
for (stage,co,mode), rs in groups.items():
 stat=dict(stage=stage,condition=co,mode=mode,n=len(rs),unique_job_ids=sorted({r['config']['id'] for r in rs.values()}),origin_stages=sorted({r['_origin_stage'] for r in rs.values()}),validation_gate_pass=sum(r['validation_gate'] is True for r in rs.values()),validation_gate_applicable=mode!='regress',metrics={},convergence={})
 for metric in metrics+perfs:
  stat['metrics'][metric]=summ([scalar(r,metric) for r in rs.values()],f'{stage}/{co}/{mode}/{metric}')
 curves=[]
 for r in rs.values():
  lc=r['learning_curve']
  if mode=='untrained':continue
  if mode=='cma':
   curve=lc['curve'];curves.append(dict(seed=r['seed'],initial=curve[0]['best_cross_entropy'],final=curve[-1]['best_cross_entropy'],final50_improvement=curve[-51]['best_cross_entropy']-curve[-1]['best_cross_entropy'],fitness_evaluations=lc['fitness_evaluations']))
  else:
   curves.append(dict(seed=r['seed'],initial=lc[0]['loss'],final=lc[-1]['loss'],final10_improvement=lc[-11]['loss']-lc[-1]['loss']))
 stat['convergence']['curves']=curves
 if curves:
  for key in curves[0]:
   if key!='seed':stat['convergence'][key]=summ([r[key] for r in curves],f'{stage}/{co}/{mode}/{key}')
  stat['convergence']['nonfinite_loss']=sum(not np.isfinite(r['final']) for r in curves)
 summaries.append(stat)

def contrast(stage,co,left,right,label,metric):
 common=sorted(set(left)&set(right));values=[];seedids=[]
 for seed in common:
  x,y=scalar(left[seed],metric),scalar(right[seed],metric)
  if x is not None and y is not None and np.isfinite(x) and np.isfinite(y):values.append(x-y);seedids.append(seed)
 if not values:return
 key=f'{stage}/{co}/{label}/{metric}';res=dict(stage=stage,condition=co,comparison=label,metric=metric,paired_seeds=seedids,differences=values,summary=summ(values,key),p_signflip=signflip(values,key),positive=sum(x>0 for x in values),negative=sum(x<0 for x in values),ties=sum(x==0 for x in values))
 allcomps.append(res)
for stage in ['E5a','E5b','E5c']:
 conditions=sorted({c for s,c,m in groups if s==stage})
 for co in conditions:
  cls=groups[(stage,co,'classify')]
  for ctl in ['regress','untrained','shuffled','cma']:
   other=groups.get((stage,co,ctl))
   if other:
    for metric in metrics:contrast(stage,co,cls,other,'classify_minus_'+ctl,metric)
  if stage=='E5c':
   for metric in [x for x in perfs if x.endswith('/accuracy')]:contrast(stage,co,cls,groups[(stage,co,'cma')],'classify_minus_cma',metric)
  if stage=='E5b':
   ref='p9_baseline' if co.startswith('p9_') else 'p27_fixed'
   if co!=ref:
    for mode in ['classify','regress']:
     ms=metrics+[x for x in perfs if x.endswith('/accuracy' if mode=='classify' else '/r2')]
     for metric in ms:contrast(stage,co,groups[(stage,co,mode)],groups[(stage,ref,mode)],mode+'_minus_matched_baseline',metric)
  if stage=='E5a' and co.startswith('p27_'):
   ref='p9_baseline' if co=='p27_fixed' else co.replace('p27_','p9_')
   for mode in ['classify','regress','untrained','shuffled']:
    for metric in metrics:contrast(stage,co,groups[(stage,co,mode)],groups[(stage,ref,mode)],mode+'_p27_minus_p9',metric)
families=defaultdict(list)
for r in allcomps:families[(r['stage'],r['comparison'],r['metric'])].append(r)
for key,rs in families.items():
 rs.sort(key=lambda r:r['p_signflip']);running=1.
 for rank in range(len(rs)-1,-1,-1):
  running=min(running,rs[rank]['p_signflip']*len(rs)/(rank+1));rs[rank]['q_BH']=running;rs[rank]['BH_family_size']=len(rs)
result=dict(root=str(ROOT),bootstrap_resamples=NBOOT,signflip_resamples=NPERM,inference_unit='paired network/data seed; not filters, trials, or reused stage records',testing='Exploratory post-run bootstrap intervals; two-sided Monte Carlo sign-flip p-values; Benjamini-Hochberg separately by stage/comparison/metric. No equivalence margin.',caveats=['E5a contains 2640 new model records plus 240 reused E1 records.','E5b contains 1200 new records plus 240 reused E1 and 240 reused synthetic control records.','Shared initialization across architecture bottlenecks is not independently replicated evidence.','No validation gate is defined for regressors: pass_count=0 is not 30 failed regressors.','Generalization assessed on fixed held-out scenes and seed-specific prototype subsets, not new scene partitions.','New normalized power/axis coherence/sign-balance metric differs from legacy amplitude-dependent metric.'],groups=summaries,comparisons=allcomps)
(DEST/'audit.json').write_text(json.dumps(result,indent=2))
with (DEST/'comparisons.csv').open('w') as f:
 writer=csv.DictWriter(f,fieldnames=['stage','condition','comparison','metric','n','mean_difference','CI_low','CI_high','p_signflip','q_BH','BH_family_size','positive','negative','ties']);writer.writeheader()
 for r in allcomps:
  out={k:r[k] for k in ['stage','condition','comparison','metric','p_signflip','q_BH','BH_family_size','positive','negative','ties']};out.update(n=r['summary']['n'],mean_difference=r['summary']['mean'],CI_low=r['summary']['ci95'][0],CI_high=r['summary']['ci95'][1]);writer.writerow(out)
with (DEST/'groups.csv').open('w') as f:
 writer=csv.DictWriter(f,fieldnames=['stage','condition','mode','metric','n','mean','CI_low','CI_high','validation_gate_pass','validation_gate_applicable']);writer.writeheader()
 for r in summaries:
  for metric,s in r['metrics'].items():
   writer.writerow(dict(stage=r['stage'],condition=r['condition'],mode=r['mode'],metric=metric,n=s['n'],mean=s['mean'],CI_low=s['ci95'][0] if s['ci95'] else None,CI_high=s['ci95'][1] if s['ci95'] else None,validation_gate_pass=r['validation_gate_pass'],validation_gate_applicable=r['validation_gate_applicable']))
print('Saved',len(summaries),'groups;',len(allcomps),'paired contrasts;',len(families),'BH families to',DEST)
