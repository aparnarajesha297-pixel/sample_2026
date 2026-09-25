"""Feature engineering (plan phase 3) and observation steps.

Messages are processed per *stream*: the sequence of messages one receiver got
from one pseudonym (receiver, sender_alias). That is the information a real
receiver has; the true sender identity is never used.

A *step* is one stream observed in one time bin (``bin_s`` seconds). It is the
unit every model classifies: RF/XGBoost look at one step, the GRU at the last
T steps of the stream, the GAT at the step plus the other streams the same
receiver heard in that bin, and RAVEN-X at both. With 1 Hz CAMs a step is
normally exactly one message; for flooding (DoS) the step keeps the last
message and records how many arrived (MsgCount).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .config import BIN_SECONDS, FEATURES


def _wrap_deg(d):
    return (d + 180.0) % 360.0 - 180.0


# columns carried from the message table into the steps (everything else is
# dropped before the sort, which keeps memory flat on multi-million-row data)
_KEEP = ["run", "split", "scenario", "road", "density", "attack_type", "receiver", "alias",
         "rcv_time", "send_time", "x", "y", "spd", "hed", "acl", "attacker",
         "road_edge", "rx_x", "rx_y", "rx_spd", "rx_hed"]


def _codes(col: pd.Series) -> np.ndarray:
    return col.cat.codes.values if isinstance(col.dtype, pd.CategoricalDtype) else pd.factorize(col)[0]


def message_features(msgs: pd.DataFrame) -> pd.DataFrame:
    """Per-message derived features computed against the previous message
    of the same stream (plan 3.1 - 3.7).

    Implemented with plain arrays after a single sort: a row's "previous
    message" is the row above it when both belong to the same stream."""
    m = msgs[[c for c in _KEEP if c in msgs.columns]]
    m = m.sort_values(["receiver", "alias", "rcv_time"], kind="mergesort").reset_index(drop=True)
    rc, al = _codes(m["receiver"]), _codes(m["alias"])
    first = np.r_[True, (rc[1:] != rc[:-1]) | (al[1:] != al[:-1])]
    m["_stream"] = np.cumsum(first) - 1

    def col(name):
        return m[name].to_numpy(dtype=np.float64)

    def prev(v):
        out = np.empty_like(v)
        out[0] = np.nan
        out[1:] = v[:-1]
        out[first] = np.nan
        return out

    x, y, spd, hed, acl = col("x"), col("y"), col("spd"), col("hed"), col("acl")
    t_snd, t_rcv = col("send_time"), col("rcv_time")
    dx, dy = x - prev(x), y - prev(y)
    dt_send, dt_rcv = t_snd - prev(t_snd), t_rcv - prev(t_rcv)
    dt = np.clip(np.where(dt_send > 0.05, dt_send, dt_rcv), 0.05, None)
    p_spd, p_acl = prev(spd), prev(acl)

    f = {}
    f["PositionChange"] = np.hypot(dx, dy)                                     # 3.1
    f["SpeedChange"] = spd - p_spd                                             # 3.2
    # 3.3 acceleration consistency: speed change vs reported acceleration
    f["AccelerationInconsistency"] = np.abs(f["SpeedChange"] / dt - (acl + p_acl) / 2)
    # rate of change of the reported acceleration
    f["Jerk"] = (acl - p_acl) / dt
    f["HeadingChange"] = _wrap_deg(hed - prev(hed))                             # 3.4
    # claimed heading vs the direction the claimed positions actually move
    # (compass bearing, 0 = north, clockwise, as in NextGen). A constantly
    # reversed heading never *changes*, but it points against the motion.
    bearing = np.degrees(np.arctan2(dx, dy)) % 360.0
    moving = np.nan_to_num(f["PositionChange"]) > 1.0
    f["HeadingInconsistency"] = np.where(moving, np.abs(_wrap_deg(hed - bearing)), 0.0)
    f["MessageGap"] = np.where(first, -1.0, dt_rcv)       # 3.5, -1 = no previous message
    f["PositionSpeed"] = f["PositionChange"] / dt                              # 3.6
    # 3.7 speed consistency: position-derived speed vs reported speed
    f["SpeedInconsistency"] = np.abs(f["PositionSpeed"] - (spd + p_spd) / 2)
    f["TimeLag"] = t_rcv - t_snd
    # map / geometry plausibility: how far the claimed position is from the
    # road, and from the receiver itself
    f["RoadEdgeDist"] = col("road_edge") if "road_edge" in m else np.zeros(len(m))
    if {"rx_x", "rx_y"} <= set(m.columns):
        f["DistanceToReceiver"] = np.hypot(x - col("rx_x"), y - col("rx_y"))
    else:
        f["DistanceToReceiver"] = np.zeros(len(m))
    # sender relative to the receiving vehicle's own state
    if {"rx_spd", "rx_hed"} <= set(m.columns):
        f["RelativeSpeed"] = spd - col("rx_spd")
        f["RelativeHeading"] = np.abs(_wrap_deg(hed - col("rx_hed")))
    else:
        f["RelativeSpeed"] = np.zeros(len(m))
        f["RelativeHeading"] = np.zeros(len(m))
    f["Speed"], f["Heading"], f["Acceleration"] = spd, hed, acl

    for c in ["PositionChange", "SpeedChange", "AccelerationInconsistency", "Jerk",
              "HeadingChange", "PositionSpeed", "SpeedInconsistency", "HeadingInconsistency"]:
        f[c][first] = 0.0
    for k, v in f.items():
        m[k] = v.astype(np.float32)
    return m


def build_steps(msgs: pd.DataFrame, bin_s: float = BIN_SECONDS) -> pd.DataFrame:
    """Collapse messages to (receiver, alias, bin) steps, sorted by stream/time.
    A step keeps the stream's last message in the bin plus the message count."""
    m = message_features(msgs)
    s = m.pop("_stream").to_numpy()
    b = np.floor(m["rcv_time"].to_numpy() / bin_s).astype(np.int64)
    new_group = np.r_[True, (s[1:] != s[:-1]) | (b[1:] != b[:-1])]
    last = np.r_[new_group[1:], True]
    counts = np.bincount(np.cumsum(new_group) - 1)
    idx = np.flatnonzero(last)
    steps = m.iloc[idx].reset_index(drop=True)
    del m
    steps["bin"] = b[idx]
    steps["MsgCount"] = counts.astype(np.float32)
    steps["label"] = steps["attacker"].to_numpy().astype(np.int64)
    stream = s[idx]
    steps["stream"] = stream
    first = np.r_[True, stream[1:] != stream[:-1]]
    ar = np.arange(len(stream))
    steps["pos_in_stream"] = ar - np.maximum.accumulate(np.where(first, ar, 0))
    steps[FEATURES] = steps[FEATURES].astype(np.float32).fillna(0.0)
    return steps


def build_windows(steps: pd.DataFrame, T: int) -> np.ndarray:
    """(N, T) indices of the last T steps of each step's stream, oldest first,
    -1 = padding. Steps must be sorted by stream then time (build_steps does).
    Windows never leave a stream, and streams never cross a split because a
    stream key includes the run (scenario/attack/split)."""
    n = len(steps)
    pos = steps["pos_in_stream"].values
    idx = np.arange(n)
    win = np.full((n, T), -1, dtype=np.int64)
    for k in range(T):
        ok = pos >= k
        win[ok, T - 1 - k] = idx[ok] - k
    return win


class Normalizer:
    """Signed log1p then z-score, fitted on training steps only."""

    def fit(self, X: np.ndarray):
        Z = np.sign(X) * np.log1p(np.abs(X))
        self.mu = Z.mean(0)
        self.sd = Z.std(0) + 1e-6
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        Z = np.sign(X) * np.log1p(np.abs(X))
        return ((Z - self.mu) / self.sd).astype(np.float32)
