# Cenários de Incidentes

Este documento descreve um conjunto de incidentes a serem executados durante o laboratório. Os incidentes evoluem em complexidade e abrangem falhas técnicas, eventos maliciosos e problemas operacionais. Para cada incidente, é fornecido um gatilho (ação manual ou script), o comportamento esperado do sistema e um playbook com passos recomendados para investigação, isolamento, mitigação e post‑mortem.

## 1. Atraso de dados (Data lag)

**Gatilho:**

Execute um script que insere um atraso artificial no pipeline ETL de embeddings (p. ex., `scripts/induce_data_lag.sh`). O script pausa a extração ou carregamento por 30 minutos, de modo que o sistema continue servindo recomendações com embeddings desatualizados.

**Comportamento esperado:**

- Os serviços de recomendação continuam respondendo, mas a qualidade das recomendações degrada progressivamente.
- Métricas de precisão/recall no MLflow mostram queda, e alertas de drift são acionados.
- Dashboards de observabilidade indicam backlog crescente no pipeline de ingestão.

**Playbook:**

- *Investigar:* Verifique dashboards do Grafana para latência de ETL e métricas de drift; consulte logs do pipeline para erros ou paradas.
- *Isolar:* Identifique o serviço ou nó responsável pelo atraso (e.g., worker travado) e redirecione novas cargas para instâncias saudáveis.
- *Mitigar:* Reinicie ou scale up o componente ETL; acione pipelines alternativos (shadow ETL) para recomputar embeddings; comunique equipes de ciência de dados sobre a defasagem.
- *Post‑mortem:* Documente a linha do tempo do atraso, métricas afetadas e decisões tomadas. Atualize procedimentos de monitoramento de latência e adicione alertas proativos para atrasos superiores a X minutos.

## 2. Falha de nó principal (Node crash – core)

**Gatilho:**

Simule a falha de um nó de controle do EKS (ou de um nó de worker crítico) desligando a instância via AWS Console ou script Terraform.

**Comportamento esperado:**

- Parte das APIs pode ficar indisponível ou com latência elevada.
- O Kubernetes tenta redistribuir pods; pods em nós afetados entram em estado *CrashLoopBackOff* ou *Unknown*.
- Alertas de disponibilidade são disparados; clientes em algumas regiões percebem degradação.

**Playbook:**

- *Investigar:* Verifique o status dos nós em `kubectl get nodes`; inspecione eventos (`kubectl describe node`), logs do control‑plane via CloudWatch e métricas de saúde do cluster.
- *Isolar:* Drene o nó defeituoso (`kubectl drain <node> --ignore-daemonsets`) para mover workloads; adicione taints para evitar agendamento futuro.
- *Mitigar:* Substitua o nó (recriando via autoscaling), reequilibre pods e valide se as APIs retornam 200; avalie replicar control‑plane em múltiplas zonas.
- *Post‑mortem:* Registre a causa raiz (falha de hardware, atualização sem cuidado); revise políticas de alta disponibilidade do cluster, backups e procedimentos de failover.

## 3. Deriva de modelo (Model drift)

**Gatilho:**

Injete uma mudança drástica na distribuição de entradas (por exemplo, carregando um conjunto de dados adversarial via `data/upload_shifted_dataset.sh`) ou modifique a função de recomendação para priorizar características irrelevantes.

**Comportamento esperado:**

- Métricas de performance do modelo (AUC, precisão) caem significativamente.
- Serviços downstream recebem decisões incoerentes; dashboards mostram aumento de erros de negócios (p.ex., cancelamentos de pedidos).
- Alertas de drift são acionados no MLflow ou nos monitores personalizados.

**Playbook:**

- *Investigar:* Analise métricas de drift e distribuições de features; compare a distribuição atual com a de treinamento usando ferramentas de XAI.
- *Isolar:* Determine se o problema está nos dados de entrada ou no próprio modelo; verifique logs de ingestão e datas dos datasets utilizados.
- *Mitigar:* Revert Models to last stable version via MLflow; execute re‑treinamento rápido com dados recentes; implemente triggers automáticos de rollback quando drift exceder um limiar.
- *Post‑mortem:* Documente o evento, a origem da deriva (campaign adversária, mudança de comportamento do usuário), e ajuste mecanismos de monitoramento/alerta para detectar drift mais cedo.

## 4. Apagão de telemetria (Telemetry blackout)

**Gatilho:**

Desabilite ou bloquee a coleta de métricas (`/metrics`) em um serviço FastAPI, ou interrompa o agente de exportação de logs/metrics (por exemplo, pare o serviço `prometheus-node-exporter`).

**Comportamento esperado:**

- Painéis Grafana mostram lacunas ou zero no número de métricas; Prometheus reporta *target down*.
- Alertas de *missing data* são disparados; engenheiros ficam sem visibilidade do estado do serviço.

**Playbook:**

- *Investigar:* Confirme se a instância está ativa via `kubectl`; verifique conexões de rede e logs do exporter; monitore se outros serviços estão coletando métricas normalmente.
- *Isolar:* Identifique se a falha é isolada a um serviço ou generalizada; use métricas internas (por exemplo, uso de CPU) para aproximar o estado.
- *Mitigar:* Reinicie ou reimplante o exportador/sidecar; se houver bug, aplique atualização da biblioteca de instrumentação (prometheus_client) ou retorne a uma versão estável.
- *Post‑mortem:* Determine a causa (bug, credenciais expiradas, alteração de configuração); melhore testes de monitoramento e adicione alertas para ausência de métricas além de métricas anômalas.

## 5. Prompt malicioso (Malicious prompt)

**Gatilho:**

Envie ao endpoint do assistente LLM um prompt contendo injeção de comandos proibidos (por exemplo, recuperando dados sensíveis ou instruindo a ignorar validações) via `curl` ou script.

**Comportamento esperado:**

- O LLM, validado com `py‑llm‑shield`, deverá rejeitar ou reparar a resposta de acordo com o esquema Pydantic (`ModelDecision`).
- Se vulnerável, o LLM pode retornar dados sensíveis ou acatar comandos; alertas de validação falha serão disparados.

**Playbook:**

- *Investigar:* Analise o prompt malicioso recebido, verifique logs do serviço de assistente e o status das validações; confira se `py‑llm‑shield` bloqueou a resposta.
- *Isolar:* Desative temporariamente o endpoint ou aplique filtros de entrada (regex, blocklist) para prompts maliciosos; aumente o nível de logging.
- *Mitigar:* Ajuste políticas de validação do LLM (por exemplo, reforçando o schema Pydantic), treine o modelo com respostas a ataques conhecidos, e comunique a equipe de segurança.
- *Post‑mortem:* Documente o vetor de ataque e a eficácia das defesas; adicione testes automatizados de prompt injection; revise mecanismos de auditoria de respostas.

## 6. Envenenamento de grafo (Graph poisoning)

**Gatilho:**

Utilize uma API interna ou script (`scripts/poison_graph.py`) para injetar nós e arestas falsas na base Neo4j ou no grafo em memória, alterando centralidades e comunidades.

**Comportamento esperado:**

- Métricas de centralidade e páginas de recomendação podem alterar drasticamente; modelos GNN treinados com o grafo corrompido começam a priorizar nós maliciosos.
- Alertas de anomalias no grafo (com base em métricas de distribuição de grau) são disparados, se configurados.

**Playbook:**

- *Investigar:* Compare snapshots de grafos anteriores com o atual; execute algoritmos de detecção de comunidades para identificar clusters anômalos; verifique logs de operações no banco.
- *Isolar:* Identifique e marque entidades suspeitas; bloqueie o acesso de ingestores responsáveis; congele o grafo para evitar nova escrita.
- *Mitigar:* Restaure o grafo a partir de backup íntegro; re‑treine modelos com dados limpos; implemente validações de integridade (assinaturas, checksums) nas importações.
- *Post‑mortem:* Analise como a injeção passou pelos controles; crie políticas de revisão de dados entrantes; melhore detecção automática de outliers em grafos.

## 7. Pico de custo (Cost spike)

**Gatilho:**

Lance intencionalmente um job que escala horizontalmente sem limites (por exemplo, ajuste autoscaling para permitir centenas de réplicas) ou acione um script que cria instâncias dispendiosas (GPU) em loop.

**Comportamento esperado:**

- A conta de cloud apresenta aumento súbito no consumo de recursos (CPU, GPU, armazenamento). Alertas de custo são disparados pelo AWS Budgets ou Stackdriver.
- Alguns serviços podem sofrer competição por recursos e degradar seu desempenho.

**Playbook:**

- *Investigar:* Verifique dashboards de custo e uso; identifique os serviços respons��veis pela escalada (via tags e métricas de auto scaling). Analise logs do CI/CD para jobs replicados.
- *Isolar:* Aplique limites de autoscaling nos deployments; pause ou elimine pods excedentes; revise políticas de escalonamento para CPU/latência.
- *Mitigar:* Defina cotas de recursos e budgets com alerta; optimize a utilização de instâncias (spot vs. on‑demand). Ao encerrar o incidente, remova recursos extras para reduzir custos.
- *Post‑mortem:* Documente como o pico ocorreu (bug, configuração incorreta, ataque). Ajuste processos de revisão de alterações de escalonamento; automatize alertas e limitação de gastos.

## 8. Vulnerabilidade na cadeia de suprimentos (Supply chain vulnerability)

**Gatilho:**

Introduza uma dependência vulnerável no `requirements.txt` ou em um Dockerfile (por exemplo, `pip install package-with-cve`) e permita que a pipeline CI a construa.

**Comportamento esperado:**

- Ferramentas de análise de segurança (Snyk, Trivy) na pipeline CI/CD identificam a CVE e falham o build.
- Se não detectada, a aplicação pode ficar exposta a exploits; alertas de segurança externas podem surgir.

**Playbook:**

- *Investigar:* Verifique logs de scanners de segurança no CI; identifique a versão e a vulnerabilidade reportada; procure por exploração ativa nos serviços.
- *Isolar:* Bloqueie a publicação da imagem vulnerável; role back para versão segura do pacote; aplique patches de segurança na imagem base.
- *Mitigar:* Atualize dependências ou substitua-as por alternativas seguras; automatize verificações de supply chain (SBOM, assinaturas de imagem). Notifique a equipe de DevSecOps.
- *Post‑mortem:* Registre o fluxo que permitiu a inclusão do pacote vulnerável; revise processos de revisão de dependências e política de pinagem de versões; implemente controles de verificação contínua.

## 9. Corrupção de dados (Data corruption)

**Gatilho:**

Corrompa um objeto S3 que contém um dataset crítico (p.ex., sobrescrevendo com bytes aleatórios) ou mova-o para outro bucket sem atualizar os apontadores; simule a corrupção via script (`scripts/corrupt_data.sh`).

**Comportamento esperado:**

- Jobs de leitura falham com erros de checksum ou *file not found*; pipelines de ingestão interrompem; métricas de sucesso de carga caem.
- MLflow ou sistemas de logging relatam falha na localização de artefatos.

**Playbook:**

- *Investigar:* Tente recuperar o objeto via `aws s3 ls` e `aws s3 cp`; verifique logs do serviço de ingestão e do MLflow para mensagens de erro; compare hashes md5 conhecidos com o arquivo atual.
- *Isolar:* Impeça que jobs dependentes continuem tentando ler o dataset corrompido; marque o bucket como em estado de erro; faça o failover para uma réplica ou backup.
- *Mitigar:* Restaure o objeto a partir de backups ou de versões anteriores (habilitar versionamento no S3); verifique a integridade de todos os outros objetos relacionados; valide o pipeline de checagens de integridade.
- *Post‑mortem:* Documente a origem da corrupção (falha de rede, script malicioso, race condition); estabeleça procedimentos de verificação de integridade automatizados e backups regulares; avalie o uso de S3 Object Lock para proteção contra alterações não autorizadas.

---

### Template de Post‑mortem

1. **Contexto:** Descrição breve do incidente e seu impacto.
2. **Linha do tempo:** Sequência de eventos antes, durante e após o incidente, com horários aproximados.
3. **Detecção:** Como o problema foi identificado (alertas, logs, usuários).
4. **Causa raiz:** Análise técnica apontando falhas ou vulnerabilidades que permitiram o incidente.
5. **Ação de resposta:** O que foi feito para mitigar, contornar ou resolver o problema.
6. **Lições aprendidas:** Pontos fortes e fracos do processo de resposta; melhorias identificadas.
7. **Plano de ação:** Passos concretos para evitar recorrência, com responsáveis e prazos.