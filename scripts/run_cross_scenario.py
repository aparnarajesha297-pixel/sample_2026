"""Cross-scenario generalisation (plan phase 10).

Is the model learning misbehaviour, or memorising the environment it was
trained in? Each test trains on the train/val splits of a source domain and
evaluates on the test split of a different target domain. The in-domain score
(source -> source test split) is reported next to it so the drop is visible.

  Test 1  urban        -> highway
  Test 2  low density  -> high density
  Test 3  scenario A   -> scenario B, for every ordered pair

Neural-model inputs are re-normalised with source-domain statistics only.

Example:
  python scripts/run_cross_scenario.py --data nextgen --root /data/NextGen \
      --density-map highway_1=low,highway_2=high,urban_1=low,urban_2=high
"""

from __future__ import annotations

import argparse
import itertools
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ravenx.experiment import (add_train_args, fit_and_score, fmt_table,  # noqa: E402
                               mean_std_table, renormalized, subsample, to_markdown)
from ravenx.metrics import detection_metrics  # noqa: E402
from ravenx.pipeline import add_data_args, load_data  # noqa: E402

COLS = ["F1", "Recall", "PR-AUC", "ECE"]


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_data_args(p)
    add_train_args(p)
    p.add_argument("--pair-models", nargs="*", default=["XGBoost", "RAVEN-X", "RAVEN-X-GF"],
                   help="models for the scenario-pair matrix (test 3)")
    p.add_argument("--skip-pairs", action="store_true")
    p.add_argument("--out", default="results/cross_scenario")
    args = p.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)

    _, data = load_data(args)
    st = data.steps
    tests = []
    if {"urban", "highway"} <= set(st["road"]):
        tests.append(("Urban → Highway", {"road": "urban"}, {"road": "highway"}, args.models))
    if {"low", "high"} <= set(st["density"]):
        tests.append(("Low → High density", {"density": "low"}, {"density": "high"}, args.models))
    if not args.skip_pairs:
        for a, b in itertools.permutations(sorted(st["scenario"].unique()), 2):
            tests.append((f"{a} → {b}", {"scenario": a}, {"scenario": b}, args.pair_models))
    if not tests:
        raise SystemExit("Need at least two roads, densities or scenarios in the data "
                         "(for NextGen pass --density-map if folder names lack low/high).")

    rows = []
    for name, src, dst, models in tests:
        tr_all, va = data.idx("train", **src), data.idx("val", **src)
        te_in, te_out = data.idx("test", **src), data.idx("test", **dst)
        if min(len(tr_all), len(va), len(te_out)) == 0:
            print(f"skip {name}: empty split"); continue
        d = renormalized(data, tr_all)
        for seed in args.seeds:
            tr = subsample(tr_all, args.max_train, seed)
            for model in models:
                print(f"\n== {name} | {model} | seed {seed} ==")
                res = fit_and_score(model, d, tr, va, te_out, args, seed)
                r_in, _ = res["model"].predict(d, te_in)
                m_in = detection_metrics(d.y[te_in], r_in, res["threshold"]) if len(te_in) else {}
                row = {"Test": name, "Model": model, "Seed": seed}
                row.update({f"{c}": res["metrics"][c] for c in COLS})
                row.update({f"in-domain {c}": m_in.get(c, float("nan")) for c in COLS})
                row["ΔF1 (cross - in)"] = row["F1"] - row["in-domain F1"]
                rows.append(row)
                print("   cross: " + "  ".join(f"{c} {row[c]:.4f}" for c in COLS)
                      + f" | in-domain F1 {row['in-domain F1']:.4f}")

    df = pd.DataFrame(rows)
    df.to_csv(out / "cross_scenario_per_seed.csv", index=False)
    df["Key"] = df["Test"] + " / " + df["Model"]
    cols = COLS + ["in-domain F1", "ΔF1 (cross - in)"]
    mean, std = mean_std_table(df.drop(columns=["Test", "Model"]).to_dict("records"), by="Key", cols=cols)
    mean.to_csv(out / "cross_scenario_mean.csv")
    md = to_markdown(fmt_table(mean, std))
    header = f"# Cross-scenario generalisation ({args.data} data)\n\n"
    if args.data == "synthetic":
        header += "> Synthetic data: pipeline check only, not a result.\n\n"
    (out / "report.md").write_text(header + md + "\n")
    print("\n" + md)


if __name__ == "__main__":
    main()
