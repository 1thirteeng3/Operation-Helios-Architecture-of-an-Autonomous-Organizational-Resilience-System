# Serviços

Os serviços nesta pasta representam microserviços modulares que compõem a arquitetura da Helius.  Incluem APIs para ingestão de dados, consulta de status do sistema, servimento de modelos e assistentes baseados em LLM.  Cada serviço é isolado em seu próprio diretório com um `Dockerfile` (a ser adicionado) e define uma aplicação **FastAPI**.

### Serviços inclusos

* **llm_assistant/** – uma API que simula um assistente de linguagem natural.  A partir de um *prompt* textual, o serviço devolve uma estrutura de decisão validada conforme o schema Pydantic `ModelDecision`.  Este serviço demonstra como integrar **py-llm-shield** para validar e reparar respostas de LLMs.
* **recommender_service/** – expõe um endpoint `/predict` que carrega um modelo de recomendação (GraphSAGE) registrado no MLflow e retorna a classe prevista para uma lista de IDs de nós.  O caminho do modelo e o arquivo de mapeamento de categorias são fornecidos via variáveis de ambiente.

Novos serviços podem ser adicionados durante a simulação, por exemplo, um serviço de ingestão de telemetria ou uma API de status do sistema.  Para cada serviço, crie um subdiretório contendo o código Python, dependências e eventuais assets (modelos, esquemas, etc.).
