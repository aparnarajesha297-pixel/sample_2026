"""Neural models: GRU, GAT and RAVEN-X (GAT -> GRU -> evidential head).

All three are the same network with parts switched on or off, so the
comparisons in Experiment 1 isolate one factor at a time:

    GRU      : per-step MLP encoder          -> GRU over T steps -> softmax
    GAT      : GAT encoder (neighbours)      -> current step     -> softmax
    GAT+GRU  : GAT encoder at every step     -> GRU              -> softmax
    RAVEN-X  : GAT encoder at every step     -> GRU              -> evidential
    RAVEN-X-GF (gated fusion), two parallel branches:

        GRU branch : per-step MLP encoder -> GRU over T steps -> h_t ─┐
                                                                     gate -> evidential
        GAT branch : GAT encoder on the current snapshot     -> h_s ─┘

        g = sigmoid(W [h_t ; h_s] + b)          (one gate per hidden unit)
        h = g * h_t + (1 - g) * h_s

      The mean of g says how much a prediction leaned on time (g -> 1) versus
      neighbours (g -> 0); it is reported per attack type.

The GAT layer is written in plain PyTorch (no torch-geometric dependency). It
is GATv2-style attention with edge attributes, plus a separate root/self
projection so the node can compare its own report with what its neighbours
report.
"""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


def scatter_softmax(score: torch.Tensor, index: torch.Tensor, n: int) -> torch.Tensor:
    """Softmax of ``score`` (E, H) over edges sharing the same ``index``."""
    H = score.shape[1]
    idx = index.unsqueeze(1).expand(-1, H)
    mx = torch.full((n, H), float("-inf"), device=score.device, dtype=score.dtype)
    mx = mx.scatter_reduce(0, idx, score, reduce="amax", include_self=True)
    ex = torch.exp(score - mx[index])
    den = torch.zeros((n, H), device=score.device, dtype=score.dtype).index_add_(0, index, ex)
    return ex / (den[index] + 1e-16)


class EdgeGATLayer(nn.Module):
    def __init__(self, d_in, d_out, heads=4, d_edge=3, dropout=0.1):
        super().__init__()
        self.h, self.d = heads, d_out
        self.w_src = nn.Linear(d_in, heads * d_out)
        self.w_dst = nn.Linear(d_in, heads * d_out)
        self.w_edge = nn.Linear(d_edge, heads * d_out, bias=False)
        self.att = nn.Parameter(torch.empty(heads, d_out))
        self.root = nn.Linear(d_in, heads * d_out)
        self.drop = nn.Dropout(dropout)
        nn.init.xavier_uniform_(self.att)
        self.last_attention = None

    def forward(self, x, src, dst, eattr):
        n = x.shape[0]
        hs = (self.w_src(x)[src] + self.w_edge(eattr)).view(-1, self.h, self.d)
        hd = self.w_dst(x)[dst].view(-1, self.h, self.d)
        score = (F.leaky_relu(hs + hd, 0.2) * self.att).sum(-1)       # (E, H)
        alpha = scatter_softmax(score, dst, n)
        self.last_attention = alpha.detach()
        msg = hs * self.drop(alpha).unsqueeze(-1)
        agg = torch.zeros((n, self.h, self.d), device=x.device, dtype=x.dtype)
        agg.index_add_(0, dst, msg)
        # nodes without neighbours fall back to their own projection
        return agg.reshape(n, -1) + self.root(x)


class StepEncoder(nn.Module):
    """Maps step features to an embedding, with or without neighbours."""

    def __init__(self, n_feat, hidden=64, use_graph=True, heads=4, layers=2, dropout=0.1):
        super().__init__()
        self.use_graph = use_graph
        self.inp = nn.Sequential(nn.Linear(n_feat, hidden), nn.ELU())
        self.layers = nn.ModuleList()
        if use_graph:
            d = hidden
            for _ in range(layers):
                self.layers.append(EdgeGATLayer(d, hidden // heads, heads, dropout=dropout))
                d = hidden
        else:
            for _ in range(layers):
                self.layers.append(nn.Linear(hidden, hidden))
        self.norms = nn.ModuleList([nn.LayerNorm(hidden) for _ in range(layers)])
        self.hops = layers if use_graph else 0

    def forward(self, x, src=None, dst=None, eattr=None):
        h = self.inp(x)
        for layer, norm in zip(self.layers, self.norms):
            out = layer(h, src, dst, eattr) if self.use_graph else layer(h)
            h = norm(h + F.elu(out))
        return h


class DetectorNet(nn.Module):
    def __init__(self, n_feat, hidden=64, use_graph=True, use_temporal=True,
                 evidential=False, fusion=False, heads=4, layers=2, dropout=0.1):
        super().__init__()
        self.use_graph, self.use_temporal, self.evidential = use_graph, use_temporal, evidential
        self.fusion = fusion
        # in fusion mode ``encoder`` is the spatial (GAT) branch and
        # ``temporal_encoder`` the per-step encoder feeding the GRU branch
        self.encoder = StepEncoder(n_feat, hidden, use_graph, heads, layers, dropout)
        if fusion:
            assert use_graph and use_temporal
            self.temporal_encoder = StepEncoder(n_feat, hidden, False, heads, layers, dropout)
            self.gate = nn.Linear(2 * hidden, hidden)
        self.last_gate = None
        if use_temporal:
            # +1 input: "this position of the window is real, not padding"
            self.gru = nn.GRU(hidden + 1, hidden, batch_first=True)
        self.head = nn.Sequential(nn.Dropout(dropout), nn.Linear(hidden, hidden), nn.ELU(),
                                  nn.Linear(hidden, 2))

    @property
    def hops(self):
        return self.encoder.hops

    def forward(self, x_nodes, win_local, src=None, dst=None, eattr=None):
        """x_nodes: features of the nodes in the batch subgraph.
        win_local: (B, T) local node index per window slot, -1 = padding
        (T = 1 for non-temporal models)."""
        if self.fusion:
            return self.head(self._fuse(x_nodes, win_local, src, dst, eattr))
        z = self.encoder(x_nodes, src, dst, eattr)
        if self.use_temporal:
            valid = (win_local >= 0)
            seq = z[win_local.clamp(min=0)] * valid.unsqueeze(-1)
            seq = torch.cat([seq, valid.unsqueeze(-1).float()], dim=-1)
            _, h = self.gru(seq)
            rep = h[-1]
        else:
            rep = z[win_local[:, -1]]
        return self.head(rep)

    def _gru_over(self, z, win_local):
        valid = (win_local >= 0)
        seq = z[win_local.clamp(min=0)] * valid.unsqueeze(-1)
        seq = torch.cat([seq, valid.unsqueeze(-1).float()], dim=-1)
        _, h = self.gru(seq)
        return h[-1]

    def _fuse(self, x_nodes, win_local, src, dst, eattr):
        h_t = self._gru_over(self.temporal_encoder(x_nodes), win_local)
        h_s = self.encoder(x_nodes, src, dst, eattr)[win_local[:, -1]]
        g = torch.sigmoid(self.gate(torch.cat([h_t, h_s], dim=-1)))
        self.last_gate = g.mean(-1).detach()
        return g * h_t + (1 - g) * h_s


# ---------------------------------------------------------------------------
# Evidential output (Sensoy et al., 2018) for K = 2 classes
# ---------------------------------------------------------------------------

def evidential_outputs(logits):
    """Returns (risk, uncertainty, alpha).
    risk = expected P(attack) = alpha_1 / S, uncertainty = K / S (vacuity)."""
    evidence = F.softplus(logits)
    alpha = evidence + 1.0
    S = alpha.sum(-1)
    risk = alpha[:, 1] / S
    unc = 2.0 / S
    return risk, unc, alpha


def evidential_loss(logits, y, kl_weight):
    _, _, alpha = evidential_outputs(logits)
    Y = F.one_hot(y, 2).float()
    S = alpha.sum(-1, keepdim=True)
    nll = (Y * (torch.digamma(S) - torch.digamma(alpha))).sum(-1)
    # KL( Dir(alpha_tilde) || Dir(1) ): penalises evidence for the wrong class
    a = Y + (1 - Y) * alpha
    Sa = a.sum(-1, keepdim=True)
    kl = (torch.lgamma(Sa).squeeze(-1) - torch.lgamma(torch.tensor(2.0, device=a.device))
          - torch.lgamma(a).sum(-1)
          + ((a - 1) * (torch.digamma(a) - torch.digamma(Sa))).sum(-1))
    return (nll + kl_weight * kl).mean()


def softmax_outputs(logits):
    p = torch.softmax(logits, -1)
    risk = p[:, 1]
    # for deterministic models "uncertainty" is the normalised entropy
    ent = -(p * torch.log(p.clamp_min(1e-12))).sum(-1) / torch.log(torch.tensor(2.0))
    return risk, ent
