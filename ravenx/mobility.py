"""Runtime mobility signals for the SVoI controller (rows 15 and 16).

Row 15, planning horizon. The controller should look further ahead for a
vehicle that stays observable for a while and decide sooner for one about to
disappear. The dataset has no "left radio range" event, so the target is the
time left in the vehicle's current stream (same receiver, same pseudonym).
That target is only known afterwards, so at runtime it is estimated from what
has been seen so far:

  constant    a quantile q of the time left on validation
  age         the same quantile given how many steps of the stream have
              been seen already
  geometric   time until the sender passes the range R at its current
              receding speed (R = 99th percentile of receiver distance on
              validation); for a sender that is not receding, the age estimate

q = 0.5 (the median) is the natural point estimate, but a cap that is too
short forces a decision before any evidence is gathered while one that is too
long costs nothing (the replay stops at the stream's end anyway), so higher q
and a minimum cap are also tried; the choice is made on validation.

The true time left is also reported, as an oracle upper bound only: on this
data it leaks the label (almost every one-message stream is a Sybil ghost).

Row 16, criticality. The CAMs carry no event flag, so a step is "critical"
when the sender is close and closing in: distance to the receiver below
d_max and time to collision (distance / closing speed) below ttc_max. The
closing speed comes from consecutive steps of the same stream. Positions are
the sender's claims, so an attacker can shape both signals; that is a
limitation of any flag built from CAM content.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from .config import BIN_SECONDS

MAX_S = 120.0          # longest time-left estimate used, in seconds
AGE_CAP = 30           # ages >= this share one bucket


def range_rate(steps: pd.DataFrame) -> np.ndarray:
    """d/dt of the receiver-sender distance within a stream (m/s, NaN on a
    stream's first step). Positive = moving apart."""
    g = steps.groupby("stream", sort=False)
    return (g["DistanceToReceiver"].diff() / g["rcv_time"].diff()).to_numpy()


def time_left(steps: pd.DataFrame) -> np.ndarray:
    """Seconds from each step to the last step of its stream (the target)."""
    return (steps.groupby("stream", sort=False)["rcv_time"].transform("max") - steps["rcv_time"]).to_numpy()


def steps_left(steps: pd.DataFrame) -> np.ndarray:
    """Number of later steps in the same stream."""
    return steps.groupby("stream", sort=False).cumcount(ascending=False).to_numpy()


@dataclass
class HorizonProxy:
    R: float = 0.0
    constant: float = 0.0
    by_age: np.ndarray = field(default=None)
    min_rate: float = 0.5          # m/s; slower than this counts as not receding
    q: float = 0.5

    @classmethod
    def fit(cls, steps: pd.DataFrame, q: float = 0.5) -> "HorizonProxy":
        left = np.minimum(time_left(steps), MAX_S)
        age = np.minimum(steps["pos_in_stream"].to_numpy(), AGE_CAP)
        by_age = pd.Series(left).groupby(age).quantile(q).reindex(range(AGE_CAP + 1))
        by_age = by_age.ffill().bfill().to_numpy()
        return cls(R=float(steps["DistanceToReceiver"].quantile(0.99)),
                   constant=float(np.quantile(left, q)), by_age=by_age, q=q)

    def predict(self, steps: pd.DataFrame) -> dict:
        age = np.minimum(steps["pos_in_stream"].to_numpy(), AGE_CAP)
        est_age = self.by_age[age]
        rate = range_rate(steps)
        d = steps["DistanceToReceiver"].to_numpy()
        receding = np.nan_to_num(rate, nan=0.0) > self.min_rate
        exit_s = np.clip(self.R - d, 0, None) / np.where(receding, rate, 1.0)
        geo = np.where(receding, np.minimum(exit_s, MAX_S), est_age)
        return {"constant": np.full(len(steps), self.constant), "age": est_age, "geometric": geo}


def horizon_cap(seconds: np.ndarray, min_cap: int = 0) -> np.ndarray:
    """Time-left estimate (s) -> number of further steps to plan for."""
    return np.maximum(np.floor(np.asarray(seconds) / BIN_SECONDS).astype(np.int64), min_cap)


def critical(steps: pd.DataFrame, d_max: float = 100.0, ttc_max: float = 10.0,
             min_rate: float = 0.5) -> np.ndarray:
    """True where the sender is within d_max and would reach the receiver in
    under ttc_max seconds at the current closing speed."""
    rate = np.nan_to_num(range_rate(steps), nan=0.0)
    d = steps["DistanceToReceiver"].to_numpy()
    closing = rate < -min_rate
    ttc = np.where(closing, d / np.where(closing, -rate, 1.0), np.inf)
    return (d < d_max) & (ttc < ttc_max)
