"""Row 6: combine per-seed cross-scenario runs into one mean +- std table.

Each seed was run into its own folder by run_cross_scenario.py. With one
scenario per density (highway_2 = low, highway_7 = high) the
"highway_2 -> highway_7" pair is the same experiment as the
"Low -> High density" test, so it is always taken from the density rows
(seed 0 had also trained it separately before the dedup was added; those
duplicate rows are dropped so every seed is counted the same way).

Example:
  python scripts/aggregate_cross_seeds.py results/cross/seed_0 results/cross/seed_1 \
      results/cross/seed_2 --pair "highway_2 → highway_7" --out reports/nextgen_cross_scenario_3seeds
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ravenx.experiment import fmt_table, to_markdown  # noqa: E402

COLS = ["F1", "Recall", "PR-AUC", "ECE", "in-domain F1", "ΔF1 (cross - in)"]
DENSITY = "Low → High density"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dirs", nargs="+")
    ap.add_argument("--pair", default="highway_2 → highway_7",
                    help="scenario pair identical to the density test")
    ap.add_argument("--pair-models", nargs="*", default=["XGBoost", "RAVEN-X", "RAVEN-X-GF"])
    ap.add_argument("--out", default="reports/nextgen_cross_scenario_3seeds")
    args = ap.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)

    df = pd.concat([pd.read_csv(Path(d) / "cross_scenario_per_seed.csv") for d in args.dirs], ignore_index=True)
    df = df[df.Test != args.pair]
    pair = df[(df.Test == DENSITY) & df.Model.isin(args.pair_models)].assign(Test=args.pair)
    df = pd.concat([df, pair], ignore_index=True).drop_duplicates(["Test", "Model", "Seed"])
    df.to_csv(out / "cross_scenario_per_seed.csv", index=False)

    g = df.groupby(["Test", "Model"], sort=False)
    mean, std = g[COLS].mean(), g[COLS].std().fillna(0.0)
    n = g.size().rename("seeds")
    mean.join(std, rsuffix=" std").join(n).to_csv(out / "cross_scenario_mean_std.csv")

    seeds = sorted(df.Seed.unique().tolist())
    md = [f"# Cross-scenario generalisation, {len(seeds)} seeds (row 6)", "",
          f"Seeds {seeds}. Train on the source domain's train/val split (threshold picked on source "
          "validation), test on the target domain's test split. In-domain F1 is the same model on the "
          "source test split. Values are mean ± std over seeds.", "",
          f"`{args.pair}` is the same experiment as `{DENSITY}` (one scenario per density) and is "
          "copied from it.", ""]
    tests = list(dict.fromkeys(df.Test))
    for t in tests:
        tab = fmt_table(mean.loc[t], std.loc[t])
        tab["seeds"] = n.loc[t].values
        md += [f"## {t}", "", to_markdown(tab), ""]
    pr = mean["PR-AUC"].unstack("Model")
    pr = pr.astype(object).where(pr.notna(), "–")
    md += ["## PR-AUC summary (mean over seeds)", "", to_markdown(pr), ""]
    (out / "report.md").write_text("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
