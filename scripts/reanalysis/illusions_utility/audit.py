import os
from pathlib import Path
if 'COLOR_RUN' not in os.environ or 'COLOR_ANALYSIS' not in os.environ:
    raise SystemExit('Run via scripts/reanalyze.py --run RUN --output ANALYSIS')
import json, pathlib, collections, csv
import numpy as np
from scipy.stats import binomtest

ROOT=Path(os.environ['COLOR_RUN']).resolve()
OUT=Path(os.environ['COLOR_ANALYSIS'])/'illusions_utility'
OUT.mkdir(parents=True,exist_ok=True)
def summary(v):
    v=np.array([x for x in v if x is not None and np.isfinite(x)],float)
    if not len(v):return dict(n=0,mean=None,ci95=None)
    rng=np.random.default_rng(20261121)
    ci=np.quantile(rng.choice(v,(10000,len(v))).mean(1),[.025,.975]).tolist() if len(v)>1 else None
    nz=v[np.abs(v)>1e-12]
    return dict(n=len(v),mean=float(v.mean()),median=float(np.median(v)),ci95=ci,
                positive=int((v>1e-12).sum()),negative=int((v< -1e-12).sum()),zero=int((abs(v)<=1e-12).sum()),
                sign_p=binomtest(int((nz>0).sum()),len(nz),.5).pvalue if len(nz) else 1.)
def cardinal(angle):
    q=np.asarray(angle)%90
    return np.minimum(q,90-q)
groups=collections.defaultdict(list)
for stage in ['E1','E2','E3','E4','E4_proxy']:
    for cp in sorted((ROOT/'configs').glob(stage+'_*.json')):
        c=json.loads(cp.read_text())
        if c.get('stage')!=stage:continue
        for mode in c.get('models',['untrained','classify','regress','shuffled']):
            p=ROOT/'jobs'/c['id']/f'{mode}.json'
            if p.exists():groups[(stage,c['condition'],mode)].append(json.loads(p.read_text()))
def signed(values):
    # A negative odd response to the two surround polarities is contrast.
    a,b=values
    if a is None or b is None:return None
    return (b-a)/2
results={}
for (stage,condition,mode),rows in groups.items():
    if stage not in ['E1','E2','E3']:continue
    g={};g['n_networks']=len(rows)
    g['test_accuracy']=summary([r['performance']['test'].get('accuracy') for r in rows])
    g['validation_pass']=sum(r['validation_gate'] is True for r in rows)
    if 'learned_or_fixed_b' in rows[0]:g['b']=summary([r['learned_or_fixed_b'] for r in rows])
    g['axes']={}
    for axis in ['RG','BY','luminance']:
        v=collections.defaultdict(list)
        for row in rows:
            if 'illusions' not in row:continue
            a=row['illusions']['axes'][axis]
            v['calibration_readout_norm'].append(a['calibration_readout_norm'])
            v['calibration_local_norm'].append(a['calibration_local_norm'])
            for field in ['readout_shift','local_target_shift','local_interior_shift']:
                v['simultaneous_odd_'+field].append(signed([p[field] for p in a['simultaneous']]))
                for p in a['simultaneous']:
                    v[f'simultaneous_{p["surround_contrast"]}_{field}'].append(p[field])
            for p in a['checkerboard']:
                for f in ['readout_shift','local_target_shift']:
                    v[f'checker_{p["cell_pixels"]}_{p["phase"]}_{f}'].append(p[f])
            for p in a['cornsweet']:
                for f in ['near_signed_difference','distant_signed_difference']:
                    v[f'cornsweet_{p["polarity"]}_{f}'].append(p[f])
            for p in a['mach']:
                for f in ['low_join_signed_residual','high_join_signed_residual']:
                    v[f'mach_{p["control"]}_{f}'].append(p[f])
            for control,p in a['watercolor'].items():
                for f in ['near_contour_shift','far_interior_shift']:
                    v[f'watercolor_{control}_{f}'].append(p[f])
        g['axes'][axis]={k:summary(vv) for k,vv in v.items()}
    if 'spatial_weights' in rows[0]:
        w=[r['spatial_weights'] for r in rows]
        g['spatial']={k:summary([x[k] for x in w]) for k in ['center_mean','surround_mean']}
        g['spatial']['opposite_sign_count']=sum(x['center_mean']*x['surround_mean']<0 for x in w)
    results['/'.join((stage,condition,mode))]=g

contexts={}
for cond in ['intact_base','shuffle_base','boundary_shuffle_base','intact_center_only','shuffle_center_only','boundary_shuffle_center_only']:
    rows=groups[('E2',cond,'classify')]
    contexts[cond]={ctx:summary([r['context_cross_evaluation'][ctx]['accuracy'] for r in rows]) for ctx in ['intact','shuffle','boundary_shuffle']}
    ref={r['seed']:r for r in groups[('E2','intact_'+('center_only' if 'center_only' in cond else 'base'),'classify')]}
    contexts[cond]['test_accuracy_paired_minus_intact']=summary([r['performance']['test']['accuracy']-ref[r['seed']]['performance']['test']['accuracy'] for r in rows])
    contexts[cond]['cross_shuffle_minus_intact']=summary([r['context_cross_evaluation']['shuffle']['accuracy']-r['context_cross_evaluation']['intact']['accuracy'] for r in rows])

utility={};perseed=[]
for (stage,cond,mode),rows in groups.items():
    if stage not in ['E4','E4_proxy']:continue
    records=[]
    for r in rows:
        loc=r['config'].get('utility_locus',0)
        gray=np.array(r['cardinal_axes_reference_lms']);bygray=gray[2]-.5*(gray[0]+gray[1]);conversion=gray[2]+.25*(gray[0]+gray[1])
        rec=dict(stage=stage,condition=cond,seed=r['seed'],locus=loc,weighting=r['config'].get('weighting','uniform'))
        for key in ['sensitivity','normalized_sensitivity']:
            ss=r['sensitivity']['rows'];x=np.array([z['target_contrast'] for z in ss]);y=np.array([z[key] if z[key] is not None else np.nan for z in ss])
            good=np.isfinite(y)
            valid=bool(good.any() and np.nanmax(y)>0 and np.nanmax(y)-np.nanmin(y)>1e-12)
            peak=float(x[np.nanargmax(y)]) if valid else None
            rec[key+'_peak_contrast']=peak
            rec[key+'_peak_by']=float(bygray+conversion*peak) if valid else None
            rec[key+'_range']=float(np.nanmax(y)-np.nanmin(y)) if good.any() else None
            rec[key+'_valid']=valid
            rec[key+'_peak_endpoint']=bool(peak in [-.25,.25]) if valid else None
        rec['test_accuracy']=r['performance']['test']['accuracy']
        if 'weighting' in r:
            rec['effective_sample_size']=r['weighting']['effective_sample_size'];rec['weighted_class_0']=r['weighting']['weighted_class_frequencies'][0]
        records.append(rec);perseed.append(rec)
    utility['/'.join((stage,cond))]=dict(locus=loc,stats={k:summary([r.get(k) for r in records]) for k in ['sensitivity_peak_contrast','sensitivity_peak_by','normalized_sensitivity_peak_contrast','normalized_sensitivity_peak_by','test_accuracy','effective_sample_size','weighted_class_0']},
       valid_raw=sum(r['sensitivity_valid'] for r in records),valid_normalized=sum(r['normalized_sensitivity_valid'] for r in records),
       normalized_peak_endpoints=sum(r['normalized_sensitivity_peak_endpoint'] is True for r in records),
       raw_peak_endpoints=sum(r['sensitivity_peak_endpoint'] is True for r in records))
slopes={}
for stage in ['E4','E4_proxy']:
    for weighting in (['frequency','loss','both'] if stage=='E4' else ['loss']):
        fits=collections.defaultdict(list)
        for seed in range(30):
            rr=[r for r in perseed if r['stage']==stage and r['weighting']==weighting and r['seed']==seed]
            for key in ['sensitivity_peak_contrast','sensitivity_peak_by','normalized_sensitivity_peak_contrast','normalized_sensitivity_peak_by']:
                valid=[r for r in rr if r[key] is not None]
                # Require all three interventions to avoid seed-dependent locus sets.
                if len(valid)==3:
                    fits[key].append(float(np.polyfit([r['locus'] for r in valid],[r[key] for r in valid],1)[0]))
        slopes[stage+'/'+weighting]={k:summary(v) for k,v in fits.items()}

cardinals={}
for (stage,cond,mode),rows in groups.items():
    if stage!='E1':continue
    ref={r['seed']:r for r in groups[(stage,cond,'untrained')]}
    vals=[];raw=[];diff=[];ratios=[]
    for r in rows:
        val=float(np.mean(cardinal(r['cardinal_axes_log_lms_degrees'])));vals.append(val)
        raw.append(float(np.mean(cardinal(r['metrics']['per_filter']['preferred_axis_degrees']))))
        diff.append(val-float(np.mean(cardinal(ref[r['seed']]['cardinal_axes_log_lms_degrees']))))
        theta=np.deg2rad(r['cardinal_axes_log_lms_degrees'])
        ratios.append(float(np.mean(np.sin(theta)**2)/np.mean(np.cos(theta)**2)))
    cardinals[cond+'/'+mode]=dict(log_lms_distance=summary(vals),raw_lms_distance=summary(raw),paired_change_vs_untrained=summary(diff),axis_unit_energy_by_to_rg=summary(ratios))
ground=json.loads((ROOT/'analysis'/'E5f.json').read_text())
pc=[]
for r in ground['pca']:
    v=np.asarray(r['chromatic_axes'])[:,1]
    ang=float(np.rad2deg(np.arctan2(v[1],v[0]))%180)
    pc.append(dict(scene=r['scene'],major_angle=ang,nearest_cardinal_distance=float(cardinal(ang)),variance_ratio=float(r['chromatic_eigenvalues'][1]/r['chromatic_eigenvalues'][0])))
grounding=dict(spatial=ground['summaries'],pca=pc,pca_cardinal_distance=summary([r['nearest_cardinal_distance'] for r in pc]))
daylight=json.loads((ROOT/'analysis'/'E5g_daylight_limits.json').read_text())
daylight={k:v for k,v in daylight.items() if k not in ['spectra','temperatures_kelvin','log_lms_opponent_coordinates']}
out=dict(illusions=results,context=contexts,utility=utility,utility_slopes=slopes,cardinals=cardinals,grounding=grounding,daylight=daylight,
    caveats=['Exploratory audit: bootstrap resamples network seeds (10,000); E5f resamples eight scenes in pre-existing analysis. Sign tests are descriptive, unadjusted exploratory p-values.',
    'Signed simultaneous odd effect is (positive-surround shift minus negative-surround shift)/2. Negative means contrast in representation, not human appearance.',
    'Missing calibrated effects indicate zero/degenerate calibration; not necessarily execution failure. Raw and normalized peak slopes exclude flat/undefined curves and require all three loci per seed.',
    'Utility target_contrast is transformed to physical BY units using the recorded gray reference before comparing against weighting loci. Peak contrast and BY slopes have different units.',
    'Cardinal summary uses each network mean over all filters as independent unit, not pooled-filter inference. Log-LMS conversion is the saved weight-direction conversion, not a new perceptual calibration.'])
(OUT/'audit.json').write_text(json.dumps(out,indent=2))
with (OUT/'utility_perseed.csv').open('w') as f:
    keys=sorted(set(k for r in perseed for k in r));w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(perseed)
print('Saved',OUT/'audit.json')
print('utility slopes',json.dumps(slopes,indent=2))
print('cardinals',json.dumps(cardinals,indent=2))
print('pca',pc)
