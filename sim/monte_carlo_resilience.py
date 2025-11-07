"""
monte_carlo_resilience.py
-------------------------

Este script executa uma simulação de Monte Carlo para avaliar a resiliência do
ecossistema Helius sob diferentes taxas de falha de nós e capacidades de
serviço.  Para cada combinação de probabilidade de falha e capacidade de
processamento, o script executa ``N`` simulações, medindo o tempo até
recuperação da propagação de falhas, a fração de usuários impactados e
métricas de backpressure (tempo médio de espera, pico de espera, etc.).  Os
resultados são exportados para um CSV e gráficos interativos (Plotly) são
salvos em formato HTML.

Uso:

```bash
python sim/monte_carlo_resilience.py \
  --graph-path data/sample_graph.json \
  --n-sims 50 \
  --output-csv sim_results.csv \
  --output-html sim_plots.html
```

Dependências: networkx, simpy, pandas, numpy, plotly.
"""

import argparse
import json
import random
from pathlib import Path
from typing import Dict, List

import networkx as nx
import pandas as pd
import plotly.express as px

from .network_failure_sim import simulate_failure
from .backpressure_sim import simulate_backpressure


def load_graph(graph_path: Path) -> nx.DiGraph:
    """Carrega um grafo de um arquivo JSON no formato usado por data/generate_graph.py."""
    with open(graph_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    G = nx.DiGraph()
    for node in data["nodes"]:
        G.add_node(node["id"], **{k: v for k, v in node.items() if k != "id"})
    for edge in data["edges"]:
        G.add_edge(edge["source"], edge["target"], **{k: v for k, v in edge.items() if k not in ["source", "target"]})
    return G


def monte_carlo(
    G: nx.DiGraph,
    n_sims: int,
    failure_probs: List[float],
    capacities: List[int],
    p_propagate: float = 0.3,
    arrival_rate: float = 10.0,
    service_rate: float = 12.0,
) -> List[Dict[str, float]]:
    """Executa as simulações e retorna uma lista de resultados.

    Args:
        G: grafo de dependências.
        n_sims: número de simulações por combinação de parâmetros.
        failure_probs: lista de probabilidades de falha inicial (p_node).
        capacities: lista de capacidades do servidor (número de atendentes).
        p_propagate: probabilidade de propagação da falha.
        arrival_rate: taxa média de chegada para a fila SimPy.
        service_rate: taxa média de serviço para cada atendente.

    Returns:
        Lista de dicionários com métricas de cada simulação.
    """
    user_nodes = {n for n, attr in G.nodes(data=True) if attr.get("category") == "user"}
    results: List[Dict[str, float]] = []
    sim_id = 0
    for p_node in failure_probs:
        for capacity in capacities:
            for i in range(n_sims):
                sim_id += 1
                recovery_time, failed = simulate_failure(G, p_node, p_propagate)
                # calcula percentual de usuários impactados
                impacted_users = len(user_nodes & failed)
                user_impact_pct = impacted_users / len(user_nodes) * 100 if user_nodes else 0.0
                # simula backpressure
                queue_metrics = simulate_backpressure(
                    arrival_rate=arrival_rate,
                    service_rate=service_rate,
                    capacity=capacity,
                    sim_time=100.0,
                )
                result = {
                    "simulation_id": sim_id,
                    "p_node": p_node,
                    "capacity": capacity,
                    "recovery_time": recovery_time,
                    "failed_nodes": len(failed),
                    "user_impact_pct": user_impact_pct,
                    "avg_wait": queue_metrics["avg_wait"],
                    "max_wait": queue_metrics["max_wait"],
                }
                results.append(result)
    return results


def generate_plots(df: pd.DataFrame, output_html: Path) -> None:
    """Gera gráficos interativos para explorar a distribuição das métricas.

    Salva os gráficos em um único arquivo HTML contendo tabs para cada plot.
    """
    figs = []
    # Histograma do tempo de recuperação
    figs.append(px.histogram(df, x="recovery_time", nbins=20, title="Distribuição do Tempo de Recuperação"))
    # Histograma do impacto em usuários
    figs.append(px.histogram(df, x="user_impact_pct", nbins=20, title="Percentual de Usuários Impactados"))
    # Scatter: tempo de recuperação vs impacto em usuários
    figs.append(px.scatter(df, x="recovery_time", y="user_impact_pct", color="p_node", title="Recuperação vs Impacto"))
    # Histograma do tempo médio de espera
    figs.append(px.histogram(df, x="avg_wait", nbins=20, title="Tempo Médio de Espera (fila)"))
    # Salva todos os gráficos em um único HTML
    with open(output_html, "w", encoding="utf-8") as f:
        for fig in figs:
            f.write(fig.to_html(full_html=False, include_plotlyjs="cdn"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Monte Carlo resilience simulation")
    parser.add_argument("--graph-path", type=Path, default=Path("data/sample_graph.json"), help="Caminho para o grafo JSON")
    parser.add_argument("--n-sims", type=int, default=50, help="Número de simulações por conjunto de parâmetros")
    parser.add_argument("--output-csv", type=Path, default=Path("sim_results.csv"), help="Arquivo CSV para salvar resultados")
    parser.add_argument("--output-html", type=Path, default=Path("sim_plots.html"), help="Arquivo HTML para salvar gráficos")
    parser.add_argument("--seed", type=int, default=None, help="Semente para reprodutibilidade")
    args = parser.parse_args()
    if args.seed is not None:
        random.seed(args.seed)
    G = load_graph(args.graph_path)
    # definições de parâmetros: probabilidades de falha e capacidades de atendimento
    failure_probs = [0.05, 0.1, 0.2]
    capacities = [1, 2, 3]
    results = monte_carlo(
        G,
        n_sims=args.n_sims,
        failure_probs=failure_probs,
        capacities=capacities,
        p_propagate=0.3,
        arrival_rate=10.0,
        service_rate=12.0,
    )
    df = pd.DataFrame(results)
    # salva CSV
    df.to_csv(args.output_csv, index=False)
    # gera e salva gráficos
    generate_plots(df, args.output_html)
    print(f"Resultados salvos em {args.output_csv}, gráficos em {args.output_html}")


if __name__ == "__main__":
    main()