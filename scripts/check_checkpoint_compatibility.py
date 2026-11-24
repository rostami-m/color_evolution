"""CPU checkpoint comparison worker; read-only on checkpoints and source trees."""
import os
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:
 os.environ[key]='2'
import argparse,sys,json,hashlib,gc
from pathlib import Path
parser=argparse.ArgumentParser();parser.add_argument('--runtime',type=Path,required=True);parser.add_argument('--run',type=Path,required=True);parser.add_argument('--data',type=Path,required=True);parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
sys.path.insert(0,str(args.runtime))
import numpy as np
import torch
from revision.data import Bank
from revision.models import make_model,evaluate
from revision.analysis import network_summary
from revision.illusions import evaluate_illusions
from revision.common import clean
try:from revision.legacy_metrics import filter_scores
except ModuleNotFoundError:from src.metrics import filter_scores
torch.set_num_threads(2);torch.set_num_interop_threads(1);torch.use_deterministic_algorithms(True)
bank=Bank(args.data,False);selected=[]
for condition in ['p9_baseline','p27_fixed','p27_dilated']:
 for seed in [0,29]:
  for mode in ['classify','regress']:selected.append((f'E1_{condition}_s{seed:02d}',mode))
for size in [9,27]:selected.append((f'E5c_p{size}_optimizer_s00','cma'))
for size in [9,27]:
 for readout in ['learned_b','spatial_coarse']:selected.append((f'E3_p{size}_{readout}_0_s01','classify'))
results=[]
for jobid,mode in selected:
 job=args.run/'jobs'/jobid;row=json.loads((job/f'{mode}.json').read_text());c=row['config']
 checkpoint=torch.load(job/f'{mode}.pt',map_location='cpu',weights_only=True)
 net=make_model(c,c['seed'],'regress' if mode=='regress' else 'classify');net.load_state_dict(checkpoint['state_dict'],strict=True);net.eval()
 test=bank.trials('test',c['seed'],c.get('n_test',1000),c)
 with torch.no_grad():pred=torch.cat([net(torch.as_tensor(test[0][i:i+128],dtype=torch.float32)) for i in range(0,len(test[0]),128)]).numpy()
 null=json.loads((args.run/'nulls'/f"k{c.get('k1',8)}-b{c.get('bottleneck',4)}.json").read_text())
 metrics=network_summary(net.conv1.weight.detach().numpy(),null['threshold']);chroma,score=filter_scores(net.conv1.weight)
 metrics['legacy']=dict(chromatic_power=chroma,double_opponency_score=score,double_opponent_fraction=float((score>null['legacy_threshold']).mean()),threshold=null['legacy_threshold'])
 record=dict(job=jobid,mode=mode,test_hashes=[hashlib.sha256(v.tobytes()).hexdigest() for v in test[:3]],test_metadata=clean(test[3]),prediction_sha256=hashlib.sha256(pred.tobytes()).hexdigest(),metrics=clean(metrics),performance=evaluate(net,*test[:3]),probes=clean(evaluate_illusions(net,bank.gray())))
 results.append(record);print(jobid,mode,flush=True);del net,test,checkpoint;gc.collect()
args.out.write_text(json.dumps(results,indent=2,allow_nan=False)+'\n')
