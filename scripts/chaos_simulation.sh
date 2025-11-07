#!/bin/bash
#
# helius-sim-lab/scripts/chaos_simulation.sh
# -------------------------------------------
#
# Este script realiza experimentos de engenharia do caos simples em um cluster
# Kubernetes. Ele remove aleatoriamente um pod de um namespace ou injeta
# perturbações definidas. Use‐o para validar a resiliência dos serviços
# implantados no laboratório. Para experimentos mais avançados, considere
# integrar o Chaos Mesh (https://chaos-mesh.org/) ou o LitmusChaos.

set -euo pipefail

NAMESPACE=${1:-"helius-sim"}

echo "[Chaos] Selecionando um pod aleatório no namespace $NAMESPACE para matar..."
POD=$(kubectl get pods -n "$NAMESPACE" --no-headers -o custom-columns=":metadata.name" | shuf -n 1 || true)
if [[ -z "$POD" ]]; then
  echo "[Chaos] Nenhum pod encontrado no namespace $NAMESPACE."
  exit 0
fi

echo "[Chaos] Deletando pod $POD para simular falha..."
kubectl delete pod "$POD" -n "$NAMESPACE" --grace-period=0 --force

echo "[Chaos] Pod $POD removido. Observe o comportamento do cluster e dos serviços."

## Para experimentar com Chaos Mesh:
# 1. Instale Chaos Mesh no cluster: https://chaos-mesh.org/docs/installation
# 2. Crie recursos ChaosExperiment YAML para NetworkChaos, PodChaos, etc.
# 3. Aplique com `kubectl apply -f experiment.yaml` e monitore os efeitos.