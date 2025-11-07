#!/usr/bin/env python3
"""
generate_graph.py
-----------------

Este script cria um grafo direcionado representando a topologia e o conhecimento da infraestrutura
da Helius Systems.  As entidades incluem serviços de microserviços, data stores, regiões de cloud,
dispositivos de borda, modelos, datasets e usuários.  As relações cobrem dependências,
chamadas entre serviços, replicação e monitoramento.  O grafo resultante possui hubs e
estruturas modulares que imitam distribuições de grau com cauda pesada.

Uso:
    python generate_graph.py --n-services 15 --n-data-stores 5 --output-prefix graph

Argumentos:
    --n-services         Número de serviços (padrão: 15)
    --n-data-stores      Número de repositórios de dados (padrão: 5)
    --n-regions          Número de regiões de cloud (padrão: 3)
    --n-edge-devices     Número de dispositivos de borda (padrão: 20)
    --n-models           Número de modelos de ML (padrão: 5)
    --n-datasets         Número de datasets (padrão: 5)
    --n-users            Número de usuários (padrão: 10)
    --output-prefix      Prefixo para os arquivos de saída (gerará .nodes.csv, .edges.csv e .json)
    --seed               Semente para reprodução

O script gera três arquivos:
    <prefix>_nodes.csv  – tabela de nós com colunas: id, label, category
    <prefix>_edges.csv  – tabela de arestas com colunas: source, target, type
    <prefix>.json       – grafo em formato JSON (lista de nós e arestas) útil para importar em outras bibliotecas
"""

import argparse
import csv
import json
import os
import random
from typing import Dict, List, Tuple


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gerador de grafo de dependências")
    parser.add_argument("--n-services", type=int, default=15, help="Número de microserviços")
    parser.add_argument("--n-data-stores", type=int, default=5, help="Número de data stores")
    parser.add_argument("--n-regions", type=int, default=3, help="Número de regiões de cloud")
    parser.add_argument("--n-edge-devices", type=int, default=20, help="Número de dispositivos de borda")
    parser.add_argument("--n-models", type=int, default=5, help="Número de modelos de ML")
    parser.add_argument("--n-datasets", type=int, default=5, help="Número de datasets")
    parser.add_argument("--n-users", type=int, default=10, help="Número de usuários")
    parser.add_argument(
        "--output-prefix",
        type=str,
        default="graph",
        help="Prefixo para arquivos de saída (resultará em <prefix>_nodes.csv etc)",
    )
    parser.add_argument("--seed", type=int, default=None, help="Semente para o gerador aleatório")
    return parser.parse_args()


def create_nodes(args: argparse.Namespace) -> List[Dict[str, object]]:
    """Cria lista de dicionários representando nós com categorias.  IDs começam em 1."""
    nodes = []
    next_id = 1
    # serviços
    for i in range(args.n_services):
        name = f"service_{i:02d}"
        nodes.append({"id": next_id, "label": name, "category": "service"})
        next_id += 1
    # data stores
    for i in range(args.n_data_stores):
        name = f"data_store_{i:02d}"
        nodes.append({"id": next_id, "label": name, "category": "data_store"})
        next_id += 1
    # regions
    for i in range(args.n_regions):
        name = f"region_{i:02d}"
        nodes.append({"id": next_id, "label": name, "category": "cloud_region"})
        next_id += 1
    # edge devices
    for i in range(args.n_edge_devices):
        name = f"edge_device_{i:02d}"
        nodes.append({"id": next_id, "label": name, "category": "edge_device"})
        next_id += 1
    # models
    for i in range(args.n_models):
        name = f"model_{i:02d}"
        nodes.append({"id": next_id, "label": name, "category": "model"})
        next_id += 1
    # datasets
    for i in range(args.n_datasets):
        name = f"dataset_{i:02d}"
        nodes.append({"id": next_id, "label": name, "category": "dataset"})
        next_id += 1
    # users
    for i in range(args.n_users):
        name = f"user_{i:03d}"
        nodes.append({"id": next_id, "label": name, "category": "user"})
        next_id += 1
    return nodes


def preferential_attachment_selection(candidates: List[int], existing_edges: Dict[int, int], k: int) -> List[int]:
    """Seleciona k candidatos usando mecanismo de preferencia por grau.

    candidates: lista de IDs candidatos
    existing_edges: dicionário mapeando id -> contagem de conexões (grau)
    Retorna lista de IDs de tamanho k (sem repetir)
    """
    # calcula pesos: grau + 1 (para evitar zero)
    weights = [(existing_edges.get(c, 0) + 1) for c in candidates]
    selected = set()
    while len(selected) < min(k, len(candidates)):
        target = random.choices(candidates, weights=weights, k=1)[0]
        selected.add(target)
    return list(selected)


def create_edges(nodes: List[Dict[str, object]], args: argparse.Namespace) -> List[Dict[str, object]]:
    """Constrói uma lista de arestas com tipos variados baseados em categorias dos nós."""
    edges = []
    # mapeia id para categoria
    category_map = {node["id"]: node["category"] for node in nodes}
    # separa listas por categoria
    services = [node["id"] for node in nodes if node["category"] == "service"]
    data_stores = [node["id"] for node in nodes if node["category"] == "data_store"]
    regions = [node["id"] for node in nodes if node["category"] == "cloud_region"]
    edge_devices = [node["id"] for node in nodes if node["category"] == "edge_device"]
    models = [node["id"] for node in nodes if node["category"] == "model"]
    datasets = [node["id"] for node in nodes if node["category"] == "dataset"]
    users = [node["id"] for node in nodes if node["category"] == "user"]
    # grau acumulado para preferential attachment
    deg = {}
    # 1. arestas de dependência: serviços dependem de data stores e datasets
    for service in services:
        # serviços dependem de data stores (1 a 3 ou menos) e datasets (0 a 2 ou menos)
        if data_stores:
            max_ds = min(3, len(data_stores))
            k_ds = random.randint(1, max_ds)
            selected_ds = random.sample(data_stores, k_ds)
        else:
            selected_ds = []
        if datasets:
            max_data = min(2, len(datasets))
            k_data = random.randint(0, max_data)
            selected_data = random.sample(datasets, k_data) if k_data > 0 else []
        else:
            selected_data = []
        for target in selected_ds + selected_data:
            edges.append({"source": service, "target": target, "type": "depends_on"})
            deg[target] = deg.get(target, 0) + 1
    # 2. arestas calls: serviços chamam outros serviços, com distribuição power-law
    for service in services:
        # cada serviço chama entre 1 e 3 outros serviços (exceto a si mesmo)
        potential = [s for s in services if s != service]
        if not potential:
            continue
        k = random.randint(1, min(3, len(potential)))
        targets = preferential_attachment_selection(potential, deg, k)
        for target in targets:
            edges.append({"source": service, "target": target, "type": "calls"})
            deg[target] = deg.get(target, 0) + 1
    # 3. replicates: data stores replicam para regiões; datasets replicam para edge devices
    for ds in data_stores:
        k = random.randint(1, min(2, len(regions))) if regions else 0
        selected = random.sample(regions, k) if k > 0 else []
        for region in selected:
            edges.append({"source": ds, "target": region, "type": "replicates"})
    for dataset in datasets:
        k = random.randint(1, min(3, len(edge_devices))) if edge_devices else 0
        selected = random.sample(edge_devices, k) if k > 0 else []
        for ed in selected:
            edges.append({"source": dataset, "target": ed, "type": "replicates"})
    # 4. monitoramento: escolhemos um serviço para monitorar outros serviços
    if services:
        monitor = random.choice(services)
        for svc in services:
            if svc != monitor:
                edges.append({"source": monitor, "target": svc, "type": "monitors"})
    # 5. relaciona serviços a modelos (serviços usam modelos)
    for service in services:
        k = random.randint(0, min(2, len(models))) if models else 0
        selected = random.sample(models, k) if k > 0 else []
        for model in selected:
            edges.append({"source": service, "target": model, "type": "depends_on"})
            deg[model] = deg.get(model, 0) + 1
    # 6. modelos treinam em datasets
    for model in models:
        k = random.randint(1, min(2, len(datasets))) if datasets else 0
        selected = random.sample(datasets, k) if k > 0 else []
        for dataset in selected:
            edges.append({"source": model, "target": dataset, "type": "depends_on"})
            deg[dataset] = deg.get(dataset, 0) + 1
    # 7. usuários interagem com serviços
    for user in users:
        k = random.randint(1, min(3, len(services))) if services else 0
        selected = random.sample(services, k) if k > 0 else []
        for svc in selected:
            edges.append({"source": user, "target": svc, "type": "calls"})
    return edges


def main() -> None:
    args = parse_args()
    if args.seed is not None:
        random.seed(args.seed)
    nodes = create_nodes(args)
    edges = create_edges(nodes, args)
    # preparar saídas
    prefix = args.output_prefix
    nodes_csv = f"{prefix}_nodes.csv"
    edges_csv = f"{prefix}_edges.csv"
    json_path = f"{prefix}.json"
    out_dir = os.path.dirname(prefix)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    # grava nodes
    with open(nodes_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "label", "category"])
        for n in nodes:
            writer.writerow([n["id"], n["label"], n["category"]])
    # grava edges
    with open(edges_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["source", "target", "type"])
        for e in edges:
            writer.writerow([e["source"], e["target"], e["type"]])
    # grava JSON
    graph = {"nodes": nodes, "edges": edges}
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)
    print(
        f"Gerados arquivos: {nodes_csv} (nós), {edges_csv} (arestas) e {json_path} (formato JSON)"
    )


if __name__ == "__main__":
    main()