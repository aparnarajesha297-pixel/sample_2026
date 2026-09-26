"""Figures for the experiments (matplotlib, saved as PNG)."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from .metrics import reliability_curve  # noqa: E402

BENIGN, ATTACK = "#3b7dd8", "#d8573b"
DEC_COLORS = {"TRUST": "#3a9b5c", "VERIFY": "#e0a526", "REJECT": "#c8412f"}


def _save(fig, path):
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def risk_distribution(risk, y, path, policy=None):
    fig, ax = plt.subplots(figsize=(6.4, 4))
    bins = np.linspace(0, 1, 51)
    ax.hist(risk[y == 0], bins, alpha=0.65, color=BENIGN, label="legitimate", density=True)
    ax.hist(risk[y == 1], bins, alpha=0.65, color=ATTACK, label="attack", density=True)
    if policy is not None:
        for t, name in ((policy.t_low, "t_low"), (policy.t_high, "t_high")):
            if 0 <= t <= 1:
                ax.axvline(t, color="k", ls="--", lw=1)
                ax.text(t, ax.get_ylim()[1] * 0.95, f" {name}={t:.2f}", fontsize=8, va="top")
    ax.set_yscale("log")
    ax.set_xlabel("risk = expected P(attack)")
    ax.set_ylabel("density (log)")
    ax.set_title("Risk distribution (test)")
    ax.legend()
    _save(fig, path)


def uncertainty_distribution(unc, y, correct, path, u_max=None):
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    bins = np.linspace(0, max(unc.max(), 1e-3), 51)
    axes[0].hist(unc[y == 0], bins, alpha=0.65, color=BENIGN, label="legitimate", density=True)
    axes[0].hist(unc[y == 1], bins, alpha=0.65, color=ATTACK, label="attack", density=True)
    axes[0].set_title("Uncertainty by class")
    axes[1].hist(unc[correct], bins, alpha=0.65, color="#3a9b5c", label="correct", density=True)
    axes[1].hist(unc[~correct], bins, alpha=0.65, color="#8e44ad", label="wrong", density=True)
    axes[1].set_title("Uncertainty: correct vs wrong predictions")
    for ax in axes:
        if u_max is not None:
            ax.axvline(u_max, color="k", ls="--", lw=1)
        ax.set_xlabel("uncertainty = K / S")
        ax.set_yscale("log")
        ax.legend()
    _save(fig, path)


def decision_scatter(risk, unc, y, policy, path, max_points=20000, seed=0):
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(risk), min(len(risk), max_points), replace=False)
    fig, ax = plt.subplots(figsize=(6.4, 4.8))
    umax_plot = max(float(unc.max()) * 1.05, policy.u_max * 1.1 if np.isfinite(policy.u_max) else 0)
    # decision regions
    ax.axvspan(0, policy.t_low, ymin=0, ymax=min(policy.u_max / umax_plot, 1), color=DEC_COLORS["TRUST"], alpha=0.12)
    ax.axvspan(policy.t_high, 1, ymin=0, ymax=min(policy.u_max / umax_plot, 1), color=DEC_COLORS["REJECT"], alpha=0.12)
    ax.scatter(risk[idx][y[idx] == 0], unc[idx][y[idx] == 0], s=3, alpha=0.35, color=BENIGN, label="legitimate")
    ax.scatter(risk[idx][y[idx] == 1], unc[idx][y[idx] == 1], s=3, alpha=0.35, color=ATTACK, label="attack")
    ax.axvline(policy.t_low, color=DEC_COLORS["TRUST"], lw=1.2)
    ax.axvline(policy.t_high, color=DEC_COLORS["REJECT"], lw=1.2)
    if np.isfinite(policy.u_max):
        ax.axhline(policy.u_max, color="k", ls="--", lw=1)
    ax.set_xlim(0, 1); ax.set_ylim(0, umax_plot)
    ax.set_xlabel("risk"); ax.set_ylabel("uncertainty")
    ax.set_title("Risk x uncertainty -> TRUST / VERIFY / REJECT")
    ax.text(0.01, 0.02, "TRUST", transform=ax.transAxes, color=DEC_COLORS["TRUST"])
    ax.text(0.85, 0.02, "REJECT", transform=ax.transAxes, color=DEC_COLORS["REJECT"])
    ax.text(0.45, 0.93, "VERIFY", transform=ax.transAxes, color=DEC_COLORS["VERIFY"])
    ax.legend(loc="upper right", markerscale=4)
    _save(fig, path)


def reliability_diagram(curves: dict, path):
    """curves: name -> (y, p)."""
    fig, ax = plt.subplots(figsize=(5.2, 5))
    ax.plot([0, 1], [0, 1], "k--", lw=1, label="perfect calibration")
    for name, (y, p) in curves.items():
        conf, acc, cnt = reliability_curve(y, p, 10)
        ok = cnt > 0
        ax.plot(conf[ok], acc[ok], "o-", ms=3, label=name)
    ax.set_xlabel("predicted P(attack)")
    ax.set_ylabel("observed attack frequency")
    ax.set_title("Reliability diagram (test)")
    ax.legend(fontsize=8)
    _save(fig, path)


def risk_coverage(curves: dict, path):
    """Accuracy of the retained predictions when the most uncertain ones are
    deferred to verification. curves: name -> (y, p, u)."""
    fig, ax = plt.subplots(figsize=(5.6, 4))
    for name, (y, p, u) in curves.items():
        order = np.argsort(u)
        correct = ((p[order] >= 0.5).astype(int) == y[order]).astype(float)
        n = np.arange(1, len(u) + 1)
        acc = np.cumsum(correct) / n
        cov = n / len(u)
        step = max(1, len(u) // 400)
        ax.plot(cov[::step], acc[::step], label=name)
    ax.set_xlabel("coverage (fraction decided automatically)")
    ax.set_ylabel("accuracy on decided observations")
    ax.set_title("Deferring uncertain cases to VERIFY")
    ax.legend(fontsize=8)
    _save(fig, path)


def attackwise_bars(table, path, value="F1"):
    """table: DataFrame index = attack, columns = models."""
    fig, ax = plt.subplots(figsize=(11, 4.4))
    n_models = table.shape[1]
    w = 0.8 / n_models
    x = np.arange(len(table))
    for i, col in enumerate(table.columns):
        ax.bar(x + i * w - 0.4 + w / 2, table[col].values, w, label=col)
    ax.set_xticks(x)
    ax.set_xticklabels(table.index, rotation=35, ha="right", fontsize=8)
    ax.set_ylabel(value)
    ax.set_ylim(0, 1.05)
    ax.set_title(f"Attack-wise {value} (test)")
    ax.legend(fontsize=8, ncol=min(n_models, 5))
    _save(fig, path)


def line_plot(x, ys: dict, xlabel, ylabel, title, path, logx=False):
    fig, ax = plt.subplots(figsize=(5.6, 4))
    for name, y in ys.items():
        ax.plot(x, y, "o-", label=name)
    if logx:
        ax.set_xscale("log")
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel); ax.set_title(title)
    if len(ys) > 1:
        ax.legend()
    _save(fig, path)
