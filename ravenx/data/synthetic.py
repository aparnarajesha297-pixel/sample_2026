"""Synthetic V2X message logs in the VeReMi NextGen schema.

This exists so the whole RAVEN-X pipeline can be developed and tested without
the 36 GB NextGen archive. It is NOT a substitute for the real dataset and any
number produced on it must not be reported as a result.

What it imitates from NextGen:
  * urban (grid) and highway roads, low and high traffic density,
  * normal / cautious / aggressive driver profiles,
  * 1 Hz CAMs logged per receiving vehicle, with sensor noise and packet loss,
  * 20 % attacker vehicles, the 15 NextGen attack types injected post hoc on a
    shared base mobility trace (as NextGen's attackGenerator does),
  * per-message ``attacker`` label = 1 only when the message deviates
    significantly from the truth or is fabricated,
  * train/val from one region split by time (50/10), test from a separate
    region (40), so train and test never share a map or a trajectory.
"""

from __future__ import annotations

import zlib

import numpy as np
import pandas as pd

from ..config import ATTACKS

DT = 0.1            # mobility step (s)
BEACON_STEPS = 10   # 1 Hz CAMs
LANE = 3.5

_PROFILES = np.array(["Normal", "Cautious", "Aggressive"])
_PROFILE_P = [0.6, 0.2, 0.2]
# cruise-speed multiplier, max accel, max decel, accel noise
_PROFILE_PARAMS = {
    "Normal": (1.00, 2.5, -4.0, 0.25),
    "Cautious": (0.85, 1.5, -3.0, 0.15),
    "Aggressive": (1.15, 3.5, -6.0, 0.45),
}
# Headings follow NextGen / SUMO: compass degrees, 0 = north (+y), clockwise.
_DIRS = np.array([[1.0, 0.0], [0.0, 1.0], [-1.0, 0.0], [0.0, -1.0]])


# ---------------------------------------------------------------------------
# Mobility
# ---------------------------------------------------------------------------

def _profile_arrays(profiles):
    p = np.array([_PROFILE_PARAMS[x] for x in profiles])
    return p[:, 0], p[:, 1], p[:, 2], p[:, 3]


def _simulate_highway(n, duration, rng, lanes=3):
    steps = int(round(duration / DT))
    length = 9000.0
    profiles = rng.choice(_PROFILES, size=n, p=_PROFILE_P)
    mult, amax, amin, anoise = _profile_arrays(profiles)
    direction = rng.choice([1.0, -1.0], size=n)
    lane = rng.integers(0, lanes, size=n)
    y = direction * (LANE / 2 + lane * LANE)
    x = np.where(direction > 0, rng.uniform(0, 2500, n), length - rng.uniform(0, 2500, n))
    cruise = rng.normal(30.0, 2.0, n) * mult
    v = cruise * rng.uniform(0.9, 1.05, n)
    slow_until = np.zeros(n)

    P = np.zeros((steps, n, 2)); V = np.zeros((steps, n)); A = np.zeros((steps, n)); H = np.zeros((steps, n))
    for k in range(steps):
        t = k * DT
        # occasional slow-downs (congestion waves)
        start = (rng.random(n) < 0.002) & (slow_until < t)
        slow_until[start] = t + rng.uniform(5, 15, start.sum())
        target = np.where(slow_until > t, 0.5 * cruise, cruise)
        a = np.clip(0.4 * (target - v) + rng.normal(0, anoise), amin, amax)
        v = np.maximum(v + a * DT, 0.0)
        x = x + direction * v * DT
        P[k, :, 0] = x; P[k, :, 1] = y; V[k] = v; A[k] = a
        H[k] = np.where(direction > 0, 90.0, 270.0)   # compass: +x = east = 90
    return P, V, A, H, profiles


def _simulate_urban(n, duration, rng, block=200.0, grid=5):
    steps = int(round(duration / DT))
    profiles = rng.choice(_PROFILES, size=n, p=_PROFILE_P)
    mult, amax, amin, anoise = _profile_arrays(profiles)
    cruise = rng.normal(12.0, 1.5, n) * mult

    ix = rng.integers(0, grid + 1, n); iy = rng.integers(0, grid + 1, n)
    d = np.array([_valid_dir(ix[i], iy[i], rng.integers(0, 4), grid, rng) for i in range(n)])
    dist = rng.uniform(1, block, n)          # distance left to next intersection
    v = cruise * rng.uniform(0.5, 1.0, n)
    will_stop = rng.random(n) < 0.35
    stop_timer = np.zeros(n)

    P = np.zeros((steps, n, 2)); V = np.zeros((steps, n)); A = np.zeros((steps, n)); H = np.zeros((steps, n))
    for k in range(steps):
        brake_target = np.sqrt(2 * 2.0 * np.maximum(dist - 1.0, 0.0))
        target = np.where(will_stop, np.minimum(cruise, brake_target), cruise)
        waiting = stop_timer > 0
        target[waiting] = 0.0
        a = np.clip(0.8 * (target - v) + rng.normal(0, anoise), amin, amax)
        v_new = np.maximum(v + a * DT, 0.0)
        a = (v_new - v) / DT
        v = v_new
        v[waiting] = 0.0; a[waiting] = 0.0
        stop_timer[waiting] -= DT

        dist = dist - v * DT
        # vehicles that stopped at the line start waiting
        arrived_stop = will_stop & (dist < 1.5) & (v < 0.3) & ~waiting
        stop_timer[arrived_stop] = rng.uniform(3, 12, arrived_stop.sum())
        will_stop[arrived_stop] = False
        # vehicles crossing an intersection pick a new direction
        crossed = np.where(dist <= 0)[0]
        for i in crossed:
            ix[i] += int(_DIRS[d[i], 0]); iy[i] += int(_DIRS[d[i], 1])
            turn = rng.choice([0, 1, 3], p=[0.6, 0.2, 0.2])   # straight / left / right
            d[i] = _valid_dir(ix[i], iy[i], (d[i] + turn) % 4, grid, rng)
            dist[i] += block
            will_stop[i] = rng.random() < 0.35

        u = _DIRS[d]
        along = block - dist
        right = np.stack([u[:, 1], -u[:, 0]], axis=1) * (LANE / 2)
        P[k] = np.stack([ix * block, iy * block], axis=1) + u * along[:, None] + right
        V[k] = v; A[k] = a
        H[k] = np.degrees(np.arctan2(u[:, 0], u[:, 1])) % 360.0   # compass, like NextGen
    return P, V, A, H, profiles


def _valid_dir(ix, iy, d, grid, rng):
    for cand in [d, (d + 1) % 4, (d + 3) % 4, (d + 2) % 4]:
        nx, ny = ix + _DIRS[cand, 0], iy + _DIRS[cand, 1]
        if 0 <= nx <= grid and 0 <= ny <= grid:
            return cand
    return d


def simulate_mobility(road, density, duration, seed, region=0):
    """Ground-truth trajectories. ``region`` changes the map (test region)."""
    rng = np.random.default_rng(seed)
    if road == "highway":
        n = {"low": 30, "high": 80}[density]
        return _simulate_highway(n, duration, rng, lanes=3 if region == 0 else 4)
    n = {"low": 30, "high": 80}[density]
    return _simulate_urban(n, duration, rng, block=200.0 if region == 0 else 160.0,
                           grid=5 if region == 0 else 6)


# ---------------------------------------------------------------------------
# Messages and attacks
# ---------------------------------------------------------------------------

def _honest_messages(P, V, A, H, rng, noise):
    steps, n = V.shape
    phase = rng.integers(0, BEACON_STEPS, n)
    rows = []
    for vid in range(n):
        ks = np.arange(phase[vid], steps, BEACON_STEPS)
        rows.append(pd.DataFrame({"vid": vid, "k": ks}))
    m = pd.concat(rows, ignore_index=True)
    k, vid = m["k"].values, m["vid"].values
    m["tx_x"] = P[k, vid, 0]; m["tx_y"] = P[k, vid, 1]
    m["x"] = m["tx_x"] + rng.normal(0, noise["pos"], len(m))
    m["y"] = m["tx_y"] + rng.normal(0, noise["pos"], len(m))
    m["spd"] = np.maximum(V[k, vid] + rng.normal(0, noise["spd"], len(m)), 0)
    m["acl"] = A[k, vid] + rng.normal(0, noise["acl"], len(m))
    m["hed"] = (H[k, vid] + rng.normal(0, noise["hed"], len(m))) % 360
    m["send_time"] = k * DT
    m["fabricated"] = False
    return m


def _state(P, V, A, H, k, vid, rng, noise):
    k = np.clip(k, 0, V.shape[0] - 1)
    return (P[k, vid, 0] + rng.normal(0, noise["pos"], np.size(k)),
            P[k, vid, 1] + rng.normal(0, noise["pos"], np.size(k)),
            np.maximum(V[k, vid] + rng.normal(0, noise["spd"], np.size(k)), 0),
            (H[k, vid] + rng.normal(0, noise["hed"], np.size(k))) % 360,
            A[k, vid] + rng.normal(0, noise["acl"], np.size(k)))


def _inject(m, attack, attackers, P, V, A, H, rng, noise, road):
    """Apply ``attack`` to the messages of ``attackers``. Returns new table."""
    steps = V.shape[0]
    extra = []
    for vid in attackers:
        idx = np.where(m["vid"].values == vid)[0]
        if len(idx) == 0:
            continue
        ks = m["k"].values[idx]
        onset = int(rng.uniform(0.1, 0.6) * steps)
        after = ks >= onset
        sl = m.index[idx]

        if attack == "constantPositionOffset":
            off = rng.uniform(20, 80, 2) * rng.choice([-1, 1], 2)
            m.loc[sl, "x"] += off[0]; m.loc[sl, "y"] += off[1]
        elif attack == "randomPositionOffset":
            m.loc[sl, "x"] += rng.uniform(-80, 80, len(idx))
            m.loc[sl, "y"] += rng.uniform(-80, 80, len(idx))
        elif attack == "positionMirroring":
            if road == "highway":
                m.loc[sl, "y"] = -m.loc[sl, "y"]
            else:
                # mirror onto the opposite lane of the same street
                h = np.radians(H[ks, vid])
                # compass heading: travel = (sin h, cos h), left = (-cos h, sin h)
                m.loc[sl, "x"] += -np.cos(h) * LANE * 2
                m.loc[sl, "y"] += np.sin(h) * LANE * 2
        elif attack == "constantSpeedOffset":
            m.loc[sl, "spd"] = np.maximum(m.loc[sl, "spd"] + rng.choice([-1, 1]) * rng.uniform(5, 12), 0)
        elif attack == "randomSpeedOffset":
            m.loc[sl, "spd"] = np.maximum(m.loc[sl, "spd"] + rng.uniform(-12, 12, len(idx)), 0)
        elif attack == "zeroSpeedReport":
            m.loc[sl, "spd"] = 0.0
        elif attack == "suddenConstantSpeed":
            frozen = V[onset, vid]
            m.loc[sl[after], "spd"] = frozen
        elif attack == "reversedHeading":
            m.loc[sl, "hed"] = (m.loc[sl, "hed"] + 180) % 360
        elif attack == "feignedBraking":
            burst = after & (rng.random(len(idx)) < 0.5)
            m.loc[sl[burst], "acl"] = rng.uniform(-9, -5, burst.sum())
        elif attack == "accelerationMultiplication":
            m.loc[sl, "acl"] = m.loc[sl, "acl"] * rng.uniform(3, 6)
        elif attack == "suddenStop":
            k0 = onset
            m.loc[sl[after], "x"] = P[k0, vid, 0] + rng.normal(0, noise["pos"], after.sum())
            m.loc[sl[after], "y"] = P[k0, vid, 1] + rng.normal(0, noise["pos"], after.sum())
            m.loc[sl[after], "spd"] = 0.0
            first = after & (ks < k0 + 2 * BEACON_STEPS)
            m.loc[sl[after], "acl"] = 0.0
            m.loc[sl[first], "acl"] = -8.0
        elif attack == "timeDelayAttack":
            delay = int(rng.uniform(1, 5) / DT)
            x, y, s, h, a = _state(P, V, A, H, ks - delay, vid, rng, noise)
            m.loc[sl, ["x", "y", "spd", "hed", "acl"]] = np.stack([x, y, s, h, a], 1)
            m.loc[sl, "send_time"] = np.maximum(ks - delay, 0) * DT
        elif attack == "dataReplay":
            d = np.linalg.norm(P[ks[0]] - P[ks[0], vid], axis=1)
            d[vid] = np.inf
            victim = int(np.argmin(d))
            x, y, s, h, a = _state(P, V, A, H, ks - 20, victim, rng, noise)
            m.loc[sl, ["x", "y", "spd", "hed", "acl"]] = np.stack([x, y, s, h, a], 1)
        elif attack == "dosAttack":
            kk = np.concatenate([np.arange(k + 1, min(k + BEACON_STEPS, steps)) for k in ks])
            x, y, s, h, a = _state(P, V, A, H, kk, vid, rng, noise)
            extra.append(pd.DataFrame({
                "vid": vid, "k": kk, "tx_x": P[kk, vid, 0], "tx_y": P[kk, vid, 1],
                "x": x, "y": y, "spd": s, "acl": a, "hed": h, "send_time": kk * DT,
                "fabricated": True}))
            m.loc[sl, "fabricated"] = True
        elif attack == "trafficCongestionSybil":
            for g in range(int(rng.integers(3, 6))):
                kk = ks[after]
                if len(kk) == 0:
                    continue
                h = np.radians(H[onset, vid])
                u = np.array([np.sin(h), np.cos(h)])
                gap = 8.0 * (g + 1)
                drift = 1.5 * (kk - onset) * DT
                gx = P[onset, vid, 0] + u[0] * (gap + drift) + rng.normal(0, noise["pos"], len(kk))
                gy = P[onset, vid, 1] + u[1] * (gap + drift) + rng.normal(0, noise["pos"], len(kk))
                extra.append(pd.DataFrame({
                    "vid": vid, "k": kk, "tx_x": P[kk, vid, 0], "tx_y": P[kk, vid, 1],
                    "x": gx, "y": gy, "spd": np.abs(rng.normal(1.5, 0.3, len(kk))),
                    "acl": rng.normal(0, 0.2, len(kk)), "hed": np.full(len(kk), H[onset, vid]),
                    "send_time": kk * DT, "fabricated": True, "ghost": g + 1}))
        else:
            raise ValueError(f"Unknown attack {attack}")
    if extra:
        m = pd.concat([m] + extra, ignore_index=True)
    return m


def _label(m, P, V, A, H):
    """attacker = 1 for a significant deviation from the truth or a fake message."""
    k, vid = m["k"].values, m["vid"].values
    dpos = np.hypot(m["x"].values - P[k, vid, 0], m["y"].values - P[k, vid, 1])
    dspd = np.abs(m["spd"].values - V[k, vid])
    dhed = np.abs((m["hed"].values - H[k, vid] + 180) % 360 - 180)
    dacl = np.abs(m["acl"].values - A[k, vid])
    dtime = np.abs(m["send_time"].values - k * DT)
    sig = (dpos > 5) | (dspd > 2) | (dhed > 20) | (dacl > 2) | (dtime > 0.2)
    return (sig | m["fabricated"].values).astype(int)


def road_edge_distance(road, region, x, y):
    """Signed distance (m) from a reported position to the nearest road edge,
    positive on the road, negative off it. Mirrors NextGen's
    ``distance_to_road_edge`` for the synthetic road layouts."""
    if road == "highway":
        lanes = 3 if region == 0 else 4
        return lanes * LANE - np.abs(y)
    block, grid = (200.0, 5) if region == 0 else (160.0, 6)
    dx = np.abs(x - np.clip(np.round(x / block), 0, grid) * block)
    dy = np.abs(y - np.clip(np.round(y / block), 0, grid) * block)
    return LANE - np.minimum(dx, dy)


def _receive(m, P, V, H, observers, rng, comm_range, loss):
    out = []
    for obs in observers:
        rx = P[m["k"].values, obs]
        d = np.hypot(m["tx_x"].values - rx[:, 0], m["tx_y"].values - rx[:, 1])
        ok = (d < comm_range) & (m["vid"].values != obs) & (rng.random(len(m)) > loss)
        r = m[ok].copy()
        r["receiver_vid"] = obs
        r["rx_x"] = rx[ok, 0]
        r["rx_y"] = rx[ok, 1]
        r["rx_spd"] = V[r["k"].values, obs]
        r["rx_hed"] = H[r["k"].values, obs]
        r["rcv_time"] = r["k"] * DT + rng.uniform(0.0005, 0.003, len(r))
        out.append(r)
    return pd.concat(out, ignore_index=True)


def generate_subset(road, density, attack, split_region, duration, seed,
                    mobility=None, n_observers=8, attacker_frac=0.2,
                    comm_range=300.0, loss=0.05):
    """One (scenario, attack, region) log, receivers x received CAMs."""
    rng = np.random.default_rng(seed)
    P, V, A, H, profiles = mobility
    n = V.shape[1]
    noise = {"pos": 1.5, "spd": 0.2, "acl": 0.15, "hed": 1.5}

    m = _honest_messages(P, V, A, H, rng, noise)
    m["ghost"] = 0
    perm = rng.permutation(n)
    n_att = max(1, int(round(attacker_frac * n)))
    attackers = perm[:n_att]
    observers = perm[n_att:n_att + n_observers]
    if attack is not None:
        m = _inject(m, attack, attackers, P, V, A, H, rng, noise, road)
    m["attacker"] = _label(m, P, V, A, H) if attack is not None else 0
    m["attacker"] = m["attacker"] * np.isin(m["vid"].values, attackers)
    m["ghost"] = m["ghost"].fillna(0).astype(int)

    # pseudonyms: each vehicle (and each Sybil ghost) has its own alias
    alias_base = rng.permutation(10_000)[: n * 8].reshape(n, 8)
    m["alias"] = alias_base[m["vid"].values, m["ghost"].values].astype(str)
    m["sender_id"] = m["vid"].astype(str)
    m["profile"] = profiles[m["vid"].values]
    m = m.sort_values(["k", "vid"]).reset_index(drop=True)
    m["msg_id"] = np.arange(len(m))

    m["road_edge"] = road_edge_distance(road, split_region, m["x"].values, m["y"].values)
    r = _receive(m, P, V, H, observers, rng, comm_range, loss)
    return r


def generate_dataset(roads=("urban", "highway"), densities=("low", "high"),
                     attacks=None, duration=60.0, n_observers=8, seed=0,
                     verbose=True) -> pd.DataFrame:
    """Train/val/test message table covering every (scenario, attack) subset."""
    attacks = list(attacks) if attacks else list(ATTACKS)
    frames = []
    for road in roads:
        for density in densities:
            scen = f"{road}_{density}"
            base_seed = seed * 1000 + zlib.crc32(scen.encode()) % 997
            mob_a = simulate_mobility(road, density, duration, base_seed, region=0)
            mob_b = simulate_mobility(road, density, duration, base_seed + 1, region=1)
            for ai, attack in enumerate(attacks):
                for region, mob in ((0, mob_a), (1, mob_b)):
                    r = generate_subset(road, density, attack, region, duration,
                                        seed=base_seed * 31 + ai * 7 + region,
                                        mobility=mob, n_observers=n_observers)
                    if region == 0:
                        cut = duration * 5 / 6         # 50 % train / 10 % val
                        r["split"] = np.where(r["k"] * DT < cut, "train", "val")
                    else:
                        r["split"] = "test"
                    r["scenario"] = scen; r["road"] = road; r["density"] = density
                    r["attack_type"] = attack
                    r["run"] = scen + "/" + attack + "/" + r["split"]
                    r["receiver"] = r["run"] + "/rx" + r["receiver_vid"].astype(str)
                    frames.append(r)
            if verbose:
                print(f"  generated {scen}: {len(attacks)} attack subsets")
    msgs = pd.concat(frames, ignore_index=True)
    cols = ["run", "split", "scenario", "road", "density", "attack_type", "receiver",
            "rcv_time", "send_time", "sender_id", "alias", "msg_id", "attacker",
            "x", "y", "spd", "hed", "acl", "profile", "rx_x", "rx_y", "road_edge", "rx_spd", "rx_hed"]
    return msgs[cols]
