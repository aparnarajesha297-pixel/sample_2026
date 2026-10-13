"""Row 16: criticality multiplier for the SVoI controller.

A wrong decision should cost more when something risky is happening nearby.
The data has no event flag, so a step is critical when the sender is within
d_max of the receiver and closing in with time to collision below ttc_max
(ravenx/mobility.py). Critical steps get stop costs multiplied by Cm
(Eqs. 12-13); one SVoI table is solved per level on VALIDATION.

Cm = 1 is the controller without the multiplier. Because Cm scales both
stop costs, accept vs reject at the moment of stopping never changes; the
multiplier only makes the controller buy more evidence before deciding on
critical steps. For each weight W the controller without the multiplier
(Cm = 1 everywhere) and with it (Cm = W on critical steps) are scored on the
same objective, where an error on a critical step costs W times more.
Reported on test for all episodes and split by whether the episode starts
on a critical step: F1 / PR-AUC of the final decisions, evidence cost, plain
and weighted error cost.

Example:
  python scripts/run_criticality.py --data nextgen --root /data/NextGen/hw2 \
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

EVIDENCE_SETS = {"a1-a4": list(svoi.EVIDENCE), "a1 only": ["a1"]}


def replay(policies, p, u, y, crit, stream, starts, H, seed=0):
    rng = np.random.default_rng(seed)
    rows = []
    for i in starts:
        j = min(i + H + 1, np.searchsorted(stream, stream[i], side="right"))
        rows.append(svoi.run_episode(policies[1.0], p[i:j], u[i:j], y[i:j], H, rng, mode="svoi",
                                     crit=crit[i:j], crit_policies=policies))
    ep = pd.DataFrame(rows)
    ep["decided_at"] = starts + ep.observations.to_numpy() - 1     # test step of the decision
    return ep


def scores(ep, flag, W):
    """Detection and cost of one set of episodes. Weighted error cost: an
    error on a critical step costs W times more (same W for the controller
    with and without the multiplier, so the two compare)."""
    s = summarise(ep)
    werr = ep.error_cost.to_numpy() * np.where(flag[ep.decided_at.to_numpy()], W, 1.0)
    return {"F1": s["F1"], "Precision": s["Precision"], "Recall": s["Recall"],
            "PR-AUC": pr_auc(ep.label.to_numpy(), ep.p_final.to_numpy()) if ep.label.nunique() > 1 else float("nan"),
            "Queries": s["Queries"], "Evidence cost": s["Evidence cost"], "Error cost": s["Error cost"],
            "Weighted error cost": werr.mean(),
            "Weighted total cost": s["Evidence cost"] + werr.mean(),
            "Decided at once (%)": s["Decided at once (%)"], "n": len(ep)}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_data_args(ap)
    ap.add_argument("--beliefs", default="results/svoi_hw2/beliefs.npz")
    ap.add_argument("--horizons", nargs="*", type=int, default=[3, 5])
    ap.add_argument("--multipliers", nargs="*", type=float, default=[1.0, 2.0, 5.0])
    ap.add_argument("--d-max", type=float, default=100.0)
    ap.add_argument("--ttc-max", type=float, default=10.0)
    ap.add_argument("--stride", type=int, default=10)
    ap.add_argument("--C-FA", type=float, default=100.0)
    ap.add_argument("--C-FR", type=float, default=20.0)
    ap.add_argument("--out", default="results/criticality")
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

    flag_va = mobility.critical(s_va, args.d_max, args.ttc_max)
    flag_te = mobility.critical(s_te, args.d_max, args.ttc_max)
    flag_stats = pd.DataFrame([
        {"Split": n, "Critical steps (%)": 100 * f.mean(), "Attack rate, critical": y[f].mean(),
         "Attack rate, other": y[~f].mean()}
        for n, f, y in (("validation", flag_va, data.y[va]), ("test", flag_te, y_te))])
    print(flag_stats.to_string(index=False))

    starts = np.flatnonzero(s_te["pos_in_stream"].to_numpy() % args.stride == 0)
    start_crit = flag_te[starts]
    H_max = max(args.horizons)
    weights = [w for w in args.multipliers if w != 1.0]
    parts = (("all", np.ones(len(starts), bool)), ("critical at start", start_crit),
             ("not critical at start", ~start_crit))
    rows = []
    for ev_name, ev in EVIDENCE_SETS.items():
        tables = {cm: svoi.fit_policy(p_va, u_va, s_va["stream"].to_numpy(), H_max, ev, args.C_FA,
                                      args.C_FR, crit=cm) for cm in [1.0] + weights}
        for H in args.horizons:
            off = replay({1.0: tables[1.0]}, p_te, u_te, y_te, np.ones(len(p_te)), stream_te, starts, H)
            for W in weights:
                on = replay({1.0: tables[1.0], W: tables[W]}, p_te, u_te, y_te,
                            np.where(flag_te, W, 1.0), stream_te, starts, H)
                for ctrl, ep in (("without multiplier", off), (f"with multiplier (Cm = {W:g})", on)):
                    for part, m in parts:
                        rows.append({"Evidence": ev_name, "H": H, "W": W, "Controller": ctrl,
                                     "Episodes": part, **scores(ep[m], flag_te, W)})
                    r = rows[-2]
                    print(f"  {ev_name:7s} H={H} W={W:g} {ctrl:28s} critical: F1 {r['F1']:.4f} "
                          f"queries {r['Queries']:.2f} weighted total {r['Weighted total cost']:.3f}", flush=True)
    res = pd.DataFrame(rows)
    res.to_csv(out / "criticality_results.csv", index=False)
    write_json({"d_max": args.d_max, "ttc_max": args.ttc_max, "multipliers": args.multipliers,
                "critical_share_test_starts": float(start_crit.mean())}, out / "criticality_setup.json")

    import matplotlib.pyplot as plt
    for ev_name in EVIDENCE_SETS:
        fig, ax = plt.subplots(figsize=(6, 4.2))
        for ctrl in res.Controller.unique():
            d = res[(res.Evidence == ev_name) & (res.Controller == ctrl) & (res.Episodes == "critical at start")]
            d = d.drop_duplicates(["H"]) if ctrl == "without multiplier" else d
            ax.plot(d["Evidence cost"], d["F1"], "o", label=ctrl)
        ax.set_xlabel("mean evidence cost per vehicle"); ax.set_ylabel("F1 of final decisions")
        ax.set_title(f"Episodes starting on a critical step ({ev_name})"); ax.legend(fontsize=8)
        plots._save(fig, out / f"critical_f1_vs_cost_{ev_name.replace(' ', '_')}.png")

    cols = ["Evidence", "H", "W", "Controller", "Episodes", "F1", "Precision", "Recall", "PR-AUC", "Queries",
            "Evidence cost", "Error cost", "Weighted error cost", "Weighted total cost", "Decided at once (%)", "n"]
    md = ["# Criticality multiplier (row 16)", "",
          f"Beliefs: `{args.beliefs}`. Critical step: sender within {args.d_max:g} m and time to "
          f"collision below {args.ttc_max:g} s (closing speed from consecutive steps). "
          f"{100 * start_crit.mean():.1f}% of the {len(starts):,} test episodes start on a critical step. "
          "SVoI tables fitted on validation, one per Cm level. For each weight W, the controller "
          "without the multiplier (Cm = 1 everywhere) and with it (Cm = W on critical steps) are "
          "scored on the same objective: an error made on a critical step costs W times more "
          "(weighted error cost). Lower weighted total cost is better.", "",
          "## Critical-step flag", "", to_markdown(flag_stats, index=False), "",
          "## Results (test)", "", to_markdown(res[cols], index=False), ""]
    (out / "report.md").write_text("\n".join(md))
    print("\n" + "\n".join(md))


if __name__ == "__main__":
    main()
