"""Resumable experiment: explicit training backend, CPU analysis and initialization."""
import argparse
import gc
import json
import os
from pathlib import Path
import platform
import time
import numpy as np
import torch
from .common import atomic_json, digest
from .data import Bank, sha256
from .models import make_model, train, evaluate
from .analysis import network_summary, filter_metrics, spectral_grounding, CHROMATIC
from .illusions import evaluate_illusions
from .evolution import train_cma
from .spectral import CONES, planck_illuminant
from .legacy_metrics import filter_scores


@torch.no_grad()
def representations(net,X):
    return torch.cat([net.representation(torch.as_tensor(X[i:i+128],dtype=torch.float32))
                      for i in range(0,len(X),128)]).numpy()


def sensitivity(net,gray,seed):
    rng=np.random.default_rng(seed+81000)
    p,c=net.geometry.patch_size,net.geometry.center
    grid=np.linspace(-.25,.25,31)
    nuisance=rng.normal(0,.01,(16,3,p,p)).astype(np.float32)
    rows=[]
    for location in grid:
        x=np.broadcast_to(gray[None,:,None,None],(16,3,p,p)).copy()+nuisance
        axis=np.array([-.5,-.5,1.])
        x[:,:,c,c]+=(gray*axis*location)[None,:,None,None]
        baseline=representations(net,x)
        perturbed=x.copy()
        step=(gray*axis*.01).astype(np.float32)
        perturbed[:,:,c,c]+=step[None,:,None,None]
        delta=representations(net,perturbed)-baseline
        raw=np.sqrt(np.mean(delta**2))/np.linalg.norm(step)
        rms=np.sqrt(np.mean(baseline**2))
        rows.append(dict(target_contrast=location,sensitivity=float(raw),
            normalized_sensitivity=float(raw/rms) if rms>0 else None,
            actual_lms_step=float(np.linalg.norm(step))))
    return dict(rows=rows,interpretation='Matched-nuisance finite-difference representation sensitivity; not JND or psychophysical threshold')


def decode(net,train_data,val_data,test_data,seed):
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import LogisticRegression,Ridge
    rows=[]
    for noise in (0.,.02,.05):
        reps=[]
        for split,data in enumerate((train_data,val_data,test_data)):
            X,y,t,_=data
            rng=np.random.default_rng(seed+91000+split)
            noisy=X+rng.normal(0,noise,X.shape).astype(np.float32)
            reps.append(representations(net,noisy))
        candidates=[]
        for strength in (.01,.1,1.,10.,100.):
            clf=make_pipeline(StandardScaler(),LogisticRegression(C=strength,max_iter=1000))
            reg=make_pipeline(StandardScaler(),Ridge(alpha=strength))
            clf.fit(reps[0],train_data[1]);reg.fit(reps[0],train_data[2])
            candidates.append((strength,clf,reg,clf.score(reps[1],val_data[1]),reg.score(reps[1],val_data[2])))
        bestc=max(candidates,key=lambda x:x[3]);bestr=max(candidates,key=lambda x:x[4])
        pred=bestr[2].predict(reps[2])
        rows.append(dict(sensor_noise=noise,classifier_C=bestc[0],ridge_alpha=bestr[0],
            test_classification_accuracy=bestc[1].score(reps[2],test_data[1]),
            test_illuminant_r2=bestr[2].score(reps[2],test_data[2]),
            test_illuminant_rmse=float(np.sqrt(np.mean((pred-test_data[2])**2))),
            constant_train_mean_test_rmse=float(np.sqrt(np.mean((train_data[2].mean()-test_data[2])**2))),
            majority_train_class_test_accuracy=float(np.mean(test_data[1]==np.argmax(np.bincount(train_data[1]))))))
    return dict(rows=rows,preprocessing='Fit on training partition only; hyperparameters selected on validation; final test untouched',
                interpretation='Separate decoding tasks; no information-theoretic ordering from unlike scores')


def null_calibration(config,root):
    key=f"k{config.get('k1',8)}-b{config.get('bottleneck',4)}"
    path=root/'nulls'/f'{key}.json'
    if path.exists():
        return json.loads(path.read_text())
    networks=[];legacy=[]
    for seed in range(200):
        n=make_model(config,900000+seed)
        w=n.conv1.weight.detach().numpy()
        networks.append(filter_metrics(w)['double_opponency_score'])
        legacy.append(filter_scores(w)[1])
    scores=np.stack(networks)
    rng=np.random.default_rng(900000)
    boot=[np.quantile(scores[rng.integers(0,len(scores),len(scores))],.95) for _ in range(500)]
    result=dict(threshold=float(np.quantile(scores,.95)),legacy_threshold=float(np.quantile(legacy,.95)),
        threshold_ci95=np.quantile(boot,[.025,.975]),n_networks=200,
        initialization_seed_range=[900000,900199],scores=scores,
        metric='normalized chromatic power × chromatic-axis coherence × spatial sign balance; descriptive weight metric')
    atomic_json(path,result)
    return result


def run(config,output,data_dir):
    torch.set_num_threads(int(os.environ.get('REVISION_THREADS','2')))
    if torch.get_num_interop_threads()!=1:torch.set_num_interop_threads(1)
    torch.use_deterministic_algorithms(True)
    training_device=config.get('training_device','cpu')
    if training_device not in ('cpu','mps'):raise ValueError('Unsupported training backend')
    if training_device=='mps':
        from .accelerator import configure_mps
        configure_mps()
    root=Path(output);root.mkdir(parents=True,exist_ok=True)
    if (root/'source_hashes.json').exists():
        expected=json.loads((root/'source_hashes.json').read_text())
        changed=[name for name,value in expected.items() if not Path(name).exists() or sha256(name)!=value]
        if changed:
            raise RuntimeError(f'Frozen production source changed: {changed}. Use a new run directory.')
    job=root/'jobs'/config['id'];job.mkdir(parents=True,exist_ok=True)
    config_hash=digest(config)
    completed=job/'done.json'
    if completed.exists():
        if json.loads(completed.read_text())['config_sha256']!=config_hash:
            raise ValueError('Refusing to reuse results from changed configuration')
        print('Already complete',config['id']);return
    started=time.monotonic()
    atomic_json(job/'config.json',config)
    bank=Bank(data_dir,config.get('synthetic',False))
    provenance=dict(config_sha256=config_hash,data=bank.manifest,
        source_sha256={str(p):sha256(p) for p in sorted(Path('revision').glob('*.py'))},
        device=training_device,training_device=training_device,analysis_device='cpu',precision='float32',
        optimizer_foreach=training_device=='mps',mps_fallback=False,torch_threads=torch.get_num_threads(),python=platform.python_version(),
        torch=torch.__version__,numpy=np.__version__,platform=platform.platform())
    atomic_json(job/'provenance.json',provenance)
    if config.get('kind')=='grounding':
        result=spectral_grounding(bank,CONES,planck_illuminant(6500))
        atomic_json(job/'grounding.json',result)
        atomic_json(completed,dict(config_sha256=config_hash,seconds=time.monotonic()-started))
        return
    seed=config['seed']
    datasets=[bank.trials(split,seed,n,config) for split,n in
        [('train',config.get('n_train',4000)),('validation',config.get('n_validation',800)),('test',config.get('n_test',1000))]]
    X,y,cct,metadata=datasets[0]
    atomic_json(job/'trial_metadata.json',{split: data[3] for split,data in zip(('train','validation','test'),datasets)})
    null=null_calibration(config,root)
    results=[]
    modes=config.get('models',['untrained','classify','regress','shuffled'])
    for mode in modes:
        os.environ['REVISION_JOB_ID']=config['id'];os.environ['REVISION_MODEL_MODE']=mode
        resultpath=job/f'{mode}.json'
        weightpath=job/f'{mode}.pt'
        if resultpath.exists() and weightpath.exists():
            existing=json.loads(resultpath.read_text())
            if digest(existing['config'])!=config_hash:
                raise ValueError('Checkpoint configuration mismatch')
            results.append(existing);continue
        objective='regress' if mode=='regress' else 'classify'
        net=make_model(config,seed,objective)
        initial={k:v.clone() for k,v in net.state_dict().items()}
        learned_y=y.copy()
        if mode=='shuffled':
            learned_y=np.random.default_rng(seed+71111).permutation(learned_y)
        weighting=config.get('weighting','uniform')
        weights=None
        if weighting!='uniform':
            coordinates=metadata['center_by']
            locus=config.get('utility_locus',0.)
            weights=.02+np.exp(-.5*((coordinates-locus)/.10)**2)
        training_started=time.monotonic()
        if mode=='untrained':
            curve=[]
        elif mode=='cma':
            curve=train_cma(net,X,learned_y,seed,config.get('cma_iterations',300),device=training_device)
        else:
            trainer=train
            if training_device=='mps':
                from .accelerator import train_mps
                trainer=train_mps
            curve=trainer(net,X,learned_y,cct,seed,epochs=config.get('epochs',80),
                batch_size=config.get('batch_size',128),
                loss_weights=weights if weighting in ('loss','both') else None,
                sampling_weights=weights if weighting in ('frequency','both') else None)
        training_seconds=time.monotonic()-training_started
        report=network_summary(net.conv1.weight.detach().numpy(),null['threshold'])
        oldchroma,oldscore=filter_scores(net.conv1.weight)
        report['legacy']=dict(chromatic_power=oldchroma,double_opponency_score=oldscore,
            double_opponent_fraction=float((oldscore>null['legacy_threshold']).mean()),threshold=null['legacy_threshold'])
        evaluation={split:evaluate(net,*data[:3]) for split,data in zip(('train','validation','test'),datasets)}
        extra=bank.trials('test',seed,config.get('n_test',1000),config,cct_mode='extrapolate')
        evaluation['illuminant_extrapolation']=evaluate(net,*extra[:3]);del extra
        result=dict(mode=mode,seed=seed,config=config,metrics=report,performance=evaluation,
            training_seconds=training_seconds,training_device='cpu_initialization' if mode=='untrained' else training_device,
            analysis_device='cpu',precision='float32',mps_peak_driver_bytes=getattr(net,'_mps_peak_driver_bytes',None),
            learning_curve=curve,parameters=sum(p.numel() for p in net.parameters()),
            validation_gate=(evaluation['validation'].get('accuracy',0)>=.8) if objective=='classify' else None,
            gate_note='All seeds primary; accuracy gate is a separately reported classifier sensitivity subset')
        if weights is not None:
            normalized=weights/weights.sum()
            result['weighting']=dict(mode=weighting,utility_locus=config.get('utility_locus',0.),
                effective_sample_size=float(1/np.sum(normalized**2)),
                uniform_class_frequencies=np.bincount(y,minlength=2)/len(y),
                weighted_class_frequencies=[float(normalized[y==c].sum()) for c in (0,1)],
                interpretation='Frequency and loss weighting can implement the same expected risk; both applies squared weighting in expectation')
        if config.get('probes',False):
            result['illusions']=evaluate_illusions(net,bank.gray())
            result['sensitivity']=sensitivity(net,bank.gray(),seed)
        if config.get('decode',False):
            result['decodability']=decode(net,*datasets,seed)
        if config.get('context','uniform')!='uniform' and mode=='classify':
            tests={}
            for context in ('intact','shuffle','boundary_shuffle'):
                data=bank.trials('test',seed,config.get('n_test',1000),dict(config,context=context))
                tests[context]=evaluate(net,*data[:3])
            result['context_cross_evaluation']=tests
        if hasattr(net,'b'):
            result['learned_or_fixed_b']=float(net.b.detach())
        if hasattr(net,'spatial'):
            w=net.spatial.detach().numpy()[0,0]
            side=w.shape[0];a=side//3;b=2*side//3
            mask=np.ones_like(w,dtype=bool);mask[a:b,a:b]=False
            result['spatial_weights']=dict(map=w,center_mean=float(w[~mask].mean()),surround_mean=float(w[mask].mean()),
                note='Relative magnitudes do not establish antagonism; inspect signs and functional probes')
        # Axes from weight sensitivities are converted before comparing to log-LMS PCA.
        axes=report['per_filter']['preferred_axis_lms']
        converted=(axes*bank.gray()) @ CHROMATIC.T
        result['cardinal_axes_log_lms_degrees']=np.rad2deg(np.arctan2(converted[:,1],converted[:,0]))%180
        result['cardinal_axes_reference_lms']=bank.gray()
        result['input_preprocessing']='Raw cone excitations in model units; no channel standardization. Reference uses mean training spectra under standard cones and 6500 K.'
        tmp=job/f'{mode}.pt.tmp'
        torch.save(dict(state_dict=net.state_dict(),initial_state_dict=initial,config=config,mode=mode),tmp)
        tmp.replace(weightpath)
        atomic_json(resultpath,result)
        results.append(result)
        print(config['id'],mode,'test',evaluation['test'],flush=True)
        del net;gc.collect()
        if training_device=='mps':torch.mps.empty_cache()
    atomic_json(completed,dict(config_sha256=config_hash,seconds=time.monotonic()-started,
        models=modes,status='complete',inference='Results require scientific interpretation; no manuscript claims automatically accepted'))


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--config',required=True);p.add_argument('--output',required=True);p.add_argument('--data-dir',required=True)
    a=p.parse_args()
    run(json.loads(Path(a.config).read_text()),a.output,a.data_dir)
