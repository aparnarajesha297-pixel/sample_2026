"""Plan phases 1-5: inspect the data and write the intermediate files.

  processed_data.csv    phase 2   one row per received message
  features.csv          phase 3   one row per step with derived features
  sequence_dataset.pkl  phase 4   (N, T, F) windows + labels per split
  edges.csv             phase 5   Timestamp, VehicleA, VehicleB, Distance
  graph_stats.csv       phase 5   vehicles / edges / neighbours per snapshot
  dataset_summary.json  phases 1-2 checkpoint numbers

Example (first NextGen checkpoint: one scenario, one attack):
  python scripts/prepare_data.py --data nextgen --root /data/NextGen \
      --scenarios highway_2 --attacks constantPositionOffset
"""

from __future__ import annotations

import argparse
import pickle
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ravenx.config import FEATURES  # noqa: E402
from ravenx.experiment import write_json  # noqa: E402
from ravenx.graph import edges_table, graph_stats  # noqa: E402
from ravenx.pipeline import add_data_args, dataset_summary, load_data  # noqa: E402


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_data_args(p)
    p.add_argument("--out", default="results/data")
    p.add_argument("--no-csv", action="store_true", help="skip the large CSV files")
    args = p.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)

    msgs, data = load_data(args)
    s = dataset_summary(msgs, data)
    write_json(s, out / "dataset_summary.json")

    print("\nCheckpoint (phase 2)")
    print(f"  Total messages     = {s['messages']:,}")
    print(f"  Unique vehicles    = {s['unique_vehicles(sender_id per run)']:,}")
    print(f"  Attack messages    = {s['attack_messages']:,}")
    print(f"  Normal messages    = {s['normal_messages']:,}")
    print(f"  Attack percentage  = {s['attack_percentage']:.2f} %")
    print(f"  Missing values     = {s['missing_values'] or 'none'}")
    print("\nCheckpoint (phase 5)")
    for k, v in s["graph"].items():
        print(f"  {k:28s} = {v:,.2f}" if isinstance(v, float) else f"  {k:28s} = {v:,}")
    print("\nPer split:", s["per_split"])

    gs = graph_stats(data.steps, data.graph, data.group)
    gs.to_csv(out / "graph_stats.csv", index=False)
    if not args.no_csv:
        msgs.to_csv(out / "processed_data.csv", index=False)
        cols = ["receiver", "alias", "bin", "rcv_time", "x", "y"] + FEATURES + ["PositionSpeed", "label",
                                                                                "split", "attack_type", "scenario"]
        data.steps[cols].rename(columns={"alias": "VehicleID", "receiver": "ReceiverID",
                                         "rcv_time": "Timestamp", "x": "X", "y": "Y",
                                         "label": "Label"}).to_csv(out / "features.csv", index=False)
        edges_table(data.steps, data.graph).to_csv(out / "edges.csv", index=False)

    seq = {}
    for split in ("train", "val", "test"):
        idx = data.idx(split)
        w = data.win[idx]
        X = np.where((w >= 0)[..., None], data.X_raw[np.maximum(w, 0)], 0.0).astype(np.float32)
        seq[split] = {"X": X, "mask": w >= 0, "y": data.y[idx], "step_index": idx}
    seq["features"] = FEATURES
    with open(out / "sequence_dataset.pkl", "wb") as f:
        pickle.dump(seq, f, protocol=pickle.HIGHEST_PROTOCOL)
    print(f"\nsequence_dataset.pkl: train {seq['train']['X'].shape}, val {seq['val']['X'].shape}, "
          f"test {seq['test']['X'].shape} (N, T, F)")
    print(f"Wrote {out}/")


if __name__ == "__main__":
    main()
