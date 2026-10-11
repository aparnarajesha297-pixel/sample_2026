"""Re-tune the alarm threshold on a small labelled slice of the target domain.

Reads the target-test scores saved by ``run_cross_scenario.py --save-scores``
(one directory per seed). The models are not retrained: only the threshold
changes. For each budget (share of target receiver files per attack run that
gets labelled) the slice is drawn ``--draws`` times; all thresholds are scored
on the receivers outside the slice. See ravenx/target_threshold.py.

Before re-tuning, every saved score file is checked against the per-seed CSV
of the run that wrote it: the source threshold on the full target set must
give the same F1.

Example:
  python scripts/run_target_threshold.py results/cross_tt/seed_0 results/cross_tt/seed_1 \\
      results/cross_tt/seed_2 --out reports/target_threshold_19f
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ravenx.experiment import to_markdown  # noqa: E402
from ravenx.metrics import detection_metrics  # noqa: E402
from ravenx.target_threshold import retune  # noqa: E402

KINDS = ["source", "tuned", "oracle"]


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("runs", nargs="+", help="cross-scenario output dirs (each with scores/ and the per-seed CSV)")
    p.add_argument("--fracs", nargs="*", type=float, default=[0.01, 0.05, 0.10, 0.20])
    p.add_argument("--draws", type=int, default=20)
    p.add_argument("--out", default="results/target_threshold")
    args = p.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)

    rows, checks, order = [], [], []
    for run_dir in map(Path, args.runs):
        ref = pd.read_csv(run_dir / "cross_scenario_per_seed.csv")
        order.append(ref)
        for f in sorted((run_dir / "scores").glob("*__seed*.npz")):
            tag, model, seed = re.match(r"(.+)__(.+?)__seed(\d+)\.npz", f.name).groups()
            seed = int(seed)
            tgt = np.load(run_dir / "scores" / f"{tag}__target.npz")
            sc = np.load(f)
            y, pr, thr = tgt["y"].astype(int), sc["p"], float(sc["thr"])
            test = tag.replace("__to__", " → ").replace("_density", " density")
            if test not in set(ref["Test"]):
                test = tag.replace("__to__", " → ")
            r = ref[(ref.Test == test) & (ref.Model == model) & (ref.Seed == seed)]
            f1_full = detection_metrics(y, pr, thr)["F1"]
            ok = len(r) == 1 and abs(r["F1"].iloc[0] - f1_full) < 1e-9
            checks.append({"Test": test, "Model": model, "Seed": seed, "F1 (csv)": r["F1"].iloc[0] if len(r) else np.nan,
                           "F1 (scores)": f1_full, "match": ok})
            if not ok:
                raise SystemExit(f"score file does not reproduce the run's F1: {f}")
            df = retune(y, pr, thr, tgt["run"], tgt["unit"], args.fracs, args.draws, seed=1000 + seed)
            df.insert(0, "Seed", seed); df.insert(0, "Model", model); df.insert(0, "Test", test)
            rows.append(df)
            print(f"{test} | {model} | seed {seed}: source F1 {f1_full:.4f}", flush=True)
    pd.DataFrame(checks).to_csv(out / "score_check.csv", index=False)
    raw = pd.concat(rows, ignore_index=True)
    raw.to_csv(out / "target_threshold_draws.csv", index=False)

    # mean over draws, then mean +- std over seeds; draw std reported separately
    per_seed = (raw.groupby(["Test", "Model", "Seed", "Budget", "Kind"])
                .agg(F1=("F1", "mean"), F1_draw_std=("F1", "std"), Precision=("Precision", "mean"),
                     Recall=("Recall", "mean"), Threshold=("Threshold", "mean"),
                     slice_rcv=("Slice receivers", "mean"), slice_steps=("Slice steps", "mean"))
                .reset_index())
    per_seed.to_csv(out / "target_threshold_per_seed.csv", index=False)
    agg = (per_seed.groupby(["Test", "Model", "Budget", "Kind"])
           .agg(F1=("F1", "mean"), F1_std=("F1", "std"), F1_draw_std=("F1_draw_std", "mean"),
                Precision=("Precision", "mean"), Recall=("Recall", "mean"),
                slice_rcv=("slice_rcv", "mean"), slice_steps=("slice_steps", "mean"),
                seeds=("Seed", "nunique"))
           .reset_index())
    agg.to_csv(out / "target_threshold_mean_std.csv", index=False)

    # same test / model order as the cross-scenario report
    ref_all = pd.concat(order)
    test_order = [t for t in dict.fromkeys(ref_all["Test"]) if t in set(raw["Test"])]
    ref_b = 0.10 if 0.10 in args.fracs else args.fracs[-1]   # budget whose held-out set shows source/oracle
    model_order = [m for m in dict.fromkeys(ref_all["Model"]) if m in set(raw["Model"])]
    md = ["# Threshold re-tuning on target data", "",
          f"Seeds {sorted(raw.Seed.unique().tolist())}, {args.draws} slice draws per budget. "
          "Budget = share of target receiver files labelled in every attack run (at least one). "
          "All F1 values are on the target receivers outside the slice, mean ± std over seeds "
          "(each seed first averaged over draws). *Source* is the threshold from source "
          "validation, *oracle* the best threshold for the held-out receivers themselves; both are "
          f"shown on the held-out receivers of the {ref_b:.0%} budget. Gains in the last table are "
          "paired (same held-out receivers for tuned and source).", ""]
    for test in test_order:
        a = agg[agg.Test == test]
        md += [f"## {test}", ""]
        cols = ["source"] + [f"tuned {b:.0%}" for b in args.fracs] + ["oracle"]
        tab = []
        for model in [m for m in model_order if m in set(a.Model)]:
            b = a[a.Model == model]
            row = {"Model": model}
            src = b[(b.Kind == "source") & (b.Budget == ref_b)].iloc[0]
            row["source"] = f"{src.F1:.4f} ± {src.F1_std:.4f}"
            for fr in args.fracs:
                t = b[(b.Kind == "tuned") & (b.Budget == fr)].iloc[0]
                row[f"tuned {fr:.0%}"] = f"{t.F1:.4f} ± {t.F1_std:.4f}"
            orc = b[(b.Kind == "oracle") & (b.Budget == ref_b)].iloc[0]
            row["oracle"] = f"{orc.F1:.4f} ± {orc.F1_std:.4f}"
            tab.append(row)
        md += [to_markdown(pd.DataFrame(tab)[["Model"] + cols], index=False), ""]
        sl = a[(a.Kind == "tuned")].groupby("Budget")[["slice_rcv", "slice_steps"]].mean()
        md += ["Slice size: " + ", ".join(f"{b:.0%} → {r.slice_rcv:.0f} receivers / {r.slice_steps:,.0f} steps"
                                           for b, r in sl.iterrows()), ""]
    # compact summary: gain of the tuned threshold at each budget
    summ = []
    for (test, model), b in agg.groupby(["Test", "Model"]):
        def f1(kind, fr):
            return b[(b.Kind == kind) & (b.Budget == fr)].F1.iloc[0]
        # paired: tuned and source on the same held-out receivers of each budget
        r = {"Test": test, "Model": model, "source F1": f"{f1('source', ref_b):.4f}"}
        for fr in args.fracs:
            r[f"Δ {fr:.0%}"] = f"{f1('tuned', fr) - f1('source', fr):+.4f}"
        r["Δ oracle"] = f"{f1('oracle', ref_b) - f1('source', ref_b):+.4f}"
        summ.append(r)
    summ = pd.DataFrame(summ)
    summ["_t"] = summ.Test.map(test_order.index); summ["_m"] = summ.Model.map(model_order.index)
    summ = summ.sort_values(["_t", "_m"]).drop(columns=["_t", "_m"])
    md += ["## F1 gain over the source threshold", "", to_markdown(summ, index=False), ""]
    (out / "report.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
