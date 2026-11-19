"""
metrics.py — null-calibrated opponency metrics.

All experiments use these functions to score conv1 filters, so every result is
produced with the same metric. The threshold for "double-opponent" is calibrated
to the 95th percentile of the UNTRAINED-initialisation null distribution, which
excludes random-init structure by construction.
"""
import numpy as np
import torch

from .spectral import lms_to_opponent


def filter_scores(conv1_weight):
    """Per-filter (chromatic_power, double_opp_score) from a conv1 weight tensor.

    chromatic_power: mean ||rg, by|| over spatial positions — continuous, threshold-free.
    double_opp_score: chromatic_power × spatial sign-reversal fraction of the dominant axis.

    Args:
        conv1_weight: (K, 3, 3, 3) tensor or array — output-channel × in-channel × h × w

    Returns:
        chroma_pow: (K,) float array
        dscore:     (K,) float array
    """
    W = conv1_weight.detach().cpu().numpy() if hasattr(conv1_weight, "detach") else np.asarray(conv1_weight)
    chroma_pow, dscore = [], []
    for k in range(W.shape[0]):
        f = W[k]
        opp = lms_to_opponent(f.reshape(3, -1).T)  # (P, 3)
        rg, by = opp[:, 1], opp[:, 2]
        chroma = np.sqrt(rg ** 2 + by ** 2)
        axis = rg if np.abs(rg).sum() >= np.abs(by).sum() else by
        pos, neg = (axis > 0).sum(), (axis < 0).sum()
        sign_rev = min(pos, neg) / max(1, pos + neg)
        chroma_pow.append(float(chroma.mean()))
        dscore.append(float(chroma.mean() * sign_rev))
    return np.array(chroma_pow), np.array(dscore)


def untrained_null(dev, make_model_fn, k1=8, bottleneck=4, n=40):
    """95th-percentile double-opp threshold and mean chroma power over random inits.

    Args:
        make_model_fn: callable(k1, bottleneck, kind) → nn.Module

    Returns:
        (double_threshold_95pct, mean_chroma_power)
    """
    ds, cs = [], []
    for s in range(n):
        torch.manual_seed(900_000 + s)
        net = make_model_fn(k1=k1, bottleneck=bottleneck, kind="survival").to(dev)
        c, d = filter_scores(net.conv1.weight)
        ds.extend(d.tolist())
        cs.extend(c.tolist())
    return float(np.percentile(ds, 95)), float(np.mean(cs))


def opponency_report(conv1_weight):
    """Classify each filter as non-opponent / single-opponent / double-opponent.

    Uses a simple heuristic threshold (chroma > 1e-3, sign_reversal > 0.25).
    The null-calibrated filter_scores() is preferred for quantitative comparisons.
    """
    W = conv1_weight.detach().cpu().numpy() if hasattr(conv1_weight, "detach") else np.asarray(conv1_weight)
    out = []
    for k in range(W.shape[0]):
        f = W[k]
        opp = lms_to_opponent(f.reshape(3, -1).T)
        rg, by = opp[:, 1], opp[:, 2]
        chroma = np.sqrt(rg ** 2 + by ** 2)
        dominant = "rg" if np.abs(rg).sum() >= np.abs(by).sum() else "by"
        axis = rg if dominant == "rg" else by
        pos, neg = (axis > 0).sum(), (axis < 0).sum()
        sign_rev = min(pos, neg) / max(1, pos + neg)
        if sign_rev > 0.25 and chroma.mean() > 1e-3:
            kind = "double-opponent"
        elif chroma.mean() > 1e-3:
            kind = "single-opponent"
        else:
            kind = "non-opponent"
        out.append(dict(filter=int(k), kind=kind,
                        chroma=float(chroma.mean()), sign_reversal=float(sign_rev)))
    return out


def count_opponency(report):
    """Returns (n_single, n_double) from opponency_report output."""
    return (
        sum(r["kind"] == "single-opponent" for r in report),
        sum(r["kind"] == "double-opponent" for r in report),
    )
