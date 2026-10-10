"""Threshold re-tuning on a small labelled slice of the target domain.

A model trained on the source domain keeps its weights; only the alarm
threshold is re-chosen on a few labelled receiver logs from the target
domain. The slice is drawn as whole receiver files, stratified by run (one
run = one attack type), so every attack type is represented and no receiver
is in both the slice and the evaluation set. Every threshold is scored on
the same held-out receivers:

  source  threshold picked on source validation (what the cross-scenario test uses)
  tuned   threshold maximising F1 on the target slice
  oracle  threshold maximising F1 on the held-out receivers themselves (upper bound)
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .metrics import best_threshold, detection_metrics

COLS = ["F1", "Precision", "Recall", "Threshold"]


def draw_slice(run: np.ndarray, unit: np.ndarray, frac: float, rng) -> np.ndarray:
    """Boolean step mask of a labelled slice: ceil(frac * n) receiver files
    (at least one) from every run."""
    picked = []
    for r in np.unique(run):
        units = np.unique(unit[run == r])
        k = max(1, int(np.ceil(frac * len(units))))
        k = min(k, len(units) - 1)          # always leave a receiver to evaluate on
        picked.append(rng.choice(units, size=k, replace=False))
    return np.isin(unit, np.concatenate(picked))


def retune(y, p, thr_src, run, unit, fracs=(0.01, 0.05, 0.10, 0.20), draws=20, seed=0):
    """One row per (budget, draw, threshold kind) with metrics on the held-out
    receivers."""
    rng = np.random.default_rng(seed)
    rows = []
    for frac in fracs:
        for d in range(draws):
            cal = draw_slice(run, unit, frac, rng)
            ev = ~cal
            thr = {"source": thr_src,
                   "tuned": best_threshold(y[cal], p[cal]),
                   "oracle": best_threshold(y[ev], p[ev])}
            for kind, t in thr.items():
                m = detection_metrics(y[ev], p[ev], t)
                rows.append({"Budget": frac, "Draw": d, "Kind": kind,
                             "Slice steps": int(cal.sum()),
                             "Slice receivers": int(len(np.unique(unit[cal]))),
                             **{c: m[c] for c in COLS}})
    return pd.DataFrame(rows)
