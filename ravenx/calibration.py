"""Post-hoc temperature scaling (Guo et al., 2017).

The logits z of a trained network are divided by one scalar T > 0. T is
fitted on the validation split only, by minimising the negative
log-likelihood of the labels; the test split is never used to choose it.

Two ways of turning the scaled logits into P(attack):

  "softmax"     p = softmax(z / T)[attack]
  "evidential"  alpha = softplus(z / T) + 1,  p = alpha_attack / sum(alpha)
                (the Dirichlet mean RAVEN-X reports; at T = 1 this is the
                model's uncalibrated output, so "before" is comparable)

For the evidential head the uncertainty K / S is recomputed from the scaled
evidence as well.
"""

from __future__ import annotations

import numpy as np
from scipy.optimize import minimize_scalar


def _softplus(x):
    return np.logaddexp(0.0, x)


def probs(z, T=1.0, mode="softmax"):
    """Returns (p_attack, uncertainty) for logits z (N, 2) at temperature T."""
    z = np.asarray(z, dtype=np.float64) / T
    if mode == "evidential":
        alpha = _softplus(z) + 1.0
        S = alpha.sum(1)
        return alpha[:, 1] / S, 2.0 / S
    zz = z - z.max(1, keepdims=True)
    e = np.exp(zz)
    p = e / e.sum(1, keepdims=True)
    ent = -(p * np.log(np.clip(p, 1e-12, None))).sum(1) / np.log(2)
    return p[:, 1], ent


def nll(y, p):
    p = np.clip(p, 1e-7, 1 - 1e-7)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


def fit_temperature(z_val, y_val, mode="softmax", bounds=(0.02, 50.0)):
    """T minimising validation NLL, searched over log T."""
    def obj(log_t):
        return nll(y_val, probs(z_val, np.exp(log_t), mode)[0])
    res = minimize_scalar(obj, bounds=(np.log(bounds[0]), np.log(bounds[1])),
                          method="bounded", options={"xatol": 1e-4})
    T = float(np.exp(res.x))
    if T <= bounds[0] * 1.01 or T >= bounds[1] * 0.99:
        print(f"    warning: temperature {T:.3f} hit the search bound {bounds}")
    return T
