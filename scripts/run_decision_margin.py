"""Row 19: how far can the global model move before decisions flip?

Takes the honest federated global model from run_addr.py, moves its
parameters by fixed amounts along several directions, and measures how
often the accept/reject decision changes at the steps where the honest SVoI
controller decides. The server's calibration (temperature fitted for the
honest model) is kept fixed, as it would be between recalibrations.

Step size: multiples of the median norm of one honest aggregated round
update (so "1" = one round's worth of model change).

Directions (unit vectors in parameter space):
  random       isotropic Gaussian draws
  reverse      minus the honest continuation's own change (theta_honest -
               theta_base), i.e. undoing training, as a sign-flip attacker
               would push
  attack       the direction of each row-18 attacked model (theta_attacked -
               theta_honest), per strength; averaged over targets
  gradient     minus the gradient of the detector's loss on the decision
               steps with every honest decision flipped: the first-order
               worst case for flipping decisions

Also places row 18's measured deviations on the same axis.

Example:
  python scripts/run_decision_margin.py --data nextgen --root /data/NextGen/hw2
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch.nn.utils import parameters_to_vector, vector_to_parameters

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ravenx import plots, svoi  # noqa: E402
from ravenx.adversarial import flip_rates, reject_decision  # noqa: E402
from ravenx.calibration import probs  # noqa: E402
from ravenx.config import FEATURES  # noqa: E402
from ravenx.experiment import to_markdown  # noqa: E402
from ravenx.models.train import NeuralDetector, make_batch  # noqa: E402
from ravenx.pipeline import add_data_args, load_data  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_data_args(ap)
    ap.add_argument("--model", default="RAVEN-X-GF")
    ap.add_argument("--addr-dir", default="results/addr")
    ap.add_argument("--aggregators", nargs="*", default=["RS-WeightedTrim", "FedAvg"])
    ap.add_argument("--scales", nargs="*", type=float, default=[0.1, 0.3, 1, 3, 10, 30])
    ap.add_argument("--random-draws", type=int, default=5)
    ap.add_argument("--test-sample", type=int, default=20000)
    ap.add_argument("--grad-sample", type=int, default=8192)
    ap.add_argument("--H", type=int, default=3)
    ap.add_argument("--hidden", type=int, default=64)
    ap.add_argument("--out", default="results/decision_margin")
    args = ap.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    # multithreaded CPU kernels otherwise make two identical runs differ, which would
    # show up as spurious decision flips
    torch.use_deterministic_algorithms(True)
    src = Path(args.addr_dir)

    _, data = load_data(args)
    va, te = data.idx("val"), data.idx("test")
    rng = np.random.default_rng(args.seed)
    S = np.sort(rng.choice(te, min(args.test_sample, len(te)), replace=False))
    det = NeuralDetector(args.model, len(FEATURES), hidden=args.hidden, seed=0, verbose=False)
    addr = pd.read_csv(src / "addr_per_target.csv") if (src / "addr_per_target.csv").exists() else None

    rows, marks = [], []
    for agg in args.aggregators:
        info = json.loads((src / f"honest_{agg}.json").read_text())
        T, unit = info["T"], info["round_update_norm_median"]
        theta_h = torch.from_numpy(np.load(src / f"theta_honest_{agg}.npy"))
        theta_b = torch.load(src / f"base_{agg}.pt", weights_only=False)["theta"]
        vector_to_parameters(theta_h.clone(), det.net.parameters())

        # honest decision moments on the test sample
        z_va = det.predict_logits(data, va)
        p_va, u_va = probs(z_va, T, "evidential")
        policy = svoi.fit_policy(p_va, u_va, data.steps["stream"].values[va], args.H)
        p, u = probs(det.predict_logits(data, S), T, "evidential")
        act = np.array([policy.decide(a, b, args.H) for a, b in zip(p, u)])
        stop = np.isin(act, [svoi.STOP_ACCEPT, svoi.STOP_REJECT])
        M = S[stop]
        rej_h = reject_decision(p[stop])
        print(f"{agg}: {len(M):,} of {len(S):,} sampled test steps are honest decisions "
              f"({100 * rej_h.mean():.1f}% reject); round update norm {unit:.4f}", flush=True)

        dirs = {f"random {i + 1}": torch.from_numpy(rng.standard_normal(theta_h.numel()).astype(np.float32))
                for i in range(args.random_draws)}
        dirs["reverse training"] = -(theta_h - theta_b)
        for f in sorted(src.glob(f"delta_{agg}_*.npy")):
            strength = f.stem.split("_")[2]
            dirs[f"attack {strength} | {f.stem.split('_', 3)[3]}"] = torch.from_numpy(np.load(f))
        # first-order worst case: descend the loss with every honest decision flipped
        g_idx = M[rng.permutation(len(M))[:args.grad_sample]]
        g_lab = data.y.copy()
        g_lab[M] = (~rej_h).astype(g_lab.dtype)
        det.net.train()
        for m in det.net.modules():             # gradient without dropout noise
            if isinstance(m, torch.nn.Dropout):
                m.eval()
        det.net.zero_grad()
        for i in range(0, len(g_idx), 1024):
            t = g_idx[i:i + 1024]
            logits = det.net(*make_batch(data, t, det.net, det.device))
            loss = det._loss(logits, torch.from_numpy(g_lab[t]), 100) * len(t) / len(g_idx)
            loss.backward()
        dirs["gradient (worst case)"] = -torch.cat([q.grad.flatten() for q in det.net.parameters()])
        det.net.eval()

        for name, d in dirs.items():
            d = d / d.norm()
            for s in args.scales:
                vector_to_parameters((theta_h + s * unit * d).clone(), det.net.parameters())
                p_o, _ = probs(det.predict_logits(data, M), T, "evidential")
                fr = flip_rates(rej_h, reject_decision(p_o))
                kind = name.split(" |")[0] if name.startswith("attack") else name.split(" ")[0]
                rows.append({"Aggregator": agg, "Direction": name, "Family": kind, "Scale (rounds)": s,
                             "‖Δθ‖ / ‖θ‖": s * unit / float(theta_h.norm()), **fr})
            last = rows[-1]
            print(f"   {name:50s} flip rate at {args.scales[-1]:g} rounds: {last['ADDR']:.4f}", flush=True)
        vector_to_parameters(theta_h.clone(), det.net.parameters())
        if addr is not None:
            for (model,), g in addr[addr.Aggregator == agg].groupby(["Model"]):
                marks.append({"Aggregator": agg, "Row-18 model": model,
                              "‖Δθ‖ / round update, mean": g["‖Δθ‖ / round update"].mean(),
                              "‖Δθ‖ / round update, max": g["‖Δθ‖ / round update"].max()})

    df = pd.DataFrame(rows)
    df.to_csv(out / "decision_flips.csv", index=False)
    fam = (df.groupby(["Aggregator", "Family", "Scale (rounds)"])
             [["ADDR", "wrongly accepted", "wrongly rejected"]].agg(["mean", "max"]).reset_index())
    fam.columns = [" ".join(c).strip() for c in fam.columns]
    fam = fam.rename(columns={"ADDR mean": "flip rate, mean", "ADDR max": "flip rate, worst"})
    fam.to_csv(out / "decision_flips_by_family.csv", index=False)
    mk = pd.DataFrame(marks)

    import matplotlib.pyplot as plt
    for agg in args.aggregators:
        fig, ax = plt.subplots(figsize=(6.4, 4.4))
        d = fam[fam.Aggregator == agg]
        for f in d.Family.unique():
            x = d[d.Family == f]
            ax.plot(x["Scale (rounds)"], x["flip rate, mean"], "o-", label=f)
        if len(mk):
            for _, r in mk[mk.Aggregator == agg].iterrows():
                ax.axvline(max(r["‖Δθ‖ / round update, mean"], 1e-3), ls=":", lw=1, color="grey")
        ax.set_xscale("log"); ax.set_xlabel("model change (multiples of one honest round's update)")
        ax.set_ylabel("share of decisions flipped"); ax.set_title(f"Decision flips vs model change ({agg})")
        ax.legend(fontsize=8)
        plots._save(fig, out / f"flips_vs_change_{agg}.png")

    md = ["# How much model change flips decisions (row 19)", "",
          f"Honest federated {args.model} from `{args.addr_dir}`; decisions compared at the steps of a "
          f"{len(S):,}-step test sample where the honest SVoI controller (H = {args.H}) stops. Temperature "
          "fixed at the honest model's. Scale = ‖Δθ‖ in multiples of the median honest round update norm.",
          "", "## Flip rate by direction family", "", to_markdown(fam, index=False), ""]
    if len(mk):
        md += ["## Row 18 deviations on the same scale (dotted lines in the plots)", "",
               to_markdown(mk, index=False), ""]
    (out / "report.md").write_text("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
