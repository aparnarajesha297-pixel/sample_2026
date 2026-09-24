"""Helpers shared by the experiment scripts."""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .config import FEATURES
from .features import Normalizer
from .metrics import best_threshold, detection_metrics
from .models.tabular import TabularDetector
from .models.train import MODEL_SPECS, NeuralDetector

ALL_MODELS = ["RandomForest", "XGBoost", "GRU", "GAT", "GAT+GRU", "RAVEN-X", "RAVEN-X-GF"]
# the plan's five-row table; GAT+GRU (softmax head) is an extra ablation
DEFAULT_MODELS = ["RandomForest", "XGBoost", "GRU", "GAT", "RAVEN-X", "RAVEN-X-GF"]


def add_train_args(p):
    g = p.add_argument_group("training")
    g.add_argument("--models", nargs="*", default=DEFAULT_MODELS, choices=ALL_MODELS)
    g.add_argument("--seeds", nargs="*", type=int, default=[0],
                   help="repeat every model with these seeds and report mean +- std")
    g.add_argument("--epochs", type=int, default=15)
    g.add_argument("--patience", type=int, default=3)
    g.add_argument("--hidden", type=int, default=64)
    g.add_argument("--batch-size", type=int, default=256)
    g.add_argument("--lr", type=float, default=1e-3)
    g.add_argument("--max-train", type=int, default=None,
                   help="subsample training steps (quick runs)")
    g.add_argument("--quiet", action="store_true")
    return p


def make_model(name, args, seed):
    if name in ("RandomForest", "XGBoost"):
        return TabularDetector(name, seed=seed)
    return NeuralDetector(name, len(FEATURES), hidden=args.hidden, lr=args.lr,
                          batch_size=args.batch_size, max_epochs=args.epochs,
                          patience=args.patience, seed=seed, verbose=not args.quiet)


def subsample(idx, n, seed):
    if n is None or len(idx) <= n:
        return idx
    return np.sort(np.random.default_rng(seed).choice(idx, n, replace=False))


def renormalized(data, fit_idx):
    """Copy of ``data`` whose neural-model inputs are normalised with
    statistics from ``fit_idx`` only (used when the training domain changes)."""
    norm = Normalizer().fit(data.X_raw[fit_idx])
    return dataclasses.replace(data, X=norm.transform(data.X_raw), normalizer=norm)


def fit_and_score(name, data, train_idx, val_idx, test_idx, args, seed):
    """Train, pick the F1 threshold on validation, score on test."""
    model = make_model(name, args, seed)
    model.fit(data, train_idx, val_idx)
    r_val, u_val = model.predict(data, val_idx)
    thr = best_threshold(data.y[val_idx], r_val)
    r_test, u_test = model.predict(data, test_idx)
    gates = getattr(model, "last_gates", None)
    metrics = detection_metrics(data.y[test_idx], r_test, thr)
    metrics["TrainTime_s"] = getattr(model, "train_time", float("nan"))
    return {"model": model, "metrics": metrics, "threshold": thr,
            "val": (r_val, u_val), "test": (r_test, u_test), "test_gates": gates}


def mean_std_table(rows: list[dict], by="Model", cols=None) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    cols = cols or [c for c in df.columns if c not in (by, "Seed")]
    g = df.groupby(by, sort=False)[cols]
    mean, std = g.mean(), g.std().fillna(0.0)
    return mean, std


def fmt_table(mean: pd.DataFrame, std: pd.DataFrame, digits=4) -> pd.DataFrame:
    out = mean.copy().astype(object)
    multi = (std.values > 0).any()
    for c in mean.columns:
        out[c] = [f"{m:.{digits}f}" + (f" ± {s:.{digits}f}" if multi else "")
                  for m, s in zip(mean[c], std[c])]
    return out


def to_markdown(df: pd.DataFrame, index=True) -> str:
    d = df.reset_index() if index else df
    cols = [str(c) for c in d.columns]
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    for _, r in d.iterrows():
        cells = [f"{float(v):.4f}" if isinstance(v, (float, np.floating)) else str(v) for v in r.values]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def write_json(obj, path):
    Path(path).write_text(json.dumps(obj, indent=2, default=lambda o: o.item() if hasattr(o, "item") else str(o)))


def is_neural(name):
    return name in MODEL_SPECS
