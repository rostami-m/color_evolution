#!/usr/bin/env python3
"""Render the six-figure study from audited summaries, without model fitting.

The two patch sizes are displayed as matched experimental conditions. Saved
descriptive intervals are copied, never recomputed here. The fixed-weight
diagnostics remain a separate post-training analysis. A figure_source_data.json
file records every plotted summary and the SHA-256 of every input.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path

os.environ.setdefault('MPLCONFIGDIR', '/tmp/color_study_mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, TwoSlopeNorm
from matplotlib.patches import FancyBboxPatch, Patch, Rectangle
import numpy as np


INK = '#173447'
BLUE = '#146D8D'
ORANGE = '#BB592C'
PURPLE = '#8762A2'
GREEN = '#388261'
GRAY = '#77818A'
SIZE = {9: BLUE, 27: ORANGE}
MODE = {'untrained': GRAY, 'shuffled': PURPLE, 'classify': BLUE, 'regress': ORANGE}
CONDITIONS = ['p9_baseline', 'p27_fixed', 'p27_dilated', 'p27_coarse']
GEOM_LABELS = ['9×9\nd=1', '27×27\nd=1', '27×27\nd=3', '27×27\ncoarse']


class StudyFigures:
    def __init__(self, bundle, diagnostics, out):
        self.bundle, self.out = bundle, out
        out.mkdir(parents=True, exist_ok=True)
        self.sources = {}
        self.records = []
        self.layout_checks = []
        self.primary = self.read(bundle/'primary/primary_analysis.json', 'primary')
        self.robust = self.read(bundle/'robustness/audit.json', 'robustness')
        self.cma_init = self.read(bundle/'robustness/cma_initialization_audit.json', 'cma_initialization')
        self.illusions = self.read(bundle/'illusions_utility/audit.json', 'illusions')
        self.extra = self.read(bundle/'illusions_utility/additional_audit.json', 'additional')
        self.raw = self.read(bundle/'raw_decoding/summary.json', 'raw_decoding')
        self.diag = self.read(diagnostics/'summary.json', 'fixed_weights')
        self.geo = self.read(bundle/'scale_geometry_data.json', 'geometry')
        self.groups = {(g['stage'], g['condition'], g['mode']): g['metrics']
                       for g in self.primary['groups']}
        self.robust_groups = {(g['stage'], g['condition'], g['mode']): g['metrics']
                              for g in self.robust['groups']}
        plt.rcParams.update({
            'font.family': 'DejaVu Sans', 'font.size': 12.5,
            'axes.titlesize': 13, 'axes.labelsize': 12.5,
            'xtick.labelsize': 12.5, 'ytick.labelsize': 12.5,
            'legend.fontsize': 12.5, 'pdf.fonttype': 42, 'ps.fonttype': 42,
            'axes.spines.top': False, 'axes.spines.right': False,
            'text.color': INK, 'axes.labelcolor': INK,
            'xtick.color': INK, 'ytick.color': INK,
            'axes.titleweight': 'bold', 'legend.framealpha': 1.,
            'legend.edgecolor': '#DDE3E7', 'figure.facecolor': 'white',
        })

    def read(self, path, name):
        self.sources[name] = {'file': path.name,
                              'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
        return json.loads(path.read_text())

    def metric(self, condition, mode, metric, stage='E1'):
        return self.groups[(stage, condition, mode)][metric]

    def probe(self, group, metric):
        return self.illusions['illusions'][group]['axes']['BY'][metric]

    def record(self, panel, label, stat, multiplier=1.):
        self.records.append({'panel': panel, 'label': label,
                             'display_multiplier': multiplier, 'source_summary': stat})

    def points(self, ax, xs, records, color, label, panel, marker='o',
               line=False, multiplier=1.):
        means = np.array([s['mean'] for s in records])*multiplier
        ci = np.array([s['ci95'] for s in records])*multiplier
        ax.errorbar(xs, means, yerr=[np.maximum(0, means-ci[:, 0]),
                                    np.maximum(0, ci[:, 1]-means)],
                    color=color, marker=marker, ls='-' if line else 'none',
                    capsize=2.5, markersize=5.3, lw=1.3, label=label)
        for x, stat in zip(xs, records):
            self.record(panel, f'{label}; x={x}', stat, multiplier)

    def interval(self, ax, stat, y, color, panel, label=None,
                 marker='o', multiplier=1.):
        mean = stat['mean']*multiplier
        lo, hi = np.array(stat['ci95'])*multiplier
        ax.errorbar(mean, y, xerr=[[max(0, mean-lo)], [max(0, hi-mean)]],
                    fmt=marker, color=color, markersize=5.4, capsize=2.5,
                    lw=1.3, label=label)
        self.record(panel, f'{label}; y={y}', stat, multiplier)

    @staticmethod
    def style(ax, title, xlabel=None, ylabel=None, horizontal=False):
        ax.set_title(title, loc='left', pad=12)
        if xlabel:
            ax.set_xlabel(xlabel, labelpad=7)
        if ylabel:
            ax.set_ylabel(ylabel, labelpad=7)
        ax.set_axisbelow(True)
        ax.grid(axis='x' if horizontal else 'y', color='#E4E9ED', lw=.8)
        if horizontal:
            ax.spines['left'].set_visible(False)
            ax.tick_params(axis='y', length=0)

    def save(self, fig, stem):
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        bounds = fig.bbox
        outside = []
        from matplotlib.text import Text
        for obj in fig.findobj(match=Text):
            if not obj.get_visible() or not obj.get_text():
                continue
            box = obj.get_window_extent(renderer)
            if box.x0 < -1 or box.y0 < -1 or box.x1 > bounds.x1+1 or box.y1 > bounds.y1+1:
                outside.append(obj.get_text())
        self.layout_checks.append({'figure': stem, 'text_outside_canvas': outside})
        if outside:
            raise ValueError(f'{stem}: text outside figure canvas: {outside}')
        fig.savefig(self.out/(stem+'.pdf'), facecolor='white')
        fig.savefig(self.out/(stem+'.png'), facecolor='white', dpi=180)
        plt.close(fig)
        print(self.out/(stem+'.pdf'))

    @staticmethod
    def box(ax, x, y, w, h, label, color='#EAF2F5'):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=.012',
                                   facecolor=color, edgecolor='#91A4B0', lw=.9, clip_on=False))
        ax.text(x+w/2, y+h/2, label, va='center', ha='center', fontsize=12.5)

    @staticmethod
    def arrow(ax, a, b):
        ax.annotate('', xy=b, xytext=a,
                    arrowprops={'arrowstyle': '-|>', 'color': INK, 'lw': 1.3})

    def design(self):
        fig = plt.figure(figsize=(8.2, 7.6))
        top = fig.add_axes([.04, .765, .92, .20])
        top.axis('off')
        top.text(0, 1., 'A  Spectral stimulus construction', fontsize=13,
                 fontweight='bold', va='top')
        labels = [('Natural-scene\nreflectance', '#F3E8D9'),
                  ('Generated\nPlanck illuminant', '#F6F0D9'),
                  ('Cone projection\nL, M, S', '#E5F0E9'),
                  ('Centered patches\n9×9 and 27×27', '#EAF2F5')]
        for i, (label, color) in enumerate(labels):
            self.box(top, .01+i*.254, .20, .21, .49, label, color)
            if i == 0:
                top.text(.242, .445, '×', ha='center', va='center', fontsize=16)
            elif i < 3:
                self.arrow(top, (.224+i*.254, .445), (.259+i*.254, .445))
        top.text(.5, .02, 'Same target-to-patch side ratio (1:3); paired seed blocks',
                 ha='center', va='bottom', fontsize=12.5)

        model = fig.add_axes([.04, .49, .92, .23])
        model.axis('off')
        model.text(0, 1., 'B  Matched architecture, separate training objectives', fontsize=13,
                   fontweight='bold', va='top')
        labels = ['3×3 conv.\n8 + ReLU', '1×1 conv.\n4 + ReLU',
                  'Target mean +\nglobal mean', 'Dense 16\n+ ReLU']
        for i, label in enumerate(labels):
            self.box(model, .005+i*.183, .31, .155, .38, label)
            if i < 3:
                self.arrow(model, (.165+i*.183, .5), (.184+i*.183, .5))
        self.box(model, .77, .52, .215, .25, 'Category\n2 logits', '#E4F0F4')
        self.box(model, .77, .13, .215, .25, 'Illuminant\n1 output', '#F8E8DF')
        self.arrow(model, (.715, .5), (.765, .64))
        self.arrow(model, (.715, .5), (.765, .26))
        model.text(.35, .095, 'Independent training; matched initial convolutional weights',
                   ha='center', va='bottom', fontsize=12.5)

        colors = ['#E8EDF1', '#F7F1E5', BLUE, '#DB9A49']
        cmap = ListedColormap(colors)
        for j, row in enumerate(self.geo['rows']):
            ax = fig.add_axes([.055+j*.323, .185, .245, .245])
            n, t, d = (row[k] for k in ('patch_size', 'target_width', 'dilation'))
            yy, xx = np.indices((n, n))
            lo, hi = (n-t)//2, (n+t)//2
            target = (yy >= lo) & (yy < hi) & (xx >= lo) & (xx < hi)
            access, padding = np.zeros_like(target), np.zeros_like(target)
            for dy in (-d, 0, d):
                for dx in (-d, 0, d):
                    sy, sx = yy+dy, xx+dx
                    inside = (sy >= 0) & (sy < n) & (sx >= 0) & (sx < n)
                    inside_target = (sy >= lo) & (sy < hi) & (sx >= lo) & (sx < hi)
                    access |= target & inside & ~inside_target
                    padding |= ~inside
            assert int(access.sum()) == row['geometry']['target_pixels_reaching_surround']
            assert int(padding.sum()) == row['geometry']['frame_pixels_reaching_zero_padding']
            values = np.zeros((n, n), int)
            values[target], values[access], values[padding] = 1, 2, 3
            ax.imshow(values, cmap=cmap, vmin=0, vmax=3, interpolation='nearest')
            ax.set_xticks(np.arange(-.5, n, 1), minor=True)
            ax.set_yticks(np.arange(-.5, n, 1), minor=True)
            ax.grid(which='minor', color='white', linewidth=.3 if n == 27 else .6)
            ax.tick_params(which='both', bottom=False, left=False,
                           labelbottom=False, labelleft=False)
            ax.add_patch(Rectangle((lo-.5, lo-.5), t, t, fill=False, edgecolor=INK, lw=1.1))
            ax.set_title(f'{chr(67+j)}  {n}×{n}; d={d}\nTarget {t}×{t}',
                         fontsize=13, pad=10)
            ax.text(.5, -.11, f"Target access: {100*access.sum()/target.sum():.1f}%",
                    transform=ax.transAxes, ha='center', fontsize=12.5, color=BLUE)
            ax.text(.5, -.23, f"Frame access: {100*padding.mean():.1f}%",
                    transform=ax.transAxes, ha='center', fontsize=12.5, color='#8A5B17')
            self.records.append({'panel': 'design/'+chr(67+j), 'exact_geometry': row['geometry'],
                                 'patch_size': n, 'target_width': t, 'dilation': d})
        fig.legend(handles=[Patch(facecolor=colors[2], label='Target samples surround'),
                            Patch(facecolor=colors[1], edgecolor=INK, label='Target samples target only'),
                            Patch(facecolor=colors[3], label='Position samples padding')],
                   loc='lower center', bbox_to_anchor=(.5, .003), frameon=False,
                   ncol=1, fontsize=12.5, labelspacing=.35)
        self.save(fig, 'study_design')

    def organization(self):
        fig, axes = plt.subplots(3, 2, figsize=(8.2, 8.6))
        fig.subplots_adjust(left=.12, right=.98, top=.89, bottom=.12,
                            wspace=.55, hspace=.85)
        for ax, metric, title, ylabel in [
            (axes[0, 0], 'legacy_chromatic_power', 'A  Chromatic amplitude', 'Weight amplitude'),
            (axes[0, 1], 'normalized_chromatic_power', 'B  Chromatic energy', 'Normalized energy')]:
            for i, (mode, label) in enumerate([('untrained', 'Initialized'),
                                              ('shuffled', 'Shuffled'), ('classify', 'Classifier')]):
                self.points(ax, np.arange(2)+(i-1)*.15,
                            [self.metric(c, mode, metric) for c in CONDITIONS[:2]],
                            MODE[mode], label, title)
            self.style(ax, title, ylabel=ylabel)
            ax.set_xticks([0, 1], ['9×9', '27×27'])
        axes[0, 0].set_ylim(0, .85)
        fig.legend(*axes[0, 0].get_legend_handles_labels(), loc='upper center',
                   bbox_to_anchor=(.54, .995), ncol=3, handletextpad=.4,
                   columnspacing=1.1, frameon=False)
        axes[0, 1].set_ylim(.50, .79)

        for ax, metric, title, ylabel, multiplier in [
            (axes[1, 0], 'legacy_count', 'C  Amplitude counts', 'Filters above null / 8', 1),
            (axes[1, 1], 'double_opponent_fraction', 'D  Normalized fractions', 'Above null (%)', 100),
            (axes[2, 0], 'double_opponency_score', 'E  Normalized score', 'Opponent score', 1)]:
            for offset, mode, label in [(-.11, 'classify', 'Classifier'), (.11, 'regress', 'Regressor')]:
                self.points(ax, np.arange(4)+offset,
                            [self.metric(c, mode, metric) for c in CONDITIONS],
                            MODE[mode], label, title, multiplier=multiplier)
            self.style(ax, title, ylabel=ylabel)
            ax.set_xticks(range(4), GEOM_LABELS)
            if metric != 'legacy_count':
                ref = self.metric('p9_baseline', 'untrained', metric)
                ax.axhline(ref['mean']*multiplier, color=GRAY, ls='--', lw=1.2,
                           label='Initialized mean')
                self.record(title, 'Initialized reference', ref, multiplier)
        axes[1, 0].set_ylim(-.1, 6.3)
        axes[1, 0].legend(loc='upper right', handletextpad=.4)
        axes[1, 1].set_ylim(-.5, 19)
        axes[2, 0].set_ylim(0, .38)
        axes[2, 0].legend(loc='upper right', fontsize=12.5, handletextpad=.4)

        ax = axes[2, 1]
        self.style(ax, 'F  Primary interaction', 'Difference in fractions\n(percentage points)', horizontal=True)
        contrast = next(c for c in self.primary['frozen_primary_comparisons']
                        if c['condition'] == 'PRIMARY_scale_by_objective')
        self.interval(ax, contrast['summary'], 0, BLUE, 'organization/F', multiplier=100)
        ax.axvline(0, color=GRAY, lw=1.1)
        ax.set(xlim=(-8, 3), ylim=(-.8, .8), yticks=[], xticks=[-6, -3, 0, 3])
        ax.text(.03, .94, '(Classifier − regressor)\nat 27×27 minus 9×9',
                transform=ax.transAxes, fontsize=12.5, va='top')
        ax.text(.03, .06, 'Holm-adjusted p = 1.00', transform=ax.transAxes,
                fontsize=12.5, va='bottom')
        self.save(fig, 'learned_organization')

    def task_reference(self):
        fig, axes = plt.subplots(2, 2, figsize=(8.2, 6.5))
        fig.subplots_adjust(left=.12, right=.98, top=.92, bottom=.10,
                            wspace=.51, hspace=.66)
        ax = axes[0, 0]
        self.style(ax, 'A  Category learning', ylabel='Accuracy')
        for offset, metric, label, color in [(-.16, 'train_accuracy', 'Train', GRAY),
                                             (0, 'validation_accuracy', 'Validation', GREEN),
                                             (.16, 'test_accuracy', 'Test', BLUE)]:
            records = [self.metric('p9_baseline', 'classify', metric),
                       self.metric('p27_fixed', 'classify', metric),
                       self.metric('p9', 'classify', metric, 'E0_synthetic'),
                       self.metric('p27', 'classify', metric, 'E0_synthetic')]
            self.points(ax, np.arange(4)+offset, records, color, label, 'task/A')
        ax.set(ylim=(0, 1.04), xticks=range(4),
               xticklabels=['Natural\n9', 'Natural\n27', 'Synth.\n9', 'Synth.\n27'])
        ax.legend(loc='lower left', labelspacing=.25)

        ax = axes[0, 1]
        self.style(ax, 'B  Reference information', ylabel='Illuminant R²')
        for i, p in enumerate([9, 27]):
            default = self.metric(CONDITIONS[i], 'regress', 'test_r2')
            neutral = self.robust_groups[('E5b', f'p{p}_surround_neutral', 'regress')]['test/r2']
            self.points(ax, np.arange(2)+(-.08 if p == 9 else .08), [default, neutral],
                        SIZE[p], f'{p}×{p}', 'task/B')
        ax.axhline(0, color=GRAY, lw=1)
        ax.set(xticks=[0, 1], xticklabels=['Unknown', 'Neutral'], ylim=(-1.05, 1.45))
        ax.legend(loc='upper left', ncol=2, columnspacing=.8, handletextpad=.3)

        for ax, metric, title, ylabel in [
            (axes[1, 0], 'test_classification_accuracy', 'C  Raw-cone category\ndecoding', 'Accuracy'),
            (axes[1, 1], 'test_illuminant_r2', 'D  Raw-cone illuminant\ndecoding', 'Illuminant R²')]:
            self.style(ax, title, 'Additional pixel-noise SD', ylabel)
            for p, cond in zip([9, 27], CONDITIONS[:2]):
                records = sorted((g for g in self.raw['groups'] if g['condition'] == cond),
                                 key=lambda g: g['additional_pixel_noise'])
                self.points(ax, np.array([g['additional_pixel_noise'] for g in records]),
                            [g['metrics'][metric] for g in records], SIZE[p], f'{p}×{p}',
                            title, marker='o' if p == 9 else 's', line=True)
            ax.set_xticks([0, .02, .05], ['0', '0.02', '0.05'])
        axes[1, 0].set_ylim(.64, .84)
        axes[1, 0].legend(loc='lower left', ncol=2, columnspacing=.8)
        axes[1, 1].axhline(0, color=GRAY, lw=1)
        axes[1, 1].set_ylim(-1.20, .08)
        self.save(fig, 'task_and_reference')

    def induction(self):
        fig, axes = plt.subplots(2, 2, figsize=(8.2, 6.9))
        fig.subplots_adjust(left=.19, right=.98, top=.90, bottom=.10,
                            wspace=1.04, hspace=.62)
        groups = [('Base 9', 'E1/p9_baseline/classify'),
                  ('Base 27', 'E1/p27_fixed/classify'),
                  ('Learn. 9', 'E3/p9_learned_b_0/classify'),
                  ('Learn. 27', 'E3/p27_learned_b_0/classify')]
        ys = np.arange(4)[::-1]
        ax = axes[0, 0]
        self.style(ax, 'A  Readout and local\ninduction', 'Signed BY shift', horizontal=True)
        labels = []
        for i, ((label, group), y) in enumerate(zip(groups, ys)):
            glob = self.probe(group, 'simultaneous_odd_readout_shift')
            local = self.probe(group, 'simultaneous_odd_local_target_shift')
            self.interval(ax, glob, y+.13, BLUE, 'induction/A', 'Global' if i == 0 else None)
            self.interval(ax, local, y-.13, ORANGE, 'induction/A', 'Local' if i == 0 else None, marker='s')
            labels.append(f'{label}\n({glob["n"]}/{local["n"]})')
        ax.set(yticks=ys, yticklabels=labels, xlim=(-.061, .083), ylim=(-.65, 5.0),
               xticks=[-.04, 0, .04, .08])
        ax.legend(loc='upper left', handletextpad=.3, labelspacing=.25)

        ax = axes[0, 1]
        self.style(ax, 'B  Contour response', 'Signed BY shift', horizontal=True)
        labels = []
        for i, ((label, group), y) in enumerate(zip(groups, ys)):
            close = self.probe(group, 'watercolor_closed_near_contour_shift')
            far = self.probe(group, 'watercolor_closed_far_interior_shift')
            self.interval(ax, close, y+.13, ORANGE, 'induction/B', 'Near' if i == 0 else None)
            self.interval(ax, far, y-.13, BLUE, 'induction/B', 'Distant' if i == 0 else None, marker='D')
            labels.append(f'{label} ({close["n"]})')
        ax.set(yticks=ys, yticklabels=labels, xlim=(-.008, .067), ylim=(-.65, 5.0),
               xticks=[0, .03, .06])
        ax.legend(loc='upper left', handletextpad=.3, labelspacing=.25)

        ax = axes[1, 0]
        self.style(ax, 'C  Cornsweet response', 'Left − right BY shift', horizontal=True)
        labels = []
        for i, (p, polarity) in enumerate([(9, 1), (9, -1), (27, 1), (27, -1)]):
            group = 'E1/'+('p9_baseline' if p == 9 else 'p27_fixed')+'/classify'
            near = self.probe(group, f'cornsweet_{polarity}_near_signed_difference')
            far = self.probe(group, f'cornsweet_{polarity}_distant_signed_difference')
            self.interval(ax, near, ys[i]+.13, ORANGE, 'induction/C', 'Near' if i == 0 else None)
            self.interval(ax, far, ys[i]-.13, BLUE, 'induction/C', 'Distant' if i == 0 else None, marker='D')
            labels.append(f'{p}, {"positive" if polarity == 1 else "reversed"}\n({near["n"]})')
        ax.set(yticks=ys, yticklabels=labels, xlim=(-.0125, .0125), ylim=(-.65, 5.0),
               xticks=[-.01, 0, .01])
        ax.legend(loc='upper left', handletextpad=.3, labelspacing=.25)

        ax = axes[1, 1]
        self.style(ax, 'D  Mach response', 'Signed Mach index', horizontal=True)
        labels = []
        for (label, group), y in zip(groups, ys):
            rec = self.extra['mach_and_contour'][group+'/BY']['mach_odd_canonical']
            self.interval(ax, rec, y, BLUE, 'induction/D')
            labels.append(f'{label} ({rec["n"]})')
        ax.set(yticks=ys, yticklabels=labels, xlim=(-.0045, .0016), ylim=(-.65, 5.0),
               xticks=[-.004, -.002, 0])
        ax.text(.02, .96, 'Negative: smoothing\nPositive: overshoot',
                transform=ax.transAxes, va='top', fontsize=12.5)
        for ax in axes.flat:
            ax.axvline(0, color=GRAY, lw=1.0)
        self.save(fig, 'signed_induction')

    def fixed_weights(self):
        fig, axes = plt.subplots(2, 2, figsize=(8.2, 6.7))
        fig.subplots_adjust(left=.12, right=.98, top=.91, bottom=.12,
                            wspace=.53, hspace=.67)
        probes = [(9, 1), (27, 1), (27, 3)]
        sources = [('p9_baseline', 'Trained 9×9', BLUE, 'o'),
                   ('p27_fixed', 'Trained 27×27', ORANGE, 's'),
                   ('p27_dilated', 'Trained 27×27, d=3', GREEN, '^')]
        for ax, scope, title in [(axes[0, 0], 'local_target', 'A  Fixed weights:\nlocal BY'),
                                 (axes[0, 1], 'global_representation', 'B  Fixed weights:\nglobal BY')]:
            self.style(ax, title, 'Probe geometry', 'Signed shift')
            for i, (source, label, color, marker) in enumerate(sources):
                records = [next(r for r in self.diag['frozen_sweep']
                                if r['source_condition'] == source and r['patch_size'] == p
                                and r['dilation'] == d and r['axis'] == 'BY')['metrics'][scope]['normalized_shift']
                           for p, d in probes]
                self.points(ax, np.arange(3)+(i-1)*.045, records, color, label,
                            title, marker=marker, line=True)
            ax.set(xticks=range(3), xticklabels=GEOM_LABELS[:3], ylim=(0, .13))
        axes[0, 0].legend(loc='upper left', labelspacing=.3, handletextpad=.4)
        labels = ['9×9', '27×27', '27×27\nd=3', 'Center\nonly']
        sources = [r[0] for r in sources]+['E2_intact_center_only']
        for ax, metric, title, ylabel in [
            (axes[1, 0], 'prediction_change_fraction', 'C  Padding: predictions', 'Changed predictions (%)'),
            (axes[1, 1], 'accuracy_difference', 'D  Padding: accuracy', 'Accuracy change (pp)')]:
            self.style(ax, title, ylabel=ylabel)
            for shift, padding, color, label in [(-.10, 'replicate', BLUE, 'Replicate'),
                                                (.10, 'reflect', ORANGE, 'Reflect')]:
                records = [next(r for r in self.diag['padding']
                                if r['source_condition'] == source and r['padding'] == padding)['metrics'][metric]
                           for source in sources]
                self.points(ax, np.arange(4)+shift, records, color, label, title, multiplier=100)
            ax.set_xticks(range(4), labels)
            ax.axhline(0, color=GRAY, lw=1.)
        axes[1, 0].set_ylim(-.15, 7.2)
        axes[1, 0].legend(loc='upper right', labelspacing=.3, handletextpad=.4)
        axes[1, 1].set_ylim(-1.25, 1.9)
        self.save(fig, 'fixed_weight_controls')

    def robustness_context(self):
        fig = plt.figure(figsize=(8.2, 9.1))
        grid = fig.add_gridspec(3, 2, left=.13, right=.97, top=.925, bottom=.075,
                               wspace=.65, hspace=.94)
        for col, metric, title in [(0, 'legacy_double_opponent_fraction', 'A  Amplitude fraction'),
                                    (1, 'double_opponent_fraction', 'B  Normalized fraction')]:
            inner = grid[0, col].subgridspec(2, 1, hspace=.55)
            for ri, p in enumerate([9, 27]):
                ax = fig.add_subplot(inner[ri])
                data = np.empty((3, 4))
                for j, b in enumerate([2, 4, 8]):
                    for i, k in enumerate([4, 8, 16, 32]):
                        cond = ('p9_baseline' if p == 9 else 'p27_fixed') if (k, b) == (8, 4) else f'p{p}_k{k}_b{b}'
                        rec = next(c for c in self.robust['comparisons'] if c['stage'] == 'E5a'
                                   and c['condition'] == cond and c['comparison'] == 'classify_minus_regress'
                                   and c['metric'] == metric)
                        data[j, i] = 100*rec['summary']['mean']
                        self.record(f'robustness/{chr(65+col)}', f'p={p}; k={k}; b={b}', rec['summary'], 100)
                im = ax.imshow(data, aspect='auto', cmap='RdBu_r',
                               norm=TwoSlopeNorm(vmin=-40, vcenter=0, vmax=40))
                ax.set(xticks=range(4), xticklabels=['4', '8', '16', '32'] if ri else [],
                       yticks=range(3), yticklabels=['2', '4', '8'])
                ax.set_title(f'{p}×{p}', fontsize=12.5, pad=4, fontweight='normal')
                if ri == 1:
                    ax.set_xlabel('First-layer filters', labelpad=4)
                if ri == 0:
                    ax.text(0, 1.75, title, transform=ax.transAxes, fontweight='bold', fontsize=13)
                for j in range(3):
                    for i in range(4):
                        ax.text(i, j, str(round(data[j,i])), ha='center', va='center',
                                fontsize=12.5, color='white' if abs(data[j,i]) > 25 else INK)
                ax.tick_params(length=0)
            fig.text(.075 if col == 0 else .60, .84, 'Bottleneck', fontsize=12.5,
                     rotation=90, ha='center', va='center')
        cax = fig.add_axes([.35, .685, .34, .013])
        cb = fig.colorbar(im, cax=cax, orientation='horizontal', ticks=[-40, 0, 40])
        cb.set_label('Classifier − regressor (pp)', fontsize=12.5, labelpad=1)
        cb.ax.tick_params(labelsize=12.5, pad=1)

        ax = fig.add_subplot(grid[1, 0])
        self.style(ax, 'C  Optimizer comparison', ylabel='Normalized above-null (%)')
        for offset, mode, label, color in [(-.10, 'classify', 'Adam', BLUE),
                                          (.10, 'cma', 'CMA', ORANGE)]:
            records = [self.robust_groups[('E5c', f'p{p}_optimizer', mode)]['double_opponent_fraction']
                       for p in [9, 27]]
            self.points(ax, np.arange(2)+offset, records, color, label, 'robustness/C', multiplier=100)
        init = self.metric('p9_baseline', 'untrained', 'double_opponent_fraction')
        # The same plotted mean is verified against the separately audited
        # matched initialization of the CMA networks at each patch size.
        for p in [9, 27]:
            cma_init = next(r for r in self.cma_init['results']
                            if r['size'] == p and r['metric'] == 'double_opponent_fraction')
            assert np.isclose(init['mean'], cma_init['untrained_mean'], rtol=0, atol=1e-14)
        ax.axhline(init['mean']*100, color=GRAY, ls='--', lw=1.)
        self.record('robustness/C', 'Initialization reference', init, 100)
        ax.set(xticks=[0, 1], xticklabels=['9×9', '27×27'], ylim=(-.5, 17))
        ax.legend(loc='upper right', labelspacing=.25, handletextpad=.3)

        ax = fig.add_subplot(grid[1, 1])
        self.style(ax, 'D  Utility at 27×27', 'Peak-location slope', horizontal=True)
        for i, (mode, y) in enumerate(zip(['frequency', 'loss', 'both'], [2, 1, 0])):
            s = self.illusions['utility_slopes']['E4/'+mode]
            self.interval(ax, s['sensitivity_peak_by'], y+.13, GREEN, 'robustness/D', 'Raw' if i == 0 else None)
            self.interval(ax, s['normalized_sensitivity_peak_by'], y-.13, ORANGE, 'robustness/D',
                          'RMS norm.' if i == 0 else None, marker='s')
        ax.axvline(0, color=GRAY, lw=1.)
        ax.set(yticks=[2, 1, 0], yticklabels=['Frequency', 'Loss', 'Both'],
               ylim=(-.5, 4.3), xlim=(-.13, .102), xticks=[-.1, 0, .1])
        ax.legend(loc='upper left', labelspacing=.25, handletextpad=.3)

        ax = fig.add_subplot(grid[2, 0])
        self.style(ax, 'E  Cardinal-axis proximity', ylabel='Angular distance (degrees)')
        for i, (mode, label) in enumerate([('untrained', 'Initialized'),
                                          ('shuffled', 'Shuffled'), ('classify', 'Classifier')]):
            records = [self.illusions['cardinals'][c+'/'+mode]['log_lms_distance']
                       for c in CONDITIONS[:2]]
            self.points(ax, np.arange(2)+(i-1)*.15, records, MODE[mode], label, 'robustness/E')
        ax.axhline(22.5, color=GRAY, lw=1, ls='--')
        ax.set(xticks=[0, 1], xticklabels=['9×9', '27×27'], ylim=(12, 37))
        ax.legend(loc='upper left', labelspacing=.2, handletextpad=.3)

        ax = fig.add_subplot(grid[2, 1])
        self.style(ax, 'F  Spatial correlations', 'Separation (pixels)', 'Pearson correlation')
        dist = np.array([1, 2, 4, 8, 16, 32, 64])
        for field, label, color, marker in [('lm_correlation', 'RG', BLUE, 'o'),
                                            ('s_lm_correlation', 'BY', ORANGE, 's')]:
            records = [self.illusions['grounding']['spatial'][str(d)][field] for d in dist]
            self.points(ax, dist, records, color, label, 'robustness/F', marker=marker, line=True)
        ax.set_xscale('log', base=2)
        ax.set_xticks([1, 4, 16, 64], ['1', '4', '16', '64'])
        ax.set_ylim(.2, 1.04)
        ax.legend(loc='lower left', labelspacing=.25, handletextpad=.3)
        self.save(fig, 'robustness_and_context')

    def run(self):
        self.design()
        self.organization()
        self.task_reference()
        self.induction()
        self.fixed_weights()
        self.robustness_context()
        (self.out/'figure_source_data.json').write_text(json.dumps({
            'description': 'Direct copies of audited summaries; no new model fitting or statistical inference.',
            'sources': self.sources, 'plotted_summaries': self.records,
            'layout_checks': self.layout_checks,
            'notes': ['Counts in figure labels are finite calibrations, not replacement zeros.',
                      'Geometry is exact offset enumeration; diagrams are not display-calibrated stimuli.',
                      'Architecture heatmap text is rounded to whole percentage points; underlying summaries are retained.',
                      'Fixed-weight and raw-cone decoder figures are separately designated post-training analyses.']
        }, indent=2)+'\n')


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', type=Path, default=root/'published_results')
    parser.add_argument('--diagnostics', type=Path)
    parser.add_argument('--output', type=Path, default=root/'generated/figures')
    args = parser.parse_args()
    if args.bundle.resolve() != (root/'published_results').resolve() and args.diagnostics is None:
        parser.error('A custom --bundle requires explicit --diagnostics from the same run.')
    diagnostics = args.diagnostics or root/'reproducibility/scale_diagnostics'
    StudyFigures(args.bundle.resolve(), diagnostics.resolve(), args.output.resolve()).run()


if __name__ == '__main__':
    main()
