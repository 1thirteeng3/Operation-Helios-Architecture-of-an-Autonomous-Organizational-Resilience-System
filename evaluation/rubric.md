# Rubrica de Avaliação

Esta rubrica detalha os critérios utilizados para pontuar os entregáveis do laboratório, totalizando **100 pontos**. Cada critério inclui peso e requisitos mínimos para obtenção de pontuação total. Utilize‑a para orientar o desenvolvimento e autoavaliação dos artefatos.

## 1. Arquitetura & Design (30 pts)

| Subcritério | Peso | Descrição |
|-------------|-----:|-----------|
| **Completude de componentes** | 10 pts | A arquitetura engloba nuvem, edge e governança de modelos; recursos de rede, armazenamento, orquestração, MLOps e observabilidade estão devidamente especificados. |
| **Redundância e failover** | 10 pts | Estratégias de alta disponibilidade estão implementadas (multi‑AZ, autoescalonamento, backups) e justificadas tecnicamente. |
| **Documentação SysML/UML** | 10 pts | Diagramas claros e legíveis descrevendo componentes, fluxos de dados, dependências e políticas de redundância. |

## 2. Diagnóstico & Análise (20 pts)

| Subcritério | Peso | Descrição |
|-------------|-----:|-----------|
| **Identificação de nós críticos e métricas** | 10 pts | O diagnóstico mapeia a topologia atual e destaca hubs, gargalos e vulnerabilidades; utiliza métricas de centralidade, modularidade e fluxo. |
| **Uso de métricas e análise de rede** | 10 pts | Emprega algoritmos adequados (grau, betweenness, modularidade) e interpreta corretamente os resultados. |

## 3. Implementação & Observabilidade (20 pts)

| Subcritério | Peso | Descrição |
|-------------|-----:|-----------|
| **Protótipo funcional** | 10 pts | Microserviços (FastAPI) respondem corretamente a `/health` e `/predict`; modelos são registrados no MLflow; repositório executável via CI. |
| **Dashboards e alertas configurados** | 10 pts | Painéis Grafana estão completos (visão de cluster, saúde do modelo, análise de grafo) e regras de alerta cobrem as principais falhas. |

## 4. Simulação & Quantitativo (15 pts)

| Subcritério | Peso | Descrição |
|-------------|-----:|-----------|
| **Monte Carlo e interpretação estatística** | 8 pts | Simulações variam parâmetros relevantes (probabilidades, capacidade); resultados são analisados com gráficos, médias e distribuição de tempos de recuperação e latências. |
| **Propagação e cenários de stress** | 7 pts | Modelos de falha em cascata e backpressure estão implementados; incluem cenários de stress e sensibilidade aos parâmetros. |

## 5. Comunicação & Estratégia (15 pts)

| Subcritério | Peso | Descrição |
|-------------|-----:|-----------|
| **Deck executivo** | 8 pts | Apresentação clara com resumo do problema, impacto e recomendações; adaptação para público não técnico; KPIs mensuráveis. |
| **Runbooks e plano de mitigação** | 7 pts | Playbooks acionáveis para cada incidente; responsabilidades definidas; plano de recuperação e ações futuras descritos. |

## Pontuação Total: 100 pontos

Para obter a pontuação máxima, todos os subcritérios devem estar satisfeitos. A pontuação parcial pode ser atribuída proporcionalmente de acordo com a qualidade e completude de cada item.