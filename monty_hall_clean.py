"""Python equivalent of monty_hall_clean.R."""

from __future__ import annotations

import random
import statistics
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


OUT_DIR = Path("outputs")


def simulate(
    n_experiments: int = 1000,
    n_chances: int = 1000,
    num_doors: int = 4,
) -> tuple[list[int], list[int], dict[str, int]]:
    door_list = list(range(1, num_doors + 1))
    diff_door = 0
    switch_correct = 0
    stay_correct = 0

    success_switch_counts: list[int] = []
    success_stay_counts: list[int] = []

    for _ in range(n_experiments):
        success_switch = 0
        success_stay = 0

        for _ in range(n_chances):
            car = random.choice(door_list)
            guess = random.choice(door_list)

            possible_hall = [door for door in door_list if door not in (guess, car)]
            hall = possible_hall[0] if len(possible_hall) == 1 else random.choice(possible_hall)

            switch_options = [door for door in door_list if door not in (guess, hall)]
            switched_guess = switch_options[0] if len(switch_options) == 1 else random.choice(switch_options)

            if switched_guess == car:
                success_switch += 1
                s_switch = 1
            else:
                s_switch = 0

            if guess == car:
                success_stay += 1
                s_stay = 1
            else:
                s_stay = 0

            if s_stay == 0 and s_switch == 0:
                diff_door += 1
            if s_stay == 0 and s_switch == 1:
                switch_correct += 1
            if s_stay == 1 and s_switch == 0:
                stay_correct += 1

        success_switch_counts.append(success_switch)
        success_stay_counts.append(success_stay)

    counts = {
        "diff_door": diff_door,
        "switch_correct": switch_correct,
        "stay_correct": stay_correct,
    }
    return success_switch_counts, success_stay_counts, counts


def plot(success_switch: list[int], success_stay: list[int], n_chances: int) -> None:
    OUT_DIR.mkdir(exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.hist(success_switch, bins=30, color="red", alpha=0.25, edgecolor="red", label="switch")
    ax.hist(success_stay, bins=30, color="blue", alpha=0.25, edgecolor="blue", label="stay")
    ax.set_title("Monty Hall: switch vs stay")
    ax.set_xlabel(f"successes out of {n_chances} per experiment")
    ax.set_ylabel("frequency")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT_DIR / "clean_switch_vs_stay.png", dpi=160)
    plt.close(fig)


def main() -> None:
    n_experiments = 1000
    n_chances = 1000
    num_doors = 4
    n_total = n_experiments * n_chances

    success_switch, success_stay, counts = simulate(n_experiments, n_chances, num_doors)
    plot(success_switch, success_stay, n_chances)

    print(
        "Mean and SD successes with switch =",
        statistics.fmean(success_switch),
        statistics.stdev(success_switch),
    )
    print(
        "Mean and SD successes without switch =",
        statistics.fmean(success_stay),
        statistics.stdev(success_stay),
    )
    print("Entirely missed =", counts["diff_door"])
    print("Switch correct =", counts["switch_correct"])
    print("Stay correct =", counts["stay_correct"])
    print(counts["diff_door"] + counts["switch_correct"] + counts["stay_correct"])
    print("confirming N_tot =", n_total, "=", n_experiments * n_chances)


if __name__ == "__main__":
    main()
