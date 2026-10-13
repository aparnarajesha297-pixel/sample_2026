"""Row 14: sweep the attack / benign decision threshold.

Uses a trained detector's calibrated beliefs (the ``beliefs.npz`` written by
run_svoi.py: temperature-scaled P(attack) on validation and test). For every
threshold from 0.10 to 0.90 in steps of 0.10 it reports precision, recall,
F1, false-positive rate and false-negative rate on both splits. The final
threshold is the grid value with the highest VALIDATION F1; test numbers are
reported for it but never used to choose it.

Example:
  python scripts/run_threshold_sweep.py --data nextgen --root /data/NextGen/hw2 \
      --beliefs results/svoi_hw2/beliefs.npz
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ravenx import plots  # noqa: E402
from ravenx.experiment import to_markdown, write_json  # noqa: E402
from ravenx.metrics import best_threshold  # noqa: E402
from ravenx.pipeline import add_data_args, load_data  # noqa: E402


def rates(y, p, t):
    yhat = p >= t
    tp = int((yhat & (y == 1)).sum()); fp = int((yhat & (y == 0)).sum())
    fn = int((~yhat & (y == 1)).sum()); tn = int((~yhat & (y == 0)).sum())
    prec = tp / max(tp + fp, 1); rec = tp / max(tp + fn, 1)
    return {"Precision": prec, "Recall": rec, "F1": 2 * prec * rec / max(prec + rec, 1e-12),
            "FPR": fp / max(fp + tn, 1), "FNR": fn / max(fn + tp, 1)}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_data_args(ap)
    ap.add_argument("--beliefs", default="results/svoi_hw2/beliefs.npz")
    ap.add_argument("--out", default="results/threshold_sweep")
    args = ap.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)

    _, data = load_data(args)
    z = np.load(args.beliefs)
    p_va, p_te, T = z["p_va"], z["p_te"], float(z["T"])
    y_va, y_te = data.y[data.idx("val")], data.y[data.idx("test")]
    assert len(p_va) == len(y_va) and len(p_te) == len(y_te), "beliefs do not match this dataset"

    grid = np.round(np.arange(0.10, 0.901, 0.10), 2)
    rows = []
    for t in grid:
        rows.append({"Threshold": t, **{f"val {k}": v for k, v in rates(y_va, p_va, t).items()},
                     **{f"test {k}": v for k, v in rates(y_te, p_te, t).items()}})
    df = pd.DataFrame(rows)
    df.to_csv(out / "threshold_sweep.csv", index=False)
    t_sel = float(df.loc[df["val F1"].idxmax(), "Threshold"])
    t_cont = best_threshold(y_va, p_va)
    ref = {"grid choice (max validation F1)": t_sel,
           "continuous max-validation-F1 threshold": t_cont,
           "cost-based SVoI boundary C_FR/(C_FA+C_FR)": 20 / 120}
    summary = pd.DataFrame([{"Rule": k, "Threshold": v, **rates(y_te, p_te, v)} for k, v in ref.items()])
    write_json({"selected_threshold": t_sel, "temperature": T, **ref}, out / "threshold_choice.json")

    tp = df.rename(columns=lambda c: c.replace("test ", ""))
    plots.line_plot(grid, {k: tp[k] for k in ("Precision", "Recall", "F1")}, "threshold",
                    "score (test)", f"Precision / recall / F1 vs threshold (chosen {t_sel:.1f} on validation)",
                    out / "sweep_precision_recall_f1.png")
    plots.line_plot(grid, {"false-positive rate": tp["FPR"], "false-negative rate": tp["FNR"]},
                    "threshold", "rate (test)", "Error rates vs threshold", out / "sweep_error_rates.png")
    plots.line_plot(grid, {"validation F1": df["val F1"], "test F1": df["test F1"]}, "threshold", "F1",
                    "Validation vs test F1 (threshold chosen on validation)", out / "sweep_val_vs_test_f1.png")

    show = df[["Threshold"] + [f"test {k}" for k in ("Precision", "Recall", "F1", "FPR", "FNR")] + ["val F1"]]
    md = ["# Threshold sweep (row 14)", "",
          f"Beliefs: temperature-scaled P(attack) from `{args.beliefs}` (T = {T:.3f}, fitted on validation). "
          f"Threshold chosen on validation only: **{t_sel:.1f}**.", "",
          to_markdown(show, index=False), "",
          "## Chosen threshold vs other rules (test)", "", to_markdown(summary, index=False), ""]
    (out / "report.md").write_text("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
