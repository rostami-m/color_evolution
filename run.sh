#!/usr/bin/env bash
# run.sh — entry point for the color-vision experiments.
#
# Usage:
#   ./run.sh                 # run all experiments (auto-detect device)
#   ./run.sh --section s1    # run only one paper section (s1..s4)
#   ./run.sh --list          # list experiments and their time budgets
#
# Environment variables (all optional; sensible defaults shown):
#   DATA_DIR     path to data/    (default: ./data)
#   RESULTS_DIR  path to results/ (default: ./results)
#   DEVICE       torch device     (default: auto-detect cuda > mps > cpu)
#   *_BUDGET     per-experiment wall-clock seconds (see ./run.sh --list)
#
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"

PYTHON="${PYTHON:-python3}"

# Default to repo-local data/ and results/ if the caller did not set them.
export DATA_DIR="${DATA_DIR:-$HERE/data}"
export RESULTS_DIR="${RESULTS_DIR:-$HERE/results}"
mkdir -p "$RESULTS_DIR"

echo "[run.sh] python      : $($PYTHON --version 2>&1)"
echo "[run.sh] DATA_DIR    : $DATA_DIR"
echo "[run.sh] RESULTS_DIR : $RESULTS_DIR"
echo "[run.sh] DEVICE      : ${DEVICE:-auto-detect}"

# Install the package in editable mode if it is not importable yet.
if ! "$PYTHON" -c "import src" 2>/dev/null; then
  echo "[run.sh] installing package (pip install -e .) ..."
  "$PYTHON" -m pip install -e . >/dev/null
fi

exec "$PYTHON" run_all.py "$@"
