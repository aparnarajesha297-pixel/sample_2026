"""TRUST / VERIFY / REJECT policy from risk and uncertainty (plan phase 7).

The thresholds are chosen on the validation split, never on test:

  u_max  : uncertainty above this is "not confident" -> VERIFY
  t_high : lowest risk at which confident REJECTs reach ``reject_precision``
  t_low  : highest risk at which confident TRUSTs keep the share of attacks
           among trusted observations at or below ``trust_miss``

  TRUST   if risk <  t_low  and u <= u_max
  REJECT  if risk >= t_high and u <= u_max
  VERIFY  otherwise
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd

TRUST, VERIFY, REJECT = "TRUST", "VERIFY", "REJECT"


@dataclass
class Policy:
    t_low: float
    t_high: float
    u_max: float

    def apply(self, risk, unc):
        d = np.full(len(risk), VERIFY, dtype=object)
        certain = unc <= self.u_max
        d[(risk < self.t_low) & certain] = TRUST
        d[(risk >= self.t_high) & certain] = REJECT
        return d

    def to_dict(self):
        return asdict(self)


FIXED_POLICY = Policy(t_low=0.30, t_high=0.80, u_max=np.inf)   # the plan's initial levels


def fit_policy(risk, unc, y, reject_precision=0.95, trust_miss=0.02,
               unc_quantile=0.90) -> Policy:
    u_max = float(np.quantile(unc, unc_quantile))
    c = unc <= u_max
    r, t = risk[c], y[c]
    grid = np.unique(np.quantile(r, np.linspace(0, 1, 401)))

    t_high = 1.01                          # never reject if the target is unreachable
    for th in grid:                        # ascending: first one that is precise enough
        sel = r >= th
        if sel.sum() >= 10 and t[sel].mean() >= reject_precision:
            t_high = float(th)
            break

    t_low = 0.0                            # never trust if the target is unreachable
    for tl in grid[::-1]:                  # descending: largest safe trust threshold
        sel = r < tl
        if sel.sum() >= 10 and t[sel].mean() <= trust_miss:
            t_low = float(tl)
            break
    t_low = min(t_low, t_high)
    return Policy(t_low, t_high, u_max)


def summarize(decisions, y) -> pd.DataFrame:
    rows = []
    for d in (TRUST, VERIFY, REJECT):
        m = decisions == d
        rows.append({
            "decision": d,
            "count": int(m.sum()),
            "share": float(m.mean()),
            "attack_rate_in_bucket": float(y[m].mean()) if m.any() else float("nan"),
            "share_of_all_attacks": float((m & (y == 1)).sum() / max((y == 1).sum(), 1)),
            "share_of_all_benign": float((m & (y == 0)).sum() / max((y == 0).sum(), 1)),
        })
    return pd.DataFrame(rows)
