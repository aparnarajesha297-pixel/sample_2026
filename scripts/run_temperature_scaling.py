"""Temperature scaling for the neural detectors (post-hoc calibration).

  1. train the model normally (train split, early stopping on validation);
  2. learn one temperature T on the VALIDATION split by minimising NLL;
  3. apply that T unchanged to the TEST logits and report before / after.

The decision threshold (max F1) is also re-chosen on validation after
scaling, so no test label touches T or the threshold.

Example:
  python scripts/run_temperature_scaling.py --data nextgen \
      --root /data/NextGen/hw2 --models RAVEN-X-GF --seeds 0 1 2
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ravenx import plots  # noqa: E402
from ravenx.calibration import fit_temperature, nll, probs  # noqa: E402
from ravenx.experiment import (add_train_args, make_model, subsample,  # noqa: E402
                               to_markdown, write_json)
from ravenx.metrics import best_threshold, detection_metrics  # noqa: E402
from ravenx.models.train import MODEL_SPECS  # noqa: E402
from ravenx.pipeline import add_data_args, load_data  # noqa: E402

COLS = ["ECE", "Brier", "NLL", "F1", "Precision", "Recall", "PR-AUC", "ROC-AUC"]


def score(y, p, thr):
    m = detection_metrics(y, p, thr)
    m["NLL"] = nll(y, p)
    return {c: m[c] for c in COLS}


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_data_args(p)
    add_train_args(p)
    p.set_defaults(models=["RAVEN-X-GF"])
    p.add_argument("--out", default="results/temperature_scaling")
    args = p.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    bad = [m for m in args.models if m not in MODEL_SPECS]
    if bad:
        raise SystemExit(f"temperature scaling needs logits; not a neural model: {bad}")

    _, data = load_data(args)
    va, te = data.idx("val"), data.idx("test")
    y_va, y_te = data.y[va], data.y[te]
    rows, curves = [], {}
    for seed in args.seeds:
        tr = subsample(data.idx("train"), args.max_train, seed)
        for name in args.models:
            print(f"\n== {name} (seed {seed}) ==")
            model = make_model(name, args, seed)
            model.fit(data, tr, va)
            z_va, z_te = model.predict_logits(data, va), model.predict_logits(data, te)
            native = "evidential" if model.net.evidential else "softmax"
            modes = [native] + (["softmax"] if native == "evidential" else [])
            for mode in modes:
                # before: T = 1, threshold from validation
                p_va, _ = probs(z_va, 1.0, mode)
                p_te, _ = probs(z_te, 1.0, mode)
                before = score(y_te, p_te, best_threshold(y_va, p_va))
                # learn T on validation only, then apply it to test
                T = fit_temperature(z_va, y_va, mode)
                p_va_T, _ = probs(z_va, T, mode)
                p_te_T, _ = probs(z_te, T, mode)
                after = score(y_te, p_te_T, best_threshold(y_va, p_va_T))
                label = f"{name} [{mode}]"
                print(f"   {mode:10s} T = {T:.3f}   ECE {before['ECE']:.4f} -> {after['ECE']:.4f}   "
                      f"Brier {before['Brier']:.4f} -> {after['Brier']:.4f}   "
                      f"F1 {before['F1']:.4f} -> {after['F1']:.4f}")
                rows.append({"Model": label, "Seed": seed, "T": T,
                             **{f"{k} before": v for k, v in before.items()},
                             **{f"{k} after": v for k, v in after.items()}})
                if seed == args.seeds[0]:
                    curves[f"{label} before"] = (y_te, p_te)
                    curves[f"{label} after (T={T:.2f})"] = (y_te, p_te_T)

    df = pd.DataFrame(rows)
    df.to_csv(out / "temperature_per_seed.csv", index=False)
    g = df.groupby("Model", sort=False)
    mean, std = g.mean(numeric_only=True), g.std(numeric_only=True).fillna(0.0)
    summary = []
    for model in mean.index:
        r = {"Model": model, "T": f"{mean.loc[model, 'T']:.3f} ± {std.loc[model, 'T']:.3f}"}
        for c in COLS:
            for when in ("before", "after"):
                k = f"{c} {when}"
                r[k] = f"{mean.loc[model, k]:.4f} ± {std.loc[model, k]:.4f}"
        summary.append(r)
    sm = pd.DataFrame(summary).set_index("Model")
    sm.to_csv(out / "temperature_summary.csv")
    write_json({m: float(mean.loc[m, "T"]) for m in mean.index}, out / "temperatures.json")
    plots.reliability_diagram(curves, out / "reliability_before_after.png")

    main_cols = ["T"] + [f"{c} {w}" for c in ("ECE", "Brier", "NLL", "F1") for w in ("before", "after")]
    md = ["# Temperature scaling", "",
          f"Data: {args.data}. Seeds: {args.seeds}. T learned on the validation split "
          "(min NLL) and applied unchanged to test; F1 threshold re-chosen on validation.", "",
          to_markdown(sm[main_cols]), "",
          "## Other metrics", "", to_markdown(sm[[f"{c} {w}" for c in ("Precision", "Recall", "PR-AUC", "ROC-AUC")
                                                 for w in ("before", "after")]]), ""]
    (out / "report.md").write_text("\n".join(md))
    print("\n" + "\n".join(md))


if __name__ == "__main__":
    main()
