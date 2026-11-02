from collections import deque

from urban_centrality.graph import Graph, Node
from typing import TypeAlias
import heapq


class NotFoundInGraphException(Exception):
    """
    Exception levée lorsqu'une un graphe ne
    contient pas un noued.
    """


def compute(graph: Graph) -> dict[Node, float]:
    """Calcule la centralité d'éloignement (closeness centrality) pour tous les noeuds.

    La centralité 'closeness' d'un nœud évalue à quel point ce nœud est proche de
    tous les autres noeuds du réseau. Elle est définie comme l'inverse de la distance
    moyenne vers tous les autres sommets. Plus un nœud est central, plus sa valeur
    est élevée.

    Formule mathématique :
        C(i) = (N - 1) / somme(distances de i vers tous les autres noeuds)

    Complexité :
        - Temps : O(V * M log V) où V est le nombre de noeuds et M le nombre d'arêtes.
        Pour un graphe routier (graphe creux où M est proportionnel à V), la
        complexité pratique est de l'ordre de O(V² log V).
        - Espace : O(V) pour allouer le dictionnaire de résultats et stocker
        temporairement les tableaux de l'algorithme de Dijkstra.

    Contrat commun :
        - Ne doit pas modifier le graphe d'origine.

    Args:
        graph (Graph): Le graphe routier (non orienté et pondéré) sur lequel
            calculer la centralité.

    Returns:
        dict[Node, float]: Un dictionnaire associant chaque nœud à son score de
            centralité closeness. Si un nœud ne peut atteindre aucun autre nœud
            (graphe déconnecté), son score est de 0.0.
    """
    closeness_centrality: dict[Node, float] = dict()
    N = graph.__len__()

    # Un graphe avec 0 ou 1 neoud a une centralité de 0
    if N <= 1:
        return {node: 0.0 for node in graph.nodes()}

    for i in graph.nodes():
        # On récupère les distances (on ignore les prédécesseurs)
        distances, _ = Dijkstra(graph, i)

        # La somme des distances de 'i' vers tous les autres nœuds 'j'
        # distances[i] vaut 0, donc l'inclure dans la somme ne fausse rien
        somme = sum(distances.values())

        # Si la somme est infinie (graphe déconnecté) ou nulle (impossible ici sauf si N=1)
        if somme == float("inf") or somme == 0:
            closeness_centrality[i] = 0.0
        else:
            closeness_centrality[i] = (N - 1) / somme

    return closeness_centrality


ShortestPath: TypeAlias = tuple[dict[Node, float], dict[Node, Node]]


def Dijkstra(graph: Graph, depart: Node) -> ShortestPath:
    """Calcule les plus courts chemins depuis un nœud source vers tous les autres.

    Cette implémentation utilise une file de priorité (tas binaire via heapq)
    avec évaluation paresseuse (lazy deletion) pour garantir des performances
    optimales sur les graphes creux.

    Complexité:
        - Temps : O(M log V) où V est le nombre de noeuds et M le nombre d'arêtes :

            Au pire chaque arête du graphe peut générer une insertion dans notre file de priorité pq.
            On fera donc au maximum M insertions (heappush)
            Le tas contient au maximum M éléments.
            Extraire un élément (heappop) ou en insérer un coûte log (M).
            Mais comme dans un graphe simple M << V^2, on sait que log(M) <= log(V^2) = 2 log(V).
            donc log(M) est strictement équivalent à log (V).
            Puisqu'on fait au plus M opérations dans le tas, l'exploration coûte O(M log V)

        - Espace : O(V) pour stocker chauqe props : les distances, les prédécesseurs, O(M) pour la file

    Args:
        graph (Graph): Le graphe pondéré sur lequel effectuer la recherche.
        depart (Node): Le nœud source à partir duquel calculer les distances.

    Returns:
        ShortestPath: Un tuple contenant deux dictionnaires :
            - distances: associe chaque nœud à sa distance minimale depuis `depart`.
            - predecesseurs: associe chaque nœud à son parent dans le plus court chemin.
              (vaut None pour le nœud de départ ou les nœuds inaccessibles).

    Raises:
        NotFoundInGraphException: Si le nœud `depart` n'est pas dans le graphe.
    """
    if depart not in graph:
        raise NotFoundInGraphException(f"{depart} n'existe pas dans le graphe")

    # Initialisation O(V)
    distances: dict[Node, float] = {n: float("inf") for n in graph.nodes()}
    predecesseurs: dict[Node, Node] = {n: None for n in graph.nodes()}

    distances[depart] = 0.0

    # File de priorité : on stocke des tuples (distance, id_noeud, noeud)
    # L'id du noeud sert de départage si deux distances sont strictement égales,
    # car les objets Node ne sont pas comparables nativement avec <.
    pq = [(0.0, depart.id, depart)]

    # Set pour ignorer les versions obsolètes d'un noeud sorti du tas
    visites: set[Node] = set()

    while pq:
        # 1. Extraction du noeud le plus proche en O(log V)
        dist_courante, _, courant = heapq.heappop(pq)

        # Si le noeud a déjà été visité (grâce à une occurrence précédente plus courte), on l'ignore
        if courant in visites:
            continue

        # On valide la visite finale de ce noeud
        visites.add(courant)

        # 2. Mise à jour des voisins
        for voisin in graph.neighbors(courant):
            if voisin in visites:
                continue

            d = dist_courante + graph.edge_length(courant, voisin)

            # Si on trouve un chemin plus court
            if d < distances[voisin]:
                distances[voisin] = d
                predecesseurs[voisin] = courant

                # On pousse la nouvelle distance dans le tas en O(log V)
                heapq.heappush(pq, (d, voisin.id, voisin))

    return distances, predecesseurs
