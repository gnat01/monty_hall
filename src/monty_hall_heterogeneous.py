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
import json
import os
import random
import statistics
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


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


def parse_probability_reward_pairs(raw: str) -> list[DoorPrior]:
    priors: list[DoorPrior] = []
    for chunk in raw.split(","):
        piece = chunk.strip()
        if not piece:
            continue
        if ":" not in piece:
            raise ValueError("Each door prior must be of the form p:v")
        prob_text, value_text = piece.split(":", 1)
        prize_prob = float(prob_text.strip())
        reward_value = float(value_text.strip())
        if not (0.0 <= prize_prob <= 1.0):
            raise ValueError("Prize probabilities must lie in [0, 1]")
        if reward_value <= 0.0:
            raise ValueError("Reward values must be strictly positive")
        priors.append(DoorPrior(zero_prob=1.0 - prize_prob, reward_value=reward_value))
    if not priors:
        raise ValueError("Need at least one door prior")
    return priors


def parse_int_list(raw: str) -> list[int]:
    values = [int(part.strip()) for part in raw.split(",") if part.strip()]
    if not values:
        raise ValueError("Need at least one integer value")
    return values


def config_to_argv(config: dict[str, object]) -> list[str]:
    command = config.get("command")
    if not isinstance(command, str) or not command:
        raise ValueError("Config must contain a non-empty 'command' string")
    argv = [command]
    for key, value in config.items():
        if key == "command" or value is None:
            continue
        flag = f"--{key.replace('_', '-')}"
        if isinstance(value, bool):
            if value:
                argv.append(flag)
            continue
        if isinstance(value, list):
            argv.extend([flag, ",".join(str(part) for part in value)])
            continue
        argv.extend([flag, str(value)])
    return argv


def resolve_cli_argv(argv: list[str] | None = None) -> list[str]:
    raw = list(sys.argv[1:] if argv is None else argv)
    if "--config" not in raw:
        return raw
    idx = raw.index("--config")
    if idx + 1 >= len(raw):
        raise ValueError("--config requires a path")
    config_path = Path(raw[idx + 1])
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if not isinstance(config, dict):
        raise ValueError("Config file must contain a JSON object")
    config_argv = config_to_argv(config)
    remainder = raw[:idx] + raw[idx + 2 :]
    return config_argv + remainder


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


def _prior_arrays(priors: list[DoorPrior]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    zero_probs = np.asarray([prior.zero_prob for prior in priors], dtype=float)
    reward_values = np.asarray([prior.reward_value for prior in priors], dtype=float)
    means = (1.0 - zero_probs) * reward_values
    return zero_probs, reward_values, means


def _batched_random_choice(mask: np.ndarray, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    counts = mask.sum(axis=1)
    active = counts > 0
    chosen = np.zeros(mask.shape[0], dtype=int)
    if np.any(active):
        active_counts = counts[active]
        ranks = (rng.random(active_counts.shape[0]) * active_counts).astype(int)
        cumulative = np.cumsum(mask[active], axis=1)
        chosen[active] = np.argmax(cumulative > ranks[:, None], axis=1)
    return chosen, active


def _batched_initial_indices(
    means: np.ndarray,
    strategy: InitialStrategy,
    trials: int,
    rng: np.random.Generator,
) -> np.ndarray:
    if strategy == "random":
        return rng.integers(0, means.shape[0], size=trials)
    if strategy == "highest_mu":
        return np.full(trials, int(np.argmax(means)), dtype=int)
    if strategy == "lowest_mu":
        return np.full(trials, int(np.argmin(means)), dtype=int)
    raise ValueError(f"unknown initial strategy: {strategy}")


def _batched_reveals(
    rewards: np.ndarray,
    means: np.ndarray,
    initial: np.ndarray,
    r: int,
    policy: MontyPolicy,
    rng: np.random.Generator,
) -> np.ndarray:
    trials, k = rewards.shape
    opened = np.zeros((trials, k), dtype=bool)
    initial_mask = np.zeros((trials, k), dtype=bool)
    initial_mask[np.arange(trials), initial] = True
    zero_mask = rewards == 0.0

    for _ in range(r):
        legal = zero_mask & ~opened & ~initial_mask
        if policy == "uniform_zero":
            chosen, active = _batched_random_choice(legal, rng)
        elif policy == "low_mu_zero":
            active = np.any(legal, axis=1)
            chosen = np.argmin(np.where(legal, means[None, :], np.inf), axis=1)
        elif policy == "high_mu_zero":
            active = np.any(legal, axis=1)
            chosen = np.argmax(np.where(legal, means[None, :], -np.inf), axis=1)
        else:
            raise ValueError(f"unknown Monty policy: {policy}")
        if not np.any(active):
            break
        active_rows = np.flatnonzero(active)
        opened[active_rows, chosen[active]] = True
    return opened


def _batched_strategy_values(
    rewards: np.ndarray,
    means: np.ndarray,
    initial: np.ndarray,
    opened: np.ndarray,
    rng: np.random.Generator,
) -> dict[str, np.ndarray]:
    trials, k = rewards.shape
    rows = np.arange(trials)
    initial_mask = np.zeros((trials, k), dtype=bool)
    initial_mask[rows, initial] = True
    options = ~opened & ~initial_mask

    stay = rewards[rows, initial]

    uniform_idx, has_uniform = _batched_random_choice(options, rng)
    uniform = stay.copy()
    uniform[has_uniform] = rewards[rows[has_uniform], uniform_idx[has_uniform]]

    prior_idx = np.argmax(np.where(options, means[None, :], -np.inf), axis=1)
    has_prior = np.any(options, axis=1)
    prior = stay.copy()
    prior[has_prior] = rewards[rows[has_prior], prior_idx[has_prior]]

    oracle_idx = np.argmax(np.where(options, rewards, -np.inf), axis=1)
    has_oracle = np.any(options, axis=1)
    oracle = stay.copy()
    oracle[has_oracle] = rewards[rows[has_oracle], oracle_idx[has_oracle]]

    return {
        "stay": stay,
        "uniform_switch": uniform,
        "prior_best_switch": prior,
        "oracle_best_switch": oracle,
    }


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

    zero_probs, reward_values, means_array = _prior_arrays(priors)
    np_rng = np.random.default_rng(seed)
    reward_draws = np.where(
        np_rng.random((trials, k)) < zero_probs[None, :],
        0.0,
        reward_values[None, :],
    )
    initial = _batched_initial_indices(means_array, initial_strategy, trials, np_rng)
    opened = _batched_reveals(reward_draws, means_array, initial, r, monty_policy, np_rng)
    strategy_vectors = _batched_strategy_values(reward_draws, means_array, initial, opened, np_rng)

    means = {
        "chosen_initial_mu": float(np.mean(means_array[initial])),
        "opened_count": float(np.mean(opened.sum(axis=1))),
        "prior_mu_min": float(np.min(means_array)),
        "prior_mu_max": float(np.max(means_array)),
        "prior_mu_mean": float(np.mean(means_array)),
    }
    empirical = {name: float(np.mean(values)) for name, values in strategy_vectors.items()}
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


def stage2_rows(
    priors: list[DoorPrior],
    r_values: list[int],
    trials: int,
    seed: int | None,
    repeats: int = 1,
) -> list[dict[str, float | str]]:
    if repeats < 1:
        raise ValueError("Need repeats >= 1")
    rows: list[dict[str, float | str]] = []
    initials: list[InitialStrategy] = ["random", "highest_mu", "lowest_mu"]
    monty_policies: list[MontyPolicy] = ["uniform_zero", "low_mu_zero", "high_mu_zero"]
    for repeat in range(repeats):
        for r_index, r in enumerate(r_values):
            for init_index, initial in enumerate(initials):
                for monty_index, monty in enumerate(monty_policies):
                    run_seed = None
                    if seed is not None:
                        run_seed = seed + 1_000_000 * repeat + 10_000 * r_index + 1_000 * init_index + 100 * monty_index
                    out = simulate_door_specific(
                        k=len(priors),
                        r=r,
                        trials=trials,
                        seed=run_seed,
                        initial_strategy=initial,
                        monty_policy=monty,
                        priors=priors,
                    )
                    for switch, value in out.strategy_values.items():
                        rows.append(
                            {
                                "repeat": float(repeat),
                                "k": float(len(priors)),
                                "r": float(r),
                                "trials": float(trials),
                                "initial_strategy": initial,
                                "monty_policy": monty,
                                "switch_strategy": switch,
                                "empirical_reward": value,
                                "chosen_initial_mu": out.means["chosen_initial_mu"],
                                "opened_count": out.means["opened_count"],
                                "prior_mu_min": out.means["prior_mu_min"],
                                "prior_mu_max": out.means["prior_mu_max"],
                                "prior_mu_mean": out.means["prior_mu_mean"],
                            }
                        )
    return rows


def average_stage2_rows(rows: list[dict[str, float | str]]) -> list[dict[str, float | str]]:
    grouped: dict[tuple[str, str, str, float], list[dict[str, float | str]]] = {}
    for row in rows:
        key = (
            str(row["initial_strategy"]),
            str(row["monty_policy"]),
            str(row["switch_strategy"]),
            float(row["r"]),
        )
        grouped.setdefault(key, []).append(row)

    averaged: list[dict[str, float | str]] = []
    for key, group in grouped.items():
        initial, monty, switch, r = key
        averaged.append(
            {
                "repeats": float(len(group)),
                "k": float(group[0]["k"]),
                "r": r,
                "trials": float(group[0]["trials"]),
                "initial_strategy": initial,
                "monty_policy": monty,
                "switch_strategy": switch,
                "empirical_reward": statistics.fmean(float(row["empirical_reward"]) for row in group),
                "empirical_reward_sd": statistics.stdev(float(row["empirical_reward"]) for row in group) if len(group) > 1 else 0.0,
                "chosen_initial_mu": statistics.fmean(float(row["chosen_initial_mu"]) for row in group),
                "opened_count": statistics.fmean(float(row["opened_count"]) for row in group),
                "prior_mu_min": statistics.fmean(float(row["prior_mu_min"]) for row in group),
                "prior_mu_max": statistics.fmean(float(row["prior_mu_max"]) for row in group),
                "prior_mu_mean": statistics.fmean(float(row["prior_mu_mean"]) for row in group),
            }
        )
    return sorted(averaged, key=lambda row: (row["initial_strategy"], row["monty_policy"], row["switch_strategy"], row["r"]))


def write_rows_csv(rows: list[dict[str, float | str]], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return path


def write_priors_csv(priors: list[DoorPrior], path: Path) -> Path:
    rows = []
    for idx, prior in enumerate(priors):
        rows.append(
            {
                "door": idx,
                "prize_prob": 1.0 - prior.zero_prob,
                "zero_prob": prior.zero_prob,
                "reward_value": prior.reward_value,
                "prior_mean": prior.mean,
            }
        )
    return write_rows_csv(rows, path)


def stage2_value_lookup(
    rows: list[dict[str, float | str]],
    initial_strategy: str,
    monty_policy: str,
    switch_strategy: str,
) -> list[tuple[int, float]]:
    points = [
        (int(row["r"]), float(row["empirical_reward"]))
        for row in rows
        if row["initial_strategy"] == initial_strategy
        and row["monty_policy"] == monty_policy
        and row["switch_strategy"] == switch_strategy
    ]
    return sorted(points)


def plot_stage2_prior_landscape(priors: list[DoorPrior], path: Path) -> Path:
    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    x = list(range(len(priors)))
    means = [prior.mean for prior in priors]
    colors = ["#22577a" if idx == max(range(len(priors)), key=lambda j: priors[j].mean) else "#8fbcd4" for idx in x]
    ax.bar(x, means, color=colors)
    for idx, prior in enumerate(priors):
        ax.text(
            idx,
            prior.mean + 0.03 * max(means),
            f"p={1.0-prior.zero_prob:.2f}\nv={prior.reward_value:.1f}",
            ha="center",
            va="bottom",
            fontsize=8,
        )
    ax.set_xlabel("door index")
    ax.set_ylabel("prior mean")
    ax.set_title("Stage 2 prior landscape")
    ax.set_xticks(x)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def plot_stage2_strategy_panel(rows: list[dict[str, float | str]], path: Path) -> Path:
    initials = ["random", "highest_mu", "lowest_mu"]
    switches = ["stay", "uniform_switch", "prior_best_switch", "oracle_best_switch"]
    colors = {
        "stay": "#22577a",
        "uniform_switch": "#0f766e",
        "prior_best_switch": "#b7791f",
        "oracle_best_switch": "#b23a30",
    }
    fig, axes = plt.subplots(1, 3, figsize=(13.4, 4.2), sharey=True)
    for ax, initial in zip(axes, initials):
        for switch in switches:
            points = stage2_value_lookup(rows, initial, "uniform_zero", switch)
            ax.plot([r for r, _ in points], [v for _, v in points], marker="o", linewidth=2.0, markersize=4, color=colors[switch], label=switch)
        ax.set_title(f"initial={initial}\nMonty=uniform_zero")
        ax.set_xlabel("reveals r")
        ax.grid(axis="y", alpha=0.25)
    axes[0].set_ylabel("empirical reward")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=4, frameon=False, bbox_to_anchor=(0.5, 1.04))
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def plot_stage2_monty_panel(rows: list[dict[str, float | str]], path: Path) -> Path:
    monty_policies = ["uniform_zero", "low_mu_zero", "high_mu_zero"]
    initials = ["random", "highest_mu", "lowest_mu"]
    colors = {
        "random": "#22577a",
        "highest_mu": "#b7791f",
        "lowest_mu": "#b23a30",
    }
    fig, axes = plt.subplots(1, 3, figsize=(13.4, 4.2), sharey=True)
    for ax, monty in zip(axes, monty_policies):
        for initial in initials:
            points = stage2_value_lookup(rows, initial, monty, "prior_best_switch")
            ax.plot([r for r, _ in points], [v for _, v in points], marker="o", linewidth=2.0, markersize=4, color=colors[initial], label=initial)
        ax.set_title(f"prior_best_switch\nMonty={monty}")
        ax.set_xlabel("reveals r")
        ax.grid(axis="y", alpha=0.25)
    axes[0].set_ylabel("empirical reward")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.04))
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def plot_stage2_gain_heatmap(rows: list[dict[str, float | str]], path: Path) -> Path:
    finals = [int(row["r"]) for row in rows]
    final_r = max(finals)
    initials = ["random", "highest_mu", "lowest_mu"]
    monty_policies = ["uniform_zero", "low_mu_zero", "high_mu_zero"]
    matrix: list[list[float]] = []
    for initial in initials:
        values: list[float] = []
        for monty in monty_policies:
            uniform_val = next(
                float(row["empirical_reward"])
                for row in rows
                if int(row["r"]) == final_r
                and row["initial_strategy"] == initial
                and row["monty_policy"] == monty
                and row["switch_strategy"] == "uniform_switch"
            )
            prior_val = next(
                float(row["empirical_reward"])
                for row in rows
                if int(row["r"]) == final_r
                and row["initial_strategy"] == initial
                and row["monty_policy"] == monty
                and row["switch_strategy"] == "prior_best_switch"
            )
            values.append(prior_val - uniform_val)
        matrix.append(values)
    vmax = max(max(abs(value) for value in row) for row in matrix)
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    image = ax.imshow(matrix, cmap="RdYlBu_r", vmin=-vmax, vmax=vmax, aspect="auto")
    ax.set_xticks(range(len(monty_policies)), monty_policies)
    ax.set_yticks(range(len(initials)), initials)
    ax.set_title(f"prior_best_switch - uniform_switch at r={final_r}")
    for i, row in enumerate(matrix):
        for j, value in enumerate(row):
            ax.text(j, i, f"{value:.3f}", ha="center", va="center", fontsize=9, color="black")
    fig.colorbar(image, ax=ax, shrink=0.85, label="reward gain")
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def plot_stage2_partial_collapse(rows: list[dict[str, float | str]], path: Path) -> Path:
    initials = ["random", "highest_mu", "lowest_mu"]
    colors = {
        "random": "#22577a",
        "highest_mu": "#b23a30",
        "lowest_mu": "#0f766e",
    }
    fig, ax = plt.subplots(figsize=(7.8, 4.8))
    max_r = max(int(row["r"]) for row in rows)
    for initial in initials:
        points: list[tuple[float, float]] = []
        for r in range(max_r + 1):
            subset = [
                row
                for row in rows
                if int(row["r"]) == r
                and row["initial_strategy"] == initial
                and row["monty_policy"] == "uniform_zero"
            ]
            values = {str(row["switch_strategy"]): float(row["empirical_reward"]) for row in subset}
            if "oracle_best_switch" not in values or "prior_best_switch" not in values:
                continue
            points.append((r / max(1, max_r), values["prior_best_switch"] / values["oracle_best_switch"]))
        ax.plot(
            [x for x, _ in points],
            [y for _, y in points],
            marker="o",
            linewidth=2.2,
            markersize=4,
            color=colors[initial],
            label=initial,
        )
    ax.set_xlabel("reveal fraction")
    ax.set_ylabel("prior_best_switch / oracle_best_switch")
    ax.set_title("Stage 2 partial collapse attempt")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def stage2_partial_collapse_rows(
    rows: list[dict[str, float | str]],
    *,
    landscape_id: int | None = None,
) -> list[dict[str, float | str]]:
    max_r = max(int(row["r"]) for row in rows)
    collapse_rows: list[dict[str, float | str]] = []
    for initial in ["random", "highest_mu", "lowest_mu"]:
        for r in range(max_r + 1):
            subset = [
                row
                for row in rows
                if int(row["r"]) == r
                and row["initial_strategy"] == initial
                and row["monty_policy"] == "uniform_zero"
            ]
            values = {str(row["switch_strategy"]): float(row["empirical_reward"]) for row in subset}
            collapse_rows.append(
                {
                    "landscape_id": float(-1 if landscape_id is None else landscape_id),
                    "initial_strategy": initial,
                    "r": float(r),
                    "reveal_fraction": r / max(1, max_r),
                    "prior_to_oracle": values["prior_best_switch"] / values["oracle_best_switch"],
                    "uniform_to_oracle": values["uniform_switch"] / values["oracle_best_switch"],
                    "stay_to_oracle": values["stay"] / values["oracle_best_switch"],
                    "prior_minus_uniform": values["prior_best_switch"] - values["uniform_switch"],
                }
            )
    return collapse_rows


def _landscape_job(
    landscape_id: int,
    k: int,
    r_values: list[int],
    trials: int,
    repeats: int,
    q_alpha: float,
    q_beta: float,
    log_mu: float,
    log_sigma: float,
    seed: int | None,
) -> tuple[list[dict[str, float | str]], list[dict[str, float | str]]]:
    landscape_seed = None if seed is None else seed + 1_000_000_000 + landscape_id
    priors_rng = random.Random(landscape_seed)
    priors = sample_door_priors(
        k,
        priors_rng,
        q_alpha=q_alpha,
        q_beta=q_beta,
        log_mu=log_mu,
        log_sigma=log_sigma,
    )
    priors_rows: list[dict[str, float | str]] = []
    for door, prior in enumerate(priors):
        priors_rows.append(
            {
                "landscape_id": float(landscape_id),
                "door": float(door),
                "prize_prob": 1.0 - prior.zero_prob,
                "reward_value": prior.reward_value,
                "prior_mean": prior.mean,
            }
        )
    raw_rows = stage2_rows(
        priors,
        r_values,
        trials,
        None if seed is None else seed + 10_000_000 * landscape_id,
        repeats,
    )
    averaged = average_stage2_rows(raw_rows)
    collapse_rows = stage2_partial_collapse_rows(averaged, landscape_id=landscape_id)
    return priors_rows, collapse_rows


def plot_stage2_family_partial_collapse(rows: list[dict[str, float | str]], path: Path) -> Path:
    initials = ["random", "highest_mu", "lowest_mu"]
    colors = {
        "random": "#22577a",
        "highest_mu": "#b23a30",
        "lowest_mu": "#0f766e",
    }
    grouped: dict[tuple[str, float], list[float]] = {}
    landscape_groups: dict[tuple[str, float, float], float] = {}
    for row in rows:
        initial = str(row["initial_strategy"])
        frac = float(row["reveal_fraction"])
        grouped.setdefault((initial, frac), []).append(float(row["prior_to_oracle"]))
        landscape_groups[(initial, float(row["landscape_id"]), frac)] = float(row["prior_to_oracle"])

    fig, axes = plt.subplots(1, 3, figsize=(13.2, 4.3), sharey=True)
    for ax, initial in zip(axes, initials):
        landscape_ids = sorted({float(row["landscape_id"]) for row in rows if row["initial_strategy"] == initial})
        fracs = sorted({float(row["reveal_fraction"]) for row in rows if row["initial_strategy"] == initial})
        for landscape_id in landscape_ids:
            values = [landscape_groups[(initial, landscape_id, frac)] for frac in fracs]
            ax.plot(fracs, values, color=colors[initial], alpha=0.18, linewidth=1.0)
        means = [statistics.fmean(grouped[(initial, frac)]) for frac in fracs]
        lowers = []
        uppers = []
        for frac in fracs:
            values = grouped[(initial, frac)]
            sd = statistics.stdev(values) if len(values) > 1 else 0.0
            lowers.append(max(0.0, statistics.fmean(values) - sd))
            uppers.append(min(1.1, statistics.fmean(values) + sd))
        ax.fill_between(fracs, lowers, uppers, color=colors[initial], alpha=0.20)
        ax.plot(fracs, means, color=colors[initial], linewidth=2.5)
        ax.set_title(initial)
        ax.set_xlabel("reveal fraction")
        ax.grid(axis="y", alpha=0.25)
    axes[0].set_ylabel("prior_best_switch / oracle_best_switch")
    fig.suptitle("Stage 2 partial collapse across random labeled landscapes", y=1.02)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=str, default=None, help="Optional JSON config file. CLI flags after --config override preset values.")
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
    ds.add_argument("--door-priors", type=str, default=None, help="Optional explicit door priors as p:v pairs, comma-separated, where p is prize probability.")

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

    s2 = sub.add_parser("door-specific-stage2", help="write Stage 2 tables and plots for labeled unequal prize priors")
    s2.add_argument("--door-priors", type=str, required=True, help="Comma-separated p:v pairs, e.g. '0.9:4,0.6:3,0.2:8,0.3:5'")
    s2.add_argument("--r-values", type=str, default=None, help="Optional comma-separated reveal counts. Default is 0..K-2.")
    s2.add_argument("--trials", type=int, default=100_000)
    s2.add_argument("--repeats", type=int, default=1)
    s2.add_argument("--seed", type=int, default=None)
    s2.add_argument("--output-prefix", type=str, default="outputs/stage2_door_specific")

    s2c = sub.add_parser("door-specific-stage2-collapse", help="sample many labeled landscapes and test the partial-collapse idea")
    s2c.add_argument("--K", "--k", dest="k", type=int, default=5)
    s2c.add_argument("--r-values", type=str, default=None, help="Optional comma-separated reveal counts. Default is 0..K-2.")
    s2c.add_argument("--landscapes", type=int, default=18)
    s2c.add_argument("--trials", type=int, default=40_000)
    s2c.add_argument("--repeats", type=int, default=4)
    s2c.add_argument("--seed", type=int, default=None)
    s2c.add_argument("--q-alpha", type=float, default=2.0)
    s2c.add_argument("--q-beta", type=float, default=2.0)
    s2c.add_argument("--log-mu", type=float, default=0.0)
    s2c.add_argument("--log-sigma", type=float, default=1.0)
    s2c.add_argument("--workers", type=int, default=0, help="Parallel worker processes; 0 means auto.")
    s2c.add_argument("--output-prefix", type=str, default="outputs/stage2_family")
    return parser.parse_args(resolve_cli_argv(argv))


def main() -> None:
    args = parse_args()
    if args.cmd == "exchangeable":
        reward_values = parse_reward_values(args.reward_values) if args.reward_values is not None else None
        out = simulate_exchangeable(args.k, args.m, args.r, args.reward_dist, reward_values, args.trials, args.seed)
        print(out)
    elif args.cmd == "door-specific":
        priors = parse_probability_reward_pairs(args.door_priors) if args.door_priors is not None else None
        out = simulate_door_specific(
            k=args.k,
            r=args.r,
            trials=args.trials,
            seed=args.seed,
            initial_strategy=args.initial,
            monty_policy=args.monty,
            priors=priors,
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
    elif args.cmd == "door-specific-stage2":
        priors = parse_probability_reward_pairs(args.door_priors)
        k = len(priors)
        r_values = parse_int_list(args.r_values) if args.r_values is not None else list(range(0, k - 1))
        if any(r < 0 or r > k - 1 for r in r_values):
            raise ValueError("Need every reveal count r to satisfy 0 <= r <= K - 1")
        prefix = Path(args.output_prefix)
        priors_path = write_priors_csv(priors, Path(f"{prefix}_priors.csv"))
        print("wrote", priors_path)
        raw_rows = stage2_rows(priors, r_values, args.trials, args.seed, args.repeats)
        if args.repeats > 1:
            repeats_path = write_rows_csv(raw_rows, Path(f"{prefix}_strategy_repeats.csv"))
            print("wrote", repeats_path)
        rows = average_stage2_rows(raw_rows)
        table_path = write_rows_csv(rows, Path(f"{prefix}_strategy_table.csv"))
        print("wrote", table_path)
        prior_plot = plot_stage2_prior_landscape(priors, Path(f"{prefix}_prior_landscape.png"))
        print("wrote", prior_plot)
        strategy_plot = plot_stage2_strategy_panel(rows, Path(f"{prefix}_strategy_panel.png"))
        print("wrote", strategy_plot)
        monty_plot = plot_stage2_monty_panel(rows, Path(f"{prefix}_monty_panel.png"))
        print("wrote", monty_plot)
        heatmap = plot_stage2_gain_heatmap(rows, Path(f"{prefix}_policy_gain_heatmap.png"))
        print("wrote", heatmap)
        partial_collapse = plot_stage2_partial_collapse(rows, Path(f"{prefix}_partial_collapse.png"))
        print("wrote", partial_collapse)
    elif args.cmd == "door-specific-stage2-collapse":
        if args.k < 3:
            raise ValueError("Need K >= 3")
        r_values = parse_int_list(args.r_values) if args.r_values is not None else list(range(0, args.k - 1))
        if any(r < 0 or r > args.k - 1 for r in r_values):
            raise ValueError("Need every reveal count r to satisfy 0 <= r <= K - 1")
        if args.landscapes < 1:
            raise ValueError("Need landscapes >= 1")
        if args.repeats < 1:
            raise ValueError("Need repeats >= 1")
        prefix = Path(args.output_prefix)
        priors_rows: list[dict[str, float | str]] = []
        collapse_rows: list[dict[str, float | str]] = []
        workers = args.workers if args.workers > 0 else min(args.landscapes, os.cpu_count() or 1)
        if workers == 1:
            for landscape_id in range(args.landscapes):
                priors_part, collapse_part = _landscape_job(
                    landscape_id,
                    args.k,
                    r_values,
                    args.trials,
                    args.repeats,
                    args.q_alpha,
                    args.q_beta,
                    args.log_mu,
                    args.log_sigma,
                    args.seed,
                )
                priors_rows.extend(priors_part)
                collapse_rows.extend(collapse_part)
        else:
            with ProcessPoolExecutor(max_workers=workers) as executor:
                futures = [
                    executor.submit(
                        _landscape_job,
                        landscape_id,
                        args.k,
                        r_values,
                        args.trials,
                        args.repeats,
                        args.q_alpha,
                        args.q_beta,
                        args.log_mu,
                        args.log_sigma,
                        args.seed,
                    )
                    for landscape_id in range(args.landscapes)
                ]
                for future in futures:
                    priors_part, collapse_part = future.result()
                    priors_rows.extend(priors_part)
                    collapse_rows.extend(collapse_part)
        priors_path = write_rows_csv(priors_rows, Path(f"{prefix}_landscapes.csv"))
        print("wrote", priors_path)
        collapse_path = write_rows_csv(collapse_rows, Path(f"{prefix}_collapse_table.csv"))
        print("wrote", collapse_path)
        collapse_plot = plot_stage2_family_partial_collapse(collapse_rows, Path(f"{prefix}_partial_collapse_family.png"))
        print("wrote", collapse_plot)


if __name__ == "__main__":
    main()
