# Learned color representations across spatial scales

Reproducible code and numerical results for the revised color-vision study. The active implementation is `revision/`, derived from the frozen source that ran the completed 2,443-job study (6,870 model/control records, 30 paired seed blocks). The older `src/`, `experiments/`, and `run_all.py` workflow is retired from this release; its Git history and the original research archive are preserved.

The revised manuscript and compiled PDF are in `paper/`. Release tag: `visionresearch-revision-20261125`. The code–paper audit is `reproducibility/PAPER_CODE_AUDIT.md`.

## Install

Python 3.10 or newer, on Linux or macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
```

`provenance/production_requirements.lock` records the actual production package versions. Installing that lock recreates the recorded software environment when the same Python/platform has compatible wheels. Broader version ranges in `pyproject.toml` support installation elsewhere but do not promise bitwise equality. The queue uses POSIX process groups; Windows execution is not supported by it.

## Recreate paper figures and numerical tables

No dataset download, model training, or GPU is needed:

```bash
python scripts/reproduce.py --output generated
```

This verifies checksums of `published_results/`, then creates `generated/figures/{study_design,learned_organization,task_and_reference,signed_induction,fixed_weight_controls,robustness_and_context}.pdf` and PNG versions, plus long-form summary tables in `generated/tables/`. `generated/figures/figure_source_data.json` records the numerical summaries and source hashes used for the six figures. The bundle contains per-seed primary results, stage summaries, robustness comparisons, signed-probe/utility audits, and raw-cone decoding summaries. These are recorded results; this command redraws and reformats them, rather than retraining models.

## Recreate the full study from the source data

The original eight Foster/Nascimento scenes are external research data and are not redistributed here. Respect the providers' terms. The downloader uses the coauthor-hosted source links and validates the scene arrays. Alternatively place `scene1.mat` through `scene8.mat` in `data/foster/` before preparation.

```bash
python -m revision.prepare_data --data-dir data
python -m revision.build_queue --project . --data-dir data --output results/replication_cpu --backend cpu
python -m revision.queue run --manifest results/replication_cpu/manifest.json --output results/replication_cpu/queue --workdir . --threads 2 --cpu-cores 1.5 --memory-gib 4
```

The default build freezes all 2,443 jobs with 30 seeds, 4,000/800/1,000 train/validation/test examples, 80 Adam epochs, batch size 128, learning rate 0.002, and the production CMA budget. The optional 81-pixel arm is excluded, as in the completed production study. Manifests refuse overwrite; use a new output directory for a changed design. `--smoke --seeds 1` builds a small-budget validation design, which must never be analyzed as production evidence.

For Apple MPS, replace `--backend cpu` with `--backend mps`, choose a separate run directory, and add `--gpu` to the queue command. Training uses explicit float32 MPS; initialization, sample permutations and evaluation remain on CPU. Unavailable MPS raises an error; silent fallback is disabled. CUDA was not a production backend and is not silently substituted. The release queue is sequential and resource bounded; the eight-worker production scheduling affected throughput, not the scientific configuration. CPU caps are sampled process-group averages, not instantaneous utilization limits. The MPS allocator ceiling defaults to 4 GiB per worker (`REVISION_MPS_MEMORY_GIB`).

To inspect/control a running queue, substitute `status`, `pause`, `resume`, or `stop` for `run`, retaining `--output results/replication_cpu/queue`. Resume after an interruption with the original `run` command. Add `--retry-failed` only to retry recorded failed jobs. Completed model checkpoints are reused; an unfinished model restarts from its seed. The supervisor needs a live machine; run under a terminal multiplexer for an SSH session that may disconnect.

After all jobs complete, recompute the production analyses and summary plots:

```bash
python scripts/reanalyze.py --run results/replication_cpu --data-dir data --output results/replication_cpu/postrun --raw-decoding
```

This produces numerical analyses and three production-summary plots. The six-figure manuscript set additionally requires the separate fixed-weight diagnostics described below; published diagnostics are never silently combined with a new run. This requires the full completed 30-seed study, not a smoke design. All stage aggregates are also generated as dependencies within the queue. Raw-cone decoding is a separate post hoc CPU analysis and is requested explicitly. MPS and CPU replications are never pooled as exchangeable seed replicates. Floating-point backend differences can lead to different learned weights; fresh CPU results need not equal the published MPS numbers bit for bit.

## Saved-checkpoint scale diagnostics

The completed supplementary diagnostics are in
`reproducibility/scale_diagnostics/`: a frozen-weight size/dilation sweep,
replicate/reflect padding interventions, and the copied-weight repeat/dilation
identity with an explicit float64 precision follow-up. These are new post-run
CPU evaluations, not additional trained replicates. Local induction attenuates
at fixed dilation and returns when dilation scales with the pattern. Padding
replacement leaves local target responses unchanged, while changing some global
predictions; its influence during learning remains unresolved. The original
strict float32 identity failures are preserved, alongside the float64 checks.

Re-evaluate from a regenerated full run, saving separately from the published
records:

```bash
mkdir -p results/replication_cpu/scale_diagnostics
cp reproducibility/scale_diagnostics/protocol.json reproducibility/scale_diagnostics/precision_protocol.json results/replication_cpu/scale_diagnostics/
python reproducibility/scale_diagnostics/run_scale_diagnostics.py --runtime . --run results/replication_cpu --data-dir data --output results/replication_cpu/scale_diagnostics
python reproducibility/scale_diagnostics/check_identity_precision.py --runtime . --run results/replication_cpu --data-dir data --output results/replication_cpu/scale_diagnostics
python reproducibility/scale_diagnostics/summarize_diagnostics.py --input results/replication_cpu/scale_diagnostics --output results/replication_cpu/scale_diagnostics
```

To redraw the supplementary figure and report from the public results alone:

```bash
python reproducibility/scale_diagnostics/summarize_diagnostics.py --input reproducibility/scale_diagnostics --output generated/scale_diagnostics
```

To draw all six manuscript figures from that independently regenerated run, after both reanalysis and diagnostic summaries are complete:

```bash
python scripts/reproduce.py --bundle results/replication_cpu/postrun --diagnostics results/replication_cpu/scale_diagnostics --output results/replication_cpu/manuscript --skip-verification
```

`--skip-verification` is for newly generated outputs whose hashes differ from the published manifests. Custom result bundles require an explicit matching diagnostics directory. The six-figure set also needs the raw-cone decoding analysis (`--raw-decoding` above). Alternatively supply `--diagnostics` to `reanalyze.py` when those diagnostics already exist.

Protocols precede execution. The summary script reads `--input` and writes `--output`. See the diagnostic README for exact settings and original-versus-release script hashes.

## Interpretation and provenance

- The 9×9 and 27×27 patches have 3×3 and 9×9 central targets. The dilated arm samples a sparse 3×3 kernel over a 7×7 footprint; it is not a dense 7×7 kernel.
- 9×9 and 27×27 are complementary conditions specified together before the reported production results; their threefold side-length ratio isolates relative-support contrasts without changing the base parameter count. Neither size was empirically optimized. Relative spatial support and padding exposure both change across arms.
- Amplitude-based and normalized weight indices are descriptive measures, not physiological neuron identities. The frozen primary normalized interaction is inconclusive; other reported comparisons must retain their exploratory status.
- Signed local feature responses and pooled representations are not calibrated human perceptual reports. Distant local filling-in is outside this architecture's support. Open contours alone do not disqualify a watercolor effect.
- Illumination uses generated Planck spectra, not measured daylight. Ecological proxy curves are analytic, not measured fruit, foliage or skin spectra. Utility probes measure bounded representation sensitivity, not human JNDs.
- Held-out scenes are 7/8; train scenes are 1/2/4/5 and validation scenes 3/6. Targets and context crops are sampled independently. Uncertainty is conditional on this small fixed scene partition.
- The original Dress result is unsupported by recoverable calibrated inputs; it is not claimed as reproduced.

See `provenance/README.md` for source lineage, data transformations and the release audit. Raw external scenes and thousands of checkpoints are omitted from Git; all procedures needed to regenerate them are included. No claim is made that this cleanup itself reran the full study.

## Validate

```bash
python -m pytest -q
```

Tests cover matched initialization, exact repeated-input/dilation identities, noise and label pairing, known filter scores, stimulus controls, signed distant probes, CMA behavior, backend guards, resource caps, queue recovery, manifest scope and public-result checksums. MPS-specific tests skip when MPS is unavailable.
