"""Release-critical checks: data/backend routing, science scope and immutable inputs."""
import importlib.util
import json
from pathlib import Path
import sys
import pytest
from revision.build_queue import build


def test_production_manifest_portable_and_complete(tmp_path):
    project = Path(__file__).resolve().parents[1]
    output, data = tmp_path/'run', tmp_path/'data with spaces'
    jobs = build(project, output, data_dir=data, backend='cpu')
    assert len(jobs) == 2443
    configs = [json.loads(p.read_text()) for p in (output/'configs').glob('*.json')]
    assert len(configs) == 2431
    assert all(c['training_device'] == 'cpu' for c in configs)
    assert all(j['command'][0] == sys.executable for j in jobs)
    assert all(str(data) in j['command'] for j in jobs if 'revision.experiments' in j['command'])
    assert {c['patch_size'] for c in configs} == {9,27}
    with pytest.raises(FileExistsError):
        build(project, output, data_dir=data)


def test_mps_routes_explicitly_and_smoke_is_labelled(tmp_path):
    project = Path(__file__).resolve().parents[1]
    build(project, tmp_path/'run', seeds=1, smoke=True, backend='mps')
    configs = [json.loads(p.read_text()) for p in (tmp_path/'run/configs').glob('*.json')]
    assert all(c['training_device'] == ('cpu' if c.get('kind') == 'grounding' else 'mps') and c['epochs'] == 1 for c in configs)
    assert json.loads((tmp_path/'run/design.json').read_text())['smoke'] is True


def test_published_bundle_checksums():
    project = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location('reproduce', project/'scripts/reproduce.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    module.verify(project/'published_results')
