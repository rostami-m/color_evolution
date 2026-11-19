"""
§2.1 — Optimizer invariance: CMA-ES replication of the emergence result.

Trains the identical network with a self-contained CMA-ES (no external dependency)
and compares emergent opponency and accuracy to a gradient-trained paired control.
This rules out backpropagation geometry as the cause of opponent structure.

Writes:
    cmaes.jsonl          — one record per (seed, grad/cmaes)
    cmaes_summary.json

Environment:
    CMAES_BUDGET  wall-clock seconds (default 9000)
"""
import os
import sys
import numpy as np
import torch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.data import get_bank, make_trials
from src.training import get_device, train_classifier, accuracy, Budget
from src.metrics import filter_scores, untrained_null
from src.io_utils import make_model, jsonl_append, save_json

BUDGET_S = float(os.environ.get("CMAES_BUDGET", 9_000))
EPOCHS = 80
ACC_GATE = 0.80
CMA_ITERS = 300


def _flat(net):
    return torch.cat([p.detach().reshape(-1) for p in net.parameters()]).cpu().numpy()


def _set_flat(net, v, dev):
    i = 0
    for p in net.parameters():
        n = p.numel()
        p.data.copy_(torch.tensor(v[i:i + n], dtype=torch.float32, device=dev).reshape(p.shape))
        i += n


@torch.no_grad()
def _fit(net, Xc, yc):
    net.eval()
    return (net(Xc).argmax(1) == yc).float().mean().item()


def cmaes(net, X, y, dev, seed, budget, iters=CMA_ITERS):
    """Compact separable CMA-ES — no external dependency. Maximises accuracy."""
    rng = np.random.default_rng(seed)
    Xc = torch.as_tensor(X, device=dev)
    yc = torch.as_tensor(y, device=dev)
    d = _flat(net).size
    mean = _flat(net).astype(np.float64)
    sigma = 0.3
    lam = 4 + int(3 * np.log(d))
    mu = lam // 2
    w = np.log(mu + 0.5) - np.log(np.arange(1, mu + 1)); w /= w.sum()
    mueff = 1.0 / np.sum(w ** 2)
    cs = (mueff + 2) / (d + mueff + 5)
    cc = (4 + mueff / d) / (d + 4 + 2 * mueff / d)
    c1 = 2 / ((d + 1.3) ** 2 + mueff)
    cmu = min(1 - c1, 2 * (mueff - 2 + 1 / mueff) / ((d + 2) ** 2 + mueff))
    damps = 1 + 2 * max(0, np.sqrt((mueff - 1) / (d + 1)) - 1) + cs
    ps = np.zeros(d); pc = np.zeros(d); C = np.ones(d)
    chiN = np.sqrt(d) * (1 - 1 / (4 * d) + 1 / (21 * d * d))
    best_v = mean.copy(); best_f = -1.0
    for it in range(iters):
        if not budget.ok(margin=3):
            break
        Z = rng.standard_normal((lam, d))
        Yk = Z * np.sqrt(C)
        Xk = mean + sigma * Yk
        fits = np.array([(_set_flat(net, Xk[k], dev), _fit(net, Xc, yc))[1] for k in range(lam)])
        idx = np.argsort(-fits)
        if fits[idx[0]] > best_f:
            best_f = float(fits[idx[0]]); best_v = Xk[idx[0]].copy()
        ysel = Yk[idx[:mu]]
        ymean = (w[:, None] * ysel).sum(0)
        mean = mean + sigma * ymean
        ps = (1 - cs) * ps + np.sqrt(cs * (2 - cs) * mueff) * (ymean / np.sqrt(C))
        hsig = np.linalg.norm(ps) / np.sqrt(1 - (1 - cs) ** (2 * (it + 1))) / chiN < 1.4 + 2 / (d + 1)
        pc = (1 - cc) * pc + (hsig * np.sqrt(cc * (2 - cc) * mueff)) * ymean
        C = ((1 - c1 - cmu) * C
             + c1 * (pc ** 2 + (not hsig) * cc * (2 - cc) * C)
             + cmu * np.sum(w[:, None] * (ysel ** 2), 0))
        C = np.clip(C, 1e-10, 1e6)
        sigma *= np.exp((cs / damps) * (np.linalg.norm(ps) / chiN - 1))
        sigma = min(sigma, 1e3)
    _set_flat(net, best_v, dev)
    return net, best_f


def main():
    dev = get_device()
    b = Budget(BUDGET_S)
    R, by, is_real = get_bank()
    thr, null_chroma = untrained_null(dev, make_model, k1=8, bottleneck=4)
    print(f"null: double-opp thr {thr:.4f}, chroma floor {null_chroma:.4f}")

    open(os.path.join(os.environ.get("RESULTS_DIR",
         os.path.join(os.path.dirname(__file__), "..", "..", "results")),
         "cmaes.jsonl"), "w").close()

    rows = []; seed = 0
    while b.ok(margin=40):
        rng = np.random.default_rng(82_000 + seed)
        X, y, m = make_trials(R, by, rng, 1500)

        g = make_model().to(dev)
        train_classifier(g, X, y, dev, epochs=EPOCHS, seed=seed)
        gc, gd = filter_scores(g.conv1.weight)
        g_acc = accuracy(g, X, y, dev)

        e = make_model().to(dev)
        e, e_acc = cmaes(e, X, y, dev, seed, b)
        ec, ed = filter_scores(e.conv1.weight)

        row = dict(seed=seed, grad_acc=g_acc, cma_acc=e_acc,
                   grad_double=int((gd > thr).sum()), cma_double=int((ed > thr).sum()),
                   grad_chroma=float(gc.mean()), cma_chroma=float(ec.mean()))
        jsonl_append("cmaes.jsonl", row)
        rows.append(row)
        seed += 1
        print(f"  seed {seed}: grad acc {g_acc:.2f} dbl {row['grad_double']} | "
              f"CMA acc {e_acc:.2f} dbl {row['cma_double']} ({b.frac() * 100:.0f}%)")

    col = lambda rs, k: np.array([r[k] for r in rs], float)
    el = [r for r in rows if r["cma_acc"] >= ACC_GATE]
    summary = dict(source="FOSTER" if is_real else "SYNTHETIC",
                   n_seeds=len(rows), null_threshold=thr, null_chroma=null_chroma,
                   grad_acc=float(col(rows, "grad_acc").mean()),
                   cma_acc=float(col(rows, "cma_acc").mean()),
                   n_cma_learned=len(el),
                   cma_double_learned=float(col(el, "cma_double").mean()) if el else None,
                   cma_chroma_learned=float(col(el, "cma_chroma").mean()) if el else None,
                   grad_double=float(col(rows, "grad_double").mean()))
    save_json("cmaes_summary.json", summary)

    print("\n===== Section 2.1 CMA-ES =====")
    print(f"n={len(rows)} | grad acc {summary['grad_acc']:.2f} | "
          f"CMA-ES acc {summary['cma_acc']:.2f}  ({len(el)} passed gate)")
    if el:
        emerges = (summary["cma_chroma_learned"] > null_chroma and
                   summary["cma_double_learned"] > 0)
        print(f"CMA-ES: chroma {summary['cma_chroma_learned']:.3f} vs floor {null_chroma:.3f}, "
              f"double {summary['cma_double_learned']:.2f}")
        print(f"=> opponency under CMA-ES: {'EMERGES - not a backpropagation artifact' if emerges else 'does not exceed null'}")
    else:
        print("=> CMA-ES did not reach the accuracy gate within the time budget.")


if __name__ == "__main__":
    main()
