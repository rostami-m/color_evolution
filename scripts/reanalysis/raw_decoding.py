"""Post hoc raw-cone decoding; no model training or production edits."""
import os
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS','BLIS_NUM_THREADS'):
    os.environ[key]='2'
os.environ['CUDA_VISIBLE_DEVICES']=''
os.environ['PYTORCH_ENABLE_MPS_FALLBACK']='0'
import gc
import hashlib
import json
from pathlib import Path
import sys
import time
PROJECT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(PROJECT))
import numpy as np
import torch
torch.set_num_threads(2)
torch.set_num_interop_threads(1)
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression,Ridge
from sklearn.metrics import r2_score
from revision.data import Bank
from revision.analysis import bootstrap
from revision.common import atomic_json
RUN=Path(os.environ['COLOR_RUN']).resolve()
DATA=Path(os.environ['COLOR_DATA']).resolve()
OUT=Path(os.environ['COLOR_ANALYSIS'])/'raw_decoding'
OUT.mkdir(parents=True,exist_ok=True)
GRID=(.01,.1,1.,10.,100.)
NOISE=(0.,.02,.05)

def features(X):
    p=X.shape[-1];t=p//3;a=(p-t)//2;b=a+t
    center=X[:,:,a:b,a:b].mean((2,3),dtype=np.float64)
    ring=(X.sum((2,3),dtype=np.float64)-center*t*t)/(p*p-t*t)
    return np.concatenate((center,ring),1)

def run(config,bank):
    start=time.monotonic(); seed=config['seed']
    datasets=[bank.trials(split,seed,n,config) for split,n in [('train',config['n_train']),('validation',config['n_validation']),('test',config['n_test'])]]
    oldmeta=json.loads((RUN/'jobs'/config['id']/'trial_metadata.json').read_text())
    for split,data in zip(('train','validation','test'),datasets):
        assert np.array_equal(oldmeta[split]['surface_ids'],data[3]['surface_ids'])
        assert np.array_equal(oldmeta[split]['surround_ids'],data[3]['surround_ids'])
    rows=[]
    for noise in NOISE:
        reps=[]
        for split,data in enumerate(datasets):
            X=data[0]
            rng=np.random.default_rng(seed+91000+split)
            noisy=X+rng.normal(0,noise,X.shape).astype(np.float32)
            reps.append(features(noisy));del noisy
        candidates=[]
        for strength in GRID:
            clf=make_pipeline(StandardScaler(),LogisticRegression(C=strength,max_iter=1000))
            reg=make_pipeline(StandardScaler(),Ridge(alpha=strength))
            clf.fit(reps[0],datasets[0][1]);reg.fit(reps[0],datasets[0][2])
            candidates.append((strength,clf,reg,clf.score(reps[1],datasets[1][1]),reg.score(reps[1],datasets[1][2])))
        bestc=max(candidates,key=lambda x:x[3]);bestr=max(candidates,key=lambda x:x[4])
        pred=bestr[2].predict(reps[2]);target=datasets[2][2]
        baseline=np.full_like(target,datasets[0][2].mean())
        rows.append(dict(additional_pixel_noise=noise,base_pixel_noise=config.get('sensor_noise',.01),classifier_C=bestc[0],ridge_alpha=bestr[0],
            validation_classification_accuracy=bestc[3],validation_illuminant_r2=bestr[4],
            train_classification_accuracy=bestc[1].score(reps[0],datasets[0][1]),
            test_classification_accuracy=bestc[1].score(reps[2],datasets[2][1]),
            test_illuminant_r2=bestr[2].score(reps[2],target),
            test_illuminant_rmse_kelvin=float(np.sqrt(np.mean((pred-target)**2))),
            constant_train_mean_test_rmse_kelvin=float(np.sqrt(np.mean((baseline-target)**2))),
            constant_train_mean_test_r2=float(r2_score(target,baseline)),
            majority_train_class_test_accuracy=float(np.mean(datasets[2][1]==np.argmax(np.bincount(datasets[0][1]))))))
        del reps,candidates
    record=dict(condition=config['condition'],seed=seed,id=config['id'],rows=rows,seconds=time.monotonic()-start,
        feature_type='Six raw cone features: mean center L,M,S plus mean ring L,M,S',
        status='Post hoc supplemental analysis; no network fitting or change to production results',
        config_sha256=hashlib.sha256((RUN/'configs'/f"{config['id']}.json").read_bytes()).hexdigest())
    atomic_json(OUT/f"{config['id']}.json",record)
    return record

if __name__=='__main__':
    started=time.monotonic();bank=Bank(DATA);records=[]
    for condition in ('p9_baseline','p27_fixed'):
        for seed in range(30):
            config=json.loads((RUN/'configs'/f'E1_{condition}_s{seed:02d}.json').read_text())
            path=OUT/f"{config['id']}.json"
            row=json.loads(path.read_text()) if path.exists() else run(config,bank)
            records.append(row);gc.collect()
            print(row['id'],round(row['seconds'],2),'seconds',flush=True)
    metrics=('test_classification_accuracy','test_illuminant_r2','test_illuminant_rmse_kelvin','constant_train_mean_test_rmse_kelvin','constant_train_mean_test_r2','majority_train_class_test_accuracy','validation_classification_accuracy','validation_illuminant_r2')
    groups=[];deltas=[]
    for condition in ('p9_baseline','p27_fixed'):
        selected=[r for r in records if r['condition']==condition]
        for i,noise in enumerate(NOISE):
            groups.append(dict(condition=condition,additional_pixel_noise=noise,metrics={m:bootstrap([r['rows'][i][m] for r in selected],unit='data seed under fixed scene partition') for m in metrics}))
            if i:
                deltas.append(dict(condition=condition,comparison=f'noise {noise} minus noise 0',metrics={m:bootstrap([r['rows'][i][m]-r['rows'][0][m] for r in selected],unit='paired data seed under fixed scene partition') for m in metrics[:3]}))
    report=dict(groups=groups,paired_noise_differences=deltas,n_seeds=30,total_seconds=time.monotonic()-started,total_decode_seconds=sum(r['seconds'] for r in records),
        note='Post hoc analysis of fixed E1 data; scaler fit on train; logistic C and ridge alpha independently selected on validation from .01,.1,1,10,100; test untouched. Baseline data include .01 pixel noise. Additional noise draws exactly match frozen decode() random streams. Per-seed uncertainty conditions on one fixed scene partition. Accuracy and R2 are on different scales and do not define an information-theoretic ordering.',
        historical_comparability='Historical run_why.py created six center/surround cone values with independent vector noise and random CV within same prototype pool. Here we use spatial means of actual held-out-scene E1 patches and corrected split-contained preprocessing; this is a controlled re-evaluation, not exact historical reproduction.',
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),source_data_manifest_sha256=hashlib.sha256((DATA/'prepared/manifest.json').read_bytes()).hexdigest())
    atomic_json(OUT/'summary.json',report)
    print(json.dumps(report,indent=2),flush=True)
