"""Messages -> steps -> windows + graph, shared by every experiment."""

from __future__ import annotations

import argparse
import hashlib
import json
import pickle
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .config import ATTACKS, BIN_SECONDS, FEATURES, NEIGHBOR_RADIUS, SEQ_LEN
from .features import Normalizer, build_steps, build_windows
from .graph import Graph, build_graph, graph_stats


@dataclass
class StepData:
    steps: pd.DataFrame      # one row per step, meta + FEATURES + label
    X_raw: np.ndarray        # (N, F) raw features (tree models)
    X: np.ndarray            # (N, F) normalised features (neural models)
    y: np.ndarray            # (N,) int64 labels
    win: np.ndarray          # (N, T) window indices
    graph: Graph
    group: np.ndarray        # snapshot id per step
    normalizer: Normalizer

    def idx(self, split=None, **filters) -> np.ndarray:
        m = np.ones(len(self.steps), dtype=bool)
        if split is not None:
            m &= self.steps["split"].values == split
        for col, val in filters.items():
            if val is None:
                continue
            vals = val if isinstance(val, (list, tuple, set)) else [val]
            m &= self.steps[col].isin(vals).values
        return np.where(m)[0]


def prepare(msgs: pd.DataFrame, bin_s=BIN_SECONDS, radius=NEIGHBOR_RADIUS,
            T=SEQ_LEN, fit_split="train", verbose=True) -> StepData:
    t0 = time.time()
    steps = build_steps(msgs, bin_s)
    win = build_windows(steps, T)
    # no window may reach into another split (plan phase 4 leakage check)
    split = steps["split"].values
    stream = steps["stream"].values
    valid = win >= 0
    rows = np.nonzero(valid)[0]
    assert (split[win[valid]] == split[rows]).all(), "temporal leakage across splits"
    assert (stream[win[valid]] == stream[rows]).all(), "window crosses streams"
    graph, group = build_graph(steps, radius)
    assert (split[graph.src] == split[graph.dst]).all(), "graph edge crosses splits"

    X_raw = steps[FEATURES].values.astype(np.float32)
    norm = Normalizer().fit(X_raw[split == fit_split])
    data = StepData(steps=steps, X_raw=X_raw, X=norm.transform(X_raw),
                    y=steps["label"].values.astype(np.int64), win=win,
                    graph=graph, group=group, normalizer=norm)
    if verbose:
        print(f"Prepared {len(steps):,} steps, {graph.n_edges:,} directed edges "
              f"in {time.time() - t0:.1f}s")
    return data


# ---------------------------------------------------------------------------
# Command-line data options shared by the scripts
# ---------------------------------------------------------------------------

def add_data_args(p: argparse.ArgumentParser):
    g = p.add_argument_group("data")
    g.add_argument("--data", choices=["synthetic", "nextgen"], default="synthetic",
                   help="synthetic = schema-compatible generator for pipeline testing; "
                        "nextgen = real VeReMi NextGen JSON under --root")
    g.add_argument("--root", type=str, help="VeReMi NextGen folder (for --data nextgen)")
    g.add_argument("--attacks", nargs="*", default=None,
                   help="attack subsets to use (default: all 15). Start with one, then 4, then all")
    g.add_argument("--scenarios", nargs="*", default=None,
                   help="scenario filter, e.g. urban_low highway_high (synthetic) or highway_2 (NextGen)")
    g.add_argument("--density-map", type=str, default=None,
                   help="NextGen only: scenario=density pairs, e.g. 'highway_1=low,highway_2=high'")
    g.add_argument("--max-files", type=int, default=None,
                   help="NextGen only: max receiver files per subset and split")
    g.add_argument("--duration", type=float, default=60.0, help="synthetic only: seconds simulated")
    g.add_argument("--observers", type=int, default=8, help="synthetic only: receivers logged")
    g.add_argument("--bin", type=float, default=BIN_SECONDS, help="step / snapshot length (s)")
    g.add_argument("--radius", type=float, default=NEIGHBOR_RADIUS, help="neighbour radius (m)")
    g.add_argument("--seq-len", type=int, default=SEQ_LEN, help="T, window length")
    g.add_argument("--cache", type=str, default="cache", help="cache folder ('' disables)")
    g.add_argument("--seed", type=int, default=0)
    return p


def load_messages(args) -> pd.DataFrame:
    attacks = args.attacks or list(ATTACKS)
    unknown = set(attacks) - set(ATTACKS)
    if unknown:
        raise SystemExit(f"Unknown attacks: {sorted(unknown)}. Valid: {ATTACKS}")
    if args.data == "nextgen":
        from .data.nextgen import load_nextgen
        if not args.root:
            raise SystemExit("--root is required with --data nextgen")
        dmap = None
        if args.density_map:
            dmap = dict(kv.split("=") for kv in args.density_map.split(","))
        return load_nextgen(args.root, attacks=attacks, scenarios=args.scenarios,
                            density_map=dmap, max_files_per_subset=args.max_files)
    from .data.synthetic import generate_dataset
    scen = args.scenarios or ["urban_low", "urban_high", "highway_low", "highway_high"]
    roads = sorted({s.split("_")[0] for s in scen})
    dens = sorted({s.split("_")[1] for s in scen})
    msgs = generate_dataset(roads, dens, attacks, duration=args.duration,
                            n_observers=args.observers, seed=args.seed)
    return msgs[msgs["scenario"].isin(scen)].reset_index(drop=True)


def load_data(args, verbose=True) -> tuple[pd.DataFrame, StepData]:
    """Messages + prepared steps, cached on disk by the data arguments."""
    keys = ["data", "root", "attacks", "scenarios", "density_map", "max_files",
            "duration", "observers", "bin", "radius", "seq_len", "seed"]
    sig = json.dumps({**{k: getattr(args, k) for k in keys}, "features": FEATURES},
                     sort_keys=True, default=str)
    h = hashlib.md5(sig.encode()).hexdigest()[:12]
    path = Path(args.cache) / f"data_{h}.pkl" if args.cache else None
    if path is not None and path.exists():
        if verbose:
            print(f"Loading cached data {path}")
        with open(path, "rb") as f:
            return pickle.load(f)
    msgs = load_messages(args)
    data = prepare(msgs, args.bin, args.radius, args.seq_len, verbose=verbose)
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump((msgs, data), f, protocol=pickle.HIGHEST_PROTOCOL)
    return msgs, data


def dataset_summary(msgs: pd.DataFrame, data: StepData) -> dict:
    """Checkpoint numbers from plan phases 1, 2 and 5."""
    out = {
        "messages": int(len(msgs)),
        "unique_vehicles(sender_id per run)": int(msgs.groupby("run")["sender_id"].nunique().sum()),
        "unique_pseudonyms(alias per run)": int(msgs.groupby("run")["alias"].nunique().sum()),
        "attacker_vehicles": int(msgs[msgs["attacker"] == 1].groupby("run")["sender_id"].nunique().sum()),
        "attack_messages": int((msgs["attacker"] == 1).sum()),
        "normal_messages": int((msgs["attacker"] == 0).sum()),
        "attack_percentage": float(100 * msgs["attacker"].mean()),
        "missing_values": {c: int(v) for c, v in msgs.isna().sum().items() if v},
        "steps": int(len(data.steps)),
        "per_split": {},
    }
    for s in ("train", "val", "test"):
        m = data.steps["split"] == s
        out["per_split"][s] = {"steps": int(m.sum()),
                               "attack_steps": int(data.steps.loc[m, "label"].sum())}
    gs = graph_stats(data.steps, data.graph, data.group)
    out["graph"] = {
        "snapshots": int(len(gs)),
        "mean_vehicles_per_snapshot": float(gs["vehicles"].mean()),
        "mean_edges_per_snapshot": float(gs["edges"].mean()),
        "mean_avg_neighbors": float(gs["avg_neighbors"].mean()),
        "max_neighbors": int(gs["max_neighbors"].max()),
    }
    per_attack = (msgs.groupby("attack_type")["attacker"]
                  .agg(messages="size", attack_messages="sum", attack_rate="mean"))
    out["per_attack"] = per_attack.reset_index().to_dict(orient="records")
    return out
