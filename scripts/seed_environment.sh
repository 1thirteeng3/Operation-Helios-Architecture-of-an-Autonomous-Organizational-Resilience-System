#!/bin/bash
#
# helius-sim-lab/scripts/seed_environment.sh
# ------------------------------------------
#
# Este script inicializa um ambiente básico para o laboratório Helius Sim Lab.
# Ele cria namespaces no Kubernetes, implanta serviços de exemplo e carrega
# dados sintéticos nos serviços de armazenamento. Ajuste conforme necessário
# para seu provedor de nuvem (AWS, GCP, Azure) e ferramentas de orquestração.

set -euo pipefail

# Namespace para os serviços de simulação
NAMESPACE="helius-sim"

echo "[Seed] Criando namespace $NAMESPACE se não existir..."
kubectl get namespace "$NAMESPACE" >/dev/null 2>&1 || kubectl create namespace "$NAMESPACE"

# Implanta serviços FastAPI de exemplo (ajuste o caminho se necessário)
echo "[Seed] Aplicando manifests do serviço LLM Assistant..."
kubectl apply -n "$NAMESPACE" -f services/fastapi/deployment.yaml -f services/fastapi/service.yaml || true

echo "[Seed] Aplicando manifests do serviço de ingestão..."
kubectl apply -n "$NAMESPACE" -f services/ingest/deployment.yaml -f services/ingest/service.yaml || true

# Cria bucket S3 para dados de exemplo (requer AWS CLI configurado)
S3_BUCKET="helius-sim-sample-$RANDOM"
echo "[Seed] Criando bucket S3 $S3_BUCKET para dados sintéticos..."
if command -v aws >/dev/null 2>&1; then
  aws s3 mb "s3://$S3_BUCKET" || true
  # Carrega alguns dados de exemplo (se existirem)
  if [[ -f data/sample_timeseries.csv ]]; then
    echo "[Seed] Carregando dados de telemetria para S3..."
    aws s3 cp data/sample_timeseries.csv "s3://$S3_BUCKET/telemetry/"
  fi
else
  echo "[Seed] AWS CLI não encontrado; pule o upload para S3."
fi

# Inicializa banco de dados (Postgres) com esquema de amostra
echo "[Seed] Preparando banco de dados de metadados..."
if command -v psql >/dev/null 2>&1; then
  DB_URI=${DB_URI:-"postgresql://postgres:password@localhost:5432/helius"}
  cat <<'SQL' | psql "$DB_URI" || true
CREATE TABLE IF NOT EXISTS telemetry (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    node_id VARCHAR(100),
    metric_cpu FLOAT,
    metric_mem FLOAT,
    latency_ms FLOAT,
    request_rate FLOAT
);
SQL
else
  echo "[Seed] psql não encontrado; pule a inicialização do banco de dados."
fi

echo "[Seed] Ambiente inicializado."