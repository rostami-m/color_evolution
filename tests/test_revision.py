import argparse
import json
from pathlib import Path
import subprocess
import sys
import numpy as np
import pytest
import torch
from revision.models import make_model
from revision.data import Bank
from revision.analysis import filter_metrics,CHROMATIC,TRANSFORM,bootstrap
from revision.illusions import evaluate_illusions
from revision.evolution import minimize
from revision.queue import read_manifest
from revision.resource_limits import ProcessGroup

torch.set_num_threads(1)


@pytest.mark.parametrize('scale',[3,9])
def test_repeated_input_dilated_model_outputs_and_gradients(scale):
    a=make_model(dict(patch_size=9),81)
    b=make_model(dict(patch_size=9*scale,dilation=scale),81)
    x=torch.rand(4,3,9,9)
    fine=x.repeat_interleave(scale,2).repeat_interleave(scale,3)
    ya,yb=a(x),b(fine)
    torch.testing.assert_close(ya,yb,rtol=1e-5,atol=1e-6)
    ya.square().sum().backward();yb.square().sum().backward()
    for pa,pb in zip(a.parameters(),b.parameters()):
        torch.testing.assert_close(pa.grad,pb.grad,rtol=1e-4,atol=1e-6)


def test_objective_initial_bodies_identical():
    a=make_model(dict(patch_size=27),15,'classify')
    b=make_model(dict(patch_size=27),15,'regress')
    for key in ('conv1.weight','conv1.bias','bottleneck.weight','bottleneck.bias'):
        torch.testing.assert_close(a.state_dict()[key],b.state_dict()[key],rtol=0,atol=0)


def test_data_scale_pairing(tmp_path):
    bank=Bank(tmp_path,True)
    a=bank.trials('train',5,40,dict(patch_size=9,noise='coarse'))
    b=bank.trials('train',5,40,dict(patch_size=27,noise='coarse'))
    np.testing.assert_allclose(b[0],a[0].repeat(3,2).repeat(3,3),rtol=0,atol=0)
    for index in (1,2):
        np.testing.assert_array_equal(a[index],b[index])
    np.testing.assert_array_equal(a[3]['surface_ids'],b[3]['surface_ids'])


def test_known_opponent_metrics_and_scale():
    spatial=np.array([[1,-1,0],[-1,1,0],[0,0,0]])
    opponent=CHROMATIC[0,:,None,None]*spatial
    achromatic=TRANSFORM[0,:,None,None]*spatial
    m=filter_metrics(np.stack([opponent,achromatic]))
    np.testing.assert_allclose(m['double_opponency_score'],[1,0],atol=1e-10)
    scaled=filter_metrics(np.stack([opponent,achromatic])*-4)
    np.testing.assert_allclose(m['double_opponency_score'],scaled['double_opponency_score'],atol=1e-10)
    assert bootstrap([1])['ci95'] is None


def test_distant_illusion_rois_have_no_local_effect():
    net=make_model(dict(patch_size=27,dilation=3),12)
    result=evaluate_illusions(net,np.array([.4,.4,.4]))
    for axis in result['axes'].values():
        for row in axis['cornsweet']:
            assert abs(row['distant_signed_difference'])<1e-5
        for row in axis['watercolor'].values():
            value=row['far_interior_shift']
            assert value is None or abs(value)<1e-5
    from revision.common import clean
    json.dumps(clean(result),allow_nan=False)


def test_identity_features_have_no_induction_but_global_pool_changes():
    from revision.models import Geometry
    class Identity(torch.nn.Module):
        geometry=Geometry(27,9)
        dilation=1
        def features(self,x):return x
        def representation(self,x):
            c=self.geometry.center
            return torch.cat((x[:,:,c,c].mean((2,3)),x.mean((2,3))),1)
    result=evaluate_illusions(Identity(),np.array([.4,.4,.4]))
    for record in result['axes'].values():
        for row in record['simultaneous']:
            assert abs(row['local_target_shift'])<1e-6
            assert abs(row['readout_shift'])>0
        for row in record['cornsweet']:
            assert abs(row['distant_signed_difference'])<1e-6
        for row in record['mach']:
            assert abs(row['low_join_signed_residual'])<1e-6
            assert abs(row['high_join_signed_residual'])<1e-6


def test_shuffle_preserves_target_histogram_and_boundary(tmp_path):
    bank=Bank(tmp_path,True)
    bank.synthetic=False
    rng=np.random.default_rng(23)
    scene=rng.uniform(.05,.95,(40,40,31)).astype(np.float32)
    bank.scenes={'test':[('fixture',scene)]}
    config=dict(patch_size=27,sensor_noise=0.,context='intact')
    a=bank.trials('test',42,4,config)
    b=bank.trials('test',42,4,dict(config,context='shuffle'))
    c=bank.trials('test',42,4,dict(config,context='boundary_shuffle'))
    np.testing.assert_array_equal(a[0][:,:,9:18,9:18],b[0][:,:,9:18,9:18])
    np.testing.assert_array_equal(a[0][:,:,8:19,8:19],c[0][:,:,8:19,8:19])
    mask=np.ones((27,27),bool);mask[9:18,9:18]=False
    for i in range(4):
        for ch in range(3):
            np.testing.assert_allclose(np.sort(a[0][i,ch][mask]),np.sort(b[0][i,ch][mask]),atol=1e-7)
    assert a[3]['crops']==b[3]['crops']==c[3]['crops']


def test_cma_improves_sphere():
    start=np.array([2.,-3.,4.])
    best,record=minimize(lambda x:float(x@x),start,3,iterations=90)
    assert best@best<.01*(start@start)
    assert record['fitness_evaluations']==1+90*record['population']


def test_manifest_rejects_unknown_dependency(tmp_path):
    path=tmp_path/'jobs.json'
    path.write_text(json.dumps([dict(id='a',command=[sys.executable],depends_on=['missing'])]))
    with pytest.raises(ValueError):
        read_manifest(path)


def test_pid_reuse_is_not_signaled(monkeypatch):
    import psutil,os,signal
    group=ProcessGroup(os.getpid(),psutil.Process().create_time()-100)
    def forbidden(*args):
        raise AssertionError('Attempted to signal unrelated/recycled process')
    monkeypatch.setattr(os,'killpg',forbidden)
    assert group.send(signal.SIGTERM) is False


def test_queue_resume_failures_and_cpu_environment(tmp_path):
    gate=tmp_path/'gate';events=tmp_path/'events';out=tmp_path/'queue'
    code=f"import os;from pathlib import Path;assert os.environ['CUDA_VISIBLE_DEVICES']=='';assert os.environ['OMP_NUM_THREADS']=='1';p=Path({str(events)!r});p.open('a').write('a')"
    jobs=[dict(id='a',command=[sys.executable,'-c',code]),
          dict(id='b',command=[sys.executable,'-c',f"from pathlib import Path;assert Path({str(gate)!r}).exists()"]),
          dict(id='c',command=[sys.executable,'-c',f"from pathlib import Path;Path({str(events)!r}).open('a').write('c')"],depends_on=['b']),
          dict(id='d',command=[sys.executable,'-c',f"from pathlib import Path;Path({str(events)!r}).open('a').write('d')"],depends_on=['b'],allow_failed_dependencies=True)]
    manifest=tmp_path/'manifest.json';manifest.write_text(json.dumps(jobs))
    command=[sys.executable,'-m','revision.queue','run','--manifest',str(manifest),'--output',str(out),'--threads','1']
    first=subprocess.run(command,timeout=30,capture_output=True,text=True)
    assert first.returncode==1,first.stderr
    assert events.read_text()=='ad'
    gate.touch()
    second=subprocess.run(command+['--retry-failed'],timeout=30,capture_output=True,text=True)
    assert second.returncode==0,second.stderr
    assert events.read_text()=='adcd'
    assert json.loads((out/'status.json').read_text())['jobs']['a']['attempts']==1
