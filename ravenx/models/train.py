"""Training / inference for the neural detectors on the step dataset."""

from __future__ import annotations

import copy
import time

import numpy as np
import torch
import torch.nn.functional as F

from ..metrics import pr_auc
from .nn import DetectorNet, evidential_loss, evidential_outputs, softmax_outputs

MODEL_SPECS = {
    # name: (use_graph, use_temporal, evidential)
    "GRU": (False, True, False),
    "GAT": (True, False, False),
    "GAT+GRU": (True, True, False),
    "RAVEN-X": (True, True, True),
}


def make_batch(data, targets, net, device):
    """Subgraph + window tensors for a batch of target steps."""
    T = data.win.shape[1] if net.use_temporal else 1
    win = data.win[targets][:, -T:]
    needed = np.unique(win[win >= 0])
    if net.use_graph:
        nodes, ls, ld, eids, _ = data.graph.subgraph(needed, net.hops)
        src = torch.from_numpy(ls).to(device)
        dst = torch.from_numpy(ld).to(device)
        eattr = torch.from_numpy(data.graph.eattr[eids]).to(device)
    else:
        nodes, src, dst, eattr = needed, None, None, None
    local = np.where(win >= 0, np.searchsorted(nodes, np.maximum(win, 0)), -1)
    x = torch.from_numpy(data.X[nodes]).to(device)
    return x, torch.from_numpy(local).to(device), src, dst, eattr


class NeuralDetector:
    def __init__(self, name, n_feat, hidden=64, lr=1e-3, weight_decay=1e-5,
                 batch_size=256, max_epochs=15, patience=3, kl_anneal=5,
                 seed=0, device="cpu", verbose=True):
        use_graph, use_temporal, evidential = MODEL_SPECS[name]
        torch.manual_seed(seed)
        self.name = name
        self.net = DetectorNet(n_feat, hidden, use_graph, use_temporal, evidential).to(device)
        self.lr, self.wd = lr, weight_decay
        self.batch_size, self.max_epochs, self.patience = batch_size, max_epochs, patience
        self.kl_anneal = kl_anneal
        self.device, self.verbose = device, verbose
        self.rng = np.random.default_rng(seed)
        self.history = []

    # -- core ---------------------------------------------------------------
    def _loss(self, logits, y, epoch):
        if self.net.evidential:
            return evidential_loss(logits, y, min(1.0, (epoch + 1) / self.kl_anneal))
        return F.cross_entropy(logits, y)

    def train_epoch(self, data, train_idx, epoch, opt=None, label_override=None):
        """One pass over ``train_idx``. ``label_override`` lets a federated
        client train on manipulated labels (label-flipping poisoning)."""
        self.net.train()
        opt = opt or self._opt
        labels = data.y if label_override is None else label_override
        perm = self.rng.permutation(train_idx)
        total, n = 0.0, 0
        for i in range(0, len(perm), self.batch_size):
            t = perm[i:i + self.batch_size]
            x, win, src, dst, eattr = make_batch(data, t, self.net, self.device)
            y = torch.from_numpy(labels[t]).to(self.device)
            logits = self.net(x, win, src, dst, eattr)
            loss = self._loss(logits, y, epoch)
            opt.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.net.parameters(), 5.0)
            opt.step()
            total += loss.item() * len(t); n += len(t)
        return total / max(n, 1)

    def fit(self, data, train_idx, val_idx):
        self._opt = torch.optim.Adam(self.net.parameters(), lr=self.lr, weight_decay=self.wd)
        best, best_state, bad = -1.0, None, 0
        t0 = time.time()
        for epoch in range(self.max_epochs):
            loss = self.train_epoch(data, train_idx, epoch)
            risk, _ = self.predict(data, val_idx)
            score = pr_auc(data.y[val_idx], risk)
            self.history.append({"epoch": epoch, "loss": loss, "val_pr_auc": score})
            if self.verbose:
                print(f"    [{self.name}] epoch {epoch:2d} loss {loss:.4f} val PR-AUC {score:.4f}"
                      f"  ({time.time() - t0:.0f}s)")
            if score > best + 1e-4:
                best, best_state, bad = score, copy.deepcopy(self.net.state_dict()), 0
            else:
                bad += 1
                if bad >= self.patience:
                    break
        if best_state is not None:
            self.net.load_state_dict(best_state)
        self.train_time = time.time() - t0
        return self

    @torch.no_grad()
    def predict(self, data, idx, batch_size=2048):
        """Returns (risk, uncertainty) arrays for steps ``idx``."""
        self.net.eval()
        risks, uncs = [], []
        for i in range(0, len(idx), batch_size):
            t = idx[i:i + batch_size]
            logits = self.net(*make_batch(data, t, self.net, self.device))
            if self.net.evidential:
                r, u, _ = evidential_outputs(logits)
            else:
                r, u = softmax_outputs(logits)
            risks.append(r.cpu().numpy()); uncs.append(u.cpu().numpy())
        if not risks:
            return np.zeros(0), np.zeros(0)
        return np.concatenate(risks), np.concatenate(uncs)

    def n_params(self):
        return sum(p.numel() for p in self.net.parameters())
