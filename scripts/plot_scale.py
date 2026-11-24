#!/usr/bin/env python3
"""Reproduce the figure from bundled data; --refresh-data re-extracts saved audits.

CPU only. No training, statistics fitting, or bootstrap resampling occurs here.
Existing audit confidence intervals are copied without modification.
"""
import os
os.environ.setdefault('OMP_NUM_THREADS', '2')
os.environ.setdefault('OPENBLAS_NUM_THREADS', '2')
os.environ.setdefault('MKL_NUM_THREADS', '2')
os.environ.setdefault('MPLCONFIGDIR', str(__import__('tempfile').gettempdir()+'/color_paper_mpl'))
os.environ.setdefault('XDG_CACHE_HOME', str(__import__('tempfile').gettempdir()+'/color_paper_cache'))
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch, Rectangle
from matplotlib.ticker import MaxNLocator

OUT = Path(os.environ.get('COLOR_FIGURES',Path(__file__).resolve().parents[1]/'generated/figures'))
OUT.mkdir(parents=True,exist_ok=True)
AUDIT = Path(os.environ.get('COLOR_BUNDLE',Path(__file__).resolve().parents[1]/'published_results'))
DATA = AUDIT / 'scale_geometry_data.json'
CONDITIONS = [('p9_baseline', 9, 3, 1), ('p27_fixed', 27, 9, 1), ('p27_dilated', 27, 9, 3)]


def masks(n, target_width, dilation):
    """Enumerate sampled 3x3 offsets, not a dense dilated footprint."""
    yy, xx = np.indices((n, n))
    lo = (n - target_width) // 2
    hi = lo + target_width
    target = (yy >= lo) & (yy < hi) & (xx >= lo) & (xx < hi)
    surround_access = np.zeros((n, n), dtype=bool)
    padding_access = np.zeros((n, n), dtype=bool)
    for dy in (-dilation, 0, dilation):
        for dx in (-dilation, 0, dilation):
            sy, sx = yy + dy, xx + dx
            inside_frame = (sy >= 0) & (sy < n) & (sx >= 0) & (sx < n)
            inside_target = (sy >= lo) & (sy < hi) & (sx >= lo) & (sx < hi)
            surround_access |= target & inside_frame & ~inside_target
            padding_access |= ~inside_frame
    assert not np.any(surround_access & padding_access)
    return target, surround_access, padding_access


def refresh_data():
    primary_path = AUDIT / 'primary/primary_analysis.json'
    illusion_path = AUDIT / 'illusions_utility/audit.json'
    p = json.loads(primary_path.read_text())
    a = json.loads(illusion_path.read_text())
    rows = []
    for condition, n, width, dilation in CONDITIONS:
        g = next(g for g in p['groups'] if (g['stage'], g['condition'], g['mode']) == ('E1', condition, 'classify'))
        s = a['illusions'][f'E1/{condition}/classify']['axes']['BY']['simultaneous_odd_local_target_shift']
        target, access, pad = masks(n, width, dilation)
        rows.append(dict(
            condition=condition, patch_size=n, target_width=width, dilation=dilation,
            geometry=dict(target_pixels=int(target.sum()), target_pixels_reaching_surround=int(access.sum()),
                          target_access_fraction=float(access.sum()/target.sum()),
                          frame_pixels=n*n, frame_pixels_reaching_zero_padding=int(pad.sum()),
                          padding_fraction=float(pad.mean())),
            legacy_count={k:g['metrics']['legacy_count'][k] for k in ('mean','n','ci95')},
            local_by_shift={k:s[k] for k in ('mean','n','ci95')}))
    data = dict(created='2026-11-22', experiment='E1 base classifier, fixed scene split',
                geometry_status='Exact enumeration of 3x3 sampled offsets; not fitted to experiment outcomes.',
                metric_notes={'legacy_count':'Amplitude-dependent legacy opponent count, out of eight filters.',
                              'local_by_shift':'Calibrated polarity-odd local target response; positive indicates assimilation in the representation, not a human percept.',
                              'interval':'Existing descriptive 95% seed-bootstrap confidence intervals copied from saved audits; no new inference performed.'},
                sources=[{'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()} for path in (primary_path, illusion_path)],
                rows=rows)
    DATA.write_text(json.dumps(data,indent=2)+'\n')


def plot(data):
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.titlesize':11.5,
                         'axes.labelsize':11,'pdf.fonttype':42,'ps.fonttype':42})
    fig, axes = plt.subplots(1,3,figsize=(7.0,4.0),facecolor='white')
    fig.subplots_adjust(left=.035,right=.985,bottom=.43,top=.88,wspace=.20)
    colors = ['#e9edf1','#f6f3e9','#287e9d','#e5a24f']
    cmap=ListedColormap(colors)
    for j,row in enumerate(data['rows']):
        ax=axes[j];n,width,d=(row[k] for k in ('patch_size','target_width','dilation'))
        target,access,pad=masks(n,width,d);geom=row['geometry']
        assert int(access.sum())==geom['target_pixels_reaching_surround']
        assert int(pad.sum())==geom['frame_pixels_reaching_zero_padding']
        arr=np.zeros((n,n),int);arr[target]=1;arr[access]=2;arr[pad]=3
        ax.imshow(arr,cmap=cmap,vmin=0,vmax=3,interpolation='nearest')
        ax.set_xticks(np.arange(-.5,n,1),minor=True);ax.set_yticks(np.arange(-.5,n,1),minor=True)
        ax.grid(which='minor',color='white',linewidth=.25 if n==27 else .55)
        ax.tick_params(which='both',bottom=False,left=False,labelbottom=False,labelleft=False)
        lo=(n-width)//2;ax.add_patch(Rectangle((lo-.5,lo-.5),width,width,fill=False,edgecolor='#17364a',linewidth=1.1))
        ax.set_title(f'{chr(65+j)}  Patch {n}×{n}\nTarget {width}×{width}; d={d}',pad=7)
        ax.text(.5,-.12,f"Access: {100*geom['target_access_fraction']:.1f}%",transform=ax.transAxes,ha='center',fontsize=11,color='#206c86')
        ax.text(.5,-.25,f"Frame: {100*geom['padding_fraction']:.1f}%",transform=ax.transAxes,ha='center',fontsize=11,color='#9a5c0c')
    legend=[Patch(facecolor=colors[2],label='Target samples surround'),Patch(facecolor=colors[1],edgecolor='#17364a',label='Target samples target only'),Patch(facecolor=colors[3],label='Position samples zero padding')]
    fig.legend(handles=legend,loc='lower center',bbox_to_anchor=(.5,.02),ncol=1,frameon=False,fontsize=11)
    fig.savefig(OUT/'scale_geometry.pdf',facecolor='white')
    fig.savefig(OUT/'scale_geometry.png',dpi=220,facecolor='white')
    plt.close(fig)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh-data',action='store_true',help='Re-extract measurements from the saved project audit JSON files.')
    args=parser.parse_args()
    if args.refresh_data:
        refresh_data()
    plot(json.loads(DATA.read_text()))
    print(OUT/'scale_geometry.pdf')
    print(OUT/'scale_geometry.png')
