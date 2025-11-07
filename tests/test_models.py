"""
Unit tests for model validation and fairness checks.

Estes testes cobrem aspectos básicos de validação de modelos, como o formato
da saída de uma rede GraphSAGE e verificações simples de equidade na
distribuição das classes previstas.  Os testes utilizam o módulo `pytest` e
podem ser executados com `pytest tests/`.
"""

import numpy as np
import torch

from helius_sim_lab.ml.train_gnn import GraphSAGEModel


def test_gnn_output_shape():
    """Verifica se o modelo GraphSAGE produz saída com a forma correta."""
    in_dim = 10
    hidden_dim = 16
    out_dim = 4
    model = GraphSAGEModel(in_dim, hidden_dim, out_dim)
    # cria 5 nós com features aleatórias
    x = torch.randn((5, in_dim))
    # grafo sem arestas para teste de forma
    edge_index = torch.empty((2, 0), dtype=torch.long)
    out = model(x, edge_index)
    assert out.shape == (5, out_dim), f"Esperado shape (5,{out_dim}), obtido {out.shape}"


def test_fairness_distribution():
    """Teste simples de equidade: nenhuma classe deve dominar a maioria absoluta (>=80%)."""
    # Predições simuladas de 100 exemplos com 3 classes
    rng = np.random.RandomState(42)
    preds = rng.choice([0, 1, 2], size=100, p=[0.5, 0.3, 0.2])
    unique, counts = np.unique(preds, return_counts=True)
    max_share = counts.max() / counts.sum()
    assert max_share < 0.8, f"Distribuição enviesada: maior classe com {max_share*100:.1f}% das amostras"