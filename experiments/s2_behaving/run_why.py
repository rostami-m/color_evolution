"""
§2.2 — Why does behaving beat world-recovery? Decodability and noise-robustness analysis.

No network training — pure decoding from raw cone-excitation features.
Shows the category is linearly decodable (acc 0.83) while the illuminant is not (R²=0.37),
and that the gap widens under sensor noise.

Writes:
    why_summary.json
"""
import os
import sys
import numpy as np
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.model_selection import cross_val_score

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.data import get_bank, N_BANDS
from src.spectral import planck_illuminant, reflectance_to_lms, lms_to_opponent, CONES
from src.data import make_prototypes, _by_of_bank
from src.io_utils import save_json


def _build(R, by, rng, n, sensor_noise=0.01, cct=(3000, 25_000)):
    protos = make_prototypes(R, by, rng)
    feats = np.empty((n, 6))
    ylab = np.empty(n, int)
    ccts = np.empty(n)
    for i in range(n):
        lab = int(rng.integers(0, 2))
        cr = np.clip(protos[lab][rng.integers(0, 8)] + rng.normal(0, 0.02, N_BANDS), 0.01, 1.1)
        sr = np.clip(protos[rng.integers(0, 2)][rng.integers(0, 8)] + rng.normal(0, 0.02, N_BANDS), 0.01, 1.1)
        c = rng.uniform(*cct)
        il = planck_illuminant(c)
        cl = CONES @ (cr * il) + rng.normal(0, sensor_noise, 3)
        sl = CONES @ (sr * il) + rng.normal(0, sensor_noise, 3)
        feats[i] = np.concatenate([cl, sl])
        ylab[i] = lab
        ccts[i] = c
    return feats, ylab, ccts


def main():
    R, by, is_real = get_bank()
    rng = np.random.default_rng(95_000)
    results = dict(source="FOSTER" if is_real else "SYN")

    f, y, c = _build(R, by, rng, 6000)
    cat = float(cross_val_score(LogisticRegression(max_iter=500), f, y, cv=5, scoring="accuracy").mean())
    ill = float(cross_val_score(Ridge(alpha=1.0), f, (c - c.mean()) / c.std(), cv=5, scoring="r2").mean())
    results["category_decode_acc"] = cat
    results["illuminant_decode_r2"] = ill
    print(f"decodability: category acc {cat:.3f} (chance 0.5) | illuminant R2 {ill:.3f}")

    noise_curve = {}
    for sn in [0.01, 0.03, 0.05, 0.08, 0.12]:
        f2, y2, c2 = _build(R, by, rng, 4000, sensor_noise=sn)
        noise_curve[str(sn)] = dict(
            category=float(cross_val_score(LogisticRegression(max_iter=500), f2, y2, cv=5, scoring="accuracy").mean()),
            illuminant=float(cross_val_score(Ridge(alpha=1.0), f2, (c2 - c2.mean()) / c2.std(), cv=5, scoring="r2").mean()),
        )
    results["noise_robustness"] = noise_curve
    print("noise robustness (category acc / illuminant R2):")
    for sn, d in noise_curve.items():
        print(f"  sigma={sn}: category {d['category']:.3f}  illuminant {d['illuminant']:.3f}")

    save_json("why_summary.json", results)
    cat_drop = noise_curve["0.01"]["category"] - noise_curve["0.12"]["category"]
    ill_drop = noise_curve["0.01"]["illuminant"] - noise_curve["0.12"]["illuminant"]
    better_posed = (cat > 0.8) and (cat_drop < ill_drop)
    print(f"\n=> behaving is the {'BETTER-POSED, illuminant-invariant objective' if better_posed else 'not clearly better-posed'}")


if __name__ == "__main__":
    main()
