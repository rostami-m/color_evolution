#!/usr/bin/env python3
"""Regenerate publication figures and long-form numeric tables without training."""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


def verify(bundle, field='files'):
    manifest = json.loads((bundle/'manifest.json').read_text())
    failed = [name for name, digest in manifest[field].items()
              if not (bundle/name).is_file() or hashlib.sha256((bundle/name).read_bytes()).hexdigest() != digest]
    if failed:
        raise ValueError(f'Published bundle checksum mismatch: {failed}')


def tables(bundle, output):
    output.mkdir(parents=True, exist_ok=True)
    for source, target in [('primary/primary_analysis.json','primary_groups.csv'),
                           ('robustness/audit.json','robustness_groups.csv')]:
        rows = []
        for group in json.loads((bundle/source).read_text())['groups']:
            for metric, stat in group['metrics'].items():
                ci = stat.get('ci95') or [None, None]
                rows.append(dict(stage=group['stage'], condition=group['condition'], mode=group['mode'],
                                 metric=metric, n=stat.get('n'), mean=stat.get('mean'), low95=ci[0], high95=ci[1]))
        with (output/target).open('w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader(); writer.writerows(rows)


def main():
    project = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', type=Path, default=project/'published_results')
    parser.add_argument('--diagnostics', type=Path,
                        help='Fixed-weight summaries from the same run; required with a custom bundle')
    parser.add_argument('--output', type=Path, default=project/'generated')
    parser.add_argument('--skip-verification', action='store_true', help='Only for an independently regenerated analysis bundle')
    args = parser.parse_args()
    bundle, output = args.bundle.resolve(), args.output.resolve()
    if bundle != (project/'published_results').resolve() and args.diagnostics is None:
        parser.error('A custom --bundle requires explicit --diagnostics from the same run; published diagnostics are not substituted.')
    diagnostics = (args.diagnostics or project/'reproducibility/scale_diagnostics').resolve()
    if not args.skip_verification:
        verify(bundle)
        verify(diagnostics, 'sha256')
    tables(bundle, output/'tables')
    env = dict(os.environ, COLOR_BUNDLE=str(bundle), COLOR_FIGURES=str(output/'figures'))
    env.setdefault('MPLCONFIGDIR',str(output/'cache/matplotlib'))
    env.setdefault('XDG_CACHE_HOME',str(output/'cache'))
    for name, extra in [('plot_study.py', ['--bundle', str(bundle), '--diagnostics', str(diagnostics),
                                         '--output', str(output/'figures')])]:
        subprocess.run([sys.executable, str(project/'scripts'/name), *extra], env=env, check=True)
    print('Regenerated figures and tables:', output)


if __name__ == '__main__':
    main()
