"""G5 feature check: why the "relative to receiver" group does not help, and
whether the neighbour-disagreement group the status document describes does.

Row 13 added the feature groups one at a time; its last group (G5 =
RelativeSpeed, RelativeHeading) compares the sender with the *receiver* and
lowered F1 slightly. The status document's description of row 13 instead
ends with "neighbor-disagreement", which was never tested.

Part 1, data checks (no training):
  - G5 recomputed from the raw fields matches the stored features;
  - sender and receiver headings use the same convention (each against the
    compass bearing of its own motion);
  - single-feature informativeness (|ROC-AUC - 0.5| on train) and train/test
    drift (KS statistic) for every feature and for the receiver's own speed
    and heading.
Part 2, retraining with thresholds on validation and metrics on test:
  G4                     the 15 features before G5 (baseline)
  G4 + G5                the current 17
  G4 + receiver state    G4 + rx_spd, rx_hed (what G5 adds beyond Speed/Heading)
  G4 + neighbour         G4 + the four config.NBR_FEATURES (the default set since this check)
  G4 + G5 + neighbour    all 21

Example:
  python scripts/run_g5_check.py --data nextgen --root /data/NextGen/hw2
"""

from __future__ import annotations

import argparse
import dataclasses
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from scipy.stats import ks_2samp
from sklearn.metrics import roc_auc_score

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ravenx.config import NBR_FEATURES, STEP_FEATURES  # noqa: E402
from ravenx.experiment import add_train_args, fit_and_score, fmt_table, mean_std_table, to_markdown  # noqa: E402
from ravenx.features import Normalizer  # noqa: E402
from ravenx.pipeline import add_data_args, load_data  # noqa: E402

G5 = ["RelativeSpeed", "RelativeHeading"]
RX = ["rx_spd", "rx_hed"]
G4 = list(STEP_FEATURES)
VARIANTS = [("G4", G4), ("G4 + G5", G4 + G5), ("G4 + receiver state", G4 + RX),
            ("G4 + neighbour", G4 + NBR_FEATURES), ("G4 + G5 + neighbour", G4 + G5 + NBR_FEATURES)]
COLS = ["F1", "Recall", "Precision", "PR-AUC", "ROC-AUC", "ECE"]


def wrap(a):
    return (a + 180.0) % 360.0 - 180.0


def data_checks(st, table, y, split):
    tr, te, va = split == "train", split == "test", split == "val"
    md = ["## 1. Data checks", ""]
    rs = st["spd"].values - st["rx_spd"].values
    rh = np.abs(wrap(st["hed"].values - st["rx_hed"].values))
    md.append(f"- Recomputed from raw fields, max |difference|: RelativeSpeed "
              f"{np.nanmax(np.abs(rs - st['RelativeSpeed'].values)):.1e}, RelativeHeading "
              f"{np.nanmax(np.abs(rh - st['RelativeHeading'].values)):.1e}.")
    g = st.groupby("stream", sort=False)
    dx, dy = g["x"].diff().values, g["y"].diff().values
    mv = (np.hypot(dx, dy) > 1) & (y == 0)
    e_s = np.abs(wrap(st["hed"].values - np.degrees(np.arctan2(dx, dy)) % 360))[mv]
    r = st.sort_values(["receiver", "rcv_time"])
    gr = r.groupby("receiver", sort=False)
    rdx, rdy = gr["rx_x"].diff().values, gr["rx_y"].diff().values
    rmv = (np.hypot(rdx, rdy) > 1) & (gr["rcv_time"].diff().values > 0.5)
    e_r = np.abs(wrap(r["rx_hed"].values - np.degrees(np.arctan2(rdx, rdy)) % 360))[rmv]
    md.append(f"- Heading convention: honest sender heading within 10° of the compass bearing of its "
              f"motion in {np.mean(e_s < 10):.0%} of moving steps; receiver heading in {np.mean(e_r < 10):.0%}. "
              "Same convention (0° = north, clockwise).")
    h = np.histogram(st["RelativeHeading"].values[(y == 0) & tr], bins=[0, 30, 60, 120, 150, 180.01])[0]
    md.append("- Honest RelativeHeading on train, share in 0–30 / 30–60 / 60–120 / 120–150 / 150–180°: "
              + " / ".join(f"{v:.2f}" for v in h / h.sum())
              + ". Many crossing directions: the scenario has ramps and crossing roads within range.")
    rows = []
    for f in table.columns:
        v = np.nan_to_num(table[f].values)
        rows.append({"Feature": f, "Group": ("G5" if f in G5 else "receiver" if f in RX
                                            else "neighbour" if f in NBR_FEATURES else "G1-G4"),
                     "|AUC - 0.5| (train)": abs(roc_auc_score(y[tr], v[tr]) - 0.5),
                     "KS train vs val": ks_2samp(v[tr], v[va]).statistic,
                     "KS train vs test": ks_2samp(v[tr], v[te]).statistic})
    inf = pd.DataFrame(rows).sort_values("|AUC - 0.5| (train)", ascending=False)
    md += ["", "Single-feature informativeness and drift:", "", to_markdown(inf, index=False), ""]
    q = lambda m, c: " / ".join(f"{v:.1f}" for v in np.quantile(st[c].values[m], [.1, .5, .9]))
    md.append("Receiver speed 10th / 50th / 90th percentile (m/s): train " + q(tr, "rx_spd") + ", val "
              + q(va, "rx_spd") + ", test " + q(te, "rx_spd") + ".")
    return md, inf


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_data_args(ap)
    add_train_args(ap)
    ap.set_defaults(models=["RAVEN-X-GF", "XGBoost"], seeds=[0, 1, 2], quiet=True)
    ap.add_argument("--out", default="results/g5_check")
    args = ap.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    torch.use_deterministic_algorithms(True)

    _, data = load_data(args)
    st = data.steps
    split = st["split"].values
    table = st[G4 + G5 + RX + NBR_FEATURES].reset_index(drop=True).astype(np.float32)
    md_checks, inf = data_checks(st, table, data.y, split)
    inf.to_csv(out / "feature_checks.csv", index=False)

    names = list(table.columns)
    X_raw = table.values.astype(np.float32)
    X = Normalizer().fit(X_raw[split == "train"]).transform(X_raw)
    tr, va, te = data.idx("train"), data.idx("val"), data.idx("test")

    per_seed = out / "g5_per_seed.csv"
    done = pd.read_csv(per_seed) if per_seed.exists() else pd.DataFrame(columns=["Variant", "Model", "Seed"])
    importances = {}
    for variant, feats in VARIANTS:
        cols = [names.index(f) for f in feats]
        d = dataclasses.replace(data, X_raw=X_raw[:, cols], X=X[:, cols])
        for seed in args.seeds:
            for model in args.models:
                if ((done.Variant == variant) & (done.Model == model) & (done.Seed == seed)).any():
                    continue
                print(f"== {variant} ({len(feats)} features) | {model} | seed {seed} ==", flush=True)
                res = fit_and_score(model, d, tr, va, te, args, seed)
                m = res["metrics"]
                row = {"Variant": variant, "Features": len(feats), "Model": model, "Seed": seed,
                       **{c: m[c] for c in COLS}}
                print("   " + "  ".join(f"{c} {row[c]:.4f}" for c in COLS), flush=True)
                done = pd.concat([done, pd.DataFrame([row])], ignore_index=True)
                done.to_csv(per_seed, index=False)
                if model == "XGBoost" and variant == VARIANTS[-1][0]:
                    imp = getattr(res["model"].model, "feature_importances_", None)
                    if imp is not None:
                        importances[seed] = pd.Series(imp, index=feats)

    md = ["# G5 feature check", "",
          "Row 13's last group (G5 = RelativeSpeed, RelativeHeading) compares the sender with the "
          "receiver. The status document's row 13 instead ends with a neighbour-disagreement group, "
          "which was not tested. This checks G5's correctness, why it does not help, and whether "
          "neighbour disagreement does.", ""] + md_checks + ["", "## 2. Retraining (test, mean ± std over seeds "
          f"{sorted(done.Seed.unique().tolist())}; thresholds on validation)", ""]
    for model in args.models:
        sub = done[done.Model == model].copy()
        mean, std = mean_std_table(sub.drop(columns=["Model", "Features"]).to_dict("records"),
                                   by="Variant", cols=COLS)
        order = [v for v, _ in VARIANTS if v in mean.index]
        mean, std = mean.reindex(order), std.reindex(order)
        tab = fmt_table(mean, std)
        tab.insert(0, "Features", [len(f) for v, f in VARIANTS if v in order])
        tab["ΔF1 vs G4"] = [f"{v:+.4f}" for v in mean["F1"] - mean.loc["G4", "F1"]]
        tab["ΔPR-AUC vs G4"] = [f"{v:+.4f}" for v in mean["PR-AUC"] - mean.loc["G4", "PR-AUC"]]
        md += [f"### {model}", "", to_markdown(tab), ""]
    if importances:
        imp = pd.concat(importances, axis=1).mean(1).sort_values(ascending=False)
        md += ["### XGBoost feature importance (gain share, all 21 features, mean over seeds)", "",
               to_markdown(imp.rename("importance").to_frame()), ""]
        imp.to_csv(out / "xgboost_importance.csv")
    (out / "report.md").write_text("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
