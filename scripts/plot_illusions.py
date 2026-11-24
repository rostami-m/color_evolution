#!/usr/bin/env python3
"""Render the completed-run audit without loading checkpoints or fitting models.

Portable layout: this file lives in figures/ beside ../illusions_utility/.
Run with Python + NumPy + Matplotlib; optionally pass --package-root DIR.
"""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import numpy as np


BLUE = '#246B9E'
ORANGE = '#C56A20'
GREEN = '#23856C'
GRAY = '#68717C'
INK = '#172C3C'


def interval(ax, record, y, color, marker='o', label=None):
    mean = record['mean']
    lo, hi = record['ci95']
    ax.errorbar(mean, y, xerr=[[max(0, mean-lo)], [max(0, hi-mean)]],
                fmt=marker, color=color, markersize=4.2,
                markeredgecolor='white', markeredgewidth=.7,
                elinewidth=1.1, capsize=2.0, label=label, zorder=3)


def style(ax, title, panel, xlabel):
    ax.set_title(f'{panel}  {title}', loc='left', pad=9,
                 fontsize=13, fontweight='bold', color=INK)
    ax.set_xlabel(xlabel, labelpad=5, fontsize=12.5)
    ax.spines[['top', 'right', 'left']].set_visible(False)
    ax.spines['bottom'].set_color('#B8C1C9')
    ax.tick_params(axis='y', length=0, pad=4)
    ax.tick_params(axis='x', color='#B8C1C9')
    ax.set_axisbelow(True)
    ax.grid(axis='x', color='#E6EAEE', linewidth=.8)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package-root', type=Path,
                        default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output-dir', type=Path)
    args = parser.parse_args()
    package = args.package_root.resolve()
    output = args.output_dir or package/'figures'
    output.mkdir(parents=True, exist_ok=True)
    source = package/'illusions_utility'
    audit = json.loads((source/'audit.json').read_text())
    extra = json.loads((source/'additional_audit.json').read_text())
    plt.rcParams.update({
        'font.family': 'DejaVu Sans', 'font.size': 12.5, 'xtick.labelsize':12.5, 'ytick.labelsize':12.5,
        'text.color': INK, 'axes.labelcolor': INK,
        'xtick.color': INK, 'ytick.color': INK,
        'pdf.fonttype': 42, 'ps.fonttype': 42,
        'figure.facecolor': 'white', 'axes.facecolor': 'white',
    })
    fig, axes = plt.subplots(3, 2, figsize=(8.2, 8.5))
    fig.subplots_adjust(left=.20, right=.98, bottom=.08, top=.93,
                        wspace=1.10, hspace=.82)

    def probes(group):
        return audit['illusions'][group]['axes']['BY']

    groups = [
        ('Base 9', 'E1/p9_baseline/classify'),
        ('Base 27', 'E1/p27_fixed/classify'),
        ('Learn. 9', 'E3/p9_learned_b_0/classify'),
        ('Learn. 27', 'E3/p27_learned_b_0/classify'),
    ]
    # A: polarity-odd simultaneous induction, representation versus local target.
    ax = axes[0,0]
    style(ax, 'Global / local\ninduction', 'A',
          'Signed BY shift')
    ys = np.arange(4)[::-1]
    labels = []
    for i, ((label, group), y) in enumerate(zip(groups, ys)):
        p = probes(group)
        glob = p['simultaneous_odd_readout_shift']
        local = p['simultaneous_odd_local_target_shift']
        interval(ax, glob, y+.11, BLUE, label='Global' if i == 0 else None)
        interval(ax, local, y-.11, ORANGE, marker='s',
                 label='Local' if i == 0 else None)
        labels.append(f'{label} ({glob["n"]}/{local["n"]})')
    ax.axvline(0, color=GRAY, lw=1.0, zorder=1)
    ax.set(yticks=ys, yticklabels=labels, ylim=(-.55, 5.1), xlim=(-.061, .084))
    ax.set_xticks([-.04, 0, .08])
    ax.legend(frameon=True, facecolor='white', edgecolor='none', framealpha=1,
              fontsize=12.5, loc='upper left',
              bbox_to_anchor=(-.02, 1.025), handletextpad=.45)

    # B: closed watercolor contour: near response but no distant interior response.
    ax = axes[0,1]
    style(ax, 'Contour response', 'B',
          'Signed BY shift')
    selected = [groups[0], groups[1], groups[3]]
    ys = np.arange(3)[::-1]
    labels = []
    for i, ((label, group), y) in enumerate(zip(selected, ys)):
        p = probes(group)
        close = p['watercolor_closed_near_contour_shift']
        far = p['watercolor_closed_far_interior_shift']
        interval(ax, close, y+.12, ORANGE, label='Near' if i == 0 else None)
        interval(ax, far, y-.12, BLUE, marker='D',
                 label='Distant' if i == 0 else None)
        labels.append(f'{label} ({close["n"]})')
    ax.axvline(0, color=GRAY, lw=1.0, zorder=1)
    ax.set(yticks=ys, yticklabels=labels, ylim=(-.5, 4.2), xlim=(-.008, .067))
    ax.set_xticks([0, .03, .06])
    ax.legend(frameon=True, facecolor='white', edgecolor='none', framealpha=1,
              fontsize=12.5, loc='upper left',
              bbox_to_anchor=(-.02, 1.025), handletextpad=.45)

    # C: polarity-resolved Cornsweet comparisons, uncontaminated distant ROIs.
    ax = axes[1,0]
    style(ax, 'Cornsweet response', 'C',
          'Left − right BY shift')
    p = probes('E1/p27_fixed/classify')
    for i, (polarity, y) in enumerate([(1, 1), (-1, 0)]):
        interval(ax, p[f'cornsweet_{polarity}_near_signed_difference'], y+.12,
                 ORANGE, label='Near cusp' if i == 0 else None)
        interval(ax, p[f'cornsweet_{polarity}_distant_signed_difference'], y-.12,
                 BLUE, marker='D', label='Distant' if i == 0 else None)
    ax.axvline(0, color=GRAY, lw=1.0, zorder=1)
    ax.set(yticks=[1, 0], yticklabels=['Positive (28)', 'Reversed (28)'],
           ylim=(-.6, 2.7), xlim=(-.0125, .0125))
    ax.set_xticks([-.01, 0, .01])
    ax.legend(frameon=True, facecolor='white', edgecolor='none', framealpha=1,
              fontsize=12.5, loc='upper left',
              bbox_to_anchor=(-.02, 1.025), handletextpad=.45)

    # D: sign is retained; positive canonical index denotes bright-high/dark-low.
    ax = axes[1,1]
    style(ax, 'Mach response', 'D',
          'Signed Mach index')
    ys = np.arange(4)[::-1]
    labels = []
    for (label, group), y in zip(groups, ys):
        rec = extra['mach_and_contour'][group+'/BY']['mach_odd_canonical']
        interval(ax, rec, y, BLUE)
        labels.append(f'{label} ({rec["n"]})')
    ax.axvline(0, color=GRAY, lw=1.0, zorder=1)
    ax.set(yticks=ys, yticklabels=labels, ylim=(-.45, 3.65), xlim=(-.0045, .0016))
    ax.set_xticks([-.004, -.002, 0])

    # E: same units for weighting locus and inferred peak; descriptive finite window.
    ax = axes[2,0]
    style(ax, 'Peak tracking', 'E',
          'Peak-location slope')
    ys = [2, 1, 0]
    for i, (mode, y) in enumerate(zip(['frequency', 'loss', 'both'], ys)):
        s = audit['utility_slopes']['E4/'+mode]
        interval(ax, s['sensitivity_peak_by'], y+.12, GREEN,
                 label='Raw' if i == 0 else None)
        interval(ax, s['normalized_sensitivity_peak_by'], y-.12, ORANGE, marker='s',
                 label='RMS norm.' if i == 0 else None)
    ax.axvline(0, color=GRAY, lw=1.0, zorder=1)
    ax.set(yticks=ys, yticklabels=['Frequency (27)', 'Loss (27)', 'Both (27)'],
           ylim=(-.5, 4.2), xlim=(-.13, .102))
    ax.set_xticks([-.1, 0, .1])
    ax.legend(frameon=True, facecolor='white', edgecolor='none', framealpha=1,
              fontsize=12.5, loc='upper left',
              bbox_to_anchor=(-.02, 1.025), handletextpad=.45)

    # F: direct completed E5f summaries; eight scenes, fixed generated illumination.
    ax = axes[2,1]
    style(ax, 'Spatial correlation', 'F',
          'Separation (pixels)')
    distances = np.array([1, 2, 4, 8, 16, 32, 64])
    for field, label, color, marker in [
        ('lm_correlation', 'RG', BLUE, 'o'),
        ('s_lm_correlation', 'BY', ORANGE, 's'),
    ]:
        records = [audit['grounding']['spatial'][str(d)][field] for d in distances]
        means = np.array([r['mean'] for r in records])
        cis = np.array([r['ci95'] for r in records])
        ax.plot(distances, means, color=color, marker=marker, markersize=5,
                linewidth=1.8, label=label)
        ax.fill_between(distances, cis[:, 0], cis[:, 1], color=color, alpha=.13,
                        linewidth=0)
    ax.set_xscale('log', base=2)
    ax.set_xticks([1,4,16,64], ['1','4','16','64'])
    ax.set_ylim(.2, 1.04)
    ax.set_yticks([.2, .6, 1.0])
    ax.set_ylabel('Pearson correlation', fontsize=12.5, labelpad=8)
    ax.spines['left'].set_visible(True)
    ax.spines['left'].set_color('#B8C1C9')
    ax.grid(axis='y', color='#E6EAEE', linewidth=.8)
    ax.legend(frameon=False, fontsize=12.5, loc='lower left')

    stem = output/'illusion_results'
    fig.savefig(stem.with_suffix('.pdf'), facecolor='white')
    fig.savefig(stem.with_suffix('.png'), dpi=180, facecolor='white')
    plt.close(fig)
    print(stem.with_suffix('.pdf'))
    print(stem.with_suffix('.png'))


if __name__ == '__main__':
    main()
