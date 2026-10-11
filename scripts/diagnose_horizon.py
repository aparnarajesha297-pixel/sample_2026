"""Row 15 follow-up: where does the mobility-aware horizon's gain come from?

Replays SVoI on test with a fixed horizon and with the validation-chosen cap
(geometric estimate, q = 0.5, minimum cap 1), split by whether the episode
starts on a stream's first step and by Sybil vs other attack runs. Then
compares against a trivial rule with no mobility content at all: plan one
step at a stream's first message, otherwise use the full horizon.

This is a diagnostic run after the test results were seen; it explains the
result and is not a method selected on test.

Example:
  python scripts/diagnose_horizon.py --data nextgen --root /data/NextGen/hw2
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from ravenx import mobility, svoi  # noqa: E402
from ravenx.experiment import to_markdown  # noqa: E402
from ravenx.pipeline import add_data_args, load_data  # noqa: E402
from run_horizon import replay  # noqa: E402
from run_svoi import summarise  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_data_args(ap)
    ap.add_argument("--beliefs", default="results/svoi_hw2/beliefs.npz")
    ap.add_argument("--stride", type=int, default=10)
    ap.add_argument("--out", default="results/horizon")
    args = ap.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)

    _, data = load_data(args)
    st = data.steps
    va, te = data.idx("val"), data.idx("test")
    z = np.load(args.beliefs)
    p_va, u_va, p_te, u_te = z["p_va"], z["u_va"], z["p_te"], z["u_te"]
    s_va, s_te = st.iloc[va], st.iloc[te]
    y, stream = data.y[te], s_te["stream"].to_numpy()
    starts = np.flatnonzero(s_te["pos_in_stream"].to_numpy() % args.stride == 0)
    first = s_te["pos_in_stream"].to_numpy()[starts] == 0
    sybil = s_te["attack_type"].astype(str).to_numpy()[starts] == "trafficCongestionSybil"
    cap = mobility.horizon_cap(mobility.HorizonProxy.fit(s_va, 0.5).predict(s_te)["geometric"], 1)
    trivial = np.where(s_te["pos_in_stream"].to_numpy() == 0, 1, 10 ** 6)

    split_rows, rule_rows = [], []
    for ev_name, ev in (("a1-a4", list(svoi.EVIDENCE)), ("a1 only", ["a1"])):
        pol = svoi.fit_policy(p_va, u_va, s_va["stream"].to_numpy(), 10, ev)
        for H in (2, 3, 5, 10):
            eps = {name: replay(pol, p_te, u_te, y, stream, starts, H, c)
                   for name, c in (("fixed H", None), ("geometric cap", cap), ("trivial rule", trivial))}
            for name, ep in eps.items():
                s = summarise(ep)
                rule_rows.append({"Evidence": ev_name, "H": H, "Horizon": name, "F1": s["F1"],
                                  "Evidence cost": s["Evidence cost"], "Total cost": s["Total cost"]})
                if H == 3 and name != "trivial rule":
                    for part, m in (("first step of stream", first), ("later step", ~first),
                                    ("Sybil runs", sybil), ("other runs", ~sybil)):
                        s = summarise(ep[m])
                        split_rows.append({"Evidence": ev_name, "Horizon": name, "Episodes": part,
                                           "n": int(m.sum()), "F1": s["F1"], "Evidence cost": s["Evidence cost"],
                                           "Total cost": s["Total cost"], "Queries": s["Queries"],
                                           "Observations": s["Observations"]})
            print(ev_name, H, flush=True)
    split, rules = pd.DataFrame(split_rows), pd.DataFrame(rule_rows)
    split.to_csv(out / "diagnosis_split.csv", index=False)
    rules.to_csv(out / "diagnosis_trivial_rule.csv", index=False)
    md = ["# Where the horizon gain comes from (row 15 diagnostic)", "",
          "Run after the test results were seen, to explain them; not a selection step.", "",
          "## H = 3, split by episode type (test)", "", to_markdown(split, index=False), "",
          "## Trivial rule vs the geometric cap (test)", "",
          "Trivial rule: plan one step at a stream's first message, otherwise use the full horizon.", "",
          to_markdown(rules, index=False), ""]
    (out / "diagnosis.md").write_text("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
