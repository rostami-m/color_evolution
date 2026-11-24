# Revision audit — 24 November 2026

This revision addresses all three comments from Reviewer 1 and the author's associated actions. The current manuscript is `visionresearch-article.tex`; `Response.tex` is the point-by-point response, and `cover_letter_vr.tex` is the updated cover letter. The response quotes the received comments and identifies the corresponding Methods, Results and Discussion changes. No journal submission is implied by synchronization to Overleaf.

## Scientific changes

Both 9×9 and 27×27 full patches remain, with 3×3 and 9×9 targets. The justification for 27 is a planned threefold enlargement preserving an odd centered target, target/patch ratio and base parameter count. Dilation restores relative sampling support without adding parameters. Neither optimality nor a human visual-angle calibration is claimed; the deferred 81-pixel condition is not reported as completed.

The revision distinguishes amplitude-based filter measurements from normalized initialization-calibrated endpoints. The frozen primary scale-by-objective interaction remains inconclusive. The new discussion connects spatial integration, boundary access and readout differences to relevant neurophysiology and psychophysics without treating those analogies as proof of the training mechanism. Reference-cue rescue, held-out-scene performance, normalization-sensitive utility results and corrected signed illusion measurements are reported explicitly. Unsupported five-illusion, Dress, universal-opponency and human-discrimination claims have been removed.

New post-production, saved-checkpoint diagnostics hold weights fixed while changing size/dilation, test the repeated-input identity, and replace padding at inference. Local BY induction attenuates from 0.03013 to 0.00990 and returns to 0.03013 with scaled dilation for the small-trained weights (28 valid calibrations). This isolates acute geometry from retraining. Padding changes some global predictions while leaving local target induction unchanged. It does not establish padding's causal role during learning. Original float32 tolerance failures are retained; the separately specified float64 check passes all 30 networks.

## Implementation and numerical evidence

The code release is https://github.com/rostami-m/color_evolution at tag `visionresearch-revision-20261124`.

| Check | Result and scope |
|---|---|
| Production inventory | 2,443 completed jobs; 6,870 nonempty model/control checkpoints |
| Frozen scientific source | All 43 recorded hashes match |
| Initial reconstruction audit | 14 representative checkpoints reproduce saved CPU metrics/test summaries |
| Portable configuration comparison | All 2,431 production configuration dictionaries match |
| Frozen-versus-release model comparison | 18 representative checkpoints produce identical test data, predictions, metrics and signed probes |
| Post-run analysis | Five numerical summaries reproduce exactly: primary, robustness, CMA initialization, illusion/utility and additional signed probes |
| CPU/MPS tests | 29 tests pass; three release tests rerun successfully after the final configuration correction |
| Packaging and smoke execution | Isolated installation/import and a four-mode CPU training smoke run pass |
| New diagnostics | Native test accuracies reproduced for 90 E1 plus 30 center-only classifiers; float64 spatial identity checked in all 30 small classifiers; portable diagnostic rerun reproduces all three per-seed files byte for byte |
| Claims | 267 indexed production claims retain values, intervals, sample sizes, source pointers and original-source hashes; all validate against the public numerical bundle |

The code repository provides detailed reports under `provenance/`, a compact result bundle under `published_results/`, and protocols, per-seed results and scripts under `reproducibility/scale_diagnostics/`. Figure regeneration, reanalysis of a completed run, and full training are documented separately. The full 2,443-job training study was not repeated during release cleanup. Raw scene files and model checkpoints are not embedded in Git; acquisition/preparation and training commands regenerate them.

## Manuscript-to-code map

| Manuscript content | Active implementation / evidence |
|---|---|
| Spectral sampling, scenes, rendering and categories | `revision/prepare_data.py`, `revision/data.py`, `revision/spectral.py`; `provenance/data_manifest.json` |
| Model, readouts and dilation | `revision/models.py`; checkpoint-compatibility report |
| Training and condition definitions | `revision/experiments.py`, `revision/build_queue.py`; configuration-equivalence report |
| Weight metrics and null calibration | `revision/analysis.py`, `revision/legacy_metrics.py`; primary result bundle |
| Signed local/global induction and masks | `revision/illusions.py`; illusion/utility and additional-probe result bundles |
| Production figures and numerical tables | `scripts/reproduce.py`; checksum-verified published summaries |
| Frozen-weight scale, identity and padding controls | `reproducibility/scale_diagnostics/` |

## Document checks and retained limitations

The manuscript, response and cover letter compile with Tectonic. Citation keys resolve and bibliography metadata were checked; new references distinguish published records from accessible preprint versions. The abstract, figures, captions, result tables and response pages were visually checked. Figures are vector PDFs regenerated from the audited result bundle. Superseded journal variants and old figures were removed from the active tree, with history retained at original Overleaf commit `c45e642`.

These checks support implementation continuity and consistency of reported measurements. They do not establish biological validity, recover the missing historical run, provide additional independent scene partitions, or guarantee identical fitted weights across hardware. Thirty seeds condition on one fixed eight-scene partition. The author retains responsibility for final scientific and submission decisions.
