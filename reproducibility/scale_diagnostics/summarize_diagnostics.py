"""Export manuscript-facing tables/figure from the saved post-production diagnostics."""
import argparse,json,os
from pathlib import Path
import numpy as np
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--input',type=Path,default=Path(__file__).parent,
                    help='Directory containing summary.json and identity_precision.json; defaults to the script directory.')
parser.add_argument('--output',type=Path,
                    help='Destination for README.md and PDF/PNG figures; defaults to the input directory.')
args=parser.parse_args()
INPUT=args.input.resolve()
ROOT=(args.output or INPUT).resolve()
ROOT.mkdir(parents=True,exist_ok=True)
os.environ['MPLCONFIGDIR']=str(ROOT/'mpl_cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
d=json.loads((INPUT/'summary.json').read_text())
precision=json.loads((INPUT/'identity_precision.json').read_text())

def fmt(v,scale=1):
    return f"{v['mean']*scale:.6f} [{v['ci95'][0]*scale:.6f}, {v['ci95'][1]*scale:.6f}], n={v['n_valid']}"

lines=['# Saved-checkpoint scale diagnostics — 24 November 2026','',
       'These are new post-production exploratory diagnostics, specified in `protocol.json` before their execution. They do not replace the original primary endpoint. No network was trained and all inference ran on CPU with two compute threads and one interop thread.','',
       '## Results','',
       'The frozen-weight probe sweep isolates an acute effect of relative spatial support: enlarging the target with fixed weights and a fixed local kernel attenuates local blue–yellow induction. Scaling dilation along with the image restores the response. The training-dependent difference in opponent weight scores remains a separate question.','',
       '| Source of saved weights | Probe 9/d1 | Probe 27/d1 | Probe 27/d3 |',
       '|---|---:|---:|---:|']
for source in ['p9_baseline','p27_fixed','p27_dilated']:
    vals=[]
    for p,di in [(9,1),(27,1),(27,3)]:
        g=next(g for g in d['frozen_sweep'] if (g['source_condition'],g['patch_size'],g['dilation'],g['axis'])==(source,p,di,'BY'))
        vals.append(fmt(g['metrics']['local_target']['normalized_shift']))
    lines.append('| '+source+' | '+' | '.join(vals)+' |')
lines += ['', 'Values are mean calibrated, polarity-odd local-target shifts with descriptive 95% seed-bootstrap intervals. Positive denotes assimilation. The table uses identical noise-free target/surround colors and native center masks. Both color axes, raw signed projection numerators, representation shifts, output-logit shifts, calibration denominators, and every seed are retained in JSON. Undefined calibration remains undefined.','',
          'For the original 9-pixel-trained weights, changing 9/d1 to 27/d1 reduces the calibrated BY target response by '+fmt(next(g for g in d['paired_frozen_contrasts'] if g['source_condition']=='p9_baseline' and g['axis']=='BY' and g['comparison']=='size27_minus9_fixed_d1')['metrics']['local_target']['normalized_shift'])+'. This contrasts acute geometry with separately retrained-model comparisons.','',
          '## Numerical identity and precision','',
          'The exact copied-weight repeat/dilation identity was tested on 32 deterministic random patches plus 14 RG/BY calibration and surround probes per seed. The original prespecified float32 atol=rtol=1e-6 checks failed for some maps, representations, and logits. They are preserved, not relabeled as passes. Maximum errors were '+', '.join(f"{k}: {d['identity'][k]['max_abs_error']:.4g}" for k in ['feature','representation','logits'])+'.','',
          'A subsequently specified precision check (`precision_protocol.json`) cast the same input values and checkpoint weights to float64. All 30 networks passed atol=rtol=1e-12 for all three arrays; maximum errors were '+', '.join(f"{k}: {precision['summary'][k]['max_abs_error']:.4g}" for k in ['feature','representation','logits'])+'. This supports floating-point accumulation as the source of the float32 discrepancy. The algebraic identity is not a claim of bitwise equality in ordinary float32 implementations.','',
          'Original float32 BY normalized identity errors were at most '+f"{d['identity']['axes']['BY']['local_target']['max_normalized_error']:.4g}"+' for local target responses and '+f"{d['identity']['axes']['BY']['global_representation']['max_normalized_error']:.4g}"+' for global representations. Valid denominators numbered 28 and 29 respectively, with no defined/undefined mismatch across scaled copies.','',
          '## Padding controls','',
          '| Source weights | Padding replacement | Accuracy change (percentage points) | Changed predictions (%) |',
          '|---|---|---:|---:|']
for row in d['padding']:
    lines.append('| '+row['source_condition']+' | '+row['padding']+' | '+fmt(row['metrics']['accuracy_difference'],100)+' | '+fmt(row['metrics']['prediction_change_fraction'],100)+' |')
lines += ['',
          'All 90 E1 native models and all 30 E2 center-only models exactly reproduced saved zero-padding test accuracies before the padding replacement. Replicate/reflect padding changed roughly 1.1–3.4% of predictions for the base E1 readout, but mean accuracy-difference intervals crossed zero. This does not establish performance equivalence.','',
          'For all E1 conditions, the local target BY response was exactly unchanged by padding replacement: the target receptive fields do not reach the image frame. Global representations and output logits can change because they pool frame features. E2 center-only controls had no prediction or accuracy changes, with only float32 roundoff in logits (mean absolute difference about 7e-7). This supports the distinction between genuinely local induction and frame-sensitive global readouts.','',
          '**Interpretive limit:** replacing padding after training is out of the training distribution. These controls do not establish that padding caused or did not cause the learned opponent-score differences. Controlled retraining would be needed for that causal question.','',
          '## Further scope limits','',
          '- The primary scale-by-objective normalized opponent-fraction result is unchanged and remains inconclusive.',
          '- These uniform simultaneous probes do not validate human percepts, distant watercolor/Cornsweet filling-in, or signed Mach-band overshoot.',
          '- Standard production Cornsweet, Mach, and watercolor probes are not literal repeat3 pairs; the identity cannot be extended to them by assumption.',
          '- The observed edge-access fraction is a support count, not a complete quantitative response model: corner and straight-edge contributions can differ.',
          '- There is no calibrated visual-angle mapping, new scene partition, new functional cone-opponency assay, or new training in this package.',
          '', '## Reproduction commands','',
          'From the repository root, recreate this figure and report from the packaged results without downloading data or training:','',
          '```bash',
          'python reproducibility/scale_diagnostics/summarize_diagnostics.py --input reproducibility/scale_diagnostics --output generated/scale_diagnostics',
          '```','',
          'To recompute the diagnostics, first complete the full 30-seed study and prepare its natural data as described in the top-level README. Checkpoints are not included in Git. Then run the following from the repository root. Replace `PATH_TO_COMPLETED_RUN` with that run directory. The protocols must be copied before execution; all newly generated results go into a separate output directory.','',
          '```bash',
          'mkdir -p generated/scale_diagnostics',
          'cp reproducibility/scale_diagnostics/protocol.json reproducibility/scale_diagnostics/precision_protocol.json generated/scale_diagnostics/',
          'python reproducibility/scale_diagnostics/run_scale_diagnostics.py --run PATH_TO_COMPLETED_RUN --runtime . --data-dir data --output generated/scale_diagnostics',
          'python reproducibility/scale_diagnostics/check_identity_precision.py --run PATH_TO_COMPLETED_RUN --runtime . --data-dir data --output generated/scale_diagnostics',
          'python reproducibility/scale_diagnostics/summarize_diagnostics.py --input generated/scale_diagnostics --output generated/scale_diagnostics',
          '```','',
          '`--runtime` can also point to the immutable production runtime. The release resolves the imported spectral module in either layout. The summary script reads only its `--input` directory and writes report/figure artifacts to `--output`; with no options both default to its own directory. Source snapshots and fitted weights may differ for a newly trained CPU replication, so fresh scientific outcomes need not equal the recorded MPS study.','',
          'Keep the protocol files with the results. `summary.json` records the executed script, protocol, source, data-manifest, and checkpoint SHA-256 hashes plus execution times. Original execution hashes remain in the published JSON; release portability changes and their lineage are documented in `RELEASE_PROVENANCE.json`. Those historical script hashes are not claims that the portability-edited scripts are byte-identical. The original run took about 16 seconds excluding interpreter/data loading and precision confirmation. Original command invocation used `nice -n 15`; macOS denied the priority adjustment in the sandbox, so numerical thread limits provided the actual resource cap.','']
(ROOT/'README.md').write_text('\n'.join(lines))

fig,axes=plt.subplots(1,3,figsize=(13.5,4.2),gridspec_kw={'width_ratios':[1.05,1.05,1.05]})
colors=['#1769aa','#d66b19','#278653']
names={'p9_baseline':'9-trained / dilation 1','p27_fixed':'27-trained / dilation 1','p27_dilated':'27-trained / dilation 3'}
for ax,scope,label in zip(axes[:2],['local_target','global_representation'],['Local target features','Global representation']):
    for color,source in zip(colors,names):
        vals=[]
        for p,di in [(9,1),(27,1),(27,3)]:
            g=next(g for g in d['frozen_sweep'] if (g['source_condition'],g['patch_size'],g['dilation'],g['axis'])==(source,p,di,'BY'))
            vals.append(g['metrics'][scope]['normalized_shift'])
        means=np.array([v['mean'] for v in vals]);lo=np.array([v['ci95'][0] for v in vals]);hi=np.array([v['ci95'][1] for v in vals])
        ax.errorbar(np.arange(3),means,yerr=[means-lo,hi-means],marker='o',color=color,label=names[source],capsize=3,lw=1.5,ms=4)
    ax.set_xticks(range(3),['9 / d1','27 / d1','27 / d3'])
    ax.set_xlabel('Probe width / kernel dilation')
    ax.set_title(label,fontsize=11)
    ax.set_ylabel('Calibrated BY shift (assimilation +)')
    ax.spines[['top','right']].set_visible(False)
    ax.axhline(0,color='#777',lw=.6)
fig.legend(*axes[0].get_legend_handles_labels(),frameon=False,fontsize=8,loc='lower center',bbox_to_anchor=(.5,-.05),ncol=3)
ax=axes[2]
order=['p9_baseline','p27_fixed','p27_dilated','E2_intact_center_only']
for j,mode in enumerate(['replicate','reflect']):
    vals=[next(g for g in d['padding'] if g['source_condition']==source and g['padding']==mode)['metrics']['accuracy_difference'] for source in order]
    means=np.array([v['mean'] for v in vals])*100;lo=np.array([v['ci95'][0] for v in vals])*100;hi=np.array([v['ci95'][1] for v in vals])*100
    y=np.arange(4)+(j-.5)*.16
    ax.errorbar(means,y,xerr=[means-lo,hi-means],fmt='o',capsize=3,label=mode,ms=4,color=['#6b44a1','#555555'][j])
ax.axvline(0,color='#777',lw=.8)
ax.set_yticks(range(4),['9 / d1','27 / d1','27 / d3','Center-only'])
ax.set_xlabel('Accuracy change (percentage points)')
ax.set_title('Zero-shot padding replacement',fontsize=11)
ax.invert_yaxis();ax.spines[['top','right']].set_visible(False);ax.legend(frameon=False,fontsize=8,loc='lower right')
fig.suptitle('Frozen weights separate acute geometry from training-dependent representations',fontsize=12,y=1.02)
fig.tight_layout()
fig.savefig(ROOT/'scale_diagnostics.pdf',bbox_inches='tight')
fig.savefig(ROOT/'scale_diagnostics.png',dpi=180,bbox_inches='tight')
print('Saved README and figure')
