#!/bin/bash
#
# helius-sim-lab/scripts/teardown.sh
# -----------------------------------
#
# Este script remove os recursos criados pelo seed_environment.sh para evitar
# custos inesperados. Ele exclui o namespace Kubernetes e remove buckets S3
# gerados. Ajuste conforme necessário para o seu ambiente de nuvem.

set -euo pipefail

NAMESPACE="helius-sim"

echo "[Teardown] Excluindo namespace $NAMESPACE..."
kubectl delete namespace "$NAMESPACE" --ignore-not-found

# Remove buckets S3 criados durante o seed (procura pelo prefixo)
if command -v aws >/dev/null 2>&1; then
  for bucket in $(aws s3 ls | awk '{print $3}' | grep '^helius-sim-sample'); do
    echo "[Teardown] Removendo bucket $bucket..."
    aws s3 rb "s3://$bucket" --force || true
  done
else
  echo "[Teardown] AWS CLI não encontrado; pule a remoção de buckets S3."
fi

echo "[Teardown] Recursos removidos."