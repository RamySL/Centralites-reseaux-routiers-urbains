from urban_centrality.graph import Graph, Node


def compute(graph: Graph) -> dict[Node, float]:
    """Calcule la centralité information pour tous les nœuds.

    Contrat commun :
    - entrée : Graph
    - sortie : dict[Node, float]
    - ne doit pas modifier le graphe d'origine
    """
    raise NotImplementedError
