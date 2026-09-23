"""Experiment 1: misbehaviour / risk detection (plan phases 6-9).

Answers, on the official train / val / test split:
  Q1  can each model detect attacks at all?          (detection table)
  Q2  does temporal information help?                RF/XGBoost -> GRU
  Q3  does neighbour information help?               RF/XGBoost -> GAT
  Q4  does spatial + temporal help?                  GRU, GAT   -> RAVEN-X
  Q5  is the model trustworthy?                      ECE, Brier, reliability
  plus: TRUST / VERIFY / REJECT policy from risk + uncertainty and the
  attack-wise precision / recall / F1 for all 15 attack types.

Example:
  python scripts/run_exp1.py --data nextgen --root /data/VeReMi_NextGen \
      --attacks constantPositionOffset --out results/exp1_step1
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ravenx import plots  # noqa: E402
from ravenx.config import ATTACK_NAMES  # noqa: E402
from ravenx.decision import FIXED_POLICY, fit_policy, summarize  # noqa: E402
from ravenx.experiment import (add_train_args, fit_and_score, fmt_table,  # noqa: E402
                               mean_std_table, subsample, to_markdown, write_json)
from ravenx.graph import graph_stats  # noqa: E402
from ravenx.metrics import detection_metrics  # noqa: E402
from ravenx.pipeline import add_data_args, dataset_summary, load_data  # noqa: E402

DET_COLS = ["Accuracy", "Precision", "Recall", "F1", "ROC-AUC", "PR-AUC"]
CAL_COLS = ["ECE", "Brier"]


def comparisons(mean: pd.DataFrame) -> str:
    """Plain-language answers to Q2-Q4 from the mean table."""
    def get(m, c):
        return mean.loc[m, c] if m in mean.index else np.nan

    tab = [m for m in ("RandomForest", "XGBoost") if m in mean.index]
    best_tab = max(tab, key=lambda m: get(m, "F1")) if tab else None
    lines = ["## Research questions (test split)", ""]

    def cmp(q, base, new):
        if base is None or new not in mean.index or base not in mean.index:
            return
        df1 = get(new, "F1") - get(base, "F1")
        dpr = get(new, "PR-AUC") - get(base, "PR-AUC")
        lines.append(f"- {q}: {new} vs {base}: ΔF1 = {df1:+.4f}, ΔPR-AUC = {dpr:+.4f}")

    cmp("Q2 temporal information", best_tab, "GRU")
    cmp("Q3 neighbour information", best_tab, "GAT")
    for base in ("GRU", "GAT"):
        cmp("Q4 spatial + temporal", base, "RAVEN-X")
    if "GAT+GRU" in mean.index:
        cmp("Q4 (softmax ablation)", "GAT+GRU", "RAVEN-X")
    lines += ["", "Positive deltas mean the added information helped on this data. "
              "With several --seeds, check that the gap is larger than the std before "
              "claiming it."]
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_data_args(p)
    add_train_args(p)
    p.add_argument("--out", default="results/exp1")
    p.add_argument("--reject-precision", type=float, default=0.98)
    p.add_argument("--trust-miss", type=float, default=0.02)
    p.add_argument("--unc-quantile", type=float, default=0.90)
    args = p.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    torch.set_num_threads(max(1, torch.get_num_threads()))

    msgs, data = load_data(args)
    summary = dataset_summary(msgs, data)
    write_json(summary, out / "dataset_summary.json")
    graph_stats(data.steps, data.graph, data.group).to_csv(out / "graph_stats.csv", index=False)
    print(f"Messages {summary['messages']:,} | attack {summary['attack_percentage']:.1f}% | "
          f"steps {summary['steps']:,} | mean neighbours {summary['graph']['mean_avg_neighbors']:.2f}")

    tr_all, va, te = data.idx("train"), data.idx("val"), data.idx("test")
    y_te = data.y[te]
    rows, attack_rows, keep = [], [], {}
    for seed in args.seeds:
        tr = subsample(tr_all, args.max_train, seed)
        for name in args.models:
            print(f"\n== {name} (seed {seed}) ==")
            res = fit_and_score(name, data, tr, va, te, args, seed)
            m = res["metrics"]
            print("   " + "  ".join(f"{k} {m[k]:.4f}" for k in DET_COLS + CAL_COLS))
            rows.append({"Model": name, "Seed": seed, **m})
            r_te, u_te = res["test"]
            # attack-wise: each NextGen subset holds one attack type plus benign traffic
            for atk, sub in data.steps.iloc[te].groupby("attack_type").indices.items():
                mm = detection_metrics(y_te[sub], r_te[sub], res["threshold"])
                attack_rows.append({"Attack": ATTACK_NAMES.get(atk, atk), "Model": name, "Seed": seed,
                                    "Precision": mm["Precision"], "Recall": mm["Recall"],
                                    "F1": mm["F1"], "PR-AUC": mm["PR-AUC"],
                                    "attack_steps": int(y_te[sub].sum()), "steps": len(sub)})
            if seed == args.seeds[0]:
                keep[name] = res
                if name == "RAVEN-X":
                    torch.save({"state_dict": res["model"].net.state_dict(),
                                "hidden": args.hidden, "seq_len": args.seq_len,
                                "radius": args.radius, "bin": args.bin,
                                "norm_mu": data.normalizer.mu, "norm_sd": data.normalizer.sd},
                               out / "ravenx_model.pt")

    # ---- detection + calibration tables -----------------------------------
    pd.DataFrame(rows).to_csv(out / "detection_per_seed.csv", index=False)
    mean, std = mean_std_table(rows, cols=DET_COLS + CAL_COLS + ["TrainTime_s"])
    mean.to_csv(out / "detection_mean.csv"); std.to_csv(out / "detection_std.csv")
    det_md = to_markdown(fmt_table(mean[DET_COLS], std[DET_COLS]))
    cal_md = to_markdown(fmt_table(mean[CAL_COLS], std[CAL_COLS]))
    report = [f"# Experiment 1 — detection ({args.data} data)", "",
              f"Seeds: {args.seeds}. Thresholds chosen on validation (max F1), metrics on test.", "",
              det_md, "", "## Calibration (lower is better)", "", cal_md, "",
              comparisons(mean), ""]

    # ---- attack-wise --------------------------------------------------------
    aw = pd.DataFrame(attack_rows)
    aw.to_csv(out / "attackwise_per_seed.csv", index=False)
    aw_mean = aw.groupby(["Attack", "Model"], sort=False)[["Precision", "Recall", "F1", "PR-AUC"]].mean()
    f1_pivot = aw_mean["F1"].unstack("Model")[[m for m in args.models]]
    f1_pivot.to_csv(out / "attackwise_f1.csv")
    plots.attackwise_bars(f1_pivot, out / "attackwise_f1.png")
    if "RAVEN-X" in args.models:
        rx = aw_mean.xs("RAVEN-X", level="Model")[["Precision", "Recall", "F1"]]
        rx.to_csv(out / "attackwise_ravenx.csv")
        report += ["## Attack-wise (RAVEN-X, test)", "", to_markdown(rx.round(4)), ""]
    report += ["## Attack-wise F1, all models", "", to_markdown(f1_pivot.round(4)), ""]

    # ---- calibration figures -------------------------------------------------
    plots.reliability_diagram({n: (y_te, keep[n]["test"][0]) for n in keep}, out / "reliability_diagram.png")
    plots.risk_coverage({n: (y_te, *keep[n]["test"]) for n in keep}, out / "uncertainty_coverage.png")

    # ---- risk decision (RAVEN-X) -------------------------------------------
    if "RAVEN-X" in keep:
        res = keep["RAVEN-X"]
        r_va, u_va = res["val"]
        r_te, u_te = res["test"]
        policy = fit_policy(r_va, u_va, data.y[va], args.reject_precision,
                            args.trust_miss, args.unc_quantile)
        dec = policy.apply(r_te, u_te)
        tuned = summarize(dec, y_te)
        fixed = summarize(FIXED_POLICY.apply(r_te, u_te), y_te)
        tuned.to_csv(out / "decision_tuned.csv", index=False)
        fixed.to_csv(out / "decision_fixed_0.3_0.8.csv", index=False)
        write_json(policy.to_dict(), out / "decision_policy.json")
        plots.risk_distribution(r_te, y_te, out / "risk_distribution.png", policy)
        plots.uncertainty_distribution(u_te, y_te, (r_te >= res["threshold"]).astype(int) == y_te,
                                       out / "uncertainty_distribution.png", policy.u_max)
        plots.decision_scatter(r_te, u_te, y_te, policy, out / "risk_uncertainty_decision.png")

        # does uncertainty flag the mistakes? error rate per uncertainty quintile
        wrong = ((r_te >= res["threshold"]).astype(int) != y_te)
        q = pd.qcut(pd.Series(u_te).rank(method="first"), 5, labels=[f"Q{i}" for i in range(1, 6)])
        unc_err = pd.DataFrame({"quintile": q, "wrong": wrong, "u": u_te}).groupby("quintile", observed=True).agg(
            mean_uncertainty=("u", "mean"), error_rate=("wrong", "mean"), n=("wrong", "size"))
        unc_err.to_csv(out / "uncertainty_vs_error.csv")

        pred = data.steps.iloc[te][["run", "receiver", "alias", "bin", "attack_type", "label"]].copy()
        pred["risk"], pred["uncertainty"], pred["decision"] = r_te, u_te, dec
        pred.to_csv(out / "ravenx_test_predictions.csv.gz", index=False)

        report += ["## Risk decision policy (RAVEN-X)", "",
                   f"Fitted on validation: t_low = {policy.t_low:.3f}, t_high = {policy.t_high:.3f}, "
                   f"u_max = {policy.u_max:.4f} (reject precision ≥ {args.reject_precision}, "
                   f"attack share among TRUST ≤ {args.trust_miss}).", "",
                   to_markdown(tuned.round(4), index=False), "",
                   "Fixed initial levels (TRUST < 0.30, REJECT ≥ 0.80, no uncertainty):", "",
                   to_markdown(fixed.round(4), index=False), "",
                   "## Uncertainty vs error (RAVEN-X, test, quintiles of uncertainty)", "",
                   to_markdown(unc_err.round(4)), ""]

    if args.data == "synthetic":
        report.insert(1, "> Synthetic data: these numbers only show the pipeline works. "
                         "Do not report them as results.\n")
    (out / "report.md").write_text("\n".join(report))
    print("\n" + det_md + "\n\n" + cal_md + "\n\n" + comparisons(mean))
    print(f"\nWrote results to {out}/")


if __name__ == "__main__":
    main()
