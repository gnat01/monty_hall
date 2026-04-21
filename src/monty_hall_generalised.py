"""Generalized Monty Hall simulations.

Model:
    K doors, m prize doors, r losing doors opened by a knowledgeable host.
    The contestant may stay with the initial door or switch uniformly to one
    other unopened, non-initial door.

Theoretical probabilities:
    P(stay wins) = m / K
    P(switch wins) = m (K - 1) / (K (K - 1 - r))
"""

from __future__ import annotations

import argparse
import random
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


OUT_DIR = Path("outputs")


@dataclass(frozen=True)
class Params:
    k: int
    m: int
    r: int
    n_experiments: int
    n_chances: int


@dataclass
class SimulationOutput:
    params: Params
    theory: dict[str, float]
    empirical: dict[str, float]
    raw: list[dict[str, int]]


def validate_params(k: int, m: int, r: int) -> None:
    if k < 3:
        raise ValueError("Need K >= 3")
    if m < 1 or m >= k:
        raise ValueError("Need 1 <= m < K")
    if r < 0 or r > (k - m - 1):
        raise ValueError("Need 0 <= r <= K - m - 1")


def theoretical_probabilities(k: int, m: int, r: int) -> dict[str, float]:
    validate_params(k, m, r)
    return {
        "stay": m / k,
        "switch": m * (k - 1) / (k * (k - 1 - r)),
    }


def simulate_monty_general(
    k: int = 3,
    m: int = 1,
    r: int = 1,
    n_experiments: int = 10_000,
    n_chances: int = 100,
    seed: int | None = None,
) -> SimulationOutput:
    validate_params(k, m, r)
    rng = random.Random(seed)

    door_list = list(range(1, k + 1))
    results: list[dict[str, int]] = []

    for experiment in range(1, n_experiments + 1):
        success_stay = 0
        success_switch = 0

        for _ in range(n_chances):
            prize_doors = set(rng.sample(door_list, m))
            guess = rng.choice(door_list)

            monty_options = [door for door in door_list if door != guess and door not in prize_doors]
            opened = set() if r == 0 else set(rng.sample(monty_options, r))

            if guess in prize_doors:
                success_stay += 1

            switch_options = [door for door in door_list if door != guess and door not in opened]
            switched_guess = rng.choice(switch_options)

            if switched_guess in prize_doors:
                success_switch += 1

        results.append(
            {
                "experiment": experiment,
                "success_stay": success_stay,
                "success_switch": success_switch,
            }
        )

    theory = theoretical_probabilities(k, m, r)

    empirical_stay = sum(row["success_stay"] for row in results) / (n_experiments * n_chances)
    empirical_switch = sum(row["success_switch"] for row in results) / (n_experiments * n_chances)

    return SimulationOutput(
        params=Params(k, m, r, n_experiments, n_chances),
        theory=theory,
        empirical={"stay": empirical_stay, "switch": empirical_switch},
        raw=results,
    )


def plot_results(out: SimulationOutput, filename: str | None = None) -> Path:
    OUT_DIR.mkdir(exist_ok=True)
    strategies = ["stay", "switch"]
    theory = [out.theory[strategy] for strategy in strategies]
    empirical = [out.empirical[strategy] for strategy in strategies]

    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    ax.scatter(strategies, theory, s=80, color="red", label="theory", zorder=3)
    ax.scatter(strategies, empirical, s=90, color="blue", alpha=0.75, label="empirical", zorder=3)
    ax.set_ylim(0, 1)
    ax.set_ylabel("Probability of winning")
    ax.set_title(
        f"Monty Hall Generalization: K={out.params.k}, m={out.params.m}, r={out.params.r}"
    )
    ax.grid(axis="y", alpha=0.25)
    ax.legend()
    fig.tight_layout()

    if filename is None:
        filename = f"generalised_K{out.params.k}_m{out.params.m}_r{out.params.r}.png"
    path = OUT_DIR / filename
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def print_output(label: str, out: SimulationOutput) -> None:
    print(label)
    print("  theory:", out.theory)
    print("  empirical:", out.empirical)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--K", "--k", dest="k", type=int, default=3, help="number of doors")
    parser.add_argument("--m", type=int, default=1, help="number of prize doors")
    parser.add_argument("--r", type=int, default=1, help="number of losing doors opened")
    parser.add_argument("--experiments", type=int, default=10_000, help="outer simulation runs")
    parser.add_argument("--chances", type=int, default=100, help="trials per experiment")
    parser.add_argument("--seed", type=int, default=None, help="random seed")
    parser.add_argument("--plot", action="store_true", help="save a theory-vs-empirical plot")
    parser.add_argument("--demo", action="store_true", help="run the original four demonstration cases")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.demo:
        cases = [
            ("Classical Monty Hall", dict(k=3, m=1, r=1)),
            ("10 doors, 1 prize, 1 door opened", dict(k=10, m=1, r=1)),
            ("10 doors, 1 prize, 8 doors opened", dict(k=10, m=1, r=8)),
            ("10 doors, 3 prizes, 4 doors opened", dict(k=10, m=3, r=4)),
        ]
        for label, params in cases:
            out = simulate_monty_general(
                **params,
                n_experiments=args.experiments,
                n_chances=args.chances,
                seed=args.seed,
            )
            print_output(label, out)
        return

    out = simulate_monty_general(
        k=args.k,
        m=args.m,
        r=args.r,
        n_experiments=args.experiments,
        n_chances=args.chances,
        seed=args.seed,
    )
    print_output("Generalized Monty Hall", out)
    if args.plot:
        path = plot_results(out)
        print("Saved plot:", path)


if __name__ == "__main__":
    main()
