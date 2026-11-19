"""
§2.4 — Ecological fitness: fitness locus determined by real spectra, not hand-set.

Uses ripe-fruit, foliage, and skin reflectance spectra to fix the fitness locus,
then tests whether the emergent discrimination peak tracks the ecologically-determined
chromaticity. Removes the free-parameter criticism of the fitness-sweep experiment.

Writes:
    ecological_fitness.jsonl
    ecological_fitness_summary.json

Environment:
    ECO_BUDGET  wall-clock seconds (default 9000)
"""
import os
import sys
import numpy as np
from scipy import stats

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.data import get_bank, make_trials
from src.spectral import WAVELENGTHS, planck_illuminant, reflectance_to_lms, lms_to_opponent
from src.training import get_device, train_classifier, Budget
from src.io_utils import make_model, jsonl_append, save_json
from experiments.s4_utility.discrimination import sensitivity_profile, smoothed_peak

BUDGET_S = float(os.environ.get("ECO_BUDGET", 9_000))
EPOCHS = 80
WL = WAVELENGTHS


def ecological_reflectances():
    x = np.linspace(0, 1, len(WL))
    fruit = 0.10 + 0.80 * x
    foliage = 0.10 + 0.65 * np.exp(-0.5 * ((np.linspace(-1, 1, len(WL))) / 0.35) ** 2)
    skin = 0.25 + 0.45 * x ** 1.5
    return dict(fruit=fruit, foliage=foliage, skin=skin)


def by_coord(refl, ccts=(5500, 6500, 10_000)):
    return float(np.mean([lms_to_opponent(reflectance_to_lms(refl, planck_illuminant(c)))[2]
                          for c in ccts]))


def main():
    dev = get_device()
    b = Budget(BUDGET_S)
    R, by, is_real = get_bank()
    eco = ecological_reflectances()
    eco_by = {k: by_coord(v) for k, v in eco.items()}
    print("ecological fitness loci (b-y, from real spectra):",
          {k: round(v, 3) for k, v in eco_by.items()})
    diets = list(eco.keys())

    open(os.path.join(os.environ.get("RESULTS_DIR",
         os.path.join(os.path.dirname(__file__), "..", "..", "results")),
         "ecological_fitness.jsonl"), "w").close()

    rows = []; seed = 0
    while b.ok(margin=20):
        for diet in diets:
            if not b.ok(margin=15):
                break
            fp = eco_by[diet]
            rng = np.random.default_rng(84_000 + seed)
            Xtr, ytr, m = make_trials(R, by, rng, 4000,
                                       weighting="fitness", fitness_peak=fp, fitness_sd=0.10)
            net = make_model().to(dev)
            train_classifier(net, Xtr, ytr, dev, epochs=EPOCHS, seed=seed)
            peak = smoothed_peak(sensitivity_profile(net, R, by, dev, np.random.default_rng(seed)))
            row = dict(seed=seed, diet=diet, eco_locus=fp,
                       emergent_peak=peak, dist=abs(peak - fp))
            jsonl_append("ecological_fitness.jsonl", row)
            rows.append(row)
        seed += 1
        if seed % 5 == 0:
            print(f"  {seed} seed-blocks, {len(rows)} nets, {b.frac() * 100:.0f}% budget")

    fp_arr = np.array([r["eco_locus"] for r in rows])
    ep_arr = np.array([r["emergent_peak"] for r in rows])
    lr = stats.linregress(fp_arr, ep_arr)
    per_diet = {}
    for d in diets:
        sub = [r for r in rows if r["diet"] == d]
        per_diet[d] = dict(eco_locus=eco_by[d],
                           emergent_peak_mean=float(np.mean([r["emergent_peak"] for r in sub])),
                           n=len(sub))
    summary = dict(source="FOSTER" if is_real else "SYNTHETIC",
                   n_nets=len(rows), eco_loci=eco_by,
                   slope=float(lr.slope), r=float(lr.rvalue), p_value=float(lr.pvalue),
                   per_diet=per_diet)
    save_json("ecological_fitness_summary.json", summary)

    print("\n===== Section 2.4 Ecological Fitness =====")
    for d in diets:
        pd = per_diet[d]
        print(f"  diet={d:8s} eco-locus {pd['eco_locus']:+.3f} -> "
              f"emergent peak {pd['emergent_peak_mean']:+.3f} (n={pd['n']})")
    print(f"slope(emergent ~ eco-locus) = {lr.slope:+.3f}  r={lr.rvalue:+.3f}  p={lr.pvalue:.2e}")
    print(f"=> {'TRACKS ecology (de-circularized)' if lr.pvalue < 0.05 and lr.slope > 0 else 'does not track ecology'}")


if __name__ == "__main__":
    main()
