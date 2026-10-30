# Architecture du projet

## But

Permettre aux trois membres de travailler indépendamment tout en partageant
exactement le même format de graphe.

```text
                    graph.py
                       ▲
          ┌────────────┼────────────┐
          │            │            │
       io/          algorithms/   analysis/
      OSMnx          centralités   résultats
```

## Règles

1. `graph.py` ne contient aucune centralité.
2. Chaque centralité vit dans son propre fichier.
3. Les centralités ne s'importent pas entre elles.
4. L'import OSMnx produit un `Graph` commun.
5. Toute centralité expose :

```python
def compute(graph: Graph) -> dict[Node, float]:
    ...
```

6. Une centralité ne doit pas modifier le graphe reçu.
7. Les distributions et graphiques sont séparés des algorithmes.

## Contrat du graphe

Représentation principale :

```python
dict[Node, list[Node]]
```

`Node` est une dataclass immuable et hashable.

Les longueurs sont stockées à part :

```python
dict[tuple[Node, Node], float]
```

Le graphe commun est non orienté, simple et pondéré par la longueur des rues.

- longueurs : mètres ;
- coordonnées `x`, `y` : système projeté cohérent avec un calcul métrique ;
- pas de boucle ;
- pas de voisin dupliqué ;
- si plusieurs arêtes relient les mêmes nœuds, on garde la plus courte.

## Pourquoi `Node` est `frozen=True`

`Node` sert de clé de dictionnaire. Une dataclass mutable avec `eq=True` est
normalement non hashable. `frozen=True` donne donc une identité stable et un
hash cohérent.

`x` et `y` ont `compare=False` : l'identité logique d'un nœud est son `id`.

## Responsabilités de `graph.py`

Seulement :

- `Node` ;
- `Graph` ;
- ajout de nœuds et d'arêtes ;
- lecture des voisins ;
- lecture des longueurs ;
- comptage et affichage simple.

Pas de BFS, Dijkstra, centralité, OSMnx ou statistique.

## Test rapide

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```
