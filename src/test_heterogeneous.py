import unittest

from monty_hall_heterogeneous import (
    DoorPrior,
    exchangeable_curve_rows,
    exchangeable_theory,
    parse_probability_reward_pairs,
    parse_reward_values,
    parse_reward_vector_sets,
    simulate_door_specific,
    simulate_exchangeable,
    stage2_rows,
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

    def test_exchangeable_explicit_unequal_rewards_match_theory(self) -> None:
        reward_values = [1.0, 2.0, 5.0, 9.0]
        out = simulate_exchangeable(
            k=12,
            m=4,
            r=4,
            reward_values=reward_values,
            trials=80_000,
            seed=321,
        )
        self.assertAlmostEqual(out.mean_total_reward, sum(reward_values))
        self.assert_close(out.empirical_stay, out.theory_stay)
        self.assert_close(out.empirical_switch, out.theory_switch)

    def test_parse_reward_values(self) -> None:
        self.assertEqual(parse_reward_values("1, 2.5, 7"), [1.0, 2.5, 7.0])
        self.assertEqual(parse_reward_vector_sets("1,2;3,4"), [[1.0, 2.0], [3.0, 4.0]])
        with self.assertRaises(ValueError):
            parse_reward_values("")
        with self.assertRaises(ValueError):
            parse_reward_values("1,0,3")

    def test_parse_probability_reward_pairs(self) -> None:
        priors = parse_probability_reward_pairs("0.9:4, 0.3:5, 0.1:10")
        self.assertEqual(len(priors), 3)
        self.assertAlmostEqual(priors[0].mean, 3.6)
        self.assertAlmostEqual(priors[1].mean, 1.5)
        self.assertAlmostEqual(priors[2].mean, 1.0)
        with self.assertRaises(ValueError):
            parse_probability_reward_pairs("")
        with self.assertRaises(ValueError):
            parse_probability_reward_pairs("1.1:4")
        with self.assertRaises(ValueError):
            parse_probability_reward_pairs("0.4:-2")

    def test_exchangeable_curve_rows_cover_all_reveals(self) -> None:
        rows = exchangeable_curve_rows(
            k=8,
            m=3,
            reward_values=[1.0, 2.0, 5.0],
            trials=20_000,
            seed=111,
            label="1,2,5",
        )
        self.assertEqual(len(rows), 8 - 3)
        self.assertEqual(rows[0]["r"], 0.0)
        self.assertEqual(rows[-1]["r"], float(8 - 3 - 1))
        for row in rows:
            self.assertAlmostEqual(row["theory_stay"], 8.0 / 8.0)

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

    def test_stage2_rows_cover_strategy_grid(self) -> None:
        priors = parse_probability_reward_pairs("0.1:1,0.2:1.5,0.8:4,0.3:2")
        rows = stage2_rows(priors=priors, r_values=[0, 1], trials=15_000, seed=41)
        self.assertEqual(len(rows), 2 * 3 * 3 * 4)
        seen = {
            (row["r"], row["initial_strategy"], row["monty_policy"], row["switch_strategy"])
            for row in rows
        }
        self.assertIn((1.0, "highest_mu", "uniform_zero", "prior_best_switch"), seen)
        self.assertIn((0.0, "lowest_mu", "high_mu_zero", "oracle_best_switch"), seen)

        stage2_slice = [
            row
            for row in rows
            if row["r"] == 1.0
            and row["initial_strategy"] == "random"
            and row["monty_policy"] == "uniform_zero"
        ]
        values = {row["switch_strategy"]: row["empirical_reward"] for row in stage2_slice}
        self.assertGreater(values["prior_best_switch"], values["uniform_switch"])
        self.assertGreaterEqual(values["oracle_best_switch"], values["prior_best_switch"])


if __name__ == "__main__":
    unittest.main()
