"""SVoI controller: when to decide, and when to gather more evidence (Eqs. 12-17).

At each decision point the RSU either stops (accept or reject the vehicle) or
takes an evidence action and looks again. Every option is priced in the same
unit, an expected cost, and the cheaper option is taken:

    C_accept(b, c) = Cm(c) * C_FA * p(b)                          (Eq. 12)
    C_reject(b, c) = Cm(c) * C_FR * (1 - p(b))                    (Eq. 13)
    C_stop(b, c)   = min(C_accept, C_reject)                      (Eq. 14)
    Q_h(b, a, c)   = Cost(a) + gamma * E_{b' ~ P(.|b,a)} V_{h-1}(b', c)   (Eq. 15)
    V_0(b, c)      = C_stop(b, c)                                 (Eq. 16)
    V_h(b, c)      = min(C_stop(b, c), min_a Q_h(b, a, c))        (Eq. 17)

The value table and the policy are solved offline over a discretised belief
space (Algorithm 1); at runtime a decision is one table lookup.

Modelling choices (agreed before implementation; see
reports/checks/svoi_rswt_guide_verification.md):

* Belief b = (p, u): p is the temperature-scaled P(attack), u the evidential
  uncertainty. The grid uses quantile bins fitted on validation beliefs. A
  cell's p(b) is the mean calibrated p of the validation beliefs in it.
* a1 (passive observation, cost 1) = wait for the vehicle's next message.
  Its transition table is counted from the model's beliefs on consecutive
  steps of the same stream in the VALIDATION split. Cells with fewer than
  n_min transitions are blended with their neighbouring cells.
* a2-a4 (neighbour query, infrastructure cross-check, cryptographic
  challenge; cost 2 / 3 / 5) are not in the dataset. Each is modelled as one
  extra noisy check of the true state with reliability rho_a
  (0.80 / 0.90 / 0.99): p is updated by Bayes' rule, and the positive and
  negative outcomes occur with the probabilities p implies. This is an
  assumption, and is reported as one.
* Criticality: K = 1 level, Cm = 1, until a criticality model exists.
* gamma = 1 by default (the finite horizon keeps V bounded; gamma < 1 would
  make postponed decisions look cheaper).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

STOP_ACCEPT, STOP_REJECT = "accept", "reject"
EVIDENCE = ("a1", "a2", "a3", "a4")
DEFAULT_COST = {"a1": 1.0, "a2": 2.0, "a3": 3.0, "a4": 5.0}
DEFAULT_RHO = {"a2": 0.80, "a3": 0.90, "a4": 0.99}


def quantile_edges(x, n_bins):
    """Inner bin edges at quantiles of x (duplicates removed)."""
    qs = np.quantile(x, np.linspace(0, 1, n_bins + 1)[1:-1])
    return np.unique(qs)


def bayes_update(p, rho, positive):
    """Posterior P(attack) after a check with reliability rho reports
    'attack' (positive=True) or 'benign'."""
    if positive:
        return rho * p / (rho * p + (1 - rho) * (1 - p))
    return (1 - rho) * p / ((1 - rho) * p + rho * (1 - p))


@dataclass
class BeliefGrid:
    p_edges: np.ndarray
    u_edges: np.ndarray
    p_value: np.ndarray = field(default=None)       # p(b) per cell

    @property
    def n_p(self):
        return len(self.p_edges) + 1

    @property
    def n_u(self):
        return len(self.u_edges) + 1

    @property
    def n_states(self):
        return self.n_p * self.n_u

    def p_bin(self, p):
        return np.searchsorted(self.p_edges, p, side="right")

    def u_bin(self, u):
        return np.searchsorted(self.u_edges, u, side="right")

    def state(self, p, u):
        return self.p_bin(p) * self.n_u + self.u_bin(u)

    def unpack(self, s):
        return np.divmod(s, self.n_u)

    @classmethod
    def fit(cls, p, u, n_p=20, n_u=8):
        g = cls(quantile_edges(p, n_p), quantile_edges(u, n_u))
        s = g.state(p, u)
        sums = np.bincount(s, weights=p, minlength=g.n_states)
        cnt = np.bincount(s, minlength=g.n_states)
        # cells with no validation belief: use the middle of their p bin
        lo = np.r_[0.0, g.p_edges]
        hi = np.r_[g.p_edges, 1.0]
        centre = np.repeat((lo + hi) / 2, g.n_u)
        g.p_value = np.where(cnt > 0, sums / np.maximum(cnt, 1), centre)
        return g


def passive_transitions(grid, p, u, stream, n_min=20):
    """P(b' | b, a1) from consecutive steps of the same stream.
    ``p, u, stream`` must be ordered by stream then time."""
    s = grid.state(p, u)
    same = stream[1:] == stream[:-1]
    src, dst = s[:-1][same], s[1:][same]
    S = grid.n_states
    C = np.zeros((S, S))
    np.add.at(C, (src, dst), 1.0)
    n = C.sum(1)
    # neighbour prior: pooled transitions of the cells within one bin
    ip, iu = grid.unpack(np.arange(S))
    prior = np.zeros((S, S))
    for k in range(S):
        near = (np.abs(ip - ip[k]) <= 1) & (np.abs(iu - iu[k]) <= 1)
        row = C[near].sum(0)
        prior[k] = row / row.sum() if row.sum() > 0 else np.eye(S)[k]
    lam = np.where(n < n_min, n_min, 0.0)
    P = (C + lam[:, None] * prior) / (n + lam)[:, None]
    return P, n


def check_transitions(grid, rho):
    """P(b' | b, a) for an evidence check of reliability rho (Bayes update of
    p; the uncertainty bin is kept, which is conservative)."""
    S = grid.n_states
    P = np.zeros((S, S))
    p = grid.p_value
    _, iu = grid.unpack(np.arange(S))
    pr_pos = rho * p + (1 - rho) * (1 - p)
    for positive, prob in ((True, pr_pos), (False, 1 - pr_pos)):
        dst = grid.p_bin(bayes_update(p, rho, positive)) * grid.n_u + iu
        np.add.at(P, (np.arange(S), dst), prob)
    return P


@dataclass
class SVoIPolicy:
    grid: BeliefGrid
    V: np.ndarray                 # (H_max + 1, S)
    action: np.ndarray            # (H_max + 1, S) indices into self.actions
    actions: tuple
    C_FA: float
    C_FR: float
    cost: dict
    rho: dict

    def decide(self, p, u, horizon):
        h = min(int(horizon), self.V.shape[0] - 1)
        return self.actions[self.action[h, self.grid.state(p, u)]]


def stop_costs(p, C_FA, C_FR, crit=1.0):
    return crit * C_FA * p, crit * C_FR * (1 - p)


def solve(grid, P, cost, H_max, C_FA=100.0, C_FR=20.0, gamma=1.0, crit=1.0, rho=None):
    """Backward induction over h = 0 .. H_max (Algorithm 1).
    P: dict action -> (S, S) transition matrix; cost: dict action -> cost."""
    acc, rej = stop_costs(grid.p_value, C_FA, C_FR, crit)
    c_stop = np.minimum(acc, rej)
    evid = [a for a in EVIDENCE if a in P]
    actions = (STOP_ACCEPT, STOP_REJECT) + tuple(evid)
    S = grid.n_states
    V = np.zeros((H_max + 1, S))
    A = np.zeros((H_max + 1, S), dtype=np.int64)
    V[0] = c_stop
    A[0] = np.where(acc <= rej, 0, 1)
    for h in range(1, H_max + 1):
        options = np.vstack([acc, rej] + [cost[a] + gamma * P[a] @ V[h - 1] for a in evid])
        A[h] = options.argmin(0)          # ties go to stopping (listed first)
        V[h] = options.min(0)
    return SVoIPolicy(grid, V, A, actions, C_FA, C_FR, dict(cost), dict(rho or DEFAULT_RHO))


def run_episode(policy, p_seq, u_seq, label_seq, H, rng, mode="svoi",
                interval=2, rand_p=0.5, fixed_action="a2"):
    """Replay one vehicle stream from its current step under a policy.

    p_seq / u_seq / label_seq: beliefs and labels from the start step onward
    (index 0 = now). Passive observation (a1) moves to the next real step;
    a check (a2-a4) updates p by Bayes' rule with an outcome drawn from the
    check's reliability and the true label of the current step (the label
    only simulates what the check would report; it is never seen by the
    policy). The decision is scored against the label of the step at which
    the vehicle is decided.

    mode: "svoi"   the solved policy
          "never"  decide immediately (no evidence)
          "always" wait for the next message (a1) until the horizon, then decide
          "fixed"  a1 at every step, plus ``fixed_action`` every ``interval``-th step
          "random" a random evidence action with probability rand_p, else decide
    """
    C_FA, C_FR, cost, rho = policy.C_FA, policy.C_FR, policy.cost, policy.rho
    t, p, u, spent, n_obs, queries = 0, float(p_seq[0]), float(u_seq[0]), 0.0, 1, 0
    for h in range(H, -1, -1):
        can_wait = t + 1 < len(p_seq)
        if h == 0:
            a = None
        elif mode == "svoi":
            a = policy.decide(p, u, h)
            a = None if a in (STOP_ACCEPT, STOP_REJECT) else a
        elif mode == "never":
            a = None
        elif mode == "always":
            a = "a1"
        elif mode == "fixed":
            a = fixed_action if (H - h + 1) % interval == 0 else "a1"
            if a == fixed_action and fixed_action not in rho:
                a = "a1"
        elif mode == "random":
            a = rng.choice(EVIDENCE) if rng.random() < rand_p else None
        else:
            raise ValueError(mode)
        if a == "a1" and not can_wait:
            a = None                         # stream ended: must decide
        if a is None:
            break
        spent += cost[a]
        queries += 1
        if a == "a1":
            t += 1
            n_obs += 1
            p, u = float(p_seq[t]), float(u_seq[t])
        else:
            truth = bool(label_seq[t])
            positive = rng.random() < (rho[a] if truth else 1 - rho[a])
            p = float(np.clip(bayes_update(p, rho[a], positive), 1e-6, 1 - 1e-6))
    reject = C_FA * p > C_FR * (1 - p)       # decide by the cheaper stop (Eq. 14)
    y = int(label_seq[t])
    error = C_FA if (y == 1 and not reject) else (C_FR if (y == 0 and reject) else 0.0)
    return {"reject": int(reject), "label": y, "evidence_cost": spent, "error_cost": error,
            "total_cost": spent + error, "observations": n_obs, "queries": queries}


def expectimax(grid, P, cost, h, s, C_FA, C_FR, gamma=1.0):
    """Brute-force value by explicit recursion (for testing solve())."""
    acc, rej = stop_costs(grid.p_value[s], C_FA, C_FR)
    best = min(acc, rej)
    if h == 0:
        return best
    for a, M in P.items():
        nxt = np.flatnonzero(M[s] > 0)
        val = cost[a] + gamma * sum(M[s, j] * expectimax(grid, P, cost, h - 1, j, C_FA, C_FR, gamma)
                                    for j in nxt)
        best = min(best, val)
    return best
