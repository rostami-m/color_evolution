# Numerical claims audit — 24 November 2026

Production run: `PRODUCTION_RUN`. Source files are read-only and SHA-256 recorded in `claims.json`. Values below are source-derived, not retyped from manuscript prose. No new experiments were run by this audit.

## Integrity and experiment status

{
  "checked_date": "2026-11-24",
  "source_run": "PRODUCTION_RUN",
  "queue_state": "completed",
  "queue_counts": {
    "completed": 2443
  },
  "queue_active": [],
  "source_hashes_checked": 43,
  "source_changed_or_missing": [],
  "checkpoint_count": 6870,
  "nonempty_checkpoints": 6870,
  "job_json_count": 16594,
  "latest_job_file_mtime_local": "2026-11-21T09:27:33.981624",
  "followup_status": "This integrity snapshot preceded the 24 November diagnostics; see scale_diagnostics/ for the subsequent saved-checkpoint experiments."
}

## Reporting constraints and unresolved follow-ups

- 27x27 was a planned threefold scale perturbation preserving an odd centered target (3x3 -> 9x9) and integer dilation control. It was not selected as the best-performing size or calibrated to human visual angle.
- Frozen primary endpoint is scale-by-objective difference in per-network fraction above a 200-network matched initialization null. No sample-size power guarantee or formal equivalence margin exists.
- Thirty seeds vary initial weights and selected prototypes under one fixed scene partition. Training scenes 1/2/4/5, validation 3/6, held-out test 7/8. All low-performing seeds retained.
- E5a default architectures and E5b default/synthetic settings reuse E1/E0 data records; reused controls are not additional independent networks.
- Local fields have a sparse 3x3 sampled receptive field; dilation3 spans a 7x7 footprint. The base final head has global access through whole-image pooling.
- Target boundary-access fractions are 8/9,32/81,72/81 for (target_width,dilation)=(3,1),(9,1),(9,3). Frame-padding exposure fractions are 32/81,104/729,288/729. This confound prevents unique attribution of learned differences to the true target boundary.
- As of the 22 November analysis, the exact repeat3/dilation3 identity was mathematical only. The 24 November saved-checkpoint diagnostics subsequently tested it numerically; see scale_diagnostics/. The production training arms still used separate dilation and coarse-noise controls.
- At the initial 24 November production audit, no later numerical followups existed. Subsequently we executed the separately frozen saved-checkpoint scale/padding diagnostics in scale_diagnostics/; those new outcomes are distinct from these production claims. Functional cone-specific opponency, controlled padding retraining, and matched human comparison remain proposed.
- Standard Cornsweet, Mach, and watercolor generators are not literal repeat3 scale pairs; one cannot infer their exact equality from the repetition identity.
- Utility probe physical BY range is [-0.056519,+0.010218], while imposed utility loci are [-0.2,0,+0.2]; endpoint maxima do not locate a global sensitivity optimum. Ecological stimuli are analytic proxies, not measured reflectance samples.
- Cornsweet prior measurement overlapped changed cusp pixels and used unsigned norm; Mach unsigned residual loses smoothing-versus-overshoot sign. Recovered original raw artifacts are insufficient to reconstruct the cause of every historical figure value.
- Watercolor can occur with open contours in related work. Open-contour persistence alone is not invalidation; the absent distant local response is the stronger limitation.
- E5g generated Planck-family axis is descriptive; Dress stimulus/calibration and original raw artifacts were not recovered. Remove unverified Dress and precise historical sensitivity-ratio claims.
- Broad-CCT E5b training covers 2500-30000 K and contains the nominal extrapolation bands; that arm is not a genuine out-of-training-range test.
- This is a controlled re-evaluation with explicit source/split/measurement corrections, not an exact numerical reproduction of missing historical runs.

## Core scale and objective results

**C001 — E0_synthetic/p27/classify: legacy_chromatic_power**

0.47879582 [0.44182552, 0.51554671], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition. Amplitude-based legacy filter score; opponent fraction/count uses its matched initialization-null threshold, not the historical hard-threshold opponency_report. Not biological cell classification or gain-invariant opponency.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/1/metrics/legacy_chromatic_power`.

**C002 — E0_synthetic/p27/classify: test_accuracy**

0.9331 [0.89706583, 0.9573], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition. Accuracy is a binary category endpoint, not a human color-constancy index.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/1/metrics/test_accuracy`.

**C003 — E0_synthetic/p9/classify: legacy_chromatic_power**

0.48756248 [0.45753817, 0.51962899], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition. Amplitude-based legacy filter score; opponent fraction/count uses its matched initialization-null threshold, not the historical hard-threshold opponency_report. Not biological cell classification or gain-invariant opponency.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/5/metrics/legacy_chromatic_power`.

**C004 — E0_synthetic/p9/classify: test_accuracy**

0.94993333 [0.93826583, 0.9606], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition. Accuracy is a binary category endpoint, not a human color-constancy index.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/5/metrics/test_accuracy`.

**C005 — E1/p27_coarse/untrained: legacy_chromatic_power**

0.1850942 [0.18114541, 0.18888591], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition. Amplitude-based legacy filter score; opponent fraction/count uses its matched initialization-null threshold, not the historical hard-threshold opponency_report. Not biological cell classification or gain-invariant opponency.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/8/metrics/legacy_chromatic_power`.

**C006 — E1/p27_coarse/untrained: legacy_count**

0.36666667 [0.13333333, 0.63333333], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition. Amplitude-based legacy filter score; opponent fraction/count uses its matched initialization-null threshold, not the historical hard-threshold opponency_report. Not biological cell classification or gain-invariant opponency.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/8/metrics/legacy_count`.

**C007 — E1/p27_coarse/untrained: double_opponency_score**

0.16461554 [0.15584739, 0.17338081], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/8/metrics/double_opponency_score`.

**C008 — E1/p27_coarse/untrained: double_opponent_fraction**

0.045833333 [0.025, 0.066666667], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/8/metrics/double_opponent_fraction`.

**C009 — E1/p27_coarse/untrained: normalized_chromatic_power**

0.6569351 [0.64168599, 0.67154901], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/8/metrics/normalized_chromatic_power`.

**C010 — E1/p27_coarse/classify: legacy_chromatic_power**

0.6102426 [0.55889845, 0.65893434], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition. Amplitude-based legacy filter score; opponent fraction/count uses its matched initialization-null threshold, not the historical hard-threshold opponency_report. Not biological cell classification or gain-invariant opponency.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/9/metrics/legacy_chromatic_power`.

**C011 — E1/p27_coarse/classify: legacy_count**

0.16666667 [0.033333333, 0.3], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition. Amplitude-based legacy filter score; opponent fraction/count uses its matched initialization-null threshold, not the historical hard-threshold opponency_report. Not biological cell classification or gain-invariant opponency.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/9/metrics/legacy_count`.

**C012 — E1/p27_coarse/classify: double_opponency_score**

0.044290339 [0.034029126, 0.056128619], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/9/metrics/double_opponency_score`.

**C013 — E1/p27_coarse/classify: double_opponent_fraction**

0.0125 [0, 0.025104167], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/9/metrics/double_opponent_fraction`.

**C014 — E1/p27_coarse/classify: normalized_chromatic_power**

0.65584803 [0.62608195, 0.68405628], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/9/metrics/normalized_chromatic_power`.

**C015 — E1/p27_coarse/classify: train_accuracy**

0.93420833 [0.90102458, 0.95444187], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/9/metrics/train_accuracy`.

**C016 — E1/p27_coarse/classify: validation_accuracy**

0.95620833 [0.92045729, 0.97854167], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/9/metrics/validation_accuracy`.

**C017 — E1/p27_coarse/classify: test_accuracy**

0.6329 [0.59159917, 0.67757083], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition. Accuracy is a binary category endpoint, not a human color-constancy index.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/9/metrics/test_accuracy`.

**C018 — E1/p27_coarse/classify: illuminant_extrapolation_accuracy**

0.67226667 [0.63646667, 0.70903333], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/9/metrics/illuminant_extrapolation_accuracy`.

**C019 — E1/p27_coarse/regress: legacy_chromatic_power**

0.47878529 [0.44333401, 0.51330142], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition. Amplitude-based legacy filter score; opponent fraction/count uses its matched initialization-null threshold, not the historical hard-threshold opponency_report. Not biological cell classification or gain-invariant opponency.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/10/metrics/legacy_chromatic_power`.

**C020 — E1/p27_coarse/regress: legacy_count**

0.23333333 [0, 0.56666667], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition. Amplitude-based legacy filter score; opponent fraction/count uses its matched initialization-null threshold, not the historical hard-threshold opponency_report. Not biological cell classification or gain-invariant opponency.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/10/metrics/legacy_count`.

**C021 — E1/p27_coarse/regress: double_opponency_score**

0.039900145 [0.028763224, 0.052857576], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/10/metrics/double_opponency_score`.

**C022 — E1/p27_coarse/regress: double_opponent_fraction**

0.0125 [0, 0.025104167], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/10/metrics/double_opponent_fraction`.

**C023 — E1/p27_coarse/regress: normalized_chromatic_power**

0.72432306 [0.69482276, 0.75367948], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/10/metrics/normalized_chromatic_power`.

**C024 — E1/p27_coarse/regress: test_r2**

-0.39539567 [-0.93072245, 0.0064496967], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/10/metrics/test_r2`.

**C025 — E1/p27_coarse/regress: test_rmse_kelvin**

7015.2842 [6166.2172, 8058.8833], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/10/metrics/test_rmse_kelvin`.

**C026 — E1/p27_coarse/shuffled: legacy_chromatic_power**

0.27762462 [0.25678032, 0.29979122], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition. Amplitude-based legacy filter score; opponent fraction/count uses its matched initialization-null threshold, not the historical hard-threshold opponency_report. Not biological cell classification or gain-invariant opponency.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/11/metrics/legacy_chromatic_power`.

**C027 — E1/p27_coarse/shuffled: legacy_count**

0.43333333 [0.23333333, 0.63333333], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition. Amplitude-based legacy filter score; opponent fraction/count uses its matched initialization-null threshold, not the historical hard-threshold opponency_report. Not biological cell classification or gain-invariant opponency.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/11/metrics/legacy_count`.

**C028 — E1/p27_coarse/shuffled: double_opponency_score**

0.070688006 [0.057980994, 0.084082466], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/11/metrics/double_opponency_score`.

**C029 — E1/p27_coarse/shuffled: double_opponent_fraction**

0.0083333333 [0, 0.020833333], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/11/metrics/double_opponent_fraction`.

**C030 — E1/p27_coarse/shuffled: normalized_chromatic_power**

0.59583023 [0.56145716, 0.63132113], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/11/metrics/normalized_chromatic_power`.

**C031 — E1/p27_dilated/untrained: legacy_chromatic_power**

0.1850942 [0.18114541, 0.18888591], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition. Amplitude-based legacy filter score; opponent fraction/count uses its matched initialization-null threshold, not the historical hard-threshold opponency_report. Not biological cell classification or gain-invariant opponency.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/12/metrics/legacy_chromatic_power`.

**C032 — E1/p27_dilated/untrained: legacy_count**

0.36666667 [0.13333333, 0.63333333], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition. Amplitude-based legacy filter score; opponent fraction/count uses its matched initialization-null threshold, not the historical hard-threshold opponency_report. Not biological cell classification or gain-invariant opponency.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/12/metrics/legacy_count`.

**C033 — E1/p27_dilated/untrained: double_opponency_score**

0.16461554 [0.15584739, 0.17338081], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/12/metrics/double_opponency_score`.

**C034 — E1/p27_dilated/untrained: double_opponent_fraction**

0.045833333 [0.025, 0.066666667], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/12/metrics/double_opponent_fraction`.

**C035 — E1/p27_dilated/untrained: normalized_chromatic_power**

0.6569351 [0.64168599, 0.67154901], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/12/metrics/normalized_chromatic_power`.

**C036 — E1/p27_dilated/classify: legacy_chromatic_power**

0.5943083 [0.54797043, 0.63756462], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition. Amplitude-based legacy filter score; opponent fraction/count uses its matched initialization-null threshold, not the historical hard-threshold opponency_report. Not biological cell classification or gain-invariant opponency.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/13/metrics/legacy_chromatic_power`.

**C037 — E1/p27_dilated/classify: legacy_count**

2.6333333 [1.9, 3.4333333], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition. Amplitude-based legacy filter score; opponent fraction/count uses its matched initialization-null threshold, not the historical hard-threshold opponency_report. Not biological cell classification or gain-invariant opponency.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/13/metrics/legacy_count`.

**C038 — E1/p27_dilated/classify: double_opponency_score**

0.084941791 [0.067155332, 0.10436148], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/13/metrics/double_opponency_score`.

**C039 — E1/p27_dilated/classify: double_opponent_fraction**

0.020833333 [0.0041666667, 0.0375], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/13/metrics/double_opponent_fraction`.

**C040 — E1/p27_dilated/classify: normalized_chromatic_power**

0.66140582 [0.63469191, 0.68570386], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/13/metrics/normalized_chromatic_power`.

**C041 — E1/p27_dilated/classify: train_accuracy**

0.941975 [0.90858312, 0.96170854], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/13/metrics/train_accuracy`.

**C042 — E1/p27_dilated/classify: validation_accuracy**

0.95179167 [0.91445729, 0.97662604], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/13/metrics/validation_accuracy`.

**C043 — E1/p27_dilated/classify: test_accuracy**

0.65733333 [0.61263333, 0.704635], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition. Accuracy is a binary category endpoint, not a human color-constancy index.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/13/metrics/test_accuracy`.

**C044 — E1/p27_dilated/classify: illuminant_extrapolation_accuracy**

0.69133333 [0.65429833, 0.7280675], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/13/metrics/illuminant_extrapolation_accuracy`.

**C045 — E1/p27_dilated/regress: legacy_chromatic_power**

0.48906538 [0.45051566, 0.52579417], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition. Amplitude-based legacy filter score; opponent fraction/count uses its matched initialization-null threshold, not the historical hard-threshold opponency_report. Not biological cell classification or gain-invariant opponency.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/14/metrics/legacy_chromatic_power`.

**C046 — E1/p27_dilated/regress: legacy_count**

0.26666667 [0.066666667, 0.53333333], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition. Amplitude-based legacy filter score; opponent fraction/count uses its matched initialization-null threshold, not the historical hard-threshold opponency_report. Not biological cell classification or gain-invariant opponency.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/14/metrics/legacy_count`.

**C047 — E1/p27_dilated/regress: double_opponency_score**

0.041727177 [0.030370368, 0.054135403], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/14/metrics/double_opponency_score`.

**C048 — E1/p27_dilated/regress: double_opponent_fraction**

0.0125 [0, 0.025104167], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/14/metrics/double_opponent_fraction`.

**C049 — E1/p27_dilated/regress: normalized_chromatic_power**

0.72657849 [0.69785278, 0.75479965], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/14/metrics/normalized_chromatic_power`.

**C050 — E1/p27_dilated/regress: test_r2**

-0.14722062 [-0.43961791, 0.094546131], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/14/metrics/test_r2`.

**C051 — E1/p27_dilated/regress: test_rmse_kelvin**

6530.0634 [5893.9671, 7249.3739], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/14/metrics/test_rmse_kelvin`.

**C052 — E1/p27_dilated/shuffled: legacy_chromatic_power**

0.26937384 [0.2503373, 0.2889954], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition. Amplitude-based legacy filter score; opponent fraction/count uses its matched initialization-null threshold, not the historical hard-threshold opponency_report. Not biological cell classification or gain-invariant opponency.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/15/metrics/legacy_chromatic_power`.

**C053 — E1/p27_dilated/shuffled: legacy_count**

0.6 [0.3, 0.93333333], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition. Amplitude-based legacy filter score; opponent fraction/count uses its matched initialization-null threshold, not the historical hard-threshold opponency_report. Not biological cell classification or gain-invariant opponency.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/15/metrics/legacy_count`.

**C054 — E1/p27_dilated/shuffled: double_opponency_score**

0.079609318 [0.066533875, 0.092886888], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/15/metrics/double_opponency_score`.

**C055 — E1/p27_dilated/shuffled: double_opponent_fraction**

0.0125 [0, 0.025], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/15/metrics/double_opponent_fraction`.

**C056 — E1/p27_dilated/shuffled: normalized_chromatic_power**

0.55277734 [0.51182794, 0.59313692], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/15/metrics/normalized_chromatic_power`.

**C057 — E1/p27_fixed/untrained: legacy_chromatic_power**

0.1850942 [0.18114541, 0.18888591], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition. Amplitude-based legacy filter score; opponent fraction/count uses its matched initialization-null threshold, not the historical hard-threshold opponency_report. Not biological cell classification or gain-invariant opponency.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/16/metrics/legacy_chromatic_power`.

**C058 — E1/p27_fixed/untrained: legacy_count**

0.36666667 [0.13333333, 0.63333333], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition. Amplitude-based legacy filter score; opponent fraction/count uses its matched initialization-null threshold, not the historical hard-threshold opponency_report. Not biological cell classification or gain-invariant opponency.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/16/metrics/legacy_count`.

**C059 — E1/p27_fixed/untrained: double_opponency_score**

0.16461554 [0.15584739, 0.17338081], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/16/metrics/double_opponency_score`.

**C060 — E1/p27_fixed/untrained: double_opponent_fraction**

0.045833333 [0.025, 0.066666667], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/16/metrics/double_opponent_fraction`.

**C061 — E1/p27_fixed/untrained: normalized_chromatic_power**

0.6569351 [0.64168599, 0.67154901], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/16/metrics/normalized_chromatic_power`.

**C062 — E1/p27_fixed/classify: legacy_chromatic_power**

0.64654188 [0.58894691, 0.70097315], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition. Amplitude-based legacy filter score; opponent fraction/count uses its matched initialization-null threshold, not the historical hard-threshold opponency_report. Not biological cell classification or gain-invariant opponency.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/17/metrics/legacy_chromatic_power`.

**C063 — E1/p27_fixed/classify: legacy_count**

0.2 [0.066666667, 0.36666667], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition. Amplitude-based legacy filter score; opponent fraction/count uses its matched initialization-null threshold, not the historical hard-threshold opponency_report. Not biological cell classification or gain-invariant opponency.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/17/metrics/legacy_count`.

**C064 — E1/p27_fixed/classify: double_opponency_score**

0.045604778 [0.034887943, 0.057870355], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/17/metrics/double_opponency_score`.

**C065 — E1/p27_fixed/classify: double_opponent_fraction**

0.0125 [0, 0.025104167], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/17/metrics/double_opponent_fraction`.

**C066 — E1/p27_fixed/classify: normalized_chromatic_power**

0.68205603 [0.65152346, 0.7117913], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/17/metrics/normalized_chromatic_power`.

**C067 — E1/p27_fixed/classify: train_accuracy**

0.94094167 [0.90781625, 0.96068354], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/17/metrics/train_accuracy`.

**C068 — E1/p27_fixed/classify: validation_accuracy**

0.95416667 [0.91883333, 0.9765], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/17/metrics/validation_accuracy`.

**C069 — E1/p27_fixed/classify: test_accuracy**

0.654 [0.60976333, 0.70166833], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition. Accuracy is a binary category endpoint, not a human color-constancy index.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/17/metrics/test_accuracy`.

**C070 — E1/p27_fixed/classify: illuminant_extrapolation_accuracy**

0.6874 [0.6478, 0.7272675], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/17/metrics/illuminant_extrapolation_accuracy`.

**C071 — E1/p27_fixed/regress: legacy_chromatic_power**

0.49311156 [0.45446917, 0.53117567], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition. Amplitude-based legacy filter score; opponent fraction/count uses its matched initialization-null threshold, not the historical hard-threshold opponency_report. Not biological cell classification or gain-invariant opponency.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/18/metrics/legacy_chromatic_power`.

**C072 — E1/p27_fixed/regress: legacy_count**

0.13333333 [0, 0.3], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition. Amplitude-based legacy filter score; opponent fraction/count uses its matched initialization-null threshold, not the historical hard-threshold opponency_report. Not biological cell classification or gain-invariant opponency.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/18/metrics/legacy_count`.

**C073 — E1/p27_fixed/regress: double_opponency_score**

0.034867042 [0.025369629, 0.0459673], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/18/metrics/double_opponency_score`.

**C074 — E1/p27_fixed/regress: double_opponent_fraction**

0.0083333333 [0, 0.020833333], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/18/metrics/double_opponent_fraction`.

**C075 — E1/p27_fixed/regress: normalized_chromatic_power**

0.73074817 [0.70214325, 0.7584743], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/18/metrics/normalized_chromatic_power`.

**C076 — E1/p27_fixed/regress: test_r2**

-0.43033904 [-0.99948311, -0.004512491], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/18/metrics/test_r2`.

**C077 — E1/p27_fixed/regress: test_rmse_kelvin**

7088.4181 [6229.7245, 8161.7866], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/18/metrics/test_rmse_kelvin`.

**C078 — E1/p27_fixed/shuffled: legacy_chromatic_power**

0.26968633 [0.24828876, 0.2928237], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition. Amplitude-based legacy filter score; opponent fraction/count uses its matched initialization-null threshold, not the historical hard-threshold opponency_report. Not biological cell classification or gain-invariant opponency.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/19/metrics/legacy_chromatic_power`.

**C079 — E1/p27_fixed/shuffled: legacy_count**

0.43333333 [0.2, 0.6675], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition. Amplitude-based legacy filter score; opponent fraction/count uses its matched initialization-null threshold, not the historical hard-threshold opponency_report. Not biological cell classification or gain-invariant opponency.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/19/metrics/legacy_count`.

**C080 — E1/p27_fixed/shuffled: double_opponency_score**

0.076256927 [0.062953973, 0.090021165], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/19/metrics/double_opponency_score`.

**C081 — E1/p27_fixed/shuffled: double_opponent_fraction**

0.0083333333 [0, 0.020833333], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/19/metrics/double_opponent_fraction`.

**C082 — E1/p27_fixed/shuffled: normalized_chromatic_power**

0.58814383 [0.55398053, 0.62228882], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/19/metrics/normalized_chromatic_power`.

**C083 — E1/p9_baseline/untrained: legacy_chromatic_power**

0.1850942 [0.18114541, 0.18888591], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition. Amplitude-based legacy filter score; opponent fraction/count uses its matched initialization-null threshold, not the historical hard-threshold opponency_report. Not biological cell classification or gain-invariant opponency.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/20/metrics/legacy_chromatic_power`.

**C084 — E1/p9_baseline/untrained: legacy_count**

0.36666667 [0.13333333, 0.63333333], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition. Amplitude-based legacy filter score; opponent fraction/count uses its matched initialization-null threshold, not the historical hard-threshold opponency_report. Not biological cell classification or gain-invariant opponency.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/20/metrics/legacy_count`.

**C085 — E1/p9_baseline/untrained: double_opponency_score**

0.16461554 [0.15584739, 0.17338081], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/20/metrics/double_opponency_score`.

**C086 — E1/p9_baseline/untrained: double_opponent_fraction**

0.045833333 [0.025, 0.066666667], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/20/metrics/double_opponent_fraction`.

**C087 — E1/p9_baseline/untrained: normalized_chromatic_power**

0.6569351 [0.64168599, 0.67154901], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/20/metrics/normalized_chromatic_power`.

**C088 — E1/p9_baseline/classify: legacy_chromatic_power**

0.55242048 [0.51135514, 0.59085838], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition. Amplitude-based legacy filter score; opponent fraction/count uses its matched initialization-null threshold, not the historical hard-threshold opponency_report. Not biological cell classification or gain-invariant opponency.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/21/metrics/legacy_chromatic_power`.

**C089 — E1/p9_baseline/classify: legacy_count**

3.1 [2.4333333, 3.8], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition. Amplitude-based legacy filter score; opponent fraction/count uses its matched initialization-null threshold, not the historical hard-threshold opponency_report. Not biological cell classification or gain-invariant opponency.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/21/metrics/legacy_count`.

**C090 — E1/p9_baseline/classify: double_opponency_score**

0.102706 [0.082862535, 0.12524813], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/21/metrics/double_opponency_score`.

**C091 — E1/p9_baseline/classify: double_opponent_fraction**

0.045833333 [0.016666667, 0.0875], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/21/metrics/double_opponent_fraction`.

**C092 — E1/p9_baseline/classify: normalized_chromatic_power**

0.65399642 [0.62569283, 0.67793637], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/21/metrics/normalized_chromatic_power`.

**C093 — E1/p9_baseline/classify: train_accuracy**

0.93444167 [0.90123333, 0.95463333], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/21/metrics/train_accuracy`.

**C094 — E1/p9_baseline/classify: validation_accuracy**

0.949875 [0.91241563, 0.97466667], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/21/metrics/validation_accuracy`.

**C095 — E1/p9_baseline/classify: test_accuracy**

0.65826667 [0.61259917, 0.7063675], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition. Accuracy is a binary category endpoint, not a human color-constancy index.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/21/metrics/test_accuracy`.

**C096 — E1/p9_baseline/classify: illuminant_extrapolation_accuracy**

0.68953333 [0.65286667, 0.72636667], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/21/metrics/illuminant_extrapolation_accuracy`.

**C097 — E1/p9_baseline/regress: legacy_chromatic_power**

0.47941458 [0.44316418, 0.51458931], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition. Amplitude-based legacy filter score; opponent fraction/count uses its matched initialization-null threshold, not the historical hard-threshold opponency_report. Not biological cell classification or gain-invariant opponency.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/22/metrics/legacy_chromatic_power`.

**C098 — E1/p9_baseline/regress: legacy_count**

0.43333333 [0.2, 0.7], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition. Amplitude-based legacy filter score; opponent fraction/count uses its matched initialization-null threshold, not the historical hard-threshold opponency_report. Not biological cell classification or gain-invariant opponency.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/22/metrics/legacy_count`.

**C099 — E1/p9_baseline/regress: double_opponency_score**

0.043812303 [0.032699853, 0.056052928], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/22/metrics/double_opponency_score`.

**C100 — E1/p9_baseline/regress: double_opponent_fraction**

0.016666667 [0.0041666667, 0.033333333], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/22/metrics/double_opponent_fraction`.

**C101 — E1/p9_baseline/regress: normalized_chromatic_power**

0.72614854 [0.69668541, 0.75434966], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/22/metrics/normalized_chromatic_power`.

**C102 — E1/p9_baseline/regress: test_r2**

-0.28054066 [-0.77709585, 0.072000873], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/22/metrics/test_r2`.

**C103 — E1/p9_baseline/regress: test_rmse_kelvin**

6749.877 [5981.3743, 7702.7981], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/22/metrics/test_rmse_kelvin`.

**C104 — E1/p9_baseline/shuffled: legacy_chromatic_power**

0.27554326 [0.25660031, 0.29559544], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition. Amplitude-based legacy filter score; opponent fraction/count uses its matched initialization-null threshold, not the historical hard-threshold opponency_report. Not biological cell classification or gain-invariant opponency.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/23/metrics/legacy_chromatic_power`.

**C105 — E1/p9_baseline/shuffled: legacy_count**

0.93333333 [0.6, 1.3], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition. Amplitude-based legacy filter score; opponent fraction/count uses its matched initialization-null threshold, not the historical hard-threshold opponency_report. Not biological cell classification or gain-invariant opponency.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/23/metrics/legacy_count`.

**C106 — E1/p9_baseline/shuffled: double_opponency_score**

0.080750672 [0.067655878, 0.094705273], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/23/metrics/double_opponency_score`.

**C107 — E1/p9_baseline/shuffled: double_opponent_fraction**

0.016666667 [0.0041666667, 0.033333333], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/23/metrics/double_opponent_fraction`.

**C108 — E1/p9_baseline/shuffled: normalized_chromatic_power**

0.56200544 [0.52651773, 0.59741107], n=30

Seed-bootstrap descriptive interval; 30 network/data seeds conditional on one fixed scene partition.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/groups/23/metrics/normalized_chromatic_power`.


## Paired core contrasts

**C109 — E1/p9_baseline: classify minus untrained: legacy_chromatic_power**

0.36732628 [0.32628109, 0.40555443], n=30

Paired seed difference; exploratory descriptive CI. A CI crossing zero does not establish equivalence.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/contrasts/20/metrics/legacy_chromatic_power`.

**C110 — E1/p9_baseline: classify minus untrained: normalized_chromatic_power**

-0.0029386773 [-0.032880893, 0.024349773], n=30

Paired seed difference; exploratory descriptive CI. A CI crossing zero does not establish equivalence.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/contrasts/20/metrics/normalized_chromatic_power`.

**C111 — E1/p9_baseline: classify minus untrained: double_opponency_score**

-0.06190954 [-0.081881234, -0.039201485], n=30

Paired seed difference; exploratory descriptive CI. A CI crossing zero does not establish equivalence.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/contrasts/20/metrics/double_opponency_score`.

**C112 — E1/p9_baseline: classify minus untrained: double_opponent_fraction**

0 [-0.0375, 0.045833333], n=30

Paired seed difference; exploratory descriptive CI. A CI crossing zero does not establish equivalence.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/contrasts/20/metrics/double_opponent_fraction`.

**C113 — E1/p9_baseline: classify minus regress: legacy_chromatic_power**

0.073005898 [0.043150106, 0.10377138], n=30

Paired seed difference; exploratory descriptive CI. A CI crossing zero does not establish equivalence.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/contrasts/22/metrics/legacy_chromatic_power`.

**C114 — E1/p9_baseline: classify minus regress: normalized_chromatic_power**

-0.072152122 [-0.10889041, -0.034825804], n=30

Paired seed difference; exploratory descriptive CI. A CI crossing zero does not establish equivalence.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/contrasts/22/metrics/normalized_chromatic_power`.

**C115 — E1/p9_baseline: classify minus regress: double_opponency_score**

0.058893695 [0.041128919, 0.079651838], n=30

Paired seed difference; exploratory descriptive CI. A CI crossing zero does not establish equivalence.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/contrasts/22/metrics/double_opponency_score`.

**C116 — E1/p9_baseline: classify minus regress: double_opponent_fraction**

0.029166667 [0, 0.070833333], n=30

Paired seed difference; exploratory descriptive CI. A CI crossing zero does not establish equivalence.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/contrasts/22/metrics/double_opponent_fraction`.

**C117 — E1/p9_baseline: shuffled minus untrained: legacy_chromatic_power**

0.090449063 [0.071752463, 0.11033331], n=30

Paired seed difference; exploratory descriptive CI. A CI crossing zero does not establish equivalence.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/contrasts/23/metrics/legacy_chromatic_power`.

**C118 — E1/p9_baseline: shuffled minus untrained: normalized_chromatic_power**

-0.094929657 [-0.1294671, -0.060448539], n=30

Paired seed difference; exploratory descriptive CI. A CI crossing zero does not establish equivalence.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/contrasts/23/metrics/normalized_chromatic_power`.

**C119 — E1/p9_baseline: shuffled minus untrained: double_opponency_score**

-0.083864865 [-0.096440268, -0.070787519], n=30

Paired seed difference; exploratory descriptive CI. A CI crossing zero does not establish equivalence.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/contrasts/23/metrics/double_opponency_score`.

**C120 — E1/p9_baseline: shuffled minus untrained: double_opponent_fraction**

-0.029166667 [-0.05, -0.0125], n=30

Paired seed difference; exploratory descriptive CI. A CI crossing zero does not establish equivalence.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/contrasts/23/metrics/double_opponent_fraction`.

**C121 — E1/classify: p27_fixed minus p9_baseline: legacy_count**

-2.9 [-3.5333333, -2.3], n=30

Paired seed difference; exploratory descriptive CI. A CI crossing zero does not establish equivalence.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/contrasts/24/metrics/legacy_count`.

**C122 — E1/classify: p27_fixed minus p9_baseline: double_opponency_score**

-0.057101219 [-0.078575043, -0.038857845], n=30

Paired seed difference; exploratory descriptive CI. A CI crossing zero does not establish equivalence.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/contrasts/24/metrics/double_opponency_score`.

**C123 — E1/classify: p27_fixed minus p9_baseline: double_opponent_fraction**

-0.033333333 [-0.075, -0.0083333333], n=30

Paired seed difference; exploratory descriptive CI. A CI crossing zero does not establish equivalence.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/contrasts/24/metrics/double_opponent_fraction`.

**C124 — E1/classify: p27_fixed minus p9_baseline: test_accuracy**

-0.0042666667 [-0.0253675, 0.015166667], n=30

Paired seed difference; exploratory descriptive CI. A CI crossing zero does not establish equivalence.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/contrasts/24/metrics/test_accuracy`.

**C125 — E1/classify: p27_dilated minus p9_baseline: legacy_count**

-0.46666667 [-0.9, -0.033333333], n=30

Paired seed difference; exploratory descriptive CI. A CI crossing zero does not establish equivalence.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/contrasts/25/metrics/legacy_count`.

**C126 — E1/classify: p27_dilated minus p9_baseline: double_opponency_score**

-0.017764206 [-0.029482149, -0.007760203], n=30

Paired seed difference; exploratory descriptive CI. A CI crossing zero does not establish equivalence.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/contrasts/25/metrics/double_opponency_score`.

**C127 — E1/classify: p27_dilated minus p9_baseline: double_opponent_fraction**

-0.025 [-0.066666667, 0], n=30

Paired seed difference; exploratory descriptive CI. A CI crossing zero does not establish equivalence.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/contrasts/25/metrics/double_opponent_fraction`.

**C128 — E1/classify: p27_dilated minus p9_baseline: test_accuracy**

-0.00093333333 [-0.013200833, 0.010366667], n=30

Paired seed difference; exploratory descriptive CI. A CI crossing zero does not establish equivalence.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/contrasts/25/metrics/test_accuracy`.

**C129 — E1/classify: p27_coarse minus p9_baseline: legacy_count**

-2.9333333 [-3.5666667, -2.3], n=30

Paired seed difference; exploratory descriptive CI. A CI crossing zero does not establish equivalence.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/contrasts/26/metrics/legacy_count`.

**C130 — E1/classify: p27_coarse minus p9_baseline: double_opponency_score**

-0.058415658 [-0.080404795, -0.039528075], n=30

Paired seed difference; exploratory descriptive CI. A CI crossing zero does not establish equivalence.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/contrasts/26/metrics/double_opponency_score`.

**C131 — E1/classify: p27_coarse minus p9_baseline: double_opponent_fraction**

-0.033333333 [-0.075, -0.0083333333], n=30

Paired seed difference; exploratory descriptive CI. A CI crossing zero does not establish equivalence.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/contrasts/26/metrics/double_opponent_fraction`.

**C132 — E1/classify: p27_coarse minus p9_baseline: test_accuracy**

-0.025366667 [-0.052000833, -0.00039916667], n=30

Paired seed difference; exploratory descriptive CI. A CI crossing zero does not establish equivalence.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/contrasts/26/metrics/test_accuracy`.

**C133 — E1/classify: p27_dilated minus p27_fixed: legacy_count**

2.4333333 [1.7333333, 3.1666667], n=30

Paired seed difference; exploratory descriptive CI. A CI crossing zero does not establish equivalence.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/contrasts/27/metrics/legacy_count`.

**C134 — E1/classify: p27_dilated minus p27_fixed: double_opponency_score**

0.039337013 [0.022020542, 0.058488203], n=30

Paired seed difference; exploratory descriptive CI. A CI crossing zero does not establish equivalence.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/contrasts/27/metrics/double_opponency_score`.

**C135 — E1/classify: p27_dilated minus p27_fixed: double_opponent_fraction**

0.0083333333 [0, 0.020833333], n=30

Paired seed difference; exploratory descriptive CI. A CI crossing zero does not establish equivalence.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/contrasts/27/metrics/double_opponent_fraction`.

**C136 — E1/classify: p27_dilated minus p27_fixed: test_accuracy**

0.0033333333 [-0.015666667, 0.024566667], n=30

Paired seed difference; exploratory descriptive CI. A CI crossing zero does not establish equivalence.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/contrasts/27/metrics/test_accuracy`.

**C137 — E1/classify: p27_coarse minus p27_fixed: legacy_count**

-0.033333333 [-0.1, 0], n=30

Paired seed difference; exploratory descriptive CI. A CI crossing zero does not establish equivalence.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/contrasts/28/metrics/legacy_count`.

**C138 — E1/classify: p27_coarse minus p27_fixed: double_opponency_score**

-0.001314439 [-0.0050645174, 0.0016483636], n=30

Paired seed difference; exploratory descriptive CI. A CI crossing zero does not establish equivalence.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/contrasts/28/metrics/double_opponency_score`.

**C139 — E1/classify: p27_coarse minus p27_fixed: double_opponent_fraction**

0 [0, 0], n=30

Paired seed difference; exploratory descriptive CI. A CI crossing zero does not establish equivalence.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/contrasts/28/metrics/double_opponent_fraction`.

**C140 — E1/classify: p27_coarse minus p27_fixed: test_accuracy**

-0.0211 [-0.042134167, -0.0044333333], n=30

Paired seed difference; exploratory descriptive CI. A CI crossing zero does not establish equivalence.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/contrasts/28/metrics/test_accuracy`.


## Frozen confirmatory endpoint

**C141 — p27_coarse: classifier minus regressor opponent fraction**

0 [0, 0], n=30; sign_test_two_sided_p=1; holm_p=1

Frozen two-sided sign test with Holm adjustment. The primary scale-by-objective interaction is inconclusive; positive exploratory endpoints do not replace it.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/frozen_primary_comparisons/0`.

**C142 — p27_dilated: classifier minus regressor opponent fraction**

0.0083333333 [0, 0.020833333], n=30; sign_test_two_sided_p=0.5; holm_p=1

Frozen two-sided sign test with Holm adjustment. The primary scale-by-objective interaction is inconclusive; positive exploratory endpoints do not replace it.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/frozen_primary_comparisons/1`.

**C143 — p27_fixed: classifier minus regressor opponent fraction**

0.0041666667 [0, 0.0125], n=30; sign_test_two_sided_p=1; holm_p=1

Frozen two-sided sign test with Holm adjustment. The primary scale-by-objective interaction is inconclusive; positive exploratory endpoints do not replace it.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/frozen_primary_comparisons/2`.

**C144 — p9_baseline: classifier minus regressor opponent fraction**

0.029166667 [0, 0.070833333], n=30; sign_test_two_sided_p=0.21875; holm_p=1

Frozen two-sided sign test with Holm adjustment. The primary scale-by-objective interaction is inconclusive; positive exploratory endpoints do not replace it.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/frozen_primary_comparisons/3`.

**C145 — PRIMARY_scale_by_objective: (classifier minus regressor fraction at 27 fixed) minus (classifier minus regressor fraction at 9 baseline)**

-0.025 [-0.066666667, 0.0083333333], n=30; sign_test_two_sided_p=0.453125; holm_p=1

Frozen two-sided sign test with Holm adjustment. The primary scale-by-objective interaction is inconclusive; positive exploratory endpoints do not replace it.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/primary/primary_analysis.json`; JSON pointer `/frozen_primary_comparisons/4`.


## Signed induction and antagonism

**C146 — E1/p9_baseline/classify/BY/simultaneous_odd_readout_shift**

0.061580124 [0.052609581, 0.070065736], n=29; signs +29/-0/0=0

Positive calibrated shift is assimilation; negative is contrast. Denominator n excludes undefined calibration, not low-performing seeds. Local and global measures differ.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/audit.json`; JSON pointer `/illusions/E1~1p9_baseline~1classify/axes/BY/simultaneous_odd_readout_shift`.

**C147 — E1/p9_baseline/classify/BY/simultaneous_odd_local_target_shift**

0.030127391 [0.024945922, 0.034681144], n=28; signs +26/-1/0=1

Positive calibrated shift is assimilation; negative is contrast. Denominator n excludes undefined calibration, not low-performing seeds. Local and global measures differ.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/audit.json`; JSON pointer `/illusions/E1~1p9_baseline~1classify/axes/BY/simultaneous_odd_local_target_shift`.

**C148 — E1/p9_baseline/classify/BY/simultaneous_odd_local_interior_shift**

0 [0, 0], n=28; signs +0/-0/0=28

Positive calibrated shift is assimilation; negative is contrast. Denominator n excludes undefined calibration, not low-performing seeds. Local and global measures differ.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/audit.json`; JSON pointer `/illusions/E1~1p9_baseline~1classify/axes/BY/simultaneous_odd_local_interior_shift`.

**C149 — E1/p27_fixed/classify/BY/simultaneous_odd_readout_shift**

0.040429782 [0.038147038, 0.042054819], n=28; signs +28/-0/0=0

Positive calibrated shift is assimilation; negative is contrast. Denominator n excludes undefined calibration, not low-performing seeds. Local and global measures differ.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/audit.json`; JSON pointer `/illusions/E1~1p27_fixed~1classify/axes/BY/simultaneous_odd_readout_shift`.

**C150 — E1/p27_fixed/classify/BY/simultaneous_odd_local_target_shift**

0.019444375 [0.017710483, 0.020704188], n=28; signs +28/-0/0=0

Positive calibrated shift is assimilation; negative is contrast. Denominator n excludes undefined calibration, not low-performing seeds. Local and global measures differ.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/audit.json`; JSON pointer `/illusions/E1~1p27_fixed~1classify/axes/BY/simultaneous_odd_local_target_shift`.

**C151 — E1/p27_fixed/classify/BY/simultaneous_odd_local_interior_shift**

0 [0, 0], n=28; signs +0/-0/0=28

Positive calibrated shift is assimilation; negative is contrast. Denominator n excludes undefined calibration, not low-performing seeds. Local and global measures differ.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/audit.json`; JSON pointer `/illusions/E1~1p27_fixed~1classify/axes/BY/simultaneous_odd_local_interior_shift`.

**C152 — E1/p27_dilated/classify/BY/simultaneous_odd_readout_shift**

0.065296906 [0.057228204, 0.073079213], n=27; signs +27/-0/0=0

Positive calibrated shift is assimilation; negative is contrast. Denominator n excludes undefined calibration, not low-performing seeds. Local and global measures differ.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/audit.json`; JSON pointer `/illusions/E1~1p27_dilated~1classify/axes/BY/simultaneous_odd_readout_shift`.

**C153 — E1/p27_dilated/classify/BY/simultaneous_odd_local_target_shift**

0.033140108 [0.028838553, 0.037255867], n=27; signs +27/-0/0=0

Positive calibrated shift is assimilation; negative is contrast. Denominator n excludes undefined calibration, not low-performing seeds. Local and global measures differ.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/audit.json`; JSON pointer `/illusions/E1~1p27_dilated~1classify/axes/BY/simultaneous_odd_local_target_shift`.

**C154 — E1/p27_dilated/classify/BY/simultaneous_odd_local_interior_shift**

0 [0, 0], n=27; signs +0/-0/0=27

Positive calibrated shift is assimilation; negative is contrast. Denominator n excludes undefined calibration, not low-performing seeds. Local and global measures differ.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/audit.json`; JSON pointer `/illusions/E1~1p27_dilated~1classify/axes/BY/simultaneous_odd_local_interior_shift`.

**C155 — E1/p27_coarse/classify/BY/simultaneous_odd_readout_shift**

0.040225671 [0.038410105, 0.041789056], n=28; signs +28/-0/0=0

Positive calibrated shift is assimilation; negative is contrast. Denominator n excludes undefined calibration, not low-performing seeds. Local and global measures differ.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/audit.json`; JSON pointer `/illusions/E1~1p27_coarse~1classify/axes/BY/simultaneous_odd_readout_shift`.

**C156 — E1/p27_coarse/classify/BY/simultaneous_odd_local_target_shift**

0.019073399 [0.017193789, 0.020516036], n=28; signs +27/-0/0=1

Positive calibrated shift is assimilation; negative is contrast. Denominator n excludes undefined calibration, not low-performing seeds. Local and global measures differ.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/audit.json`; JSON pointer `/illusions/E1~1p27_coarse~1classify/axes/BY/simultaneous_odd_local_target_shift`.

**C157 — E1/p27_coarse/classify/BY/simultaneous_odd_local_interior_shift**

0 [0, 0], n=28; signs +0/-0/0=28

Positive calibrated shift is assimilation; negative is contrast. Denominator n excludes undefined calibration, not low-performing seeds. Local and global measures differ.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/audit.json`; JSON pointer `/illusions/E1~1p27_coarse~1classify/axes/BY/simultaneous_odd_local_interior_shift`.

**C158 — E3/p9_learned_b_0/classify: learned b**

0.40114278 [0.36247015, 0.43635067], n=30; signs +30/-0/0=0

Unconstrained b positive in all 30 seeds; supports learning within the explicitly designed center-minus-b-times-ring readout family.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/audit.json`; JSON pointer `/illusions/E3~1p9_learned_b_0~1classify/b`.

**C159 — E3/p9_learned_b_0/classify/BY/simultaneous_odd_readout_shift**

-0.041854132 [-0.04799909, -0.036113492], n=27; signs +0/-27/0=0

Calibrated feature/readout response, not fitted human appearance. Missing zero calibration slopes are undefined; global pooling is not spatial filling-in.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/audit.json`; JSON pointer `/illusions/E3~1p9_learned_b_0~1classify/axes/BY/simultaneous_odd_readout_shift`.

**C160 — E3/p9_learned_b_0/classify/BY/simultaneous_odd_local_target_shift**

0.024501932 [0.017903546, 0.030596256], n=27; signs +22/-5/0=0

Calibrated feature/readout response, not fitted human appearance. Missing zero calibration slopes are undefined; global pooling is not spatial filling-in.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/audit.json`; JSON pointer `/illusions/E3~1p9_learned_b_0~1classify/axes/BY/simultaneous_odd_local_target_shift`.

**C161 — E3/p9_learned_b_0/classify/RG/simultaneous_odd_readout_shift**

-0.04692955 [-0.10137194, -0.0016222596], n=28; signs +15/-13/0=0

Calibrated feature/readout response, not fitted human appearance. Missing zero calibration slopes are undefined; global pooling is not spatial filling-in.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/audit.json`; JSON pointer `/illusions/E3~1p9_learned_b_0~1classify/axes/RG/simultaneous_odd_readout_shift`.

**C162 — E3/p9_learned_b_0/classify/RG/simultaneous_odd_local_target_shift**

0.054764676 [0.035387196, 0.073374207], n=28; signs +24/-3/0=1

Calibrated feature/readout response, not fitted human appearance. Missing zero calibration slopes are undefined; global pooling is not spatial filling-in.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/audit.json`; JSON pointer `/illusions/E3~1p9_learned_b_0~1classify/axes/RG/simultaneous_odd_local_target_shift`.

**C163 — E3/p27_learned_b_0/classify: learned b**

0.27088036 [0.24584785, 0.2942302], n=30; signs +30/-0/0=0

Unconstrained b positive in all 30 seeds; supports learning within the explicitly designed center-minus-b-times-ring readout family.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/audit.json`; JSON pointer `/illusions/E3~1p27_learned_b_0~1classify/b`.

**C164 — E3/p27_learned_b_0/classify/BY/simultaneous_odd_readout_shift**

-0.028457245 [-0.035374853, -0.023236432], n=27; signs +0/-27/0=0

Calibrated feature/readout response, not fitted human appearance. Missing zero calibration slopes are undefined; global pooling is not spatial filling-in.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/audit.json`; JSON pointer `/illusions/E3~1p27_learned_b_0~1classify/axes/BY/simultaneous_odd_readout_shift`.

**C165 — E3/p27_learned_b_0/classify/BY/simultaneous_odd_local_target_shift**

0.014641866 [0.0082801965, 0.018404358], n=27; signs +26/-1/0=0

Calibrated feature/readout response, not fitted human appearance. Missing zero calibration slopes are undefined; global pooling is not spatial filling-in.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/audit.json`; JSON pointer `/illusions/E3~1p27_learned_b_0~1classify/axes/BY/simultaneous_odd_local_target_shift`.

**C166 — E3/p27_learned_b_0/classify/RG/simultaneous_odd_readout_shift**

-0.020897536 [-0.025292128, -0.016202407], n=27; signs +2/-25/0=0

Calibrated feature/readout response, not fitted human appearance. Missing zero calibration slopes are undefined; global pooling is not spatial filling-in.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/audit.json`; JSON pointer `/illusions/E3~1p27_learned_b_0~1classify/axes/RG/simultaneous_odd_readout_shift`.

**C167 — E3/p27_learned_b_0/classify/RG/simultaneous_odd_local_target_shift**

0.02138119 [0.019842328, 0.023023255], n=27; signs +27/-0/0=0

Calibrated feature/readout response, not fitted human appearance. Missing zero calibration slopes are undefined; global pooling is not spatial filling-in.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/audit.json`; JSON pointer `/illusions/E3~1p27_learned_b_0~1classify/axes/RG/simultaneous_odd_local_target_shift`.


## Natural-context controls

**C168 — shuffle_base: test_accuracy_paired_minus_intact**

0.0094 [-0.0055, 0.0254], n=30; signs +17/-12/0=1

Texture controls do not preserve naturally adjacent target/surround material pairs: the independently selected central target is inserted into the crop.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/audit.json`; JSON pointer `/context/shuffle_base/test_accuracy_paired_minus_intact`.

**C169 — boundary_shuffle_base: test_accuracy_paired_minus_intact**

0.0079 [-0.0071341667, 0.024066667], n=30; signs +15/-13/0=2

Texture controls do not preserve naturally adjacent target/surround material pairs: the independently selected central target is inserted into the crop.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/audit.json`; JSON pointer `/context/boundary_shuffle_base/test_accuracy_paired_minus_intact`.

**C170 — shuffle_center_only: test_accuracy_paired_minus_intact**

-0.0085333333 [-0.028934167, 0.0089333333], n=30; signs +15/-14/0=1

Texture controls do not preserve naturally adjacent target/surround material pairs: the independently selected central target is inserted into the crop.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/audit.json`; JSON pointer `/context/shuffle_center_only/test_accuracy_paired_minus_intact`.

**C171 — boundary_shuffle_center_only: test_accuracy_paired_minus_intact**

0 [0, 0], n=30; signs +0/-0/0=30

Texture controls do not preserve naturally adjacent target/surround material pairs: the independently selected central target is inserted into the crop.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/audit.json`; JSON pointer `/context/boundary_shuffle_center_only/test_accuracy_paired_minus_intact`.


## Utility and proxy limitations

**C172 — E4/frequency: sensitivity_peak_by**

0.048816879 [0.012765511, 0.083009292], n=27; signs +16/-6/0=5

Complete finite, nonflat seed profiles across all loci. Raw versus per-location RMS-normalized functions differ. Probe range fails to span most utility loci; no global optimum or human JND is established.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/audit.json`; JSON pointer `/utility_slopes/E4~1frequency/sensitivity_peak_by`.

**C173 — E4/frequency: normalized_sensitivity_peak_by**

-0.060557647 [-0.087746795, -0.034192413], n=27; signs +1/-17/0=9

Complete finite, nonflat seed profiles across all loci. Raw versus per-location RMS-normalized functions differ. Probe range fails to span most utility loci; no global optimum or human JND is established.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/audit.json`; JSON pointer `/utility_slopes/E4~1frequency/normalized_sensitivity_peak_by`.

**C174 — E4/loss: sensitivity_peak_by**

0.038106003 [0.0053502887, 0.068796783], n=27; signs +17/-6/0=4

Complete finite, nonflat seed profiles across all loci. Raw versus per-location RMS-normalized functions differ. Probe range fails to span most utility loci; no global optimum or human JND is established.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/audit.json`; JSON pointer `/utility_slopes/E4~1loss/sensitivity_peak_by`.

**C175 — E4/loss: normalized_sensitivity_peak_by**

-0.030896759 [-0.056026123, -0.0063853302], n=27; signs +2/-13/0=12

Complete finite, nonflat seed profiles across all loci. Raw versus per-location RMS-normalized functions differ. Probe range fails to span most utility loci; no global optimum or human JND is established.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/audit.json`; JSON pointer `/utility_slopes/E4~1loss/normalized_sensitivity_peak_by`.

**C176 — E4/both: sensitivity_peak_by**

0.032750564 [-0.0051546093, 0.068178848], n=27; signs +15/-9/0=3

Complete finite, nonflat seed profiles across all loci. Raw versus per-location RMS-normalized functions differ. Probe range fails to span most utility loci; no global optimum or human JND is established.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/audit.json`; JSON pointer `/utility_slopes/E4~1both/sensitivity_peak_by`.

**C177 — E4/both: normalized_sensitivity_peak_by**

-0.083215271 [-0.11328812, -0.051489449], n=27; signs +3/-21/0=3

Complete finite, nonflat seed profiles across all loci. Raw versus per-location RMS-normalized functions differ. Probe range fails to span most utility loci; no global optimum or human JND is established.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/audit.json`; JSON pointer `/utility_slopes/E4~1both/normalized_sensitivity_peak_by`.

**C178 — E4_proxy/loss: sensitivity_peak_by**

0.074322475 [0.0060930707, 0.14044742], n=29; signs +20/-7/0=2

Complete finite, nonflat seed profiles across all loci. Raw versus per-location RMS-normalized functions differ. Probe range fails to span most utility loci; no global optimum or human JND is established.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/audit.json`; JSON pointer `/utility_slopes/E4_proxy~1loss/sensitivity_peak_by`.

**C179 — E4_proxy/loss: normalized_sensitivity_peak_by**

-0.038943198 [-0.097511025, 0.016502317], n=28; signs +5/-7/0=16

Complete finite, nonflat seed profiles across all loci. Raw versus per-location RMS-normalized functions differ. Probe range fails to span most utility loci; no global optimum or human JND is established.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/audit.json`; JSON pointer `/utility_slopes/E4_proxy~1loss/normalized_sensitivity_peak_by`.


## Cardinal and environmental alignment

**C180 — p9_baseline/classify: log_lms_distance**

18.419314 [15.976038, 20.875101], n=30; signs +30/-0/0=0

Nearest cardinal angle in declared log-cone convention; network-level seed uncertainty. Category-task specificity requires shuffled comparison.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/audit.json`; JSON pointer `/cardinals/p9_baseline~1classify/log_lms_distance`.

**C181 — p9_baseline/classify: paired_change_vs_untrained**

-3.7319545 [-6.0681956, -1.3334581], n=30; signs +8/-22/0=0

Nearest cardinal angle in declared log-cone convention; network-level seed uncertainty. Category-task specificity requires shuffled comparison.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/audit.json`; JSON pointer `/cardinals/p9_baseline~1classify/paired_change_vs_untrained`.

**C182 — p9_baseline/untrained: log_lms_distance**

22.151268 [20.762939, 23.429301], n=30; signs +30/-0/0=0

Nearest cardinal angle in declared log-cone convention; network-level seed uncertainty. Category-task specificity requires shuffled comparison.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/audit.json`; JSON pointer `/cardinals/p9_baseline~1untrained/log_lms_distance`.

**C183 — p9_baseline/untrained: paired_change_vs_untrained**

0 [0, 0], n=30; signs +0/-0/0=30

Nearest cardinal angle in declared log-cone convention; network-level seed uncertainty. Category-task specificity requires shuffled comparison.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/audit.json`; JSON pointer `/cardinals/p9_baseline~1untrained/paired_change_vs_untrained`.

**C184 — p9_baseline/shuffled: log_lms_distance**

20.150746 [18.500288, 21.761565], n=30; signs +30/-0/0=0

Nearest cardinal angle in declared log-cone convention; network-level seed uncertainty. Category-task specificity requires shuffled comparison.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/audit.json`; JSON pointer `/cardinals/p9_baseline~1shuffled/log_lms_distance`.

**C185 — p9_baseline/shuffled: paired_change_vs_untrained**

-2.0005223 [-3.7086618, -0.27043165], n=30; signs +12/-18/0=0

Nearest cardinal angle in declared log-cone convention; network-level seed uncertainty. Category-task specificity requires shuffled comparison.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/audit.json`; JSON pointer `/cardinals/p9_baseline~1shuffled/paired_change_vs_untrained`.

**C186 — p27_fixed/classify: log_lms_distance**

20.352782 [17.932163, 22.654974], n=30; signs +30/-0/0=0

Nearest cardinal angle in declared log-cone convention; network-level seed uncertainty. Category-task specificity requires shuffled comparison.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/audit.json`; JSON pointer `/cardinals/p27_fixed~1classify/log_lms_distance`.

**C187 — p27_fixed/classify: paired_change_vs_untrained**

-1.7984859 [-4.2405058, 0.6313819], n=30; signs +11/-19/0=0

Nearest cardinal angle in declared log-cone convention; network-level seed uncertainty. Category-task specificity requires shuffled comparison.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/audit.json`; JSON pointer `/cardinals/p27_fixed~1classify/paired_change_vs_untrained`.

**C188 — p27_fixed/untrained: log_lms_distance**

22.151268 [20.762939, 23.429301], n=30; signs +30/-0/0=0

Nearest cardinal angle in declared log-cone convention; network-level seed uncertainty. Category-task specificity requires shuffled comparison.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/audit.json`; JSON pointer `/cardinals/p27_fixed~1untrained/log_lms_distance`.

**C189 — p27_fixed/untrained: paired_change_vs_untrained**

0 [0, 0], n=30; signs +0/-0/0=30

Nearest cardinal angle in declared log-cone convention; network-level seed uncertainty. Category-task specificity requires shuffled comparison.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/audit.json`; JSON pointer `/cardinals/p27_fixed~1untrained/paired_change_vs_untrained`.

**C190 — p27_fixed/shuffled: log_lms_distance**

19.965022 [18.10431, 21.801059], n=30; signs +30/-0/0=0

Nearest cardinal angle in declared log-cone convention; network-level seed uncertainty. Category-task specificity requires shuffled comparison.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/audit.json`; JSON pointer `/cardinals/p27_fixed~1shuffled/log_lms_distance`.

**C191 — p27_fixed/shuffled: paired_change_vs_untrained**

-2.1862459 [-4.2971715, 0.053957714], n=30; signs +9/-21/0=0

Nearest cardinal angle in declared log-cone convention; network-level seed uncertainty. Category-task specificity requires shuffled comparison.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/audit.json`; JSON pointer `/cardinals/p27_fixed~1shuffled/paired_change_vs_untrained`.

**C192 — Natural scenes, separation 1px: lm_correlation**

0.93141136 [0.89087735, 0.96628218], n=8

Eight scenes under a fixed generated 6500 K illuminant; bootstrap unit is scene. Pixel separation is not visual angle.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/audit.json`; JSON pointer `/grounding/spatial/1/lm_correlation`.

**C193 — Natural scenes, separation 1px: s_lm_correlation**

0.9352423 [0.89413239, 0.967398], n=8

Eight scenes under a fixed generated 6500 K illuminant; bootstrap unit is scene. Pixel separation is not visual angle.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/audit.json`; JSON pointer `/grounding/spatial/1/s_lm_correlation`.

**C194 — Natural scenes, separation 64px: lm_correlation**

0.32337096 [0.25296022, 0.39427795], n=8

Eight scenes under a fixed generated 6500 K illuminant; bootstrap unit is scene. Pixel separation is not visual angle.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/audit.json`; JSON pointer `/grounding/spatial/64/lm_correlation`.

**C195 — Natural scenes, separation 64px: s_lm_correlation**

0.3785766 [0.27095741, 0.49007083], n=8

Eight scenes under a fixed generated 6500 K illuminant; bootstrap unit is scene. Pixel separation is not visual angle.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/audit.json`; JSON pointer `/grounding/spatial/64/s_lm_correlation`.

**C196 — Scene PCA nearest cardinal distance**

6.6313425 [4.1143212, 8.9523191], n=8; signs +8/-0/0=0

Environmental descriptive axis, not proof of learned task mechanism.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/audit.json`; JSON pointer `/grounding/pca_cardinal_distance`.

**C197 — Planck-family dominant chromatic axis in degrees**

100.01093264548268

Generated Planck curves, not measured daylight; no calibrated Dress experiment was recovered.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/audit.json`; JSON pointer `/daylight/dominant_axis_degrees`.

**C201 — p9_baseline: classifier-minus-shuffled cardinal angle**

-1.7314322 [-4.7667803, 1.3686218], n=30; signs +13/-17/0=0

CIs cross zero; no clear category-specific alignment advantage over the matched shuffled control.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/additional_audit.json`; JSON pointer `/cardinal_classify_minus_shuffled/p9_baseline`.

**C202 — p27_fixed: classifier-minus-shuffled cardinal angle**

0.38775995 [-2.6635388, 3.4664066], n=30; signs +14/-16/0=0

CIs cross zero; no clear category-specific alignment advantage over the matched shuffled control.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/additional_audit.json`; JSON pointer `/cardinal_classify_minus_shuffled/p27_fixed`.

**C203 — p27_dilated: classifier-minus-shuffled cardinal angle**

0.27748594 [-2.662662, 3.2475222], n=30; signs +14/-16/0=0

CIs cross zero; no clear category-specific alignment advantage over the matched shuffled control.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/additional_audit.json`; JSON pointer `/cardinal_classify_minus_shuffled/p27_dilated`.

**C204 — p27_coarse: classifier-minus-shuffled cardinal angle**

-1.793448 [-4.6130376, 1.0075369], n=30; signs +13/-17/0=0

CIs cross zero; no clear category-specific alignment advantage over the matched shuffled control.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/additional_audit.json`; JSON pointer `/cardinal_classify_minus_shuffled/p27_coarse`.


## Signed illusion limitations

**C198 — All far-field probe completeness checks**

{"total_networks":2280,"cornsweet_finite":18909,"cornsweet_max_abs":6.776263578034403e-21,"cornsweet_undefined":1611,"watercolor_finite":25212,"watercolor_max_abs":0.0}

Values count repeated axes/probes, not independent networks. Local far watercolor exactly zero; Cornsweet numerical zero. Open contours alone do not disqualify watercolor.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/additional_audit.json`; JSON pointer `/far_checks`.

**C199 — E3/p9_learned_b_0/classify/BY: canonical Mach index**

-0.0024279408 [-0.0032229678, -0.0015534347], n=27; signs +5/-22/0=0

Positive index denotes canonical bright-high/dark-low overshoot; negative is smoothing. An unsigned norm cannot establish Mach-band sign.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/additional_audit.json`; JSON pointer `/mach_and_contour/E3~1p9_learned_b_0~1classify~1BY/mach_odd_canonical`.

**C200 — E3/p27_learned_b_0/classify/BY: canonical Mach index**

-0.0017222092 [-0.0021572748, -0.0010036869], n=27; signs +1/-26/0=0

Positive index denotes canonical bright-high/dark-low overshoot; negative is smoothing. An unsigned norm cannot establish Mach-band sign.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/illusions_utility/additional_audit.json`; JSON pointer `/mach_and_contour/E3~1p27_learned_b_0~1classify~1BY/mach_odd_canonical`.


## Reference cues and optimizer controls

**C205 — E5b/p27_fixed/regress: test/r2**

-0.43033904 [-1.0022144, -0.0060134391], n=30

Known neutral surround substantially resolves estimation ambiguity under this input design; RMSE accompanies R2 because target variance matters.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/robustness/audit.json`; JSON pointer `/groups/106/metrics/test~1r2`.

**C206 — E5b/p27_fixed/regress: test/rmse_kelvin**

7088.4181 [6216.1783, 8151.8347], n=30

Known neutral surround substantially resolves estimation ambiguity under this input design; RMSE accompanies R2 because target variance matters.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/robustness/audit.json`; JSON pointer `/groups/106/metrics/test~1rmse_kelvin`.

**C207 — E5b/p9_baseline/regress: test/r2**

-0.28054066 [-0.82858042, 0.071273963], n=30

Known neutral surround substantially resolves estimation ambiguity under this input design; RMSE accompanies R2 because target variance matters.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/robustness/audit.json`; JSON pointer `/groups/110/metrics/test~1r2`.

**C208 — E5b/p9_baseline/regress: test/rmse_kelvin**

6749.877 [5982.7113, 7749.7726], n=30

Known neutral surround substantially resolves estimation ambiguity under this input design; RMSE accompanies R2 because target variance matters.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/robustness/audit.json`; JSON pointer `/groups/110/metrics/test~1rmse_kelvin`.

**C209 — E5b/p27_surround_neutral/regress: test/r2**

0.97080756 [0.93021492, 0.99337176], n=30

Known neutral surround substantially resolves estimation ambiguity under this input design; RMSE accompanies R2 because target variance matters.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/robustness/audit.json`; JSON pointer `/groups/131/metrics/test~1r2`.

**C210 — E5b/p27_surround_neutral/regress: test/rmse_kelvin**

673.44185 [437.97002, 1026.0344], n=30

Known neutral surround substantially resolves estimation ambiguity under this input design; RMSE accompanies R2 because target variance matters.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/robustness/audit.json`; JSON pointer `/groups/131/metrics/test~1rmse_kelvin`.

**C211 — E5b/p9_surround_neutral/regress: test/r2**

0.96820312 [0.93272746, 0.98944401], n=30

Known neutral surround substantially resolves estimation ambiguity under this input design; RMSE accompanies R2 because target variance matters.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/robustness/audit.json`; JSON pointer `/groups/151/metrics/test~1r2`.

**C212 — E5b/p9_surround_neutral/regress: test/rmse_kelvin**

817.27355 [580.8717, 1133.8182], n=30

Known neutral surround substantially resolves estimation ambiguity under this input design; RMSE accompanies R2 because target variance matters.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/robustness/audit.json`; JSON pointer `/groups/151/metrics/test~1rmse_kelvin`.

**C213 — E5c/p27_optimizer/classify: test/accuracy**

0.66803333 [0.62376583, 0.7148675], n=30

CMA and Adam share loss/training-trial count, not compute budget. Similar accuracy is not equivalence or representation invariance.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/robustness/audit.json`; JSON pointer `/groups/152/metrics/test~1accuracy`.

**C214 — E5c/p27_optimizer/classify: legacy_chromatic_power**

0.57588911 [0.5321204, 0.61772816], n=30

CMA and Adam share loss/training-trial count, not compute budget. Similar accuracy is not equivalence or representation invariance.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/robustness/audit.json`; JSON pointer `/groups/152/metrics/legacy_chromatic_power`.

**C215 — E5c/p27_optimizer/classify: legacy_double_opponent_fraction**

0.0125 [0, 0.029166667], n=30

CMA and Adam share loss/training-trial count, not compute budget. Similar accuracy is not equivalence or representation invariance.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/robustness/audit.json`; JSON pointer `/groups/152/metrics/legacy_double_opponent_fraction`.

**C216 — E5c/p27_optimizer/classify: double_opponent_fraction**

0.0125 [0, 0.029166667], n=30

CMA and Adam share loss/training-trial count, not compute budget. Similar accuracy is not equivalence or representation invariance.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/robustness/audit.json`; JSON pointer `/groups/152/metrics/double_opponent_fraction`.

**C217 — E5c/p27_optimizer/classify: double_opponency_score**

0.044979093 [0.034808676, 0.056903383], n=30

CMA and Adam share loss/training-trial count, not compute budget. Similar accuracy is not equivalence or representation invariance.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/robustness/audit.json`; JSON pointer `/groups/152/metrics/double_opponency_score`.

**C218 — E5c/p27_optimizer/cma: test/accuracy**

0.64596667 [0.60016583, 0.6922675], n=30

CMA and Adam share loss/training-trial count, not compute budget. Similar accuracy is not equivalence or representation invariance.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/robustness/audit.json`; JSON pointer `/groups/153/metrics/test~1accuracy`.

**C219 — E5c/p27_optimizer/cma: legacy_chromatic_power**

2.3322263 [2.2488724, 2.4148578], n=30

CMA and Adam share loss/training-trial count, not compute budget. Similar accuracy is not equivalence or representation invariance.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/robustness/audit.json`; JSON pointer `/groups/153/metrics/legacy_chromatic_power`.

**C220 — E5c/p27_optimizer/cma: legacy_double_opponent_fraction**

0.99583333 [0.9875, 1], n=30

CMA and Adam share loss/training-trial count, not compute budget. Similar accuracy is not equivalence or representation invariance.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/robustness/audit.json`; JSON pointer `/groups/153/metrics/legacy_double_opponent_fraction`.

**C221 — E5c/p27_optimizer/cma: double_opponent_fraction**

0.058333333 [0.029166667, 0.091666667], n=30

CMA and Adam share loss/training-trial count, not compute budget. Similar accuracy is not equivalence or representation invariance.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/robustness/audit.json`; JSON pointer `/groups/153/metrics/double_opponent_fraction`.

**C222 — E5c/p27_optimizer/cma: double_opponency_score**

0.15344229 [0.13824174, 0.16937752], n=30

CMA and Adam share loss/training-trial count, not compute budget. Similar accuracy is not equivalence or representation invariance.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/robustness/audit.json`; JSON pointer `/groups/153/metrics/double_opponency_score`.

**C223 — E5c/p9_optimizer/classify: test/accuracy**

0.66366667 [0.6158, 0.71247], n=30

CMA and Adam share loss/training-trial count, not compute budget. Similar accuracy is not equivalence or representation invariance.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/robustness/audit.json`; JSON pointer `/groups/154/metrics/test~1accuracy`.

**C224 — E5c/p9_optimizer/classify: legacy_chromatic_power**

0.50101068 [0.46755771, 0.53162964], n=30

CMA and Adam share loss/training-trial count, not compute budget. Similar accuracy is not equivalence or representation invariance.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/robustness/audit.json`; JSON pointer `/groups/154/metrics/legacy_chromatic_power`.

**C225 — E5c/p9_optimizer/classify: legacy_double_opponent_fraction**

0.27083333 [0.17916667, 0.3625], n=30

CMA and Adam share loss/training-trial count, not compute budget. Similar accuracy is not equivalence or representation invariance.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/robustness/audit.json`; JSON pointer `/groups/154/metrics/legacy_double_opponent_fraction`.

**C226 — E5c/p9_optimizer/classify: double_opponent_fraction**

0.016666667 [0.0041666667, 0.033333333], n=30

CMA and Adam share loss/training-trial count, not compute budget. Similar accuracy is not equivalence or representation invariance.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/robustness/audit.json`; JSON pointer `/groups/154/metrics/double_opponent_fraction`.

**C227 — E5c/p9_optimizer/classify: double_opponency_score**

0.087621637 [0.07276241, 0.10303463], n=30

CMA and Adam share loss/training-trial count, not compute budget. Similar accuracy is not equivalence or representation invariance.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/robustness/audit.json`; JSON pointer `/groups/154/metrics/double_opponency_score`.

**C228 — E5c/p9_optimizer/cma: test/accuracy**

0.66033333 [0.6202325, 0.70147], n=30

CMA and Adam share loss/training-trial count, not compute budget. Similar accuracy is not equivalence or representation invariance.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/robustness/audit.json`; JSON pointer `/groups/155/metrics/test~1accuracy`.

**C229 — E5c/p9_optimizer/cma: legacy_chromatic_power**

2.3093384 [2.2013248, 2.4218251], n=30

CMA and Adam share loss/training-trial count, not compute budget. Similar accuracy is not equivalence or representation invariance.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/robustness/audit.json`; JSON pointer `/groups/155/metrics/legacy_chromatic_power`.

**C230 — E5c/p9_optimizer/cma: legacy_double_opponent_fraction**

0.99583333 [0.9875, 1], n=30

CMA and Adam share loss/training-trial count, not compute budget. Similar accuracy is not equivalence or representation invariance.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/robustness/audit.json`; JSON pointer `/groups/155/metrics/legacy_double_opponent_fraction`.

**C231 — E5c/p9_optimizer/cma: double_opponent_fraction**

0.066666667 [0.041666667, 0.095833333], n=30

CMA and Adam share loss/training-trial count, not compute budget. Similar accuracy is not equivalence or representation invariance.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/robustness/audit.json`; JSON pointer `/groups/155/metrics/double_opponent_fraction`.

**C232 — E5c/p9_optimizer/cma: double_opponency_score**

0.16747382 [0.15181531, 0.18267535], n=30

CMA and Adam share loss/training-trial count, not compute budget. Similar accuracy is not equivalence or representation invariance.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/robustness/audit.json`; JSON pointer `/groups/155/metrics/double_opponency_score`.

**C233 — E5b/p27_cct_narrow/classify_minus_matched_baseline: test/accuracy**

0.075 [0.051566667, 0.097166667], n=30; p_signflip=1.5258789e-05; q_BH=5.5948893e-05

Exploratory paired network/data-seed comparison. CMA differences here are Adam minus CMA; CI crossing zero does not show equivalence.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/robustness/audit.json`; JSON pointer `/comparisons/885`.

**C234 — E5b/p27_refl_noise_vhi/classify_minus_matched_baseline: test/accuracy**

-0.057 [-0.077834167, -0.0376], n=30; p_signflip=1.5258789e-05; q_BH=5.5948893e-05

Exploratory paired network/data-seed comparison. CMA differences here are Adam minus CMA; CI crossing zero does not show equivalence.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/robustness/audit.json`; JSON pointer `/comparisons/1051`.

**C235 — E5b/p27_sensor_noise_hi/classify_minus_matched_baseline: test/accuracy**

-0.027033333 [-0.044266667, -0.011433333], n=30; p_signflip=0.0018920898; q_BH=0.0034688314

Exploratory paired network/data-seed comparison. CMA differences here are Adam minus CMA; CI crossing zero does not show equivalence.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/robustness/audit.json`; JSON pointer `/comparisons/1080`.

**C236 — E5b/p27_surround_neutral/regress_minus_matched_baseline: test/r2**

1.4011466 [0.99062361, 1.951621], n=30; p_signflip=1.5258789e-05; q_BH=8.392334e-05

Exploratory paired network/data-seed comparison. CMA differences here are Adam minus CMA; CI crossing zero does not show equivalence.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/robustness/audit.json`; JSON pointer `/comparisons/1149`.

**C237 — E5b/p9_cct_narrow/classify_minus_matched_baseline: test/accuracy**

0.0586 [0.027, 0.088133333], n=30; p_signflip=0.0012359619; q_BH=0.0027191162

Exploratory paired network/data-seed comparison. CMA differences here are Adam minus CMA; CI crossing zero does not show equivalence.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/robustness/audit.json`; JSON pointer `/comparisons/1260`.

**C238 — E5b/p9_refl_noise_vhi/classify_minus_matched_baseline: test/accuracy**

-0.057066667 [-0.075666667, -0.039166667], n=30; p_signflip=1.5258789e-05; q_BH=5.5948893e-05

Exploratory paired network/data-seed comparison. CMA differences here are Adam minus CMA; CI crossing zero does not show equivalence.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/robustness/audit.json`; JSON pointer `/comparisons/1405`.

**C239 — E5b/p9_sensor_noise_hi/classify_minus_matched_baseline: test/accuracy**

-0.071033333 [-0.093, -0.050999167], n=30; p_signflip=1.5258789e-05; q_BH=5.5948893e-05

Exploratory paired network/data-seed comparison. CMA differences here are Adam minus CMA; CI crossing zero does not show equivalence.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/robustness/audit.json`; JSON pointer `/comparisons/1434`.

**C240 — E5b/p9_surround_neutral/regress_minus_matched_baseline: test/r2**

1.2487438 [0.91465773, 1.7446918], n=30; p_signflip=1.5258789e-05; q_BH=8.392334e-05

Exploratory paired network/data-seed comparison. CMA differences here are Adam minus CMA; CI crossing zero does not show equivalence.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/robustness/audit.json`; JSON pointer `/comparisons/1503`.

**C241 — E5c/p27_optimizer/classify_minus_cma: double_opponency_score**

-0.10846319 [-0.12860536, -0.087779947], n=30; p_signflip=1.5258789e-05; q_BH=1.5258789e-05

Exploratory paired network/data-seed comparison. CMA differences here are Adam minus CMA; CI crossing zero does not show equivalence.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/robustness/audit.json`; JSON pointer `/comparisons/1550`.

**C242 — E5c/p27_optimizer/classify_minus_cma: test/accuracy**

0.022066667 [-0.017000833, 0.059300833], n=30; p_signflip=0.27780151; q_BH=0.55560303

Exploratory paired network/data-seed comparison. CMA differences here are Adam minus CMA; CI crossing zero does not show equivalence.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/robustness/audit.json`; JSON pointer `/comparisons/1557`.

**C243 — E5c/p9_optimizer/classify_minus_cma: double_opponency_score**

-0.07985218 [-0.10087201, -0.05889794], n=30; p_signflip=1.5258789e-05; q_BH=1.5258789e-05

Exploratory paired network/data-seed comparison. CMA differences here are Adam minus CMA; CI crossing zero does not show equivalence.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/robustness/audit.json`; JSON pointer `/comparisons/1561`.

**C244 — E5c/p9_optimizer/classify_minus_cma: test/accuracy**

0.0033333333 [-0.028233333, 0.038768333], n=30; p_signflip=0.85839844; q_BH=0.85839844

Exploratory paired network/data-seed comparison. CMA differences here are Adam minus CMA; CI crossing zero does not show equivalence.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/robustness/audit.json`; JSON pointer `/comparisons/1568`.

**C245 — CMA minus initialization p9: double_opponency_score**

difference=0.0028582804, CI=[-0.01317947363598818, 0.018269817026675825]; qBH=0.72991943

No clear normalized opponency increase above matched initialization, despite successful task training.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/robustness/cma_initialization_audit.json`; JSON pointer `/results/1`.

**C246 — CMA minus initialization p9: double_opponent_fraction**

difference=0.020833333, CI=[-0.0125, 0.05416666666666667]; qBH=0.66778564

No clear normalized opponency increase above matched initialization, despite successful task training.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/robustness/cma_initialization_audit.json`; JSON pointer `/results/2`.

**C247 — CMA minus initialization p27: double_opponency_score**

difference=-0.011173252, CI=[-0.028676395717480985, 0.007283308324657155]; qBH=0.48025513

No clear normalized opponency increase above matched initialization, despite successful task training.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/robustness/cma_initialization_audit.json`; JSON pointer `/results/4`.

**C248 — CMA minus initialization p27: double_opponent_fraction**

difference=0.0125, CI=[-0.025, 0.05]; qBH=0.66778564

No clear normalized opponency increase above matched initialization, despite successful task training.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/robustness/cma_initialization_audit.json`; JSON pointer `/results/5`.


## Architecture scope

**C249 — p9 exploratory classifier advantage for legacy_double_opponent_fraction**

12/12 positive BH-significant

Exploratory paired-mean sign-flip/BH family. Do not call this the frozen sign-test/Holm result.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/robustness/audit.json`; JSON pointer `/comparisons`.

**C250 — p27 exploratory classifier advantage for legacy_double_opponent_fraction**

0/12 positive BH-significant

Exploratory paired-mean sign-flip/BH family. Do not call this the frozen sign-test/Holm result.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/robustness/audit.json`; JSON pointer `/comparisons`.

**C251 — p9 exploratory classifier advantage for double_opponency_score**

10/12 positive BH-significant

Exploratory paired-mean sign-flip/BH family. Do not call this the frozen sign-test/Holm result.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/robustness/audit.json`; JSON pointer `/comparisons`.

**C252 — p27 exploratory classifier advantage for double_opponency_score**

1/12 positive BH-significant

Exploratory paired-mean sign-flip/BH family. Do not call this the frozen sign-test/Holm result.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/robustness/audit.json`; JSON pointer `/comparisons`.

**C253 — p9 exploratory classifier advantage for double_opponent_fraction**

3/12 positive BH-significant

Exploratory paired-mean sign-flip/BH family. Do not call this the frozen sign-test/Holm result.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/robustness/audit.json`; JSON pointer `/comparisons`.

**C254 — p27 exploratory classifier advantage for double_opponent_fraction**

0/12 positive BH-significant

Exploratory paired-mean sign-flip/BH family. Do not call this the frozen sign-test/Holm result.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/robustness/audit.json`; JSON pointer `/comparisons`.

**C255 — Frozen architecture objective comparisons**

24 complete indexed records in claims.json

All 24 architecture-size conditions use normalized above-null fraction and frozen sign-test/Holm; none reaches adjusted p<0.05.

Source: `PRODUCTION_RUN/analysis/E5a.json`; JSON pointer `/objective_comparisons`.


## Post-run raw-cone decoding

**C256 — p9_baseline: test_classification_accuracy**

0.7358 [0.7018325, 0.7702375], n=30

Explicitly supplemental post-run diagnostic: six center/ring LMS means; train-only standardization, validation-tuned logistic/ridge decoder, fixed held-out scenes. Accuracy and R2 are not comparable information units.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/raw_decoding/summary.json`; JSON pointer `/groups/0/metrics/test_classification_accuracy`.

**C257 — p9_baseline: test_illuminant_r2**

-0.59523957 [-1.1159713, -0.14381806], n=30

Explicitly supplemental post-run diagnostic: six center/ring LMS means; train-only standardization, validation-tuned logistic/ridge decoder, fixed held-out scenes. Accuracy and R2 are not comparable information units.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/raw_decoding/summary.json`; JSON pointer `/groups/0/metrics/test_illuminant_r2`.

**C258 — p9_baseline: test_illuminant_rmse_kelvin**

7437.6771 [6457.5194, 8528.3247], n=30

Explicitly supplemental post-run diagnostic: six center/ring LMS means; train-only standardization, validation-tuned logistic/ridge decoder, fixed held-out scenes. Accuracy and R2 are not comparable information units.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/raw_decoding/summary.json`; JSON pointer `/groups/0/metrics/test_illuminant_rmse_kelvin`.

**C259 — p9_baseline: constant_train_mean_test_rmse_kelvin**

6352.4643 [6320.8316, 6384.6895], n=30

Explicitly supplemental post-run diagnostic: six center/ring LMS means; train-only standardization, validation-tuned logistic/ridge decoder, fixed held-out scenes. Accuracy and R2 are not comparable information units.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/raw_decoding/summary.json`; JSON pointer `/groups/0/metrics/constant_train_mean_test_rmse_kelvin`.

**C260 — p27_fixed: test_classification_accuracy**

0.73603333 [0.70299667, 0.77156833], n=30

Explicitly supplemental post-run diagnostic: six center/ring LMS means; train-only standardization, validation-tuned logistic/ridge decoder, fixed held-out scenes. Accuracy and R2 are not comparable information units.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/raw_decoding/summary.json`; JSON pointer `/groups/3/metrics/test_classification_accuracy`.

**C261 — p27_fixed: test_illuminant_r2**

-0.62599218 [-1.1689493, -0.16044853], n=30

Explicitly supplemental post-run diagnostic: six center/ring LMS means; train-only standardization, validation-tuned logistic/ridge decoder, fixed held-out scenes. Accuracy and R2 are not comparable information units.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/raw_decoding/summary.json`; JSON pointer `/groups/3/metrics/test_illuminant_r2`.

**C262 — p27_fixed: test_illuminant_rmse_kelvin**

7490.8062 [6484.1631, 8602.1385], n=30

Explicitly supplemental post-run diagnostic: six center/ring LMS means; train-only standardization, validation-tuned logistic/ridge decoder, fixed held-out scenes. Accuracy and R2 are not comparable information units.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/raw_decoding/summary.json`; JSON pointer `/groups/3/metrics/test_illuminant_rmse_kelvin`.

**C263 — p27_fixed: constant_train_mean_test_rmse_kelvin**

6352.4643 [6320.8316, 6384.6895], n=30

Explicitly supplemental post-run diagnostic: six center/ring LMS means; train-only standardization, validation-tuned logistic/ridge decoder, fixed held-out scenes. Accuracy and R2 are not comparable information units.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/raw_decoding/summary.json`; JSON pointer `/groups/3/metrics/constant_train_mean_test_rmse_kelvin`.

**C264 — p9_baseline/noise 0.05 minus noise 0: test_classification_accuracy**

-0.0049333333 [-0.0173675, 0.0087341667], n=30

No clear classification collapse; R2 improves from negative baseline. Potential regularization account is untested.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/raw_decoding/summary.json`; JSON pointer `/paired_noise_differences/1/metrics/test_classification_accuracy`.

**C265 — p9_baseline/noise 0.05 minus noise 0: test_illuminant_r2**

0.23455608 [0.059051034, 0.45584252], n=30

No clear classification collapse; R2 improves from negative baseline. Potential regularization account is untested.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/raw_decoding/summary.json`; JSON pointer `/paired_noise_differences/1/metrics/test_illuminant_r2`.

**C266 — p27_fixed/noise 0.05 minus noise 0: test_classification_accuracy**

-0.00023333333 [-0.0120025, 0.012035], n=30

No clear classification collapse; R2 improves from negative baseline. Potential regularization account is untested.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/raw_decoding/summary.json`; JSON pointer `/paired_noise_differences/3/metrics/test_classification_accuracy`.

**C267 — p27_fixed/noise 0.05 minus noise 0: test_illuminant_r2**

0.076720186 [0.026143427, 0.13586577], n=30

No clear classification collapse; R2 improves from negative baseline. Potential regularization account is untested.

Source: `PRODUCTION_RUN/analysis/comparison_20261121/raw_decoding/summary.json`; JSON pointer `/paired_noise_differences/3/metrics/test_illuminant_r2`.
