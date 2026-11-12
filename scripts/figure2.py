"""Calcule les centralités des villes et trace l'équivalent de la Figure 2.

Exemples (depuis la racine du dépôt) :
    PYTHONPATH=src python scripts/figure2.py
    PYTHONPATH=src python scripts/figure2.py --centralities straightness closeness
    PYTHONPATH=src python scripts/figure2.py --cities Rome Chicago --recompute

Les scores sont enregistrés dans results/scores/<ville>_<centralité>.csv et
réutilisés aux lancements suivants (sauf avec --recompute).
"""

import argparse
import csv
import importlib
import time
from pathlib import Path

from urban_centrality.analysis.plotting import plot_figure_2
from urban_centrality.io.cities import CITIES
from urban_centrality.io.osmnx_loader import load_city

CENTRALITIES = ["closeness", "betweenness", "straightness", "information"]
SCORES_DIR = Path("results/scores")
FIGURE = Path("results/figures/figure2.png")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--cities", nargs="+", choices=CITIES, default=list(CITIES),
        help="villes à traiter (défaut : toutes)",
    )
    parser.add_argument(
        "--centralities", nargs="+", choices=CENTRALITIES, default=["straightness"],
        help="centralités à calculer (défaut : straightness)",
    )
    parser.add_argument(
        "--recompute", action="store_true",
        help="recalcule les scores même s'ils sont déjà enregistrés",
    )
    parser.add_argument(
        "--output", type=Path, default=FIGURE, help=f"image produite (défaut : {FIGURE})",
    )
    return parser.parse_args()


def get_scores(city: str, centrality: str, recompute: bool, graphs: dict) -> list[float]:
    """Lit les scores enregistrés, ou les calcule puis les enregistre."""
    path = SCORES_DIR / f"{city}_{centrality}.csv"
    if path.exists() and not recompute:
        with path.open() as f:
            return [float(row["score"]) for row in csv.DictReader(f)]

    if city not in graphs:  # un seul téléchargement par ville
        c = CITIES[city]
        graphs[city] = load_city(c.lat, c.lon, network_type=c.network_type)
        print(f"{city}: {graphs[city]}")

    compute = importlib.import_module(f"urban_centrality.algorithms.{centrality}").compute
    start = time.perf_counter()
    scores = compute(graphs[city])
    print(f"{city}: {centrality} en {time.perf_counter() - start:.1f} s")

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "x", "y", "score"])
        for node, score in scores.items():
            writer.writerow([node.id, node.x, node.y, score])
    return list(scores.values())


def main() -> None:
    args = parse_args()
    graphs = {}
    scores = {
        centrality: {
            city: get_scores(city, centrality, args.recompute, graphs)
            for city in args.cities
        }
        for centrality in args.centralities
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    categories = {name: city.category for name, city in CITIES.items()}
    for line in plot_figure_2(scores, categories, str(args.output)):
        print(line)
    print(f"Figure enregistrée : {args.output}")


if __name__ == "__main__":
    main()
