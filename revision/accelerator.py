"""Explicit float32 MPS training; CPU initialization, sampling and analysis."""
import os
from datetime import datetime, timezone
import numpy as np
import torch


def configure_mps():
    if not torch.backends.mps.is_available():raise RuntimeError('MPS unavailable; CPU fallback forbidden')
    cap=int(os.environ.get('REVISION_MPS_MEMORY_GIB','4'))*1024**3
    torch.mps.set_per_process_memory_fraction(min(1.,cap/torch.mps.recommended_max_memory()))
    return cap


def synchronize(device):
    if str(device)=='mps':torch.mps.synchronize()


def progress(**values):
    path=os.environ.get('REVISION_PROGRESS_PATH')
    if path:
        from .common import atomic_json
        atomic_json(path,dict(time=datetime.now(timezone.utc).isoformat(),
            job_id=os.environ.get('REVISION_JOB_ID'),mode=os.environ.get('REVISION_MODEL_MODE'),
            training_device='mps',driver_allocated_bytes=torch.mps.driver_allocated_memory(),
            tensor_allocated_bytes=torch.mps.current_allocated_memory(),**values))


def train_mps(net,X,y,cct,seed,epochs=80,lr=.002,batch_size=128,
              loss_weights=None,sampling_weights=None):
    configure_mps()
    torch.manual_seed(int(seed))
    generator=torch.Generator(device='cpu').manual_seed(int(seed))
    target_cpu=(torch.as_tensor((cct-14000.)/7000.,dtype=torch.float32)[:,None]
                if net.objective=='regress' else torch.as_tensor(y,dtype=torch.long))
    sample=None if sampling_weights is None else torch.as_tensor(sampling_weights,dtype=torch.float32)
    orders=[torch.randperm(len(X),generator=generator) if sample is None else
            torch.multinomial(sample,len(X),replacement=True,generator=generator) for _ in range(epochs)]
    counts=[None if net.objective=='regress' else torch.bincount(target_cpu[o],minlength=2).tolist() for o in orders]
    orders=torch.stack(orders).to('mps');X=torch.as_tensor(X,dtype=torch.float32).to('mps');target=target_cpu.to('mps')
    weights=None
    if loss_weights is not None:
        weights=torch.as_tensor(loss_weights,dtype=torch.float32);weights=(weights/weights.mean()).to('mps')
    net.to('mps');net.train()
    opt=torch.optim.Adam(net.parameters(),lr=lr,foreach=True)
    curve=[]
    max_driver=0
    for epoch in range(epochs):
        total=torch.zeros((),device='mps');correct=torch.zeros((),device='mps',dtype=torch.int64)
        for ix in orders[epoch].split(batch_size):
            opt.zero_grad(set_to_none=True)
            pred=net(X[ix]);losses=((pred-target[ix]).square().mean(1) if net.objective=='regress' else
                                   torch.nn.functional.cross_entropy(pred,target[ix],reduction='none'))
            loss=losses.mean() if weights is None else (losses*weights[ix]).mean()
            loss.backward();opt.step();total.add_(loss.detach()*len(ix))
            if net.objective!='regress':correct.add_((pred.argmax(1)==target[ix]).sum())
        value=float(total.cpu())/len(X)
        if not np.isfinite(value):raise FloatingPointError('Non-finite MPS training loss')
        curve.append({'epoch':epoch+1,'loss':value,'sampled_class_counts':counts[epoch],
                      'sampled_train_accuracy':None if net.objective=='regress' else int(correct.cpu())/len(X)})
        max_driver=max(max_driver,torch.mps.driver_allocated_memory())
        if epoch==0 or (epoch+1)%5==0 or epoch+1==epochs:
            progress(phase='training',epoch=epoch+1,epochs=epochs,loss=value)
        if max_driver>int(os.environ.get('REVISION_MPS_MEMORY_GIB','4'))*1024**3:
            raise MemoryError('MPS driver memory exceeds configured ceiling')
    synchronize('mps');net.to('cpu');net._mps_peak_driver_bytes=max_driver
    if not all(bool(torch.isfinite(p).all()) for p in net.parameters()):raise FloatingPointError('Non-finite trained parameter')
    progress(phase='training_complete',epoch=epochs,epochs=epochs)
    return curve
