"""Row 18: ADDR, stealthy targeted poisoning of the federated model.

How often can one compromised RSU flip one target vehicle's accept/reject
decision while the global model still looks normal?

1. Train federated RAVEN-X-GF honestly for --base-rounds (20 RSUs, spatial
   partition), once per aggregator, and checkpoint it.
2. From the checkpoint, continue for --attack-rounds:
     honest         all RSUs honest (the reference model)
     honest (rerun) the same again, to measure run-to-run noise
     attacked       one RSU runs ravenx.adversarial.TargetedAttack against
                    one target vehicle, at each strength
3. Decisions. The server calibrates each global model on validation
   (temperature). The honest model's SVoI controller (H = 3, a1-a4) defines
   the decision moments: the target's test steps at which it stops. At those
   steps the honest and the other model's Eq. 14 decisions are compared.
   The attacker has seen only the first half of the target's messages
   (poisoning set); ADDR is reported on the second half (future decisions)
   and, as an upper bound, on the first half.
4. Stealth: validation PR-AUC, F1 and ECE of every model on the same
   validation subsample.

Targets are chosen before any model is trained: test vehicles (run, pseudonym)
with at least --min-steps steps, --targets attackers (label rate >= 0.9,
distinct attack types) and --targets honest vehicles (label rate 0).

Example:
  python scripts/run_addr.py --data nextgen --root /data/NextGen/hw2
"""

from __future__ import annotations

import argparse
import copy
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch.nn.utils import parameters_to_vector, vector_to_parameters

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ravenx import svoi  # noqa: E402
from ravenx.adversarial import STRENGTHS, TargetedAttack, flip_rates, reject_decision  # noqa: E402
from ravenx.calibration import fit_temperature, probs  # noqa: E402
from ravenx.config import FEATURES  # noqa: E402
from ravenx.experiment import to_markdown, write_json  # noqa: E402
from ravenx.federated import make_aggregator, partition_rsus, run_federated  # noqa: E402
from ravenx.metrics import ece, pr_auc  # noqa: E402
from ravenx.models.train import NeuralDetector  # noqa: E402
from ravenx.pipeline import add_data_args, load_data  # noqa: E402


def pick_targets(data, te, n, min_steps, seed):
    st = data.steps.iloc[te]
    df = pd.DataFrame({"run": st["run"].astype(str).values, "alias": st["alias"].values,
                       "attack": st["attack_type"].astype(str).values, "y": data.y[te], "idx": te,
                       "t": st["rcv_time"].values})
    g = df.groupby(["run", "alias"]).agg(n=("y", "size"), rate=("y", "mean"), attack=("attack", "first"))
    g = g[g.n >= min_steps]
    rng = np.random.default_rng(seed)
    atk = g[g.rate >= 0.9].sample(frac=1.0, random_state=seed)
    atk = atk.groupby("attack").head(1).head(n)                       # one per attack type
    hon = g[g.rate == 0].sample(n=n, random_state=int(rng.integers(1 << 31)))
    targets = []
    for kind, sel in (("attacker", atk), ("honest", hon)):
        for (run, alias), row in sel.iterrows():
            v = df[(df.run == run) & (df.alias == alias)].sort_values("t")
            half = len(v) // 2
            targets.append({"id": f"{kind}:{row.attack}:{alias}", "kind": kind, "attack": row.attack,
                            "steps": int(row.n), "label_rate": float(row.rate),
                            "poison_idx": v.idx.values[:half], "eval_idx": v.idx.values[half:]})
    return targets


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_data_args(ap)
    ap.add_argument("--model", default="RAVEN-X-GF")
    ap.add_argument("--rsus", type=int, default=20)
    ap.add_argument("--base-rounds", type=int, default=10)
    ap.add_argument("--attack-rounds", type=int, default=3)
    ap.add_argument("--aggregators", nargs="*", default=["FedAvg", "RS-WeightedTrim"])
    ap.add_argument("--strengths", nargs="*", default=list(STRENGTHS), choices=list(STRENGTHS))
    ap.add_argument("--boost", type=float, default=20.0)
    ap.add_argument("--target-share", type=float, default=0.2)
    ap.add_argument("--targets", type=int, default=5, help="per kind (attacker / honest)")
    ap.add_argument("--min-steps", type=int, default=50)
    ap.add_argument("--val-sample", type=int, default=40000)
    ap.add_argument("--H", type=int, default=3)
    ap.add_argument("--hidden", type=int, default=64)
    ap.add_argument("--batch-size", type=int, default=256)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--out", default="results/addr")
    args = ap.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    # multithreaded CPU kernels otherwise make two identical runs differ, which would
    # show up as spurious decision flips
    torch.use_deterministic_algorithms(True)

    _, data = load_data(args)
    tr, va, te = data.idx("train"), data.idx("val"), data.idx("test")
    clients = partition_rsus(data, tr, args.rsus, "spatial", args.seed)
    rng = np.random.default_rng(args.seed)
    attacker = int(rng.choice(args.rsus))
    va_s = np.sort(rng.choice(va, min(args.val_sample, len(va)), replace=False))
    targets = pick_targets(data, te, args.targets, args.min_steps, args.seed)
    with open(out / "targets.pkl", "wb") as f:
        pickle.dump(targets, f)
    print(f"attacking RSU {attacker} ({len(clients[attacker])} steps); targets:")
    for t in targets:
        print(f"   {t['id']:45s} steps {t['steps']:4d}  poison {len(t['poison_idx'])}  eval {len(t['eval_idx'])}")

    def make(seed):
        return NeuralDetector(args.model, len(FEATURES), hidden=args.hidden, lr=args.lr,
                              batch_size=args.batch_size, seed=seed, verbose=False)

    probe = make(0)

    def load(theta):
        vector_to_parameters(theta.clone(), probe.net.parameters())
        return probe

    def calibrated(theta, val_idx, idx_sets):
        """Server pipeline: temperature on validation, then calibrated (p, u)."""
        det = load(theta)
        z_va = det.predict_logits(data, val_idx)
        T = fit_temperature(z_va, data.y[val_idx], "evidential")
        p_va, u_va = probs(z_va, T, "evidential")
        return T, (p_va, u_va), [probs(det.predict_logits(data, i), T, "evidential") for i in idx_sets]

    def stealth(theta, T):
        det = load(theta)
        z = det.predict_logits(data, va_s)
        p, _ = probs(z, T, "evidential")
        raw, _ = probs(z, 1.0, "evidential")
        y = data.y[va_s]
        rej = reject_decision(p)
        tp, fp, fn = (rej & (y == 1)).sum(), (rej & (y == 0)).sum(), (~rej & (y == 1)).sum()
        return {"val PR-AUC": pr_auc(y, p), "val F1": 2 * tp / max(2 * tp + fp + fn, 1), "val ECE": ece(y, raw)}

    per_row = out / "addr_per_target.csv"
    rows = pd.read_csv(per_row).to_dict("records") if per_row.exists() else []
    done = {(r["Aggregator"], r["Model"], r["Target"]) for r in rows}
    idx_sets = [np.concatenate([t["poison_idx"], t["eval_idx"]]) for t in targets]

    for agg_name in args.aggregators:
        ck = out / f"base_{agg_name}.pt"
        if ck.exists():
            state = torch.load(ck, weights_only=False)
            theta_base, agg_base = state["theta"], state["aggregator"]
        else:
            print(f"\n== base training: {agg_name}, {args.base_rounds} rounds ==", flush=True)
            agg = make_aggregator(agg_name, args.rsus, 1)
            det, log, _, _ = run_federated(make, data, clients, agg, rounds=args.base_rounds)
            theta_base = parameters_to_vector(det.net.parameters()).detach().clone()
            agg_base = agg
            torch.save({"theta": theta_base, "aggregator": agg_base, "log": log}, ck)

        def continue_from(attack=None, tag=""):
            ck2 = out / f"cont_{agg_name}_{tag}.pt"
            if ck2.exists():
                s = torch.load(ck2, weights_only=False)
                return s["theta"], s["log"], s.get("attack_log", [])
            agg = copy.deepcopy(agg_base)
            det, log, _, _ = run_federated(make, data, clients, agg, rounds=args.attack_rounds,
                                           theta0=theta_base, round0=args.base_rounds,
                                           malicious=[attacker] if attack else (),
                                           poisoning="targeted" if attack else "none", attack=attack,
                                           verbose=False)
            theta = parameters_to_vector(det.net.parameters()).detach().clone()
            alog = attack.log if attack else []
            torch.save({"theta": theta, "log": log, "attack_log": alog}, ck2)
            return theta, log, alog

        print(f"\n== {agg_name}: honest continuation ==", flush=True)
        theta_h, log_h, _ = continue_from(tag="honest")
        # honest reference: full validation for the SVoI table, then decision moments
        det = load(theta_h)
        z_va = det.predict_logits(data, va)
        T_h = fit_temperature(z_va, data.y[va], "evidential")
        p_va, u_va = probs(z_va, T_h, "evidential")
        policy = svoi.fit_policy(p_va, u_va, data.steps["stream"].values[va], args.H)
        honest = []
        for t, ix in zip(targets, idx_sets):
            p, u = probs(det.predict_logits(data, ix), T_h, "evidential")
            act = np.array([policy.decide(pi, ui, args.H) for pi, ui in zip(p, u)])
            stop = np.isin(act, [svoi.STOP_ACCEPT, svoi.STOP_REJECT])
            honest.append({"stop": stop, "reject": act == svoi.STOP_REJECT,
                           "poison": np.arange(len(ix)) < len(t["poison_idx"])})
        st_h = stealth(theta_h, T_h)
        round_norm = float(np.median([e["update_norm"] for e in log_h]))
        write_json({"T": T_h, "round_update_norm_median": round_norm, "attacker_rsu": attacker,
                    "theta_norm": float(theta_h.norm()), **st_h}, out / f"honest_{agg_name}.json")
        np.save(out / f"theta_honest_{agg_name}.npy", theta_h.numpy())

        runs = [("honest (rerun)", None, None)] + [(s, s, t) for t in targets for s in args.strengths]
        for model, strength, tgt in runs:
            tlist = targets if tgt is None else [tgt]
            if all((agg_name, model, t["id"]) in done for t in tlist):
                continue
            tag = "rerun" if tgt is None else f"{strength}_{tgt['id'].replace(':', '_')}"
            print(f"== {agg_name} | {model} | {'all targets' if tgt is None else tgt['id']} ==", flush=True)
            attack = None
            if tgt is not None:
                attack = TargetedAttack(make, data, clients[attacker], tgt["poison_idx"], strength,
                                        args.boost, args.target_share)
            theta_o, _, alog = continue_from(attack, tag)
            sel = [targets.index(t) for t in tlist]
            T_o, _, pu = calibrated(theta_o, va_s, [idx_sets[i] for i in sel])
            st_o = stealth(theta_o, T_o)
            dev = float((theta_o - theta_h).norm())
            if tgt is not None:
                np.save(out / f"delta_{agg_name}_{tag}.npy", (theta_o - theta_h).numpy())
            for i, (p_o, _) in zip(sel, pu):
                t, h = targets[i], honest[i]
                rej_o = reject_decision(p_o)
                row = {"Aggregator": agg_name, "Model": model, "Target": t["id"], "Kind": t["kind"],
                       "Attack type": t["attack"], "Steps": t["steps"],
                       "Honest decides (%)": 100 * h["stop"].mean(),
                       "Honest rejects (% of decisions)": 100 * h["reject"][h["stop"]].mean() if h["stop"].any() else np.nan}
                for part, m in (("future", ~h["poison"]), ("seen", h["poison"])):
                    m = m & h["stop"]
                    fr = flip_rates(h["reject"][m], rej_o[m])
                    row.update({f"{k} ({part})": v for k, v in fr.items()})
                row.update({"‖Δθ‖": dev, "‖Δθ‖ / round update": dev / round_norm,
                            "‖Δθ‖ / ‖θ‖": dev / float(theta_h.norm()), **st_o,
                            **{f"{k} (honest)": v for k, v in st_h.items()}})
                if alog:
                    row.update({"sent / benign norm": np.mean([a["sent_norm"] / a["benign_norm"] for a in alog]),
                                "cosine to benign": np.mean([a["cosine_to_benign"] for a in alog])})
                rows.append(row)
                print(f"   {t['id']:45s} ADDR future {row['ADDR (future)']:.3f} seen {row['ADDR (seen)']:.3f}  "
                      f"val F1 {st_o['val F1']:.4f} (honest {st_h['val F1']:.4f})", flush=True)
            pd.DataFrame(rows).to_csv(per_row, index=False)

    df = pd.DataFrame(rows)
    write_report(df, args, out)


def write_report(df, args, out):
    md = ["# ADDR: stealthy targeted poisoning (row 18)", "",
          f"{args.model}, {args.rsus} RSUs (spatial), one compromised RSU. {args.base_rounds} honest rounds, "
          f"then {args.attack_rounds} rounds with the attacker active. Boost {args.boost:g}; target messages "
          f"≈ {100 * args.target_share:.0f}% of the attacker's local training stream. Decisions at the steps "
          f"where the honest SVoI controller (H = {args.H}) stops; Eq. 14 decision on each model's own "
          "validation-calibrated belief. 'future' = the half of the target's messages the attacker never saw; "
          "'seen' = the half it trained on (upper bound). 'honest (rerun)' is a second honest continuation: "
          "its ADDR is the noise floor.", ""]
    summ = []
    for (agg, model, kind), g in df.groupby(["Aggregator", "Model", "Kind"], sort=False):
        summ.append({"Aggregator": agg, "Model": model, "Targets": kind,
                     "ADDR future, mean": g["ADDR (future)"].mean(), "ADDR future, worst": g["ADDR (future)"].max(),
                     "wrongly accepted (future)": g["wrongly accepted (future)"].mean(),
                     "wrongly rejected (future)": g["wrongly rejected (future)"].mean(),
                     "ADDR seen, mean": g["ADDR (seen)"].mean(), "ADDR seen, worst": g["ADDR (seen)"].max(),
                     "val F1": g["val F1"].mean(), "val F1 (honest)": g["val F1 (honest)"].mean(),
                     "val ECE": g["val ECE"].mean(), "val ECE (honest)": g["val ECE (honest)"].mean(),
                     "‖Δθ‖ / round update": g["‖Δθ‖ / round update"].mean()})
    summ = pd.DataFrame(summ)
    summ.to_csv(out / "addr_summary.csv", index=False)
    md += ["## Summary (mean over targets, worst case = highest)", "", to_markdown(summ, index=False), ""]
    cols = ["Aggregator", "Model", "Target", "Honest decides (%)", "Honest rejects (% of decisions)",
            "ADDR (future)", "wrongly accepted (future)", "wrongly rejected (future)", "decisions (future)",
            "ADDR (seen)", "val F1", "val ECE", "‖Δθ‖ / round update"]
    md += ["## Per target", "", to_markdown(df[[c for c in cols if c in df]], index=False), ""]
    (out / "report.md").write_text("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
