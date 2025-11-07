# Infraestrutura

Esta pasta contém artefatos de *Infraestrutura como Código* (IaC) para
provisionar o ambiente necessário à execução do Helius Sim Lab.  Você
encontrará definições de **Terraform** para nuvens públicas (AWS),
exemplos de configuração de **Kubernetes local** (k3d/kind/minikube) e
orientações para ambientes de desenvolvimento em Docker e Python.

## Estrutura

- **terraform/aws/** – Stack de Terraform que cria uma VPC, um cluster
  EKS, grupos de nós (edge/core/GPU), buckets S3, um repositório ECR,
  uma instância RDS/Postgres, papéis IAM, chaves KMS e integrações
  básicas com CloudWatch.  Consulte o arquivo ``README.md`` dessa
  pasta para detalhes de uso.
- **local/** – Exemplos para provisionar clusters Kubernetes
  localmente.  Inclui:
  - ``k3d/cluster.yaml``: configuração para criar um cluster k3d com
    três agentes rotulados (edge, core, gpu).
  - ``README.md``: instruções para usar k3d, kind ou minikube, bem
    como diretrizes para configurar ambientes Python (Poetry/virtualenv) e
    Docker Compose para orquestrar serviços como MLflow, Prometheus e
    Grafana.
- **mlflow/** – Documentação sobre como iniciar um servidor MLflow.

## Próximos passos

- Acrescentar manifestos de serviços do Kubernetes (Deployments,
  Services, Ingresses, ConfigMaps) para a observabilidade, pipelines de
  ML e APIs.
- Integrar ferramentas de **secrets management** (HashiCorp Vault ou
  AWS Secrets Manager) e **sealed-secrets** para armazenar senhas e
  chaves de forma segura.
- Configurar runners de CI/CD (por exemplo, GitHub Actions) que
  constroem imagens, publicam no ECR e implantam nos clusters
  provisionados.
