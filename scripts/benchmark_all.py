import time
import random
import math
import matplotlib.pyplot as plt

from urban_centrality.graph import Graph, Node

# Importez ici toutes vos centralités implémentées
from urban_centrality.algorithms.closeness import compute as compute_closeness
from urban_centrality.algorithms.information import compute as compute_information

# from urban_centrality.algorithms.betweenness import compute as compute_betweenness
from urban_centrality.algorithms.straightness import compute as compute_straightness


def generer_graphe_test(nb_noeuds: int, nb_aretes: int) -> Graph:
    """Génère un graphe aléatoire simulant un réseau routier creux."""
    g = Graph()
    noeuds = []
    for i in range(nb_noeuds):
        n = Node(id=i, x=random.uniform(0, 1000), y=random.uniform(0, 1000))
        g.add_node(n)
        noeuds.append(n)

    # Sécurité pour éviter la boucle infinie si on demande trop d'arêtes
    max_aretes = nb_noeuds * (nb_noeuds - 1) // 2
    nb_aretes = min(nb_aretes, max_aretes)

    aretes_creees = 0
    while aretes_creees < nb_aretes:
        u = random.choice(noeuds)
        v = random.choice(noeuds)
        if u != v and not g.has_edge(u, v):
            distance = random.uniform(10.0, 100.0)
            g.add_edge(u, v, distance)
            aretes_creees += 1

    return g


def main():
    # 1. Configuration du benchmark
    # Tailles des graphes à tester (N)
    tailles_noeuds = [20, 50, 100, 150, 200, 300]
    RATIO_ARETES = 2.5  # M = 2.5 * V (typique d'un réseau routier)

    # Les algorithmes à tester
    algorithmes = {
        "Closeness": compute_closeness,
        "Information": compute_information,
        "Straightness": compute_straightness,
    }

    # Dictionnaire pour stocker les temps de calcul
    temps_execution = {nom: [] for nom in algorithmes}

    # 2. Exécution du benchmark
    print("Démarrage du benchmark...\n")
    for N in tailles_noeuds:
        M = int(N * RATIO_ARETES)
        print(f"Génération d'un graphe de {N} nœuds et {M} arêtes...")
        graphe = generer_graphe_test(N, M)

        for nom, fonction in algorithmes.items():
            debut = time.perf_counter()
            fonction(graphe)
            fin = time.perf_counter()

            duree = fin - debut
            temps_execution[nom].append(duree)
            print(f"  - {nom:12s} : {duree:.4f} sec")
        print("-" * 40)

    # 3. Tracé des courbes (Matplotlib)
    plt.figure(figsize=(10, 6))

    couleurs = {"Closeness": "blue", "Information": "red", "Straightness": "green"}

    for nom, temps in temps_execution.items():
        # Courbe empirique réelle (ligne pleine)
        plt.plot(
            tailles_noeuds,
            temps,
            marker="o",
            label=f"{nom} (Réel)",
            color=couleurs.get(nom, "black"),
        )

        # Calcul et tracé de la courbe théorique mise à l'échelle (en pointillés)
        # On aligne la courbe théorique sur le dernier point réel calculé
        T_max_reel = temps[-1]
        N_max = tailles_noeuds[-1]

        valeurs_theoriques = []
        for N in tailles_noeuds:
            M = N * RATIO_ARETES
            if nom in ("Closeness", "Straightness"):
                # Closeness / Straightness : un Dijkstra par nœud, O(V * M log V) = O(V^2 log V)
                complexite_max = (N_max**2) * math.log(N_max)
                complexite_N = (N**2) * math.log(N)

            elif nom == "Information":
                # Information: O(V * P_moyen * M log V).
                # P_moyen évolue souvent en sqrt(V). Donc ~ O(V^2.5 log V)
                complexite_max = (N_max**2.5) * math.log(N_max)
                complexite_N = (N**2.5) * math.log(N)
            else:
                complexite_max, complexite_N = 1, 1

            # Mise à l'échelle de la théorie pour toucher le dernier point empirique
            constante = T_max_reel / complexite_max if complexite_max > 0 else 0
            valeurs_theoriques.append(constante * complexite_N)

        plt.plot(
            tailles_noeuds,
            valeurs_theoriques,
            linestyle="--",
            color=couleurs.get(nom, "black"),
            alpha=0.5,
            label=f"{nom} (Théorie)",
        )

    # Mise en forme du graphique
    plt.title(
        "Benchmark des Centralités : Temps d'exécution vs Taille du graphe", fontsize=14
    )
    plt.xlabel("Nombre de nœuds (V)", fontsize=12)
    plt.ylabel("Temps d'exécution (secondes)", fontsize=12)
    plt.grid(True, linestyle=":", alpha=0.7)
    plt.legend()
    plt.tight_layout()

    # Sauvegarde et affichage
    chemin_image = "results/figures/benchmark_complexite.png"
    plt.savefig(chemin_image, dpi=300)
    print(f"\nGraphique sauvegardé dans : {chemin_image}")
    plt.show()


if __name__ == "__main__":
    main()
