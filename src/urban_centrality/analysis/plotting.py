"""Reproduction de la Figure 2 : distributions cumulées et ajustements.

Une ligne par centralité, une colonne par catégorie de ville
(auto-organisée / planifiée). Points : données ; pointillés : meilleure loi.
"""

import matplotlib

matplotlib.use("Agg")  # pas d'affichage : on enregistre directement l'image
import matplotlib.pyplot as plt

from urban_centrality.analysis.distributions import best_fit, cumulative_distribution
from urban_centrality.io.cities import PLANNED, SELF_ORGANIZED

# scores[centralité][ville] = liste des valeurs de centralité des nœuds
Scores = dict[str, dict[str, list[float]]]


def plot_figure_2(scores: Scores, categories: dict[str, str], path: str) -> list[str]:
    """Trace la figure et l'enregistre dans `path`.

    `categories[ville]` donne la catégorie de chaque ville.
    Renvoie un résumé texte des ajustements (une ligne par ville et centralité).
    """
    columns = [SELF_ORGANIZED, PLANNED]
    fig, axes = plt.subplots(
        len(scores), 2, figsize=(10, 4 * len(scores)), squeeze=False
    )
    summary = []

    for row, (centrality, by_city) in enumerate(scores.items()):
        for col, category in enumerate(columns):
            ax = axes[row][col]
            cities = [name for name in by_city if categories[name] == category]
            summary += _plot_panel(ax, centrality, cities, by_city)
            ax.set_title(f"{centrality} — villes {category}s")

    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return summary


def _plot_panel(ax, centrality: str, cities: list[str], by_city) -> list[str]:
    """Un panneau : distribution de chaque ville + sa meilleure loi."""
    summary = []
    power_law = False

    for city in cities:
        c, p = cumulative_distribution(by_city[city])
        law = best_fit(by_city[city])

        points = ax.plot(c, p, "o", markersize=3, label=city)[0]
        ax.plot(c, law.predict(c), "--", color=points.get_color(), label=law.label())

        power_law |= law.law == "puissance"
        summary.append(f"{centrality:12s} {city:14s} {law.label():40s} R² = {law.r2:.3f}")

    # Échelle log-log pour une loi de puissance (droite), sinon semi-log.
    ax.set_yscale("log")
    if power_law:
        ax.set_xscale("log")
    ax.set_xlabel(f"C ({centrality})")
    ax.set_ylabel("P(C)")
    if cities:
        ax.legend(fontsize=7)
    return summary
