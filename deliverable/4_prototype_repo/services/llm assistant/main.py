"""
Serviço Backend (LLM Assistant)

Este é o microsserviço que simula a resposta de um LLM.
O LLM Router (gateway) chamará este serviço.
"""
import os
import random
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

# --- Esquemas (Schemas) ---
# (Definidos localmente para simplicidade do microsserviço)

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

# --- Configuração do App ---

APP_VERSION = os.getenv("APP_VERSION", "0.1.0-assistant")
log = logging.getLogger("uvicorn")

app = FastAPI(
    title="Helius LLM Assistant (Backend)",
    version=APP_VERSION,
    description="Backend que simula o processamento de LLM.",
)

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check básico para o Kubernetes (Liveness/Readiness)."""
    return HealthResponse(
        status="ok",
        service="llm-assistant",
        version=APP_VERSION
    )

def mock_llm_response(prompt: str) -> dict:
    """Simula a resposta de um LLM."""
    log.info(f"Processando prompt (mock): {prompt[:20]}...")
    
    # Simula falha intermitente (ex: 10% de chance de falha)
    if random.random() < 0.1:
         raise HTTPException(status_code=500, detail="Simulated Internal LLM Error")

    prompt_lower = prompt.lower()
    if "recommend" in prompt_lower:
        action = "recommend_item"
    elif "status" in prompt_lower:
        action = "report_status"
    else:
        action = "acknowledge"
    
    confidence = round(random.uniform(0.7, 0.99), 2)
    rationale = f"Mock response based on keywords in prompt for action: {action}"
    
    return {"action": action, "confidence": confidence, "rationale": rationale}

@app.post("/assist", response_model=ModelDecision)
async def assist(req: PromptRequest):
    """Ponto de entrada principal para o LLM."""
    try:
        raw_resp = mock_llm_response(req.prompt)
        # (Aqui entraria a validação py-llm-shield)
        decision = ModelDecision(**raw_resp)
        return decision
    except HTTPException as http_exc:
        # Repassa o erro simulado
        raise http_exc
    except Exception as exc:
        log.error(f"Erro inesperado no assist: {exc}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {exc}")