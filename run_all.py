"""
run_all.py — sequential runner for all paper experiments.

Usage:
    python run_all.py                   # run everything
    python run_all.py --section s1      # only §2.1 emergence experiments
    python run_all.py --section s2      # only §2.2 behaving vs world-recovery
    python run_all.py --section s3      # only §2.3 illusions
    python run_all.py --section s4      # only §2.4 utility

Each experiment is run as an isolated subprocess so a failure in one step does
not abort the rest. Results land in RESULTS_DIR (default: code/results/).

Set DATA_DIR and RESULTS_DIR to change input and output locations. Set DEVICE
to select a PyTorch device. Individual experiment budgets are controlled by
environment variables (e.g. EMERGENCE_BUDGET=3600).
"""
import argparse
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable

EXPERIMENTS = [
    # (section-tag, module-path, default-budget-env-var, default-budget-s)
    ("s1", "experiments.s1_emergence.run_emergence",       "EMERGENCE_BUDGET",      1_800),
    ("s1", "experiments.s1_emergence.run_robustness",      "ROBUSTNESS_BUDGET",    18_000),
    ("s1", "experiments.s1_emergence.run_cmaes",           "CMAES_BUDGET",          9_000),
    ("s2", "experiments.s2_behaving.run_gap",              "GAP_BUDGET",            2_400),
    ("s2", "experiments.s2_behaving.run_arch_sweep",       "ARCH_SWEEP_BUDGET",     5_400),
    ("s2", "experiments.s2_behaving.run_why",              None,                    None),
    ("s3", "experiments.s3_illusions.run_contrast_assimilation", "ILLUSION_BUDGET", 6_000),
    ("s3", "experiments.s3_illusions.run_antagonism_emerges",    "ANTAG_BUDGET",    6_000),
    ("s3", "experiments.s3_illusions.run_more_illusions",        "MORE_ILLUSIONS_BUDGET", 6_000),
    ("s4", "experiments.s4_utility.run_fitness_sweep",     "FITNESS_BUDGET",       14_400),
    ("s4", "experiments.s4_utility.run_ecological_fitness","ECO_BUDGET",            9_000),
]


def run_experiment(module, timeout):
    t0 = time.time()
    result = subprocess.run(
        [PY, "-m", module],
        cwd=HERE,
        timeout=timeout + 120 if timeout else None,
    )
    elapsed = time.time() - t0
    return result.returncode, elapsed


def main():
    ap = argparse.ArgumentParser(description="Run paper experiments")
    ap.add_argument("--section", choices=["s1", "s2", "s3", "s4"], default=None,
                    help="Run only experiments for this paper section (default: all)")
    ap.add_argument("--list", action="store_true", help="List experiments and exit")
    args = ap.parse_args()

    to_run = [(s, m, benv, bd) for s, m, benv, bd in EXPERIMENTS
              if args.section is None or s == args.section]

    if args.list:
        for s, m, benv, bd in to_run:
            budget = f"{os.environ.get(benv, str(bd))}s" if benv else "n/a"
            print(f"  [{s}] {m}  budget={budget}")
        return

    print(f"Running {len(to_run)} experiment(s)...\n")
    results = []
    for s, module, benv, bd in to_run:
        timeout = int(os.environ.get(benv, bd)) if benv and bd else None
        budget = f"{timeout}s" if timeout is not None else "n/a"
        print(f"[{s}] {module} (budget={budget}) ...", flush=True)
        try:
            rc, elapsed = run_experiment(module, timeout)
            status = "OK" if rc == 0 else f"FAILED (rc={rc})"
        except subprocess.TimeoutExpired:
            rc = -1; elapsed = timeout or 0
            status = "TIMEOUT"
        print(f"     {status}  ({elapsed:.0f}s)\n")
        results.append((module, status))

    print("=" * 60)
    for m, st in results:
        print(f"  {'+' if st == 'OK' else '!'}  {m:<55} {st}")
    n_ok = sum(1 for _, st in results if st == "OK")
    print(f"\n{n_ok}/{len(results)} experiments completed successfully.")


if __name__ == "__main__":
    main()
