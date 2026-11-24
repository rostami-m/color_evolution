"""Historical amplitude-based weight score used alongside normalized metrics.

The score depends on filter magnitude and is not a physiological cell taxonomy.
A matched initialization percentile is a descriptive threshold, not a test that
eliminates random structure. Only the production-used scoring function remains.
"""
import numpy as np
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
