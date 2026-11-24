"""Download the original Foster scenes; validate before enabling natural jobs."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import zipfile
import shutil
from urllib.parse import urljoin
import numpy as np
from scipy.io import loadmat
from .common import atomic_json
from .data import sha256

PAGE = 'https://personalpages.manchester.ac.uk/staff/david.foster/Hyperspectral_images_of_natural_scenes_02.html'
MIRROR = 'https://sites.google.com/view/sergionascimento/home/scientific-data/hyperspectral-images-of-natural-scenes-2002'
LINK_IDS = ['2f1l57d8xor3kcx','k8htlamps6zscb5','kj6bjly4cxf8464','jjq2srkhrz9b6uz',
            'iuwi89l4pnbnue5','dxnj6lgdoi9iugz','bdixyqgme3px0tt','xrerga98z563xvm']
LINKS = {i+1:f'https://www.dropbox.com/s/{key}/scene{i+1}.zip?dl=1' for i,key in enumerate(LINK_IDS)}


def download(url, path):
    partial = Path(str(path)+'.partial')
    subprocess.run(['curl','-L','--fail','--silent','--show-error','--connect-timeout','15',
        '--max-time','900','--retry','2','--retry-delay','5','--limit-rate','10M',
        url,'-o',str(partial)], check=True)
    partial.replace(path)


def prepare(data_dir):
    root = Path(data_dir)
    raw, prepared = root/'foster', root/'prepared'
    raw.mkdir(parents=True,exist_ok=True)
    prepared.mkdir(parents=True,exist_ok=True)
    if (prepared/'manifest.json').exists():
        manifest=json.loads((prepared/'manifest.json').read_text())
        valid=manifest.get('schema_version')==2 and all((prepared/f"{record['scene']}.npy").exists() and
                  sha256(prepared/f"{record['scene']}.npy")==record['prepared_sha256']
                  for record in manifest['scenes'])
        if valid and all((prepared/f'{split}_bank.npy').exists() for split in ('train','validation','test')):
            print('Prepared scene checksums verified',flush=True)
            return manifest
    records, splits = [], dict(train=[],validation=[],test=[])
    banks = {k: [] for k in splits}
    page = root/'foster_source.html'
    links = LINKS.copy()
    missing = [i for i in range(1,9) if not (raw/f'scene{i}.mat').exists() and not (raw/f'scene{i}.zip').exists()]
    if missing and not links:
        if not page.exists():
            download(PAGE,page)
        for link in re.findall(r'href\s*=\s*["\']([^"\']+)["\']',page.read_text(),re.I):
            if '.zip' in link.lower():
                match = re.search(r'scene\s*[_-]?(\d)',link,re.I)
                if match:
                    links[int(match.group(1))] = urljoin(PAGE,link)
        if not all(i in links for i in missing):
            raise RuntimeError('Could not identify all eight official ZIP links. Supply original scene1.mat through scene8.mat in data/foster; no synthetic fallback is permitted.')
    for i in range(1,9):
        name = f'scene{i}'
        mat, archive = raw/f'{name}.mat', raw/f'{name}.zip'
        if not mat.exists():
            if not archive.exists():
                print('Downloading',name,flush=True)
                download(links[i],archive)
            with zipfile.ZipFile(archive) as z:
                candidates = [v for v in z.infolist() if v.filename.lower().endswith('.mat')]
                if len(candidates) != 1 or candidates[0].file_size > 2*1024**3:
                    raise ValueError('Unexpected scene archive')
                with z.open(candidates[0]) as source, mat.open('wb') as dest:
                    shutil.copyfileobj(source,dest,1024*1024)
        contents = loadmat(mat)
        cubes = [(k,v) for k,v in contents.items() if isinstance(v,np.ndarray) and v.ndim==3 and v.shape[-1]==31]
        if len(cubes)!=1:
            raise ValueError(f'{name}: expected one HxWx31 effective-reflectance cube')
        key,cube=cubes[0]
        if min(cube.shape[:2])<81 or not np.isfinite(cube).all():
            raise ValueError(f'{name}: invalid dimensions or values')
        # Historical 410..710 -> 400..700 convention: nearest endpoint at 400.
        grid=np.r_[0,np.arange(30)]
        valid=np.any(cube>0,axis=2)
        rows,columns=np.where(valid)
        bounds=[int(rows.min()),int(rows.max()+1),int(columns.min()),int(columns.max()+1)]
        cropped=cube[bounds[0]:bounds[1],bounds[2]:bounds[3]]
        if not np.all(np.any(cropped>0,axis=2)):
            raise ValueError(f'{name}: internal missing-data region requires an explicit mask')
        arr=np.clip(cropped[:,:,grid],.001,1.2).astype(np.float32)
        np.save(prepared/f'{name}.npy',arr)
        split='train' if i in (1,2,4,5) else 'validation' if i in (3,6) else 'test'
        splits[split].append(name)
        rng=np.random.default_rng(20261119+i)
        flat=arr.reshape(-1,31)
        banks[split].append(flat[rng.choice(len(flat),10000,replace=False)])
        records.append(dict(scene=name,mat_key=key,shape=cube.shape,crop_bounds=bounds,prepared_shape=arr.shape,raw_sha256=sha256(mat),
            prepared_sha256=sha256(prepared/f'{name}.npy'),download_url=links.get(i),
            fraction_above_one=float(np.mean(cube>1)),fraction_below_zero=float(np.mean(cube<0))))
        print('Validated',name,split,flush=True)
        del contents,cubes,cube,cropped,arr,flat
    for split,parts in banks.items():
        np.save(prepared/f'{split}_bank.npy',np.concatenate(parts))
    manifest=dict(schema_version=2,source='Foster 2002 effective-reflectance scenes; Nascimento coauthor-hosted files (zero border padding removed)',source_page=PAGE,download_listing=MIRROR,
        split_rationale='Frozen before natural-network training: train 1/2/4/5, validation 3/6, test 7/8; distinct scenes and sufficient category support. An initial scene-6-only validation partition lacked one category.',
        citation='Nascimento, Ferreira & Foster (2002), JOSA A 19, 1484–1490',
        original_wavelength_nm=list(range(410,711,10)),model_wavelength_nm=list(range(400,701,10)),
        resampling='400 nm uses 410 nm endpoint; 410–700 nm use measured bands',
        bank_clip=[.001,1.2],trial_clip=[.01,1.1],
        reflectance_note='Effective reflectance can legitimately exceed one because of surface orientation; historical clipping retained and recorded.',
        splits=splits,scenes=records)
    atomic_json(prepared/'manifest.json',manifest)
    return manifest


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--data-dir',required=True)
    a=p.parse_args()
    prepare(a.data_dir)
