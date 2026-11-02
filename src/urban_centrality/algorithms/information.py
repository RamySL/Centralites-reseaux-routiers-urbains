from math import hypot
from typing import TypeAlias
import heapq
from urban_centrality.graph import Graph, Node


class NotFoundInGraphException(Exception):
    pass


ShortestPath: TypeAlias = tuple[dict[Node, float], dict[Node, Node]]


def Dijkstra(graph: Graph, depart: Node, ignore_node: Node = None) -> ShortestPath:
    """Calcule les plus courts chemins en pouvant ignorer un noeud à la volée.

    Cette version optimisée de Dijkstra permet de simuler la suppression d'un noeud
    sans avoir à reconstruire un nouveau graphe en mémoire.

    Complexité :
        - Temps : O(M log V) où V est le nombre de noeuds et M le nombre d'arêtes.
        - Espace : O(V) pour stocker les distances, les prédécesseurs et la file.

    Args:
        graph (Graph): Le graphe pondéré sur lequel effectuer la recherche.
        depart (Node): Le noeud source à partir duquel calculer les distances.
        ignore_node (Node, optional): Un noeud à ignorer totalement lors de
            l'exploration, simulant ainsi sa désactivation. Par défaut à None.

    Returns:
        ShortestPath: Un tuple contenant deux dictionnaires :
            - distances: associe chaque noeud à sa distance minimale depuis `depart`.
            - predecesseurs: associe chaque noeud à son parent dans le plus court chemin.

    Raises:
        NotFoundInGraphException: Si le noeud `depart` n'est pas dans le graphe.
    """
    if depart not in graph:
        raise NotFoundInGraphException(f"{depart} n'existe pas")

    distances = {n: float("inf") for n in graph.nodes()}
    predecesseurs = {n: None for n in graph.nodes()}

    distances[depart] = 0.0
    pq = [(0.0, depart.id, depart)]
    visites = set()

    while pq:
        dist_courante, _, courant = heapq.heappop(pq)

        if courant in visites:
            continue
        visites.add(courant)

        for voisin in graph.neighbors(courant):
            # EXCLUSION À LA VOLÉE
            if ignore_node and voisin.id == ignore_node.id:
                continue

            if voisin in visites:
                continue

            d = dist_courante + graph.edge_length(courant, voisin)

            if d < distances[voisin]:
                distances[voisin] = d
                predecesseurs[voisin] = courant
                heapq.heappush(pq, (d, voisin.id, voisin))

    return distances, predecesseurs


def euclidean_distance(i: Node, j: Node) -> float:
    """Calcule la distance euclidienne (à vol d'oiseau) entre deux noeuds.

    Complexité :
        - Temps : O(1)
        - Espace : O(1)

    Args:
        i (Node): Le premier noeud.
        j (Node): Le second noeud.

    Returns:
        float: La distance géométrique linéaire entre i et j.
    """
    return hypot(i.x - j.x, i.y - j.y)


def compute(graph: Graph) -> dict[Node, float]:
    """Calcule la centralité d'information (Information Centrality) pour tous les noeuds.

    La centralité d'information mesure la chute d'efficacité globale du réseau
    lorsqu'un noeud spécifique est désactivé. Plus la chute est grande, plus le
    noeud est crucial pour la connectivité du réseau.

    Cette implémentation utilise l'optimisation de l'arbre des plus courts chemins :
    le recalcul de Dijkstra n'est déclenché que si le noeud retiré agit comme un
    pont vital (noeud intermédiaire) pour la source évaluée.

    Complexité :
        - Temps : O(V * P_moyen * M log V) où V est le nombre total de noeuds,
          M le nombre d'arêtes, et P_moyen le nombre moyen de noeuds intermédiaires
          (ponts) par arbre de plus courts chemins. C'est une amélioration majeure
          par rapport à l'approche naïve en O(V² * M log V).
        - Espace : O(V) pour allouer le dictionnaire de résultats et les variables
          de cumul d'efficacité.

    Contrat commun :
        - Ne doit pas modifier le graphe d'origine.

    Args:
        graph (Graph): Le graphe routier sur lequel calculer la centralité.

    Returns:
        dict[Node, float]: Un dictionnaire associant chaque noeud à son score
            de centralité d'information (valeur comprise entre 0.0 et 1.0).
    """
    N = graph.number_of_nodes()
    if N < 2:
        return {node: 0.0 for node in graph.nodes()}

    nodes = graph.nodes()

    # On va stocker l'efficacité globale lorsque le noeud k est retiré
    E_k_total = {n: 0.0 for n in nodes}
    E_orig_total = 0.0

    # Au lieu de boucler sur "le noeud retiré", on boucle sur "la source"
    for i in nodes:
        distances, predecesseurs = Dijkstra(graph, i)

        # 1. Calcul de la contribution de la source 'i' au graphe normal
        C_i = 0.0
        for j in nodes:
            if i != j and distances[j] != float("inf"):
                C_i += euclidean_distance(i, j) / distances[j]

        E_orig_total += C_i

        # 2. Quels sont les noeuds qui servent de ponts/étapes depuis 'i' ?
        # set() dédoublonne automatiquement les valeurs.
        intermediate_nodes = set(predecesseurs.values())
        intermediate_nodes.discard(None)  # On retire None (le parent de la source)
        intermediate_nodes.discard(i)  # La source n'est pas un intermédiaire

        # 3. Évaluation de l'impact du retrait de chaque noeud 'k'
        for k in nodes:
            if k == i:
                # Si on retire la source i, sa propre contribution devient 0
                continue

            if k in intermediate_nodes:
                # CAS A : k est un pont vital depuis i.
                # On doit relancer Dijkstra depuis i en ignorant k.
                new_dist, _ = Dijkstra(graph, i, ignore_node=k)
                C_new = 0.0
                for j in nodes:
                    if j != i and j != k and new_dist[j] != float("inf"):
                        C_new += euclidean_distance(i, j) / new_dist[j]
                E_k_total[k] += C_new
            else:
                # CAS B : k n'est PAS un pont.
                # Retirer k ne casse que la destination k. Tous les autres chemins restent intacts !
                val = 0.0
                if distances[k] != float("inf"):
                    val = euclidean_distance(i, k) / distances[k]

                # La nouvelle contribution est juste l'ancienne (C_I graphe originl) moins le trajet vers k
                E_k_total[k] += C_i - val

    # 4. Calcul final des scores
    norm = N * (N - 1)
    E_orig = E_orig_total / norm

    if E_orig == 0.0:
        return {n: 0.0 for n in nodes}

    CI = {}
    for k in nodes:
        E_k = E_k_total[k] / norm
        CI[k] = (E_orig - E_k) / E_orig

    return CI
