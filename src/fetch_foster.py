"""
fetch_foster.py — download Foster (2002) hyperspectral natural-scene .mat files.

Downloads into DATA_DIR/foster/ (see src/data.py for DATA_DIR resolution).
Idempotent: skips scenes already present. Deletes the zip after extracting.

Usage:
    python -m src.fetch_foster          # download 3 scenes (default)
    python -m src.fetch_foster --n 8    # download all 8 scenes
"""
import argparse
import os
import ssl
import sys
import urllib.request
import zipfile

BASE = (
    "https://personalpages.manchester.ac.uk/staff/d.h.foster/"
    "Hyperspectral_images_of_natural_scenes_02_files/"
)
SCENES = [f"scene{i}.zip" for i in range(1, 9)]


def _data_dir():
    env = os.environ.get("DATA_DIR", "").strip()
    if env:
        return env
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "..", "data")


def fetch(n):
    foster_dir = os.path.join(_data_dir(), "foster")
    os.makedirs(foster_dir, exist_ok=True)
    ctx = ssl.create_default_context()
    got = []
    for s in SCENES[:n]:
        stem = s.replace(".zip", "")
        existing = [f for f in os.listdir(foster_dir)
                    if f.lower().startswith(stem) and f.lower().endswith(".mat")]
        if existing:
            print(f"[skip] {stem} already present ({existing[0]})")
            got.append(os.path.join(foster_dir, existing[0]))
            continue
        url = BASE + s
        zp = os.path.join(foster_dir, s)
        print(f"[get ] {url}")
        try:
            with urllib.request.urlopen(url, context=ctx, timeout=120) as r, \
                 open(zp, "wb") as fh:
                fh.write(r.read())
            with zipfile.ZipFile(zp) as z:
                z.extractall(foster_dir)
            os.remove(zp)
            mats = [f for f in os.listdir(foster_dir)
                    if f.lower().startswith(stem) and f.lower().endswith(".mat")]
            if mats:
                got.append(os.path.join(foster_dir, mats[0]))
                print(f"[ok  ] {mats[0]}")
            else:
                print(f"[warn] no .mat after extracting {s}")
        except Exception as e:
            print(f"[fail] {s}: {type(e).__name__}: {e}")
            if os.path.exists(zp):
                os.remove(zp)
    print(f"\nfetched {len(got)} scene file(s) into {foster_dir}")
    return got


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Download Foster hyperspectral scenes")
    ap.add_argument("--n", type=int, default=3, help="number of scenes to download (1-8)")
    a = ap.parse_args()
    files = fetch(min(a.n, 8))
    sys.exit(0 if files else 1)
