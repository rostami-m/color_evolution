import copy
import numpy as np
import pytest
import torch
from revision.models import make_model,train
from revision.accelerator import train_mps,configure_mps

pytestmark=pytest.mark.skipif(not torch.backends.mps.is_available(),reason='MPS hardware required')

@pytest.mark.parametrize('config',[
 dict(patch_size=9),dict(patch_size=27),dict(patch_size=27,dilation=3),
 dict(patch_size=27,readout='fixed_b',b=.5),dict(patch_size=27,readout='learned_b'),
 dict(patch_size=27,readout='spatial'),dict(patch_size=27,readout='spatial_coarse'),
 dict(patch_size=27,k1=32,bottleneck=8)])
def test_cpu_mps_forward_gradient_and_adam_step(config):
 configure_mps();torch.use_deterministic_algorithms(True)
 cpu=make_model(config,121);gpu=copy.deepcopy(cpu).to('mps')
 p=config['patch_size'];x=torch.rand(8,3,p,p);y=torch.arange(8)%2
 torch.testing.assert_close(cpu(x),gpu(x.to('mps')).cpu(),rtol=2e-5,atol=2e-6)
 oc=torch.optim.Adam(cpu.parameters(),lr=.002);og=torch.optim.Adam(gpu.parameters(),lr=.002,foreach=True)
 lc=torch.nn.functional.cross_entropy(cpu(x),y);lg=torch.nn.functional.cross_entropy(gpu(x.to('mps')),y.to('mps'))
 lc.backward();lg.backward()
 for a,b in zip(cpu.parameters(),gpu.parameters()):torch.testing.assert_close(a.grad,b.grad.cpu(),rtol=2e-4,atol=2e-6)
 oc.step();og.step()
 for a,b in zip(cpu.parameters(),gpu.parameters()):torch.testing.assert_close(a,b.cpu(),rtol=2e-4,atol=3e-5)

@pytest.mark.parametrize('objective',['classify','regress'])
def test_training_sampling_and_initialization_preserved(objective):
 from revision.data import Bank
 config=dict(patch_size=9);bank=Bank('/unused',True);X,y,t,_=bank.trials('train',4,128,config)
 a=make_model(config,4,objective);b=make_model(config,4,objective)
 w=np.linspace(.02,1.,len(y)).astype(np.float32)
 ca=train(a,X,y,t,4,epochs=2,batch_size=32,loss_weights=w,sampling_weights=w)
 cb=train_mps(b,X,y,t,4,epochs=2,batch_size=32,loss_weights=w,sampling_weights=w)
 assert [r['sampled_class_counts'] for r in ca]==[r['sampled_class_counts'] for r in cb]
 np.testing.assert_allclose([r['loss'] for r in ca],[r['loss'] for r in cb],rtol=1e-4,atol=1e-5)
 assert all(p.device.type=='cpu' for p in b.parameters())
 for p,q in zip(a.parameters(),b.parameters()):torch.testing.assert_close(p,q,rtol=1e-3,atol=1e-4)

def test_mps_repeated_input_dilated_equivalence():
 a=make_model(dict(patch_size=9),81).to('mps');b=make_model(dict(patch_size=27,dilation=3),81).to('mps')
 x=torch.rand(4,3,9,9).to('mps');fine=x.repeat_interleave(3,2).repeat_interleave(3,3)
 ya,yb=a(x),b(fine);torch.testing.assert_close(ya.cpu(),yb.cpu(),rtol=2e-5,atol=2e-6)
 ya.square().sum().backward();yb.square().sum().backward()
 for pa,pb in zip(a.parameters(),b.parameters()):torch.testing.assert_close(pa.grad.cpu(),pb.grad.cpu(),rtol=2e-4,atol=2e-6)
