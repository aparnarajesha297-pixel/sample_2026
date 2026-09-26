"""Merge Experiment 1 runs over many seeds and test whether the gaps are real.

Reads ``detection_per_seed.csv`` (and ``attackwise_per_seed.csv``) from each
given result folder, keeps one row per (model, seed), and reports:

  * mean ± std, 95 % confidence interval of the mean, and min–max per model;
  * paired comparisons of a reference model against every other model,
    matched by seed: mean difference with its 95 % CI, paired t-test,
    Wilcoxon signed-rank test, and how many seeds the reference won;
  * attack-wise F1 mean ± std.

Example:
  python scripts/aggregate_seeds.py results/nextgen_step3_v3/exp1 results/seeds10/seed_* \
      --reference RAVEN-X-GF --out reports/final_10seeds
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ravenx.experiment import to_markdown  # noqa: E402

METRICS = ["Accuracy", "Precision", "Recall", "F1", "ROC-AUC", "PR-AUC", "ECE", "Brier"]
LOWER_IS_BETTER = {"ECE", "Brier"}


def load(dirs, name):
    frames = []
    for d in dirs:
        f = Path(d) / name
        if f.exists():
            frames.append(pd.read_csv(f))
    if not frames:
        raise SystemExit(f"no {name} found in {dirs}")
    df = pd.concat(frames, ignore_index=True)
    keys = [c for c in ("Attack", "Model", "Seed") if c in df.columns]
    dup = df.duplicated(keys, keep="last")
    if dup.any():
        print(f"note: {dup.sum()} duplicate rows in {name} (same model and seed); keeping the last")
    return df[~dup]


def ci95(x):
    x = np.asarray(x, float)
    if len(x) < 2:
        return (np.nan, np.nan)
    h = stats.t.ppf(0.975, len(x) - 1) * x.std(ddof=1) / np.sqrt(len(x))
    return (x.mean() - h, x.mean() + h)


def summary_table(det, models):
    rows = []
    for m in models:
        d = det[det["Model"] == m]
        r = {"Model": m, "seeds": len(d)}
        for c in METRICS:
            r[c] = f"{d[c].mean():.4f} ± {d[c].std(ddof=1):.4f}"
        lo, hi = ci95(d["F1"])
        r["F1 95% CI"] = f"[{lo:.4f}, {hi:.4f}]"
        r["F1 min–max"] = f"{d['F1'].min():.4f} – {d['F1'].max():.4f}"
        rows.append(r)
    return pd.DataFrame(rows).set_index("Model")


def paired(det, ref, others, metric):
    rows = []
    a = det[det["Model"] == ref].set_index("Seed")[metric]
    for m in others:
        b = det[det["Model"] == m].set_index("Seed")[metric]
        seeds = a.index.intersection(b.index)
        if len(seeds) < 2:
            continue
        diff = (a[seeds] - b[seeds]).values
        if metric in LOWER_IS_BETTER:
            diff = -diff                      # positive = reference is better
        lo, hi = ci95(diff)
        t_p = stats.ttest_rel(a[seeds], b[seeds]).pvalue
        try:
            w_p = stats.wilcoxon(diff).pvalue if np.any(diff != 0) else 1.0
        except ValueError:
            w_p = np.nan
        rows.append({
            "vs": m, "seeds": len(seeds),
            f"Δ{metric} (ref − other)": f"{diff.mean():+.4f}",
            "95% CI of Δ": f"[{lo:+.4f}, {hi:+.4f}]",
            "ref wins": f"{int((diff > 0).sum())}/{len(seeds)}",
            "paired t p": f"{t_p:.2g}",
            "Wilcoxon p": f"{w_p:.2g}",
            "significant (p<0.05, both)": "yes" if (t_p < 0.05 and w_p < 0.05 and diff.mean() > 0) else "no",
        })
    return pd.DataFrame(rows)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("dirs", nargs="+", help="result folders written by run_exp1.py")
    p.add_argument("--reference", default="RAVEN-X-GF")
    p.add_argument("--out", default="results/aggregate")
    args = p.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)

    det = load(args.dirs, "detection_per_seed.csv")
    det.to_csv(out / "detection_all_seeds.csv", index=False)
    order = ["RandomForest", "XGBoost", "GRU", "GAT", "GAT+GRU", "RAVEN-X", "RAVEN-X-GF"]
    models = [m for m in order if m in set(det["Model"])] + \
             sorted(set(det["Model"]) - set(order))
    seeds = sorted(int(s) for s in det["Seed"].unique())
    others = [m for m in models if m != args.reference]

    summ = summary_table(det, models)
    summ.to_csv(out / "summary.csv")
    md = [f"# Experiment 1 over {len(seeds)} seeds", "",
          f"Seeds: {seeds}. Each seed retrains every model from scratch; thresholds are chosen "
          "on validation, metrics are on the test split.", "",
          "## Detection (mean ± std over seeds)", "",
          to_markdown(summ[["seeds"] + METRICS[:6]]), "",
          "## F1 stability and calibration", "",
          to_markdown(summ[["F1 95% CI", "F1 min–max", "ECE", "Brier"]]), ""]

    for metric in ("F1", "PR-AUC", "ROC-AUC", "ECE"):
        pt = paired(det, args.reference, others, metric)
        if len(pt):
            pt.to_csv(out / f"paired_{metric}.csv", index=False)
            md += [f"## Paired comparison on {metric}: {args.reference} vs each model", "",
                   ("Positive Δ = the reference is better" +
                    (" (for ECE, lower is better, so Δ is other − ref)." if metric in LOWER_IS_BETTER else ".")),
                   "", to_markdown(pt, index=False), ""]

    try:
        aw = load(args.dirs, "attackwise_per_seed.csv")
        g = aw.groupby(["Attack", "Model"])["F1"]
        tab = (g.mean().round(3).astype(str) + " ± " + g.std(ddof=1).round(3).astype(str)).unstack("Model")
        tab = tab[[m for m in models if m in tab.columns]]
        tab.to_csv(out / "attackwise_f1.csv")
        md += ["## Attack-wise F1 (mean ± std over seeds)", "", to_markdown(tab), ""]
    except SystemExit:
        pass

    (out / "report.md").write_text("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
