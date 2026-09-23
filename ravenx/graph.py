"""Dynamic vehicle graph (plan phase 5).

One graph per (receiver, time bin): its nodes are the streams that receiver
heard in that bin, and two nodes are joined when their *reported* positions
are closer than ``radius``. This is the neighbour table an RSU or vehicle can
actually build from received CAMs.

Edges are stored directed (both directions) as global step indices, with
three edge attributes the attention can use to compare a vehicle with its
neighbours: normalised distance, speed difference and heading agreement.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

from .config import NEIGHBOR_RADIUS


class Graph:
    def __init__(self, src, dst, eattr, n_nodes):
        self.src = src.astype(np.int64)
        self.dst = dst.astype(np.int64)
        self.eattr = eattr.astype(np.float32)
        self.n_nodes = n_nodes
        # CSR over destinations: incoming edges of node v are
        # order[rowptr[v]:rowptr[v+1]]
        order = np.argsort(self.dst, kind="stable")
        self.order = order
        self.rowptr = np.zeros(n_nodes + 1, dtype=np.int64)
        np.add.at(self.rowptr, self.dst + 1, 1)
        self.rowptr = np.cumsum(self.rowptr)

    @property
    def n_edges(self):
        return len(self.src)

    def in_edges(self, nodes: np.ndarray) -> np.ndarray:
        """Edge ids whose destination is in ``nodes``."""
        starts, ends = self.rowptr[nodes], self.rowptr[nodes + 1]
        lens = ends - starts
        if lens.sum() == 0:
            return np.zeros(0, dtype=np.int64)
        offs = np.repeat(starts - np.cumsum(np.r_[0, lens[:-1]]), lens)
        return self.order[offs + np.arange(lens.sum())]

    def subgraph(self, targets: np.ndarray, hops: int):
        """Nodes/edges needed to compute ``hops`` layers of message passing
        for ``targets``. Returns (nodes, local_src, local_dst, eids, local
        index of each target)."""
        nodes = np.unique(targets)
        for _ in range(hops):
            e = self.in_edges(nodes)
            nodes = np.union1d(nodes, self.src[e])
        e = self.in_edges(nodes)
        # all sources are inside ``nodes`` after the expansion except for the
        # outermost hop, whose contribution does not reach the targets
        keep = np.isin(self.src[e], nodes, assume_unique=False)
        e = e[keep]
        loc_src = np.searchsorted(nodes, self.src[e])
        loc_dst = np.searchsorted(nodes, self.dst[e])
        loc_t = np.searchsorted(nodes, targets)
        return nodes, loc_src, loc_dst, e, loc_t


def build_graph(steps: pd.DataFrame, radius: float = NEIGHBOR_RADIUS):
    """Build edges between steps sharing a (receiver, bin) snapshot.

    All snapshots go into one KD-tree: each snapshot is shifted along x by
    more than the whole coordinate span plus the radius, so a radius query
    can only ever pair nodes of the same snapshot.
    """
    g = steps.groupby(["receiver", "bin"], sort=False).ngroup().values
    n = len(steps)
    x = steps["x"].values.astype(np.float64)
    y = steps["y"].values.astype(np.float64)
    spd = steps["Speed"].values.astype(np.float64)
    hed = np.radians(steps["Heading"].values.astype(np.float64))

    if n > 1:
        shift = (np.nanmax(x) - np.nanmin(x)) + 2 * radius + 1.0
        pts = np.stack([x - np.nanmin(x) + g * shift, y], axis=1)
        pairs = cKDTree(pts).query_pairs(radius, output_type="ndarray")
        pairs = pairs[g[pairs[:, 0]] == g[pairs[:, 1]]]      # belt and braces
    else:
        pairs = np.zeros((0, 2), dtype=np.int64)
    src = np.concatenate([pairs[:, 0], pairs[:, 1]])
    dst = np.concatenate([pairs[:, 1], pairs[:, 0]])

    dist = np.hypot(x[src] - x[dst], y[src] - y[dst])
    eattr = np.stack([
        dist / radius,
        (spd[src] - spd[dst]) / 10.0,
        np.cos(hed[src] - hed[dst]),
    ], axis=1)
    return Graph(src, dst, eattr, n), g


def graph_stats(steps: pd.DataFrame, graph: Graph, group: np.ndarray) -> pd.DataFrame:
    """Per-snapshot statistics required by the plan: vehicles, edges,
    average and maximum neighbours."""
    indeg = np.bincount(graph.dst, minlength=graph.n_nodes)
    df = pd.DataFrame({"group": group, "deg": indeg,
                       "receiver": steps["receiver"].values,
                       "bin": steps["bin"].values,
                       "split": steps["split"].values})
    out = df.groupby("group").agg(
        receiver=("receiver", "first"), bin=("bin", "first"), split=("split", "first"),
        vehicles=("deg", "size"), directed_edges=("deg", "sum"),
        avg_neighbors=("deg", "mean"), max_neighbors=("deg", "max"))
    out["edges"] = out["directed_edges"] // 2
    return out.drop(columns="directed_edges").reset_index(drop=True)


def edges_table(steps: pd.DataFrame, graph: Graph) -> pd.DataFrame:
    """edges.csv of the plan: Timestamp, VehicleA, VehicleB, Distance (undirected)."""
    keep = graph.src < graph.dst
    s, d = graph.src[keep], graph.dst[keep]
    return pd.DataFrame({
        "Receiver": steps["receiver"].values[d],
        "Timestamp": steps["bin"].values[d],
        "VehicleA": steps["alias"].values[s],
        "VehicleB": steps["alias"].values[d],
        "Distance": np.hypot(steps["x"].values[s] - steps["x"].values[d],
                             steps["y"].values[s] - steps["y"].values[d]),
    })
