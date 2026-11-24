"""Explicit descriptive metrics; independent units are networks or scenes."""
import numpy as np

TRANSFORM = np.array([[1, 1, 1], [1, -1, 0], [-1, -1, 2]]) / np.sqrt([3, 2, 6])[:, None]
CHROMATIC = TRANSFORM[1:]


def filter_metrics(weights, threshold=None):
    w = np.asarray(weights, dtype=float)
    if w.ndim != 4 or w.shape[1] != 3 or not np.isfinite(w).all():
        raise ValueError('Expected finite Kx3xHxW weights')
    c = np.einsum('ac,kchw->kahw', CHROMATIC, w).reshape(len(w), 2, -1)
    raw = (c*c).sum((1, 2))
    norm = raw/np.maximum((w*w).sum((1, 2, 3)), 1e-30)
    eigenvalues, vectors = np.linalg.eigh(np.einsum('kcp,kdp->kcd', c, c))
    coherence = np.clip((eigenvalues[:, 1]-eigenvalues[:, 0])/np.maximum(raw, 1e-30), 0, 1)
    axes = vectors[:, :, -1]
    projection = np.einsum('kc,kcp->kp', axes, c)
    balance = 1-np.abs(projection.sum(1))/np.maximum(np.abs(projection).sum(1), 1e-30)
    score = np.clip(norm*coherence*balance, 0, 1)
    angles = np.rad2deg(np.arctan2(axes[:, 1], axes[:, 0])) % 180
    angles[(norm < 1e-12) | (coherence < 1e-12)] = np.nan
    return dict(raw_chromatic_power=raw, normalized_chromatic_power=norm,
                axis_coherence=coherence, spatial_sign_balance=balance,
                double_opponency_score=score, preferred_axis_degrees=angles,
                preferred_axis_lms=axes @ CHROMATIC, null_threshold=threshold,
                double_opponent_fraction=None if threshold is None else float((score > threshold).mean()))


def network_summary(weights, threshold):
    m = filter_metrics(weights, threshold)
    result = {k: float(np.mean(m[k])) for k in ('raw_chromatic_power', 'normalized_chromatic_power', 'double_opponency_score')}
    result.update(double_opponent_fraction=m['double_opponent_fraction'], null_threshold=threshold,
                  n_filters=len(weights), per_filter=m, inference_unit='seed block, not filter')
    return result


def bootstrap(values, seed=0, n_boot=2000, unit='network seed'):
    v = np.array([x for x in values if x is not None and np.isfinite(x)], dtype=float)
    out = dict(mean=float(v.mean()) if len(v) else None, n=len(v), ci95=None, independent_unit=unit)
    if len(v) > 1:
        rng = np.random.default_rng(seed)
        out['ci95'] = np.quantile(rng.choice(v, (n_boot, len(v))).mean(1), [.025, .975]).tolist()
    return out


def spectral_grounding(bank, cones, illuminant):
    white = illuminant @ cones.T
    rows, pca = [], []
    for split, scenes in bank.scenes.items():
        for name, spectra in scenes:
            # Float32 response maps keep full-scene processing under the RSS limit.
            lms = np.einsum('hwl,cl->hwc', spectra, cones*illuminant, optimize=True)/white
            z = np.log(np.maximum(lms, 1e-8)) @ TRANSFORM.T
            for d in (1, 2, 4, 8, 16, 32, 64):
                rng = np.random.default_rng(20261119+d)
                if min(z.shape[:2]) <= 2*d:
                    continue
                r = rng.integers(d, z.shape[0]-d, 10000)
                c = rng.integers(d, z.shape[1]-d, 10000)
                a = z[r, c]
                b = z[r, c+d]
                ac, bc = a-a.mean(0), b-b.mean(0)
                corr = (ac*bc).sum(0)/np.maximum(np.linalg.norm(ac, axis=0)*np.linalg.norm(bc, axis=0), 1e-30)
                surround = (z[r-d,c,1:]+z[r+d,c,1:]+z[r,c-d,1:]+z[r,c+d,1:])/4
                intact = np.mean((a[:,1:]-surround)**2)
                shuffled = np.mean([np.mean((a[:,1:]-surround[rng.permutation(len(a))])**2) for _ in range(16)])
                rows.append(dict(scene=name, split=split, separation_pixels=d,
                    luminance_correlation=corr[0], lm_correlation=corr[1], s_lm_correlation=corr[2],
                    intact_mse=intact, shuffled_mse=shuffled, mse_improvement=shuffled-intact))
            subset = z.reshape(-1,3)[::max(1, z.shape[0]*z.shape[1]//10000)]
            covariance = np.cov(subset, rowvar=False)
            values, vectors = np.linalg.eigh(covariance[1:,1:])
            pca.append(dict(scene=name, covariance=covariance, chromatic_eigenvalues=values,
                            chromatic_axes=vectors, coordinates='white-normalized log-LMS orthonormal opponent coordinates'))
    summaries = {str(d): {key: bootstrap([r[key] for r in rows if r['separation_pixels'] == d], unit='scene')
        for key in ('luminance_correlation', 'lm_correlation', 's_lm_correlation', 'mse_improvement')}
        for d in (1, 2, 4, 8, 16, 32, 64)}
    return dict(per_scene=rows, pca=pca, summaries=summaries, source=bank.manifest,
                caveat='Observational, pixel-scale statistics; eight scenes are not eight independent ecosystems.')
