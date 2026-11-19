"""
§2.4 — Behavioral utility sharpens discrimination: imposed fitness-peak sweep.

Sweeps the fitness-peak location and regresses the emergent sensitivity peak on the
imposed location. Mechanism is established if slope > 0 with CI excluding 0.

Writes:
    fitness_sweep.jsonl
    fitness_sweep_summary.json

Environment:
    FITNESS_BUDGET  wall-clock seconds (default 14400)
"""
import os
import sys
import numpy as np
from scipy import stats

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.data import get_bank, make_trials
from src.training import get_device, train_classifier, Budget
from src.io_utils import make_model, jsonl_append, save_json
from experiments.s4_utility.discrimination import sensitivity_profile, smoothed_peak, PROBE_GRID

BUDGET_S = float(os.environ.get("FITNESS_BUDGET", 14_400))
EPOCHS = 80
FITNESS_SWEEP = [-0.30, -0.20, -0.10, 0.0, 0.10, 0.20, 0.30]
FITNESS_SD = 0.10


def main():
    dev = get_device()
    b = Budget(BUDGET_S)
    R, by, is_real = get_bank()

    open(os.path.join(os.environ.get("RESULTS_DIR",
         os.path.join(os.path.dirname(__file__), "..", "..", "results")),
         "fitness_sweep.jsonl"), "w").close()

    rows = []; seed = 0
    while b.ok(margin=20):
        for fp in FITNESS_SWEEP:
            if not b.ok(margin=15):
                break
            rng = np.random.default_rng(60_000 + seed)
            Xtr, ytr, _ = make_trials(R, by, rng, 4000,
                                       weighting="fitness", fitness_peak=fp, fitness_sd=FITNESS_SD)
            net = make_model().to(dev)
            train_classifier(net, Xtr, ytr, dev, epochs=EPOCHS, seed=seed)
            sens = sensitivity_profile(net, R, by, dev, np.random.default_rng(seed))
            row = dict(seed=seed, fitness_peak=fp,
                       emergent_peak=smoothed_peak(sens),
                       argmax_peak=float(PROBE_GRID[np.nanargmax(sens)]))
            jsonl_append("fitness_sweep.jsonl", row)
            rows.append(row)
        seed += 1
        if seed % 5 == 0:
            print(f"  {seed} seed-blocks, {len(rows)} nets, {b.frac() * 100:.0f}% budget")

    fp_arr = np.array([r["fitness_peak"] for r in rows], float)
    ep_arr = np.array([r["emergent_peak"] for r in rows], float)
    lr = stats.linregress(fp_arr, ep_arr)
    rng2 = np.random.default_rng(0); idx = np.arange(len(fp_arr))
    slopes = []
    for _ in range(5000):
        s = rng2.choice(idx, len(idx))
        try:
            slopes.append(stats.linregress(fp_arr[s], ep_arr[s]).slope)
        except Exception:
            pass
    ci = (float(np.percentile(slopes, 2.5)), float(np.percentile(slopes, 97.5)))
    permean = {f"{p:+.2f}": float(ep_arr[fp_arr == p].mean()) for p in FITNESS_SWEEP}

    summary = dict(source="FOSTER" if is_real else "SYNTHETIC",
                   n_nets=len(rows), slope=float(lr.slope), slope_ci95=ci,
                   r=float(lr.rvalue), p_value=float(lr.pvalue),
                   per_location_emergent_peak=permean)
    save_json("fitness_sweep_summary.json", summary)

    print("\n===== Section 2.4 Fitness Sweep =====")
    for p in FITNESS_SWEEP:
        print(f"   imposed {p:+.2f} -> emergent {permean[f'{p:+.2f}']:+.3f}")
    print(f"slope(emergent ~ imposed) = {lr.slope:+.3f}  95%CI {ci}  r={lr.rvalue:+.3f}  p={lr.pvalue:.2e}")
    tracks = ci[0] > 0
    print(f"=> emergent JND peak {'TRACKS imposed fitness peak (mechanism confirmed)' if tracks else 'does not track fitness'}")


if __name__ == "__main__":
    main()
