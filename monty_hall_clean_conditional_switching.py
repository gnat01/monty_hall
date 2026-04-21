"""Conditional-switching Monty Hall simulation.

This fixes the bookkeeping bug in the R version: whether a switch was
approved is recorded on every trial, not once after an experiment loop.

The script compares three strategies in the generalized K-door, m-prize,
r-reveal game:
    stay: keep the initial door,
    switch: always switch uniformly to another unopened door,
    conditional: switch with probability p, otherwise stay.

If p is omitted, the default is 1 / (K - 1 - r), the probability of choosing
a particular one of the available switch doors after r reveals.
"""

from __future__ import annotations

import argparse
import random
import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import TypedDict

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from monty_hall_generalised import theoretical_probabilities, validate_params


OUT_DIR = Path("outputs")


class Trial(TypedDict):
    car_or_first_prize: int
    guess: int
    opened_count: int
    switched_guess: int
    final_conditional_guess: int
    stay_win: int
    switch_win: int
    conditional_win: int
    switch_approved: int


@dataclass
class ConditionalOutput:
    k: int
    m: int
    r: int
    n_experiments: int
    n_chances: int
    switch_probability: float
    success_stay: list[int]
    success_switch: list[int]
    success_conditional: list[int]
    trials: list[Trial]

    @property
    def total_trials(self) -> int:
        return self.n_experiments * self.n_chances

    @property
    def empirical(self) -> dict[str, float]:
        denom = self.total_trials
        return {
            "stay": sum(self.success_stay) / denom,
            "switch": sum(self.success_switch) / denom,
            "conditional": sum(self.success_conditional) / denom,
        }


def default_switch_probability(k: int, r: int) -> float:
    return 1.0 / (k - 1 - r)


def simulate_conditional_switching(
    k: int = 5,
    m: int = 1,
    r: int = 1,
    n_experiments: int = 1000,
    n_chances: int = 100,
    switch_probability: float | None = None,
    seed: int | None = None,
) -> ConditionalOutput:
    validate_params(k, m, r)
    if switch_probability is None:
        switch_probability = default_switch_probability(k, r)
    if not 0.0 <= switch_probability <= 1.0:
        raise ValueError("Need 0 <= switch_probability <= 1")

    rng = random.Random(seed)
    door_list = list(range(1, k + 1))
    success_stay: list[int] = []
    success_switch: list[int] = []
    success_conditional: list[int] = []
    trials: list[Trial] = []

    for _ in range(n_experiments):
        stay_count = 0
        switch_count = 0
        conditional_count = 0

        for _ in range(n_chances):
            prize_doors = set(rng.sample(door_list, m))
            guess = rng.choice(door_list)
            monty_options = [door for door in door_list if door != guess and door not in prize_doors]
            opened = set() if r == 0 else set(rng.sample(monty_options, r))
            switch_options = [door for door in door_list if door != guess and door not in opened]
            switched_guess = rng.choice(switch_options)

            switch_approved = 1 if rng.random() <= switch_probability else 0
            final_conditional_guess = switched_guess if switch_approved else guess

            stay_win = 1 if guess in prize_doors else 0
            switch_win = 1 if switched_guess in prize_doors else 0
            conditional_win = 1 if final_conditional_guess in prize_doors else 0

            stay_count += stay_win
            switch_count += switch_win
            conditional_count += conditional_win

            trials.append(
                {
                    "car_or_first_prize": min(prize_doors),
                    "guess": guess,
                    "opened_count": len(opened),
                    "switched_guess": switched_guess,
                    "final_conditional_guess": final_conditional_guess,
                    "stay_win": stay_win,
                    "switch_win": switch_win,
                    "conditional_win": conditional_win,
                    "switch_approved": switch_approved,
                }
            )

        success_stay.append(stay_count)
        success_switch.append(switch_count)
        success_conditional.append(conditional_count)

    return ConditionalOutput(
        k=k,
        m=m,
        r=r,
        n_experiments=n_experiments,
        n_chances=n_chances,
        switch_probability=switch_probability,
        success_stay=success_stay,
        success_switch=success_switch,
        success_conditional=success_conditional,
        trials=trials,
    )


def theoretical_conditional(k: int, m: int, r: int, switch_probability: float) -> dict[str, float]:
    theory = theoretical_probabilities(k, m, r)
    conditional = (1.0 - switch_probability) * theory["stay"] + switch_probability * theory["switch"]
    return {**theory, "conditional": conditional}


def plot(out: ConditionalOutput) -> Path:
    OUT_DIR.mkdir(exist_ok=True)
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.hist(out.success_switch, bins=30, color="#d94841", alpha=0.25, edgecolor="#d94841", label="always switch")
    ax.hist(out.success_stay, bins=30, color="#276fbf", alpha=0.25, edgecolor="#276fbf", label="stay")
    ax.hist(
        out.success_conditional,
        bins=30,
        color="#2a9d8f",
        alpha=0.25,
        edgecolor="#2a9d8f",
        label=f"conditional p={out.switch_probability:.3g}",
    )
    ax.set_title(f"Conditional switching: K={out.k}, m={out.m}, r={out.r}")
    ax.set_xlabel(f"successes out of {out.n_chances} per experiment")
    ax.set_ylabel("frequency")
    ax.legend()
    fig.tight_layout()
    path = OUT_DIR / f"conditional_K{out.k}_m{out.m}_r{out.r}.png"
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--K", "--k", dest="k", type=int, default=5, help="number of doors")
    parser.add_argument("--m", type=int, default=1, help="number of prize doors")
    parser.add_argument("--r", type=int, default=1, help="number of losing doors opened")
    parser.add_argument("--experiments", type=int, default=1000, help="outer simulation runs")
    parser.add_argument("--chances", type=int, default=100, help="trials per experiment")
    parser.add_argument("--switch-probability", type=float, default=None, help="probability of taking the switch")
    parser.add_argument("--seed", type=int, default=None, help="random seed")
    parser.add_argument("--plot", action="store_true", help="save a histogram plot")
    return parser.parse_args()


def summarize_counts(label: str, values: list[int]) -> None:
    print(f"{label}: mean={statistics.fmean(values):.4f}, sd={statistics.stdev(values):.4f}")


def main() -> None:
    args = parse_args()
    out = simulate_conditional_switching(
        k=args.k,
        m=args.m,
        r=args.r,
        n_experiments=args.experiments,
        n_chances=args.chances,
        switch_probability=args.switch_probability,
        seed=args.seed,
    )
    theory = theoretical_conditional(out.k, out.m, out.r, out.switch_probability)

    print(f"K={out.k}, m={out.m}, r={out.r}, switch_probability={out.switch_probability:.6g}")
    print("theory:", theory)
    print("empirical:", out.empirical)
    summarize_counts("stay successes", out.success_stay)
    summarize_counts("always-switch successes", out.success_switch)
    summarize_counts("conditional successes", out.success_conditional)
    print("switches approved:", sum(row["switch_approved"] for row in out.trials), "of", out.total_trials)

    if args.plot:
        print("Saved plot:", plot(out))


if __name__ == "__main__":
    main()
