"""
network_failure_sim.py
----------------------

Utilitários para simular falhas de nós em grafos e propagação em cascata usando
NetworkX.  Estas funções são usadas pelo script de Monte Carlo para avaliar
resiliência.  O modelo é simplificado: cada nó falha com uma probabilidade
``p_node``, e as falhas propagam-se aos vizinhos com probabilidade
``p_propagate``.  O tempo de recuperação é o número de steps até que não
haja novas falhas.

Exemplo de uso:

```python
import json
import networkx as nx
from sim.network_failure_sim import simulate_failure

with open('data/sample_graph.json') as f:
    g_data = json.load(f)

G = nx.DiGraph()
G.add_nodes_from([n['id'] for n in g_data['nodes']])
G.add_edges_from([(e['source'], e['target']) for e in g_data['edges']])

recovery_time, failed_nodes = simulate_failure(G, p_node=0.1, p_propagate=0.3)
print(f"Tempo de recuperação: {recovery_time}, nós impactados: {len(failed_nodes)}")
```
"""

import random
from typing import Set, Tuple

import networkx as nx


def simulate_failure(graph: nx.Graph, p_node: float, p_propagate: float) -> Tuple[int, Set[int]]:
    """Simula falhas iniciais e propagação em um grafo.

    Args:
        graph: Grafo direcionado ou não direcionado do NetworkX.
        p_node: Probabilidade de cada nó falhar no início da simulação.
        p_propagate: Probabilidade de uma falha propagar-se de um nó para um vizinho.

    Returns:
        recovery_time: número de passos até cessar a propagação.
        failed_nodes: conjunto de IDs de nós que falharam durante a simulação.
    """
    # determina falhas iniciais
    failed: Set[int] = set()
    for node in graph.nodes:
        if random.random() < p_node:
            failed.add(node)
    # fila para BFS de propagação
    frontier = list(failed)
    recovery_time = 0
    while frontier:
        next_frontier = []
        recovery_time += 1
        for node in frontier:
            for neighbor in graph.neighbors(node):
                if neighbor not in failed and random.random() < p_propagate:
                    failed.add(neighbor)
                    next_frontier.append(neighbor)
        frontier = next_frontier
    return recovery_time, failed