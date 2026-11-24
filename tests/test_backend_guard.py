import json
import pytest
from revision.aggregate import aggregate
from revision.common import atomic_json

def test_mixed_training_backends_rejected_and_matching_allowed(tmp_path):
 for seed,device in enumerate(('cpu','mps')):
  ident=f'fixture_s{seed}';config=dict(id=ident,stage='E4',condition='fixture',seed=seed,models=['classify'])
  atomic_json(tmp_path/'configs'/f'{ident}.json',config)
  atomic_json(tmp_path/'jobs'/ident/'classify.json',dict(seed=seed,mode='classify',training_device=device,
    validation_gate=True,metrics=dict(normalized_chromatic_power=.1,double_opponency_score=.2,double_opponent_fraction=.25),
    performance=dict(test=dict(accuracy=.6,balanced_accuracy=.6))))
 with pytest.raises(ValueError,match='mixed-backend'):aggregate(tmp_path,'E4')
 path=tmp_path/'jobs/fixture_s0/classify.json';row=json.loads(path.read_text());row['training_device']='mps';atomic_json(path,row)
 aggregate(tmp_path,'E4')
 assert json.loads((tmp_path/'analysis/E4.json').read_text())['training_backends']==['mps']
