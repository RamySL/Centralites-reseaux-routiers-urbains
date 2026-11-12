"""Villes étudiées : aucune ne figure dans l'article.

Chaque ville est un carré d'un mile de côté centré sur (lat, lon).
`network_type` vaut "walk" quand le tissu historique est surtout piéton
(médinas) : le réseau carrossable y serait presque vide.
"""

from dataclasses import dataclass

SELF_ORGANIZED = "auto-organisée"
PLANNED = "planifiée"


@dataclass(frozen=True)
class City:
    name: str
    lat: float
    lon: float
    category: str
    network_type: str = "drive"


CITIES = {
    city.name: city
    for city in [
        # Villes auto-organisées (centres historiques, tissu organique)
        City("Fes", 34.0640, -4.9730, SELF_ORGANIZED, "walk"),
        City("Rome", 41.8986, 12.4769, SELF_ORGANIZED),
        City("Istanbul", 41.0086, 28.9700, SELF_ORGANIZED),
        # Villes planifiées (plans en grille)
        City("Chicago", 41.8781, -87.6298, PLANNED),
        City("La_Plata", -34.9214, -57.9545, PLANNED),
        City("Philadelphia", 39.9526, -75.1652, PLANNED),
    ]
}
