import unittest
from math import sqrt

from urban_centrality.algorithms.straightness import compute
from urban_centrality.graph import Graph, Node


class StraightnessTests(unittest.TestCase):
    def test_straight_line_gives_one(self) -> None:
        # Nœuds alignés, arêtes de la longueur euclidienne : trajets parfaitement droits.
        a, b, c = Node(1, 0, 0), Node(2, 1, 0), Node(3, 2, 0)
        graph = Graph()
        graph.add_edge(a, b, 1.0)
        graph.add_edge(b, c, 1.0)

        for score in compute(graph).values():
            self.assertAlmostEqual(score, 1.0)

    def test_detour_lowers_score(self) -> None:
        # Carré a-b-c-d : pour aller de a à c il faut faire 2 au lieu de sqrt(2).
        a, b, c, d = Node(1, 0, 0), Node(2, 1, 0), Node(3, 1, 1), Node(4, 0, 1)
        graph = Graph()
        for u, v in [(a, b), (b, c), (c, d), (d, a)]:
            graph.add_edge(u, v, 1.0)

        expected = (1 + 1 + sqrt(2) / 2) / 3
        for score in compute(graph).values():
            self.assertAlmostEqual(score, expected)

    def test_unreachable_node_contributes_zero(self) -> None:
        a, b, c = Node(1, 0, 0), Node(2, 1, 0), Node(3, 5, 5)
        graph = Graph()
        graph.add_edge(a, b, 1.0)
        graph.add_node(c)

        scores = compute(graph)
        self.assertAlmostEqual(scores[a], 0.5)
        self.assertAlmostEqual(scores[c], 0.0)

    def test_graph_is_not_modified(self) -> None:
        a, b = Node(1, 0, 0), Node(2, 3, 4)
        graph = Graph()
        graph.add_edge(a, b, 5.0)

        compute(graph)
        self.assertEqual(str(graph), "Graph(nodes=2, edges=1)")
        self.assertEqual(graph.edge_length(a, b), 5.0)

    def test_small_graphs(self) -> None:
        self.assertEqual(compute(Graph()), {})
        graph = Graph()
        graph.add_node(Node(1, 0, 0))
        self.assertEqual(list(compute(graph).values()), [0.0])


if __name__ == "__main__":
    unittest.main()
