"""Classical per-observation baselines (E1.1 Random Forest, E1.2 XGBoost)."""

from __future__ import annotations

import time

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier


def _entropy(p):
    p = np.clip(p, 1e-12, 1 - 1e-12)
    return -(p * np.log2(p) + (1 - p) * np.log2(1 - p))


class TabularDetector:
    def __init__(self, name, seed=0, n_jobs=-1):
        self.name = name
        if name == "RandomForest":
            self.model = RandomForestClassifier(
                n_estimators=300, min_samples_leaf=2, n_jobs=n_jobs, random_state=seed)
        elif name == "XGBoost":
            self.model = XGBClassifier(
                n_estimators=600, max_depth=6, learning_rate=0.08, subsample=0.9,
                colsample_bytree=0.9, tree_method="hist", n_jobs=n_jobs,
                random_state=seed, eval_metric="logloss", early_stopping_rounds=40)
        else:
            raise ValueError(name)

    def fit(self, data, train_idx, val_idx):
        t0 = time.time()
        X, y = data.X_raw, data.y
        if self.name == "XGBoost":
            self.model.fit(X[train_idx], y[train_idx],
                           eval_set=[(X[val_idx], y[val_idx])], verbose=False)
        else:
            self.model.fit(X[train_idx], y[train_idx])
        self.train_time = time.time() - t0
        return self

    def predict(self, data, idx):
        if len(idx) == 0:
            return np.zeros(0), np.zeros(0)
        p = self.model.predict_proba(data.X_raw[idx])[:, 1]
        return p, _entropy(p)
