"""
§2.3 — Contrast and assimilation: same objective, sign set by spatial configuration.

Tests whether the sign of the induced shift flips between a uniform and a fine-
checkerboard surround. Also sweeps the antagonism parameter b to show both regimes
exist within a single model family.

Writes:
    contrast_assimilation.jsonl
    contrast_assimilation_summary.json
    antagonism_sweep_summary.json

Environment:
    ILLUSION_BUDGET  wall-clock seconds (default 6000)
"""
import os
import sys
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.data import get_bank, make_trials
from src.training import get_device, train_classifier, accuracy, Budget
from src.io_utils import jsonl_append, save_json
from experiments.s3_illusions.illusion_stimuli import adapting_gray, induced_shift, INDUCERS
from experiments.s3_illusions.cs_model import CSReadoutCNN, train_cs

BUDGET_S = float(os.environ.get("ILLUSION_BUDGET", 6000))
EPOCHS = 80
BALANCES = [0.0, 0.5, 1.0, 1.5]


def main():
    dev = get_device()
    b = Budget(BUDGET_S)
    R, by, is_real = get_bank()

    for name in ("contrast_assimilation.jsonl", "antagonism_sweep.jsonl"):
        open(os.path.join(os.environ.get("RESULTS_DIR",
             os.path.join(os.path.dirname(__file__), "..", "..", "results")), name), "w").close()

    rows_sign = []; rows_b = []; seed = 0
    while b.ok(margin=15):
        rng = np.random.default_rng(88_000 + seed)
        X, y, m = make_trials(R, by, rng, 4000)
        gray = adapting_gray(R, rng)
        pr = np.random.default_rng(seed)

        # --- Sign-flip test: uniform vs fine surround ---
        from src.io_utils import make_model
        from src.training import train_world_recovery
        snet = make_model().to(dev)
        train_classifier(snet, X, y, dev, epochs=EPOCHS, seed=seed)
        for cfg in ("uniform", "fine"):
            shifts = [induced_shift(snet, gray, v, cfg, R, dev, pr) for v in INDUCERS.values()]
            row = dict(seed=seed, config=cfg, mean_shift=float(np.mean(shifts)))
            jsonl_append("contrast_assimilation.jsonl", row)
            rows_sign.append(row)

        # --- Antagonism sweep (every other seed to save budget) ---
        if seed % 2 == 0:
            for bal in BALANCES:
                if not b.ok(margin=10):
                    break
                net = CSReadoutCNN(b=bal).to(dev)
                train_cs(net, X, y, dev, seed)
                acc = accuracy(net, X, y, dev)
                shift = float(np.mean([induced_shift(net, gray, v, "uniform", R, dev, pr)
                                       for v in INDUCERS.values()]))
                row = dict(seed=seed, balance=bal, acc=acc, mean_shift=shift)
                jsonl_append("antagonism_sweep.jsonl", row)
                rows_b.append(row)

        seed += 1
        if seed % 8 == 0:
            print(f"  {seed} seeds, {b.frac() * 100:.0f}% budget, {len(rows_sign)} sign-rows, {len(rows_b)} b-rows")

    # --- Summaries ---
    def grp(rows, cfg):
        return np.array([r["mean_shift"] for r in rows if r.get("config") == cfg])

    su = grp(rows_sign, "uniform"); sf = grp(rows_sign, "fine")
    save_json("contrast_assimilation_summary.json", dict(
        source="FOSTER" if is_real else "SYNTHETIC",
        n_seeds=len(set(r["seed"] for r in rows_sign)),
        surv_uniform_shift=float(su.mean()) if len(su) else None,
        surv_fine_shift=float(sf.mean()) if len(sf) else None,
        frac_uniform_contrast=float((su < 0).mean()) if len(su) else None,
        frac_fine_assimilation=float((sf > 0).mean()) if len(sf) else None,
    ))

    per_b = {}
    for bal in BALANCES:
        v = np.array([r["mean_shift"] for r in rows_b if r["balance"] == bal and r["acc"] >= 0.7])
        if len(v):
            per_b[bal] = dict(mean_shift=float(v.mean()), frac_contrast=float((v < 0).mean()), n=len(v))
    save_json("antagonism_sweep_summary.json", dict(
        source="FOSTER" if is_real else "SYNTHETIC",
        per_balance=per_b,
    ))

    print("\n===== Section 2.3 Contrast/Assimilation =====")
    if len(su) and len(sf):
        flip = su.mean() < 0 < sf.mean()
        print(f"uniform shift {su.mean():+.4f}  fine shift {sf.mean():+.4f}")
        print(f"=> sign flip: {'YES - both illusions from one objective' if flip else 'NO'}")
    for bal in BALANCES:
        if bal in per_b:
            print(f"  b={bal}: shift {per_b[bal]['mean_shift']:+.4f}  "
                  f"contrast in {per_b[bal]['frac_contrast']*100:.0f}%")


if __name__ == "__main__":
    main()
