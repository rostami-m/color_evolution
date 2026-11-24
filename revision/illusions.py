"""Signed induction probes with physically equal ROIs and local controls.

The outputs are calibrated model-response contrasts, not human percepts.
Global pooled responses do not establish local filling-in.
"""
import numpy as np
import torch

AXES = {'RG': np.array([1., -1., 0.]), 'BY': np.array([-.5, -.5, 1.]), 'luminance': np.ones(3)}


@torch.no_grad()
def evaluate_illusions(net, gray):
    net.eval()
    g = net.geometry
    p, c, r = g.patch_size, g.center, net.dilation
    gray = np.asarray(gray, float)
    amp = .15
    def image(size, contrast=0., axis=None):
        color = gray if axis is None else gray*(1+contrast*axis)
        return np.broadcast_to(color[:,None,None], (3,size,size)).copy()
    def features(x):
        return net.features(torch.tensor(x[None], dtype=torch.float32))[0].numpy()
    def rep(x):
        return net.representation(torch.tensor(x[None], dtype=torch.float32))[0].numpy()
    def projected(delta, slope):
        denom = float(slope @ slope)
        return float(delta @ slope / denom) if denom > 1e-14 else None
    out = dict(geometry=vars(g), receptive_field_radius=r, contrast_amplitude=amp,
               units='equivalent input contrast projected on independent calibration slope',
               caveat='Local features and global readout are reported separately; no human appearance inference.', axes={})
    for name, axis in AXES.items():
        neutral = image(p)
        f0, h0 = features(neutral), rep(neutral)
        plus, minus = neutral.copy(), neutral.copy()
        plus[:,c,c] = (gray*(1+amp*axis))[:,None,None]
        minus[:,c,c] = (gray*(1-amp*axis))[:,None,None]
        hslope = (rep(plus)-rep(minus))/(2*amp)
        fslope = (features(image(p,amp,axis))[:,p//2,p//2]-features(image(p,-amp,axis))[:,p//2,p//2])/(2*amp)
        simultaneous, checker = [], []
        for sign in (-1,1):
            x = image(p,sign*amp,axis)
            x[:,c,c] = gray[:,None,None]
            delta = features(x)-f0
            interior = slice(c.start+r, c.stop-r)
            simultaneous.append(dict(surround_contrast=sign*amp,
                readout_shift=projected(rep(x)-h0, hslope),
                local_target_shift=projected(delta[:,c,c].mean((1,2)),fslope),
                local_interior_shift=projected(delta[:,interior,interior].mean((1,2)),fslope) if c.stop-c.start > 2*r else None))
        for cell in sorted(set([1,p//9])):
            pattern = ((np.indices((p,p))//cell).sum(0)%2)*2-1
            mask = g.ring()
            pattern = pattern.astype(float)
            pattern[mask] -= pattern[mask].mean()
            for sign in (-1,1):
                x = gray[:,None,None]*(1+sign*amp*axis[:,None,None]*pattern)
                x[:,c,c] = gray[:,None,None]
                checker.append(dict(cell_pixels=cell,phase=sign,readout_shift=projected(rep(x)-h0,hslope),
                    local_target_shift=projected((features(x)-f0)[:,c,c].mean((1,2)),fslope)))
        n = max(3*p, 8*r+15)
        if n%2 == 0:
            n += 1
        mid = n//2
        support = max(2,p//9)
        positions = np.arange(n)-mid+.5
        profile = -amp*np.sign(positions)*np.maximum(0,1-np.abs(positions)/(support+.5))
        validrows = slice(r+1,n-r-1)
        # Each column is compared to a uniform field with identical physical LMS.
        def profile_response(profile):
            x = gray[:,None,None]*(1+axis[:,None,None]*profile[None,None,:])
            x = np.broadcast_to(x, (3,n,n)).copy()
            observed = features(x)[:,validrows,:].mean(1,dtype=np.float64)
            uniforms = np.stack([image(2*r+3,float(v),axis) for v in profile])
            reference = net.features(torch.tensor(uniforms,dtype=torch.float32))[:,:,r+1,r+1].numpy().T
            residual = observed-reference
            return np.array([projected(residual[:,i],fslope) for i in range(n)],dtype=float)
        corn = []
        left = np.arange(r+1,mid-support-r-1)
        right = np.arange(mid+support+r+1,n-r-1)
        zero=profile==0
        nearleft=np.flatnonzero(zero & (positions<0) & (positions>=-support-r-1.5))
        nearright=np.flatnonzero(zero & (positions>0) & (positions<=support+r+1.5))
        if not len(left) or not len(right):
            raise ValueError('No uncontaminated Cornsweet ROI')
        for sign in (1,-1,0):
            residual = profile_response(sign*profile)
            if np.any(profile[np.r_[left,right]] != 0):
                raise AssertionError('Cornsweet measurement overlaps physical cusp')
            corn.append(dict(polarity=sign,profile=sign*profile,response=residual,
                left_roi=left,right_roi=right,distant_signed_difference=float(np.mean(residual[left])-np.mean(residual[right])),
                near_left_roi=nearleft,near_right_roi=nearright,
                near_signed_difference=float(np.mean(residual[nearleft])-np.mean(residual[nearright]))))
        lo,hi = n//3,2*n//3
        ramp = np.clip((np.arange(n)-lo)/(hi-lo),0,1)*2*amp-amp
        mach = []
        for label, physical in [('ramp',ramp),('reversed',-ramp),('linear',np.linspace(-amp,amp,n)),('flat',np.zeros(n))]:
            residual = profile_response(physical)
            mach.append(dict(control=label,profile=physical,response=residual,
                low_join_signed_residual=float(np.mean(residual[lo-r:lo+r+1])),
                high_join_signed_residual=float(np.mean(residual[hi-r:hi+r+1]))))
        inner = max(g.target_size,2*r+5)
        if inner%2 == 0:
            inner+=1
        a,b=(n-inner)//2,(n+inner)//2
        width=max(1,p//27)
        plain=image(n)
        plain_features=features(plain)
        maps={}
        for kind in ('closed','closed_reversed','open','removed'):
            x=plain.copy()
            if kind != 'removed':
                x[:,a-width:b+width,a-width:b+width]=(.7*gray)[:,None,None]
                polarity=-1 if kind=='closed_reversed' else 1
                x[:,a:b,a:b]=(gray*(1+polarity*amp*axis))[:,None,None]
                x[:,a+width:b-width,a+width:b-width]=gray[:,None,None]
                if kind=='open':
                    x[:,a-width:a+width,a-width:b+width]=gray[:,None,None]
            delta=features(x)-plain_features
            far=slice(a+width+r,b-width-r)
            if far.stop<=far.start:
                raise ValueError('Empty watercolor interior')
            assert np.allclose(x[:,far,far],gray[:,None,None])
            near=np.zeros((n,n),dtype=bool)
            near[a+width:b-width,a+width:b-width]=True
            near[far,far]=False
            assert np.allclose(x[:,near],gray[:,None])
            maps[kind]=dict(far_roi=[far.start,far.stop],
                far_interior_shift=projected(delta[:,far,far].mean((1,2)),fslope),
                near_contour_shift=projected(delta[:,near].mean(1),fslope))
        out['axes'][name]=dict(simultaneous=simultaneous,checkerboard=checker,
            cornsweet=corn,mach=mach,watercolor=maps,
            calibration_readout_norm=float(np.linalg.norm(hslope)),calibration_local_norm=float(np.linalg.norm(fslope)))
    return out
