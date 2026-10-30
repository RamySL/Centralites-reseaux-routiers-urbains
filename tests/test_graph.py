import unittest

from urban_centrality.graph import Graph, Node


class GraphTests(unittest.TestCase):
    def setUp(self) -> None:
        self.a = Node(1, 0.0, 0.0)
        self.b = Node(2, 1.0, 0.0)
        self.c = Node(3, 2.0, 0.0)

    def test_node_can_be_dict_key(self) -> None:
        values = {self.a: "A"}
        self.assertEqual(values[self.a], "A")

    def test_add_undirected_edge(self) -> None:
        graph = Graph()
        graph.add_edge(self.a, self.b, 12.5)

        self.assertIn(self.b, graph.neighbors(self.a))
        self.assertIn(self.a, graph.neighbors(self.b))
        self.assertEqual(graph.edge_length(self.a, self.b), 12.5)
        self.assertEqual(graph.edge_length(self.b, self.a), 12.5)

    def test_parallel_edges_keep_shortest_length(self) -> None:
        graph = Graph()
        graph.add_edge(self.a, self.b, 20.0)
        graph.add_edge(self.a, self.b, 12.0)

        self.assertEqual(graph.number_of_edges(), 1)
        self.assertEqual(graph.edge_length(self.a, self.b), 12.0)
        self.assertEqual(graph.neighbors(self.a).count(self.b), 1)

    def test_graph_summary(self) -> None:
        graph = Graph()
        graph.add_edge(self.a, self.b, 10.0)
        graph.add_edge(self.b, self.c, 15.0)

        self.assertEqual(graph.number_of_nodes(), 3)
        self.assertEqual(graph.number_of_edges(), 2)
        self.assertEqual(str(graph), "Graph(nodes=3, edges=2)")


if __name__ == "__main__":
    unittest.main()
