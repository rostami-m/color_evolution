"""
§2.3 — Does the behaving objective itself select center-surround antagonism?

Two tests:
  (A) Learnable-b: make b a free scalar parameter (init 0); does training drive it positive?
  (B) Free-spatial: fully learnable spatial readout; measure emergent antagonism post-hoc.

Writes:
    antagonism_emerges.jsonl
    antagonism_emerges_summary.json

Environment:
    ANTAG_BUDGET  wall-clock seconds (default 6000)
"""
import os
import sys
import numpy as np
from scipy import stats

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.data import get_bank, make_trials
from src.training import get_device, accuracy, Budget
from src.io_utils import jsonl_append, save_json
from experiments.s3_illusions.cs_model import LearnableBCNN, FreeSpatialCNN, CSReadoutCNN, train_cs

BUDGET_S = float(os.environ.get("ANTAG_BUDGET", 6000))
EPOCHS = 100
FIXED_BS = [0.0, 0.5, 1.0, 1.5, 2.0]


def main():
    dev = get_device()
    bud = Budget(BUDGET_S)
    R, by, is_real = get_bank()

    open(os.path.join(os.environ.get("RESULTS_DIR",
         os.path.join(os.path.dirname(__file__), "..", "..", "results")),
         "antagonism_emerges.jsonl"), "w").close()

    learned_b = []; emergent_ant = []; fixedb_acc = {b2: [] for b2 in FIXED_BS}
    seed = 0
    while bud.ok(margin=20):
        rng = np.random.default_rng(90_000 + seed)
        X, y, m = make_trials(R, by, rng, 4000)
        Xv, yv, _ = make_trials(R, by, rng, 1000)

        nb = LearnableBCNN(b_init=0.0).to(dev)
        train_cs(nb, X, y, dev, seed, epochs=EPOCHS)
        b_final = float(nb.b.detach().cpu())
        a_acc = accuracy(nb, Xv, yv, dev)
        learned_b.append(b_final)

        nf = FreeSpatialCNN().to(dev)
        train_cs(nf, X, y, dev, seed, epochs=EPOCHS)
        ant, cen, sur = nf.emergent_antagonism()
        f_acc = accuracy(nf, Xv, yv, dev)
        emergent_ant.append(ant)

        accs = {}
        if seed % 3 == 0:
            for fb in FIXED_BS:
                if not bud.ok(margin=12):
                    break
                nc = CSReadoutCNN(b=fb).to(dev)
                train_cs(nc, X, y, dev, seed)
                ac = accuracy(nc, Xv, yv, dev)
                fixedb_acc[fb].append(ac); accs[str(fb)] = ac

        row = dict(seed=seed, learned_b=b_final, learnable_acc=a_acc,
                   emergent_antagonism=ant, free_center=cen, free_surround=sur,
                   free_acc=f_acc, fixedb_acc=accs)
        jsonl_append("antagonism_emerges.jsonl", row)
        seed += 1
        if seed % 5 == 0:
            print(f"  {seed} seeds, learned_b~{np.mean(learned_b):.2f}, "
                  f"emergent_ant~{np.mean(emergent_ant):.3f}, {bud.frac()*100:.0f}%")

    lb = np.array(learned_b); ea = np.array(emergent_ant)
    summary = dict(
        source="FOSTER" if is_real else "SYNTHETIC",
        n_seeds=len(lb),
        learned_b_mean=float(lb.mean()),
        learned_b_frac_positive=float((lb > 0).mean()),
        learned_b_p=float(stats.wilcoxon(lb).pvalue) if len(lb) > 5 and np.any(lb != 0) else None,
        emergent_antagonism_mean=float(ea.mean()),
        emergent_antagonism_frac_positive=float((ea > 0).mean()),
        emergent_antagonism_p=float(stats.wilcoxon(ea).pvalue) if len(ea) > 5 and np.any(ea != 0) else None,
        fixedb_accuracy={str(b2): (float(np.mean(v)) if v else None) for b2, v in fixedb_acc.items()},
    )
    save_json("antagonism_emerges_summary.json", summary)

    print("\n===== Section 2.3 Antagonism Emerges =====")
    print(f"(A) learnable b (init 0): mean {lb.mean():+.3f}, positive in {(lb>0).mean()*100:.0f}%, p={summary['learned_b_p']}")
    print(f"(B) free-spatial antagonism: mean {ea.mean():+.4f}, positive in {(ea>0).mean()*100:.0f}%")
    selects = lb.mean() > 0.05 and ea.mean() > 0
    print(f"=> behaving {'SELECTS antagonism (contrast regime) spontaneously' if selects else 'does not clearly select antagonism'}")


if __name__ == "__main__":
    main()
