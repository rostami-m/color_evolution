# Revision audit

Current release: `visionresearch-neuroscience-20261125`. The final section records the neuroscience and illustration revision; earlier validation is retained below.

## Initial release — 24 November 2026

This revision addresses all three comments from Reviewer 1 and the author's associated actions. The current manuscript is `visionresearch-article.tex`; `Response.tex` is the point-by-point response, and `cover_letter_vr.tex` is the updated cover letter. The response quotes the received comments and identifies the corresponding Methods, Results and Discussion changes. No journal submission is implied by synchronization to Overleaf.

## Scientific changes

Both 9×9 and 27×27 full patches remain, with 3×3 and 9×9 targets. The justification for 27 is a planned threefold enlargement preserving an odd centered target, target/patch ratio and base parameter count. Dilation restores relative sampling support without adding parameters. Neither optimality nor a human visual-angle calibration is claimed; the deferred 81-pixel condition is not reported as completed.

The revision distinguishes amplitude-based filter measurements from normalized initialization-calibrated endpoints. The frozen primary scale-by-objective interaction remains inconclusive. The new discussion connects spatial integration, boundary access and readout differences to relevant neurophysiology and psychophysics without treating those analogies as proof of the training mechanism. Reference-cue rescue, held-out-scene performance, normalization-sensitive utility results and corrected signed illusion measurements are reported explicitly. Unsupported five-illusion, Dress, universal-opponency and human-discrimination claims have been removed.

New post-production, saved-checkpoint diagnostics hold weights fixed while changing size/dilation, test the repeated-input identity, and replace padding at inference. Local BY induction attenuates from 0.03013 to 0.00990 and returns to 0.03013 with scaled dilation for the small-trained weights (28 valid calibrations). This isolates acute geometry from retraining. Padding changes some global predictions while leaving local target induction unchanged. It does not establish padding's causal role during learning. Original float32 tolerance failures are retained; the separately specified float64 check passes all 30 networks.

## Implementation and numerical evidence

The code release is https://github.com/rostami-m/color_evolution at tag `visionresearch-revision-20261124-v2`.

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

## Reviewer-adequacy follow-up

A further review found that scaling the figures in LaTeX reduced some labels to 5–6 points. The generators were revised, and the compiled manuscript was checked again: ordinary axis, legend, count and panel text is now at least 8.1 points (the mathematical superscript in R² is smaller). Captions and legend placement were checked in the final document. No scientific results changed.

The related-work discussion now balances CLIP limitations with Akbarinia's positive task-dependent category-agreement result (2025, DOI 10.1016/j.neunet.2024.106758; primary author project and publisher/PubMed metadata checked). It also specifies the distinction between network chromatic activation tuning and human detection thresholds in Songlin et al. The introduction states the transferable contribution as a dissociation between learned weight indices, fixed-weight induction and decoded response sign. The response letter provides exact section, figure and table locations.

All explicit reviewer requests have substantive responses. Human-scale validation, resolution convergence, causal attribution of learned-filter changes, and broader environmental generalization remain outside the established findings. The versioned follow-up is `visionresearch-revision-20261124-v2`; the original tag remains available.

## Author revision — 25 November 2026

Current release: `visionresearch-revision-20261125` (package 0.2.2). The revision incorporates the author-edited Overleaf commit `a654c83` and all five inline manuscript comments. The author confirmed that these TeX comments, together with edits to Response.tex, were the intended comment source.

| Author request | Completed change |
|---|---|
| Short, engaging abstract | A 159-word abstract leads with the scientific question and findings; detailed numerical audit material is removed, while the inconclusive primary comparison remains accurately summarized. |
| Standalone scientific narrative | Introduction and Discussion present a joint center–surround study, without amendment or historical-correction framing. |
| Unified methods | The design describes the actual reported experiments, with operational history retained in provenance files rather than the main narrative. |
| Complementary size justification | Methods explain compact boundary access, extended target interior, the shared one-third ratio, fixed parameter count, and threefold dilation/noise controls before the Results. Both sizes were specified before production outcomes. Directional mechanisms are conditional interpretations, not falsely claimed prospective registrations. E2/E4 remain explicitly 27-pixel-only. |
| Six informative figures | Six figures are regenerated from verified current results: study design, learned organization, task/reference effects, signed induction, fixed-weight controls, and robustness/context. Unsupported historical panels are not reused. |

The response preserves submission ID VR-26-173 and the author's preferred framing, gives precise section/figure/table locations, and matches the six-figure structure. The cover letter is dated November 25, 2026. The main document retains the normalized primary null and identifies saved-weight controls as exploratory post-production tests.

Validation for this revision: 267 indexed numerical claims pass; 211 plotted summaries independently checked against eight source files; six figures regenerate from checksum-verified public results and diagnostic inputs; four release tests pass. The added test prevents silently mixing an independent result bundle with published fixed-weight diagnostics. The training implementation, configurations, recorded numerical results, and diagnostic records are unchanged. Full training and the previously completed 29-test scientific suite were not repeated for this manuscript/plotting revision.

The manuscript compiles to 40 pages, the response to seven pages, and the cover letter to one page. All citations and references resolve. Ordinary text in the six figures measures at least 8.05 points in the compiled manuscript (mathematical superscripts are smaller). Sources, figures, captions, and compiled pages were checked together. The existing 2.608-point class/frontmatter box warning causes no visible clipping. Public code includes the manuscript and figure source audit, while private reviewer/author correspondence remains in Overleaf.

## Integrated neuroscience and illustration revision — 25 November 2026

Current release: `visionresearch-neuroscience-20261125` (package 0.2.3). The manuscript was read end to end and revised around three distinct computations: learned cone-contrast selectivity, local spatial integration, and readout. Both spatial sizes remain complementary production conditions. The normalized primary interaction remains inconclusive, and saved-weight mechanistic controls remain explicitly exploratory.

Nine primary neuroscience/psychophysics references support and constrain the interpretation. Chromatic boundary-versus-interior responses motivate the geometry comparison; population decoding and contextual reference cues motivate distinct readout and information questions. Cornsweet, watercolor, and feedback studies are presented with differences in species, stimulus, and measurement intact. Inferred effective connectivity is separated from causal perturbation. Distant local nulls do not establish that perceived surface color requires a uniformly activated early cortical map. Prospective recurrent, multiscale, and spatial-appearance-decoder tests are clearly identified as unperformed. Public full texts and author manuscripts were read; the exact accessible versions and evidential limits are recorded in `provenance/neuroscience_revision_20261125.json` in the code release.

The seventh figure illustrates exact inputs from the induction evaluator, physical profiles, and measurement regions for simultaneous induction, Cornsweet, Mach, and watercolor probes. Colors are schematic; analysis masks are not perceived tints. The figure uses no invented response data. Its script saves the underlying LMS arrays and masks, source hashes, and 24 physical-input/support checks. Cornsweet near and distant windows overlap by one unchanged column per side; distant windows still exclude the cusp and its sampling support. Scientific code and numerical records are unchanged.

Validation: all seven figures regenerate from the checksum-verified public bundle and diagnostics; the 211 recorded plotting summaries exactly match the prior audited records; 267 indexed claims pass; four release tests pass. The response and cover are aligned with the seven-figure manuscript and new interpretation, with reviewer quotations preserved. Final PDFs are 47 manuscript pages, eight response pages, and one cover page. Citations and references resolve, there is no text outside page bounds, and ordinary figure labels measure at least 8.05 points in the manuscript (8.16 in the new guide; mathematical superscripts are smaller). The class/frontmatter box and package-source encoding warnings produce no visible clipping or replacement glyphs. Full training and the previously completed scientific test suite were not repeated for this interpretation and plotting revision.
