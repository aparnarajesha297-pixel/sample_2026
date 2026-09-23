"""Experiment 4: scalability (plan phase 14).

Places N vehicles inside one RSU's coverage area (default 1 km x 1 km street
grid, so neighbour counts grow with N: the stress case), simulates T + 1
seconds of 1 Hz CAMs, and measures, for N in 10 ... 1000:

  feature time      messages -> step features for the whole window
  graph time        dynamic vehicle graph for the whole window
  inference latency scoring every vehicle's newest step (mean, P95, P99)
  CPU usage         process CPU % during inference (100 % = one core)
  memory            process RSS after the run (MB)

Latency is the end-to-end cost of recomputing the full T-step window; an RSU
that caches per-snapshot embeddings would be cheaper. Weights do not affect
timing; pass --checkpoint results/exp1/ravenx_model.pt to use a trained model.

Example:
  python scripts/run_scalability.py --vehicles 10 50 100 200 500 1000
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import psutil
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ravenx import plots  # noqa: E402
from ravenx.config import FEATURES, NEIGHBOR_RADIUS, SEQ_LEN  # noqa: E402
from ravenx.experiment import to_markdown  # noqa: E402
from ravenx.features import Normalizer, build_steps, build_windows  # noqa: E402
from ravenx.graph import build_graph  # noqa: E402
from ravenx.models.train import NeuralDetector  # noqa: E402
from ravenx.pipeline import StepData  # noqa: E402


def scene_messages(n, T, area, block, rng):
    """1 Hz CAMs of n vehicles driving on a street grid, heard by one RSU."""
    lines = np.arange(0, area + 1e-9, block)
    horizontal = rng.random(n) < 0.5
    street = rng.choice(lines, n)
    along = rng.uniform(0, area, n)
    direction = rng.choice([-1.0, 1.0], n)
    speed = rng.uniform(5, 15, n)
    rows = []
    for t in range(T + 1):
        s = speed + rng.normal(0, 0.3, n)
        along = (along + direction * s) % area
        x = np.where(horizontal, along, street) + rng.normal(0, 1.5, n)
        y = np.where(horizontal, street, along) + rng.normal(0, 1.5, n)
        hed = np.where(horizontal, np.where(direction > 0, 0, 180), np.where(direction > 0, 90, 270))
        rows.append(pd.DataFrame({
            "alias": np.arange(n).astype(str), "rcv_time": t + 0.002, "send_time": float(t),
            "x": x, "y": y, "spd": s, "hed": hed.astype(float), "acl": rng.normal(0, 0.3, n)}))
    m = pd.concat(rows, ignore_index=True)
    m["receiver"] = "rsu0"; m["attacker"] = 0; m["split"] = "test"
    return m


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--vehicles", nargs="*", type=int, default=[10, 50, 100, 200, 500, 1000])
    p.add_argument("--repeats", type=int, default=30)
    p.add_argument("--area", type=float, default=1000.0, help="RSU coverage side length (m)")
    p.add_argument("--block", type=float, default=100.0, help="street spacing (m)")
    p.add_argument("--radius", type=float, default=NEIGHBOR_RADIUS)
    p.add_argument("--seq-len", type=int, default=SEQ_LEN)
    p.add_argument("--hidden", type=int, default=64)
    p.add_argument("--model", default="RAVEN-X", choices=["RAVEN-X", "GAT+GRU", "GRU", "GAT"])
    p.add_argument("--checkpoint", default=None)
    p.add_argument("--threads", type=int, default=None, help="torch CPU threads")
    p.add_argument("--out", default="results/scalability")
    p.add_argument("--seed", type=int, default=0)
    args = p.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    if args.threads:
        torch.set_num_threads(args.threads)

    det = NeuralDetector(args.model, len(FEATURES), hidden=args.hidden, verbose=False)
    norm = None
    if args.checkpoint:
        ck = torch.load(args.checkpoint, weights_only=False)
        det.net.load_state_dict(ck["state_dict"])
        norm = Normalizer(); norm.mu, norm.sd = ck["norm_mu"], ck["norm_sd"]
    det.net.eval()
    proc = psutil.Process()
    rng = np.random.default_rng(args.seed)

    rows = []
    for n in args.vehicles:
        msgs = scene_messages(n, args.seq_len, args.area, args.block, rng)
        t0 = time.perf_counter()
        steps = build_steps(msgs, 1.0)
        win = build_windows(steps, args.seq_len)
        t_feat = time.perf_counter() - t0
        t0 = time.perf_counter()
        graph, group = build_graph(steps, args.radius)
        t_graph = time.perf_counter() - t0
        X_raw = steps[FEATURES].values.astype(np.float32)
        nm = norm or Normalizer().fit(X_raw)
        data = StepData(steps, X_raw, nm.transform(X_raw), steps["label"].values, win, graph, group, nm)
        newest = np.where(steps["bin"].values == steps["bin"].max())[0]

        det.predict(data, newest)                      # warm-up
        proc.cpu_percent(None)
        lat = []
        wall0 = time.perf_counter()
        for _ in range(args.repeats):
            t0 = time.perf_counter()
            det.predict(data, newest, batch_size=4096)
            lat.append(time.perf_counter() - t0)
        cpu = proc.cpu_percent(None)
        lat_ms = np.array(lat) * 1000
        snap = graph.n_edges / max(steps["bin"].nunique(), 1) / 2
        rows.append({
            "Vehicles": n,
            "AvgNeighbors": graph.n_edges / len(steps),
            "EdgesPerSnapshot": snap,
            "FeatureTime_ms": t_feat * 1000,
            "GraphTime_ms": t_graph * 1000,
            "Latency_mean_ms": lat_ms.mean(),
            "Latency_P95_ms": np.percentile(lat_ms, 95),
            "Latency_P99_ms": np.percentile(lat_ms, 99),
            "PerVehicle_ms": lat_ms.mean() / len(newest),
            "CPU_percent": cpu,
            "RSS_MB": proc.memory_info().rss / 2 ** 20,
            "Wall_s": time.perf_counter() - wall0,
        })
        r = rows[-1]
        print(f"N={n:5d}  neighbours {r['AvgNeighbors']:6.1f}  graph {r['GraphTime_ms']:8.1f} ms  "
              f"latency {r['Latency_mean_ms']:8.1f} ms (P95 {r['Latency_P95_ms']:.1f}, "
              f"P99 {r['Latency_P99_ms']:.1f})  CPU {r['CPU_percent']:.0f}%  RSS {r['RSS_MB']:.0f} MB")

    df = pd.DataFrame(rows)
    df.to_csv(out / "scalability.csv", index=False)
    x = df["Vehicles"].values
    plots.line_plot(x, {"mean": df["Latency_mean_ms"], "P95": df["Latency_P95_ms"],
                        "P99": df["Latency_P99_ms"]}, "vehicles", "latency (ms)",
                    "Vehicles vs inference latency", out / "vehicles_vs_latency.png", logx=True)
    plots.line_plot(x, {"CPU": df["CPU_percent"]}, "vehicles", "CPU (% of one core)",
                    "Vehicles vs CPU", out / "vehicles_vs_cpu.png", logx=True)
    plots.line_plot(x, {"RSS": df["RSS_MB"]}, "vehicles", "process memory (MB)",
                    "Vehicles vs memory", out / "vehicles_vs_memory.png", logx=True)
    plots.line_plot(x, {"graph": df["GraphTime_ms"], "features": df["FeatureTime_ms"]},
                    "vehicles", "time (ms)", "Vehicles vs graph construction time",
                    out / "vehicles_vs_graph_time.png", logx=True)
    (out / "report.md").write_text(
        f"# Scalability ({args.model}, {torch.get_num_threads()} CPU threads)\n\n"
        + to_markdown(df, index=False) + "\n")
    print("\n" + to_markdown(df, index=False))


if __name__ == "__main__":
    main()
