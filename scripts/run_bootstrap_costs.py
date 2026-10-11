"""Stream-level bootstrap intervals for the SVoI cost comparison (Tables IX and X).

Re-uses the cached beliefs of a trained detector, so nothing is retrained:

  python scripts/run_bootstrap_costs.py --data nextgen --root /data/NextGen/hw2 \
      --beliefs results/svoi_hw2_nbr/beliefs.npz --out results/bootstrap_svoi_19f
  python scripts/run_bootstrap_costs.py ... --evidence a1 --out results/bootstrap_svoi_19f_passive

The policy is fitted on validation exactly as in run_svoi.py. Test episodes are
replayed once per policy and horizon. The bootstrap then resamples whole
STREAMS (a sender heard by a receiver) with replacement, because episodes from
the same stream are correlated. Every replicate scores all policies on the same
resampled streams, so the differences are paired.

The interval covers variation of the test streams for one trained detector. It
does not cover training variation; the 10-seed detection results do that.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from ravenx import svoi  # noqa: E402
from run_svoi import MODE, evaluate  # noqa: E402

COMPARE = ["Always-query", "Never-query"]


def per_stream_sums(ep, stream_of_ep):
    """Per-stream sums of what the metrics need, aligned across policies."""
    df = pd.DataFrame({
        "s": stream_of_ep, "n": 1,
        "total": ep.total_cost.values, "evid": ep.evidence_cost.values, "err": ep.error_cost.values,
        "tp": ((ep.reject == 1) & (ep.label == 1)).astype(int).values,
        "fp": ((ep.reject == 1) & (ep.label == 0)).astype(int).values,
        "fn": ((ep.reject == 0) & (ep.label == 1)).astype(int).values,
    })
    return df.groupby("s", sort=True).sum()


def bootstrap(sums, B, seed):
    """sums: {policy: per-stream DataFrame with identical index}. Returns replicate arrays."""
    pols = list(sums)
    S = len(sums[pols[0]])
    rng = np.random.default_rng(seed)
    cols = ["n", "total", "evid", "err", "tp", "fp", "fn"]
    A = {p: sums[p][cols].to_numpy(float) for p in pols}
    out = {p: {"total": np.empty(B), "evid": np.empty(B), "err": np.empty(B), "F1": np.empty(B)} for p in pols}
    for b in range(B):
        w = rng.multinomial(S, np.full(S, 1.0 / S)).astype(float)
        for p in pols:
            t = w @ A[p]
            n = t[0]
            prec = t[4] / max(t[4] + t[5], 1)
            rec = t[4] / max(t[4] + t[6], 1)
            out[p]["total"][b] = t[1] / n
            out[p]["evid"][b] = t[2] / n
            out[p]["err"][b] = t[3] / n
            out[p]["F1"][b] = 2 * prec * rec / max(prec + rec, 1e-12)
    return out


def ci(x):
    return np.percentile(x, [2.5, 97.5])


def summarise_rows(H, rep, point):
    rows = []
    s = rep["SVoI"]
    for other in COMPARE:
        if other not in rep:
            continue
        o = rep[other]
        diff = o["total"] - s["total"]
        red = 100 * diff / o["total"]
        d_lo, d_hi = ci(diff)
        r_lo, r_hi = ci(red)
        f_lo, f_hi = ci(s["F1"] - o["F1"])
        rows.append({
            "H": H, "Compared with": other,
            "SVoI total cost": point["SVoI"]["total"],
            "Baseline total cost": point[other]["total"],
            "Difference (baseline - SVoI)": point[other]["total"] - point["SVoI"]["total"],
            "Difference 95% CI": f"[{d_lo:+.3f}, {d_hi:+.3f}]",
            "Reduction (%)": 100 * (point[other]["total"] - point["SVoI"]["total"]) / point[other]["total"],
            "Reduction 95% CI (%)": f"[{r_lo:.1f}, {r_hi:.1f}]",
            "F1 difference (SVoI - baseline)": point["SVoI"]["F1"] - point[other]["F1"],
            "F1 difference 95% CI": f"[{f_lo:+.4f}, {f_hi:+.4f}]",
        })
    return rows


def point_estimates(sums):
    out = {}
    for p, d in sums.items():
        t = d.sum()
        prec = t.tp / max(t.tp + t.fp, 1)
        rec = t.tp / max(t.tp + t.fn, 1)
        out[p] = {"total": t.total / t.n, "F1": 2 * prec * rec / max(prec + rec, 1e-12)}
    return out


def run(policy, p_te, u_te, y_te, stream, pos, horizons, policies, stride, B, seed):
    starts = np.flatnonzero(pos % stride == 0)
    stream_of_ep = stream[starts]
    rows, between_h = [], {}
    for H in horizons:
        sums = {}
        for name in policies:
            ep = evaluate(policy, p_te, u_te, y_te, stream, pos, starts, H, MODE[name], seed)
            sums[name] = per_stream_sums(ep, stream_of_ep)
        rep = bootstrap(sums, B, seed + H)
        rows += summarise_rows(H, rep, point_estimates(sums))
        between_h[H] = (sums, rep)
    # Paired comparison between horizons for SVoI (is H = 2 really better than H = 1?)
    hz_rows = []
    hs = sorted(between_h)
    for i, a in enumerate(hs):
        for b in hs[i + 1:]:
            sa, sb = between_h[a][0]["SVoI"], between_h[b][0]["SVoI"]
            rng = np.random.default_rng(seed + 1000 * a + b)
            S = len(sa)
            Aa, Ab = sa[["n", "total"]].to_numpy(float), sb[["n", "total"]].to_numpy(float)
            d = np.empty(B)
            for k in range(B):
                w = rng.multinomial(S, np.full(S, 1.0 / S)).astype(float)
                ta, tb = w @ Aa, w @ Ab
                d[k] = tb[1] / tb[0] - ta[1] / ta[0]
            lo, hi = ci(d)
            pa = Aa[:, 1].sum() / Aa[:, 0].sum()
            pb = Ab[:, 1].sum() / Ab[:, 0].sum()
            hz_rows.append({"SVoI at": f"H = {a}", "versus": f"H = {b}", "cost (H=a)": pa, "cost (H=b)": pb,
                            "difference (b - a)": pb - pa, "95% CI": f"[{lo:+.3f}, {hi:+.3f}]",
                            "excludes 0": bool(lo > 0 or hi < 0)})
    return pd.DataFrame(rows), pd.DataFrame(hz_rows)


def to_md(df, floatfmt=3):
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for r in df.itertuples(index=False):
        lines.append("| " + " | ".join(f"{v:.{floatfmt}f}" if isinstance(v, float) else str(v) for v in r) + " |")
    return "\n".join(lines)


def main():
    from ravenx.pipeline import add_data_args, load_data
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_data_args(ap)
    ap.add_argument("--beliefs", required=True, help="beliefs.npz written by run_svoi.py")
    ap.add_argument("--C-FA", type=float, default=100.0)
    ap.add_argument("--C-FR", type=float, default=20.0)
    ap.add_argument("--gamma", type=float, default=1.0)
    ap.add_argument("--horizons", nargs="*", type=int, default=[1, 2, 3, 5])
    ap.add_argument("--p-bins", type=int, default=20)
    ap.add_argument("--u-bins", type=int, default=8)
    ap.add_argument("--n-min", type=int, default=20)
    ap.add_argument("--stride", type=int, default=10)
    ap.add_argument("--evidence", nargs="*", default=list(svoi.EVIDENCE), choices=list(svoi.EVIDENCE))
    ap.add_argument("--boot", type=int, default=1000, help="bootstrap replicates")
    ap.add_argument("--out", default="results/bootstrap_svoi")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    _, data = load_data(args)
    va, te = data.idx("val"), data.idx("test")
    z = np.load(args.beliefs)
    p_va, u_va, p_te, u_te = z["p_va"], z["u_va"], z["p_te"], z["u_te"]
    assert len(p_va) == len(va) and len(p_te) == len(te), "beliefs.npz does not match this data split"
    st = data.steps
    policy = svoi.fit_policy(p_va, u_va, st["stream"].values[va], max(args.horizons), args.evidence,
                             args.C_FA, args.C_FR, args.gamma, p_bins=args.p_bins, u_bins=args.u_bins,
                             n_min=args.n_min)
    y_te = data.y[te]
    stream, pos = st["stream"].values[te], st["pos_in_stream"].values[te]
    pols = ["SVoI", "Always-query", "Never-query"]
    res, hz = run(policy, p_te, u_te, y_te, stream, pos, args.horizons, pols, args.stride, args.boot, seed=0)
    res.to_csv(out / "bootstrap_policy_vs_baseline.csv", index=False)
    hz.to_csv(out / "bootstrap_svoi_across_horizons.csv", index=False)
    n_streams = len(np.unique(stream[np.flatnonzero(pos % args.stride == 0)]))
    md = ["# Stream-level bootstrap of the SVoI cost comparison", "",
          f"Beliefs from `{args.beliefs}`; evidence actions {args.evidence}; {args.boot} replicates; "
          f"{n_streams:,} streams carry the test episodes. 95% percentile intervals; replicates are paired.",
          "", "## SVoI against baselines", "", to_md(res), "", "## SVoI across horizons", "", to_md(hz), ""]
    (out / "report.md").write_text("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
