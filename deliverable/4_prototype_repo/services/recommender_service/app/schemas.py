from pydantic import BaseModel, Field
from typing import List, Optional


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    mlflow_connected: bool
    model_version: str # MODIFICADO: Reporta o modo do modelo


class PredictRequest(BaseModel):
    features: List[float] = Field(
        ...,
        description="Lista de features numéricos para o modelo (ex.: 10 valores)."
    )


class PredictResponse(BaseModel):
    prediction: float
    model_version: str
    metadata: dict