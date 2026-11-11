"""Centralité straightness

    C_S(i) = 1 / (N - 1) * somme_{j != i} d_eucl(i, j) / d(i, j)

d(i, j)      : longueur du plus court chemin dans le réseau (mètres).
d_eucl(i, j) : distance à vol d'oiseau entre i et j

Chaque terme vaut au plus 1 : un score proche de 1 signifie que, depuis i,
les trajets réels sont presque aussi directs que la ligne droite
"""

import heapq
from math import hypot, inf

from urban_centrality.graph import Graph, Node


def compute(graph: Graph) -> dict[Node, float]:
    """Calcule la straightness de tous les noeuds.

    Un noeud j inaccessible depuis i contribue 0 (d(i, j) infinie).
    Le graphe n'est pas modifié.

    Complexité : un Dijkstra par noeud, soit O(N * M log N),
    donc ~O(N² log N) sur un réseau routier (M proportionnel à N).
    """
    nodes = graph.nodes()
    n = len(nodes)

    if n < 2:
        return {node: 0.0 for node in nodes}

    scores: dict[Node, float] = {}
    for source in nodes:
        distances = _shortest_distances(graph, source)

        total = 0.0
        for target, d in distances.items():
            if target != source:
                total += _euclidean(source, target) / d

        scores[source] = total / (n - 1)

    return scores


def _shortest_distances(graph: Graph, source: Node) -> dict[Node, float]:
    """Dijkstra : distances depuis `source` vers les nœuds accessibles uniquement."""
    distances: dict[Node, float] = {source: 0.0}
    # L'id départage les distances égales.
    heap = [(0.0, source.id, source)]
    done: set[Node] = set()

    while heap:
        d, _, node = heapq.heappop(heap)
        if node in done:
            continue  # entrée obsolète, déjà traitée avec distance plus courte
        done.add(node)

        for neighbor in graph.neighbors(node):
            new_d = d + graph.edge_length(node, neighbor)
            if new_d < distances.get(neighbor, inf):
                distances[neighbor] = new_d
                heapq.heappush(heap, (new_d, neighbor.id, neighbor))

    return distances


def _euclidean(a: Node, b: Node) -> float:
    """Distance a vol d'oiseau entre deux noeuds a et b"""
    return hypot(a.x - b.x, a.y - b.y)
