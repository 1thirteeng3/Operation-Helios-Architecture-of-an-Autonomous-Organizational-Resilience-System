# Geradores de Dados

Esta pasta contém scripts e arquivos responsáveis por criar conjuntos de dados sintéticos que alimentam as diversas etapas da simulação.  Os dados são gerados de forma estocástica e realista, seguindo esquemas definidos e incorporando ruído e eventos de falha.

## Scripts Disponíveis

- **`generate_timeseries.py`** – cria séries temporais de telemetria para múltiplos nós, incluindo CPU, memória, latência e taxa de requisições.  Permite configurar número de nós, duração, frequência e perfis de carga.
- **`generate_logs.py`** – produz logs estruturados em formato JSON com níveis de severidade variados, identificadores de trace e simula logs malformados para testar a robustez de parsers.
- **`generate_graph.py`** – constrói um grafo de dependências entre serviços, data stores, regiões de cloud, dispositivos de borda, modelos, datasets e usuários.  Gera arquivos CSV compatíveis com Neo4j e um formato JSON simples para análises com NetworkX ou outras ferramentas.
- **`generate_transactions.py`** – gera eventos transacionais de recomendação, com usuários, itens, pontuações, features e rótulos (potencialmente ruidosos) para experimentos de ML e testes de drift.
- **`adversarial_inputs.json`** – contém exemplos de entradas adversariais e prompts maliciosos projetados para testar a resiliência de LLMs e pipelines de inferência.

Para executar qualquer script, utilize o Python 3 com os argumentos desejados.  Por exemplo:

```bash
python data/generate_timeseries.py --nb-nodes 20 --duration-hours 12 --frequency-sec 60 --output data/timeseries.csv
```

Cada script inclui uma descrição detalhada de seus parâmetros via `--help`.
