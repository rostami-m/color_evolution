"""
illusion_stimuli.py — shared stimulus helpers for §2.3 illusion experiments.

All illusion experiments import from here rather than duplicating the same
cone-contrast and patch-building code across files.
"""
import numpy as np
import torch

from src.spectral import planck_illuminant, CONES
from src.model import PATCH, CENTER

INDUCE = 0.30  # chromatic-contrast magnitude of the inducer surround

INDUCERS = {
    "red":    (+1.0, -1.0,  0.0),
    "green":  (-1.0, +1.0,  0.0),
    "blue":   ( 0.0,  0.0, +1.0),
    "yellow": ( 0.0,  0.0, -1.0),
}


def adapting_gray(R, rng, n=3000):
    """Mean LMS of a random sample from the reflectance bank under daylight 6500 K."""
    lms = (R[rng.choice(len(R), n, replace=False)] * planck_illuminant(6500)) @ CONES.T
    return lms.mean(0)


def cone_contrast(gray, vec, c):
    """Shift gray by a cone-contrast step of magnitude c in direction vec."""
    v = np.array(vec, float); v = v / (np.linalg.norm(v) + 1e-9)
    return np.clip(gray * (1.0 + c * v), 1e-3, None)


def build_patch(center_lms, surround_lms, config, fine_lms=None):
    """Build a 3×PATCH×PATCH cone-excitation patch.

    config='uniform' : uniform chromatic surround
    config='fine'    : fine checkerboard surround (same mean chroma, high SF)
    """
    p = np.empty((3, PATCH, PATCH), np.float32)
    if config == "uniform":
        p[:] = surround_lms[:, None, None]
    else:
        cb = np.indices((PATCH, PATCH)).sum(0) % 2
        for ch in range(3):
            p[ch] = np.where(cb == 0, surround_lms[ch], fine_lms[ch])
    p[:, CENTER, CENTER] = center_lms[:, None, None]
    return p


@torch.no_grad()
def center_repr(net, X, dev):
    """Mean feature-map activation at the central 3×3 target region."""
    net.eval()
    Xt = torch.as_tensor(X, device=dev)
    h = net.features(Xt)
    c = net.center if hasattr(net, "center") else CENTER
    return h[:, :, c, c].mean(dim=(2, 3)).cpu().numpy()


def induced_shift(net, gray, vec, config, R, dev, rng, n=64):
    """Signed projection of the induced center shift onto the inducer direction.

    Returns > 0 for assimilation (toward inducer), < 0 for contrast (away).
    """
    sur = cone_contrast(gray, vec, INDUCE)
    mirror = cone_contrast(gray, tuple(-x for x in vec), INDUCE)
    neutral_sur = gray
    Xn = np.asarray([build_patch(gray, neutral_sur, "uniform") for _ in range(n)], np.float32)
    Xi = np.asarray([build_patch(gray, sur, config, fine_lms=mirror) for _ in range(n)], np.float32)
    rn = center_repr(net, Xn, dev).mean(0)
    ri = center_repr(net, Xi, dev).mean(0)
    Xd = np.asarray([build_patch(sur, gray, "uniform") for _ in range(n)], np.float32)
    rd = center_repr(net, Xd, dev).mean(0) - rn
    rd_n = rd / (np.linalg.norm(rd) + 1e-9)
    return float(np.dot(ri - rn, rd_n))
