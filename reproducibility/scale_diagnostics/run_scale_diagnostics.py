"""Post-production, CPU-only frozen-checkpoint diagnostics. No optimizer or training.

Usage: python run_scale_diagnostics.py --run RUN --runtime CODE --data-dir DATA --output OUT
The separately frozen protocol.json must exist in OUT before this script starts.
"""
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS',
            'MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','BLIS_NUM_THREADS'):
    os.environ[key] = '2'
os.environ.update(CUDA_VISIBLE_DEVICES='', HIP_VISIBLE_DEVICES='', ROCR_VISIBLE_DEVICES='',
                  DEVICE='cpu', FORCE_CPU='1', REVISION_THREADS='2', PYTORCH_ENABLE_MPS_FALLBACK='0')
import argparse
import collections
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import time

ap = argparse.ArgumentParser(description=__doc__)
for name in ['run','runtime','data-dir','output']:
    ap.add_argument('--'+name, required=True, type=Path)
args = ap.parse_args()
args.runtime = args.runtime.resolve()
args.output.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(args.runtime))
import numpy as np
import torch
from revision.data import Bank
from revision.models import make_model
from revision.illusions import AXES

torch.set_num_threads(2)
torch.set_num_interop_threads(1)
torch.use_deterministic_algorithms(True)
torch.set_grad_enabled(False)

protocol_path = args.output/'protocol.json'
protocol = json.loads(protocol_path.read_text())
started = datetime.now(timezone.utc).isoformat()
assert started > protocol['frozen_at_utc']
bank = Bank(args.data_dir, synthetic=False)
gray = bank.gray()
amp = .15
source_hashes = {}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def track(path):
    source_hashes[str(path)] = sha(path)


spectral_module = sys.modules.get('revision.spectral') or sys.modules.get('src.spectral')
if spectral_module is None:
    raise RuntimeError('The spectral implementation imported by revision.data was not found.')
for path in [__file__, protocol_path, args.data_dir/'prepared/manifest.json',
             args.runtime/'revision/models.py', args.runtime/'revision/data.py',
             args.runtime/'revision/illusions.py', Path(spectral_module.__file__)]:
    track(path)


def clean(obj):
    if isinstance(obj,dict): return {str(k):clean(v) for k,v in obj.items()}
    if isinstance(obj,(list,tuple)): return [clean(x) for x in obj]
    if isinstance(obj,np.ndarray): return clean(obj.tolist())
    if isinstance(obj,np.generic): return clean(obj.item())
    if isinstance(obj,float) and not np.isfinite(obj): return None
    return obj


def save(name,obj):
    (args.output/name).write_text(json.dumps(clean(obj), indent=2, allow_nan=False)+'\n')


def load_net(jobid):
    job=args.run/'jobs'/jobid
    cp=job/'classify.pt'
    checkpoint=torch.load(cp,map_location='cpu',weights_only=True)
    config=checkpoint['config']
    net=make_model(config,config['seed'])
    net.load_state_dict(checkpoint['state_dict'],strict=True)
    net.eval()
    assert all(x.device.type=='cpu' for x in net.parameters())
    track(cp)
    return net,config


def altered(net,config,p,d,padding='zeros'):
    cfg=dict(config,patch_size=p,dilation=d)
    new=make_model(cfg,cfg['seed'])
    new.load_state_dict(net.state_dict(),strict=True)
    new.conv1.padding_mode=padding
    return new.eval()


def probe_batch(p,axis):
    # [neutral, target+, target-, uniform+, uniform-, surround+, surround-]
    x=np.broadcast_to(gray[None,:,None,None],(7,3,p,p)).copy()
    c=slice(p//3,2*p//3)
    for sign,i in [(1,1),(-1,2)]: x[i,:,c,c]=(gray*(1+sign*amp*axis))[:,None,None]
    for sign,i in [(1,3),(-1,4)]: x[i]=(gray*(1+sign*amp*axis))[:,None,None]
    for sign,i in [(1,5),(-1,6)]:
        x[i]=(gray*(1+sign*amp*axis))[:,None,None]
        x[i,:,c,c]=gray[:,None,None]
    return torch.tensor(x,dtype=torch.float32)


def projected(delta,slope):
    # Float32 slope matches the production calibration; double dot for reporting.
    delta=np.asarray(delta,dtype=np.float64)
    slope=np.asarray(slope,dtype=np.float64)
    den=float(slope@slope)
    numerator=float(delta@slope)
    return dict(raw_signed_projection=numerator,
                normalized_shift=numerator/den if den>1e-14 else None,
                calibration_squared_norm=den, raw_delta=delta.tolist(),
                calibration_slope=slope.tolist())


def probe(net,axis):
    p=net.geometry.patch_size
    c=net.geometry.center
    x=probe_batch(p,axis)
    f=net.features(x).numpy()
    h=net.representation(x).numpy()
    logit=net(x).numpy()
    fslope=(f[3,:,p//2,p//2]-f[4,:,p//2,p//2])/(2*amp)
    hslope=(h[1]-h[2])/(2*amp)
    lslope=(logit[1]-logit[2])/(2*amp)
    delta=(f[5]-f[6])/2
    local=projected(delta[:,c,c].mean((1,2)),fslope)
    global_=projected((h[5]-h[6])/2,hslope)
    logits=projected((logit[5]-logit[6])/2,lslope)
    radius=net.dilation
    interior=slice(c.start+radius,c.stop-radius)
    inner=projected(delta[:,interior,interior].mean((1,2)),fslope) if interior.stop>interior.start else None
    return dict(local_target=local,global_representation=global_,output_logits=logits,local_interior=inner)


def compare_tensor(a,b):
    return dict(max_abs_error=float((a-b).abs().max()),
                allclose=bool(torch.allclose(a,b,atol=1e-6,rtol=1e-6)))


def identity(net,cfg,seed):
    other=altered(net,cfg,27,3)
    gen=torch.Generator().manual_seed(4400+seed)
    x=torch.rand((32,3,9,9),generator=gen)
    x=torch.cat([x,probe_batch(9,AXES['BY']),probe_batch(9,AXES['RG'])])
    up=lambda z:z.repeat_interleave(3,2).repeat_interleave(3,3)
    y=up(x)
    result=dict(seed=seed,feature=compare_tensor(up(net.features(x)),other.features(y)),
                representation=compare_tensor(net.representation(x),other.representation(y)),
                logits=compare_tensor(net(x),other(y)),axes={})
    for axis in ['BY','RG']:
        a,b=probe(net,AXES[axis]),probe(other,AXES[axis])
        row={}
        for scope in ['local_target','global_representation','output_logits']:
            av,bv=a[scope],b[scope]
            row[scope]=dict(raw_projection_error=abs(av['raw_signed_projection']-bv['raw_signed_projection']),
                normalized_error=abs(av['normalized_shift']-bv['normalized_shift']) if av['normalized_shift'] is not None and bv['normalized_shift'] is not None else None,
                defined_both=av['normalized_shift'] is not None and bv['normalized_shift'] is not None,
                undefined_both=av['normalized_shift'] is None and bv['normalized_shift'] is None,
                native=av,repeat_dilated=bv)
        result['axes'][axis]=row
    return result


def logits(net,X):
    return torch.cat([net(torch.as_tensor(X[i:i+128],dtype=torch.float32))
                      for i in range(0,len(X),128)]).numpy()


def padding_check(net,cfg,jobid):
    X,y,_,metadata=bank.trials('test',cfg['seed'],cfg.get('n_test',1000),cfg)
    base=logits(net,X)
    base_labels=base.argmax(1)
    base_acc=float(np.mean(base_labels==y))
    saved=json.loads((args.run/'jobs'/jobid/'classify.json').read_text())['performance']['test']['accuracy']
    rows=[]
    bprobe=probe(net,AXES['BY'])
    for mode in ['replicate','reflect']:
        alt=altered(net,cfg,cfg['patch_size'],cfg.get('dilation',1),mode)
        pred=logits(alt,X)
        acc=float(np.mean(pred.argmax(1)==y))
        rows.append(dict(job=jobid,seed=cfg['seed'],padding=mode,patch_size=cfg['patch_size'],
            dilation=cfg.get('dilation',1),readout=cfg.get('readout','base'),
            n_test=len(y),zero_accuracy=base_acc,accuracy=acc,accuracy_difference=acc-base_acc,
            prediction_change_fraction=float(np.mean(pred.argmax(1)!=base_labels)),
            mean_abs_logit_difference=float(np.mean(np.abs(pred-base))),
            max_abs_logit_difference=float(np.max(np.abs(pred-base))),
            zero_accuracy_matches_saved=base_acc==saved,
            probe_zero=bprobe,probe_altered=probe(alt,AXES['BY'])))
    return rows


identity_rows=[]
sweep=[]
padding=[]
start=time.monotonic()
for condition in ['p9_baseline','p27_fixed','p27_dilated']:
    for seed in range(30):
        jobid=f'E1_{condition}_s{seed:02d}'
        net,cfg=load_net(jobid)
        if condition=='p9_baseline':identity_rows.append(identity(net,cfg,seed))
        for p in [9,27]:
            for d in [1,3]:
                alt=altered(net,cfg,p,d)
                for axis in ['BY','RG']:
                    sweep.append(dict(source_condition=condition,seed=seed,patch_size=p,dilation=d,
                                      axis=axis,metrics=probe(alt,AXES[axis])))
        for row in padding_check(net,cfg,jobid):
            row['source_condition']=condition
            padding.append(row)
        if (seed+1)%10==0:print(condition,'completed',seed+1,'seeds;',round(time.monotonic()-start,1),'s',flush=True)
    save('identity_per_seed.json',identity_rows)
    save('frozen_sweep_per_seed.json',sweep)
    save('padding_per_seed.json',padding)

for seed in range(30):
    jobid=f'E2_intact_center_only_s{seed:02d}'
    net,cfg=load_net(jobid)
    for row in padding_check(net,cfg,jobid):
        row['source_condition']='E2_intact_center_only'
        padding.append(row)
    if (seed+1)%10==0:print('center_only negative control',seed+1,'seeds;',round(time.monotonic()-start,1),'s',flush=True)
save('padding_per_seed.json',padding)


def summarize(values):
    finite=[float(v) for v in values if v is not None and np.isfinite(v)]
    n=len(finite)
    out=dict(n_planned=len(values),n_valid=n,n_undefined=len(values)-n)
    if n:
        x=np.array(finite)
        # Same seed for bootstrap indices makes matched-seed contrasts reproducible;
        # descriptive intervals only, no hypothesis or equivalence tests.
        rng=np.random.default_rng(20261124)
        ci=np.percentile(x[rng.integers(0,n,(10000,n))].mean(1),[2.5,97.5])
        out.update(mean=float(x.mean()),median=float(np.median(x)),ci95=ci.tolist(),
                   min=float(x.min()),max=float(x.max()),
                   positive=int(np.sum(x>0)),negative=int(np.sum(x<0)),zero=int(np.sum(x==0)))
    return out


sweep_summary=[]
for key in sorted(set((r['source_condition'],r['patch_size'],r['dilation'],r['axis']) for r in sweep)):
    rows=[r for r in sweep if (r['source_condition'],r['patch_size'],r['dilation'],r['axis'])==key]
    metrics={}
    for scope in ['local_target','global_representation','output_logits','local_interior']:
        metrics[scope]={metric:summarize([r['metrics'][scope][metric] if r['metrics'][scope] else None for r in rows])
                        for metric in ['raw_signed_projection','normalized_shift','calibration_squared_norm']}
    sweep_summary.append(dict(source_condition=key[0],patch_size=key[1],dilation=key[2],axis=key[3],metrics=metrics))

contrasts=[]
for source in ['p9_baseline','p27_fixed','p27_dilated']:
    for axis in ['BY','RG']:
        for label,A,B in [('size27_minus9_fixed_d1',(27,1),(9,1)),
                          ('dilation3_minus1_at27',(27,3),(27,1)),
                          ('matched27d3_minus9d1',(27,3),(9,1))]:
            ra={r['seed']:r for r in sweep if r['source_condition']==source and r['axis']==axis and (r['patch_size'],r['dilation'])==A}
            rb={r['seed']:r for r in sweep if r['source_condition']==source and r['axis']==axis and (r['patch_size'],r['dilation'])==B}
            metrics={}
            for scope in ['local_target','global_representation','output_logits']:
                metrics[scope]={}
                for metric in ['normalized_shift','raw_signed_projection']:
                    vals=[]
                    for seed in range(30):
                        a,b=ra[seed]['metrics'][scope][metric],rb[seed]['metrics'][scope][metric]
                        vals.append(a-b if a is not None and b is not None else None)
                    metrics[scope][metric]=summarize(vals)
            contrasts.append(dict(source_condition=source,axis=axis,comparison=label,metrics=metrics))

pad_summary=[]
for key in sorted(set((r['source_condition'],r['padding']) for r in padding)):
    rows=[r for r in padding if (r['source_condition'],r['padding'])==key]
    metrics={m:summarize([r[m] for r in rows]) for m in ['zero_accuracy','accuracy','accuracy_difference',
             'prediction_change_fraction','mean_abs_logit_difference','max_abs_logit_difference']}
    for scope in ['local_target','global_representation','output_logits']:
        for metric in ['normalized_shift','raw_signed_projection']:
            vals=[]
            for r in rows:
                a,b=r['probe_altered'][scope][metric],r['probe_zero'][scope][metric]
                vals.append(a-b if a is not None and b is not None else None)
            metrics[f'BY_{scope}_{metric}_difference']=summarize(vals)
    pad_summary.append(dict(source_condition=key[0],padding=key[1],metrics=metrics,
                            all_zero_accuracy_matches_saved=all(r['zero_accuracy_matches_saved'] for r in rows)))

idsum={scope:dict(all_pass=all(r[scope]['allclose'] for r in identity_rows),
                  max_abs_error=max(r[scope]['max_abs_error'] for r in identity_rows))
       for scope in ['feature','representation','logits']}
idsum['axes']={}
for axis in ['BY','RG']:
    idsum['axes'][axis]={}
    for scope in ['local_target','global_representation','output_logits']:
        rows=[r['axes'][axis][scope] for r in identity_rows]
        idsum['axes'][axis][scope]=dict(n_defined=sum(r['defined_both'] for r in rows),
            n_undefined_both=sum(r['undefined_both'] for r in rows),
            n_definition_mismatch=sum(not(r['defined_both'] or r['undefined_both']) for r in rows),
            max_raw_projection_error=max(r['raw_projection_error'] for r in rows),
            max_normalized_error=max([r['normalized_error'] for r in rows if r['normalized_error'] is not None],default=None))

result=dict(protocol_sha256=sha(protocol_path),script_sha256=sha(__file__),started_utc=started,
            finished_utc=datetime.now(timezone.utc).isoformat(),elapsed_seconds=time.monotonic()-start,
            cpu_threads=torch.get_num_threads(),interop_threads=torch.get_num_interop_threads(),
            training=False,source_run=str(args.run),gray=gray.tolist(),source_hashes=source_hashes,
            n_identity_networks=len(identity_rows),n_source_networks=90,n_center_only_negative_controls=30,
            n_sweep_rows=len(sweep),n_padding_rows=len(padding),identity=idsum,
            frozen_sweep=sweep_summary,paired_frozen_contrasts=contrasts,padding=pad_summary,
            caveats=['Post-production exploratory diagnostics, distinct from frozen primary training endpoint.',
                     'Thirty seed blocks share one fixed scene partition; not 30 independent datasets.',
                     'Zero-shot padding changes are out-of-training-distribution, not controlled retraining evidence.',
                     'Calibrated response shifts are model functions, not human appearance estimates.',
                     'No separate scene partitions, new training, or calibrated human study performed.'])
save('summary.json',result)
print('DONE',round(result['elapsed_seconds'],2),'seconds; identity',idsum,flush=True)
