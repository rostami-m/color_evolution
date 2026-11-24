import os
from pathlib import Path
if 'COLOR_RUN' not in os.environ or 'COLOR_ANALYSIS' not in os.environ:
    raise SystemExit('Run via scripts/reanalyze.py --run RUN --output ANALYSIS')
"""Exploratory CMA versus its matched first-layer initialization, reused from E1.
The E1 and E5c make_model calls use the same seed/body, so the initial conv1 weights match.
"""
import os
for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:os.environ[k]='1'
from pathlib import Path
import json
import numpy as np
ROOT=Path(os.environ['COLOR_RUN']).resolve()
results=[]
for size,condition in [(9,'p9_baseline'),(27,'p27_fixed')]:
 for metric in ['normalized_chromatic_power','double_opponency_score','double_opponent_fraction']:
  diffs=[];vals=[];refs=[]
  for seed in range(30):
   c=json.loads((ROOT/'jobs'/f'E5c_p{size}_optimizer_s{seed:02d}'/'cma.json').read_text())
   u=json.loads((ROOT/'jobs'/f'E1_{condition}_s{seed:02d}'/'untrained.json').read_text())
   vals.append(c['metrics'][metric]);refs.append(u['metrics'][metric]);diffs.append(vals[-1]-refs[-1])
  v=np.array(diffs);rng=np.random.default_rng(20261121+size)
  ci=np.quantile(rng.choice(v,(10000,30)).mean(1),[.025,.975]).tolist()
  count=0
  for i in range(0,65535,2048):
   signs=rng.choice([-1,1],(min(2048,65535-i),30));count+=np.count_nonzero(abs((signs*v).mean(1))>=abs(v.mean())-1e-14)
  results.append(dict(size=size,metric=metric,cma_mean=float(np.mean(vals)),untrained_mean=float(np.mean(refs)),mean_difference=float(v.mean()),CI95=ci,p_signflip=(count+1)/65536,paired_seed_differences=diffs))
for metric in sorted({r['metric'] for r in results}):
 rows=sorted([r for r in results if r['metric']==metric],key=lambda r:r['p_signflip']);running=1.
 for rank in range(len(rows)-1,-1,-1):
  running=min(running,rows[rank]['p_signflip']*len(rows)/(rank+1));rows[rank]['q_BH']=running
out=dict(comparison='CMA minus matched first-layer initialization, seed-paired; exploratory, not equivalence test',bootstrap_resamples=10000,signflip_resamples=65535,BH_family='two patch sizes within each metric',results=results)
(Path(os.environ['COLOR_ANALYSIS'])/'robustness/cma_initialization_audit.json').write_text(json.dumps(out,indent=2))
for r in results:print({k:v for k,v in r.items() if k!='paired_seed_differences'})
