"""
data.py — stimulus generation and data loading.

Two levels:
  - Synthetic stimuli (no downloads required): random smooth reflectances.
  - Foster hyperspectral reflectances: loaded from DATA_DIR/foster/*.mat if present;
    falls back to synthetic with a printed warning.

DATA_DIR is resolved (in priority order) from:
  1. DATA_DIR environment variable
  2. <repo-root>/data (default)
"""
import os
import glob
import numpy as np

from .spectral import (
    WAVELENGTHS, N_BANDS, CONES,
    planck_illuminant, reflectance_to_lms, lms_to_opponent, random_reflectance,
)

PATCH = 9
CENTER = slice(3, 6)

FOSTER_WL = np.arange(410, 711, 10)  # Foster scenes: 410–710 nm, 31 bands


def _data_dir():
    env = os.environ.get("DATA_DIR")
    if env:
        return env
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "..", "data")


def _results_dir():
    env = os.environ.get("RESULTS_DIR")
    if env:
        return env
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "..", "results")


def results_path(name):
    """Absolute path for a results file, creating the directory if needed."""
    d = _results_dir()
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, name)


def _load_mat(path):
    """Load a Foster .mat (v7 or v7.3 HDF5). Returns (H,W,31) array or None."""
    try:
        from scipy.io import loadmat
        m = loadmat(path)
        for k, v in m.items():
            if not k.startswith("__") and hasattr(v, "ndim") and v.ndim == 3 and v.shape[-1] == 31:
                return np.asarray(v, dtype=np.float64)
    except NotImplementedError:
        pass
    try:
        import h5py
        with h5py.File(path, "r") as f:
            for k in f.keys():
                v = np.array(f[k])
                if v.ndim == 3 and 31 in v.shape:
                    ax = list(v.shape).index(31)
                    return np.moveaxis(v, ax, -1).astype(np.float64)
    except Exception:
        pass
    return None


def _resample_foster(refl_31):
    """Map Foster 410–710 grid to our 400–700 grid by nearest wavelength."""
    idx = [int(np.argmin(np.abs(FOSTER_WL - wl))) for wl in WAVELENGTHS]
    return refl_31[..., idx]


def load_reflectance_bank(max_pixels=200_000, seed=0):
    """Return (R, is_real) where R is (N, 31) on our wavelength grid.

    Looks for Foster .mat files in DATA_DIR/foster/. Falls back to synthetic if
    none are found.
    """
    rng = np.random.default_rng(seed)
    foster_dir = os.path.join(_data_dir(), "foster")
    mats = sorted(glob.glob(os.path.join(foster_dir, "*.mat")))
    banks = []
    for p in mats:
        arr = _load_mat(p)
        if arr is None:
            continue
        arr = _resample_foster(arr)
        flat = arr.reshape(-1, 31)
        flat = flat[np.isfinite(flat).all(1)]
        flat = np.clip(flat, 0.001, 1.2)
        banks.append(flat)
    if banks:
        R = np.concatenate(banks, 0)
        if len(R) > max_pixels:
            R = R[rng.choice(len(R), max_pixels, replace=False)]
        return R, True
    print("[data] No Foster .mat files found - using synthetic reflectances. "
          "Run  python -m src.fetch_foster  to download real data.")
    R = np.stack([random_reflectance(rng) for _ in range(20_000)])
    return R, False


def chromatic_density(R, n_illum=5, seed=0):
    """Blue-yellow opponent coordinates under several daylight illuminants."""
    rng = np.random.default_rng(seed)
    by = []
    for _ in range(n_illum):
        illum = planck_illuminant(rng.uniform(4000, 25000))
        lms = (R * illum) @ CONES.T
        by.append(lms_to_opponent(lms)[:, 2])
    return np.concatenate(by)


def _by_of_bank(R, cct=6500):
    """Blue-yellow coord of each reflectance under a canonical neutral illuminant."""
    lms = (R * planck_illuminant(cct)) @ CONES.T
    return lms_to_opponent(lms)[:, 2]


def make_prototypes(R, by, rng, n_per_class=8):
    """Two illuminant-invariant material categories split on the blue-yellow axis."""
    order = np.argsort(by)
    cool = R[order[:len(order) // 4]]
    warm = R[order[-len(order) // 4:]]
    return {
        0: cool[rng.choice(len(cool), n_per_class, replace=False)],
        1: warm[rng.choice(len(warm), n_per_class, replace=False)],
    }


def _weighted_choice(protos, by_protos, rng, weighting, fitness_peak, fitness_sd):
    classes = list(protos.keys())
    if weighting == "uniform":
        c = rng.integers(0, 2)
        return c, rng.integers(0, len(protos[c]))
    flat = [(c, i, by_protos[c][i]) for c in classes for i in range(len(protos[c]))]
    coords = np.array([f[2] for f in flat])
    if weighting == "density":
        w = np.exp(-0.5 * (coords / 0.10) ** 2)
    elif weighting == "fitness":
        w = np.exp(-0.5 * ((coords - fitness_peak) / fitness_sd) ** 2) + 0.02
    else:
        w = np.ones(len(flat))
    w = w / w.sum()
    j = rng.choice(len(flat), p=w)
    return flat[j][0], flat[j][1]


def make_trials(R, by, rng, n, cct_range=(3000, 25000), n_per_class=8,
                weighting="uniform", fitness_peak=-0.20, fitness_sd=0.10,
                refl_noise=0.02):
    """Build n trials for the behaving task.

    Returns:
        X: (n, 3, PATCH, PATCH) float32 — cone-excitation patches
        y: (n,) int64 — category labels {0, 1}
        meta: dict — cct, center_by arrays and prototype arrays (never fed to the network)
    """
    protos = make_prototypes(R, by, rng, n_per_class)
    by_protos = {c: _by_of_bank(protos[c]) for c in protos}
    X = np.empty((n, 3, PATCH, PATCH), np.float32)
    y = np.empty(n, np.int64)
    cct_arr = np.empty(n)
    cby_arr = np.empty(n)
    for i in range(n):
        c, idx = _weighted_choice(protos, by_protos, rng, weighting, fitness_peak, fitness_sd)
        cr = np.clip(protos[c][idx] + rng.normal(0, refl_noise, N_BANDS), 0.01, 1.1)
        sc = rng.integers(0, 2)
        sr = np.clip(
            protos[sc][rng.integers(0, len(protos[sc]))] + rng.normal(0, refl_noise, N_BANDS),
            0.01, 1.1,
        )
        cc = rng.uniform(*cct_range)
        il = planck_illuminant(cc)
        cl = reflectance_to_lms(cr, il)
        sl = reflectance_to_lms(sr, il)
        patch = np.empty((3, PATCH, PATCH), np.float32)
        patch[:] = sl[:, None, None]
        patch[:, CENTER, CENTER] = cl[:, None, None]
        patch += rng.normal(0, 0.01, patch.shape).astype(np.float32)
        X[i] = patch
        y[i] = c
        cct_arr[i] = cc
        cby_arr[i] = lms_to_opponent(cl)[2]
    return X, y, dict(cct=cct_arr, center_by=cby_arr, protos=protos, by_protos=by_protos)


def get_bank(seed=0):
    """Convenience wrapper: load reflectance bank and compute blue-yellow coords."""
    R, is_real = load_reflectance_bank(seed=seed)
    by = _by_of_bank(R)
    return R, by, is_real
