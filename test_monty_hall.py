import math
import unittest

from monty_hall_clean_conditional_switching import (
    simulate_conditional_switching,
    theoretical_conditional,
)
from monty_hall_generalised import simulate_monty_general, theoretical_probabilities


class MontyHallTheoryTests(unittest.TestCase):
    def assert_close(self, observed: float, expected: float, tolerance: float = 0.012) -> None:
        self.assertLessEqual(
            abs(observed - expected),
            tolerance,
            f"observed={observed}, expected={expected}, tolerance={tolerance}",
        )

    def test_theory_classical(self) -> None:
        theory = theoretical_probabilities(k=3, m=1, r=1)
        self.assertEqual(theory["stay"], 1 / 3)
        self.assertEqual(theory["switch"], 2 / 3)

    def test_generalised_empirical_matches_theory(self) -> None:
        cases = [
            (3, 1, 1),
            (10, 1, 1),
            (10, 1, 8),
            (10, 3, 4),
        ]
        for k, m, r in cases:
            with self.subTest(k=k, m=m, r=r):
                out = simulate_monty_general(
                    k=k,
                    m=m,
                    r=r,
                    n_experiments=400,
                    n_chances=500,
                    seed=1000 + 100 * k + 10 * m + r,
                )
                self.assert_close(out.empirical["stay"], out.theory["stay"])
                self.assert_close(out.empirical["switch"], out.theory["switch"])

    def test_conditional_empirical_matches_mixture_theory(self) -> None:
        out = simulate_conditional_switching(
            k=8,
            m=2,
            r=3,
            n_experiments=400,
            n_chances=500,
            switch_probability=0.35,
            seed=4242,
        )
        theory = theoretical_conditional(k=8, m=2, r=3, switch_probability=0.35)
        self.assert_close(out.empirical["stay"], theory["stay"])
        self.assert_close(out.empirical["switch"], theory["switch"])
        self.assert_close(out.empirical["conditional"], theory["conditional"])

    def test_conditional_default_probability(self) -> None:
        out = simulate_conditional_switching(k=7, m=1, r=2, n_experiments=5, n_chances=5, seed=7)
        self.assertTrue(math.isclose(out.switch_probability, 1 / (7 - 1 - 2)))


if __name__ == "__main__":
    unittest.main()
