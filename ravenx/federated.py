"""Federated training of RAVEN-X across RSUs (plan phases 12-13).

Each RSU owns the observations of the receivers in its area and trains the
model locally; only model updates (parameter deltas) reach the server. The
aggregation rules below operate on a (n_clients, n_params) matrix of updates.

This is a self-contained simulation (sequential clients in one process). The
aggregators are plain functions of the update matrix, so they can be dropped
into a Flower ``Strategy.aggregate_fit`` unchanged when moving to a
multi-process Flower deployment.
"""

from __future__ import annotations

import time

import numpy as np
import torch
from sklearn.cluster import KMeans
from torch.nn.utils import parameters_to_vector, vector_to_parameters

# ---------------------------------------------------------------------------
# Aggregation rules
# ---------------------------------------------------------------------------


def fedavg(U, w, **_):
    w = w / w.sum()
    return (w[:, None] * U).sum(0)


def coord_median(U, w, **_):
    return np.median(U, axis=0)


def krum(U, w, n_malicious=0, **_):
    """Blanchard et al. (2017): pick the update closest to its n - f - 2
    nearest neighbours."""
    n = len(U)
    k = max(1, n - n_malicious - 2)
    sq = (U ** 2).sum(1)
    D = sq[:, None] + sq[None, :] - 2 * U @ U.T
    np.fill_diagonal(D, np.inf)
    scores = np.sort(D, axis=1)[:, :k].sum(1)
    return U[int(np.argmin(scores))]


def capped_simplex_projection(raw_scores, kappa):
    """Stage 1 of RS-WeightedTrim: weights with sum 1 and no weight above
    kappa / n, by water-filling.

    Normalise the non-negative scores; clamp every weight above the cap to
    exactly the cap; hand the removed excess to the not-yet-capped RSUs in
    proportion to their current weight; repeat (at most n times) until no
    weight exceeds the cap. Plain clip-and-renormalise does not guarantee the
    cap, which is why the loop is needed.

    Edge case not covered by the guide: if every uncapped RSU has weight 0,
    the excess cannot be shared proportionally, so it is shared equally among
    them (otherwise the weights could not sum to 1).
    """
    raw = np.clip(np.asarray(raw_scores, dtype=np.float64), 0.0, None)
    n = len(raw)
    if kappa < 1:
        raise ValueError("kappa must be >= 1, otherwise n * kappa / n < 1 and no valid weights exist")
    cap = kappa / n
    W = raw / raw.sum() if raw.sum() > 0 else np.full(n, 1.0 / n)
    capped = np.zeros(n, dtype=bool)
    for _ in range(n + 1):
        over = ~capped & (W > cap)
        if not over.any():
            break
        excess = float((W[over] - cap).sum())
        W[over] = cap
        capped |= over
        free = ~capped
        if not free.any():
            break
        total = W[free].sum()
        if total > 0:
            W[free] += excess * W[free] / total
        else:
            W[free] += excess / free.sum()
    return W


def weighted_trimmed_mean(U, W, beta_trim):
    """Stage 2 of RS-WeightedTrim: for every coordinate, drop the
    ceil(beta_trim * n) lowest and highest values, then average the survivors
    weighted by their Stage-1 weights, renormalised over the survivors only."""
    n = U.shape[0]
    k = int(np.ceil(beta_trim * n))
    if not 0 <= beta_trim < 0.5 or n - 2 * k < 1:
        raise ValueError(f"beta_trim={beta_trim} leaves no survivors for n={n}")
    order = np.argsort(U, axis=0, kind="stable")[k:n - k]          # (m, d) survivor ids
    vals = np.take_along_axis(U, order, axis=0)
    w = W[order]
    s = w.sum(axis=0, keepdims=True)
    # all survivors of a coordinate with zero weight: fall back to their plain mean
    w = np.where(s > 0, w / np.where(s > 0, s, 1.0), 1.0 / w.shape[0])
    return (w * vals).sum(axis=0)


def _reputation(state, U):
    """Non-negative trust score per RSU: exponential moving average of
    max(0, cosine(update_i, coordinate-wise median update))."""
    med = np.median(U, axis=0)
    norms = np.linalg.norm(U, axis=1)
    cos = U @ med / (norms * np.linalg.norm(med) + 1e-12)
    state.rep = state.beta * state.rep + (1 - state.beta) * np.clip(cos, 0, 1)
    state.history.append(state.rep.copy())
    return norms


class RSWeightedTrim:
    """RS-WeightedTrim as specified for the paper's Theorem 1.

      raw score  W^_i = reputation_i * n_i  (n_i = local sample count)
      Stage 1    W = capped-simplex projection of W^: sum 1, every W_i <= kappa / n
      Stage 2    coordinate-wise: trim ceil(beta_trim * n) from each end, then
                 average the survivors with their W, renormalised over the
                 survivors only

    The order (cap, then trim) and the survivor-only renormalisation are what
    the bound assumes. Aggregating updates (deltas) instead of parameters gives
    the same model, because every RSU starts from the same global parameters.
    Requires f / n <= beta_trim < 1/2 for f compromised RSUs.
    """

    def __init__(self, n_clients, kappa=2.0, beta_trim=0.2, beta=0.6):
        self.rep = np.ones(n_clients)
        self.kappa, self.beta_trim, self.beta = kappa, beta_trim, beta
        self.history, self.weights = [], []

    def __call__(self, U, w, client_ids=None, **_):
        _reputation(self, U)
        W = capped_simplex_projection(self.rep * w, self.kappa)
        self.weights.append(W)
        return weighted_trimmed_mean(U, W, self.beta_trim)


class ReputationDrop:
    """Baseline (the earlier "RS-WeightedTrim" stand-in): drop the ``trim``
    fraction of RSUs with the lowest reputation, clip the rest to the median
    update norm, average with weights reputation * n_i. Theorem 1 does NOT
    cover this rule."""

    def __init__(self, n_clients, beta=0.6, trim=0.2):
        self.rep = np.ones(n_clients)
        self.beta, self.trim = beta, trim
        self.history = []

    def __call__(self, U, w, client_ids=None, **_):
        norms = _reputation(self, U)
        n_drop = int(np.floor(self.trim * len(U)))
        keep = np.argsort(self.rep)[n_drop:]
        clip = np.minimum(1.0, np.median(norms) / (norms + 1e-12))
        weights = self.rep[keep] * w[keep]
        weights = weights / max(weights.sum(), 1e-12)
        return (weights[:, None] * (U[keep] * clip[keep, None])).sum(0)


def make_aggregator(name, n_clients, n_malicious):
    if name == "FedAvg":
        return fedavg
    if name == "Median":
        return coord_median
    if name == "Krum":
        return lambda U, w, **kw: krum(U, w, n_malicious=n_malicious)
    if name == "RS-WeightedTrim":
        # beta_trim must cover the expected compromised fraction (f / n)
        return RSWeightedTrim(n_clients, kappa=2.0,
                              beta_trim=max(0.2, n_malicious / max(n_clients, 1)))
    if name == "ReputationDrop":
        return ReputationDrop(n_clients)
    raise ValueError(name)


AGGREGATORS = ["FedAvg", "Median", "Krum", "RS-WeightedTrim", "ReputationDrop"]
POISONING = ["none", "label_flip", "sign_flip"]

# ---------------------------------------------------------------------------
# Data partition
# ---------------------------------------------------------------------------


def partition_rsus(data, train_idx, n_rsus, how="spatial", seed=0):
    """Split training steps between RSUs by *receiver*, so each RSU keeps whole
    streams and whole graph snapshots (no raw data crosses RSUs).

    spatial : k-means on each receiver's mean reported position (non-IID)
    random  : receivers assigned uniformly at random (IID)
    attack  : each RSU gets receivers from only a few attack subsets (strongly
              non-IID)
    """
    st = data.steps.iloc[train_idx]
    rec = st.groupby("receiver", observed=True).agg(x=("x", "mean"), y=("y", "mean"),
                                     attack=("attack_type", "first"))
    rng = np.random.default_rng(seed)
    if how == "spatial":
        lab = KMeans(n_rsus, n_init=4, random_state=seed).fit_predict(rec[["x", "y"]].values)
    elif how == "random":
        lab = rng.integers(0, n_rsus, len(rec))
    elif how == "attack":
        atk = {a: i for i, a in enumerate(sorted(rec["attack"].astype(str).unique()))}
        codes = rec["attack"].astype(str).map(atk).values
        lab = (codes * n_rsus // max(len(atk), 1) + rng.integers(0, 2, len(rec))) % n_rsus
    else:
        raise ValueError(how)
    rsu_of = dict(zip(rec.index, lab))
    owner = st["receiver"].map(rsu_of).values
    return [train_idx[owner == k] for k in range(n_rsus)]


# ---------------------------------------------------------------------------
# Training loop
# ---------------------------------------------------------------------------


def run_federated(make_detector, data, clients, aggregator, rounds=10,
                  local_epochs=1, malicious=(), poisoning="none", sign_scale=3.0,
                  eval_fn=None, verbose=True):
    """Returns (global_detector, per-round log, comm_bytes, wall_time)."""
    glob = make_detector(seed=0)
    worker = make_detector(seed=1)
    theta = parameters_to_vector(glob.net.parameters()).detach().clone()
    n_params = theta.numel()
    sizes = np.array([len(c) for c in clients], dtype=float)
    malicious = set(malicious)
    log, comm = [], 0
    t0 = time.time()
    for r in range(rounds):
        updates = []
        for k, idx in enumerate(clients):
            # vector_to_parameters makes the parameters *views* of the vector,
            # so always hand it a copy or local training would write into theta
            vector_to_parameters(theta.clone(), worker.net.parameters())
            opt = torch.optim.Adam(worker.net.parameters(), lr=worker.lr, weight_decay=worker.wd)
            labels = None
            if k in malicious and poisoning == "label_flip":
                labels = data.y.copy()
                labels[idx] = 0          # teach the model that attacks are benign
            if len(idx):
                for e in range(local_epochs):
                    worker.train_epoch(data, idx, r * local_epochs + e, opt=opt, label_override=labels)
            delta = parameters_to_vector(worker.net.parameters()).detach() - theta
            if k in malicious and poisoning == "sign_flip":
                delta = -sign_scale * delta
            updates.append(delta.numpy())
        comm += 2 * len(clients) * n_params * 4          # download + upload, float32
        agg = aggregator(np.stack(updates), sizes, client_ids=np.arange(len(clients)))
        theta = theta + torch.from_numpy(agg.astype(np.float32))
        vector_to_parameters(theta.clone(), glob.net.parameters())
        entry = {"round": r, "elapsed_s": time.time() - t0}
        if eval_fn is not None:
            entry.update(eval_fn(glob))
        log.append(entry)
        if verbose:
            extra = "  ".join(f"{k} {v:.4f}" for k, v in entry.items() if k not in ("round", "elapsed_s"))
            print(f"    round {r:2d}  {extra}  ({entry['elapsed_s']:.0f}s)")
    return glob, log, comm, time.time() - t0
