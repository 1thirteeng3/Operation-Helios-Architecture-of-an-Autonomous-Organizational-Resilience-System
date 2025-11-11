"""
Serviço LLM Router (Gateway Resiliente)

Implementa o Blueprint - Fase 2:
1. Roteamento com Failover (Primário -> Secundário).
2. Fail-Open (Confiança 0.0) se todos os backends falharem.
"""
import os
import httpx
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

# Instrumentação Prometheus (Fase 3)
from prometheus_fastapi_instrumentator import Instrumentator

# --- Esquemas (Schemas) ---

class ModelDecision(BaseModel):
    action: str = Field(...)
    confidence: float = Field(...)
    rationale: str = Field(...)

class PromptRequest(BaseModel):
    prompt: str

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    primary_backend_ok: bool
    secondary_backend_ok: bool

# --- Configuração de Resiliência (Fase 2) ---

APP_VERSION = os.getenv("APP_VERSION", "0.1.0-router")

# URLs injetadas pelo ConfigMap (k8s/04-llm-router-ha.yaml)
LLM_ASSISTANT_PRIMARY_URL = os.getenv("LLM_ASSISTANT_PRIMARY_URL")
LLM_ASSISTANT_SECONDARY_URL = os.getenv("LLM_ASSISTANT_SECONDARY_URL") # Pode ser None

log = logging.getLogger("uvicorn")
app = FastAPI(
    title="Helius LLM Router (Gateway)",
    version=APP_VERSION,
    description="Gateway resiliente com lógica de failover (Fase 2).",
)

# Configura Métricas Prometheus (Fase 3)
Instrumentator().instrument(app).expose(app)


async def check_backend_health(url: Optional[str]) -> bool:
    """Verifica a saúde de um backend."""
    if not url:
        return False
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{url}/health", timeout=2.0)
            return resp.status_code == 200
    except Exception:
        return False

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Verifica a saúde do router E dos backends que ele pode ver."""
    primary_ok = await check_backend_health(LLM_ASSISTANT_PRIMARY_URL)
    secondary_ok = await check_backend_health(LLM_ASSISTANT_SECONDARY_URL)
    
    return HealthResponse(
        status="ok",
        service="llm-router",
        version=APP_VERSION,
        primary_backend_ok=primary_ok,
        secondary_backend_ok=secondary_ok
    )


@app.post("/route", response_model=ModelDecision)
async def route_request(req: PromptRequest):
    """
    IMPLEMENTAÇÃO FASE 2: Lógica de Failover e Fail-Open.
    Tenta o Primário. Se falhar, tenta o Secundário. Se falhar, retorna Confiança 0.0.
    """
    
    backends_to_try: List[Optional[str]] = [
        LLM_ASSISTANT_PRIMARY_URL, 
        LLM_ASSISTANT_SECONDARY_URL
    ]
    
    last_exception: Optional[Exception] = None
    
    async with httpx.AsyncClient() as client:
        for i, url in enumerate(backends_to_try):
            if not url: # Pula se a URL (ex: Secundária) não estiver configurada
                continue
                
            log.info(f"Tentando backend {'Primário' if i==0 else 'Secundário'}: {url}")
            try:
                resp = await client.post(
                    f"{url}/assist", 
                    json={"prompt": req.prompt}, 
                    timeout=5.0
                )
                resp.raise_for_status() # Levanta erro em 4xx/5xx
                
                # Sucesso! Validar e retornar.
                data = resp.json()
                # (Aqui entraria o py-llm-shield para validação de output)
                decision = ModelDecision(**data) 
                log.info(f"Sucesso no backend {'Primário' if i==0 else 'Secundário'}.")
                return decision
            
            except (httpx.RequestError, httpx.HTTPStatusError) as exc:
                log.warning(f"Falha no backend {'Primário' if i==0 else 'Secundário'} ({url}): {exc}")
                last_exception = exc
                continue # Tenta o próximo (Failover)

    # --- IMPLEMENTAÇÃO FASE 2: Fail-Open (Confiança 0.0) ---
    # Se todos os backends falharam (ex: Falha Regional Total)
    
    log.error(f"Todos os backends ({backends_to_try}) falharam. Ativando modo Fail-Open.")
    
    # Em vez de retornar 502 (Bad Gateway), retornamos uma resposta
    # válida e segura que o Control Plane pode rastrear.
    return ModelDecision(
        action="safemode_fallback",
        confidence=0.0,
        rationale=f"Erro sistêmico: Backends indisponíveis. Último erro: {last_exception}"
    )