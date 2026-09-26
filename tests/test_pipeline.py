"""Fast checks of the data pipeline, models and aggregators.

Run with:  python -m pytest -q
"""

import json

import numpy as np
import pandas as pd
import pytest
import torch

from ravenx.config import FEATURES
from ravenx.data.nextgen import load_nextgen, parse_path_meta
from ravenx.data.synthetic import generate_dataset
from ravenx.decision import fit_policy
from ravenx.federated import RSWeightedTrim, coord_median, fedavg, krum
from ravenx.metrics import best_threshold, ece
from ravenx.models.nn import evidential_loss, evidential_outputs
from ravenx.models.train import MODEL_SPECS, NeuralDetector
from ravenx.pipeline import prepare


@pytest.fixture(scope="module")
def data():
    msgs = generate_dataset(roads=("urban",), densities=("low",),
                            attacks=["constantSpeedOffset", "trafficCongestionSybil"],
                            duration=30, n_observers=4, verbose=False)
    return msgs, prepare(msgs, verbose=False)


def test_splits_and_labels(data):
    msgs, d = data
    assert set(msgs["split"]) == {"train", "val", "test"}
    assert 0.05 < msgs["attacker"].mean() < 0.6
    assert set(d.steps["label"].unique()) <= {0, 1}
    assert np.isfinite(d.X).all() and np.isfinite(d.X_raw).all()


def test_windows_stay_in_stream(data):
    _, d = data
    valid = d.win >= 0
    rows = np.nonzero(valid)[0]
    assert (d.steps["stream"].values[d.win[valid]] == d.steps["stream"].values[rows]).all()
    # last slot is the step itself, earlier slots are strictly older
    assert (d.win[:, -1] == np.arange(len(d.win))).all()
    b = d.steps["bin"].values
    ok = d.win[:, -2] >= 0
    assert (b[d.win[ok, -2]] < b[ok]).all()


def test_graph_edges_same_snapshot_and_radius(data):
    _, d = data
    g = d.graph
    assert (d.group[g.src] == d.group[g.dst]).all()
    assert (g.eattr[:, 0] < 1.0).all()
    # symmetric
    fwd = set(zip(g.src.tolist(), g.dst.tolist()))
    assert all((b, a) in fwd for a, b in list(fwd)[:500])


def test_subgraph_contains_two_hops(data):
    _, d = data
    t = np.arange(0, len(d.steps), 97)
    nodes, ls, ld, eids, loc_t = d.graph.subgraph(t, 2)
    assert (nodes[loc_t] == t).all()
    one_hop = d.graph.src[d.graph.in_edges(t)]
    assert np.isin(one_hop, nodes).all()


@pytest.mark.parametrize("name", list(MODEL_SPECS))
def test_neural_models_train_and_predict(data, name):
    _, d = data
    tr, va = d.idx("train")[:2000], d.idx("val")[:500]
    det = NeuralDetector(name, len(FEATURES), hidden=16, max_epochs=1, verbose=False)
    det.fit(d, tr, va)
    r, u = det.predict(d, va)
    assert r.shape == u.shape == (len(va),)
    assert ((r >= 0) & (r <= 1)).all()
    if name == "RAVEN-X":
        assert ((u > 0) & (u <= 1)).all()


def test_evidential_head():
    logits = torch.tensor([[0.0, 10.0], [10.0, 0.0], [0.0, 0.0]])
    risk, unc, alpha = evidential_outputs(logits)
    assert risk[0] > 0.8 and risk[1] < 0.2 and abs(risk[2] - 0.5) < 1e-6
    assert unc[2] > unc[0]           # no evidence -> maximal uncertainty
    loss = evidential_loss(logits, torch.tensor([1, 0, 1]), kl_weight=1.0)
    assert torch.isfinite(loss)


def test_metrics_and_policy():
    rng = np.random.default_rng(0)
    y = rng.integers(0, 2, 5000)
    p = np.clip(y * 0.7 + rng.normal(0.15, 0.15, 5000), 0, 1)
    thr = best_threshold(y, p)
    assert 0 < thr < 1
    assert ece(y, y.astype(float)) == 0.0
    u = rng.uniform(0, 1, 5000)
    pol = fit_policy(p, u, y)
    assert pol.t_low <= pol.t_high


def test_aggregators_resist_outliers():
    rng = np.random.default_rng(0)
    honest = rng.normal(1.0, 0.1, (8, 50))
    bad = -20 * np.ones((2, 50))
    U = np.vstack([honest, bad]); w = np.ones(10)
    assert fedavg(U, w).mean() < 0                    # FedAvg is dragged away
    assert coord_median(U, w).mean() > 0.8
    assert krum(U, w, n_malicious=2).mean() > 0.8
    rs = RSWeightedTrim(10)
    for _ in range(3):
        out = rs(U, w)
    assert out.mean() > 0.8


def test_nextgen_loader(tmp_path):
    rec = {"rcvTime": 1_000_000_000, "sendTime": 999_000_000, "sender_id": "12",
           "sender_alias": 7, "messageID": 1, "attacker": 1,
           "receiver": {"pos": [0, 0, 0]},
           "sender": {"pos": [10.0, 5.0, 0.0], "spd": 13.2, "acl": 0.1, "hed": 90.0,
                      "driversProfile": "Normal"}}
    f = tmp_path / "InTAS_highway_2_constantPositionOffset" / "train" / "rx_42.json"
    f.parent.mkdir(parents=True)
    f.write_text(json.dumps([rec, {**rec, "rcvTime": 2_000_000_000, "sendTime": 1_999_000_000,
                                   "messageID": 2}]))
    meta = parse_path_meta(f, tmp_path)
    assert meta["split"] == "train" and meta["attack_type"] == "constantPositionOffset"
    assert meta["scenario"] == "highway_2"
    m = load_nextgen(tmp_path, verbose=False)
    assert len(m) == 2 and m["rcv_time"].iloc[0] == pytest.approx(1.0)
    assert isinstance(m, pd.DataFrame) and m["attacker"].sum() == 2


def test_temperature_scaling_recovers_known_temperature():
    from ravenx.calibration import fit_temperature, probs
    rng = np.random.default_rng(0)
    # true logit margin m; labels drawn from sigmoid(m); model reports 3 * m
    m = rng.normal(0, 2, 20000)
    y = (rng.random(20000) < 1 / (1 + np.exp(-m))).astype(int)
    z = np.stack([np.zeros_like(m), 3 * m], axis=1)   # overconfident by 3x
    T = fit_temperature(z, y, "softmax")
    assert abs(T - 3.0) < 0.15
    p, _ = probs(z, T, "softmax")
    assert ece(y, p) < ece(y, probs(z, 1.0, "softmax")[0])


# ---------------------------------------------------------------------------
# RS-WeightedTrim (capped-simplex weights + weighted trimmed mean)
# ---------------------------------------------------------------------------

def _guide_projection(raw_scores, kappa):
    """Line-by-line port of the reference code in the SVoI/RS-WeightedTrim guide."""
    n = len(raw_scores)
    cap = kappa / n
    W = raw_scores / raw_scores.sum()
    uncapped = set(range(n))
    while True:
        over = [i for i in uncapped if W[i] > cap]
        if not over:
            break
        excess = sum(W[i] - cap for i in over)
        for i in over:
            W[i] = cap
            uncapped.discard(i)
        if uncapped:
            total_uncapped = sum(W[i] for i in uncapped)
            for i in uncapped:
                W[i] += excess * (W[i] / total_uncapped)
    return W


def _guide_aggregate(client_params, W, beta_trim):
    n = len(client_params)
    trim_k = int(np.ceil(beta_trim * n))
    out = np.zeros(client_params.shape[1])
    for j in range(client_params.shape[1]):
        col = client_params[:, j]
        order = np.argsort(col, kind="stable")
        surv = order[trim_k:n - trim_k]
        w = W[surv] / W[surv].sum()
        out[j] = np.dot(w, col[surv])
    return out


def test_capped_simplex_projection_cap_and_sum():
    from ravenx.federated import capped_simplex_projection
    rng = np.random.default_rng(0)
    for trial in range(300):
        n = int(rng.integers(3, 40))
        kappa = float(rng.choice([1.0, 1.5, 2.0, 3.0]))
        raw = rng.lognormal(0, 2, n)                  # heavy-tailed: some huge scores
        W = capped_simplex_projection(raw, kappa)
        assert abs(W.sum() - 1) < 1e-9
        assert W.max() <= kappa / n + 1e-12
        assert np.allclose(W, _guide_projection(raw.copy(), kappa), atol=1e-12)
    # kappa = 1 forces exactly equal weights
    assert np.allclose(capped_simplex_projection(np.array([100., 1, 1, 1]), 1.0), 0.25)
    # uncapped RSUs keep their relative proportions
    W = capped_simplex_projection(np.array([100., 1, 2, 3, 4]), 2.0)
    assert np.isclose(W[0], 0.4) and np.allclose(W[1:] / W[1], [1, 2, 3, 4])
    # zero-score RSUs: weights still valid (guide's loop would divide by zero)
    W = capped_simplex_projection(np.array([5., 5, 0, 0, 0, 0, 0, 0, 0, 0]), 1.0)
    assert abs(W.sum() - 1) < 1e-9 and W.max() <= 0.1 + 1e-12


def test_weighted_trimmed_mean_matches_guide_and_trims_outlier():
    from ravenx.federated import capped_simplex_projection, weighted_trimmed_mean
    rng = np.random.default_rng(1)
    U = rng.normal(0, 1, (20, 50))
    W = capped_simplex_projection(rng.uniform(0.1, 5, 20), 2.0)
    assert np.allclose(weighted_trimmed_mean(U, W, 0.2), _guide_aggregate(U, W, 0.2))
    # one wildly extreme RSU with the largest weight is trimmed out entirely
    honest = rng.normal(1.0, 0.1, (19, 30))
    U = np.vstack([honest, np.full((1, 30), 1e6)])
    W = capped_simplex_projection(np.r_[np.ones(19), 1000.0], 2.0)
    out = weighted_trimmed_mean(U, W, 0.2)
    assert np.all(np.abs(out - 1.0) < 0.2)
    # renormalisation is over survivors only: with equal weights it is the
    # ordinary trimmed mean, not a mean shrunk by the trimmed share
    U = rng.normal(3.0, 1.0, (10, 5))
    k = 2
    ref = np.sort(U, axis=0)[k:10 - k].mean(axis=0)
    assert np.allclose(weighted_trimmed_mean(U, np.full(10, 0.1), 0.2), ref)


def test_rs_weightedtrim_resists_poisoned_updates():
    from ravenx.federated import RSWeightedTrim
    rng = np.random.default_rng(2)
    honest = rng.normal(1.0, 0.1, (16, 40))
    bad = -20 * np.ones((4, 40))                     # 4 of 20 malicious (f/n = 0.2)
    U = np.vstack([honest, bad]); w = np.ones(20)
    agg = RSWeightedTrim(20, kappa=2.0, beta_trim=0.2)
    for _ in range(3):
        out = agg(U, w)
    assert out.mean() > 0.8
    assert all(W.max() <= 2.0 / 20 + 1e-12 for W in agg.weights)


# ---------------------------------------------------------------------------
# SVoI controller
# ---------------------------------------------------------------------------

def _small_svoi(seed=0, n_p=6, n_u=2):
    from ravenx import svoi
    rng = np.random.default_rng(seed)
    # two-humped like real detector beliefs: mostly near 0, a fifth near 1
    p = np.where(rng.random(4000) < 0.8, rng.beta(0.5, 8, 4000), rng.beta(8, 0.5, 4000))
    u = rng.uniform(0.02, 0.3, 4000)
    grid = svoi.BeliefGrid.fit(p, u, n_p, n_u)
    stream = np.repeat(np.arange(400), 10)
    P = {"a1": svoi.passive_transitions(grid, p, u, stream, n_min=5)[0]}
    for a, r in svoi.DEFAULT_RHO.items():
        P[a] = svoi.check_transitions(grid, r)
    return svoi, grid, P


def test_svoi_transition_rows_sum_to_one():
    svoi, grid, P = _small_svoi()
    for M in P.values():
        assert np.allclose(M.sum(1), 1.0) and (M >= 0).all()


def test_svoi_solution_matches_bruteforce_expectimax():
    svoi, grid, P = _small_svoi()
    cost = svoi.DEFAULT_COST
    pol = svoi.solve(grid, P, cost, H_max=3, C_FA=100, C_FR=20)
    for h in (1, 2, 3):
        for s in range(grid.n_states):
            assert np.isclose(pol.V[h, s], svoi.expectimax(grid, P, cost, h, s, 100, 20))


def test_svoi_one_step_rule_corollary():
    svoi, grid, P = _small_svoi()
    cost = svoi.DEFAULT_COST
    pol = svoi.solve(grid, P, cost, H_max=1, C_FA=100, C_FR=20)
    acc, rej = svoi.stop_costs(grid.p_value, 100, 20)
    c_stop = np.minimum(acc, rej)
    one_step = np.min(np.vstack([c_stop] + [cost[a] + P[a] @ c_stop for a in P]), axis=0)
    assert np.allclose(pol.V[1], one_step)


def test_svoi_cost_scale_matters():
    """With C_FA=5, C_FR=1 the stopping cost never exceeds 5/6 < Cost(a1) = 1,
    so evidence is never bought; with C_FA=100, C_FR=20 it is bought near the
    decision boundary p = C_FR / (C_FA + C_FR)."""
    svoi, grid, P = _small_svoi()
    small = svoi.solve(grid, P, svoi.DEFAULT_COST, H_max=3, C_FA=5, C_FR=1)
    assert all(small.actions[i] in ("accept", "reject") for i in np.unique(small.action))
    big = svoi.solve(grid, P, svoi.DEFAULT_COST, H_max=3, C_FA=100, C_FR=20)
    chosen = {big.actions[i] for i in np.unique(big.action[3])}
    assert chosen & set(svoi.EVIDENCE)
    # far from the boundary the policy stops
    assert big.decide(0.001, 0.05, 3) == "accept" and big.decide(0.999, 0.05, 3) == "reject"
