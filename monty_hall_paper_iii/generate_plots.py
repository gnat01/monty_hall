from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from monty_hall_heterogeneous import DoorPrior, simulate_door_specific, simulate_exchangeable


plt.rcParams.update(
    {
        "figure.facecolor": "#f8f4ea",
        "axes.facecolor": "#f8f4ea",
        "axes.edgecolor": "#302a22",
        "axes.labelcolor": "#302a22",
        "axes.titleweight": "bold",
        "font.size": 11,
        "grid.color": "#e7dcc8",
        "grid.linewidth": 0.8,
        "legend.frameon": False,
        "xtick.color": "#302a22",
        "ytick.color": "#302a22",
    }
)

COLORS = {
    "ink": "#302a22",
    "teal": "#0f766e",
    "red": "#b23a30",
    "gold": "#b7791f",
    "blue": "#22577a",
    "green": "#4d7c0f",
    "purple": "#6d597a",
}


def savefig(name: str) -> None:
    plt.tight_layout()
    plt.savefig(name, dpi=320)
    plt.close()


def fig_exchangeable_collapse() -> None:
    configs = ["fixed", "uniform", "exponential", "lognormal", "pareto"]
    empirical = []
    theory = []
    for i, dist in enumerate(configs):
        out = simulate_exchangeable(k=12, m=4, r=4, reward_dist=dist, trials=45_000, seed=100 + i)
        empirical.append(out.empirical_switch)
        theory.append(out.theory_switch)

    x = np.arange(len(configs))
    width = 0.36
    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    ax.bar(x - width / 2, theory, width, color=COLORS["teal"], label="theory")
    ax.bar(x + width / 2, empirical, width, color=COLORS["gold"], label="simulation")
    ax.set_xticks(x)
    ax.set_xticklabels(configs, rotation=18)
    ax.set_ylabel("Expected switch reward")
    ax.set_title("Exchangeable heterogeneous rewards collapse to total mass")
    ax.legend()
    ax.grid(axis="y")
    savefig("fig_exchangeable_collapse.png")


def fig_prior_landscape() -> None:
    priors = [
        DoorPrior(0.1, 4.0),
        DoorPrior(0.4, 3.0),
        DoorPrior(0.8, 2.0),
        DoorPrior(0.95, 1.0),
        DoorPrior(0.55, 5.0),
        DoorPrior(0.72, 8.0),
    ]
    x = np.arange(1, len(priors) + 1)
    q = [p.zero_prob for p in priors]
    v = [p.reward_value for p in priors]
    mu = [p.mean for p in priors]

    fig, ax1 = plt.subplots(figsize=(7.4, 4.4))
    ax1.bar(x - 0.18, mu, width=0.36, color=COLORS["blue"], label=r"prior mean $\mu_j$")
    ax1.bar(x + 0.18, v, width=0.36, color=COLORS["gold"], alpha=0.7, label=r"value if nonzero $v_j$")
    ax1.set_xlabel("door")
    ax1.set_ylabel("reward scale")
    ax2 = ax1.twinx()
    ax2.plot(x, q, color=COLORS["red"], marker="o", linewidth=2.0, label=r"zero probability $q_j$")
    ax2.set_ylabel(r"$q_j$")
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")
    ax1.set_title("Door-specific priors create labeled heterogeneity")
    ax1.grid(axis="y")
    savefig("fig_prior_landscape.png")


def fig_strategy_comparison() -> None:
    priors = [
        DoorPrior(0.9, 1.0),
        DoorPrior(0.8, 1.5),
        DoorPrior(0.2, 4.0),
        DoorPrior(0.7, 2.0),
        DoorPrior(0.95, 10.0),
    ]
    out = simulate_door_specific(
        k=5,
        r=1,
        trials=80_000,
        seed=7,
        initial_strategy="lowest_mu",
        monty_policy="uniform_zero",
        priors=priors,
    )
    labels = ["stay", "uniform_switch", "prior_best_switch", "oracle_best_switch"]
    values = [out.strategy_values[label] for label in labels]
    pretty = ["stay", "uniform\nswitch", "prior-best\nswitch", "oracle\nupper bound"]

    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    ax.bar(pretty, values, color=[COLORS["blue"], COLORS["teal"], COLORS["gold"], COLORS["red"]])
    ax.set_ylabel("Empirical reward")
    ax.set_title("Door-specific priors make switching rules diverge")
    ax.grid(axis="y")
    savefig("fig_strategy_comparison.png")


def fig_sacrifice_choice() -> None:
    priors = [
        DoorPrior(0.1, 4.0),
        DoorPrior(0.4, 3.0),
        DoorPrior(0.8, 2.0),
        DoorPrior(0.95, 1.0),
    ]
    high = simulate_door_specific(
        k=4,
        r=1,
        trials=80_000,
        seed=11,
        initial_strategy="highest_mu",
        monty_policy="uniform_zero",
        priors=priors,
    )
    low = simulate_door_specific(
        k=4,
        r=1,
        trials=80_000,
        seed=12,
        initial_strategy="lowest_mu",
        monty_policy="uniform_zero",
        priors=priors,
    )
    labels = ["stay", "uniform_switch", "prior_best_switch"]
    x = np.arange(len(labels))
    width = 0.35
    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    ax.bar(x - width / 2, [high.strategy_values[l] for l in labels], width, color=COLORS["red"], label="initial = highest mean")
    ax.bar(x + width / 2, [low.strategy_values[l] for l in labels], width, color=COLORS["teal"], label="initial = lowest mean")
    ax.set_xticks(x)
    ax.set_xticklabels(["stay", "uniform\nswitch", "prior-best\nswitch"])
    ax.set_ylabel("Empirical reward")
    ax.set_title("A low-value initial choice can preserve better switch options")
    ax.legend()
    ax.grid(axis="y")
    savefig("fig_sacrifice_choice.png")


def fig_monty_policy_effect() -> None:
    priors = [
        DoorPrior(0.2, 6.0),
        DoorPrior(0.55, 5.0),
        DoorPrior(0.75, 3.0),
        DoorPrior(0.9, 8.0),
        DoorPrior(0.4, 2.0),
        DoorPrior(0.82, 9.0),
    ]
    policies = ["uniform_zero", "low_mu_zero", "high_mu_zero"]
    values = []
    for i, policy in enumerate(policies):
        out = simulate_door_specific(
            k=6,
            r=2,
            trials=70_000,
            seed=20 + i,
            initial_strategy="random",
            monty_policy=policy,
            priors=priors,
        )
        values.append(out.strategy_values["prior_best_switch"])

    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    ax.bar(["uniform zero", "low-$\\mu$ zero", "high-$\\mu$ zero"], values, color=[COLORS["teal"], COLORS["blue"], COLORS["gold"]])
    ax.set_ylabel("Prior-best switch reward")
    ax.set_title("With labeled priors, Monty's reveal policy matters")
    ax.grid(axis="y")
    savefig("fig_monty_policy_effect.png")


if __name__ == "__main__":
    fig_exchangeable_collapse()
    fig_prior_landscape()
    fig_strategy_comparison()
    fig_sacrifice_choice()
    fig_monty_policy_effect()
    print("Generated Part III figures.")
