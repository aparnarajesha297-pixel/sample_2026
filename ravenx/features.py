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


def message_features(msgs: pd.DataFrame) -> pd.DataFrame:
    """Per-message derived features computed against the previous message
    of the same stream (plan 3.1 - 3.7)."""
    m = msgs.sort_values(["receiver", "alias", "rcv_time"], kind="mergesort").reset_index(drop=True)
    grp = m.groupby(["receiver", "alias"], sort=False)
    prev = grp[["x", "y", "spd", "hed", "acl", "send_time", "rcv_time"]].shift(1)
    first = prev["rcv_time"].isna().values

    dx = m["x"] - prev["x"]
    dy = m["y"] - prev["y"]
    dt_send = m["send_time"] - prev["send_time"]
    dt_rcv = m["rcv_time"] - prev["rcv_time"]
    dt = dt_send.where(dt_send > 0.05, dt_rcv).clip(lower=0.05)

    m["PositionChange"] = np.hypot(dx, dy)                              # 3.1
    m["SpeedChange"] = m["spd"] - prev["spd"]                           # 3.2
    m["AccelError"] = (m["SpeedChange"] / dt - (m["acl"] + prev["acl"]) / 2).abs()  # 3.3
    m["HeadingChange"] = _wrap_deg(m["hed"] - prev["hed"])              # 3.4
    # claimed heading vs the direction the claimed positions actually move
    # (compass bearing, 0 = north, clockwise, as in NextGen). A constantly
    # reversed heading never *changes*, but it points against the motion.
    bearing = np.degrees(np.arctan2(dx, dy)) % 360.0
    moving = m["PositionChange"].values > 1.0
    m["HeadingMotionError"] = np.where(moving, np.abs(_wrap_deg(m["hed"] - bearing)), 0.0)
    m["MessageGap"] = dt_rcv                                            # 3.5
    m["PositionSpeed"] = m["PositionChange"] / dt                       # 3.6
    m["SpeedError"] = (m["PositionSpeed"] - (m["spd"] + prev["spd"]) / 2).abs()  # 3.7
    m["TimeLag"] = m["rcv_time"] - m["send_time"]
    # map / geometry plausibility (plan 3.x extension): how far the claimed
    # position is from the road, and from the receiver itself
    m["RoadEdgeDist"] = m["road_edge"] if "road_edge" in m else 0.0
    if {"rx_x", "rx_y"} <= set(m.columns):
        m["ClaimedDistance"] = np.hypot(m["x"] - m["rx_x"], m["y"] - m["rx_y"])
    else:
        m["ClaimedDistance"] = 0.0
    m["Speed"] = m["spd"]
    m["Heading"] = m["hed"]
    m["Acceleration"] = m["acl"]

    for c in ["PositionChange", "SpeedChange", "AccelError", "HeadingChange",
              "PositionSpeed", "SpeedError", "HeadingMotionError"]:
        m.loc[first, c] = 0.0
    m.loc[first, "MessageGap"] = -1.0   # "no previous message" marker
    return m


def build_steps(msgs: pd.DataFrame, bin_s: float = BIN_SECONDS) -> pd.DataFrame:
    """Collapse messages to (receiver, alias, bin) steps, sorted by stream/time."""
    m = message_features(msgs)
    m["bin"] = np.floor(m["rcv_time"] / bin_s).astype(np.int64)
    key = ["receiver", "alias", "bin"]
    counts = m.groupby(key, sort=False).size().rename("MsgCount")
    last = m.groupby(key, sort=False).tail(1).set_index(key)
    steps = last.join(counts).reset_index()
    steps = steps.sort_values(["receiver", "alias", "bin"], kind="mergesort").reset_index(drop=True)
    steps["label"] = steps["attacker"].astype(np.int64)
    steps["stream"] = steps.groupby(["receiver", "alias"], sort=False).ngroup()
    steps["pos_in_stream"] = steps.groupby("stream").cumcount()
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
