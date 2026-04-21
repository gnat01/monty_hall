"""Variable reveal costs for the generalized Monty Hall model.

This module keeps the Part I probability law

    S(t) = m(K - 1) / (K(K - 1 - t))

and studies the deterministic stopping problem

    max_t S(t) - C(t),

where C(t) is the cumulative cost of buying t reveals.
"""

from __future__ import annotations

import argparse
import csv
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Literal


CostKind = Literal["constant", "linear", "saturating", "linear_saturating"]


@dataclass(frozen=True)
class VariableCostResult:
    k: int
    m: int
    costs: list[float]
    success: list[float]
    cumulative_cost: list[float]
    net_value: list[float]
    optimal_t: int
    optimal_value: float

    @property
    def max_reveals(self) -> int:
        return self.k - self.m - 1


def validate_params(k: int, m: int) -> None:
    if k < 3:
        raise ValueError("Need K >= 3")
    if m < 1 or m >= k:
        raise ValueError("Need 1 <= m < K")
    if k - m - 1 < 0:
        raise ValueError("Need at least one feasible stopping time")


def switch_success(k: int, m: int, t: int | float) -> float:
    validate_params(k, m)
    if t < 0 or t > k - m - 1:
        raise ValueError("Need 0 <= t <= K - m - 1")
    return m * (k - 1) / (k * (k - 1 - t))


def marginal_value(k: int, m: int, t: int) -> float:
    validate_params(k, m)
    if t < 0 or t >= k - m - 1:
        raise ValueError("Need 0 <= t < K - m - 1")
    return switch_success(k, m, t + 1) - switch_success(k, m, t)


def cost_sequence(
    kind: CostKind,
    max_reveals: int,
    base: float,
    slope: float = 0.0,
    saturation: float | None = None,
    tau: float | None = None,
) -> list[float]:
    """Return reveal costs c_0,...,c_{T-1}.

    `linear`: c_t = base + slope * t.
    `saturating`: c_t = base + saturation * (1 - exp(-t/tau)).
    `linear_saturating`: c_t = base + min(slope * t, saturation).
    """
    if max_reveals < 0:
        raise ValueError("Need max_reveals >= 0")
    if base < 0 or slope < 0:
        raise ValueError("Need nonnegative base and slope")

    if kind == "constant":
        return [base for _ in range(max_reveals)]

    if kind == "linear":
        return [base + slope * t for t in range(max_reveals)]

    if kind == "saturating":
        if saturation is None:
            saturation = slope
        if tau is None:
            tau = max(1.0, max_reveals / 5)
        if saturation < 0 or tau <= 0:
            raise ValueError("Need saturation >= 0 and tau > 0")
        return [base + saturation * (1.0 - math.exp(-t / tau)) for t in range(max_reveals)]

    if kind == "linear_saturating":
        if saturation is None:
            raise ValueError("linear_saturating requires --saturation")
        if saturation < 0:
            raise ValueError("Need saturation >= 0")
        return [base + min(slope * t, saturation) for t in range(max_reveals)]

    raise ValueError(f"Unknown cost kind: {kind}")


def cumulative_costs(costs: Iterable[float]) -> list[float]:
    cumulative = [0.0]
    total = 0.0
    for cost in costs:
        total += cost
        cumulative.append(total)
    return cumulative


def solve_variable_costs(k: int, m: int, costs: list[float]) -> VariableCostResult:
    validate_params(k, m)
    max_reveals = k - m - 1
    if len(costs) != max_reveals:
        raise ValueError(f"Need exactly {max_reveals} reveal costs")
    if any(cost < 0 for cost in costs):
        raise ValueError("Costs must be nonnegative")

    success = [switch_success(k, m, t) for t in range(max_reveals + 1)]
    cumulative = cumulative_costs(costs)
    net_value = [s - c for s, c in zip(success, cumulative)]
    optimal_t = max(range(max_reveals + 1), key=lambda t: net_value[t])
    return VariableCostResult(
        k=k,
        m=m,
        costs=costs,
        success=success,
        cumulative_cost=cumulative,
        net_value=net_value,
        optimal_t=optimal_t,
        optimal_value=net_value[optimal_t],
    )


def solve_from_family(
    k: int,
    m: int,
    kind: CostKind,
    base: float,
    slope: float = 0.0,
    saturation: float | None = None,
    tau: float | None = None,
) -> VariableCostResult:
    validate_params(k, m)
    max_reveals = k - m - 1
    costs = cost_sequence(kind, max_reveals, base, slope, saturation, tau)
    return solve_variable_costs(k, m, costs)


def write_csv(result: VariableCostResult, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["t", "S_t", "C_t", "W_t", "next_cost", "delta_t"])
        for t, (success, cumulative, net) in enumerate(
            zip(result.success, result.cumulative_cost, result.net_value)
        ):
            next_cost = result.costs[t] if t < len(result.costs) else ""
            delta = marginal_value(result.k, result.m, t) if t < result.max_reveals else ""
            writer.writerow([t, success, cumulative, net, next_cost, delta])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--K", "--k", dest="k", type=int, default=50)
    parser.add_argument("--m", type=int, default=1)
    parser.add_argument(
        "--kind",
        choices=["constant", "linear", "saturating", "linear_saturating"],
        default="linear",
    )
    parser.add_argument("--base", type=float, default=0.002)
    parser.add_argument("--slope", type=float, default=0.0004)
    parser.add_argument("--saturation", type=float, default=None)
    parser.add_argument("--tau", type=float, default=None)
    parser.add_argument("--csv", type=Path, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = solve_from_family(
        k=args.k,
        m=args.m,
        kind=args.kind,
        base=args.base,
        slope=args.slope,
        saturation=args.saturation,
        tau=args.tau,
    )
    print(f"K={result.k}, m={result.m}, max_reveals={result.max_reveals}")
    print(f"optimal_t={result.optimal_t}, optimal_value={result.optimal_value:.8f}")
    print(f"S(optimal_t)={result.success[result.optimal_t]:.8f}")
    print(f"C(optimal_t)={result.cumulative_cost[result.optimal_t]:.8f}")
    print(f"W(0)={result.net_value[0]:.8f}")
    print(f"W(T)={result.net_value[-1]:.8f}")
    if args.csv is not None:
        write_csv(result, args.csv)
        print(f"wrote {args.csv}")


if __name__ == "__main__":
    main()
