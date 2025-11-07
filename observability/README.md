# Observabilidade

Os artefatos desta pasta são dedicados ao monitoramento e logging do ambiente simulado.  Incluem configurações para **Prometheus** e **Grafana**, dashboards pré‑configurados, alertas e sugestões de exporters de métricas.  A integridade e visibilidade do sistema dependem de uma observabilidade sólida, por isso considere customizar estes recursos conforme os serviços definidos.

## Prometheus

* ``prometheus/prometheus.yml`` – arquivo de configuração com uma scrape job chamada ``fastapi-services`` que coleta métricas do endpoint ``/metrics`` nos serviços FastAPI.  Ajuste os targets para os nomes ou endereços corretos dos serviços no cluster.  Há também um exemplo comentado de descoberta via Kubernetes.
* ``prometheus/alerts.yml`` – conjunto de regras de alerta para uso com Alertmanager.  Inclui alertas quando mais de 5 % das respostas de modelo são inválidas, quando a latência p95 excede 2 s, quando o backlog de processamento ultrapassa 100 mensagens e quando a ingestão de logs para por mais de 10 minutos.

## Grafana

Os dashboards podem ser importados via UI ou provisionados como arquivos JSON:

* ``grafana/dashboards/system_overview.json`` – visualiza CPU e memória por nó usando métricas de node exporter e o status de saúde dos nodes.  As consultas assumem que ``node_cpu_seconds_total``, ``node_memory_MemAvailable_bytes`` e ``kube_node_status_condition`` estão sendo expostos pelo Prometheus.
* ``grafana/dashboards/model_health.json`` – monitora a latência (p95) das requisições, a taxa de erros e um indicador de drift do modelo.  Requer que os serviços exponham métricas ``request_latency_seconds_bucket``, ``request_errors_total``, ``request_total`` e ``model_drift_score``.
* ``grafana/dashboards/graph_analysis.json`` – painel para análise de grafos, com um bargauge para tamanhos de comunidades (``community_size``) e uma série temporal para centralidade dos nós (``centrality_score``).  Para funcionar, é preciso expor essas métricas via Prometheus a partir do módulo de análise de grafos.

## Próximos passos

- Instrumentar as APIs FastAPI com ``prometheus_client`` para expor métricas como contagem de requisições, latência e total de erros.
- Integrar a ingestão de logs com Loki ou outro sistema de logging para compor o pipeline completo de observabilidade.
- Ajustar as regras de alerta e os painéis conforme as necessidades da operação (SLAs, comportamentos esperados).  Por exemplo, parâmetros de latência e backlog podem variar conforme a carga.
