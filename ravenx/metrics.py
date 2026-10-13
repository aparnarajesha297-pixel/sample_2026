"""Detection and calibration metrics."""

from __future__ import annotations

import numpy as np
from sklearn.metrics import (accuracy_score, average_precision_score, f1_score,
                             precision_score, recall_score, roc_auc_score)


def pr_auc(y, p):
    return float(average_precision_score(y, p)) if len(np.unique(y)) > 1 else float("nan")


def best_threshold(y, p):
    """Threshold maximising F1 (chosen on the validation split only)."""
    if len(np.unique(y)) < 2:
        return 0.5
    order = np.argsort(-p)
    ys, ps = y[order], p[order]
    tp = np.cumsum(ys)
    fp = np.cumsum(1 - ys)
    prec = tp / (tp + fp)
    rec = tp / ys.sum()
    f1 = 2 * prec * rec / np.clip(prec + rec, 1e-12, None)
    # only consider cut points between distinct scores
    distinct = np.r_[ps[1:] != ps[:-1], True]
    f1 = np.where(distinct, f1, -1)
    i = int(np.argmax(f1))
    return float(ps[i])


def ece(y, p, n_bins=15):
    """Expected calibration error of P(attack): sum_b |B|/N * |acc_b - conf_b|
    over equal-width bins of the predicted attack probability."""
    bins = np.linspace(0, 1, n_bins + 1)
    ids = np.clip(np.digitize(p, bins[1:-1]), 0, n_bins - 1)
    total = 0.0
    for b in range(n_bins):
        m = ids == b
        if m.any():
            total += m.mean() * abs(y[m].mean() - p[m].mean())
    return float(total)


def brier(y, p):
    return float(np.mean((p - y) ** 2))


def reliability_curve(y, p, n_bins=10):
    bins = np.linspace(0, 1, n_bins + 1)
    ids = np.clip(np.digitize(p, bins[1:-1]), 0, n_bins - 1)
    conf, acc, cnt = [], [], []
    for b in range(n_bins):
        m = ids == b
        conf.append(p[m].mean() if m.any() else np.nan)
        acc.append(y[m].mean() if m.any() else np.nan)
        cnt.append(int(m.sum()))
    return np.array(conf), np.array(acc), np.array(cnt)


def detection_metrics(y, p, thr):
    yhat = (p >= thr).astype(int)
    both = len(np.unique(y)) > 1
    return {
        "Accuracy": accuracy_score(y, yhat),
        "Precision": precision_score(y, yhat, zero_division=0),
        "Recall": recall_score(y, yhat, zero_division=0),
        "F1": f1_score(y, yhat, zero_division=0),
        "ROC-AUC": roc_auc_score(y, p) if both else float("nan"),
        "PR-AUC": pr_auc(y, p),
        "ECE": ece(y, p),
        "Brier": brier(y, p),
        "Threshold": thr,
    }
