from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt


plt.rcParams.update(
    {
        "figure.facecolor": "#fbf7ef",
        "axes.facecolor": "#fbf7ef",
        "axes.edgecolor": "#34312d",
        "axes.labelcolor": "#34312d",
        "axes.titleweight": "bold",
        "font.size": 11,
        "grid.color": "#e8dfcf",
        "grid.linewidth": 0.8,
        "legend.frameon": False,
        "xtick.color": "#34312d",
        "ytick.color": "#34312d",
    }
)


COLORS = {
    "teal": "#0f766e",
    "red": "#bf3f2f",
    "gold": "#c98200",
    "blue": "#22577a",
    "slate": "#475569",
    "green": "#4d7c0f",
}


def S(K: int, m: int, t):
    return m * (K - 1) / (K * (K - 1 - t))


def delta(K: int, m: int, t):
    return m * (K - 1) / (K * (K - 2 - t) * (K - 1 - t))


def t_star(K: int, m: int, c: float) -> int:
    t = np.arange(0, K - m)
    return int(t[np.argmax(S(K, m, t) - c * t)])


def savefig(name: str) -> None:
    plt.tight_layout()
    plt.savefig(name, dpi=320)
    plt.close()


def fig_success_curve() -> None:
    K, m = 50, 1
    t = np.arange(0, K - m)
    y = S(K, m, t)

    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    ax.plot(t, y, color=COLORS["teal"], linewidth=2.6)
    ax.scatter([0, K - m - 1], [S(K, m, 0), S(K, m, K - m - 1)], color=COLORS["red"], zorder=3)
    ax.annotate(r"$S(0)=1/K$", xy=(0, S(K, m, 0)), xytext=(6, 0.14), arrowprops={"arrowstyle": "->", "color": COLORS["slate"]})
    ax.annotate(r"$S(T)=(K-1)/K$", xy=(K - m - 1, S(K, m, K - m - 1)), xytext=(24, 0.82), arrowprops={"arrowstyle": "->", "color": COLORS["slate"]})
    ax.set_title(r"Eliminative information concentrates success probability")
    ax.set_xlabel(r"reveals $t$")
    ax.set_ylabel(r"switch success probability $S(t)$")
    ax.set_ylim(0, 1.04)
    ax.grid(True)
    savefig("fig_S.png")


def fig_net_value() -> None:
    K, m = 50, 1
    threshold = 1 / K
    t = np.arange(0, K - m)
    costs = [0.008, threshold, 0.032]
    labels = [r"$c<1/K$", r"$c=1/K$", r"$c>1/K$"]
    colors = [COLORS["teal"], COLORS["gold"], COLORS["red"]]

    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    for c, label, color in zip(costs, labels, colors):
        W = S(K, m, t) - c * t
        ax.plot(t, W, linewidth=2.4, color=color, label=label)
        ax.scatter([t[np.argmax(W)]], [np.max(W)], color=color, s=36, zorder=4)
    ax.axhline(S(K, m, 0), color=COLORS["slate"], linestyle=":", linewidth=1.2)
    ax.set_title(r"Net value selects an endpoint")
    ax.set_xlabel(r"reveals $t$")
    ax.set_ylabel(r"$W(t)=S(t)-ct$")
    ax.legend()
    ax.grid(True)
    savefig("fig_W.png")


def fig_phase_transition() -> None:
    K, m = 50, 1
    scaled_cost = np.linspace(0.2, 1.8, 600)
    c_vals = scaled_cost / K
    stars = np.array([t_star(K, m, c) for c in c_vals])

    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    ax.plot(scaled_cost, stars / (K - m - 1), color=COLORS["blue"], linewidth=2.6)
    ax.axvline(1, color=COLORS["red"], linestyle="--", linewidth=1.6, label=r"$cK=1$")
    ax.set_title(r"Optimal policy has a sharp threshold")
    ax.set_xlabel(r"scaled cost $cK$")
    ax.set_ylabel(r"fraction of maximum reveals $t^*/T$")
    ax.set_ylim(-0.04, 1.04)
    ax.legend()
    ax.grid(True)
    savefig("fig_tstar.png")


def fig_marginal_value() -> None:
    K, m = 50, 1
    t = np.arange(0, K - m - 1)
    y = delta(K, m, t)

    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    ax.plot(t, y, color=COLORS["green"], linewidth=2.5)
    ax.fill_between(t, 0, y, color=COLORS["green"], alpha=0.18)
    ax.axhline(1 / K, color=COLORS["red"], linestyle="--", linewidth=1.4, label=r"global threshold $1/K$")
    ax.set_title(r"Marginal value increases rather than diminishes")
    ax.set_xlabel(r"reveals already purchased $t$")
    ax.set_ylabel(r"$\Delta_t=S(t+1)-S(t)$")
    ax.legend()
    ax.grid(True)
    savefig("fig_marginal.png")


def fig_multik_transition() -> None:
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    for K, color in zip([10, 20, 50, 100], [COLORS["teal"], COLORS["gold"], COLORS["blue"], COLORS["red"]]):
        m = 1
        scaled_cost = np.linspace(0.2, 1.8, 700)
        c_vals = scaled_cost / K
        stars = np.array([t_star(K, m, c) for c in c_vals])
        ax.plot(scaled_cost, stars / (K - m - 1), linewidth=2.1, color=color, label=fr"$K={K}$")
    ax.axvline(1, color=COLORS["slate"], linestyle="--", linewidth=1.4)
    ax.set_title(r"Scaling collapse across problem sizes")
    ax.set_xlabel(r"scaled cost $cK$")
    ax.set_ylabel(r"$t^*/T$")
    ax.set_ylim(-0.04, 1.04)
    ax.legend(ncol=2)
    ax.grid(True)
    savefig("fig_multiK_tstar.png")


def fig_cstar_scaling() -> None:
    K_vals = np.arange(5, 151)
    c_star = 1 / K_vals

    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    ax.plot(K_vals, c_star, color=COLORS["red"], linewidth=2.4, label=r"exact $c^*(K)=1/K$")
    ax.scatter([10, 20, 50, 100], 1 / np.array([10, 20, 50, 100]), color=COLORS["blue"], zorder=3, label="plotted experiments")
    ax.set_title(r"The critical cost is exactly inverse in $K$")
    ax.set_xlabel(r"number of doors $K$")
    ax.set_ylabel(r"critical cost $c^*$")
    ax.legend()
    ax.grid(True)
    savefig("fig_cstar_scaling.png")


if __name__ == "__main__":
    fig_success_curve()
    fig_net_value()
    fig_phase_transition()
    fig_marginal_value()
    fig_multik_transition()
    fig_cstar_scaling()
    print("Generated paper figures.")
