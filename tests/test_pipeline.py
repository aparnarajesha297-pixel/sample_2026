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
