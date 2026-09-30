"""Row 20: tune the neighbour radius and the time-bin length on validation.

One factor at a time around the defaults (radius 150 m, bin 1 s):
  radius in {50, 100, 150, 250} m   with bin = 1 s
  bin    in {0.5, 1, 2} s           with radius = 150 m
For each setting the steps and the neighbour graph are rebuilt and the
detector retrained. The setting is chosen by VALIDATION PR-AUC (threshold
free); validation F1 and test metrics are reported alongside, and the test
split plays no part in the choice.

Note: the bin length changes what one step is (a shorter bin gives more,
smaller steps), so metrics across bin lengths are over slightly different
units; within a bin length they are directly comparable.

Example:
  python scripts/run_graph_params.py --data nextgen --root /data/NextGen/hw2 --seeds 0 1
"""

from __future__ import annotations

import argparse
import gc
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ravenx import plots  # noqa: E402
from ravenx.experiment import add_train_args, fit_and_score, to_markdown  # noqa: E402
from ravenx.metrics import best_threshold, detection_metrics, pr_auc  # noqa: E402
from ravenx.pipeline import add_data_args, load_messages, prepare  # noqa: E402

SETTINGS = [(50, 1.0), (100, 1.0), (150, 1.0), (250, 1.0), (150, 0.5), (150, 2.0)]
COLS = ["val PR-AUC", "val F1", "F1", "PR-AUC", "Recall", "Precision", "ECE", "neighbours/vehicle", "steps"]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_data_args(ap)
    add_train_args(ap)
    ap.set_defaults(models=["RAVEN-X-GF"], seeds=[0, 1], quiet=True)
    ap.add_argument("--out", default="results/graph_params")
    args = ap.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    per_seed = out / "graph_params_per_seed.csv"
    done = pd.read_csv(per_seed) if per_seed.exists() else pd.DataFrame(columns=["Radius", "Bin", "Model", "Seed"])

    msgs = load_messages(args)
    for radius, bin_s in SETTINGS:
        todo = [(m, s) for s in args.seeds for m in args.models
                if not ((done.Radius == radius) & (done.Bin == bin_s) & (done.Model == m) & (done.Seed == s)).any()]
        if not todo:
            continue
        data = prepare(msgs, bin_s, radius, args.max_neighbors or None, args.seq_len)
        tr, va, te = data.idx("train"), data.idx("val"), data.idx("test")
        nbr = data.graph.n_edges / len(data.steps)
        for model, seed in todo:
            print(f"== radius {radius} m, bin {bin_s} s | {model} | seed {seed} ==", flush=True)
            res = fit_and_score(model, data, tr, va, te, args, seed)
            r_va = res["val"][0]
            m = res["metrics"]
            row = {"Radius": radius, "Bin": bin_s, "Model": model, "Seed": seed,
                   "val PR-AUC": pr_auc(data.y[va], r_va),
                   "val F1": detection_metrics(data.y[va], r_va, best_threshold(data.y[va], r_va))["F1"],
                   "F1": m["F1"], "PR-AUC": m["PR-AUC"], "Recall": m["Recall"],
                   "Precision": m["Precision"], "ECE": m["ECE"],
                   "neighbours/vehicle": nbr, "steps": len(data.steps)}
            print("   " + "  ".join(f"{c} {row[c]:.4f}" for c in COLS[:7]), flush=True)
            done = pd.concat([done, pd.DataFrame([row])], ignore_index=True)
            done.to_csv(per_seed, index=False)
        del data
        gc.collect()

    g = done.groupby(["Model", "Radius", "Bin"])
    mean, std = g[COLS].mean(), g[COLS].std().fillna(0.0)
    md = ["# Neighbour radius and time-bin length (row 20)", "",
          f"Seeds: {sorted(done.Seed.unique().tolist())}. Chosen by validation PR-AUC; "
          "test metrics shown for reference only.", ""]
    for model in mean.index.get_level_values(0).unique():
        mm, ss = mean.loc[model], std.loc[model]
        best = mm["val PR-AUC"].idxmax()
        tab = mm.copy().astype(object)
        for c in COLS:
            fmt = "{:.0f}" if c == "steps" else ("{:.2f}" if c == "neighbours/vehicle" else "{:.4f}")
            tab[c] = [fmt.format(v) + (f" ± {s:.4f}" if c in COLS[:7] and len(args.seeds) > 1 else "")
                      for v, s in zip(mm[c], ss[c])]
        tab.insert(0, "chosen", ["◀" if i == best else "" for i in tab.index])
        md += [f"## {model}", "", f"Chosen on validation: radius **{best[0]} m**, bin **{best[1]} s**.", "",
               to_markdown(tab), ""]
        rad = mm.xs(1.0, level="Bin")
        plots.line_plot(rad.index.values, {"validation PR-AUC": rad["val PR-AUC"], "test PR-AUC": rad["PR-AUC"]},
                        "neighbour radius (m)", "PR-AUC", f"{model}: radius (bin = 1 s)",
                        out / f"radius_{model}.png")
        bins = mm.xs(150, level="Radius")
        plots.line_plot(bins.index.values, {"validation PR-AUC": bins["val PR-AUC"], "test PR-AUC": bins["PR-AUC"]},
                        "time bin (s)", "PR-AUC", f"{model}: bin length (radius = 150 m)",
                        out / f"bin_{model}.png")
    (out / "report.md").write_text("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
