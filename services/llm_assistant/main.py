"""
FastAPI application acting as a mock LLM assistant.

This microservice exposes an endpoint that accepts a user prompt and returns a
structured response adhering to a predefined schema.  The response schema is
validated using Pydantic (via `llm_schema.ModelDecision`), ensuring the LLM
output meets expectations.  A real implementation could call an external LLM
(e.g. OpenAI) and then run the result through `py-llm-shield` for validation
and repair; here we simulate the behaviour for demonstration purposes.
"""

import random
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Ajusta sys.path para permitir importação da pasta raíz do projeto
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))
try:
    # Importa o schema definido em ml/llm_schema.py
    from ml.llm_schema import ModelDecision  # type: ignore
except ImportError:
    # fallback: define um schema básico para evitar falhas
    from pydantic import BaseModel, Field
    class ModelDecision(BaseModel):
        action: str = Field(...)
        confidence: float = Field(...)
        rationale: str = Field(...)

# Request model for incoming prompts
class PromptRequest(BaseModel):
    prompt: str

# Instantiate FastAPI app
app = FastAPI(title="LLM Assistant", version="0.1.0")


def mock_llm_response(prompt: str) -> dict:
    """Simula um modelo de linguagem gerando uma decisão a partir do prompt.

    Em um sistema real, você integraria com um provedor de LLM (OpenAI,
    HuggingFace, etc.).  A resposta bruta retornada deveria então ser
    passada por uma validação com ``py-llm-shield`` ou validação Pydantic
    para garantir conformidade com o contrato de resposta.
    """
    # lógica simples: escolhe ação com base em palavras-chave
    prompt_lower = prompt.lower()
    if "recommend" in prompt_lower:
        action = "recommend_item"
    elif "status" in prompt_lower:
        action = "report_status"
    elif "help" in prompt_lower:
        action = "provide_help"
    else:
        action = "acknowledge"
    confidence = round(random.uniform(0.6, 0.99), 2)
    rationale = "Resposta gerada pelo mock LLM baseado em palavras-chave."
    return {"action": action, "confidence": confidence, "rationale": rationale}


def validate_with_shield(raw: dict) -> ModelDecision:
    """Valida e corrige a resposta de um LLM usando a schema ``ModelDecision``.

    Esta função simula a integração com py-llm-shield: tenta criar uma
    instância de ``ModelDecision`` a partir do dicionário.  Se algum campo
    obrigatório estiver ausente ou com tipo incorreto, ele aplicará
    reparos simples (por exemplo, definir valores padrão) antes de
    levantar uma exceção final.

    Args:
        raw: dicionário retornado pelo LLM.

    Returns:
        Instância de ``ModelDecision`` válida.

    Raises:
        ValueError: se a resposta não puder ser reparada para cumprir o schema.
    """
    try:
        return ModelDecision(**raw)
    except Exception:
        # aplica reparos simples: garante todos os campos e tipos básicos
        repaired = {
            "action": str(raw.get("action", "unknown")),
            "confidence": float(raw.get("confidence", 0.0)),
            "rationale": str(raw.get("rationale", "")),
        }
        # tenta validar novamente
        try:
            return ModelDecision(**repaired)
        except Exception as exc:
            raise ValueError(f"Falha ao validar saída do LLM: {exc}") from exc


@app.post("/assist", response_model=ModelDecision)
async def assist(req: PromptRequest):
    """Receive a user prompt and return a validated decision.

    The mock LLM generates a response dictionary, which is validated
    against the `ModelDecision` schema.  If validation fails, a 400 error
    is returned.
    """
    raw_resp = mock_llm_response(req.prompt)
    # Integrar py-llm-shield: validação e reparação da resposta
    try:
        decision = validate_with_shield(raw_resp)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return decision


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)