"""Simulate a red team attack on the graph by injecting malicious nodes and edges.

This script loads a graph in NetworkX node-link JSON format, adds a number of
malicious nodes and randomly connects them to existing nodes. The
modified graph is written back to a new JSON file. Use this tool to
evaluate how graph poisoning impacts centrality measures and downstream
recommendations.

Usage:

    python scripts/red_team_attack.py --input data/sample_graph.json --output data/poisoned_graph.json --num-nodes 10 --edges-per-node 3

"""

import argparse
import json
import random
from pathlib import Path
import networkx as nx


def inject_attack(graph: nx.Graph, num_nodes: int, edges_per_node: int) -> nx.Graph:
    """Add malicious nodes and connect them randomly to existing nodes."""
    max_node = max(graph.nodes) if graph.nodes else 0
    existing_nodes = list(graph.nodes())
    for i in range(1, num_nodes + 1):
        node_id = max_node + i
        graph.add_node(node_id, category="malicious")
        targets = random.sample(existing_nodes, min(edges_per_node, len(existing_nodes)))
        for t in targets:
            graph.add_edge(node_id, t, relation="attack")
    return graph


def main(input_path: str, output_path: str, num_nodes: int, edges_per_node: int) -> None:
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    G = nx.node_link_graph(data)
    G = inject_attack(G, num_nodes, edges_per_node)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(nx.node_link_data(G), f, ensure_ascii=False, indent=2)
    print(f"Injected {num_nodes} malicious nodes. Output written to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inject malicious nodes and edges into a graph")
    parser.add_argument("--input", required=True, help="Path to input graph JSON")
    parser.add_argument("--output", required=True, help="Path to output poisoned graph JSON")
    parser.add_argument("--num-nodes", type=int, default=5, help="Number of malicious nodes to add")
    parser.add_argument("--edges-per-node", type=int, default=2, help="Edges per malicious node")
    args = parser.parse_args()
    main(args.input, args.output, args.num_nodes, args.edges_per_node)