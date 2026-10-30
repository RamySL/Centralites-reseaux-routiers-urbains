from urban_centrality.graph import Graph


def load_city(*args, **kwargs) -> Graph:
    """Importe et normalise une ville vers le Graph commun du projet.

    Contrat de sortie :
    - graphe non orienté ;
    - graphe simple ;
    - longueurs en mètres ;
    - coordonnées x/y adaptées aux distances spatiales ;
    - une seule instance logique de Node par intersection.
    """
    raise NotImplementedError
