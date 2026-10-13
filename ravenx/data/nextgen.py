"""Loader for VeReMi NextGen JSON message logs.

Each NextGen JSON file is an array of received CAMs:

    {"rcvTime", "sendTime", "sender_id", "sender_alias", "messageID",
     "attacker", "receiver": {...}, "sender": {"pos", "spd", "acl", "hed", ...}}

Files are organised per scenario / attack subset / split. The exact folder
layout of the Zenodo archive is not hard-coded: split, attack type and scenario
are inferred from the path, and every value can be overridden.

Only receiver-observable information is turned into features. ``sender_id``
(the true vehicle identity) is kept for bookkeeping but never used as input;
streams are keyed on ``sender_alias`` because that is what a receiver sees.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

from ..config import ATTACKS

_SPLIT_TOKENS = {
    "train": "train", "training": "train",
    "val": "val", "valid": "val", "validation": "val",
    "test": "test", "testing": "test",
}
_SCENARIO_RE = re.compile(r"(urban|highway)[_-]?(\d+)?", re.IGNORECASE)


def parse_path_meta(path: Path, root: Path) -> dict:
    """Infer split / attack / scenario / density from a file path."""
    rel = str(path.relative_to(root)) if root in path.parents else str(path)
    tokens = re.split(r"[\\/_\-.]+", rel.lower())

    split = next((_SPLIT_TOKENS[t] for t in reversed(tokens) if t in _SPLIT_TOKENS), None)
    attack = next((a for a in ATTACKS if a.lower() in rel.lower()), None)

    m = _SCENARIO_RE.search(rel)
    scenario = (m.group(1).lower() + (f"_{m.group(2)}" if m.group(2) else "")) if m else "unknown"
    road = m.group(1).lower() if m else "unknown"

    density = "unknown"
    if "low" in tokens:
        density = "low"
    elif "high" in tokens:
        density = "high"

    return {"split": split, "attack_type": attack, "scenario": scenario,
            "road": road, "density": density}


def _read_messages(path: Path) -> list[dict]:
    text = path.read_text()
    text_stripped = text.lstrip()
    if text_stripped.startswith("["):
        return json.loads(text)
    # JSON-lines fallback
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def _parse_pos(pos):
    """Positions are documented as [x, y, z] but the released files store
    them as a "x,y,z" string. Accept both."""
    if pos is None:
        return (np.nan, np.nan)
    if isinstance(pos, str):
        parts = pos.split(",")
        return (float(parts[0]), float(parts[1]))
    return (float(pos[0]), float(pos[1]))


def _flatten(records: list[dict]) -> pd.DataFrame:
    rows = []
    for r in records:
        s = r.get("sender", {})
        pos = _parse_pos(s.get("pos"))
        rcv = r.get("receiver", {})
        rx = _parse_pos(rcv.get("pos"))
        rows.append((
            r.get("rcvTime"), r.get("sendTime"), r.get("sender_id"),
            r.get("sender_alias"), r.get("messageID"), r.get("attacker", 0),
            pos[0], pos[1], s.get("spd"), s.get("hed"), s.get("acl"),
            s.get("driversProfile"), rx[0], rx[1], s.get("distance_to_road_edge", np.nan),
            rcv.get("spd", np.nan), rcv.get("hed", np.nan),
        ))
    df = pd.DataFrame(rows, columns=[
        "rcv_time", "send_time", "sender_id", "alias", "msg_id", "attacker",
        "x", "y", "spd", "hed", "acl", "profile", "rx_x", "rx_y", "road_edge",
        "rx_spd", "rx_hed",
    ])
    for c in ("spd", "hed", "acl", "rx_spd", "rx_hed", "road_edge"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def _to_seconds(t: pd.Series) -> pd.Series:
    t = pd.to_numeric(t, errors="coerce").astype(float)
    # NextGen documents timestamps in nanoseconds; accept seconds too.
    if np.nanmedian(np.abs(t.values)) > 1e7:
        t = t / 1e9
    return t


def load_nextgen(root: str | Path,
                 attacks: list[str] | None = None,
                 splits: list[str] | None = None,
                 scenarios: list[str] | None = None,
                 density_map: dict[str, str] | None = None,
                 max_files_per_subset: int | None = None,
                 verbose: bool = True) -> pd.DataFrame:
    """Read every JSON file under ``root`` into one message table.

    Parameters
    ----------
    attacks, splits, scenarios : optional filters.
    density_map : e.g. {"highway_1": "low", "highway_2": "high"} when the
        folder names do not contain "low"/"high".
    max_files_per_subset : cap on receiver files per (subset, split); useful
        for the first small runs recommended in the plan.
    """
    root = Path(root)
    files = sorted(root.rglob("*.json"))
    if not files:
        raise FileNotFoundError(f"No .json files under {root}")

    per_subset: dict[tuple, int] = {}
    frames, metas = [], []
    for f in files:
        meta = parse_path_meta(f, root)
        if meta["split"] is None:
            continue
        if attacks and meta["attack_type"] not in attacks:
            continue
        if splits and meta["split"] not in splits:
            continue
        if scenarios and meta["scenario"] not in scenarios:
            continue
        if density_map and meta["scenario"] in density_map:
            meta["density"] = density_map[meta["scenario"]]
        key = (meta["scenario"], meta["attack_type"], meta["split"])
        if max_files_per_subset is not None and per_subset.get(key, 0) >= max_files_per_subset:
            continue
        per_subset[key] = per_subset.get(key, 0) + 1

        df = _flatten(_read_messages(f))
        if df.empty:
            continue
        # compact per-file columns; metadata is attached once, after concat
        df["rcv_time"] = _to_seconds(df["rcv_time"])
        df["send_time"] = _to_seconds(df["send_time"])
        df["alias"] = df["alias"].astype(str)
        df["attacker"] = pd.to_numeric(df["attacker"], errors="coerce").fillna(0).astype(np.int8)
        for c in ("spd", "hed", "acl", "rx_spd", "rx_hed", "road_edge"):
            df[c] = df[c].astype(np.float32)
        run = f"{meta['scenario']}/{meta['attack_type']}/{meta['split']}"
        # One NextGen file = one receiving vehicle's log.
        metas.append({**meta, "run": run, "receiver": f"{run}/{f.stem}"})
        frames.append(df)

    if not frames:
        raise ValueError("No files matched the requested filters")
    sizes = np.array([len(df) for df in frames])
    msgs = pd.concat(frames, ignore_index=True)
    del frames
    # metadata as categoricals: one small code array per column, not one
    # Python string per message
    for key in ("run", "receiver", "split", "attack_type", "scenario", "road", "density"):
        values = pd.Series([mt[key] for mt in metas], dtype="object")
        codes, cats = pd.factorize(values, sort=True)
        msgs[key] = pd.Categorical.from_codes(np.repeat(codes, sizes), categories=cats)
    for key in ("alias", "sender_id", "profile"):
        msgs[key] = msgs[key].astype("category")
    msgs["attacker"] = msgs["attacker"].astype(int)
    if verbose:
        print(f"Loaded {len(msgs):,} messages from {len(sizes)} files")
    return msgs
