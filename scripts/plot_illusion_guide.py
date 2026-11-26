#!/usr/bin/env python3
"""Illustrate the actual induction probes without generating model results.

The production evaluator is called with a recording, identity feature object to
capture its input arrays. Its artificial response outputs are discarded. Only
input geometry, physical profiles, and measurement masks enter this figure.
The display RGB mapping is schematic, not a cone-to-display calibration.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

os.environ.setdefault('MPLCONFIGDIR', '/tmp/color_illusion_guide_mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.text import Text
import numpy as np
import torch

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))
from revision.illusions import AXES, evaluate_illusions
from revision.models import Geometry

INK = '#173447'
NEAR = '#CC7734'
FAR = '#238179'
NEUTRAL = np.array([.76, .76, .76])
POSITIVE = np.array([.30, .47, .88])
NEGATIVE = np.array([.94, .77, .27])


class InputRecorder:
    """Capture evaluator inputs; identity outputs have no scientific meaning."""
    geometry = Geometry(27, 9)
    dilation = 1

    def __init__(self):
        self.inputs = []

    def eval(self):
        return self

    def features(self, x):
        self.inputs.append(x.detach().cpu().numpy().copy())
        return x

    def representation(self, x):
        c = self.geometry.center
        return x[:, :, c, c].mean((2, 3))


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def capture(gray):
    """Select exact inputs from the evaluator and validate the expected ordering."""
    recorder = InputRecorder()
    output = evaluate_illusions(recorder, gray)
    p, n = 27, 81
    axis_index = list(AXES).index('BY')
    patch_inputs = [a[0] for a in recorder.inputs if a.shape == (1, 3, p, p)]
    extended_inputs = [a[0] for a in recorder.inputs if a.shape == (1, 3, n, n)]
    # Per axis: neutral, calibration +/-, surround -/+, 4 checker probes.
    assert len(patch_inputs) == 9 * len(AXES)
    # Per axis: 3 Cornsweet, 4 Mach, neutral, 4 watercolor probes.
    assert len(extended_inputs) == 12 * len(AXES)
    patches = patch_inputs[9*axis_index:9*(axis_index+1)]
    extended = extended_inputs[12*axis_index:12*(axis_index+1)]
    luminance_index = list(AXES).index('luminance')
    luminance = extended_inputs[12*luminance_index:12*(luminance_index+1)]
    data = output['axes']['BY']
    lum_data = output['axes']['luminance']
    arrays = {'gray_lms': gray,
              'simultaneous_negative_lms': patches[3],
              'simultaneous_positive_lms': patches[4],
              'cornsweet_positive_lms': luminance[0],
              'cornsweet_reversed_lms': luminance[1],
              'cornsweet_removed_lms': luminance[2],
              'mach_ramp_lms': luminance[3],
              'mach_reversed_lms': luminance[4],
              'mach_linear_lms': luminance[5],
              'mach_flat_lms': luminance[6],
              'watercolor_closed_lms': extended[8],
              'watercolor_reversed_lms': extended[9],
              'watercolor_open_lms': extended[10],
              'watercolor_removed_lms': extended[11]}
    target = np.zeros((p, p), bool)
    target[recorder.geometry.center, recorder.geometry.center] = True
    interior = np.zeros_like(target)
    interior[10:17, 10:17] = True
    arrays.update(simultaneous_target_mask=target,
                  simultaneous_boundary_mask=target & ~interior,
                  simultaneous_interior_mask=interior)
    corn = lum_data['cornsweet'][0]
    arrays['cornsweet_profile'] = np.asarray(corn['profile'])
    for name in ('left_roi', 'right_roi', 'near_left_roi', 'near_right_roi'):
        arrays['cornsweet_'+name] = np.asarray(corn[name])
    for label, record in zip(('ramp', 'reversed', 'linear', 'flat'), lum_data['mach']):
        arrays['mach_'+label+'_profile'] = np.asarray(record['profile'])
    arrays['mach_low_join_roi'] = np.arange(n//3-1, n//3+2)
    arrays['mach_high_join_roi'] = np.arange(2*n//3-1, 2*n//3+2)
    start, stop = data['watercolor']['closed']['far_roi']
    far = np.zeros((n, n), bool)
    far[start:stop, start:stop] = True
    # The unchanged enclosed interior is 7 x 7 in this 9-pixel contour.
    inner = max(recorder.geometry.target_size, 2*recorder.dilation+5)
    inner += inner % 2 == 0
    a, b = (n-inner)//2, (n+inner)//2
    width = max(1, p//27)
    near = np.zeros_like(far)
    near[a+width:b-width, a+width:b-width] = True
    near[far] = False
    arrays['watercolor_near_mask'] = near
    arrays['watercolor_far_mask'] = far
    arrays['watercolor_zoom_bounds'] = np.array([32, 49])
    checks = {}

    def check(name, condition):
        checks[name] = bool(condition)
        if not checks[name]:
            raise AssertionError(name)

    gray32 = gray.astype(np.float32)
    for sign, label in ((-1, 'negative'), (1, 'positive')):
        x = arrays['simultaneous_'+label+'_lms']
        check('simultaneous_'+label+'_target_unchanged',
              np.array_equal(x[:, target], np.repeat(gray32[:, None], target.sum(), axis=1)))
        expected = (gray*(1+sign*.15*AXES['BY'])).astype(np.float32)
        check('simultaneous_'+label+'_surround_contrast',
              np.array_equal(x[:, ~target], np.repeat(expected[:, None], (~target).sum(), axis=1)))
    check('simultaneous_boundary_count_32', (target & ~interior).sum() == 32)
    for stem in ('cornsweet_positive', 'mach_ramp'):
        profile = arrays['cornsweet_profile' if stem.startswith('corn') else 'mach_ramp_profile']
        expected = gray[:, None, None]*(1+AXES['luminance'][:, None, None]*profile[None, None, :])
        expected = np.broadcast_to(expected, (3, n, n)).astype(np.float32)
        check(stem+'_captured_input_matches_recorded_profile',
              np.array_equal(arrays[stem+'_lms'], expected))
    for name in ('left_roi', 'right_roi', 'near_left_roi', 'near_right_roi'):
        check('cornsweet_'+name+'_physically_neutral',
              np.all(arrays['cornsweet_profile'][arrays['cornsweet_'+name]] == 0))
    cusp = np.flatnonzero(arrays['cornsweet_profile'] != 0)
    distant = np.r_[arrays['cornsweet_left_roi'], arrays['cornsweet_right_roi']]
    check('cornsweet_distant_outside_changed_input_support',
          np.min(np.abs(distant[:, None]-cusp[None, :])) > recorder.dilation)
    for kind in ('closed', 'reversed', 'open', 'removed'):
        x = arrays['watercolor_'+kind+'_lms']
        for region, mask in (('near', near), ('far', far)):
            check('watercolor_'+kind+'_'+region+'_physically_unchanged',
                  np.array_equal(x[:, mask], np.repeat(gray32[:, None], mask.sum(), axis=1)))
    changed = np.any(arrays['watercolor_closed_lms'] != gray32[:, None, None], axis=0)
    accessible = np.zeros_like(changed)
    for row, col in np.argwhere(changed):
        accessible[max(0, row-1):row+2, max(0, col-1):col+2] = True
    check('watercolor_far_outside_changed_input_support', not np.any(accessible & far))
    check('watercolor_near_accesses_changed_contour', np.all(accessible[near]))
    check('watercolor_near_far_disjoint', not np.any(near & far))
    check('no_artificial_response_values_exported', all('response' not in k for k in arrays))
    return arrays, checks


def display_rgb(lms, gray):
    relative = lms / gray[:, None, None]
    luminance = relative.mean(axis=0)
    contrast = (relative[2]-(relative[0]+relative[1])/2)/1.5
    color_delta = np.where((contrast >= 0)[..., None], POSITIVE-NEUTRAL, NEGATIVE-NEUTRAL)
    return np.clip(luminance[..., None]*NEUTRAL + np.abs(contrast[..., None])/.15*color_delta, 0, 1)


def image_axes(fig, rect, image, title=None):
    ax = fig.add_axes(rect)
    ax.imshow(image, interpolation='nearest', origin='upper')
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_edgecolor('#9AA6AD')
        spine.set_linewidth(.7)
    if title:
        ax.set_title(title, fontsize=15.0, pad=7)
    return ax


def text_axes(fig, rect, text):
    ax = fig.add_axes(rect)
    ax.axis('off')
    ax.text(0, 1, text, ha='left', va='top', fontsize=15.0, linespacing=1.35)
    return ax


def profile_axes(fig, rect, values, title):
    ax = fig.add_axes(rect)
    ax.plot(np.arange(len(values)), values, color=INK, lw=1.7, zorder=4)
    ax.axhline(0, color='#C8D2D9', lw=.8, zorder=0)
    ax.set(xlim=(0, len(values)-1), ylim=(-.19, .19),
           xticks=[0, 40, 80], yticks=[-.15, 0, .15])
    ax.set_title(title, fontsize=15.0, pad=7)
    ax.set_ylabel('Input contrast', fontsize=15.0, labelpad=2)
    ax.tick_params(labelsize=15.0, length=3)
    ax.spines[['top', 'right']].set_visible(False)
    return ax


def draw(arrays, output):
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 15.0,
                         'text.color': INK, 'axes.labelcolor': INK,
                         'xtick.color': INK, 'ytick.color': INK,
                         'pdf.fonttype': 42, 'ps.fonttype': 42})
    fig = plt.figure(figsize=(9.4, 10.6), facecolor='white')
    gray = arrays['gray_lms']
    def rgb(stem):
        lms = arrays[stem+'_lms']
        if stem.startswith(('cornsweet', 'mach')):
            relative = lms / gray[:, None, None]
            return np.clip(relative.mean(axis=0)[..., None]*NEUTRAL, 0, 1)
        return display_rgb(lms, gray)
    for y in (.754, .506, .257):
        fig.add_artist(plt.Line2D([.035, .97], [y, y], transform=fig.transFigure,
                                  color='#D9E1E6', lw=.8))
    for y, title in ((.975, 'A  Simultaneous induction: equal targets, different surrounds'),
                     (.729, 'B  Cornsweet: a narrow cusp between physically equal fields'),
                     (.481, 'C  Mach: signed residuals at the two ramp joins'),
                     (.232, 'D  Watercolor: contour cues versus the unchanged interior')):
        fig.text(.035, y, title, fontsize=16, weight='bold', va='top')

    image_axes(fig, [.045, .790, .18, .14], rgb('simultaneous_negative'), 'Surround −0.15')
    image_axes(fig, [.255, .790, .18, .14], rgb('simultaneous_positive'), 'Surround +0.15')
    mask_rgb = np.full((27, 27, 3), .9)
    mask_rgb[arrays['simultaneous_boundary_mask']] = matplotlib.colors.to_rgb(NEAR)
    mask_rgb[arrays['simultaneous_interior_mask']] = matplotlib.colors.to_rgb(FAR)
    image_axes(fig, [.465, .790, .18, .14], mask_rgb, 'Local support')
    fig.text(.24, .773, '27×27 patch; same 9×9 targets', fontsize=15.0, ha='center')
    fig.text(.555, .773, '32/81 at boundary', fontsize=15.0, ha='center')
    text_axes(fig, [.70, .775, .28, .17],
              'Local: boundary features\nsample target + surround.\n\nGlobal readout:\n$z=c-bs$\ncan change the sign.')

    image_axes(fig, [.045, .536, .19, .15], rgb('cornsweet_positive'), '81×81 probe')
    ax = profile_axes(fig, [.345, .564, .325, .105], arrays['cornsweet_profile'], 'Cusp profile (pixel column)')
    for name in ('left_roi', 'right_roi', 'near_left_roi', 'near_right_roi'):
        inds = arrays['cornsweet_'+name]
        color = NEAR if name.startswith('near') else FAR
        ax.axvspan(inds.min()-.5, inds.max()+.5, color=color, alpha=.22, zorder=1)
    fig.text(.345, .517, 'Near cue', color=NEAR, fontsize=15.0)
    fig.text(.515, .517, 'Distant field', color=FAR, fontsize=15.0)
    text_axes(fig, [.73, .545, .25, .165],
              'Shaded regions have\nzero input contrast.\n\nDistant local features\ncannot sample the cusp\nwith a 3×3 kernel.')

    image_axes(fig, [.045, .288, .19, .15], rgb('mach_ramp'), '81×81 probe')
    ax = profile_axes(fig, [.345, .316, .325, .105], arrays['mach_ramp_profile'], 'Ramp profile (pixel column)')
    for name in ('low', 'high'):
        inds = arrays['mach_'+name+'_join_roi']
        ax.axvspan(inds.min()-.5, inds.max()+.5, color=NEAR, alpha=.26, zorder=1)
    fig.text(.38, .269, 'Low join', fontsize=15.0, color=NEAR)
    fig.text(.55, .269, 'High join', fontsize=15.0, color=NEAR)
    text_axes(fig, [.73, .294, .25, .173],
              'Subtract each column’s\nmatched uniform-field\nresponse.\n\nHigh − low residual:\n+ overshoot\n− smoothing')

    ax = image_axes(fig, [.045, .047, .17, .141], rgb('watercolor_closed'), 'Closed, 81×81')
    a, b = arrays['watercolor_zoom_bounds']
    ax.add_patch(Rectangle((a-.5, a-.5), b-a, b-a, fill=False,
                           edgecolor=INK, lw=.8, linestyle='--'))
    image_axes(fig, [.255, .047, .17, .141], rgb('watercolor_open'), 'Open, 81×81')
    zoom = rgb('watercolor_closed')[a:b, a:b].copy()
    zoom[arrays['watercolor_near_mask'][a:b, a:b]] = matplotlib.colors.to_rgb(NEAR)
    zoom[arrays['watercolor_far_mask'][a:b, a:b]] = matplotlib.colors.to_rgb(FAR)
    image_axes(fig, [.465, .047, .17, .141], zoom, '17×17 zoom + masks')
    fig.text(.46, .026, 'Near', color=NEAR, fontsize=15.0)
    fig.text(.555, .026, 'Distant', color=FAR, fontsize=15.0)
    text_axes(fig, [.70, .045, .28, .165],
              'Both masks contain\nunchanged target input.\n\nOnly near-mask features\ncan sample the contour.\nOpening also changes\nlocal contour input.')
    fig.text(.035, .006, 'A,D: BY; B,C: luminance. Schematic colors; masks are measurement regions.',
             fontsize=15.0, color=INK)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    outside = []
    for obj in fig.findobj(match=Text):
        if obj.get_visible() and obj.get_text():
            bounds = obj.get_window_extent(renderer)
            if bounds.x0 < -1 or bounds.y0 < -1 or bounds.x1 > fig.bbox.x1+1 or bounds.y1 > fig.bbox.y1+1:
                outside.append(obj.get_text())
    if outside:
        raise ValueError('Figure text outside canvas: '+repr(outside))
    fig.savefig(output/'illusion_guide.pdf', facecolor='white')
    fig.savefig(output/'illusion_guide.png', facecolor='white', dpi=180)
    plt.close(fig)
    return {'font_min_points': 15.0, 'figure_inches': [9.4, 10.6],
            'text_outside_canvas': outside}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--diagnostics', type=Path,
                        default=PROJECT/'reproducibility/scale_diagnostics',
                        help='Directory containing the matching summary.json gray reference')
    parser.add_argument('--output', type=Path, default=PROJECT/'generated/figures')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    torch.set_num_threads(1)
    diagnostic = args.diagnostics/'summary.json'
    gray = np.asarray(json.loads(diagnostic.read_text())['gray'], dtype=float)
    arrays, checks = capture(gray)
    array_path = args.output/'illusion_guide_stimuli.npz'
    np.savez_compressed(array_path, **arrays)
    layout = draw(arrays, args.output)
    metadata = {
        'purpose': 'Explanatory input geometry; no model-response or human-response data',
        'input_source': 'Inputs captured directly from revision.illusions.evaluate_illusions',
        'capture_object': 'Identity feature/input recorder; artificial outputs are discarded',
        'geometry': {'patch_size': 27, 'target_size': 9, 'dilation': 1, 'profile_grid': 81},
        'axes': {'A_simultaneous': 'BY', 'B_cornsweet': 'luminance',
                 'C_mach': 'luminance', 'D_watercolor': 'BY'},
        'axis_relative_lms': {k: AXES[k].tolist() for k in ('BY', 'luminance')},
        'contrast_amplitude': .15,
        'gray_lms': gray.tolist(),
        'display': {'calibrated_rgb': False, 'neutral_rgb': NEUTRAL.tolist(),
                    'positive_rgb': POSITIVE.tolist(), 'negative_rgb': NEGATIVE.tolist(),
                    'note': 'Schematic interpolation of BY relative contrast; mean relative LMS scales gray.'},
        'watercolor': {'contour_outer_dark_relative_lms': .7,
                       'near_pixels': int(arrays['watercolor_near_mask'].sum()),
                       'far_pixels': int(arrays['watercolor_far_mask'].sum()),
                       'zoom_bounds': arrays['watercolor_zoom_bounds'].tolist()},
        'cornsweet': {'near_distant_left_overlap': np.intersect1d(
                         arrays['cornsweet_left_roi'], arrays['cornsweet_near_left_roi']).tolist(),
                     'near_distant_right_overlap': np.intersect1d(
                         arrays['cornsweet_right_roi'], arrays['cornsweet_near_right_roi']).tolist(),
                     'note': 'Production near and distant windows overlap in one unchanged column per side; distant windows remain outside cusp support.'},
        'validation': checks, 'layout': layout,
        'source_sha256': {'revision/illusions.py': sha256(PROJECT/'revision/illusions.py'),
                          'revision/models.py': sha256(PROJECT/'revision/models.py'),
                          'diagnostics/summary.json': sha256(diagnostic),
                          'scripts/plot_illusion_guide.py': sha256(__file__)},
        'output_sha256': {'illusion_guide_stimuli.npz': sha256(array_path),
                          'illusion_guide.pdf': sha256(args.output/'illusion_guide.pdf')},
        'arrays': {name: {'shape': list(value.shape), 'dtype': str(value.dtype)}
                   for name, value in arrays.items()}}
    (args.output/'illusion_guide_sources.json').write_text(json.dumps(metadata, indent=2)+'\n')
    print(args.output/'illusion_guide.pdf')
    print(f'{len(checks)} physical-input and support checks passed; no model statistics generated.')


if __name__ == '__main__':
    main()
