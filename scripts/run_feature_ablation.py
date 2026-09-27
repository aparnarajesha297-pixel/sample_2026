"""Row 13: feature-group ablation.

Retrains the detectors on five progressively larger feature sets, so each
step shows what one group of features adds:

  G1 basic motion        Speed, Heading, Acceleration, PositionChange,
                         SpeedChange, HeadingChange, Jerk
  G2 + timing            MessageGap, TimeLag, MsgCount
  G3 + self-consistency  SpeedInconsistency, AccelerationInconsistency,
                         HeadingInconsistency
  G4 + map / geometry    RoadEdgeDist, DistanceToReceiver
  G5 + relative to receiver (all 17)   RelativeSpeed, RelativeHeading

Thresholds are chosen on validation; metrics are on test. Results are
written after every training, and a rerun skips (step, model, seed)
combinations that are already done.

Example:
  python scripts/run_feature_ablation.py --data nextgen --root /data/NextGen/hw2 \
      --models RAVEN-X-GF XGBoost --seeds 0 1 2
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ravenx import plots  # noqa: E402
from ravenx.config import FEATURES  # noqa: E402
from ravenx.experiment import (add_train_args, feature_subset, fit_and_score,  # noqa: E402
                               fmt_table, mean_std_table, to_markdown)
from ravenx.pipeline import add_data_args, load_data  # noqa: E402

GROUPS = [
    ("G1 basic motion", ["Speed", "Heading", "Acceleration", "PositionChange", "SpeedChange",
                         "HeadingChange", "Jerk"]),
    ("G2 + timing", ["MessageGap", "TimeLag", "MsgCount"]),
    ("G3 + self-consistency", ["SpeedInconsistency", "AccelerationInconsistency",
                               "HeadingInconsistency"]),
    ("G4 + map/geometry", ["RoadEdgeDist", "DistanceToReceiver"]),
    ("G5 + relative to receiver", ["RelativeSpeed", "RelativeHeading"]),
]
assert sorted(sum((g for _, g in GROUPS), [])) == sorted(FEATURES), "groups must cover all features"
COLS = ["F1", "Recall", "Precision", "PR-AUC", "ROC-AUC", "ECE"]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_data_args(ap)
    add_train_args(ap)
    ap.set_defaults(models=["RAVEN-X-GF", "XGBoost"], seeds=[0, 1, 2], quiet=True)
    ap.add_argument("--out", default="results/feature_ablation")
    args = ap.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    per_seed = out / "ablation_per_seed.csv"
    done = pd.read_csv(per_seed) if per_seed.exists() else pd.DataFrame(columns=["Step", "Model", "Seed"])

    _, data = load_data(args)
    tr, va, te = data.idx("train"), data.idx("val"), data.idx("test")
    names = []
    for step, group in GROUPS:
        names = names + group
        d = feature_subset(data, names)
        for seed in args.seeds:
            for model in args.models:
                if ((done.Step == step) & (done.Model == model) & (done.Seed == seed)).any():
                    continue
                print(f"== {step} ({len(names)} features) | {model} | seed {seed} ==", flush=True)
                m = fit_and_score(model, d, tr, va, te, args, seed)["metrics"]
                row = {"Step": step, "Features": len(names), "Model": model, "Seed": seed,
                       **{c: m[c] for c in COLS}}
                print("   " + "  ".join(f"{c} {row[c]:.4f}" for c in COLS), flush=True)
                done = pd.concat([done, pd.DataFrame([row])], ignore_index=True)
                done.to_csv(per_seed, index=False)

    md = ["# Feature-group ablation (row 13)", "",
          f"Seeds: {sorted(done.Seed.unique().tolist())}. Each step adds one feature group to the "
          "previous step; thresholds chosen on validation, metrics on test.", ""]
    for model in args.models:
        sub = done[done.Model == model].copy()
        sub["Key"] = sub["Step"] + " (" + sub["Features"].astype(int).astype(str) + ")"
        mean, std = mean_std_table(sub.drop(columns=["Step", "Model", "Features"]).to_dict("records"),
                                   by="Key", cols=COLS)
        order = [f"{s} ({n})" for s, n in zip([g[0] for g in GROUPS],
                                               pd.Series([len(g[1]) for g in GROUPS]).cumsum())]
        mean, std = mean.reindex([o for o in order if o in mean.index]), std.reindex([o for o in order if o in std.index])
        gain = mean["F1"].diff()
        tab = fmt_table(mean, std)
        tab["ΔF1 vs previous step"] = [("" if pd.isna(g) else f"{g:+.4f}") for g in gain]
        md += [f"## {model}", "", to_markdown(tab), ""]
        plots.line_plot(range(1, len(mean) + 1), {"F1": mean["F1"], "PR-AUC": mean["PR-AUC"],
                                                  "Recall": mean["Recall"]},
                        "feature step (G1 … G5)", "score (test, mean over seeds)",
                        f"Feature-group ablation: {model}", out / f"ablation_{model}.png")
    (out / "report.md").write_text("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
