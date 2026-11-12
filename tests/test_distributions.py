import unittest

try:
    import numpy as np

    from urban_centrality.analysis.distributions import best_fit, cumulative_distribution
except ImportError:  # numpy non installé
    np = None


@unittest.skipIf(np is None, "numpy non installé")
class DistributionTests(unittest.TestCase):
    def test_cumulative_distribution(self) -> None:
        c, p = cumulative_distribution([3.0, 1.0, 2.0, 2.0])
        self.assertEqual(c.tolist(), [1.0, 2.0, 3.0])
        self.assertEqual(p.tolist(), [1.0, 0.75, 0.25])

    def test_recognizes_each_law(self) -> None:
        # Échantillons tirés de chaque loi : best_fit doit la retrouver.
        rng = np.random.default_rng(0)
        samples = {
            "exponentielle": rng.exponential(2.0, 3000),
            "gaussienne": rng.normal(0.8, 0.05, 3000),
            "puissance": rng.pareto(2.0, 3000) + 1,  # P(C) ~ C^-2
        }
        for law, values in samples.items():
            self.assertEqual(best_fit(values).law, law)

    def test_parameters(self) -> None:
        rng = np.random.default_rng(1)
        self.assertAlmostEqual(best_fit(rng.exponential(2.0, 5000)).params[0], 2.0, delta=0.3)
        mu, sigma = best_fit(rng.normal(0.8, 0.05, 5000)).params
        self.assertAlmostEqual(mu, 0.8, delta=0.01)
        self.assertAlmostEqual(sigma, 0.05, delta=0.01)


if __name__ == "__main__":
    unittest.main()
