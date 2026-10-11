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

Scores are sorted once per model; each draw is then a few linear passes over
a mask, which gives the same thresholds as ``metrics.best_threshold``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

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


def _best_threshold_sorted(ys, ps):
    """``metrics.best_threshold`` for scores already sorted in descending order."""
    if ys.size == 0 or ys.min() == ys.max():
        return 0.5
    tp = np.cumsum(ys)
    fp = np.cumsum(1 - ys)
    f1 = 2 * tp / (tp + fp + ys.sum())          # = 2PR/(P+R)
    distinct = np.r_[ps[1:] != ps[:-1], True]   # cut points between distinct scores
    f1 = np.where(distinct, f1, -1)
    return float(ps[int(np.argmax(f1))])


def _prf(y, p, thr):
    yhat = p >= thr
    tp = int(np.sum(yhat & (y == 1)))
    fp = int(np.sum(yhat)) - tp
    fn = int(np.sum(y == 1)) - tp
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * tp / (2 * tp + fp + fn) if tp else 0.0
    return {"F1": f1, "Precision": prec, "Recall": rec, "Threshold": thr}


def retune(y, p, thr_src, run, unit, fracs=(0.01, 0.05, 0.10, 0.20), draws=20, seed=0):
    """One row per (budget, draw, threshold kind) with metrics on the held-out
    receivers."""
    order = np.argsort(-p, kind="stable")
    y, p, run, unit = (np.asarray(a)[order] for a in (y, p, run, unit))
    y = y.astype(np.int64)
    rng = np.random.default_rng(seed)
    rows = []
    for frac in fracs:
        for d in range(draws):
            cal = draw_slice(run, unit, frac, rng)
            ev = ~cal
            ye, pe = y[ev], p[ev]
            thr = {"source": thr_src,
                   "tuned": _best_threshold_sorted(y[cal], p[cal]),
                   "oracle": _best_threshold_sorted(ye, pe)}
            for kind, t in thr.items():
                rows.append({"Budget": frac, "Draw": d, "Kind": kind,
                             "Slice steps": int(cal.sum()),
                             "Slice receivers": int(len(np.unique(unit[cal]))),
                             **_prf(ye, pe, t)})
    return pd.DataFrame(rows)
