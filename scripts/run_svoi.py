"""SVoI controller experiment (rows 10-11): decide now, or gather evidence?

1. Train the detector (default RAVEN-X-GF) on the train split.
2. On VALIDATION only: fit the temperature, the belief grid, p(b) per cell,
   and the passive-observation transitions; then solve the SVoI tables
   (Eqs. 12-17) up to the largest horizon.
3. On TEST: replay vehicle streams from evenly spaced start steps under five
   policies at each horizon H:
     SVoI          the solved policy
     Never-query   decide immediately (cost-optimal threshold, no evidence)
     Always-query  wait for the next message until the horizon, then decide
     Fixed-interval  wait every step, neighbour query (a2) every 2nd step
     Random        a random evidence action with probability 0.5, else decide
   and report F1 / precision / recall / PR-AUC of the final decisions, evidence
   cost, error cost, total cost, and how many observations were used.

Example:
  python scripts/run_svoi.py --data nextgen --root /data/NextGen/hw2
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ravenx import plots, svoi  # noqa: E402
from ravenx.calibration import fit_temperature, probs  # noqa: E402
from ravenx.experiment import make_model, to_markdown, write_json  # noqa: E402
from ravenx.metrics import pr_auc  # noqa: E402
from ravenx.pipeline import add_data_args, load_data  # noqa: E402

POLICIES = ["SVoI", "Never-query", "Always-query", "Fixed-interval", "Random"]
MODE = {"SVoI": "svoi", "Never-query": "never", "Always-query": "always",
        "Fixed-interval": "fixed", "Random": "random"}


def beliefs(model, data, idx, T):
    z = model.predict_logits(data, idx)
    return probs(z, T, "evidential")


def evaluate(policy, p, u, y, stream, pos, starts, H, mode, seed):
    rng = np.random.default_rng(seed)
    rows = []
    for i in starts:
        end = i + H + 1
        j = np.searchsorted(stream, stream[i], side="right")      # end of this stream
        sl = slice(i, min(end, j))
        rows.append(svoi.run_episode(policy, p[sl], u[sl], y[sl], H, rng, mode=mode))
    return pd.DataFrame(rows)


def summarise(ep):
    tp = int(((ep.reject == 1) & (ep.label == 1)).sum())
    fp = int(((ep.reject == 1) & (ep.label == 0)).sum())
    fn = int(((ep.reject == 0) & (ep.label == 1)).sum())
    prec = tp / max(tp + fp, 1)
    rec = tp / max(tp + fn, 1)
    return {
        "F1": 2 * prec * rec / max(prec + rec, 1e-12), "Precision": prec, "Recall": rec,
        "Accuracy": float((ep.reject == ep.label).mean()),
        "Evidence cost": ep.evidence_cost.mean(), "Error cost": ep.error_cost.mean(),
        "Total cost": ep.total_cost.mean(), "Observations": ep.observations.mean(),
        "Queries": ep.queries.mean(), "Decided at once (%)": 100 * (ep.queries == 0).mean(),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_data_args(ap)
    ap.add_argument("--model", default="RAVEN-X-GF")
    ap.add_argument("--C-FA", type=float, default=100.0, help="cost of accepting an attacker")
    ap.add_argument("--C-FR", type=float, default=20.0, help="cost of rejecting an honest vehicle")
    ap.add_argument("--gamma", type=float, default=1.0)
    ap.add_argument("--horizons", nargs="*", type=int, default=[1, 2, 3, 5])
    ap.add_argument("--p-bins", type=int, default=20)
    ap.add_argument("--u-bins", type=int, default=8)
    ap.add_argument("--n-min", type=int, default=20)
    ap.add_argument("--stride", type=int, default=10, help="start an episode every N steps of a stream")
    ap.add_argument("--epochs", type=int, default=15)
    ap.add_argument("--patience", type=int, default=3)
    ap.add_argument("--hidden", type=int, default=64)
    ap.add_argument("--batch-size", type=int, default=256)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--out", default="results/svoi")
    args = ap.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)

    _, data = load_data(args)
    va, te = data.idx("val"), data.idx("test")
    cache = out / "beliefs.npz"
    if cache.exists():
        z = np.load(cache)
        p_va, u_va, p_te, u_te, T = z["p_va"], z["u_va"], z["p_te"], z["u_te"], float(z["T"])
        print(f"Loaded beliefs from {cache} (T = {T:.3f})")
    else:
        model = make_model(args.model, args, args.seed)
        model.fit(data, data.idx("train"), va)
        z_va, z_te = model.predict_logits(data, va), model.predict_logits(data, te)
        T = fit_temperature(z_va, data.y[va], "evidential")
        p_va, u_va = probs(z_va, T, "evidential")
        p_te, u_te = probs(z_te, T, "evidential")
        np.savez(cache, p_va=p_va, u_va=u_va, p_te=p_te, u_te=u_te, T=T)
        print(f"Trained {args.model}; temperature T = {T:.3f} (fitted on validation)")

    # --- offline: everything below is fitted on VALIDATION only -------------
    st = data.steps
    grid = svoi.BeliefGrid.fit(p_va, u_va, args.p_bins, args.u_bins)
    P = {"a1": svoi.passive_transitions(grid, p_va, u_va, st["stream"].values[va], args.n_min)[0]}
    for a, r in svoi.DEFAULT_RHO.items():
        P[a] = svoi.check_transitions(grid, r)
    H_max = max(args.horizons)
    policy = svoi.solve(grid, P, svoi.DEFAULT_COST, H_max, args.C_FA, args.C_FR, args.gamma)
    boundary = args.C_FR / (args.C_FA + args.C_FR)
    print(f"Grid {grid.n_p} x {grid.n_u} = {grid.n_states} beliefs; decision boundary p = {boundary:.3f}")
    mix = {h: pd.Series([policy.actions[i] for i in policy.action[h]]).value_counts().to_dict()
           for h in range(1, H_max + 1)}
    write_json({"T": T, "C_FA": args.C_FA, "C_FR": args.C_FR, "gamma": args.gamma,
                "costs": svoi.DEFAULT_COST, "rho": svoi.DEFAULT_RHO, "grid": [grid.n_p, grid.n_u],
                "actions_per_horizon (cells)": mix}, out / "svoi_setup.json")

    # --- online: replay test vehicles -------------------------------------
    y_te = data.y[te]
    stream, pos = st["stream"].values[te], st["pos_in_stream"].values[te]
    starts = np.flatnonzero(pos % args.stride == 0)
    print(f"Replaying {len(starts):,} test episodes per policy and horizon")
    rows, hist = [], []
    for H in args.horizons:
        for name in POLICIES:
            ep = evaluate(policy, p_te, u_te, y_te, stream, pos, starts, H, MODE[name], args.seed)
            r = {"H": H, "Policy": name, **summarise(ep)}
            rows.append(r)
            if name == "SVoI":
                hist.append(ep.observations.value_counts().sort_index().rename(f"H={H}"))
            print(f"  H={H} {name:14s} F1 {r['F1']:.4f}  total cost {r['Total cost']:.3f}  "
                  f"evidence {r['Evidence cost']:.3f}  obs {r['Observations']:.2f}")
    res = pd.DataFrame(rows)
    res.to_csv(out / "svoi_results.csv", index=False)
    decided = pd.concat(hist, axis=1).fillna(0).astype(int)
    decided.index.name = "observations used"
    decided.to_csv(out / "svoi_observations_used.csv")

    # F1 vs evidence cost, one point per (policy, horizon)
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6, 4.2))
    for name in POLICIES:
        d = res[res.Policy == name]
        ax.plot(d["Evidence cost"], d["F1"], "o-", label=name)
    ax.set_xlabel("mean evidence cost per vehicle"); ax.set_ylabel("F1 of final decisions")
    ax.set_title("Decision quality vs evidence cost (test)"); ax.legend(fontsize=8)
    plots._save(fig, out / "f1_vs_evidence_cost.png")

    single_pr = pr_auc(y_te, p_te)
    cols = ["H", "Policy", "F1", "Precision", "Recall", "Evidence cost", "Error cost", "Total cost",
            "Observations", "Queries", "Decided at once (%)"]
    md = [f"# SVoI controller ({args.data} data)", "",
          f"Detector {args.model}, temperature T = {T:.3f} fitted on validation (single-step PR-AUC "
          f"of the calibrated belief on test: {single_pr:.4f}). Costs: C_FA = {args.C_FA:g}, "
          f"C_FR = {args.C_FR:g}; evidence a1..a4 = 1 / 2 / 3 / 5; check reliabilities "
          f"a2..a4 = 0.80 / 0.90 / 0.99 (assumed); gamma = {args.gamma:g}; criticality K = 1. "
          f"Grid, p(b), transitions and the policy are fitted on validation; "
          f"{len(starts):,} test episodes per row.", "",
          "Lower total cost is better (evidence spent + cost of wrong decisions).", "",
          to_markdown(res[cols], index=False), "",
          "## SVoI: vehicles decided after k observations", "", to_markdown(decided), ""]
    if args.data == "synthetic":
        md.insert(1, "> Synthetic data: pipeline check only, not a result.\n")
    (out / "report.md").write_text("\n".join(md))
    print("\n" + "\n".join(md))


if __name__ == "__main__":
    main()
