"""
§2.1 — Robustness of emergence across 12 rendering perturbations.

Tests both headline claims under systematic variations:
  (A) chromatic power >> untrained null
  (B) behaving >= world-recovery opponency

Writes:
    robustness.jsonl          — one record per (condition, seed)
    robustness_summary.json   — per-condition A/B pass rates

Environment:
    ROBUSTNESS_BUDGET  wall-clock seconds (default 18000 ≈ 5h)
    DATA_DIR / RESULTS_DIR / DEVICE  (see §2.1)
"""
import os
import sys
import collections
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.data import get_bank, N_BANDS, WAVELENGTHS
from src.spectral import planck_illuminant, reflectance_to_lms, lms_to_opponent
from src.training import get_device, train_classifier, train_world_recovery, Budget, accuracy
from src.metrics import filter_scores, untrained_null
from src.io_utils import make_model, jsonl_append, save_json
from src.model import PATCH, CENTER

BUDGET_S = float(os.environ.get("ROBUSTNESS_BUDGET", 18_000))
EPOCHS = 80

CONDITIONS = [
    dict(name="default"),
    dict(name="cct_broad",        cct=(2500, 30_000)),
    dict(name="cct_narrow",       cct=(5000,  8_000)),
    dict(name="cones_shift_pos",  cone_shift=+10.0),
    dict(name="cones_shift_neg",  cone_shift=-10.0),
    dict(name="cones_wide",       cone_sigma_scale=1.3),
    dict(name="refl_noise_hi",    refl_noise=0.05),
    dict(name="refl_noise_vhi",   refl_noise=0.08),
    dict(name="surround_neutral", surround="neutral"),
    dict(name="surround_highchroma", surround="highchroma"),
    dict(name="sensor_noise_hi",  sensor_noise=0.04),
    dict(name="synthetic_refl",   synthetic=True),
]


def custom_cones(shift=0.0, sigma_scale=1.0):
    wl = WAVELENGTHS
    g = lambda mu, s: np.exp(-0.5 * ((wl - mu) / s) ** 2)
    L = g(565 + shift, 45 * sigma_scale)
    M = g(540 + shift, 45 * sigma_scale)
    S = g(445 + shift, 35 * sigma_scale)
    C = np.stack([L, M, S], 0)
    return C / C.sum(1, keepdims=True)


def make_cond_trials(cond, R, by, rng, n):
    from src.data import make_prototypes
    cones = custom_cones(cond.get("cone_shift", 0.0), cond.get("cone_sigma_scale", 1.0))
    cct_range = cond.get("cct", (3000, 25_000))
    rn = cond.get("refl_noise", 0.02)
    sn = cond.get("sensor_noise", 0.01)
    sur_mode = cond.get("surround", "natural")
    protos = make_prototypes(R, by, rng)
    X = np.empty((n, 3, PATCH, PATCH), np.float32)
    y = np.empty(n, np.int64)
    ccts = np.empty(n)
    for i in range(n):
        lab = int(rng.integers(0, 2))
        cr = np.clip(protos[lab][rng.integers(0, 8)] + rng.normal(0, rn, N_BANDS), 0.01, 1.1)
        if sur_mode == "neutral":
            sr = np.full(N_BANDS, 0.5)
        elif sur_mode == "highchroma":
            sr = np.clip(protos[rng.integers(0, 2)][rng.integers(0, 8)] * 1.5, 0.01, 1.1)
        else:
            sr = np.clip(protos[rng.integers(0, 2)][rng.integers(0, 8)]
                         + rng.normal(0, rn, N_BANDS), 0.01, 1.1)
        c = rng.uniform(*cct_range)
        il = planck_illuminant(c)
        cl = cones @ (cr * il)
        sl = cones @ (sr * il)
        p = np.empty((3, PATCH, PATCH), np.float32)
        p[:] = sl[:, None, None]
        p[:, CENTER, CENTER] = cl[:, None, None]
        p += rng.normal(0, sn, p.shape).astype(np.float32)
        X[i] = p; y[i] = lab; ccts[i] = c
    return X, y, ccts


def main():
    dev = get_device()
    bud = Budget(BUDGET_S)
    R_foster, by_f, is_real = get_bank()

    from src.spectral import random_reflectance
    R_syn = np.stack([random_reflectance(np.random.default_rng(k)) for k in range(20_000)])
    by_syn = lms_to_opponent((R_syn * planck_illuminant(6500)) @ __import__("src.spectral", fromlist=["CONES"]).CONES.T)[:, 2]

    thr, null_chroma = untrained_null(dev, make_model, k1=8, bottleneck=4)
    print(f"null: thr {thr:.4f}, chroma floor {null_chroma:.4f}")

    open(os.path.join(os.environ.get("RESULTS_DIR",
         os.path.join(os.path.dirname(__file__), "..", "..", "results")),
         "robustness.jsonl"), "w").close()

    rows = []; seed = 0
    while bud.ok(margin=30):
        for cond in CONDITIONS:
            if not bud.ok(margin=20):
                break
            R, by = (R_syn, by_syn) if cond.get("synthetic") else (R_foster, by_f)
            rng = np.random.default_rng(93_000 + seed * 100 + hash(cond["name"]) % 50)
            X, y, cct = make_cond_trials(cond, R, by, rng, 4000)
            s = make_model().to(dev)
            train_classifier(s, X, y, dev, epochs=EPOCHS, seed=seed)
            sc, sd = filter_scores(s.conv1.weight)
            s_acc = accuracy(s, X, y, dev)
            w = make_model(kind="world").to(dev)
            train_world_recovery(w, X, cct, dev, epochs=EPOCHS, seed=seed)
            _, wd = filter_scores(w.conv1.weight)
            row = dict(seed=seed, cond=cond["name"],
                       surv_acc=s_acc,
                       surv_chroma=float(sc.mean()),
                       surv_double=int((sd > thr).sum()),
                       world_double=int((wd > thr).sum()),
                       A_emergence=bool(sc.mean() > null_chroma * 1.3),
                       B_surv_gt_world=bool((sd > thr).sum() >= (wd > thr).sum()))
            jsonl_append("robustness.jsonl", row)
            rows.append(row)
        seed += 1
        if seed % 3 == 0:
            print(f"  {seed} sweeps, {bud.frac() * 100:.0f}% budget, {len(rows)} rows")

    per = collections.defaultdict(lambda: dict(A=[], B=[], chroma=[], gap=[]))
    for r in rows:
        if r["surv_acc"] >= 0.65:
            per[r["cond"]]["A"].append(r["A_emergence"])
            per[r["cond"]]["B"].append(r["B_surv_gt_world"])
            per[r["cond"]]["chroma"].append(r["surv_chroma"])
            per[r["cond"]]["gap"].append(r["surv_double"] - r["world_double"])

    summary = dict(
        source="FOSTER" if is_real else "SYN",
        null_chroma=null_chroma,
        per_condition={
            c: dict(A_frac=float(np.mean(d["A"])), B_frac=float(np.mean(d["B"])),
                    chroma=float(np.mean(d["chroma"])), mean_gap=float(np.mean(d["gap"])),
                    n=len(d["A"]))
            for c, d in per.items() if d["A"]
        },
    )
    save_json("robustness_summary.json", summary)

    print("\n===== Section 2.1 Robustness =====")
    nA = nB = 0
    for c, d in summary["per_condition"].items():
        okA = d["A_frac"] > 0.8; okB = d["B_frac"] > 0.6
        nA += okA; nB += okB
        print(f"  {c:22s}: emerge {d['A_frac']*100:3.0f}%  surv>=world {d['B_frac']*100:3.0f}%  "
              f"gap {d['mean_gap']:+.2f}  n={d['n']}  {'OK' if okA and okB else '<-- check'}")
    nc = len(summary["per_condition"])
    print(f"=> emergence robust in {nA}/{nc}; survival>=world in {nB}/{nc}")


if __name__ == "__main__":
    main()
