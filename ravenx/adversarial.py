"""Stealthy targeted poisoning and decision-flip measures (rows 18 and 19).

Row 18 (ADDR). One compromised RSU tries to flip the accept/reject decision
for one target vehicle while the global model still looks normal. Following
the targeted model-poisoning setup of Bhagoji et al. (ICML 2019), each round
the RSU

  1. trains honestly on its own data (the benign update it would send),
  2. separately trains from the same global parameters on its own data plus
     the target's observed messages with flipped labels (repeated so they are
     about ``target_share`` of the local batch stream),
  3. sends either
       norm-matched: the adversarial update rescaled to the benign update's
                     norm (same size as an honest update), or
       boosted:      benign + boost * (adversarial - benign), which survives
                     1/n averaging but is larger than an honest update.

The adversarial training uses its own detector instance and random stream,
so the honest clients' data order is identical with and without the attack.

Decisions. A vehicle is decided with Eq. 14 on the calibrated belief:
reject when C_FA * p > C_FR * (1 - p). ADDR is measured only at the steps
where the honest SVoI controller stops (does not ask for more evidence).
"""

from __future__ import annotations

import numpy as np
import torch
from torch.nn.utils import parameters_to_vector, vector_to_parameters

STRENGTHS = ("norm-matched", "boosted")


def reject_decision(p, C_FA=100.0, C_FR=20.0):
    """Eq. 14: True = reject (the cheaper stop is rejecting)."""
    return C_FA * np.asarray(p) > C_FR * (1 - np.asarray(p))


def flip_rates(honest_reject, other_reject):
    """Share of decisions that differ, split by direction.
    wrongly accepted: honest rejects, other accepts; wrongly rejected: the reverse."""
    h, o = np.asarray(honest_reject, bool), np.asarray(other_reject, bool)
    n = max(len(h), 1)
    return {"ADDR": float((h != o).sum() / n),
            "wrongly accepted": float((h & ~o).sum() / n),
            "wrongly rejected": float((~h & o).sum() / n),
            "decisions": int(len(h))}


class TargetedAttack:
    """Callable for ``run_federated(attack=...)``."""

    def __init__(self, make_detector, data, own_idx, target_idx, strength="norm-matched",
                 boost=20.0, target_share=0.2, seed=2):
        if strength not in STRENGTHS:
            raise ValueError(strength)
        self.det = make_detector(seed=seed)
        self.data, self.strength, self.boost = data, strength, boost
        reps = max(1, int(round(target_share * len(own_idx) / ((1 - target_share) * max(len(target_idx), 1)))))
        self.idx = np.concatenate([own_idx, np.tile(target_idx, reps)])
        self.labels = data.y.copy()
        self.labels[target_idx] = 1 - data.y[target_idx]
        self.log = []

    def __call__(self, k, theta, benign, r):
        vector_to_parameters(theta.clone(), self.det.net.parameters())
        opt = torch.optim.Adam(self.det.net.parameters(), lr=self.det.lr, weight_decay=self.det.wd)
        self.det.train_epoch(self.data, self.idx, r, opt=opt, label_override=self.labels)
        adv = parameters_to_vector(self.det.net.parameters()).detach() - theta
        nb, na = float(benign.norm()), float(adv.norm())
        if self.strength == "norm-matched":
            out = adv * (nb / max(na, 1e-12))
        else:
            out = benign + self.boost * (adv - benign)
        self.log.append({"round": r, "benign_norm": nb, "adversarial_norm": na, "sent_norm": float(out.norm()),
                         "cosine_to_benign": float(torch.dot(out, benign) / (out.norm() * benign.norm() + 1e-12))})
        return out
