#!/usr/bin/env python3
"""Recompute post-run analyses from a completed full experiment run."""
import argparse
import os
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--data-dir', type=Path)
    parser.add_argument('--raw-decoding', action='store_true')
    args = parser.parse_args()
    if args.raw_decoding and args.data_dir is None:
        parser.error('--raw-decoding requires --data-dir')
    root = Path(__file__).resolve().parents[1]
    output = args.output.resolve(); output.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, COLOR_RUN=str(args.run.resolve()), COLOR_ANALYSIS=str(output))
    for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:
        env[key] = '2'
    scripts = ['primary/analyze_primary.py', 'robustness/audit.py',
               'robustness/cma_initialization_audit.py', 'illusions_utility/audit.py',
               'illusions_utility/additional_audit.py']
    if args.raw_decoding:
        env['COLOR_DATA'] = str(args.data_dir.resolve()); scripts.append('raw_decoding.py')
    for script in scripts:
        subprocess.run([sys.executable, str(root/'scripts/reanalysis'/script)], env=env, cwd=root, check=True)
    # Re-extract geometry measurements from this run, not the published reference bundle.
    env.update(COLOR_BUNDLE=str(output), COLOR_FIGURES=str(output/'figures'))
    subprocess.run([sys.executable, str(root/'scripts/plot_scale.py'), '--refresh-data'], env=env, check=True)
    subprocess.run([sys.executable, str(root/'scripts/reproduce.py'), '--bundle', str(output),
                    '--output', str(output), '--skip-verification'], check=True)


if __name__ == '__main__':
    main()
