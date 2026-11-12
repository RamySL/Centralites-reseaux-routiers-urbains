"""Import d'un réseau routier OpenStreetMap vers le `Graph` commun du projet.

Comme dans l'article, on prend un carré d'un mile de côté (environ 1,6 km)
centré sur un point de la ville. Les intersections sont les nœuds, les rues
sont les arêtes pondérées par leur longueur en mètres.
"""

from math import hypot

import osmnx as ox

from urban_centrality.graph import Graph, Node

# Moitié du côté d'un carré d'un mile, en mètres.
HALF_MILE = 804.672

# Cache des requêtes OSM dans data/raw (ignoré par git).
ox.settings.cache_folder = "data/raw/osmnx_cache"


def load_city(
    lat: float,
    lon: float,
    half_side: float = HALF_MILE,
    network_type: str = "drive",
) -> Graph:
    """Télécharge le réseau autour de (lat, lon) et le convertit en `Graph`.

    Étapes :
    1. téléchargement d'un carré de côté 2 * half_side, rues simplifiées
       (seules les intersections et impasses restent des nœuds) ;
    2. projection en UTM : x, y en mètres, pour la distance à vol d'oiseau ;
    3. réduction à la plus grande composante connexe, puis non orienté ;
    4. conversion vers `Graph` (graphe simple, plus courte arête gardée).

    `network_type` : "drive" (rues carrossables), "walk" (ex. Venise), "all"...
    """
    osm_graph = ox.graph_from_point(
        (lat, lon),
        dist=half_side,
        dist_type="bbox",
        network_type=network_type,
        simplify=True,
    )
    osm_graph = ox.project_graph(osm_graph)
    # Faiblement connexe en orienté = connexe une fois non orienté.
    osm_graph = ox.truncate.largest_component(osm_graph, strongly=False)
    osm_graph = ox.convert.to_undirected(osm_graph)
    return to_graph(osm_graph)


def to_graph(osm_graph) -> Graph:
    """Convertit un graphe networkx projeté en `Graph`.

    La longueur d'une rue est mesurée dans le plan projeté (voir
    `_projected_length`). Les boucles sont ignorées ; pour des arêtes
    parallèles, `Graph.add_edge` garde la plus courte.
    """
    graph = Graph()
    nodes = {
        osm_id: Node(int(osm_id), float(data["x"]), float(data["y"]))
        for osm_id, data in osm_graph.nodes(data=True)
    }
    for node in nodes.values():
        graph.add_node(node)

    for u, v, data in osm_graph.edges(data=True):
        if u != v:
            graph.add_edge(nodes[u], nodes[v], _projected_length(nodes[u], nodes[v], data))

    return graph


def _projected_length(a: Node, b: Node, data: dict) -> float:
    """Longueur de la rue a-b dans le même repère que x, y.

    Le champ `length` d'OSMnx est calculé sur la sphère, avant projection :
    il peut être un peu plus court que la ligne droite projetée, et le
    rapport de la straightness dépasserait alors 1. On mesure donc le tracé
    projeté (`geometry`), ou le segment a-b si la rue est droite.
    """
    if "geometry" in data:
        return data["geometry"].length
    return hypot(a.x - b.x, a.y - b.y)
