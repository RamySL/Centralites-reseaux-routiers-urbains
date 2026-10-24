# Centralités dans les réseaux routiers urbains

Projet universitaire réalisé dans le cadre du module **Analyse d'algorithme, Graphes et applications**, autour de la science des réseaux : reproduction et extension de l'étude

> P. Crucitti, V. Latora, S. Porta, *Centrality measures in spatial networks of urban streets*, Physical Review E 73, 036125 (2006).

## Sujet

Une ville peut être vue comme un **réseau spatial** : les intersections sont les nœuds, les rues sont les arêtes, pondérées par leur longueur en mètres. L'article montre qu'un ensemble de mesures de centralité permet de caractériser la structure d'une ville, et de distinguer :

- les villes **auto-organisées** (centres historiques, tissu organique), dont certaines distributions de centralité suivent une **loi de puissance** ;
- les villes **planifiées** (plans en grille), dont les distributions sont **exponentielles ou gaussiennes**.

L'objectif du projet est de vérifier si ces résultats tiennent sur **d'autres villes** que celles de l'article.

## Objectifs

- Implémenter les quatre centralités de l'article, en distances métriques (et non topologiques) :
  - **Closeness** : proximité moyenne d'un nœud à tous les autres ;
  - **Betweenness** : part des plus courts chemins qui passent par le nœud ;
  - **Straightness** : écart entre le trajet réel et la ligne droite ;
  - **Information** : perte d'efficacité du réseau quand le nœud est désactivé.
- Récupérer des réseaux routiers de villes auto-organisées et planifiées via [OSMnx](https://github.com/gboeing/osmnx) (OpenStreetMap).
- Comparer les résultats à ceux de l'article et discuter leur cohérence.