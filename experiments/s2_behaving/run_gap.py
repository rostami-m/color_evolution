"""
§2.2 — Large-N paired test of the behaving vs world-recovery opponency gap.

Both networks share an identical body; only the objective differs.
This is a direct comparison of learned objectives, not of a learned vs. classical method.

Writes:
    gap.jsonl          — one record per seed
    gap_summary.json   — mean gap, 95% CI, sign-test p-value

Environment:
    GAP_BUDGET  wall-clock seconds (default 2400)
"""
import os
import sys
import numpy as np
from math import comb

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.data import get_bank, make_trials
from src.training import get_device, train_classifier, train_world_recovery, Budget
from src.metrics import opponency_report, count_opponency
from src.io_utils import make_model, jsonl_append, save_json

BUDGET_S = float(os.environ.get("GAP_BUDGET", 2400))
EPOCHS = 80


def main():
    dev = get_device()
    b = Budget(BUDGET_S)
    R, by, is_real = get_bank()

    open(os.path.join(os.environ.get("RESULTS_DIR",
         os.path.join(os.path.dirname(__file__), "..", "..", "results")),
         "gap.jsonl"), "w").close()

    rows = []; seed = 0
    while b.ok(margin=6):
        rng = np.random.default_rng(10_000 + seed)
        X, y, m = make_trials(R, by, rng, 4000)

        snet = make_model().to(dev)
        train_classifier(snet, X, y, dev, epochs=EPOCHS, seed=seed)
        s_ns, s_nd = count_opponency(opponency_report(snet.conv1.weight))

        wnet = make_model(kind="world").to(dev)
        train_world_recovery(wnet, X, m["cct"], dev, epochs=EPOCHS, seed=seed)
        w_ns, w_nd = count_opponency(opponency_report(wnet.conv1.weight))

        row = dict(seed=seed, surv_double=s_nd, surv_single=s_ns,
                   world_double=w_nd, world_single=w_ns, gap=s_nd - w_nd)
        jsonl_append("gap.jsonl", row)
        rows.append(row)
        seed += 1
        if seed % 10 == 0:
            print(f"  {seed} seeds, {b.frac() * 100:.0f}% budget")

    gap = np.array([r["gap"] for r in rows], float)
    sd = np.array([r["surv_double"] for r in rows])
    wd = np.array([r["world_double"] for r in rows])
    rng2 = np.random.default_rng(0)
    boot = [rng2.choice(gap, len(gap)).mean() for _ in range(5000)]
    ci = (float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5)))
    pos = int((gap > 0).sum()); neg = int((gap < 0).sum())
    n = pos + neg
    p = sum(comb(n, k) for k in range(pos, n + 1)) / (2 ** n) if n > 0 else 1.0

    summary = dict(source="FOSTER" if is_real else "SYNTHETIC",
                   n_seeds=len(rows),
                   surv_double_mean=float(sd.mean()), world_double_mean=float(wd.mean()),
                   gap_mean=float(gap.mean()), gap_ci95=ci,
                   frac_surv_ge_world=float((gap >= 0).mean()), sign_test_p=p)
    save_json("gap_summary.json", summary)

    print("\n===== Section 2.2 Behaving vs World-Recovery =====")
    print(f"n={len(rows)} seeds | survival double {sd.mean():.2f} vs world {wd.mean():.2f}")
    print(f"gap mean {gap.mean():+.2f}  95%CI {ci}  sign-test p={p:.2e}")
    print(f"survival>=world in {(gap >= 0).mean() * 100:.0f}% of seeds")


if __name__ == "__main__":
    main()
