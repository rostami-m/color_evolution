# Saved-checkpoint scale diagnostics — 24 November 2026

These are new post-production exploratory diagnostics, specified in `protocol.json` before their execution. They do not replace the original primary endpoint. No network was trained and all inference ran on CPU with two compute threads and one interop thread.

## Results

The frozen-weight probe sweep isolates an acute effect of relative spatial support: enlarging the target with fixed weights and a fixed local kernel attenuates local blue–yellow induction. Scaling dilation along with the image restores the response. The training-dependent difference in opponent weight scores remains a separate question.

| Source of saved weights | Probe 9/d1 | Probe 27/d1 | Probe 27/d3 |
|---|---:|---:|---:|
| p9_baseline | 0.030127 [0.025171, 0.034715], n=28 | 0.009901 [0.008000, 0.011658], n=28 | 0.030127 [0.025171, 0.034715], n=28 |
| p27_fixed | 0.054228 [0.049704, 0.057271], n=28 | 0.019444 [0.017654, 0.020704], n=28 | 0.054228 [0.049704, 0.057271], n=28 |
| p27_dilated | 0.033140 [0.028731, 0.037265], n=27 | 0.010977 [0.009234, 0.012594], n=27 | 0.033140 [0.028731, 0.037265], n=27 |

Values are mean calibrated, polarity-odd local-target shifts with descriptive 95% seed-bootstrap intervals. Positive denotes assimilation. The table uses identical noise-free target/surround colors and native center masks. Both color axes, raw signed projection numerators, representation shifts, output-logit shifts, calibration denominators, and every seed are retained in JSON. Undefined calibration remains undefined.

For the original 9-pixel-trained weights, changing 9/d1 to 27/d1 reduces the calibrated BY target response by -0.020226 [-0.023064, -0.017157], n=28. This contrasts acute geometry with separately retrained-model comparisons.

## Numerical identity and precision

The exact copied-weight repeat/dilation identity was tested on 32 deterministic random patches plus 14 RG/BY calibration and surround probes per seed. The original prespecified float32 atol=rtol=1e-6 checks failed for some maps, representations, and logits. They are preserved, not relabeled as passes. Maximum errors were feature: 2.861e-05, representation: 8.583e-06, logits: 6.485e-05.

A subsequently specified precision check (`precision_protocol.json`) cast the same input values and checkpoint weights to float64. All 30 networks passed atol=rtol=1e-12 for all three arrays; maximum errors were feature: 3.553e-15, representation: 5.329e-15, logits: 1.776e-14. This supports floating-point accumulation as the source of the float32 discrepancy. The algebraic identity is not a claim of bitwise equality in ordinary float32 implementations.

Original float32 BY normalized identity errors were at most 9.596e-08 for local target responses and 3.432e-07 for global representations. Valid denominators numbered 28 and 29 respectively, with no defined/undefined mismatch across scaled copies.

## Padding controls

| Source weights | Padding replacement | Accuracy change (percentage points) | Changed predictions (%) |
|---|---|---:|---:|
| E2_intact_center_only | reflect | 0.000000 [0.000000, 0.000000], n=30 | 0.000000 [0.000000, 0.000000], n=30 |
| E2_intact_center_only | replicate | 0.000000 [0.000000, 0.000000], n=30 | 0.000000 [0.000000, 0.000000], n=30 |
| p27_dilated | reflect | 0.353333 [-0.413333, 1.083333], n=30 | 3.353333 [2.556667, 4.183333], n=30 |
| p27_dilated | replicate | 0.360000 [-0.413333, 1.096667], n=30 | 3.373333 [2.580000, 4.196667], n=30 |
| p27_fixed | reflect | 0.083333 [-0.283333, 0.480000], n=30 | 1.110000 [0.623333, 1.776667], n=30 |
| p27_fixed | replicate | 0.083333 [-0.283333, 0.480000], n=30 | 1.103333 [0.616667, 1.773333], n=30 |
| p9_baseline | reflect | 0.490000 [-0.210000, 1.190000], n=30 | 2.843333 [2.089917, 3.666667], n=30 |
| p9_baseline | replicate | 0.500000 [-0.196667, 1.193333], n=30 | 2.820000 [2.063250, 3.643333], n=30 |

All 90 E1 native models and all 30 E2 center-only models exactly reproduced saved zero-padding test accuracies before the padding replacement. Replicate/reflect padding changed roughly 1.1–3.4% of predictions for the base E1 readout, but mean accuracy-difference intervals crossed zero. This does not establish performance equivalence.

For all E1 conditions, the local target BY response was exactly unchanged by padding replacement: the target receptive fields do not reach the image frame. Global representations and output logits can change because they pool frame features. E2 center-only controls had no prediction or accuracy changes, with only float32 roundoff in logits (mean absolute difference about 7e-7). This supports the distinction between genuinely local induction and frame-sensitive global readouts.

**Interpretive limit:** replacing padding after training is out of the training distribution. These controls do not establish that padding caused or did not cause the learned opponent-score differences. Controlled retraining would be needed for that causal question.

## Further scope limits

- The primary scale-by-objective normalized opponent-fraction result is unchanged and remains inconclusive.
- These uniform simultaneous probes do not validate human percepts, distant watercolor/Cornsweet filling-in, or signed Mach-band overshoot.
- Standard production Cornsweet, Mach, and watercolor probes are not literal repeat3 pairs; the identity cannot be extended to them by assumption.
- The observed edge-access fraction is a support count, not a complete quantitative response model: corner and straight-edge contributions can differ.
- There is no calibrated visual-angle mapping, new scene partition, new functional cone-opponency assay, or new training in this package.

## Reproduction commands

From the repository root, recreate this figure and report from the packaged results without downloading data or training:

```bash
python reproducibility/scale_diagnostics/summarize_diagnostics.py --input reproducibility/scale_diagnostics --output generated/scale_diagnostics
```

To recompute the diagnostics, first complete the full 30-seed study and prepare its natural data as described in the top-level README. Checkpoints are not included in Git. Then run the following from the repository root. Replace `PATH_TO_COMPLETED_RUN` with that run directory. The protocols must be copied before execution; all newly generated results go into a separate output directory.

```bash
mkdir -p generated/scale_diagnostics
cp reproducibility/scale_diagnostics/protocol.json reproducibility/scale_diagnostics/precision_protocol.json generated/scale_diagnostics/
python reproducibility/scale_diagnostics/run_scale_diagnostics.py --run PATH_TO_COMPLETED_RUN --runtime . --data-dir data --output generated/scale_diagnostics
python reproducibility/scale_diagnostics/check_identity_precision.py --run PATH_TO_COMPLETED_RUN --runtime . --data-dir data --output generated/scale_diagnostics
python reproducibility/scale_diagnostics/summarize_diagnostics.py --input generated/scale_diagnostics --output generated/scale_diagnostics
```

`--runtime` can also point to the immutable production runtime. The release resolves the imported spectral module in either layout. The summary script reads only its `--input` directory and writes report/figure artifacts to `--output`; with no options both default to its own directory. Source snapshots and fitted weights may differ for a newly trained CPU replication, so fresh scientific outcomes need not equal the recorded MPS study.

Keep the protocol files with the results. `summary.json` records the executed script, protocol, source, data-manifest, and checkpoint SHA-256 hashes plus execution times. Original execution hashes remain in the published JSON; release portability changes and their lineage are documented in `RELEASE_PROVENANCE.json`. Those historical script hashes are not claims that the portability-edited scripts are byte-identical. The original run took about 16 seconds excluding interpreter/data loading and precision confirmation. Original command invocation used `nice -n 15`; macOS denied the priority adjustment in the sandbox, so numerical thread limits provided the actual resource cap.
