"""
io_utils.py — incremental result I/O and model factory.

Results are written relative to RESULTS_DIR (env var) or results/ by default.
"""
import json
import os

from .data import results_path


def jsonl_append(name, obj):
    """Append one JSON record to a .jsonl file identified by name (not full path)."""
    path = results_path(name)
    with open(path, "a") as f:
        f.write(json.dumps(obj) + "\n")
    return path


def save_json(name, obj):
    """Write a JSON summary, identified by name."""
    path = results_path(name)
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)
    return path


def load_json(name):
    path = results_path(name)
    with open(path) as f:
        return json.load(f)


def load_jsonl(name):
    path = results_path(name)
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def make_model(k1=8, bottleneck=4, kind="survival"):
    """Model factory: returns an untrained network of the requested type."""
    from .model import RetinalCNN, WorldRecoveryCNN
    if kind == "world":
        return WorldRecoveryCNN(k1=k1, bottleneck=bottleneck)
    return RetinalCNN(k1=k1, bottleneck=bottleneck)
