"""Uncertainty of the evidential detector (RAVEN-X-GF by default).

Reads the calibrated beliefs that run_temperature_scaling.py saves per seed
(temperature fitted on validation; p = P(attack), u = evidential uncertainty
2 / S) and asks whether u is useful:

  1. error rate per uncertainty quintile (errors at the validation-chosen
     F1 threshold);
  2. how well u ranks the model's own errors (AUROC), against the simplest
     alternative that needs no uncertainty head: closeness of p to the
     threshold (1 - |p - thr| scaled);
  3. selective prediction: set aside the most uncertain x% for verification
     and score the decisions on the rest (and the same with the margin
     instead of u);
  4. mean u and error rate per attack type;
  5. the TRUST / VERIFY / REJECT policy (ravenx.decision, fitted on
     validation with run_exp1's defaults) on these calibrated outputs.

Example:
  python scripts/run_uncertainty.py --data nextgen --root /data/NextGen/hw2 \
      --beliefs-dir results/temperature_scaling_nbr
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ravenx import plots  # noqa: E402
from ravenx.config import ATTACK_NAMES  # noqa: E402
from ravenx.decision import fit_policy, summarize  # noqa: E402
from ravenx.experiment import to_markdown  # noqa: E402
from ravenx.pipeline import add_data_args, load_data  # noqa: E402

COVERAGE_DROP = [0, 5, 10, 20, 30]


def f1(y, yhat):
    tp, fp, fn = (yhat & (y == 1)).sum(), (yhat & (y == 0)).sum(), (~yhat & (y == 1)).sum()
    return 2 * tp / max(2 * tp + fp + fn, 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_data_args(ap)
    ap.add_argument("--model", default="RAVEN-X-GF")
    ap.add_argument("--beliefs-dir", default="results/temperature_scaling_nbr")
    ap.add_argument("--reject-precision", type=float, default=0.98)
    ap.add_argument("--trust-miss", type=float, default=0.02)
    ap.add_argument("--unc-quantile", type=float, default=0.90)
    ap.add_argument("--out", default="results/uncertainty")
    args = ap.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)

    _, data = load_data(args)
    va, te = data.idx("val"), data.idx("test")
    y_va, y_te = data.y[va], data.y[te]
    attack = data.steps["attack_type"].astype(str).values[te]
    files = sorted(Path(args.beliefs_dir).glob(f"beliefs_{args.model}_seed*.npz"))
    if not files:
        raise SystemExit(f"no beliefs_{args.model}_seed*.npz in {args.beliefs_dir}")

    quint, auroc, sel, per_attack, dec_rows = [], [], [], [], []
    for f in files:
        seed = int(f.stem.split("seed")[-1])
        z = np.load(f)
        p_va, u_va, p, u, thr = z["p_va"], z["u_va"], z["p_te"], z["u_te"], float(z["thr"])
        assert len(p) == len(te), "beliefs do not match this dataset"
        yhat = p >= thr
        wrong = yhat != (y_te == 1)
        margin = -np.abs(p - thr)                     # higher = closer to the threshold
        q = pd.qcut(pd.Series(u).rank(method="first"), 5, labels=[f"Q{i}" for i in range(1, 6)])
        t = pd.DataFrame({"q": q, "u": u, "wrong": wrong}).groupby("q", observed=True).agg(
            mean_u=("u", "mean"), error_rate=("wrong", "mean"))
        t["Seed"] = seed
        quint.append(t.reset_index())
        auroc.append({"Seed": seed, "AUROC uncertainty → error": roc_auc_score(wrong, u),
                      "AUROC margin → error": roc_auc_score(wrong, margin),
                      "AUROC u among honest": roc_auc_score(wrong[y_te == 0], u[y_te == 0]),
                      "AUROC u among attacks": roc_auc_score(wrong[y_te == 1], u[y_te == 1]),
                      "error rate": wrong.mean()})
        for drop in COVERAGE_DROP:
            for by, score in (("uncertainty", u), ("margin", margin)):
                # exactly drop% set aside, most uncertain first (ties broken by position)
                rank = np.argsort(np.argsort(-score, kind="stable"), kind="stable")
                keep = rank >= int(round(drop / 100 * len(u)))
                sel.append({"Seed": seed, "Set aside by": by, "Set aside (%)": drop,
                            "F1 on rest": f1(y_te[keep], yhat[keep]), "Error rate on rest": wrong[keep].mean(),
                            "Attacks set aside (%)": 100 * (~keep & (y_te == 1)).sum() / max((y_te == 1).sum(), 1)})
        a = pd.DataFrame({"attack": np.where(y_te == 1, attack, "benign"), "u": u, "wrong": wrong})
        a = a.groupby("attack").agg(mean_u=("u", "mean"), error_rate=("wrong", "mean"), n=("u", "size"))
        a["Seed"] = seed
        per_attack.append(a.reset_index())
        pol = fit_policy(p_va, u_va, y_va, args.reject_precision, args.trust_miss, args.unc_quantile)
        s = summarize(pol.apply(p, u), y_te)
        s["Seed"], s["t_low"], s["t_high"], s["u_max"] = seed, pol.t_low, pol.t_high, pol.u_max
        dec_rows.append(s)
        if f == files[0]:
            plots.uncertainty_distribution(u, y_te, ~wrong, out / "uncertainty_distribution.png", pol.u_max)
            plots.decision_scatter(p, u, y_te, pol, out / "risk_uncertainty_decision.png")

    def ms(df, by, cols):
        g = df.groupby(by, sort=False)[cols]
        m, s = g.mean(), g.std().fillna(0.0)
        r = m.copy().astype(object)
        for c in cols:
            r[c] = [f"{a:.4f} ± {b:.4f}" if len(files) > 1 else f"{a:.4f}" for a, b in zip(m[c], s[c])]
        return r, m

    seeds = sorted(int(f.stem.split("seed")[-1]) for f in files)
    Q, _ = ms(pd.concat(quint), "q", ["mean_u", "error_rate"])
    A = pd.DataFrame(auroc)
    Au, Am = ms(A.assign(k="all"), "k", [c for c in A.columns if c != "Seed"])
    S = pd.concat([pd.DataFrame(sel)])
    Sm, Smean = ms(S, ["Set aside by", "Set aside (%)"], ["F1 on rest", "Error rate on rest", "Attacks set aside (%)"])
    P, Pm = ms(pd.concat(per_attack), "attack", ["mean_u", "error_rate"])
    P = P.loc[Pm.sort_values("mean_u", ascending=False).index]
    P.index = [ATTACK_NAMES.get(i, i) for i in P.index]
    D, _ = ms(pd.concat(dec_rows), "decision", ["share", "attack_rate_in_bucket", "share_of_all_attacks",
                                                "share_of_all_benign"])
    pol_m = pd.concat(dec_rows).groupby("Seed")[["t_low", "t_high", "u_max"]].first().mean()
    for name, df in (("quintiles", Q), ("auroc", Au), ("selective", Sm), ("per_attack", P), ("decision", D)):
        df.to_csv(out / f"uncertainty_{name}.csv")
    A.to_csv(out / "uncertainty_auroc_per_seed.csv", index=False)
    plots.line_plot(COVERAGE_DROP, {f"set aside by {b}": Smean.xs(b, level=0)["F1 on rest"]
                                    for b in ("uncertainty", "margin")},
                    "share set aside for verification (%)", "F1 on the remaining steps",
                    f"{args.model}: selective prediction (test)", out / "selective_f1.png")

    md = [f"# Uncertainty of {args.model}", "",
          f"Seeds {seeds}. Calibrated beliefs from `{args.beliefs_dir}` (temperature fitted on validation). "
          "u = evidential uncertainty 2/S. Errors are at the validation-chosen F1 threshold. Test split.", "",
          "## Error rate by uncertainty quintile", "", to_markdown(Q), "",
          "## How well uncertainty ranks the model's own errors", "",
          "'margin' = closeness of the belief to the threshold, which needs no uncertainty head.", "",
          to_markdown(Au), "",
          "## Selective prediction: set aside the most uncertain steps for verification", "", to_markdown(Sm), "",
          "## Uncertainty and errors by attack type (sorted by mean u)", "", to_markdown(P), "",
          "## TRUST / VERIFY / REJECT on calibrated outputs", "",
          f"Fitted on validation per seed (mean thresholds: t_low = {pol_m.t_low:.3f}, t_high = {pol_m.t_high:.3f}, "
          f"u_max = {pol_m.u_max:.4f}; reject precision ≥ {args.reject_precision}, attack share among TRUST ≤ "
          f"{args.trust_miss}, u above its validation {args.unc_quantile:.0%} quantile → VERIFY).", "",
          to_markdown(D), ""]
    (out / "report.md").write_text("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
