"""
discrimination.py — shared discrimination-sensitivity helpers for §2.4 experiments.

Exports: sensitivity_profile, smoothed_peak, make_probe_patch, center_repr_net
These are imported by both run_fitness_sweep.py and run_ecological_fitness.py.
"""
import numpy as np
import torch

from src.data import N_BANDS
from src.spectral import planck_illuminant, reflectance_to_lms, lms_to_opponent
from src.model import PATCH, CENTER

PROBE_GRID = np.linspace(-0.45, 0.45, 19)
DELTA = 0.03


def center_repr_net(net, X, dev):
    """Mean feature activation at the central 3×3 target region."""
    with torch.no_grad():
        net.eval()
        Xt = torch.as_tensor(X, device=dev)
        h = net.features(Xt)
        c = net.center if hasattr(net, "center") else CENTER
        return h[:, :, c, c].mean(dim=(2, 3)).cpu().numpy()


def make_probe_patch(by_target, R, by, rng, n=64, cct=(3000, 25_000)):
    """Build patches whose center surface has approximately by_target blue-yellow coord."""
    idx = np.argsort(np.abs(by - by_target))[:200]
    X = np.empty((n, 3, PATCH, PATCH), np.float32)
    ach = np.empty(n)
    for i in range(n):
        cr = R[idx[rng.integers(0, len(idx))]]
        sr = R[rng.integers(0, len(R))]
        il = planck_illuminant(rng.uniform(*cct))
        cl = reflectance_to_lms(cr, il)
        sl = reflectance_to_lms(sr, il)
        p = np.empty((3, PATCH, PATCH), np.float32)
        p[:] = sl[:, None, None]; p[:, CENTER, CENTER] = cl[:, None, None]
        X[i] = p; ach[i] = lms_to_opponent(cl)[2]
    return X, ach


def sensitivity_profile(net, R, by, dev, rng):
    """Model JND along the blue-yellow axis: ||Δrepr|| per unit Δchroma."""
    sens = np.full(len(PROBE_GRID), np.nan)
    for j, s in enumerate(PROBE_GRID):
        Xa, aa = make_probe_patch(s - DELTA / 2, R, by, rng)
        Xb, ab = make_probe_patch(s + DELTA / 2, R, by, rng)
        ra = center_repr_net(net, Xa, dev).mean(0)
        rb = center_repr_net(net, Xb, dev).mean(0)
        dchroma = abs(np.mean(ab) - np.mean(aa)) + 1e-6
        sens[j] = np.linalg.norm(rb - ra) / dchroma
    return sens


def smoothed_peak(sens):
    """Sensitivity-weighted centroid of the top half of the sensitivity profile."""
    s = np.array(sens, float)
    s = s - np.nanmin(s)
    thr = np.nanpercentile(s, 50)
    w = np.where(s >= thr, s, 0.0)
    if w.sum() <= 0:
        return float(PROBE_GRID[np.nanargmax(s)])
    return float((w * PROBE_GRID).sum() / w.sum())
