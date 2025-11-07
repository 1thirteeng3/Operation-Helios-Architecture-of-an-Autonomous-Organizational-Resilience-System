# Checklist de QA e Consistência

Esta checklist deve ser usada por revisores para validar que todos os entregáveis atendem aos critérios de aceitação. Marque cada item quando concluído.

## Diagnóstico (deliverable/1_diagnosis.pdf)

- [ ] O PDF contém um grafo de dependências anotado.
- [ ] Há uma lista de pelo menos 10 nós críticos identificados.
- [ ] Cada nó crítico possui uma mitigação priorizada associada.

## Arquitetura (deliverable/2_architecture_blueprint.pdf)

- [ ] O documento apresenta diagramas SysML/UML legíveis, com componentes, fluxos e redundâncias.
- [ ] Estratégias de redundância (multi‑AZ, backup, failover) estão explicitadas.
- [ ] Fluxos de failover e de autoscaling são descritos.

## Simulação (deliverable/3_simulation_report.csv, report.ipynb)

- [ ] O arquivo CSV contém resultados de pelo menos três cenários distintos (variação de `p_node`, capacidade, etc.).
- [ ] O notebook interpreta os resultados: inclui gráficos, estatísticas (média, variância, histogramas) e discussão de sensibilidade.
- [ ] A simulação inclui modelos de falha em cascata e de backpressure.

## Protótipo (deliverable/4_prototype_repo)

- [ ] O repositório contém um modelo registrado no MLflow com artefatos acessíveis.
- [ ] O serviço FastAPI responde a `/health` e `/predict` retornando código 200.
- [ ] Os manifests Kubernetes estão presentes e podem ser aplicados com `kubectl apply` sem erros.
- [ ] O workflow CI passa sem falhas (lint, testes unitários, build de contêiner).

## Comunicação (deliverable/5_board_deck.pptx, dashboard_link)

- [ ] A apresentação em PPTX possui pelo menos uma página executiva e cobre problema, impacto, mitigação de curto prazo, roadmap de longo prazo e custos.
- [ ] Há um link ou referência a dashboards interativos (Grafana) mostrando KPIs de saúde do sistema.
- [ ] Os KPIs são mensuráveis e alinhados com os requisitos (latência, disponibilidade, custo, precisão do modelo).

## Governança e Segurança

- [ ] O checklist de segurança e conformidade foi cumprido ou há justificativa para itens pendentes.
- [ ] Runbooks (responders, incidentes) estão completos e acionáveis.
- [ ] Existem planos de post‑mortem com lições aprendidas e ações de acompanhamento.