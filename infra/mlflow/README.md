# Configuração do MLflow

Este diretório contém orientações para configurar um servidor de tracking do **MLflow** e armazenar artefatos de modelos.  O MLflow é utilizado pelo laboratório para versionar modelos, registrar métricas, controlar variações de datasets e garantir reprodutibilidade.

## Servidor de Tracking

Para iniciar o servidor de tracking localmente, você pode executar:

```bash
mlflow server \
  --backend-store-uri sqlite:///mlflow.db \
  --default-artifact-root ./mlruns \
  --host 0.0.0.0 --port 5000
```

Opções:

- `--backend-store-uri`: define onde serão armazenados os metadados das execuções.  Pode ser um banco SQLite local (`sqlite:///mlflow.db`) ou um S3/MinIO, Postgres, etc.
- `--default-artifact-root`: raiz padrão para armazenar artefatos de modelos (por exemplo, `s3://helius-mlflow-artifacts/`).
- `--host` e `--port`: endereços de escuta do servidor.

Em ambientes de produção, recomenda‑se utilizar um banco de dados robusto (Postgres/MySQL) para o backend e um bucket S3/MinIO para os artefatos.

## Uso

Os scripts de treinamento (como `ml/train_gnn.py` ou o notebook `ml/train_gnn.ipynb`) podem se conectar ao servidor definindo a URI de tracking através de:

```python
import mlflow
mlflow.set_tracking_uri("http://<host>:<port>")
```

Durante a execução, registre parâmetros (hiperparâmetros, seed, versões de datasets), métricas (loss, accuracy, fairness) e artefatos (modelos, gráficos).  Dessa forma, a governança e o versionamento ficam centralizados.
