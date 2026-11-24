import os
from pathlib import Path
if 'COLOR_RUN' not in os.environ or 'COLOR_ANALYSIS' not in os.environ:
    raise SystemExit('Run via scripts/reanalyze.py --run RUN --output ANALYSIS')
import json,pathlib,numpy as np
ROOT=Path(os.environ['COLOR_RUN']).resolve()
OUT=Path(os.environ['COLOR_ANALYSIS'])/'illusions_utility'
OUT.mkdir(parents=True,exist_ok=True)
def summ(v):
 v=np.array([x for x in v if x is not None and np.isfinite(x)],float)
 if not len(v):return dict(n=0)
 ci=np.quantile(np.random.default_rng(20261121).choice(v,(10000,len(v))).mean(1),[.025,.975]).tolist()
 return dict(n=len(v),mean=float(v.mean()),median=float(np.median(v)),ci95=ci,positive=int((v>1e-7).sum()),negative=int((v< -1e-7).sum()),near_zero=int((np.abs(v)<=1e-7).sum()))
def card(a):
 q=np.array(a)%90;return np.minimum(q,90-q).mean()
extra={};distant=[];far=[];near=[];total=0;missing=0
for cp in sorted((ROOT/'configs').glob('*.json')):
 c=json.loads(cp.read_text());stage=c.get('stage')
 if stage not in ['E1','E2','E3']:continue
 for mode in c.get('models',['untrained','classify','regress','shuffled']):
  r=json.loads((ROOT/'jobs'/c['id']/f'{mode}.json').read_text())
  if 'illusions' not in r:continue
  total+=1
  for axis,a in r['illusions']['axes'].items():
   group=extra.setdefault(stage+'/'+c['condition']+'/'+mode+'/'+axis,dict(mach_odd_canonical=[],mach_minus_linear_low=[],mach_minus_linear_high=[],watercolor_closed_minus_open=[]))
   m={p['control']:p for p in a['mach']}
   def delta(m):return m['high_join_signed_residual']-m['low_join_signed_residual']
   if all(m[k]['low_join_signed_residual'] is not None and m[k]['high_join_signed_residual'] is not None for k in ['ramp','reversed','linear']):
    group['mach_odd_canonical'].append((delta(m['ramp'])-delta(m['reversed']))/2)
    group['mach_minus_linear_low'].append(m['ramp']['low_join_signed_residual']-m['linear']['low_join_signed_residual'])
    group['mach_minus_linear_high'].append(m['ramp']['high_join_signed_residual']-m['linear']['high_join_signed_residual'])
   w=a['watercolor']
   if w['closed']['near_contour_shift'] is not None and w['open']['near_contour_shift'] is not None:
    group['watercolor_closed_minus_open'].append(w['closed']['near_contour_shift']-w['open']['near_contour_shift'])
   for p in a['cornsweet']:
    if p['distant_signed_difference'] is not None:distant.append(abs(p['distant_signed_difference']))
    else:missing+=1
   for p in w.values():
    if p['far_interior_shift'] is not None:far.append(abs(p['far_interior_shift']))
cardinal={}
for cond in ['p9_baseline','p27_fixed','p27_dilated','p27_coarse']:
 val=[]
 for seed in range(30):
  job=ROOT/'jobs'/f'E1_{cond}_s{seed:02d}'
  a,b=[json.loads((job/f'{mode}.json').read_text()) for mode in ['classify','shuffled']]
  val.append(card(a['cardinal_axes_log_lms_degrees'])-card(b['cardinal_axes_log_lms_degrees']))
 cardinal[cond]=summ(val)
identity={}
for mode in ['untrained','classify','regress','shuffled']:
 equal=[]
 for seed in range(30):
  a,b=[json.loads((ROOT/'jobs'/f'E2_{cond}_s{seed:02d}'/f'{mode}.json').read_text()) for cond in ['intact_center_only','boundary_shuffle_center_only']]
  equal.append(all(a[k]==b[k] for k in ['metrics','performance','illusions','sensitivity','learning_curve']))
 identity[mode]=sum(equal)
out=dict(mach_and_contour={k:{field:summ(vv) for field,vv in v.items()} for k,v in extra.items()},
 cardinal_classify_minus_shuffled=cardinal,
 far_checks=dict(total_networks=total,cornsweet_finite=len(distant),cornsweet_max_abs=max(distant),cornsweet_undefined=missing,watercolor_finite=len(far),watercolor_max_abs=max(far)),
 center_only_intact_boundary_equal=identity,
 interpretation='Mach canonical signed index is high-join minus low-join residual, polarity-odd. Positive matches bright high-side/dark low-side overshoot; negative matches smoothing. This remains a representation response, not a psychophysical appearance estimate.')
(OUT/'additional_audit.json').write_text(json.dumps(out,indent=2))
print('far_checks',out['far_checks']);print('identity',identity);print('cardinal_classifier_minus_shuffled',cardinal)
for key in ['E1/p9_baseline/classify/BY','E1/p27_fixed/classify/BY','E3/p9_learned_b_0/classify/BY','E3/p27_learned_b_0/classify/BY']:
 print(key,out['mach_and_contour'][key])
