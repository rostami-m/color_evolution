"""Deterministic, scene-separated spectral inputs; no silent synthetic fallback."""
from pathlib import Path
import hashlib
import json
import numpy as np
from .spectral import CONES, WAVELENGTHS, planck_illuminant, random_reflectance
from .models import Geometry


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


class Bank:
    def __init__(self, data_dir, synthetic=False):
        self.data_dir = Path(data_dir)
        self.synthetic = synthetic
        self.scenes = {}
        if synthetic:
            rng = np.random.default_rng(20261119)
            R = np.stack([random_reflectance(rng) for _ in range(24000)])
            self.banks = {'train': R[:16000], 'validation': R[16000:20000], 'test': R[20000:]}
            self.manifest = {'source': 'SYNTHETIC_CONTROL', 'seed': 20261119,
                             'partitions': 'disjoint generated spectra; no natural-scene claims'}
        else:
            manifest_path = self.data_dir/'prepared'/'manifest.json'
            if not manifest_path.exists():
                raise FileNotFoundError('Natural data are required: run revision.prepare_data first.')
            self.manifest = json.loads(manifest_path.read_text())
            self.banks = {split: np.load(self.data_dir/'prepared'/f'{split}_bank.npy')
                          for split in ('train', 'validation', 'test')}
            for split, names in self.manifest['splits'].items():
                self.scenes[split] = [(name, np.load(self.data_dir/'prepared'/f'{name}.npy', mmap_mode='r'))
                                      for name in names]
        self.thresholds = np.quantile(self.by(self.banks['train']), [.25, .75])

    @staticmethod
    def by(R):
        x = (R*planck_illuminant(6500.)) @ CONES.T
        return x[:, 2]-.5*(x[:, 0]+x[:, 1])

    def trials(self, split, seed, n, config, cct_mode='iid'):
        R = self.banks[split]
        coords = self.by(R)
        pools = [np.flatnonzero(coords <= self.thresholds[0]), np.flatnonzero(coords >= self.thresholds[1])]
        if min(map(len, pools)) < 8:
            raise ValueError('Insufficient held-out spectra in predefined training categories.')
        # Separate streams prevent larger noise arrays from changing subsequent trial metadata.
        split_id = {'train': 0, 'validation': 1, 'test': 2}[split]
        streams = np.random.SeedSequence([20261119, int(seed), split_id]).spawn(5)
        surface_rng, light_rng, noise_rng, context_rng, refl_rng = map(np.random.default_rng, streams)
        protos = [surface_rng.choice(p, 8, replace=False) for p in pools]
        y = np.arange(n, dtype=np.int64) % 2
        surface_rng.shuffle(y)
        selected = np.array([protos[c][surface_rng.integers(8)] for c in y])
        surround_ids = np.array([protos[surface_rng.integers(2)][surface_rng.integers(8)] for _ in range(n)])
        rn = config.get('reflectance_noise', .02)
        bounds = config.get('reflectance_clip', [.01, 1.1])
        center = np.clip(R[selected] + refl_rng.normal(0, rn, (n, 31)), *bounds)
        surround = np.clip(R[surround_ids] + refl_rng.normal(0, rn, (n, 31)), *bounds)
        if config.get('surround_mode') == 'neutral':
            surround[:] = .5
        elif config.get('surround_mode') == 'highchroma':
            surround = np.clip(surround*1.5, *bounds)
        low, high = config.get('cct_range', [3000., 25000.])
        cct = light_rng.uniform(low, high, n)
        if cct_mode == 'extrapolate':
            cct = np.where(light_rng.random(n) < .5,
                           light_rng.uniform(2500, 3000, n), light_rng.uniform(25000, 30000, n))
        illuminants = np.stack([planck_illuminant(t) for t in cct])
        cones = CONES.copy()
        if config.get('cone_shift', 0) or config.get('cone_width', 1) != 1:
            means = np.array([565., 540., 445.])+config.get('cone_shift', 0)
            widths = np.array([45., 45., 35.])*config.get('cone_width', 1)
            cones = np.exp(-.5*((WAVELENGTHS[None, :]-means[:, None])/widths[:, None])**2)
            cones /= cones.sum(1, keepdims=True)
        cl = (center*illuminants) @ cones.T
        sl = (surround*illuminants) @ cones.T
        geo = Geometry(config['patch_size'], config['patch_size']//3)
        p, c = geo.patch_size, geo.center
        X = np.empty((n, 3, p, p), np.float32)
        context = config.get('context', 'uniform')
        crop_records = []
        for i in range(n):
            if context == 'uniform':
                X[i] = sl[i, :, None, None]
            else:
                if self.synthetic:
                    raise ValueError('Natural-texture experiment requires measured scenes.')
                scenes = self.scenes[split]
                scene_name, scene = scenes[context_rng.integers(len(scenes))]
                row = context_rng.integers(scene.shape[0]-p+1)
                col = context_rng.integers(scene.shape[1]-p+1)
                crop_records.append([scene_name,int(row),int(col),p])
                crop = np.array(scene[row:row+p, col:col+p], dtype=np.float32)
                # Permutation is independent of crop selection, so each arm receives the same crops.
                shuffle_rng = np.random.default_rng(np.random.SeedSequence([seed, split_id, i, 9182]))
                if context in ('shuffle', 'boundary_shuffle'):
                    mask = geo.ring()
                    if context == 'boundary_shuffle':
                        width = int(config.get('dilation', 1))
                        a, b = max(0, c.start-width), min(p, c.stop+width)
                        mask[a:b, a:b] = False
                    vectors = crop[mask].copy()
                    crop[mask] = vectors[shuffle_rng.permutation(len(vectors))]
                X[i] = np.einsum('hwl,cl->chw', crop*illuminants[i], cones, optimize=True)
            X[i, :, c, c] = cl[i, :, None, None]
        sigma = config.get('sensor_noise', .01)
        if config.get('noise', 'iid') == 'coarse':
            if p % 9:
                raise ValueError('Repeated-noise control requires an integer multiple of 9.')
            coarse = noise_rng.normal(0, sigma, (n, 3, 9, 9)).astype(np.float32)
            scale = p//9
            X += coarse.repeat(scale, 2).repeat(scale, 3)
        else:
            X += noise_rng.normal(0, sigma, X.shape).astype(np.float32)
        return X, y, cct, {'center_by': coords[selected], 'surface_ids': selected,
                           'surround_ids': surround_ids, 'split': split,
                           'scene_ids': self.manifest.get('splits', {}).get(split, []),
                           'crops': crop_records,
                           'cct_mode': cct_mode}

    def gray(self):
        return np.mean((self.banks['train']*planck_illuminant(6500)) @ CONES.T, axis=0)
