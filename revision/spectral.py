"""
spectral.py — physics-based spectral stimulus pipeline.

Pipeline: reflectance(λ) × illuminant(λ) → radiance(λ)
          radiance · cone_sensitivity → LMS excitations
          LMS → opponent coordinates (luminance, L-M, S-(L+M))

Everything is reproducible from a seed; no external colour-science dependency.
"""
import numpy as np

# Wavelength grid: 400–700 nm in 10 nm steps (31 model bands; measured Foster bands are 410–710 nm).
WAVELENGTHS = np.arange(400, 701, 10, dtype=np.float64)
N_BANDS = len(WAVELENGTHS)


def planck_illuminant(cct_kelvin, wavelengths=WAVELENGTHS):
    """Relative spectral power distribution of a blackbody at temperature cct_kelvin."""
    h = 6.62607015e-34
    c = 2.99792458e8
    kB = 1.380649e-23
    lam = wavelengths * 1e-9
    expo = (h * c) / (lam * kB * cct_kelvin)
    spd = (1.0 / (lam ** 5)) * (1.0 / (np.exp(expo) - 1.0))
    return spd / spd.max()


def sample_illuminant(rng, cct_range=(4000.0, 25000.0)):
    """Draw a random Planck illuminant. Returns (spd, cct)."""
    cct = rng.uniform(*cct_range)
    return planck_illuminant(cct), cct


def _gaussian(x, mu, sigma):
    return np.exp(-0.5 * ((x - mu) / sigma) ** 2)


def cone_sensitivities(wavelengths=WAVELENGTHS):
    """Returns (3, N_BANDS) array; rows are L, M, S cone sensitivities."""
    L = _gaussian(wavelengths, 565.0, 45.0)
    M = _gaussian(wavelengths, 540.0, 45.0)
    S = _gaussian(wavelengths, 445.0, 35.0)
    C = np.stack([L, M, S], axis=0)
    return C / C.sum(axis=1, keepdims=True)


CONES = cone_sensitivities()  # (3, 31)


def random_reflectance(rng, n_basis=5):
    """One smooth reflectance spectrum in [0, 1] via low-frequency cosine bases."""
    x = np.linspace(0, np.pi, N_BANDS)
    coeffs = rng.normal(0, 1, size=n_basis)
    basis = np.stack([np.cos(k * x) for k in range(n_basis)], axis=0)
    raw = coeffs @ basis
    r = 1.0 / (1.0 + np.exp(-raw))
    return 0.05 + 0.90 * r


def reflectance_to_lms(reflectance, illuminant, cones=CONES):
    """Cone excitations (3,) for a surface under an illuminant."""
    return cones @ (reflectance * illuminant)


def lms_to_opponent(lms):
    """LMS → (luminance, L-M, S-(L+M)) opponent coordinates.
    Accepts arrays of any leading shape (..., 3)."""
    L, M, S = lms[..., 0], lms[..., 1], lms[..., 2]
    lum = L + M
    rg = L - M
    by = S - 0.5 * (L + M)
    return np.stack([lum, rg, by], axis=-1)
