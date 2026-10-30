from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator, TypeAlias


@dataclass(frozen=True, slots=True)
class Node:
    """Sommet commun à tout le projet.

    `id` identifie logiquement le nœud.
    `x` et `y` sont ses coordonnées spatiales.

    Pour les calculs métriques (straightness et information), le contrat du
    projet est que x/y soient exprimés dans un système de coordonnées projeté
    cohérent, idéalement en mètres.
    """

    id: int
    x: float = field(compare=False)
    y: float = field(compare=False)


EdgeKey: TypeAlias = tuple[Node, Node]


@dataclass(slots=True)
class Graph:
    """Graphe routier non orienté, simple et pondéré.

    Représentation principale :
        dict[Node, list[Node]]

    Les longueurs sont stockées séparément pour garder une liste d'adjacence
    simple.
    """

    adjacency: dict[Node, list[Node]] = field(default_factory=dict)
    edge_lengths: dict[EdgeKey, float] = field(default_factory=dict)

    @staticmethod
    def _edge_key(u: Node, v: Node) -> EdgeKey:
        """Clé canonique d'une arête non orientée."""
        return (u, v) if u.id <= v.id else (v, u)

    def add_node(self, node: Node) -> None:
        """Ajoute un nœud s'il n'existe pas déjà."""
        self.adjacency.setdefault(node, [])

    def add_edge(self, u: Node, v: Node, length: float) -> None:
        """Ajoute une arête non orientée u-v et sa longueur.

        Si plusieurs arêtes relient u et v, seule la plus courte est gardée.
        """
        if u == v:
            raise ValueError("Les boucles (u, u) ne sont pas autorisées.")

        if length <= 0:
            raise ValueError("La longueur d'une arête doit être > 0.")

        self.add_node(u)
        self.add_node(v)

        key = self._edge_key(u, v)

        if key in self.edge_lengths:
            self.edge_lengths[key] = min(self.edge_lengths[key], float(length))
            return

        self.adjacency[u].append(v)
        self.adjacency[v].append(u)
        self.edge_lengths[key] = float(length)

    def has_node(self, node: Node) -> bool:
        return node in self.adjacency

    def has_edge(self, u: Node, v: Node) -> bool:
        return self._edge_key(u, v) in self.edge_lengths

    def neighbors(self, node: Node) -> tuple[Node, ...]:
        """Voisins du nœud, sans exposer la liste interne aux modifications."""
        return tuple(self.adjacency[node])

    def edge_length(self, u: Node, v: Node) -> float:
        """Longueur de l'arête u-v."""
        return self.edge_lengths[self._edge_key(u, v)]

    def nodes(self) -> tuple[Node, ...]:
        return tuple(self.adjacency.keys())

    def edges(self) -> Iterator[tuple[Node, Node, float]]:
        """Itère une seule fois sur chaque arête non orientée."""
        for (u, v), length in self.edge_lengths.items():
            yield u, v, length

    def number_of_nodes(self) -> int:
        return len(self.adjacency)

    def number_of_edges(self) -> int:
        return len(self.edge_lengths)

    def __contains__(self, node: Node) -> bool:
        return self.has_node(node)

    def __len__(self) -> int:
        return self.number_of_nodes()

    def __str__(self) -> str:
        return f"Graph(nodes={self.number_of_nodes()}, edges={self.number_of_edges()})"
