"""Row 15: mobility-aware planning horizon for the SVoI controller.

1. How well can "time left before the vehicle disappears" be estimated at
   runtime? Target: seconds from a step to the last step of its stream. The
   estimators (constant, age, geometric; see ravenx/mobility.py) are fitted on
   VALIDATION and scored on TEST with MAE / RMSE / bias.
2. Does capping the planning horizon with that estimate help? SVoI is replayed
   on test with a fixed horizon H and with H_v(t) = min(H, estimated steps
   left), for every estimator, plus the true steps left as an oracle upper
   bound (not deployable: on this data it leaks the Sybil label).
3. The median (q = 0.5) turns out to cut the horizon to zero for every new
   stream, because most one-message streams are Sybil ghosts. An estimate
   that is too short is costly and one that is too long is free, so the
   quantile q in {0.5, 0.75, 0.9}, a minimum cap in {0, 1} and the estimator
   (age, geometric) are chosen per H and evidence set by total cost on a
   VALIDATION replay, and only that choice is scored on test.

Beliefs come from run_svoi.py (temperature-scaled RAVEN-X-GF on validation and
test), so no detector is retrained.

Example:
  python scripts/run_horizon.py --data nextgen --root /data/NextGen/hw2 \
      --beliefs results/svoi_hw2/beliefs.npz
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from ravenx import mobility, plots, svoi  # noqa: E402
from ravenx.experiment import to_markdown, write_json  # noqa: E402
from ravenx.metrics import pr_auc  # noqa: E402
from ravenx.pipeline import add_data_args, load_data  # noqa: E402
from run_svoi import summarise  # noqa: E402

PROXIES = ["constant", "age", "geometric"]
EVIDENCE_SETS = {"a1-a4": list(svoi.EVIDENCE), "a1 only": ["a1"]}


def replay(policy, p, u, y, stream, starts, H, cap=None, seed=0):
    rng = np.random.default_rng(seed)
    rows = []
    for i in starts:
        j = min(i + H + 1, np.searchsorted(stream, stream[i], side="right"))
        rows.append(svoi.run_episode(policy, p[i:j], u[i:j], y[i:j], H, rng, mode="svoi",
                                     h_cap=None if cap is None else cap[i:j]))
    return pd.DataFrame(rows)


def error_table(truth, est, label):
    rows = []
    for name, e in est.items():
        for part, m in (("all", np.ones_like(label, bool)), ("benign", label == 0),
                        ("attacker", label == 1), ("true time left ≤ 10 s", truth <= 10)):
            d = e[m] - truth[m]
            rows.append({"Estimator": name, "Steps": part, "MAE (s)": np.abs(d).mean(),
                         "RMSE (s)": np.sqrt((d ** 2).mean()), "Bias (s)": d.mean(), "n": int(m.sum())})
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_data_args(ap)
    ap.add_argument("--beliefs", default="results/svoi_hw2/beliefs.npz")
    ap.add_argument("--horizons", nargs="*", type=int, default=[1, 2, 3, 5, 10])
    ap.add_argument("--stride", type=int, default=10)
    ap.add_argument("--C-FA", type=float, default=100.0)
    ap.add_argument("--C-FR", type=float, default=20.0)
    ap.add_argument("--quantiles", nargs="*", type=float, default=[0.5, 0.75, 0.9])
    ap.add_argument("--min-caps", nargs="*", type=int, default=[0, 1])
    ap.add_argument("--out", default="results/horizon")
    args = ap.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)

    _, data = load_data(args)
    st = data.steps
    va, te = data.idx("val"), data.idx("test")
    z = np.load(args.beliefs)
    p_va, u_va, p_te, u_te = z["p_va"], z["u_va"], z["p_te"], z["u_te"]
    assert len(p_va) == len(va) and len(p_te) == len(te), "beliefs do not match this dataset"
    s_va, s_te = st.iloc[va], st.iloc[te]
    stream_te = s_te["stream"].to_numpy()
    assert (np.diff(stream_te) >= 0).all(), "test steps must be ordered by stream"
    y_te = data.y[te]

    # 1. time-left estimators: fitted on validation, scored on test
    proxy = mobility.HorizonProxy.fit(s_va)
    truth = np.minimum(mobility.time_left(s_te), mobility.MAX_S)
    est = proxy.predict(s_te)
    err = error_table(truth, est, y_te)
    err.to_csv(out / "time_left_errors.csv", index=False)
    rate = mobility.range_rate(s_te)
    receding = np.nan_to_num(rate, nan=0.0) > proxy.min_rate
    print(f"R = {proxy.R:.0f} m, constant = {proxy.constant:.1f} s, receding steps {receding.mean():.1%}")

    # 2. fixed vs mobility-aware horizon
    caps = {name: mobility.horizon_cap(e) for name, e in est.items()}
    caps["oracle (true steps left)"] = mobility.steps_left(s_te)
    starts = np.flatnonzero(s_te["pos_in_stream"].to_numpy() % args.stride == 0)
    H_max = max(args.horizons)
    rows = []
    for ev_name, ev in EVIDENCE_SETS.items():
        policy = svoi.fit_policy(p_va, u_va, s_va["stream"].to_numpy(), H_max, ev, args.C_FA, args.C_FR)
        for H in args.horizons:
            for name, cap in [("fixed H", None)] + list(caps.items()):
                ep = replay(policy, p_te, u_te, y_te, stream_te, starts, H, cap)
                shrunk = float("nan") if cap is None else float((cap[starts] < H).mean() * 100)
                r = {"Evidence": ev_name, "H": H, "Horizon": name, **summarise(ep),
                     "PR-AUC": pr_auc(ep.label.to_numpy(), ep.p_final.to_numpy()),
                     "Horizon shrunk at start (%)": shrunk}
                rows.append(r)
                print(f"  {ev_name:7s} H={H:2d} {name:26s} F1 {r['F1']:.4f}  total {r['Total cost']:.3f}  "
                      f"evidence {r['Evidence cost']:.3f}  obs {r['Observations']:.2f}", flush=True)
    # 3. estimator, quantile and minimum cap chosen on a VALIDATION replay
    stream_va = s_va["stream"].to_numpy()
    assert (np.diff(stream_va) >= 0).all(), "validation steps must be ordered by stream"
    starts_va = np.flatnonzero(s_va["pos_in_stream"].to_numpy() % args.stride == 0)
    y_va = data.y[va]
    fitted = {q: mobility.HorizonProxy.fit(s_va, q) for q in args.quantiles}
    est_va = {q: f.predict(s_va) for q, f in fitted.items()}
    est_te = {q: f.predict(s_te) for q, f in fitted.items()}
    sel_rows = []
    for ev_name, ev in EVIDENCE_SETS.items():
        policy = svoi.fit_policy(p_va, u_va, stream_va, H_max, ev, args.C_FA, args.C_FR)
        for H in args.horizons:
            cand = []
            for q in args.quantiles:
                for est_name in ("age", "geometric"):
                    for mc in args.min_caps:
                        cap = mobility.horizon_cap(est_va[q][est_name], mc)
                        ep = replay(policy, p_va, u_va, y_va, stream_va, starts_va, H, cap)
                        cand.append((summarise(ep)["Total cost"], q, est_name, mc))
            base_va = summarise(replay(policy, p_va, u_va, y_va, stream_va, starts_va, H))["Total cost"]
            cost_va, q, est_name, mc = min(cand)
            name = f"validation-chosen ({est_name}, q = {q:g}, min cap {mc})"
            cap = mobility.horizon_cap(est_te[q][est_name], mc)
            ep = replay(policy, p_te, u_te, y_te, stream_te, starts, H, cap)
            r = {"Evidence": ev_name, "H": H, "Horizon": name, **summarise(ep),
                 "PR-AUC": pr_auc(ep.label.to_numpy(), ep.p_final.to_numpy()),
                 "Horizon shrunk at start (%)": float((cap[starts] < H).mean() * 100)}
            rows.append(r)
            sel_rows.append({"Evidence": ev_name, "H": H, "Estimator": est_name, "q": q, "Min cap": mc,
                             "Validation total cost": cost_va, "Validation total cost, fixed H": base_va})
            print(f"  {ev_name:7s} H={H:2d} {name:48s} F1 {r['F1']:.4f}  total {r['Total cost']:.3f}  "
                  f"(validation {cost_va:.3f} vs fixed {base_va:.3f})", flush=True)
            # oracle with the same minimum cap, for reference
            if mc > 0:
                cap = mobility.horizon_cap(mobility.steps_left(s_te), mc)
                ep = replay(policy, p_te, u_te, y_te, stream_te, starts, H, cap)
                rows.append({"Evidence": ev_name, "H": H, "Horizon": f"oracle, min cap {mc}", **summarise(ep),
                             "PR-AUC": pr_auc(ep.label.to_numpy(), ep.p_final.to_numpy()),
                             "Horizon shrunk at start (%)": float((cap[starts] < H).mean() * 100)})
    sel = pd.DataFrame(sel_rows)
    sel.to_csv(out / "validation_choice.csv", index=False)
    res = pd.DataFrame(rows)
    res.to_csv(out / "horizon_results.csv", index=False)

    import matplotlib.pyplot as plt
    for ev_name in EVIDENCE_SETS:
        fig, ax = plt.subplots(figsize=(6, 4.2))
        for name in res.Horizon.unique():
            d = res[(res.Evidence == ev_name) & (res.Horizon == name)]
            if len(d) < 2 and name.startswith(("validation", "oracle,")):
                continue
            ax.plot(d["Evidence cost"], d["F1"], "o-", label=name)
        ax.set_xlabel("mean evidence cost per vehicle"); ax.set_ylabel("F1 of final decisions")
        ax.set_title(f"Fixed vs mobility-aware horizon ({ev_name}; H = {', '.join(map(str, args.horizons))})")
        ax.legend(fontsize=8)
        plots._save(fig, out / f"f1_vs_cost_{ev_name.replace(' ', '_')}.png")

    # headline: change vs fixed H, per horizon
    base = res[res.Horizon == "fixed H"].set_index(["Evidence", "H"])
    delta = res[res.Horizon != "fixed H"].copy()
    for c in ("F1", "Total cost", "Evidence cost"):
        delta[f"Δ{c}"] = delta[c].to_numpy() - base.loc[list(zip(delta.Evidence, delta.H)), c].to_numpy()
    write_json({"R_m": proxy.R, "constant_s": proxy.constant, "age_median_s": proxy.by_age.tolist(),
                "receding_share_test": float(receding.mean())}, out / "horizon_setup.json")

    cols = ["Evidence", "H", "Horizon", "F1", "Precision", "Recall", "PR-AUC", "Evidence cost",
            "Error cost", "Total cost", "Observations", "Horizon shrunk at start (%)"]
    md = ["# Mobility-aware planning horizon (row 15)", "",
          f"Beliefs: `{args.beliefs}`. Estimators and SVoI tables fitted on validation; "
          f"{len(starts):,} test episodes per row. Range R = {proxy.R:.0f} m (99th percentile of "
          f"receiver distance on validation); {receding.mean():.1%} of test steps have a receding sender.",
          "", "## 1. Estimating time left (test, seconds, capped at "
          f"{mobility.MAX_S:.0f} s)", "", to_markdown(err, index=False), "",
          "## 2. Fixed vs mobility-aware horizon (test)", "",
          "The oracle uses the true steps left in the stream. It is an upper bound only: it is not "
          "available at runtime and it leaks the label (one-message streams are almost all Sybil ghosts).",
          "", to_markdown(res[cols], index=False), "",
          "## Validation choice", "",
          "Chosen per H and evidence set by the lowest total cost on a validation replay; the test "
          "rows above labelled 'validation-chosen' use exactly this choice.", "",
          to_markdown(sel, index=False), "",
          "## Change vs fixed H", "",
          to_markdown(delta[["Evidence", "H", "Horizon", "ΔF1", "ΔTotal cost", "ΔEvidence cost"]], index=False), ""]
    (out / "report.md").write_text("\n".join(md))
    print("\n" + "\n".join(md))


if __name__ == "__main__":
    main()
