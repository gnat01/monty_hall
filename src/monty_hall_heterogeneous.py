"""Heterogeneous-reward Monty Hall models.

Two models are intentionally kept separate:

1. Exchangeable reward multiset:
   rewards v_1,...,v_m plus zeros are randomly permuted among K doors.
   Under uniform switching, expected values collapse to total reward mass V.

2. Door-specific Bernoulli-value priors:
   door j has X_j = 0 with probability q_j and X_j = v_j otherwise.
   Door labels carry information through prior means mu_j=(1-q_j)v_j.
"""

from __future__ import annotations

import argparse
import csv
import random
import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


OUT_DIR = Path("outputs")
RewardDist = Literal["fixed", "uniform", "exponential", "lognormal", "pareto"]
InitialStrategy = Literal["random", "highest_mu", "lowest_mu"]
SwitchStrategy = Literal["stay", "uniform_switch", "prior_best_switch", "oracle_best_switch"]
MontyPolicy = Literal["uniform_zero", "low_mu_zero", "high_mu_zero"]


@dataclass(frozen=True)
class DoorPrior:
    zero_prob: float
    reward_value: float

    @property
    def mean(self) -> float:
        return (1.0 - self.zero_prob) * self.reward_value


@dataclass
class ExchangeableOutput:
    k: int
    m: int
    r: int
    reward_dist: str
    trials: int
    mean_total_reward: float
    empirical_stay: float
    empirical_switch: float
    theory_stay: float
    theory_switch: float


@dataclass
class DoorSpecificOutput:
    k: int
    r: int
    trials: int
    initial_strategy: str
    monty_policy: str
    means: dict[str, float]
    strategy_values: dict[str, float]
    priors: list[DoorPrior]


def validate_exchangeable(k: int, m: int, r: int) -> None:
    if k < 3:
        raise ValueError("Need K >= 3")
    if m < 1 or m >= k:
        raise ValueError("Need 1 <= m < K")
    if r < 0 or r > k - m - 1:
        raise ValueError("Need 0 <= r <= K - m - 1")


def parse_reward_values(raw: str) -> list[float]:
    values = [float(part.strip()) for part in raw.split(",") if part.strip()]
    if not values:
        raise ValueError("Need at least one explicit reward value")
    if any(value <= 0 for value in values):
        raise ValueError("Explicit reward values must be strictly positive")
    return values


def parse_reward_vector_sets(raw: str) -> list[list[float]]:
    vectors = [parse_reward_values(chunk) for chunk in raw.split(";") if chunk.strip()]
    if not vectors:
        raise ValueError("Need at least one reward vector")
    return vectors


def sample_positive_rewards(
    m: int,
    rng: random.Random,
    kind: RewardDist = "lognormal",
    fixed_value: float = 1.0,
    low: float = 0.25,
    high: float = 2.0,
    scale: float = 1.0,
    log_mu: float = 0.0,
    log_sigma: float = 1.0,
    pareto_alpha: float = 2.5,
) -> list[float]:
    if m < 1:
        raise ValueError("Need m >= 1")
    if kind == "fixed":
        return [fixed_value] * m
    if kind == "uniform":
        return [rng.uniform(low, high) for _ in range(m)]
    if kind == "exponential":
        return [rng.expovariate(1.0 / scale) for _ in range(m)]
    if kind == "lognormal":
        return [rng.lognormvariate(log_mu, log_sigma) for _ in range(m)]
    if kind == "pareto":
        return [scale * rng.paretovariate(pareto_alpha) for _ in range(m)]
    raise ValueError(f"unknown reward distribution: {kind}")


def place_rewards_exchangeably(k: int, rewards: list[float], rng: random.Random) -> list[float]:
    if len(rewards) > k:
        raise ValueError("Need at most K positive rewards")
    values = rewards + [0.0] * (k - len(rewards))
    rng.shuffle(values)
    return values


def legal_zero_doors(rewards: list[float], initial: int, opened: set[int]) -> list[int]:
    return [idx for idx, reward in enumerate(rewards) if idx != initial and idx not in opened and reward == 0.0]


def switch_options(k: int, initial: int, opened: set[int]) -> list[int]:
    return [idx for idx in range(k) if idx != initial and idx not in opened]


def reveal_doors_uniform_zero(
    rewards: list[float],
    initial: int,
    r: int,
    rng: random.Random,
) -> set[int]:
    legal = legal_zero_doors(rewards, initial, set())
    if len(legal) < r:
        raise ValueError("not enough legal zero doors to reveal")
    return set(rng.sample(legal, r))


def exchangeable_theory(k: int, m: int, r: int, total_reward: float) -> dict[str, float]:
    validate_exchangeable(k, m, r)
    return {
        "stay": total_reward / k,
        "switch": total_reward * (k - 1) / (k * (k - 1 - r)),
    }


def exchangeable_curve_rows(
    k: int,
    m: int,
    reward_dist: RewardDist = "lognormal",
    reward_values: list[float] | None = None,
    trials: int = 100_000,
    seed: int | None = None,
    label: str | None = None,
) -> list[dict[str, float | str]]:
    validate_exchangeable(k, m, 0)
    total_reward = sum(reward_values) if reward_values is not None else None
    rows: list[dict[str, float | str]] = []
    for r in range(0, k - m):
        out = simulate_exchangeable(
            k=k,
            m=m,
            r=r,
            reward_dist=reward_dist,
            reward_values=reward_values,
            trials=trials,
            seed=None if seed is None else seed + 10_000 * r,
        )
        current_total_reward = total_reward if total_reward is not None else out.mean_total_reward
        rows.append(
            {
                "label": label or (",".join(f"{value:g}" for value in reward_values) if reward_values is not None else reward_dist),
                "k": float(k),
                "m": float(m),
                "r": float(r),
                "total_reward": current_total_reward,
                "empirical_stay": out.empirical_stay,
                "theory_stay": out.theory_stay,
                "empirical_switch": out.empirical_switch,
                "theory_switch": out.theory_switch,
                "empirical_stay_per_total": out.empirical_stay / current_total_reward,
                "theory_stay_per_total": out.theory_stay / current_total_reward,
                "empirical_switch_per_total": out.empirical_switch / current_total_reward,
                "theory_switch_per_total": out.theory_switch / current_total_reward,
            }
        )
    return rows


def write_exchangeable_rows_csv(rows: list[dict[str, float | str]], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return path


def plot_exchangeable_theory_vs_empirical(rows: list[dict[str, float | str]], path: Path) -> Path:
    OUT_DIR.mkdir(exist_ok=True)
    r_vals = [row["r"] for row in rows]
    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    ax.plot(r_vals, [row["theory_stay"] for row in rows], color="#22577a", linewidth=2.2, label="stay theory")
    ax.plot(r_vals, [row["theory_switch"] for row in rows], color="#b7791f", linewidth=2.2, label="switch theory")
    ax.scatter(r_vals, [row["empirical_stay"] for row in rows], color="#22577a", s=34, alpha=0.85, label="stay empirical")
    ax.scatter(r_vals, [row["empirical_switch"] for row in rows], color="#b7791f", s=34, alpha=0.85, label="switch empirical")
    ax.set_xlabel("reveals r")
    ax.set_ylabel("expected reward")
    ax.set_title("Exchangeable unequal prizes: theory vs empirical")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(ncol=2)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def plot_exchangeable_collapse(rows: list[dict[str, float | str]], path: Path, *, normalized: bool) -> Path:
    grouped: dict[str, list[dict[str, float | str]]] = {}
    for row in rows:
        grouped.setdefault(str(row["label"]), []).append(row)
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    colors = ["#22577a", "#0f766e", "#b7791f", "#b23a30", "#6d597a", "#4d7c0f"]
    for index, (label, group_rows) in enumerate(sorted(grouped.items())):
        group_rows = sorted(group_rows, key=lambda row: row["r"])
        r_vals = [row["r"] for row in group_rows]
        if normalized:
            ys = [row["empirical_switch_per_total"] for row in group_rows]
            theory = [row["theory_switch_per_total"] for row in group_rows]
            y_label = "switch reward / V"
            title = "Normalized collapse across reward vectors"
        else:
            ys = [row["empirical_switch"] for row in group_rows]
            theory = [row["theory_switch"] for row in group_rows]
            y_label = "switch reward"
            title = "Same-V collapse across reward vectors"
        color = colors[index % len(colors)]
        ax.scatter(r_vals, ys, s=32, alpha=0.85, color=color, label=label)
        ax.plot(r_vals, theory, linewidth=1.4, alpha=0.9, color=color)
    ax.set_xlabel("reveals r")
    ax.set_ylabel(y_label)
    ax.set_title(title)
    ax.grid(axis="y", alpha=0.25)
    ax.legend(title="reward vector", fontsize=8)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def simulate_exchangeable(
    k: int = 10,
    m: int = 3,
    r: int = 2,
    reward_dist: RewardDist = "lognormal",
    reward_values: list[float] | None = None,
    trials: int = 100_000,
    seed: int | None = None,
) -> ExchangeableOutput:
    validate_exchangeable(k, m, r)
    if reward_values is not None and len(reward_values) != m:
        raise ValueError("Need len(reward_values) == m")
    rng = random.Random(seed)
    stay_values: list[float] = []
    switch_values: list[float] = []
    total_rewards: list[float] = []

    for _ in range(trials):
        rewards = list(reward_values) if reward_values is not None else sample_positive_rewards(m, rng, reward_dist)
        total_rewards.append(sum(rewards))
        doors = place_rewards_exchangeably(k, rewards, rng)
        initial = rng.randrange(k)
        opened = reveal_doors_uniform_zero(doors, initial, r, rng)
        options = switch_options(k, initial, opened)
        switched = rng.choice(options)
        stay_values.append(doors[initial])
        switch_values.append(doors[switched])

    mean_total_reward = statistics.fmean(total_rewards)
    theory = exchangeable_theory(k, m, r, mean_total_reward)
    return ExchangeableOutput(
        k=k,
        m=m,
        r=r,
        reward_dist="explicit" if reward_values is not None else reward_dist,
        trials=trials,
        mean_total_reward=mean_total_reward,
        empirical_stay=statistics.fmean(stay_values),
        empirical_switch=statistics.fmean(switch_values),
        theory_stay=theory["stay"],
        theory_switch=theory["switch"],
    )


def beta_sample(rng: random.Random, alpha: float, beta: float) -> float:
    return rng.betavariate(alpha, beta)


def sample_door_priors(
    k: int,
    rng: random.Random,
    q_alpha: float = 2.0,
    q_beta: float = 2.0,
    log_mu: float = 0.0,
    log_sigma: float = 1.0,
) -> list[DoorPrior]:
    if k < 3:
        raise ValueError("Need K >= 3")
    priors = []
    for _ in range(k):
        priors.append(
            DoorPrior(
                zero_prob=beta_sample(rng, q_alpha, q_beta),
                reward_value=rng.lognormvariate(log_mu, log_sigma),
            )
        )
    return priors


def sample_realized_rewards(priors: list[DoorPrior], rng: random.Random) -> list[float]:
    rewards = []
    for prior in priors:
        rewards.append(0.0 if rng.random() < prior.zero_prob else prior.reward_value)
    return rewards


def choose_initial(priors: list[DoorPrior], strategy: InitialStrategy, rng: random.Random) -> int:
    if strategy == "random":
        return rng.randrange(len(priors))
    if strategy == "highest_mu":
        return max(range(len(priors)), key=lambda idx: priors[idx].mean)
    if strategy == "lowest_mu":
        return min(range(len(priors)), key=lambda idx: priors[idx].mean)
    raise ValueError(f"unknown initial strategy: {strategy}")


def monty_reveal(
    rewards: list[float],
    priors: list[DoorPrior],
    initial: int,
    opened: set[int],
    policy: MontyPolicy,
    rng: random.Random,
) -> int | None:
    legal = legal_zero_doors(rewards, initial, opened)
    if not legal:
        return None
    if policy == "uniform_zero":
        return rng.choice(legal)
    if policy == "low_mu_zero":
        return min(legal, key=lambda idx: priors[idx].mean)
    if policy == "high_mu_zero":
        return max(legal, key=lambda idx: priors[idx].mean)
    raise ValueError(f"unknown Monty policy: {policy}")


def reveal_sequential(
    rewards: list[float],
    priors: list[DoorPrior],
    initial: int,
    r: int,
    policy: MontyPolicy,
    rng: random.Random,
) -> set[int]:
    opened: set[int] = set()
    for _ in range(r):
        door = monty_reveal(rewards, priors, initial, opened, policy, rng)
        if door is None:
            break
        opened.add(door)
    return opened


def choose_switch(
    priors: list[DoorPrior],
    rewards: list[float],
    initial: int,
    opened: set[int],
    strategy: SwitchStrategy,
    rng: random.Random,
) -> int:
    if strategy == "stay":
        return initial
    options = switch_options(len(priors), initial, opened)
    if not options:
        return initial
    if strategy == "uniform_switch":
        return rng.choice(options)
    if strategy == "prior_best_switch":
        return max(options, key=lambda idx: priors[idx].mean)
    if strategy == "oracle_best_switch":
        return max(options, key=lambda idx: rewards[idx])
    raise ValueError(f"unknown switch strategy: {strategy}")


def simulate_door_specific(
    k: int = 10,
    r: int = 2,
    trials: int = 100_000,
    seed: int | None = None,
    initial_strategy: InitialStrategy = "random",
    monty_policy: MontyPolicy = "uniform_zero",
    q_alpha: float = 2.0,
    q_beta: float = 2.0,
    log_mu: float = 0.0,
    log_sigma: float = 1.0,
    priors: list[DoorPrior] | None = None,
) -> DoorSpecificOutput:
    if k < 3:
        raise ValueError("Need K >= 3")
    if r < 0 or r > k - 1:
        raise ValueError("Need 0 <= r <= K - 1")
    rng = random.Random(seed)
    if priors is None:
        priors = sample_door_priors(k, rng, q_alpha, q_beta, log_mu, log_sigma)
    if len(priors) != k:
        raise ValueError("Need one prior per door")

    strategy_values = {
        "stay": [],
        "uniform_switch": [],
        "prior_best_switch": [],
        "oracle_best_switch": [],
    }
    chosen_initial_means: list[float] = []
    opened_counts: list[int] = []

    for _ in range(trials):
        rewards = sample_realized_rewards(priors, rng)
        initial = choose_initial(priors, initial_strategy, rng)
        opened = reveal_sequential(rewards, priors, initial, r, monty_policy, rng)
        chosen_initial_means.append(priors[initial].mean)
        opened_counts.append(len(opened))
        for strategy in strategy_values:
            door = choose_switch(priors, rewards, initial, opened, strategy, rng)
            strategy_values[strategy].append(rewards[door])

    means = {
        "chosen_initial_mu": statistics.fmean(chosen_initial_means),
        "opened_count": statistics.fmean(opened_counts),
        "prior_mu_min": min(prior.mean for prior in priors),
        "prior_mu_max": max(prior.mean for prior in priors),
        "prior_mu_mean": statistics.fmean(prior.mean for prior in priors),
    }
    empirical = {name: statistics.fmean(values) for name, values in strategy_values.items()}
    return DoorSpecificOutput(
        k=k,
        r=r,
        trials=trials,
        initial_strategy=initial_strategy,
        monty_policy=monty_policy,
        means=means,
        strategy_values=empirical,
        priors=priors,
    )


def find_sacrifice_example(
    k: int = 4,
    r: int = 1,
    tries: int = 200,
    trials: int = 20_000,
    seed: int | None = None,
) -> dict[str, object] | None:
    rng = random.Random(seed)
    best_gap = 0.0
    best: dict[str, object] | None = None
    for attempt in range(tries):
        priors = sample_door_priors(k, rng, q_alpha=2.0, q_beta=2.0, log_mu=0.0, log_sigma=1.1)
        high = simulate_door_specific(
            k=k,
            r=r,
            trials=trials,
            seed=rng.randrange(10**9),
            initial_strategy="highest_mu",
            monty_policy="uniform_zero",
            priors=priors,
        )
        low = simulate_door_specific(
            k=k,
            r=r,
            trials=trials,
            seed=rng.randrange(10**9),
            initial_strategy="lowest_mu",
            monty_policy="uniform_zero",
            priors=priors,
        )
        gap = low.strategy_values["prior_best_switch"] - high.strategy_values["prior_best_switch"]
        if gap > best_gap:
            best_gap = gap
            best = {"attempt": attempt, "gap": gap, "highest_initial": high, "lowest_initial": low}
    return best


def plot_door_specific(out: DoorSpecificOutput, filename: str | None = None) -> Path:
    OUT_DIR.mkdir(exist_ok=True)
    labels = list(out.strategy_values)
    values = [out.strategy_values[label] for label in labels]
    fig, ax = plt.subplots(figsize=(7.2, 4.3))
    ax.bar(labels, values, color=["#22577a", "#0f766e", "#b7791f", "#b23a30"])
    ax.set_ylabel("Empirical reward")
    ax.set_title(f"Door-specific priors: initial={out.initial_strategy}, Monty={out.monty_policy}")
    ax.tick_params(axis="x", rotation=18)
    fig.tight_layout()
    if filename is None:
        filename = f"heterogeneous_{out.initial_strategy}_K{out.k}_r{out.r}.png"
    path = OUT_DIR / filename
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    ex = sub.add_parser("exchangeable", help="simulate exchangeable reward multiset")
    ex.add_argument("--K", "--k", dest="k", type=int, default=10)
    ex.add_argument("--m", type=int, default=3)
    ex.add_argument("--r", type=int, default=2)
    ex.add_argument("--reward-dist", choices=["fixed", "uniform", "exponential", "lognormal", "pareto"], default="lognormal")
    ex.add_argument("--reward-values", type=str, default=None, help="Optional comma-separated unequal positive prize values; if set, must have length m.")
    ex.add_argument("--trials", type=int, default=100_000)
    ex.add_argument("--seed", type=int, default=None)

    ds = sub.add_parser("door-specific", help="simulate Bernoulli-value door priors")
    ds.add_argument("--K", "--k", dest="k", type=int, default=10)
    ds.add_argument("--r", type=int, default=2)
    ds.add_argument("--trials", type=int, default=100_000)
    ds.add_argument("--seed", type=int, default=None)
    ds.add_argument("--initial", choices=["random", "highest_mu", "lowest_mu"], default="random")
    ds.add_argument("--monty", choices=["uniform_zero", "low_mu_zero", "high_mu_zero"], default="uniform_zero")
    ds.add_argument("--plot", action="store_true")

    fs = sub.add_parser("find-sacrifice", help="search for low-initial-choice advantage")
    fs.add_argument("--K", "--k", dest="k", type=int, default=4)
    fs.add_argument("--r", type=int, default=1)
    fs.add_argument("--tries", type=int, default=200)
    fs.add_argument("--trials", type=int, default=20_000)
    fs.add_argument("--seed", type=int, default=None)

    s1 = sub.add_parser("exchangeable-stage1", help="write Stage 1 tables and collapse plots for unequal exchangeable prizes")
    s1.add_argument("--K", "--k", dest="k", type=int, required=True)
    s1.add_argument("--m", type=int, required=True)
    s1.add_argument("--reward-vectors", type=str, required=True, help="Semicolon-separated reward vectors, each comma-separated, e.g. '1,2,5,9;4,4,4,5'")
    s1.add_argument("--trials", type=int, default=100_000)
    s1.add_argument("--seed", type=int, default=None)
    s1.add_argument("--output-prefix", type=str, default="outputs/stage1_exchangeable")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.cmd == "exchangeable":
        reward_values = parse_reward_values(args.reward_values) if args.reward_values is not None else None
        out = simulate_exchangeable(args.k, args.m, args.r, args.reward_dist, reward_values, args.trials, args.seed)
        print(out)
    elif args.cmd == "door-specific":
        out = simulate_door_specific(
            k=args.k,
            r=args.r,
            trials=args.trials,
            seed=args.seed,
            initial_strategy=args.initial,
            monty_policy=args.monty,
        )
        print("means:", out.means)
        print("strategy_values:", out.strategy_values)
        if args.plot:
            print("Saved plot:", plot_door_specific(out))
    elif args.cmd == "find-sacrifice":
        out = find_sacrifice_example(args.k, args.r, args.tries, args.trials, args.seed)
        if out is None:
            print("No sacrifice example found.")
        else:
            print("best gap:", out["gap"])
            high = out["highest_initial"]
            low = out["lowest_initial"]
            assert isinstance(high, DoorSpecificOutput)
            assert isinstance(low, DoorSpecificOutput)
            print("highest-initial values:", high.strategy_values)
            print("lowest-initial values:", low.strategy_values)
            print("priors:", [(p.zero_prob, p.reward_value, p.mean) for p in high.priors])
    elif args.cmd == "exchangeable-stage1":
        reward_vectors = parse_reward_vector_sets(args.reward_vectors)
        if any(len(vector) != args.m for vector in reward_vectors):
            raise ValueError("Every reward vector must have length m")
        prefix = Path(args.output_prefix)
        all_rows: list[dict[str, float | str]] = []
        totals = {round(sum(vector), 12) for vector in reward_vectors}
        for idx, vector in enumerate(reward_vectors):
            label = ",".join(f"{value:g}" for value in vector)
            rows = exchangeable_curve_rows(
                k=args.k,
                m=args.m,
                reward_values=vector,
                trials=args.trials,
                seed=None if args.seed is None else args.seed + 100_000 * idx,
                label=label,
            )
            all_rows.extend(rows)
            if idx == 0:
                table_path = write_exchangeable_rows_csv(rows, Path(f"{prefix}_curve_table.csv"))
                print("wrote", table_path)
                curve_path = plot_exchangeable_theory_vs_empirical(rows, Path(f"{prefix}_theory_vs_empirical.png"))
                print("wrote", curve_path)
        collapse_path = write_exchangeable_rows_csv(all_rows, Path(f"{prefix}_collapse_table.csv"))
        print("wrote", collapse_path)
        raw_collapse = plot_exchangeable_collapse(all_rows, Path(f"{prefix}_same_v_collapse.png"), normalized=False)
        print("wrote", raw_collapse)
        normalized_collapse = plot_exchangeable_collapse(all_rows, Path(f"{prefix}_normalized_collapse.png"), normalized=True)
        print("wrote", normalized_collapse)
        if len(totals) != 1:
            print("warning: reward vectors do not share the same total reward V, so the raw collapse is not expected to coincide exactly")


if __name__ == "__main__":
    main()
