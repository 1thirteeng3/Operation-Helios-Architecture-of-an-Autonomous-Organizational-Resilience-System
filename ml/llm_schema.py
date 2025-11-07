"""
llm_schema.py
-------------

Define Pydantic data models used for validating LLM outputs.  These schemas
describe the expected shape of responses returned by our LLM assistant or other
model-serving endpoints.  Using Pydantic ensures that the responses conform
to the contract defined by the API and facilitates automatic type checking
and validation when integrated with py-llm-shield.

Example:

```python
from llm_schema import ModelDecision

# validate a dictionary
payload = {"action": "recommend_item", "confidence": 0.92, "rationale": "High similarity"}
decision = ModelDecision(**payload)
print(decision)
```
"""

from pydantic import BaseModel, Field


class ModelDecision(BaseModel):
    """Representa uma decisão tomada por um modelo ou assistente.

    Attributes:
        action: A ação recomendada ou decisão realizada.
        confidence: Probabilidade/confiança associada à decisão (0–1).
        rationale: Texto explicando a justificativa para a decisão.
    """

    action: str = Field(..., description="Ação recomendada ou decisão tomada")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confiança associada à decisão (0–1)")
    rationale: str = Field(..., description="Justificativa ou explicação da decisão")

    class Config:
        schema_extra = {
            "example": {
                "action": "recommend_item",
                "confidence": 0.87,
                "rationale": "Usuário demonstrou interesse em itens similares."
            }
        }