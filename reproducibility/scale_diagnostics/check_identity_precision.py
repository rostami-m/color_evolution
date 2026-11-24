"""Precision follow-up; preserves all original float32 tolerance failures."""
import argparse, hashlib, json, os, sys
from pathlib import Path
from datetime import datetime, timezone
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='2'
os.environ['CUDA_VISIBLE_DEVICES']=''
p=argparse.ArgumentParser()
for name in ['runtime','run','data-dir','output']:p.add_argument('--'+name,required=True,type=Path)
a=p.parse_args()
a.runtime=a.runtime.resolve()
a.output.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(a.runtime))
import numpy as np
import torch
from revision.models import make_model
from revision.data import Bank
from revision.illusions import AXES
torch.set_num_threads(2);torch.set_num_interop_threads(1);torch.set_grad_enabled(False)
torch.use_deterministic_algorithms(True)
protocol=a.output/'precision_protocol.json'
started=datetime.now(timezone.utc).isoformat()
assert started>json.loads(protocol.read_text())['frozen_at_utc']
gray=Bank(a.data_dir).gray()
def probes(axis):
    x=np.broadcast_to(gray[None,:,None,None],(7,3,9,9)).copy();c=slice(3,6)
    for sign,i in [(1,1),(-1,2)]:x[i,:,c,c]=(gray*(1+sign*.15*axis))[:,None,None]
    for sign,i in [(1,3),(-1,4)]:x[i]=(gray*(1+sign*.15*axis))[:,None,None]
    for sign,i in [(1,5),(-1,6)]:
        x[i]=(gray*(1+sign*.15*axis))[:,None,None];x[i,:,c,c]=gray[:,None,None]
    # Preserve identical float32 inputs to original run, then increase arithmetic precision.
    return torch.tensor(x,dtype=torch.float32).double()
rows=[]
for seed in range(30):
    cp=torch.load(a.run/'jobs'/f'E1_p9_baseline_s{seed:02d}'/'classify.pt',map_location='cpu',weights_only=True)
    c=cp['config'];net=make_model(c,seed);net.load_state_dict(cp['state_dict']);net=net.double().eval()
    alt=make_model(dict(c,patch_size=27,dilation=3),seed);alt.load_state_dict(cp['state_dict']);alt=alt.double().eval()
    gen=torch.Generator().manual_seed(4400+seed)
    x=torch.cat([torch.rand((32,3,9,9),generator=gen).double(),probes(AXES['BY']),probes(AXES['RG'])])
    up=lambda x:x.repeat_interleave(3,2).repeat_interleave(3,3)
    y=up(x)
    d={'seed':seed}
    for name,v,w in [('feature',up(net.features(x)),alt.features(y)),('representation',net.representation(x),alt.representation(y)),('logits',net(x),alt(y))]:
        d[name]={'max_abs_error':float((v-w).abs().max()),'allclose':bool(torch.allclose(v,w,atol=1e-12,rtol=1e-12))}
    rows.append(d)
out={'started_utc':started,'finished_utc':datetime.now(timezone.utc).isoformat(),'dtype':'float64','n':30,
     'protocol_sha256':hashlib.sha256(protocol.read_bytes()).hexdigest(),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
     'summary':{k:{'passed_count':sum(r[k]['allclose'] for r in rows),'max_abs_error':max(r[k]['max_abs_error'] for r in rows)} for k in ['feature','representation','logits']},
     'records':rows,'interpretation':'Float64 precision check supplements and does not replace the original prespecified float32 results.'}
(a.output/'identity_precision.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out['summary']))
