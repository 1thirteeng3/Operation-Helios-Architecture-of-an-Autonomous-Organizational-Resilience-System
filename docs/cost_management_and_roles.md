# Gestão de Custos, Sandboxing Seguro e Papéis no Laboratório

Este documento fornece orientações sobre como gerenciar custos e isolar
ambientes de teste de forma segura no Helius Sim Lab. Inclui também
uma descrição dos papéis necessários para conduzir a simulação, com
responsabilidades claras para cada integrante.

## Gestão de Custos e Sandboxing

Para evitar surpresas financeiras e garantir que a experimentação ocorra
em ambientes controlados, recomenda‑se seguir estas práticas:

- **Use clusters pequenos e efêmeros:** Crie clusters Kubernetes com o mínimo de nós necessário e com tamanho de máquina compatível com a carga. Prefira instâncias spot ou preemptible, que reduzem significativamente o custo, assumindo que interrupções podem ser toleradas durante simulações.
- **Infraestrutura de curta duração:** Automatize a criação e destruição de ambientes (via Terraform e scripts) e utilize a infraestrutura apenas durante o tempo de teste. Execute o script `scripts/teardown.sh` após cada sessão para liberar recursos.
- **Tagueamento de recursos:** Aplique tags como `project=helius-sim-lab` em todos os recursos (buckets, instâncias, clusters, discos) para facilitar o rastreamento e a aplicação de políticas de budget.
- **Alertas de orçamento:** Configure alertas de orçamento na sua conta de nuvem (AWS Budgets, GCP Budget Alerts) com limiares semanais ou mensais. Notifique o Arquiteto Chefe e a equipe de SRE quando 50 %, 80 % e 100 % do budget forem atingidos.
- **Sandbox local:** Sempre que possível, execute simulações localmente usando ferramentas como **k3d** ou **Kind** para o cluster Kubernetes, **MinIO** como alternativa ao S3 e **Postgres** ou **SQLite** em contêineres. O script `scripts/seed_environment.sh` pode ser adaptado para usar MinIO (`minio server`) e um banco local (`docker run postgres`). Isso evita custos de nuvem durante a fase de desenvolvimento.

## Papéis e Responsabilidades

### Arquiteto Chefe (você)

- Liderar o design da arquitetura e tomar decisões estratégicas.
- Revisar a integração entre componentes (ML, infra, observabilidade) e garantir alinhamento com objetivos de resiliência.
- Definir prioridades de mitigação e roadmap evolutivo.

### SRE / DevOps

- Prover e manter a infraestrutura (Terraform, Kubernetes, CI/CD).
- Configurar monitoramento e alertas (Prometheus, Grafana) e garantir visibilidade dos serviços.
- Executar automações de seed/teardown e otimizar uso de recursos (spot instances, escalonamento).

### Engenheiro(a) de ML

- Treinar modelos (GraphSAGE, LLMs), gerenciar experimentos via MLflow e assegurar registro adequado.
- Desenvolver e implantar pipelines de inferência (FastAPI) e supervisionar métricas de qualidade e drift.
- Participar das simulações de risco, analisando impacto nos modelos e propondo ajustes.

### Engenheiro(a) de Dados

- Construir e manter pipelines de ETL e ingestão de dados sintéticos. Garantir que dados usados nas simulações respeitem privacidade e conformidade.
- Ajudar na geração de gráficos e topologias (NetworkX, Neo4j) e na criação de dados de logs.
- Trabalhar com SRE para integrar pipelines à infraestrutura de armazenamento (S3, MinIO, RDS).

### Engenheiro(a) de Segurança

- Realizar threat modeling, identificar vetores de ataque (prompt injection, poisoning) e sugerir controles.
- Executar varreduras em contêineres e dependências (Trivy, Snyk) e gerenciar secrets (Vault, Secrets Manager).
- Definir políticas de IAM e RBAC de acordo com o princípio do menor privilégio e revisar logs de auditoria.

### Product / Stakeholder

- Definir SLAs, KPIs e critérios de aceitação para cada fase da simulação.
- Priorizar requisitos de negócio e comunicar restrições de custo e risco.
- Participar das apresentações executivas, aprovando ou ajustando recomendações.

### Avaliador(a) / Revisor(a)

- Aplicar a rubrica de avaliação (`evaluation/rubric.md`) para medir a qualidade dos entregáveis.
- Executar o script de pontuação (`evaluation/score.py`) e revisar resultados quantitativos e qualitativos.
- Compilar feedback estruturado e recomendar melhorias.

---

Seguindo essas recomendações de custos e papéis, o laboratório pode ser executado de forma eficiente e segura, permitindo o foco no aprendizado e na experimentação sem comprometer o orçamento nem a conformidade.