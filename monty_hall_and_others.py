"""Python equivalent of monty_hall_and_others.R.

This script keeps the exploratory structure of the original R file:
1. a small arrow/path plot,
2. a tiny membership-key demo,
3. a Rademacher sampling demo,
4. a classical Monty Hall simulation comparing switch vs stay.
"""

from __future__ import annotations

import random
import statistics
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


OUT_DIR = Path("outputs")


def ensure_output_dir() -> None:
    OUT_DIR.mkdir(exist_ok=True)


def path_plot() -> None:
    x_values = list(range(11))
    y_values = [x * x + 2 + random.gauss(3, 2) for x in x_values]

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(x_values, y_values, marker="o", color="#2f6f9f")
    for start, end in zip(zip(x_values, y_values), zip(x_values[1:], y_values[1:])):
        ax.annotate(
            "",
            xy=end,
            xytext=start,
            arrowprops={"arrowstyle": "->", "color": "#2f6f9f", "lw": 1.2},
        )
    ax.set_title("Toy path plot")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "and_others_path_plot.png", dpi=160)
    plt.close(fig)


def membership_demo() -> None:
    dd = [{"x": 0, "y": 2}, {"x": 1, "y": 3}]
    key_set = {f"{row['x']}||{row['y']}" for row in dd}

    def check_member(x: int, y: int) -> bool:
        return f"{x}||{y}" in key_set

    print("membership demo data:", dd)
    print("key_set:", sorted(key_set))
    print("check_member(0, 1):", check_member(0, 1))
    print("check_member(1, 3):", check_member(1, 3))


def rademacher_demo(n: int = 100_000) -> None:
    choices = [-1, 1]
    weights = [0.75, 0.25]
    sample_data = random.choices(choices, weights=weights, k=n)
    print("Rademacher mean:", statistics.fmean(sample_data))
    print("Rademacher sd:", statistics.stdev(sample_data))


def simulate_classical_monty(n_experiments: int = 10_000, n_chances: int = 100) -> None:
    doors = [1, 0, 0]
    car = doors.index(1) + 1
    door_list = [1, 2, 3]
    success_switch_counts: list[int] = []
    success_stay_counts: list[int] = []

    for experiment in range(1, n_experiments + 1):
        if experiment % 1000 == 0 or experiment == 1:
            print(f"expt num = {experiment}")

        success_switch = 0
        success_stay = 0

        for _ in range(n_chances):
            guess = random.choice(door_list)

            if guess == car:
                possible_hall = [door for door in door_list if door != guess]
            else:
                possible_hall = [door for door in door_list if door not in (guess, car)]
            hall = random.choice(possible_hall)

            switched_guess = [door for door in door_list if door not in (guess, hall)][0]
            stay_guess = guess

            if switched_guess == car:
                success_switch += 1
            if stay_guess == car:
                success_stay += 1

        success_switch_counts.append(success_switch)
        success_stay_counts.append(success_stay)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.hist(success_switch_counts, bins=30, color="red", alpha=0.25, edgecolor="red", label="switch")
    ax.hist(success_stay_counts, bins=30, color="blue", alpha=0.25, edgecolor="blue", label="stay")
    ax.set_title("Comparing Monty Hall successes with switch and not")
    ax.set_xlabel(f"successes out of {n_chances}")
    ax.set_ylabel("frequency")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT_DIR / "and_others_monty_hist.png", dpi=160)
    plt.close(fig)

    print(
        "Mean and SD successes with switch =",
        statistics.fmean(success_switch_counts),
        statistics.stdev(success_switch_counts),
    )
    print(
        "Mean and SD successes without switch =",
        statistics.fmean(success_stay_counts),
        statistics.stdev(success_stay_counts),
    )


def main() -> None:
    random.seed()
    ensure_output_dir()
    path_plot()
    membership_demo()
    rademacher_demo()
    simulate_classical_monty()


if __name__ == "__main__":
    main()
