# Ambientes de Desenvolvimento Local

Esta pasta contém orientações e arquivos de configuração para
provisionar ambientes de desenvolvimento local, facilitando testes e
prototipação sem depender de um provedor de nuvem.  Os seguintes
conceitos são abordados:

## Kubernetes local

Você pode escolher entre diferentes ferramentas para rodar um cluster
Kubernetes em sua máquina:

- **k3d**: executa o K3s (Kubernetes leve) dentro de contêineres
  Docker.  Recomendado para quem já utiliza Docker Desktop.
- **kind**: cria clusters Kubernetes utilizando contêineres Docker.
- **minikube**: roda Kubernetes em uma VM ou contêiner.  Permite
  experimentação mais próxima de um cluster real.

### Configuração com k3d

Um exemplo de configuração de cluster K3d está em ``k3d/cluster.yaml``.
Para criar o cluster, execute:

```bash
# instale k3d se necessário: https://k3d.io/v5.0.0/#install
k3d cluster create helius-sim -c k3d/cluster.yaml

# Verifique o cluster
kubectl cluster-info
kubectl get nodes
```

O arquivo ``cluster.yaml`` define 3 agentes com labels ``edge``,
``core`` e ``gpu`` (este último opcional).  A configuração mapeia
portas para acesso ao cluster e ativa o traefik como IngressController.

### Configuração com kind

Para criar um cluster com três nós de trabalho usando kind, você pode
utilizar o exemplo abaixo (salve como ``kind/config.yaml``):

```yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
  - role: control-plane
  - role: worker
    labels:
      role: edge
  - role: worker
    labels:
      role: core
  - role: worker
    labels:
      role: gpu
    # Taints para agendar workloads GPU explicitamente
    kubeadmConfigPatches:
      - |
        kind: KubeletConfiguration
        metadata:
          name: config
        evictions:
          imagefs.available: 10%
```

Crie o cluster com:

```bash
kind create cluster --config kind/config.yaml --name helius-sim
```

### Minikube

Para iniciar um cluster com suporte a addons do Kubernetes:

```bash
minikube start --profile helius-sim --cpus=4 --memory=8g
minikube addons enable ingress
```

Você pode usar ``kubectl label node`` para adicionar labels ``edge`` e
``core`` conforme necessário.

## Ambiente Python

Recomenda-se utilizar o **Python 3.11** com isolamento de ambiente via
virtualenv ou [Poetry](https://python-poetry.org/).  Um exemplo de
passos utilizando Poetry:

```bash
# Instale Poetry se ainda não estiver instalado
curl -sSL https://install.python-poetry.org | python3 -

# Crie o ambiente
cd helius-sim-lab
poetry env use 3.11
poetry install

# Ative o ambiente
poetry shell

# Agora você pode executar scripts como generate_timeseries.py
python data/generate_timeseries.py --help
```

Alternativamente, você pode utilizar um simples virtualenv:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Um arquivo ``requirements.txt`` será criado à medida que as dependências
forem definidas (por exemplo, ``fastapi``, ``mlflow``, ``torch``, etc.).

## Docker Compose

Para quem utiliza Docker Desktop, é possível orquestrar os serviços
locais (MLflow, Prometheus, Grafana, etc.) com o **Docker Compose**.
Crie um arquivo ``docker-compose.yml`` na raiz do projeto com os
containers desejados.  Um exemplo básico pode incluir:

```yaml
version: "3.9"
services:
  mlflow:
    image: mlflow/mlflow
    command: mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root /mlflow
    ports:
      - "5000:5000"
    volumes:
      - ./mlflow:/mlflow

  prometheus:
    image: prom/prometheus
    volumes:
      - ./observability/prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=helius
    volumes:
      - ./observability/grafana:/var/lib/grafana
```

Os serviços FastAPI podem ser containerizados com Dockerfiles
individuais e publicados no repositório ECR configurado via Terraform.