import unittest

try:
    import networkx as nx
    from shapely.geometry import LineString

    from urban_centrality.io.osmnx_loader import to_graph
except ImportError:  # osmnx / networkx non installés
    nx = None


@unittest.skipIf(nx is None, "osmnx non installé")
class ToGraphTests(unittest.TestCase):
    def test_conversion(self) -> None:
        # Petit graphe au format OSMnx : arêtes parallèles et une boucle.
        osm = nx.MultiGraph()
        osm.add_node(10, x=0.0, y=0.0)
        osm.add_node(20, x=3.0, y=4.0)
        # Rue courbe (0,0) -> (3,0) -> (3,4) : 7 m.
        osm.add_edge(10, 20, geometry=LineString([(0, 0), (3, 0), (3, 4)]))
        # Rue droite sans géométrie : longueur = segment, 5 m.
        osm.add_edge(10, 20)
        osm.add_edge(10, 10, length=2.0)

        graph = to_graph(osm)
        a, b = graph.nodes()

        self.assertEqual((a.id, b.id), (10, 20))
        self.assertEqual((b.x, b.y), (3.0, 4.0))
        self.assertEqual(graph.number_of_edges(), 1)
        self.assertEqual(graph.edge_length(a, b), 5.0)

    def test_curved_street_uses_geometry(self) -> None:
        osm = nx.MultiGraph()
        osm.add_node(1, x=0.0, y=0.0)
        osm.add_node(2, x=3.0, y=4.0)
        osm.add_edge(1, 2, geometry=LineString([(0, 0), (3, 0), (3, 4)]))

        graph = to_graph(osm)
        a, b = graph.nodes()
        self.assertEqual(graph.edge_length(a, b), 7.0)


if __name__ == "__main__":
    unittest.main()
