"""
train_gnn.py
------------

Script de treinamento de um modelo baseline GraphSAGE para recomendação ou
classificação de nós.  Este código utiliza PyTorch e PyTorch Geometric para
definir um grafo, construir um modelo de Graph Neural Network (GNN) e realizar
treino/avaliação.  Os artefatos (modelo treinado, métricas, parâmetros) são
registrados no MLflow para facilitar reprodutibilidade e versionamento.

Para executar este script, é necessário instalar as dependências:

```bash
pip install torch torch-geometric mlflow
```

Uso:
    python train_gnn.py --graph-path data/graph.json --run-name experiment_001 \
        --mlflow-uri http://localhost:5000

O script espera um arquivo JSON com nós e arestas no formato gerado por
`generate_graph.py`.  Caso você ainda não tenha features para os nós, o
script irá gerar vetores de atributos aleatórios e codificações one-hot das
categorias.  O objetivo supervisionado de exemplo é classificar o tipo de nó
(serviço, data_store, etc.), mas você pode adaptar para tarefas de
recomendação, predição de links, etc.
"""

import argparse
import json
import os
from pathlib import Path
from typing import Dict, List

import mlflow
import numpy as np
import torch
import torch.nn.functional as F

try:
    from torch_geometric.data import Data
    from torch_geometric.nn import SAGEConv
except ImportError:
    raise ImportError(
        "PyTorch Geometric não está instalado. Execute `pip install torch-geometric` "
        "e consulte a documentação https://pytorch-geometric.readthedocs.io para mais detalhes."
    )


def load_graph(graph_path: str) -> Dict[str, List[Dict[str, object]]]:
    with open(graph_path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_dataset(graph: Dict[str, List[Dict[str, object]]]):
    """Constrói tensores de features e labels a partir do grafo.

    Para cada nó, gera features combinando um vetor aleatório e uma codificação
    one‑hot da categoria.  O label é o índice da categoria.
    """
    nodes = graph["nodes"]
    edges = graph["edges"]
    # mapeia categoria para índice
    categories = sorted(set(n["category"] for n in nodes))
    cat_to_idx = {cat: i for i, cat in enumerate(categories)}
    num_nodes = len(nodes)
    num_cats = len(categories)
    # gera features aleatórias (dim=16)
    rand_dim = 16
    x_rand = np.random.randn(num_nodes, rand_dim).astype(np.float32)
    # gera one-hot
    x_onehot = np.zeros((num_nodes, num_cats), dtype=np.float32)
    for i, n in enumerate(nodes):
        cat_idx = cat_to_idx[n["category"]]
        x_onehot[i, cat_idx] = 1.0
    # concatena
    x = np.concatenate([x_rand, x_onehot], axis=1)
    # labels
    y = np.array([cat_to_idx[n["category"]] for n in nodes], dtype=np.int64)
    # edge_index
    # edges são direcionados; vamos converter para array 2xE
    edge_list = []
    for e in edges:
        source = e["source"] - 1  # ids começam em 1
        target = e["target"] - 1
        edge_list.append((source, target))
        # adiciona também a aresta reversa para tornar não direcionado
        edge_list.append((target, source))
    edge_index = torch.tensor(edge_list, dtype=torch.long).t().contiguous()
    data = Data(x=torch.tensor(x, dtype=torch.float32), edge_index=edge_index, y=torch.tensor(y))
    return data, categories


class GraphSAGEModel(torch.nn.Module):
    def __init__(self, in_channels: int, hidden_channels: int, out_channels: int):
        super().__init__()
        self.conv1 = SAGEConv(in_channels, hidden_channels)
        self.conv2 = SAGEConv(hidden_channels, out_channels)

    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index)
        x = F.relu(x)
        x = self.conv2(x, edge_index)
        return x


def train_model(
    data: Data,
    num_classes: int,
    run_name: str,
    mlflow_uri: str,
    dataset_version: str = "unknown",
    random_seed: int = 42,
) -> GraphSAGEModel:
    """Treina o modelo GraphSAGE e registra parâmetros/artefatos no MLflow.

    Args:
        data: objeto ``Data`` do PyTorch Geometric com features, arestas e labels.
        num_classes: número de classes na tarefa de classificação.
        run_name: nome da execução no MLflow.
        mlflow_uri: URI do servidor de tracking do MLflow.
        dataset_version: string que identifica a versão do conjunto de dados utilizado.
        random_seed: semente para aleatoriedade, garantindo reprodutibilidade.

    Returns:
        Instância treinada do ``GraphSAGEModel``.
    """
    # define semente para reprodutibilidade
    np.random.seed(random_seed)
    torch.manual_seed(random_seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(random_seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    data = data.to(device)
    model = GraphSAGEModel(in_channels=data.x.size(1), hidden_channels=32, out_channels=num_classes).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    # divisão simples: usa 80% para treino, 20% para teste
    num_nodes = data.num_nodes
    idx = np.arange(num_nodes)
    np.random.shuffle(idx)
    split = int(0.8 * num_nodes)
    train_idx = torch.tensor(idx[:split], dtype=torch.long, device=device)
    test_idx = torch.tensor(idx[split:], dtype=torch.long, device=device)
    with mlflow.start_run(run_name=run_name):
        # registra parâmetros
        mlflow.log_param("num_nodes", int(num_nodes))
        mlflow.log_param("num_classes", int(num_classes))
        mlflow.log_param("dataset_version", dataset_version)
        mlflow.log_param("random_seed", random_seed)
        mlflow.log_param("framework", "pytorch_geometric")
        for epoch in range(1, 51):
            model.train()
            optimizer.zero_grad()
            out = model(data.x, data.edge_index)
            loss = F.cross_entropy(out[train_idx], data.y[train_idx])
            loss.backward()
            optimizer.step()
            # avalia
            model.eval()
            with torch.no_grad():
                logits = model(data.x, data.edge_index)
                pred = logits.argmax(dim=1)
                train_acc = (pred[train_idx] == data.y[train_idx]).float().mean().item()
                test_acc = (pred[test_idx] == data.y[test_idx]).float().mean().item()
            # loga métricas
            mlflow.log_metric("train_loss", loss.item(), step=epoch)
            mlflow.log_metric("train_accuracy", train_acc, step=epoch)
            mlflow.log_metric("test_accuracy", test_acc, step=epoch)
            print(
                f"Epoch {epoch:02d} loss={loss.item():.4f} train_acc={train_acc:.3f} test_acc={test_acc:.3f}"
            )
        # salva modelo e registra artefato
        mlflow.pytorch.log_model(model, artifact_path="model")
    return model


def main() -> None:
    parser = argparse.ArgumentParser(description="Treina um GNN GraphSAGE e registra no MLflow")
    parser.add_argument("--graph-path", type=str, required=True, help="Caminho para o arquivo JSON do grafo gerado")
    parser.add_argument("--run-name", type=str, default="gnn_experiment", help="Nome da execução do MLflow")
    parser.add_argument(
        "--mlflow-uri",
        type=str,
        default="http://127.0.0.1:5000",
        help="URI do servidor de tracking do MLflow (ex: http://localhost:5000)",
    )
    parser.add_argument(
        "--dataset-version",
        type=str,
        default="v1",
        help="Identificador de versão do conjunto de dados utilizado",
    )
    parser.add_argument(
        "--random-seed",
        type=int,
        default=42,
        help="Semente para geração de números aleatórios",
    )
    args = parser.parse_args()
    # configura MLflow
    mlflow.set_tracking_uri(args.mlflow_uri)
    graph = load_graph(args.graph_path)
    data, categories = build_dataset(graph)
    train_model(
        data,
        num_classes=len(categories),
        run_name=args.run_name,
        mlflow_uri=args.mlflow_uri,
        dataset_version=args.dataset_version,
        random_seed=args.random_seed,
    )


if __name__ == "__main__":
    main()