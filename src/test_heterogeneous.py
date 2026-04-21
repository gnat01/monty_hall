import unittest

from monty_hall_heterogeneous import (
    DoorPrior,
    exchangeable_theory,
    simulate_door_specific,
    simulate_exchangeable,
)


class HeterogeneousRewardTests(unittest.TestCase):
    def assert_close(self, observed: float, expected: float, tolerance: float = 0.04) -> None:
        self.assertLessEqual(
            abs(observed - expected),
            tolerance,
            f"observed={observed}, expected={expected}, tolerance={tolerance}",
        )

    def test_exchangeable_theory_fixed_rewards_matches_identical_case(self) -> None:
        theory = exchangeable_theory(k=10, m=3, r=4, total_reward=3.0)
        self.assertAlmostEqual(theory["stay"], 0.3)
        self.assertAlmostEqual(theory["switch"], 0.54)

    def test_exchangeable_simulation_collapses_to_total_reward_mass(self) -> None:
        out = simulate_exchangeable(k=10, m=3, r=4, reward_dist="lognormal", trials=80_000, seed=123)
        self.assert_close(out.empirical_stay, out.theory_stay)
        self.assert_close(out.empirical_switch, out.theory_switch)

    def test_door_specific_prior_best_beats_uniform_in_skewed_case(self) -> None:
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
            trials=50_000,
            seed=99,
            initial_strategy="lowest_mu",
            monty_policy="uniform_zero",
            priors=priors,
        )
        self.assertGreater(out.strategy_values["prior_best_switch"], out.strategy_values["uniform_switch"])

    def test_low_initial_can_preserve_high_value_switch_options(self) -> None:
        priors = [
            DoorPrior(0.1, 4.0),
            DoorPrior(0.4, 3.0),
            DoorPrior(0.8, 2.0),
            DoorPrior(0.95, 1.0),
        ]
        high = simulate_door_specific(
            k=4,
            r=1,
            trials=50_000,
            seed=7,
            initial_strategy="highest_mu",
            monty_policy="uniform_zero",
            priors=priors,
        )
        low = simulate_door_specific(
            k=4,
            r=1,
            trials=50_000,
            seed=8,
            initial_strategy="lowest_mu",
            monty_policy="uniform_zero",
            priors=priors,
        )
        self.assertGreater(low.strategy_values["prior_best_switch"], high.strategy_values["prior_best_switch"])


if __name__ == "__main__":
    unittest.main()
