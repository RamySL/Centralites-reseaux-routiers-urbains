"""Distributions cumulées de centralité et ajustements (Figure 2 de l'article).

Distribution cumulée : P(C) = proportion de nœuds dont la centralité est >= C.

Trois lois sont testées, comme dans l'article :
    exponentielle  P(C) ~ exp(-C / s)                  (single scale)
    gaussienne     P(C) = P(X >= C), X ~ N(μ, σ²)      (single scale)
    puissance      P(C) ~ C^(-γ)                       (broad scale)

- exponentielle et puissance : droites en semi-log et en log-log, ajustées
  par moindres carrés sur log P (log P = a - C/s, log P = a - γ log C).
- gaussienne : μ et σ sont la moyenne et l'écart-type des valeurs. On ne
  reprend pas la forme exp(-C²/2σ²) de l'article, centrée en 0 : elle ne
  convient pas à la straightness ou à la closeness, concentrées loin de 0.

On garde la loi dont le R² (calculé sur log P) est le plus élevé.
"""

from dataclasses import dataclass
from math import erfc, sqrt

import numpy as np


@dataclass(frozen=True)
class Fit:
    """Loi ajustée : `params` = (s,), (μ, σ) ou (γ,) ; `scale` = constante."""

    law: str
    params: tuple[float, ...]
    scale: float
    r2: float

    def predict(self, c: np.ndarray) -> np.ndarray:
        """Valeurs de P(C) prédites par la loi."""
        c = np.asarray(c, dtype=float)
        if self.law == "exponentielle":
            (s,) = self.params
            return self.scale * np.exp(-c / s)
        if self.law == "gaussienne":
            mu, sigma = self.params
            return np.array([0.5 * erfc((x - mu) / (sigma * sqrt(2))) for x in c])
        (gamma,) = self.params
        return self.scale * c**-gamma

    def label(self) -> str:
        """Texte court pour une légende, ex. « exponentielle, s = 0.12 »."""
        names = {"exponentielle": ["s"], "gaussienne": ["μ", "σ"], "puissance": ["γ"]}
        values = ", ".join(
            f"{n} = {v:.3g}" for n, v in zip(names[self.law], self.params)
        )
        return f"{self.law}, {values}"


LAWS = ("exponentielle", "gaussienne", "puissance")


def cumulative_distribution(values) -> tuple[np.ndarray, np.ndarray]:
    """Renvoie (C, P(C)) pour chaque valeur distincte, C croissant."""
    values = np.sort(np.asarray(list(values), dtype=float))
    c, first_index = np.unique(values, return_index=True)
    # Nombre de valeurs >= c = n - (indice de la première occurrence de c).
    p = (len(values) - first_index) / len(values)
    return c, p


def fit(values, law: str) -> Fit:
    """Ajuste une loi sur la distribution cumulée des valeurs."""
    values = np.asarray(list(values), dtype=float)
    c, p = cumulative_distribution(values)

    if law == "gaussienne":
        result = Fit(law, (values.mean(), values.std()), 1.0, 0.0)
    elif law == "exponentielle":
        slope, intercept = np.polyfit(c, np.log(p), 1)
        result = Fit(law, (-1 / slope,), np.exp(intercept), 0.0)
    else:
        keep = c > 0  # log C impossible en 0
        c, p = c[keep], p[keep]
        slope, intercept = np.polyfit(np.log(c), np.log(p), 1)
        result = Fit(law, (-slope,), np.exp(intercept), 0.0)

    r2 = _r2(np.log(p), np.log(np.maximum(result.predict(c), 1e-300)))
    return Fit(result.law, result.params, result.scale, r2)


def best_fit(values) -> Fit:
    """Loi (parmi les trois) qui ajuste le mieux la distribution."""
    return max((fit(values, law) for law in LAWS), key=lambda f: f.r2)


def _r2(observed: np.ndarray, predicted: np.ndarray) -> float:
    """Coefficient de détermination (1 = ajustement parfait)."""
    total = np.sum((observed - observed.mean()) ** 2)
    if total == 0:
        return 0.0
    return float(1 - np.sum((observed - predicted) ** 2) / total)
