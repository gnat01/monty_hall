import unittest

from monty_hall_variable_costs import (
    cost_sequence,
    solve_from_family,
    solve_variable_costs,
    switch_success,
)


class VariableCostTests(unittest.TestCase):
    def test_switch_success_matches_part_i_formula(self) -> None:
        self.assertAlmostEqual(switch_success(3, 1, 1), 2 / 3)
        self.assertAlmostEqual(switch_success(10, 3, 4), 0.54)

    def test_constant_cost_threshold_behavior(self) -> None:
        low = solve_from_family(50, 1, "constant", base=0.015)
        high = solve_from_family(50, 1, "constant", base=0.025)
        self.assertEqual(low.optimal_t, low.max_reveals)
        self.assertEqual(high.optimal_t, 0)

    def test_linear_cost_can_have_interior_optimum(self) -> None:
        out = solve_from_family(50, 1, "linear", base=0.0, slope=0.001)
        self.assertGreater(out.optimal_t, 0)
        self.assertLess(out.optimal_t, out.max_reveals)

    def test_saturating_cost_sequence_caps(self) -> None:
        costs = cost_sequence("linear_saturating", max_reveals=10, base=0.1, slope=0.05, saturation=0.2)
        self.assertEqual(costs[0], 0.1)
        self.assertAlmostEqual(costs[-1], 0.3)

    def test_rejects_wrong_cost_length(self) -> None:
        with self.assertRaises(ValueError):
            solve_variable_costs(10, 1, [0.1, 0.2])


if __name__ == "__main__":
    unittest.main()
