import logging
from typing import List, Tuple
from .mlflow_utils import load_model_from_mlflow
import numpy as np

log = logging.getLogger("uvicorn")

class PredictionModel:
    def __init__(self):
        self._model: Any = None
        self._model_version: str = "unloaded"
        self.is_fallback: bool = True # Começa como fallback até o carregamento

    def load(self) -> None:
        """
        IMPLEMENTAÇÃO FASE 2: Padrão de Cache/Fallback.
        Tenta carregar do MLflow; se falhar, usa fallback.
        """
        try:
            # 1. Tentar MLflow (Fonte Primária)
            self._model = load_model_from_mlflow()
            # (Opcional: recuperar metadados de versão do modelo)
            self._model_version = "mlflow-model-v1" # Simulado
            self.is_fallback = False
            log.info(f"Sucesso: Modelo carregado do MLflow (URI: {os.getenv('MLFLOW_MODEL_URI')})")

        except Exception as e:
            # 2. Fallback (Modo Degradado)
            # O MLflow está inacessível (ex: falha de rede, SPOF do Dia 0)
            log.error(f"FALHA AO CARREGAR MODELO DO MLFLOW: {e}. Ativando modo fallback.")
            self._model = None # Garante que estamos usando o dummy
            self._model_version = "fallback-dummy-v0.1"
            self.is_fallback = True

    @property
    def version(self) -> str:
        return self._model_version

    @property
    def fallback_active(self) -> bool:
        return self.is_fallback

    def predict(self, features: List[float]) -> Tuple[float, str]:
        x = np.array(features).reshape(1, -1)

        # Se o modelo do MLflow (primário) estiver carregado, use-o.
        if self._model is not None and not self.is_fallback:
            try:
                y = self._model.predict(x)
                return float(y[0]), self._model_version
            except Exception as e:
                # O modelo do MLflow falhou na inferência (ex: input corrompido)
                log.warning(f"Erro na inferência do modelo MLflow: {e}. Usando fallback.")
                return float(np.mean(x)), "fallback-on-inference-error"
        else:
            # Se self._model é None, estamos no modo fallback (MLflow falhou no startup)
            log.warning("Serviço em modo fallback (MLflow indisponível ou falha no carregamento).")
            return float(np.mean(x)), self._model_version