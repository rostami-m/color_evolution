"""
§2.3 — Four additional illusions from the same center-surround mechanism:
  I1  Chromatic Chubb / gamut-contraction
  I2  Chromatic Cornsweet edge
  I3  Chromatic Mach bands
  I4  Chromatic Munker-White

All use CSReadoutCNN at contrast-regime antagonism (b=1.0).

Writes:
    more_illusions.jsonl
    more_illusions_summary.json

Environment:
    MORE_ILLUSIONS_BUDGET  wall-clock seconds (default 6000)
"""
import os
import sys
import numpy as np
import torch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.data import get_bank, make_trials
from src.training import get_device, accuracy, Budget
from src.io_utils import jsonl_append, save_json
from experiments.s3_illusions.illusion_stimuli import (
    adapting_gray, cone_contrast, build_patch, INDUCERS, INDUCE, CENTER,
)
from experiments.s3_illusions.cs_model import CSReadoutCNN, train_cs, cs_repr

BUDGET_S = float(os.environ.get("MORE_ILLUSIONS_BUDGET", 6000))
EPOCHS = 80
B_ANTAG = 1.0

BIGP = 21
CEN_L = slice(2, 9)
CEN_R = slice(12, 19)


def cornsweet_patch(gray, vec, amp, cusp=True):
    p = np.empty((3, BIGP, BIGP), np.float32); p[:] = gray[:, None, None]
    hi = cone_contrast(gray, vec, amp)
    lo = cone_contrast(gray, tuple(-x for x in vec), amp)
    if cusp:
        for c in range(BIGP):
            d = c - BIGP // 2
            if abs(d) <= 4:
                w = (4 - abs(d)) / 4.0
                col = hi if d < 0 else lo
                for ch in range(3):
                    p[ch, :, c] = gray[ch] + (col[ch] - gray[ch]) * w
    return p


def mach_ramp(gray, vec, amp):
    p = np.empty((3, BIGP, BIGP), np.float32)
    plateau = cone_contrast(gray, vec, amp)
    for c in range(BIGP):
        if c < BIGP // 3:
            w = 0.0
        elif c > 2 * BIGP // 3:
            w = 1.0
        else:
            w = (c - BIGP // 3) / (BIGP // 3)
        for ch in range(3):
            p[ch, :, c] = gray[ch] + (plateau[ch] - gray[ch]) * w
    return p


def run_cornsweet(net, gray, dev):
    res = {}
    for vec_name, vec in INDUCERS.items():
        X = np.stack([cornsweet_patch(gray, vec, INDUCE, cusp=True) for _ in range(32)])
        with torch.no_grad():
            h = net.features(torch.as_tensor(X, device=dev))
            L = h[:, :, :, CEN_L].mean(dim=(2, 3)).cpu().numpy().mean(0)
            Rr = h[:, :, :, CEN_R].mean(dim=(2, 3)).cpu().numpy().mean(0)
        res[vec_name] = float(np.linalg.norm(L - Rr))
    return res


def run_mach(net, gray, dev):
    res = {}
    for vec_name, vec in INDUCERS.items():
        X = np.stack([mach_ramp(gray, vec, INDUCE) for _ in range(16)])
        with torch.no_grad():
            h = net.features(torch.as_tensor(X, device=dev)).mean(0).cpu().numpy()
        prof = np.linalg.norm(h.mean(1), axis=0)
        x = np.arange(BIGP); lin = np.polyval(np.polyfit(x, prof, 1), x)
        infl = [BIGP // 3, 2 * BIGP // 3]
        res[vec_name] = float(np.mean([abs(prof[i] - lin[i]) for i in infl]))
    return res


def run_chubb(net, gray, R, dev, rng):
    res = {}
    for var in [0.0, 0.15, 0.30, 0.45]:
        mags = []
        cb = np.indices((9, 9)).sum(0) % 2
        dirs = list(INDUCERS.values())
        for vec in INDUCERS.values():
            test = cone_contrast(gray, vec, INDUCE)
            n = 48
            X = np.empty((n, 3, 9, 9), np.float32)
            X0 = np.empty((n, 3, 9, 9), np.float32)
            for i in range(n):
                p = np.empty((3, 9, 9), np.float32)
                if var == 0:
                    p[:] = gray[:, None, None]
                else:
                    d = dirs[rng.integers(0, len(dirs))]
                    hi = cone_contrast(gray, d, var)
                    lo = cone_contrast(gray, tuple(-x for x in d), var)
                    for ch in range(3):
                        p[ch] = np.where(cb == 0, hi[ch], lo[ch])
                p[:, CENTER, CENTER] = test[:, None, None]
                X[i] = p
                p0 = p.copy(); p0[:, CENTER, CENTER] = gray[:, None, None]; X0[i] = p0
            r = cs_repr(net, X, dev).mean(0)
            r0 = cs_repr(net, X0, dev).mean(0)
            mags.append(np.linalg.norm(r - r0))
        res[str(var)] = float(np.mean(mags))
    return res


def run_munker(net, gray, dev, rng):
    res = {}
    for vn, vec in INDUCERS.items():
        n = 32
        stripe = cone_contrast(gray, vec, INDUCE)
        anti = cone_contrast(gray, tuple(-x for x in vec), INDUCE)
        X = np.empty((n, 3, 9, 9), np.float32)
        Xn = np.stack([build_patch(gray, gray, "uniform") for _ in range(n)])
        for i in range(n):
            p = np.empty((3, 9, 9), np.float32)
            for r in range(9):
                col = stripe if (r // 2) % 2 == 0 else anti
                for ch in range(3):
                    p[ch, r, :] = col[ch]
            p[:, CENTER, CENTER] = gray[:, None, None]
            X[i] = p
        r = cs_repr(net, X, dev).mean(0)
        r0 = cs_repr(net, Xn, dev).mean(0)
        Xd = np.stack([build_patch(cone_contrast(gray, vec, INDUCE), gray, "uniform") for _ in range(n)])
        sd = cs_repr(net, Xd, dev).mean(0) - r0
        sd /= (np.linalg.norm(sd) + 1e-9)
        res[vn] = float(np.dot(r - r0, sd))
    return res


def main():
    dev = get_device()
    b = Budget(BUDGET_S)
    R, by, is_real = get_bank()

    open(os.path.join(os.environ.get("RESULTS_DIR",
         os.path.join(os.path.dirname(__file__), "..", "..", "results")),
         "more_illusions.jsonl"), "w").close()

    rows = []; seed = 0
    while b.ok(margin=20):
        rng = np.random.default_rng(99_000 + seed)
        X, y, m = make_trials(R, by, rng, 4000)
        net = CSReadoutCNN(b=B_ANTAG).to(dev)
        train_cs(net, X, y, dev, seed)
        if accuracy(net, X, y, dev) < 0.7:
            seed += 1; continue
        gray = adapting_gray(R, rng)
        pr = np.random.default_rng(seed)
        rec = dict(seed=seed,
                   chubb=run_chubb(net, gray, R, dev, pr),
                   cornsweet=run_cornsweet(net, gray, dev),
                   mach=run_mach(net, gray, dev),
                   munker=run_munker(net, gray, dev, pr))
        jsonl_append("more_illusions.jsonl", rec)
        rows.append(rec); seed += 1
        if seed % 10 == 0:
            print(f"  {seed} nets, {b.frac() * 100:.0f}% budget")

    def meanfield(key, sub):
        vals = [r[key][sub] for r in rows if sub in r[key]]
        return float(np.mean(vals)) if vals else None

    chubb = {v: float(np.mean([r["chubb"][v] for r in rows])) for v in ["0.0", "0.15", "0.30", "0.45"]}
    summary = dict(source="FOSTER" if is_real else "SYN", n=len(rows),
                   chubb_saturation_vs_variance=chubb,
                   cornsweet_flank_diff={k: meanfield("cornsweet", k) for k in INDUCERS},
                   mach_overshoot={k: meanfield("mach", k) for k in INDUCERS},
                   munker_collinear_shift={k: meanfield("munker", k) for k in INDUCERS})
    save_json("more_illusions_summary.json", summary)

    print("\n===== Section 2.3 More Illusions =====")
    cv = list(chubb.values())
    print(f"I1 Chubb: {[(k, round(v, 3)) for k, v in chubb.items()]}")
    print(f"   -> {'DECREASES with variance' if cv[0] > cv[-1] else 'no contraction'}")
    cs_v = np.mean([v for v in summary["cornsweet_flank_diff"].values() if v])
    print(f"I2 Cornsweet: mean flank difference {cs_v:.3f}")
    mb = np.mean([v for v in summary["mach_overshoot"].values() if v])
    print(f"I3 Mach bands: mean overshoot {mb:.3f}")
    mk = np.mean([v for v in summary["munker_collinear_shift"].values() if v])
    print(f"I4 Munker-White: mean collinear shift {mk:+.3f}")


if __name__ == "__main__":
    main()
