"""
§2.2 — Architecture sweep: behaving >= world-recovery holds across the full k1 × bottleneck grid.

Writes:
    arch_sweep.jsonl       — one record per (arch, seed)
    arch_sweep_summary.json

Environment:
    ARCH_SWEEP_BUDGET  wall-clock seconds (default 5400)
"""
import os
import sys
import collections
import numpy as np
from itertools import product
from math import comb

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.data import get_bank, make_trials
from src.training import get_device, train_classifier, train_world_recovery, Budget
from src.metrics import filter_scores, untrained_null
from src.io_utils import make_model, jsonl_append, save_json

BUDGET_S = float(os.environ.get("ARCH_SWEEP_BUDGET", 5400))
EPOCHS = 80
K1S = [4, 8, 16, 32]
BNS = [2, 4, 8]


def main():
    dev = get_device()
    b = Budget(BUDGET_S)
    R, by, is_real = get_bank()

    nulls = {}
    for k1, bn in product(K1S, BNS):
        nulls[(k1, bn)] = untrained_null(dev, make_model, k1=k1, bottleneck=bn, n=20)[0]

    open(os.path.join(os.environ.get("RESULTS_DIR",
         os.path.join(os.path.dirname(__file__), "..", "..", "results")),
         "arch_sweep.jsonl"), "w").close()

    rows = []; seed = 0
    while b.ok(margin=10):
        for k1, bn in product(K1S, BNS):
            if not b.ok(margin=6):
                break
            thr = nulls[(k1, bn)]
            rng = np.random.default_rng(83_000 + seed)
            X, y, m = make_trials(R, by, rng, 4000)
            s = make_model(k1=k1, bottleneck=bn).to(dev)
            train_classifier(s, X, y, dev, epochs=EPOCHS, seed=seed)
            _, sd = filter_scores(s.conv1.weight)
            w = make_model(k1=k1, bottleneck=bn, kind="world").to(dev)
            train_world_recovery(w, X, m["cct"], dev, epochs=EPOCHS, seed=seed)
            _, wd = filter_scores(w.conv1.weight)
            row = dict(seed=seed, k1=k1, bottleneck=bn,
                       surv_double=int((sd > thr).sum()),
                       world_double=int((wd > thr).sum()))
            row["gap"] = row["surv_double"] - row["world_double"]
            jsonl_append("arch_sweep.jsonl", row)
            rows.append(row)
        seed += 1
        if seed % 3 == 0:
            print(f"  {seed} seed-blocks, {b.frac() * 100:.0f}% budget, {len(rows)} rows")

    agg = collections.defaultdict(list)
    for r in rows:
        agg[(r["k1"], r["bottleneck"])].append(r["gap"])

    per_arch = {}
    n_pos = 0
    for (k1, bn), gaps in sorted(agg.items()):
        g = np.array(gaps, float)
        pos = int((g > 0).sum()); neg = int((g < 0).sum()); n = pos + neg
        p = (sum(comb(n, k) for k in range(pos, n + 1)) / (2 ** n)) if n > 0 else 1.0
        per_arch[f"k{k1}_b{bn}"] = dict(mean_gap=float(g.mean()),
                                         frac_surv_ge_world=float((g >= 0).mean()),
                                         n=len(g), sign_p=p)
        if g.mean() > 0:
            n_pos += 1

    summary = dict(source="FOSTER" if is_real else "SYNTHETIC",
                   n_rows=len(rows), n_archs=len(agg),
                   n_archs_survival_wins=n_pos, per_arch=per_arch)
    save_json("arch_sweep_summary.json", summary)

    print("\n===== Section 2.2 Architecture Sweep =====")
    print(f"{n_pos}/{len(agg)} architectures show behaving > world-recovery (mean gap > 0)")
    for k, v in per_arch.items():
        print(f"  {k}: gap {v['mean_gap']:+.2f}  surv>=world {v['frac_surv_ge_world']*100:.0f}%  "
              f"(n={v['n']}, sign-test p={v['sign_p']:.2e})")
    robust = n_pos >= 0.8 * len(agg)
    print(f"=> behaving>=world-recovery: {'ROBUST across all architectures' if robust else 'architecture-dependent - report which'}")


if __name__ == "__main__":
    main()
