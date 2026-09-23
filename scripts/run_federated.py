"""Experiments 3 and poisoning: federated RAVEN-X across RSUs (plan 12-13).

For every aggregation rule (FedAvg, Median, Krum, RS-WeightedTrim) and every
poisoning setting (none, label flipping, sign-flipped scaled updates) it
trains RAVEN-X over ``--rsus`` RSUs and reports

  Global Accuracy, F1, Recall, PR-AUC, ECE, communication cost, training time
  ΔF1 = F1(no attack) - F1(poisoned)             (same aggregator)
  ASR = share of test attack steps the poisoned model lets through as benign

The server uses the validation split only to pick the decision threshold.

Example:
  python scripts/run_federated.py --rsus 20 --malicious 4 --rounds 15
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ravenx import plots  # noqa: E402
from ravenx.config import FEATURES  # noqa: E402
from ravenx.experiment import subsample, to_markdown, write_json  # noqa: E402
from ravenx.federated import (AGGREGATORS, POISONING, make_aggregator,  # noqa: E402
                              partition_rsus, run_federated)
from ravenx.metrics import best_threshold, detection_metrics, pr_auc  # noqa: E402
from ravenx.models.train import NeuralDetector  # noqa: E402
from ravenx.pipeline import add_data_args, load_data  # noqa: E402


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_data_args(p)
    p.add_argument("--model", default="RAVEN-X", choices=["RAVEN-X", "GAT+GRU", "GRU", "GAT"])
    p.add_argument("--rsus", type=int, default=20)
    p.add_argument("--partition", choices=["spatial", "random", "attack"], default="spatial")
    p.add_argument("--rounds", type=int, default=10)
    p.add_argument("--local-epochs", type=int, default=1)
    p.add_argument("--malicious", type=int, default=4, help="number of poisoning RSUs")
    p.add_argument("--sign-scale", type=float, default=3.0)
    p.add_argument("--aggregators", nargs="*", default=AGGREGATORS, choices=AGGREGATORS)
    p.add_argument("--poisoning", nargs="*", default=POISONING, choices=POISONING)
    p.add_argument("--hidden", type=int, default=64)
    p.add_argument("--batch-size", type=int, default=256)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--max-train", type=int, default=None)
    p.add_argument("--out", default="results/federated")
    args = p.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)

    _, data = load_data(args)
    tr = subsample(data.idx("train"), args.max_train, args.seed)
    va, te = data.idx("val"), data.idx("test")
    clients = partition_rsus(data, tr, args.rsus, args.partition, args.seed)
    rng = np.random.default_rng(args.seed)
    malicious = sorted(rng.choice(args.rsus, args.malicious, replace=False).tolist())
    sizes = [len(c) for c in clients]
    print(f"{args.rsus} RSUs, steps per RSU min/median/max = "
          f"{min(sizes)}/{int(np.median(sizes))}/{max(sizes)}; malicious RSUs: {malicious}")
    write_json({"sizes": sizes, "malicious": malicious, "partition": args.partition},
               out / "partition.json")

    def make(seed):
        return NeuralDetector(args.model, len(FEATURES), hidden=args.hidden, lr=args.lr,
                              batch_size=args.batch_size, seed=seed, verbose=False)

    def eval_round(det):
        r, _ = det.predict(data, va)
        return {"val_pr_auc": pr_auc(data.y[va], r)}

    rows, curves = [], {}
    for agg_name in args.aggregators:
        for pois in args.poisoning:
            print(f"\n== {agg_name} | poisoning: {pois} ==")
            agg = make_aggregator(agg_name, args.rsus, args.malicious if pois != "none" else 0)
            det, log, comm, wall = run_federated(
                make, data, clients, agg, rounds=args.rounds, local_epochs=args.local_epochs,
                malicious=malicious if pois != "none" else (), poisoning=pois,
                sign_scale=args.sign_scale, eval_fn=eval_round)
            r_va, _ = det.predict(data, va)
            thr = best_threshold(data.y[va], r_va)
            r_te, _ = det.predict(data, te)
            m = detection_metrics(data.y[te], r_te, thr)
            atk = data.y[te] == 1
            asr = float((r_te[atk] < thr).mean()) if atk.any() else float("nan")
            rows.append({"Aggregator": agg_name, "Poisoning": pois,
                         "Accuracy": m["Accuracy"], "F1": m["F1"], "Recall": m["Recall"],
                         "PR-AUC": m["PR-AUC"], "ECE": m["ECE"], "ASR": asr,
                         "Comm_MB": comm / 2 ** 20, "TrainTime_s": wall})
            curves[f"{agg_name} / {pois}"] = [e["val_pr_auc"] for e in log]
            pd.DataFrame(log).to_csv(out / f"rounds_{agg_name}_{pois}.csv", index=False)
            print("   " + "  ".join(f"{k} {v:.4f}" for k, v in rows[-1].items()
                                    if isinstance(v, float)))

    df = pd.DataFrame(rows)
    clean = df[df["Poisoning"] == "none"].set_index("Aggregator")
    if not clean.empty:
        df["ΔF1"] = df.apply(lambda r: clean.loc[r["Aggregator"], "F1"] - r["F1"]
                             if r["Aggregator"] in clean.index else np.nan, axis=1)
        df["ΔASR"] = df.apply(lambda r: r["ASR"] - clean.loc[r["Aggregator"], "ASR"]
                              if r["Aggregator"] in clean.index else np.nan, axis=1)
    df.to_csv(out / "federated_results.csv", index=False)
    rounds = np.arange(1, args.rounds + 1)
    for pois in args.poisoning:
        sel = {k.split(" / ")[0]: v for k, v in curves.items() if k.endswith(f"/ {pois}")}
        plots.line_plot(rounds, sel, "round", "validation PR-AUC",
                        f"Federated training, poisoning = {pois}", out / f"rounds_{pois}.png")

    md = to_markdown(df, index=False)
    header = (f"# Federated RAVEN-X ({args.data} data)\n\n{args.rsus} RSUs ({args.partition} partition), "
              f"{args.rounds} rounds x {args.local_epochs} local epoch(s), "
              f"{args.malicious} malicious RSUs in poisoned runs.\n\n")
    if args.data == "synthetic":
        header += "> Synthetic data: pipeline check only, not a result.\n\n"
    (out / "report.md").write_text(header + md + "\n")
    print("\n" + md)


if __name__ == "__main__":
    main()
