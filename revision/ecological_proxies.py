"""Analytic proxy spectra, not measured fruit, foliage or skin reflectances.

These functions preserve the exact production E4_proxy stimuli. The names label
illustrative curve shapes and do not establish ecological validity.
"""
import numpy as np
from .spectral import WAVELENGTHS, planck_illuminant, reflectance_to_lms, lms_to_opponent


def ecological_reflectances():
    x = np.linspace(0, 1, len(WAVELENGTHS))
    fruit = 0.10 + 0.80 * x
    foliage = 0.10 + 0.65 * np.exp(-0.5 * (np.linspace(-1, 1, len(WAVELENGTHS)) / 0.35) ** 2)
    skin = 0.25 + 0.45 * x ** 1.5
    return dict(fruit=fruit, foliage=foliage, skin=skin)


def by_coord(refl, ccts=(5500, 6500, 10_000)):
    return float(np.mean([lms_to_opponent(reflectance_to_lms(refl, planck_illuminant(c)))[2]
                          for c in ccts]))
