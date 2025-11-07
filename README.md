# Helius Sim Lab

Este repositório contém um **monorepo** modular para a simulação de resiliência organizacional da Helius Systems.  Ele foi construído para suportar experimentos complexos envolvendo monitoramento, MLOps/LLMOps, modelagem de grafos, observabilidade e automação.  A estrutura de diretórios segue a convenção descrita no roteiro da simulação e pode ser facilmente expandida com novos serviços ou ferramentas.

## Estrutura de Diretórios

- `infra/` – scripts de infraestrutura como código (Terraform, manifests de Kubernetes e Dockerfiles) para provisionar ambientes cloud e edge.
- `data/` – geradores de dados sintéticos, esquemas e amostras para telemetria, logs, grafos e transações.
- `services/` – microserviços implementados em Python (FastAPI) para ingestão, consulta de status e servir modelos de ML.
- `ml/` – notebooks, modelos e artefatos do MLflow para experimentos de MLOps/LLMOps.
- `sim/` – simulações de risco e falhas, utilizando frameworks como NetworkX e SimPy.
- `observability/` – dashboards e configurações de Prometheus, Grafana e Loki para monitoramento distribuído.
- `playbooks/` – runbooks, cenários de incidentes e templates de apresentações para o board.
- `ci/` – definições de workflows do GitHub Actions e suites de testes automatizados.
- `evaluation/` – rubricas de avaliação, scripts de scoring e checklists de aceitação.
- `docs/` – guias do laboratório, instruções de execução e requisitos técnicos.

Cada pasta contém um arquivo `README.md` descritivo que explica o propósito daquele módulo e orientações de uso.

## Dados Sintéticos

A pasta `data/` inclui scripts de geração de dados sintéticos utilizados ao longo das fases da simulação.  Estes scripts produzem conjuntos realistas de telemetria, logs estruturados (e não estruturados), grafos de dependência e eventos transacionais.  O objetivo é permitir a reprodução de cenários de falhas em cascata, drift de modelos e ataques adversariais de forma verossímil.  Execute cada gerador com `--help` para ver os parâmetros disponíveis.
