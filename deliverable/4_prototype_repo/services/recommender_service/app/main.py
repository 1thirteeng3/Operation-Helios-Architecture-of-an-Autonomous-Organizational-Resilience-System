from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import logging

# IMPLEMENTAÇÃO FASE 3: Instrumentação Prometheus
from prometheus_fastapi_instrumentator import Instrumentator, Info

from .schemas import HealthResponse, PredictRequest, PredictResponse
from .model import PredictionModel
from .mlflow_utils import configure_mlflow, log_inference

APP_VERSION = os.getenv("APP_VERSION", "0.1.0-k8s")
log = logging.getLogger("uvicorn")

app = FastAPI(
    title="Helius Reco Service",
    version=APP_VERSION,
    description="Serviço de predição resiliente da Helius Systems (Protótipo Fase 4).",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# Modelo global (carregado na inicialização)
prediction_model = PredictionModel()

# --- IMPLEMENTAÇÃO FASE 3: Self-Observability ---

def get_model_fallback_status(info: Info) -> int:
    """Exporta '1' se o modelo estiver em fallback, '0' se saudável."""
    return 1 if prediction_model.fallback_active else 0

# Configura o instrumentador do Prometheus
instrumentator = Instrumentator(
    should_instrument_requests=True,
    should_instrument_responses=True,
    excluded_handlers=["/metrics"], # Não monitorar o próprio Prometheus
    default_latency_buckets=(0.01, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0),
)

# Adiciona a métrica customizada de resiliência (Fase 3)
instrumentator.add(
    Info(
        name="reco_engine_in_fallback_mode",
        description="Indica se o serviço de recomendação está operando em modo fallback (1) ou saudável (0).",
        info_func=get_model_fallback_status
    )
)
instrumentator.instrument(app)
# --------------------------------------------------

@app.on_event("startup")
async def startup_event():
    """
    IMPLEMENTAÇÃO FASE 2: O 'prediction_model.load()' agora é 
    resiliente e NUNCA falha o startup do serviço.
    """
    prediction_model.load()
    log.info(f"[startup] Carregamento do modelo concluído. Versão: {prediction_model.version}")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check resiliente. O serviço reporta 'ok' mesmo se o MLflow
    falhar, mas reporta o status de fallback.
    """
    mlflow_connected = False
    notes = "MLflow (dependência) indisponível. Serviço em modo fallback."
    
    # Teste de conexão (não-bloqueante)
    try:
        configure_mlflow() # Tenta conectar
        mlflow_connected = True
        notes = "Serviço saudável."
    except Exception:
        pass # Falha de conexão é esperada se o MLflow estiver fora (Fase 2)

    # O status do app é 'ok' desde que o fallback esteja funcionando
    return HealthResponse(
        status="ok",
        service="helius-reco-service",
        version=APP_VERSION,
        mlflow_connected=mlflow_connected,
        model_version=prediction_model.version
    )


@app.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest):
    if not request.features:
        raise HTTPException(status_code=400, detail="Lista de features vazia.")

    # A lógica de fallback já está contida no método .predict()
    prediction, model_version = prediction_model.predict(request.features)

    # Log assíncrono (não bloqueia a resposta se o MLflow falhar)
    try:
        log_inference(
            run_name="inference_prototype",
            features=request.features,
            prediction=prediction,
        )
    except Exception:
        log.warning("Falha no logging de inferência (não-bloqueante).")
        pass

    return PredictResponse(
        prediction=prediction,
        model_version=model_version,
        metadata={"n_features": len(request.features)},
    )