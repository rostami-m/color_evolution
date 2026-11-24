"""Fixed-budget separable CMA-ES minimizing the same cross entropy as Adam."""
import numpy as np
import torch


def minimize(fitness, initial, seed, iterations=300, sigma=.3, progress_callback=None):
    rng=np.random.default_rng(seed)
    mean=np.array(initial,dtype=float)
    d=len(mean)
    lam=4+int(3*np.log(d)); mu=lam//2
    w=np.log(mu+.5)-np.log(np.arange(1,mu+1)); w/=w.sum()
    eff=1/np.sum(w*w)
    cs=(eff+2)/(d+eff+5); cc=(4+eff/d)/(d+4+2*eff/d)
    c1=2/((d+1.3)**2+eff)
    cmu=min(1-c1,2*(eff-2+1/eff)/((d+2)**2+eff))
    damps=1+2*max(0,np.sqrt((eff-1)/(d+1))-1)+cs
    chi=np.sqrt(d)*(1-1/(4*d)+1/(21*d*d))
    ps=np.zeros(d); pc=np.zeros(d); C=np.ones(d)
    best=mean.copy(); bestloss=float(fitness(mean)); curve=[]
    for it in range(iterations):
        steps=rng.normal(size=(lam,d))*np.sqrt(C)
        pop=mean+sigma*steps
        losses=np.array([fitness(v) for v in pop])
        if not np.isfinite(losses).all():
            raise FloatingPointError('Nonfinite evolutionary loss')
        ix=np.argsort(losses)
        if losses[ix[0]]<bestloss:
            bestloss=float(losses[ix[0]]); best=pop[ix[0]].copy()
        selected=steps[ix[:mu]]
        ym=(w[:,None]*selected).sum(0)
        mean+=sigma*ym
        ps=(1-cs)*ps+np.sqrt(cs*(2-cs)*eff)*ym/np.sqrt(C)
        h=np.linalg.norm(ps)/np.sqrt(1-(1-cs)**(2*(it+1)))/chi < 1.4+2/(d+1)
        pc=(1-cc)*pc+h*np.sqrt(cc*(2-cc)*eff)*ym
        C=(1-c1-cmu)*C+c1*(pc*pc+(not h)*cc*(2-cc)*C)+cmu*(w[:,None]*selected**2).sum(0)
        C=np.clip(C,1e-10,1e6)
        sigma=min(1e3,sigma*np.exp(cs/damps*(np.linalg.norm(ps)/chi-1)))
        curve.append(dict(iteration=it+1,best_cross_entropy=bestloss,sigma=float(sigma)))
        if progress_callback and (it==0 or (it+1)%10==0 or it+1==iterations):progress_callback(it+1,bestloss)
    return best,dict(curve=curve,fitness_evaluations=1+lam*iterations,population=lam)


def train_cma(net,X,y,seed,iterations=300,device='cpu'):
    from torch.nn.utils import parameters_to_vector, vector_to_parameters
    X=torch.tensor(X,dtype=torch.float32,device=device); y=torch.tensor(y,dtype=torch.long,device=device)
    initial=parameters_to_vector(net.parameters()).detach().numpy()
    net.to(device)
    @torch.no_grad()
    def fitness(v):
        vector_to_parameters(torch.tensor(v,dtype=torch.float32,device=device),net.parameters())
        total=torch.zeros((),dtype=torch.float32,device=device) if device=='mps' else 0.
        for start in range(0,len(X),128):
            loss=torch.nn.functional.cross_entropy(net(X[start:start+128]),y[start:start+128],reduction='sum')
            total+=loss if device=='mps' else float(loss)
        return float(total.cpu())/len(X) if device=='mps' else total/len(X)
    callback=None
    if device=='mps':
        from .accelerator import progress
        callback=lambda iteration,loss:progress(phase='cma_training',iteration=iteration,iterations=iterations,loss=loss)
    best,result=minimize(fitness,initial,seed,iterations,progress_callback=callback)
    vector_to_parameters(torch.tensor(best,dtype=torch.float32,device=device),net.parameters())
    if device=='mps':
        torch.mps.synchronize();net._mps_peak_driver_bytes=torch.mps.driver_allocated_memory()
        net.to('cpu')
    result['covariance_device']='cpu_float64';result['fitness_device']=device
    return result
