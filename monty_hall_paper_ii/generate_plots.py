from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from monty_hall_variable_costs import cost_sequence, marginal_value, solve_from_family


plt.rcParams.update(
    {
        "figure.facecolor": "#f7f2e8",
        "axes.facecolor": "#f7f2e8",
        "axes.edgecolor": "#2f2a24",
        "axes.labelcolor": "#2f2a24",
        "axes.titleweight": "bold",
        "font.size": 11,
        "grid.color": "#e3d7c3",
        "grid.linewidth": 0.8,
        "legend.frameon": False,
        "xtick.color": "#2f2a24",
        "ytick.color": "#2f2a24",
    }
)


COLORS = {
    "ink": "#2f2a24",
    "teal": "#0f766e",
    "red": "#b23a30",
    "gold": "#b7791f",
    "blue": "#22577a",
    "green": "#4d7c0f",
    "slate": "#475569",
}


def savefig(name: str) -> None:
    plt.tight_layout()
    plt.savefig(name, dpi=320)
    plt.close()


def fig_cost_shapes() -> None:
    k, m = 50, 1
    t = np.arange(k - m - 1)
    linear = cost_sequence("linear", len(t), base=0.002, slope=0.00055)
    sat = cost_sequence("saturating", len(t), base=0.002, saturation=0.022, tau=9.0)
    lin_sat = cost_sequence("linear_saturating", len(t), base=0.002, slope=0.0018, saturation=0.024)
    delta = [marginal_value(k, m, int(i)) for i in t]

    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    ax.plot(t, delta, color=COLORS["ink"], linewidth=2.4, label=r"benefit $\Delta_t$")
    ax.plot(t, linear, color=COLORS["red"], linewidth=2.1, label="linear cost")
    ax.plot(t, sat, color=COLORS["teal"], linewidth=2.1, label="smooth saturation")
    ax.plot(t, lin_sat, color=COLORS["gold"], linewidth=2.1, label="linear + cap")
    ax.set_title("Benefits rise; costs may rise, bend, or saturate")
    ax.set_xlabel(r"reveal index $t$")
    ax.set_ylabel(r"one-step amount")
    ax.set_ylim(0, max(max(delta), max(lin_sat)) * 1.08)
    ax.legend()
    ax.grid(True)
    savefig("fig_cost_shapes.png")


def fig_linear_regimes() -> None:
    k, m = 50, 1
    cases = [
        ("low slope: full reveal", 0.0015, 0.00008, COLORS["teal"]),
        ("moderate: early interior optimum", 0.0, 0.0010, COLORS["gold"]),
        ("high slope: no reveal", 0.026, 0.0010, COLORS["red"]),
    ]
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    for label, base, slope, color in cases:
        out = solve_from_family(k, m, "linear", base=base, slope=slope)
        t = np.arange(out.max_reveals + 1)
        ax.plot(t, out.net_value, linewidth=2.2, color=color, label=label)
        ax.scatter([out.optimal_t], [out.optimal_value], color=color, s=42, zorder=4)
    ax.set_title("Linear cost growth creates richer stopping behavior")
    ax.set_xlabel(r"reveals purchased $t$")
    ax.set_ylabel(r"net value $W(t)$")
    ax.legend()
    ax.grid(True)
    savefig("fig_linear_regimes.png")


def fig_saturation_pushthrough() -> None:
    k, m = 50, 1
    linear = solve_from_family(k, m, "linear", base=0.004, slope=0.00055)
    sat = solve_from_family(k, m, "linear_saturating", base=0.004, slope=0.0018, saturation=0.022)
    smooth = solve_from_family(k, m, "saturating", base=0.004, saturation=0.026, tau=8.0)
    t = np.arange(linear.max_reveals + 1)

    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    for out, label, color in [
        (linear, "linear costs", COLORS["red"]),
        (sat, "linear + cap", COLORS["gold"]),
        (smooth, "smooth saturation", COLORS["teal"]),
    ]:
        ax.plot(t, out.net_value, linewidth=2.25, color=color, label=f"{label}, t*={out.optimal_t}")
        ax.scatter([out.optimal_t], [out.optimal_value], color=color, s=38, zorder=4)
    ax.set_title("Saturation can restore the push-through effect")
    ax.set_xlabel(r"reveals purchased $t$")
    ax.set_ylabel(r"net value $W(t)$")
    ax.legend()
    ax.grid(True)
    savefig("fig_saturation_pushthrough.png")


def fig_linear_phase_diagram() -> None:
    k, m = 50, 1
    bases = np.linspace(0.0, 0.04, 90)
    slopes = np.linspace(0.0, 0.0012, 90)
    z = np.zeros((len(slopes), len(bases)))
    for i, slope in enumerate(slopes):
        for j, base in enumerate(bases):
            out = solve_from_family(k, m, "linear", base=float(base), slope=float(slope))
            z[i, j] = out.optimal_t / out.max_reveals

    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    im = ax.imshow(
        z,
        origin="lower",
        aspect="auto",
        extent=[bases.min(), bases.max(), slopes.min(), slopes.max()],
        cmap="viridis",
        vmin=0,
        vmax=1,
    )
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label(r"optimal fraction $t^*/T$")
    ax.set_title("Phase diagram for linear reveal costs")
    ax.set_xlabel(r"base cost $a$")
    ax.set_ylabel(r"slope $b$ in $c_t=a+bt$")
    savefig("fig_linear_phase.png")


def fig_saturating_phase_diagram() -> None:
    k, m = 50, 1
    bases = np.linspace(0.0, 0.04, 90)
    caps = np.linspace(0.0, 0.055, 90)
    z = np.zeros((len(caps), len(bases)))
    for i, cap in enumerate(caps):
        for j, base in enumerate(bases):
            out = solve_from_family(k, m, "linear_saturating", base=float(base), slope=0.0018, saturation=float(cap))
            z[i, j] = out.optimal_t / out.max_reveals

    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    im = ax.imshow(
        z,
        origin="lower",
        aspect="auto",
        extent=[bases.min(), bases.max(), caps.min(), caps.max()],
        cmap="magma",
        vmin=0,
        vmax=1,
    )
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label(r"optimal fraction $t^*/T$")
    ax.set_title("Phase diagram for costs that rise then saturate")
    ax.set_xlabel(r"base cost $a$")
    ax.set_ylabel(r"saturation increment")
    savefig("fig_saturating_phase.png")


if __name__ == "__main__":
    fig_cost_shapes()
    fig_linear_regimes()
    fig_saturation_pushthrough()
    fig_linear_phase_diagram()
    fig_saturating_phase_diagram()
    print("Generated Part II figures.")
