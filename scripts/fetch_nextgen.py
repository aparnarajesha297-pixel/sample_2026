"""Download VeReMi NextGen subsets from Zenodo, optionally keeping only a
random fraction of the receiver files.

The larger scenarios do not fit on a small machine (highway_7 is about
13 GB zipped). Each attack archive is downloaded, the requested fraction of
receiver files is extracted from every split (Train / Validation / Test)
with a fixed seed, and the archive is deleted before the next one. Sampling
whole receiver files keeps every kept receiver's full message stream, so
streams, sequences and neighbour graphs stay intact.

Example:
  python scripts/fetch_nextgen.py --scenario urban_2 --fraction 0.15 --out /data/nextgen/u2
"""

from __future__ import annotations

import argparse
import io
import random
import shutil
import sys
import time
import urllib.request
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ravenx.config import ATTACKS  # noqa: E402

RECORD = "https://zenodo.org/records/19665762/files"


def download(url, dest, retries=4):
    for i in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=120) as r, open(dest, "wb") as f:
                shutil.copyfileobj(r, f, length=1 << 22)
            return
        except Exception as e:  # noqa: BLE001
            if i == retries - 1:
                raise
            wait = 2 ** (i + 1)
            print(f"    download failed ({e}); retrying in {wait}s")
            time.sleep(wait)


def extract_sample(outer_zip, out_dir, fraction, seed):
    """Extract a fraction of the receiver files from each inner split zip."""
    kept = total = 0
    with zipfile.ZipFile(outer_zip) as outer:
        for inner_name in [n for n in outer.namelist() if n.lower().endswith(".zip")]:
            parts = inner_name.replace("\\", "/").split("/")
            split = parts[-2]                                  # Train / Validation / Test
            stem = parts[-1][:-4]                              # InTAS_<scenario>_<attack>
            with zipfile.ZipFile(io.BytesIO(outer.read(inner_name))) as inner:
                names = [n for n in inner.namelist() if n.lower().endswith(".json")]
                rng = random.Random(f"{seed}/{stem}/{split}")
                k = len(names) if fraction >= 1 else max(1, round(fraction * len(names)))
                chosen = sorted(rng.sample(sorted(names), k))
                target = Path(out_dir) / stem / split / stem
                target.mkdir(parents=True, exist_ok=True)
                for n in chosen:
                    (target / Path(n.replace("\\", "/")).name).write_bytes(inner.read(n))
                kept += len(chosen); total += len(names)
    return kept, total


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--scenario", required=True, help="e.g. highway_2, highway_7, urban_2, urban_7")
    p.add_argument("--attacks", nargs="*", default=ATTACKS)
    p.add_argument("--fraction", type=float, default=1.0,
                   help="fraction of receiver files kept per split (1 = all)")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--out", required=True)
    args = p.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)

    for atk in args.attacks:
        stem = f"InTAS_{args.scenario}_{atk}"
        if (out / stem).exists():
            print(f"{stem}: already there, skipping"); continue
        tmp = out / f"{stem}.zip"
        t0 = time.time()
        download(f"{RECORD}/{stem}.zip?download=1", tmp)
        size = tmp.stat().st_size / 2 ** 20
        kept, total = extract_sample(tmp, out, args.fraction, args.seed)
        tmp.unlink()
        print(f"{stem}: {size:.0f} MB, kept {kept}/{total} receiver files "
              f"({time.time() - t0:.0f}s)", flush=True)


if __name__ == "__main__":
    main()
