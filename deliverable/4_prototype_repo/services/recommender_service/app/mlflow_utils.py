import os
from typing import Any, Optional
import mlflow
from mlflow import MlflowClient

# Variáveis de ambiente são injetadas pelo ConfigMap do Kubernetes
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow-failure:5000")
MLFLOW_MODEL_URI = os.getenv("MLFLOW_MODEL_URI", "models:/helius-reco-model/Production")


def configure_mlflow() -> MlflowClient:
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    client = MlflowClient()
    # Testa a conexão (falha rápido se o RDS/URI estiver inacessível)
    client.search_experiments()
    return client


def load_model_from_mlflow() -> Any:
    """
    Carrega o modelo registrado no MLflow.
    """
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    model = mlflow.pyfunc.load_model(MLFLOW_MODEL_URI)
    return model


def log_inference(run_name: str, features, prediction: float) -> None:
    """
    Log simples de inferência no MLflow (assíncrono/não-bloqueante).
    """
    # (Em produção, isso seria delegado a um processo/fila separada)
    try:
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        with mlflow.start_run(run_name=run_name, nested=True):
            mlflow.log_param("n_features", len(features))
            mlflow.log_metric("prediction", float(prediction))
    except Exception as e:
        # NUNCA deve falhar a requisição principal se o logging falhar
        print(f"ALERTA: Falha ao logar inferência no MLflow: {e}")