"""
§2.1 — Color opponency and constancy emerge from the behaving objective.

Three paired conditions (untrained | shuffled-labels | behaving) with:
  (1) accuracy gate — only analyse networks that solved the task (acc ≥ 0.80)
  (2) untrained null — 95th-percentile threshold calibrated on random-init networks
  (3) chromatic power — continuous, threshold-free measure of color structure

Writes:
    emergence.jsonl   — one record per seed (untrained / shuffled / behaving triplet)
    emergence_summary.json — statistics, verdict flags

Environment:
    EMERGENCE_BUDGET  wall-clock seconds (default 1800)
    DATA_DIR          path to data/  (default: code/data/)
    RESULTS_DIR       path to results/ (default: code/results/)
    DEVICE            torch device string (default: auto-detect CUDA > MPS > CPU)
"""
import os
import sys
import numpy as np
import torch
from scipy import stats

# Make src/ importable when this file is run directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.data import get_bank, make_trials, results_path
from src.training import get_device, train_classifier, Budget
from src.metrics import filter_scores, untrained_null
from src.io_utils import make_model, jsonl_append, save_json

BUDGET_S = float(os.environ.get("EMERGENCE_BUDGET", 1800))
EPOCHS = 80
ACC_GATE = 0.80


def main():
    dev = get_device()
    b = Budget(BUDGET_S)
    R, by, is_real = get_bank()
    print(f"data source: {'Foster (real)' if is_real else 'synthetic fallback'}")

    # Calibrate the double-opponent threshold on random-init networks
    thr, null_chroma = untrained_null(dev, make_model, k1=8, bottleneck=4)
    print(f"untrained null: double-opp threshold(95pct)={thr:.4f}  "
          f"mean chroma power={null_chroma:.4f}")

    # Start each run from a fresh results file (overwrite rather than append).
    open(results_path("emergence.jsonl"), "w").close()

    rows = []
    seed = 0
    while b.ok(margin=4):
        rng = np.random.default_rng(50_000 + seed)
        X, y, m = make_trials(R, by, rng, 4000)
        Xv, yv, _ = make_trials(R, by, rng, 800)

        # Untrained baseline
        torch.manual_seed(50_000 + seed)
        un = make_model(k1=8, bottleneck=4).to(dev)
        uc, _ = filter_scores(un.conv1.weight)

        # Behaving objective
        rnet = make_model(k1=8, bottleneck=4).to(dev)
        train_classifier(rnet, X, y, dev, epochs=EPOCHS, seed=seed)
        with torch.no_grad():
            rnet.eval()
            racc = (rnet(torch.as_tensor(Xv, device=dev)).argmax(1) ==
                    torch.as_tensor(yv, device=dev)).float().mean().item()
        rc, rd = filter_scores(rnet.conv1.weight)

        # Shuffled-labels negative control
        ys = y.copy(); rng.shuffle(ys)
        snet = make_model(k1=8, bottleneck=4).to(dev)
        train_classifier(snet, X, ys, dev, epochs=EPOCHS, seed=seed)
        with torch.no_grad():
            snet.eval()
            sacc = (snet(torch.as_tensor(Xv, device=dev)).argmax(1) ==
                    torch.as_tensor(yv, device=dev)).float().mean().item()
        sc, sd = filter_scores(snet.conv1.weight)

        row = dict(seed=seed,
                   real_acc=racc, shuf_acc=sacc,
                   real_double=int((rd > thr).sum()), shuf_double=int((sd > thr).sum()),
                   untr_double=int(((_ := filter_scores(un.conv1.weight))[1] > thr).sum()),
                   real_chroma=float(rc.mean()), shuf_chroma=float(sc.mean()),
                   untr_chroma=float(uc.mean()))
        jsonl_append("emergence.jsonl", row)
        rows.append(row)
        seed += 1
        if seed % 10 == 0:
            print(f"  {seed} seeds, {b.frac() * 100:.0f}% budget used")

    # --- Summary statistics ---
    learned = [r for r in rows if r["real_acc"] >= ACC_GATE]

    def col(rs, k):
        return np.array([r[k] for r in rs], float)

    summary = dict(
        source="FOSTER" if is_real else "SYNTHETIC",
        n_seeds=len(rows),
        n_learned=len(learned),
        acc_gate=ACC_GATE,
        null_threshold=thr,
        null_chroma_mean=null_chroma,
        real_acc_mean=float(col(rows, "real_acc").mean()),
        shuf_acc_mean=float(col(rows, "shuf_acc").mean()),
    )
    if learned:
        for cond in ("real", "shuf", "untr"):
            summary[f"{cond}_double_mean"] = float(col(learned, f"{cond}_double").mean())
            summary[f"{cond}_chroma_mean"] = float(col(learned, f"{cond}_chroma").mean())

        rd = col(learned, "real_double"); ud = col(learned, "untr_double"); sd = col(learned, "shuf_double")
        rc = col(learned, "real_chroma"); uc_ = col(learned, "untr_chroma"); sc_ = col(learned, "shuf_chroma")

        def safe_wilcoxon(a, b2):
            try:
                return float(stats.wilcoxon(a, b2).pvalue)
            except Exception:
                return float("nan")

        summary["p_double_real_vs_untr"] = safe_wilcoxon(rd, ud)
        summary["p_double_real_vs_shuf"] = safe_wilcoxon(rd, sd)
        summary["p_chroma_real_vs_untr"] = safe_wilcoxon(rc, uc_)
        summary["p_chroma_real_vs_shuf"] = safe_wilcoxon(rc, sc_)

    save_json("emergence_summary.json", summary)

    print("\n===== Section 2.1 Emergence =====")
    print(f"n={len(rows)} seeds; learned (acc>={ACC_GATE}) = {len(learned)}")
    if learned:
        print(f"double-opp (above null): real {summary['real_double_mean']:.2f} | "
              f"shuf {summary['shuf_double_mean']:.2f} | untrained {summary['untr_double_mean']:.2f}")
        print(f"  p(real>untrained)={summary['p_chroma_real_vs_untr']:.2e}  "
              f"p(real>shuffled)={summary['p_chroma_real_vs_shuf']:.2e}")
        print(f"chromatic power: real {summary['real_chroma_mean']:.4f} | "
              f"shuf {summary['shuf_chroma_mean']:.4f} | untrained {summary['untr_chroma_mean']:.4f}")
        emerges = (summary["real_double_mean"] > summary["untr_double_mean"] and
                   summary["real_chroma_mean"] > summary["untr_chroma_mean"])
        print(f"=> opponency emerges from the behaving objective: {'YES' if emerges else 'NO - investigate'}")


if __name__ == "__main__":
    main()
