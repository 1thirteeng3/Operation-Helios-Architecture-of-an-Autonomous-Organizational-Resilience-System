"""
FastAPI service for serving a GraphSAGE recommender model.

This service loads a trained model artifact from MLflow and exposes an API to
generate predictions for input nodes or feature vectors.  It demonstrates how
to integrate model artifacts with a microservice and provides a starting point
for implementing proper recommendation logic (e.g., top‑k item ranking, user
embedding lookup, etc.).  The current implementation performs node
classification: given a node identifier, it returns the predicted category.
"""

import os
import sys
from pathlib import Path
from typing import List

import mlflow
import numpy as np
import torch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Ajusta sys.path para localizar pacotes internos
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))


class PredictRequest(BaseModel):
    node_ids: List[int]


class PredictResponse(BaseModel):
    predictions: List[str]


app = FastAPI(title="Recommender Service", version="0.1.0")

# Configurações: path do modelo e dicionário de categorias
MLFLOW_MODEL_URI = os.environ.get("MLFLOW_MODEL_URI", "mlruns/0/model")
CATEGORY_MAPPING_PATH = os.environ.get("CATEGORY_MAPPING_PATH", "category_mapping.json")


def load_model():
    """Carrega modelo a partir do MLflow.

    Usa mlflow.pytorch.load_model para carregar o módulo TorchScript salvando
    durante o treinamento.
    """
    try:
        model = mlflow.pytorch.load_model(MLFLOW_MODEL_URI)
        return model
    except Exception as exc:
        raise RuntimeError(f"Falha ao carregar modelo de {MLFLOW_MODEL_URI}: {exc}")


def load_category_mapping() -> List[str]:
    """Carrega arquivo JSON contendo a lista de categorias por índice."""
    import json
    if not os.path.exists(CATEGORY_MAPPING_PATH):
        raise FileNotFoundError(f"Mapping file {CATEGORY_MAPPING_PATH} não encontrado")
    with open(CATEGORY_MAPPING_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# Carrega modelo e categorias na inicialização
MODEL = None
CATEGORIES: List[str] = []


@app.on_event("startup")
def startup_event():
    global MODEL, CATEGORIES
    MODEL = load_model()
    CATEGORIES = load_category_mapping()


@app.post("/predict", response_model=PredictResponse)
async def predict(req: PredictRequest):
    """Recebe uma lista de IDs de nós e retorna as categorias previstas."""
    if MODEL is None or not CATEGORIES:
        raise HTTPException(status_code=500, detail="Modelo não carregado corretamente")
    node_ids = req.node_ids
    # Constrói matriz de features sintética: apenas one-hot dos IDs para exemplo
    # Em um serviço real, aqui você buscaria embeddings ou atributos do grafo.
    num_nodes = len(node_ids)
    feat = np.eye(num_nodes, dtype=np.float32)
    x = torch.tensor(feat)
    # Cria um grafo vazio sem arestas para inferência isolada
    edge_index = torch.empty((2, 0), dtype=torch.long)
    with torch.no_grad():
        logits = MODEL(x, edge_index)
        preds = logits.argmax(dim=1).tolist()
    labels = [CATEGORIES[p] for p in preds]
    return PredictResponse(predictions=labels)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)