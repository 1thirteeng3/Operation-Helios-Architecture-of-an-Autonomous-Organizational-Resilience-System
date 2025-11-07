##
# Dockerfile para o serviço Recommender Service
#
# Semelhante ao LLM Assistant, este serviço utiliza FastAPI para expor
# um modelo de recomendação treinado via MLflow.  As dependências são
# instaladas a partir de requirements.txt.

FROM python:3.11-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instala dependências
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copia código
COPY . .

EXPOSE 8001

# Executa o serviço FastAPI
CMD ["uvicorn", "services.recommender_service.main:app", "--host", "0.0.0.0", "--port", "8001"]

# Healthcheck que verifica se a API retorna código 200
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s \
  CMD curl -f http://localhost:8001/predict -H 'Content-Type: application/json' -d '{"node_ids":[1]}' || exit 1